"""
Baseline Statistical Synthetic Generator.
Implements Gaussian Copula / Empirical Multi-Distribution synthesis.
Note: This method preserves empirical statistical distributions but does NOT provide formal Differential Privacy guarantees.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd
from app.ml.preprocessor import TabularDataPreprocessor

class BaselineStatisticalGenerator:
    """
    Empirical statistical generator based on correlation preservation and marginal sampling.
    Clearly marks and notes that no differential privacy guarantee is provided.
    """
    def __init__(self):
        self.preprocessor: TabularDataPreprocessor = None
        self.mean_vector: np.ndarray = None
        self.cov_matrix: np.ndarray = None
        self.is_fitted = False
        
    def fit(self, df: pd.DataFrame, preprocessor: TabularDataPreprocessor):
        self.preprocessor = preprocessor
        transformed_matrix = self.preprocessor.transform(df)
        
        self.mean_vector = np.mean(transformed_matrix, axis=0)
        # Add small regularization diagonal to ensure positive semi-definite covariance
        cov = np.cov(transformed_matrix, rowvar=False)
        if cov.ndim == 0:
            cov = np.array([[float(cov)]])
        reg = np.eye(cov.shape[0]) * 1e-4
        self.cov_matrix = cov + reg
        self.is_fitted = True
        return self

    def generate(self, num_records: int) -> pd.DataFrame:
        if not self.is_fitted:
            raise ValueError("Generator is not fitted.")
            
        # Sample from multivariate Gaussian
        raw_samples = np.random.multivariate_normal(
            mean=self.mean_vector,
            cov=self.cov_matrix,
            size=num_records
        )
        
        # Clip numerical features to valid [0, 1] range
        raw_samples = np.clip(raw_samples, 0.0, 1.0)
        
        # Softmax normalize categorical slices
        for col in self.preprocessor.categorical_cols:
            sl = self.preprocessor.column_slices[col]
            cat_logits = raw_samples[:, sl]
            # Softmax
            exp_logits = np.exp(cat_logits - np.max(cat_logits, axis=1, keepdims=True))
            raw_samples[:, sl] = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
            
        synthetic_df = self.preprocessor.inverse_transform(raw_samples)
        return synthetic_df

    @property
    def has_formal_dp_guarantee(self) -> bool:
        return False

    @property
    def guarantee_statement(self) -> str:
        return (
            "NO FORMAL DIFFERENTIAL PRIVACY GUARANTEE: "
            "This baseline generator models empirical statistics directly. "
            "It does not introduce bounded sensitivity or calibrated noise, and thus cannot "
            "prevent membership inference or reconstruction attacks under rigorous privacy models."
        )
