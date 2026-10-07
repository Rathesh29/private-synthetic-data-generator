"""
Tabular Data Preprocessor for HR Datasets.
Handles normalization, categorical encoding, identifier exclusion, and inverse transformations.
"""

from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
import numpy as np

class TabularDataPreprocessor:
    """
    Stateful preprocessor for tabular HR datasets.
    Converts mixed tabular data to continuous normalized representations for ML models
    and safely inverse-transforms synthetic continuous arrays back into clean tabular records.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.drop_identifiers = self.config.get("drop_identifiers", True)
        self.scaling = self.config.get("numerical_scaling", "minmax")
        self.encoding = self.config.get("categorical_encoding", "onehot")
        
        self.identifier_cols: List[str] = []
        self.numeric_cols: List[str] = []
        self.categorical_cols: List[str] = []
        
        # Scaling params: col -> (min, max, mean, std)
        self.numeric_stats: Dict[str, Dict[str, float]] = {}
        # Categorical categories: col -> list of unique categories
        self.categorical_maps: Dict[str, List[str]] = {}
        self.encoded_feature_names: List[str] = []
        self.column_slices: Dict[str, slice] = {}
        self.is_fitted = False

    def detect_columns(self, df: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
        identifiers = []
        numerics = []
        categoricals = []

        for col in df.columns:
            col_lower = str(col).lower()
            # Identifier heuristics
            if any(term in col_lower for term in ["id", "employee_id", "ssn", "uuid", "badge", "email"]):
                identifiers.append(col)
            elif pd.api.types.is_numeric_dtype(df[col]):
                # If numeric but very few unique values (e.g. 2 values like 0/1), check if categorical
                if df[col].nunique() <= 4 and df[col].nunique() / len(df) < 0.05:
                    categoricals.append(col)
                else:
                    numerics.append(col)
            else:
                categoricals.append(col)

        return identifiers, numerics, categoricals

    def fit(self, df: pd.DataFrame, custom_identifiers: Optional[List[str]] = None):
        """Fits preprocessor on original dataframe."""
        df_copy = df.copy()
        
        auto_ids, numerics, categoricals = self.detect_columns(df_copy)
        if custom_identifiers is not None:
            self.identifier_cols = custom_identifiers
            # Recalculate numerics/categoricals excluding custom identifiers
            remaining = [c for c in df_copy.columns if c not in self.identifier_cols]
            self.numeric_cols = [c for c in remaining if pd.api.types.is_numeric_dtype(df_copy[c])]
            self.categorical_cols = [c for c in remaining if c not in self.numeric_cols]
        else:
            self.identifier_cols = auto_ids
            self.numeric_cols = numerics
            self.categorical_cols = categoricals

        # Handle numeric statistics
        for col in self.numeric_cols:
            series = pd.to_numeric(df_copy[col], errors='coerce')
            median_val = series.median()
            series = series.fillna(median_val if not pd.isna(median_val) else 0.0)
            
            c_min = float(series.min())
            c_max = float(series.max())
            c_mean = float(series.mean())
            c_std = float(series.std() if series.std() > 0 else 1.0)
            
            # If min == max, expand slightly to prevent div by zero
            if c_min == c_max:
                c_max += 1.0
                
            self.numeric_stats[col] = {
                "min": c_min,
                "max": c_max,
                "mean": c_mean,
                "std": c_std,
                "median": float(median_val if not pd.isna(median_val) else 0.0),
                "is_integer": bool(pd.api.types.is_integer_dtype(df_copy[col]))
            }

        # Handle categorical categories
        for col in self.categorical_cols:
            cats = [str(x) for x in df_copy[col].dropna().unique().tolist()]
            if not cats:
                cats = ["Unknown"]
            self.categorical_maps[col] = sorted(cats)

        # Build feature layout
        self.encoded_feature_names = []
        current_idx = 0
        
        for col in self.numeric_cols:
            self.encoded_feature_names.append(col)
            self.column_slices[col] = slice(current_idx, current_idx + 1)
            current_idx += 1
            
        for col in self.categorical_cols:
            cats = self.categorical_maps[col]
            start = current_idx
            for cat in cats:
                self.encoded_feature_names.append(f"{col}_{cat}")
                current_idx += 1
            self.column_slices[col] = slice(start, current_idx)

        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transforms a dataframe into normalized ML numerical array."""
        if not self.is_fitted:
            raise ValueError("Preprocessor is not fitted yet.")

        num_samples = len(df)
        total_dim = len(self.encoded_feature_names)
        output_matrix = np.zeros((num_samples, total_dim), dtype=np.float32)

        # Transform numeric features to [0, 1]
        for col in self.numeric_cols:
            sl = self.column_slices[col]
            stats = self.numeric_stats[col]
            if col in df.columns:
                series = pd.to_numeric(df[col], errors='coerce').fillna(stats["median"])
            else:
                series = pd.Series([stats["median"]] * num_samples)
                
            norm_vals = (series.values - stats["min"]) / (stats["max"] - stats["min"])
            output_matrix[:, sl] = np.clip(norm_vals, 0.0, 1.0)[:, np.newaxis]

        # Transform categoricals to one-hot vectors
        for col in self.categorical_cols:
            sl = self.column_slices[col]
            cats = self.categorical_maps[col]
            cat_to_idx = {c: i for i, c in enumerate(cats)}
            
            if col in df.columns:
                series = df[col].astype(str).fillna("Unknown")
            else:
                series = pd.Series(["Unknown"] * num_samples)

            col_sub = np.zeros((num_samples, len(cats)), dtype=np.float32)
            for row_i, val in enumerate(series):
                idx = cat_to_idx.get(str(val), 0)
                col_sub[row_i, idx] = 1.0
            output_matrix[:, sl] = col_sub

        return output_matrix

    def inverse_transform(self, matrix: np.ndarray, add_synthetic_ids: bool = True) -> pd.DataFrame:
        """
        Transforms normalized synthetic ML array back to full tabular DataFrame
        with proper column types, realistic values, and synthetic identifier badges.
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor is not fitted yet.")

        num_samples = matrix.shape[0]
        data = {}

        # Reconstruct numerical columns
        for col in self.numeric_cols:
            sl = self.column_slices[col]
            stats = self.numeric_stats[col]
            norm_col = matrix[:, sl].flatten()
            norm_col = np.clip(norm_col, 0.0, 1.0)
            unscaled = norm_col * (stats["max"] - stats["min"]) + stats["min"]
            
            if stats.get("is_integer", False):
                data[col] = np.round(unscaled).astype(int)
            else:
                data[col] = np.round(unscaled, 2)

        # Reconstruct categorical columns via argmax over one-hot slices
        for col in self.categorical_cols:
            sl = self.column_slices[col]
            cats = self.categorical_maps[col]
            cat_slice = matrix[:, sl]
            best_cat_indices = np.argmax(cat_slice, axis=1)
            data[col] = [cats[i] for i in best_cat_indices]

        # Reconstruct synthetic identifiers if requested
        if add_synthetic_ids and self.identifier_cols:
            for id_col in self.identifier_cols:
                data[id_col] = [f"SYN_{i+1:05d}" for i in range(num_samples)]

        df_out = pd.DataFrame(data)
        
        # Ensure original column ordering where possible
        original_cols = self.identifier_cols + self.numeric_cols + self.categorical_cols
        existing_cols = [c for c in original_cols if c in df_out.columns]
        other_cols = [c for c in df_out.columns if c not in existing_cols]
        return df_out[existing_cols + other_cols]

    def get_summary(self) -> Dict[str, Any]:
        """Returns metadata summary of the preprocessing configuration."""
        return {
            "dropped_identifiers": self.identifier_cols,
            "numeric_columns": self.numeric_cols,
            "categorical_columns": self.categorical_cols,
            "total_encoded_dimensions": len(self.encoded_feature_names),
            "feature_names": self.encoded_feature_names,
            "categorical_categories_count": {c: len(cats) for c, cats in self.categorical_maps.items()}
        }
