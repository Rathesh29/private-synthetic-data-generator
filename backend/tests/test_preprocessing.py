"""
Data Preprocessing Pipeline Unit Tests.
"""

import pandas as pd
import numpy as np
from app.ml.preprocessor import TabularDataPreprocessor

def test_preprocessor_detection_and_transform():
    df = pd.DataFrame({
        "employee_id": ["EMP001", "EMP002", "EMP003", "EMP004"],
        "age": [28, 45, 34, 52],
        "department": ["Engineering", "Sales", "Engineering", "HR"],
        "salary": [80000, 65000, 92000, 58000],
        "attrition": ["No", "Yes", "No", "No"]
    })

    preprocessor = TabularDataPreprocessor({"drop_identifiers": True})
    preprocessor.fit(df)

    assert "employee_id" in preprocessor.identifier_cols
    assert "age" in preprocessor.numeric_cols
    assert "salary" in preprocessor.numeric_cols
    assert "department" in preprocessor.categorical_cols
    assert "attrition" in preprocessor.categorical_cols

    transformed = preprocessor.transform(df)
    assert transformed.shape[0] == 4
    assert transformed.shape[1] == len(preprocessor.encoded_feature_names)
    # Check bounded within [0, 1]
    assert np.all(transformed >= 0.0)
    assert np.all(transformed <= 1.0)

    # Test inverse transformation
    reconstructed_df = preprocessor.inverse_transform(transformed)
    assert len(reconstructed_df) == 4
    assert "age" in reconstructed_df.columns
    assert "department" in reconstructed_df.columns
    assert "employee_id" in reconstructed_df.columns
    assert reconstructed_df["employee_id"].iloc[0].startswith("SYN_")
