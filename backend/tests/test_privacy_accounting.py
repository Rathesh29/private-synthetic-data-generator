"""
Differential Privacy Accountant Unit Tests.
"""

import pytest
from app.privacy.accountant import RDPAccountant

def test_rdp_accountant_calculation():
    # Test standard parameters: dataset=1000, batch=64, sigma=1.1, epochs=20, delta=1e-5
    result = RDPAccountant.get_privacy_spent(
        dataset_size=1000,
        batch_size=64,
        noise_multiplier=1.1,
        epochs=20,
        target_delta=1e-5,
        clipping_norm=1.0
    )

    assert "epsilon" in result
    assert "delta" in result
    assert result["epsilon"] > 0.0
    assert result["delta"] == 1e-5
    assert result["noise_multiplier"] == 1.1
    assert "Subsampled Gaussian" in result["mechanism"]
    assert "assumptions" in result

def test_higher_noise_yields_lower_epsilon():
    # Higher noise multiplier should provide stronger privacy (lower epsilon)
    res_high_noise = RDPAccountant.get_privacy_spent(
        dataset_size=1000,
        batch_size=64,
        noise_multiplier=2.5,
        epochs=15,
        target_delta=1e-5
    )
    res_low_noise = RDPAccountant.get_privacy_spent(
        dataset_size=1000,
        batch_size=64,
        noise_multiplier=0.8,
        epochs=15,
        target_delta=1e-5
    )

    assert res_high_noise["epsilon"] < res_low_noise["epsilon"]

def test_more_epochs_yields_higher_epsilon():
    # Training for more steps increases privacy expenditure
    res_few_epochs = RDPAccountant.get_privacy_spent(
        dataset_size=1000,
        batch_size=64,
        noise_multiplier=1.1,
        epochs=5,
        target_delta=1e-5
    )
    res_many_epochs = RDPAccountant.get_privacy_spent(
        dataset_size=1000,
        batch_size=64,
        noise_multiplier=1.1,
        epochs=30,
        target_delta=1e-5
    )

    assert res_many_epochs["epsilon"] > res_few_epochs["epsilon"]
