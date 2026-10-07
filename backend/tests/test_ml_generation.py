"""
Machine Learning and Synthetic Generation Unit Tests.
"""

import pandas as pd
from app.ml.preprocessor import TabularDataPreprocessor
from app.ml.baseline_generator import BaselineStatisticalGenerator
from app.ml.dp_neural_generator import DPNeuralGenerator
from app.ml.evaluator import SyntheticDataEvaluator

def test_baseline_generator():
    df = pd.DataFrame({
        "age": [25, 30, 35, 40, 45, 50, 55, 60],
        "salary": [50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000],
        "department": ["Engineering", "Sales", "Engineering", "HR", "Sales", "Finance", "HR", "Engineering"]
    })
    prep = TabularDataPreprocessor()
    prep.fit(df)

    gen = BaselineStatisticalGenerator()
    gen.fit(df, prep)

    assert not gen.has_formal_dp_guarantee
    assert "NO FORMAL DIFFERENTIAL PRIVACY" in gen.guarantee_statement

    synth_df = gen.generate(num_records=10)
    assert len(synth_df) == 10
    assert "age" in synth_df.columns
    assert "salary" in synth_df.columns
    assert "department" in synth_df.columns

def test_dp_neural_generator_training_and_guarantee():
    df = pd.DataFrame({
        "age": [25, 30, 35, 40, 45, 50, 55, 60],
        "salary": [50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000],
        "department": ["Engineering", "Sales", "Engineering", "HR", "Sales", "Finance", "HR", "Engineering"]
    })
    prep = TabularDataPreprocessor()
    prep.fit(df)

    dp_gen = DPNeuralGenerator(
        latent_dim=4,
        hidden_dim=16,
        clipping_norm=1.0,
        noise_multiplier=1.2,
        epochs=3,
        batch_size=4
    )
    dp_gen.fit(df, prep)

    assert dp_gen.has_formal_dp_guarantee
    assert "FORMAL DIFFERENTIAL PRIVACY GUARANTEE" in dp_gen.guarantee_statement
    assert dp_gen.privacy_details["epsilon"] > 0

    synth_df = dp_gen.generate(num_records=10)
    assert len(synth_df) == 10
    assert "age" in synth_df.columns

def test_evaluator_metrics():
    df_real = pd.DataFrame({
        "age": [25, 30, 35, 40, 45, 50, 55, 60],
        "salary": [50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000],
        "department": ["Engineering", "Sales", "Engineering", "HR", "Sales", "Finance", "HR", "Engineering"]
    })
    df_synth = pd.DataFrame({
        "age": [26, 31, 34, 42, 44, 49, 56, 59],
        "salary": [51000, 62000, 69000, 81000, 92000, 99000, 108000, 119000],
        "department": ["Engineering", "Sales", "Engineering", "HR", "Sales", "Finance", "HR", "Engineering"]
    })

    eval_out = SyntheticDataEvaluator.evaluate(df_real, df_synth)
    assert "overall_utility_score" in eval_out
    assert "privacy_risk_score" in eval_out
    assert eval_out["overall_utility_score"] > 50.0
    assert "column_metrics" in eval_out
    assert "correlation_metrics" in eval_out
    assert "nearest_neighbor_risk" in eval_out
    assert "membership_inference_risk" in eval_out
