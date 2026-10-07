"""
Privacy Service.
Enforces Differential Privacy limits, tracks accumulated epsilon and delta expenditures,
and provides trade-off estimations between privacy protection and data utility.
"""

from typing import Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.repositories.privacy_repo import PrivacyRepository
from app.privacy.accountant import RDPAccountant
from app.schemas.privacy import PrivacyBudgetStatus, PrivacyAccountingResponse, PrivacyTradeoffEstimate

class PrivacyService:
    def __init__(self, db: Session):
        self.db = db
        self.privacy_repo = PrivacyRepository(db)

    def get_budget_status(self) -> PrivacyBudgetStatus:
        total_spent = self.privacy_repo.get_total_epsilon_spent()
        max_budget = settings.MAX_GLOBAL_EPSILON_BUDGET
        remaining = max(0.0, round(max_budget - total_spent, 4))
        depleted = remaining <= 0.001
        utilization_pct = min(100.0, round((total_spent / max_budget) * 100.0, 1))
        active_models = self.privacy_repo.count_active_guarantee_models()
        total_runs = len(self.privacy_repo.get_privacy_records(limit=1000))

        explanation = (
            f"Differential Privacy guarantees strict mathematical bounds on individual privacy leakage. "
            f"Current organization budget allows up to ε={max_budget}. A total of ε={total_spent} has been spent "
            f"across {total_runs} training runs. "
            + ("Budget is fully exhausted; further DP training is blocked." if depleted else f"Remaining allowance is ε={remaining}.")
        )

        return PrivacyBudgetStatus(
            max_epsilon_budget=max_budget,
            total_epsilon_spent=total_spent,
            remaining_epsilon_budget=remaining,
            is_budget_depleted=depleted,
            budget_utilization_pct=utilization_pct,
            total_training_runs=total_runs,
            active_guarantee_models=active_models,
            delta_reference=settings.DEFAULT_DELTA,
            accounting_method="Rényi Differential Privacy (Subsampled Gaussian Mechanism)",
            explanation=explanation
        )

    def validate_budget_availability(self, estimated_epsilon: float):
        status_info = self.get_budget_status()
        if status_info.remaining_epsilon_budget < estimated_epsilon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Privacy budget exceeded. Requested training requires estimated ε={estimated_epsilon:.2f}, "
                    f"but only ε={status_info.remaining_epsilon_budget:.2f} remains in the organizational privacy budget. "
                    "Please adjust noise multiplier, reduce epochs, or contact an administrator to increase the budget cap."
                )
            )

    def estimate_tradeoff(
        self,
        noise_multiplier: float,
        clipping_norm: float,
        epochs: int,
        batch_size: int,
        dataset_size: int,
        target_delta: float = 1e-5
    ) -> PrivacyTradeoffEstimate:
        privacy_result = RDPAccountant.get_privacy_spent(
            dataset_size=dataset_size,
            batch_size=batch_size,
            noise_multiplier=noise_multiplier,
            epochs=epochs,
            target_delta=target_delta,
            clipping_norm=clipping_norm
        )
        eps = privacy_result["epsilon"]

        # Utility estimation heuristic: higher noise -> lower utility
        # Lower epsilon -> stronger privacy -> slightly reduced utility
        if eps < 0.5:
            projected_utility = 72.0
            risk_level = "Very Low"
        elif eps < 1.5:
            projected_utility = 84.0
            risk_level = "Low"
        elif eps < 5.0:
            projected_utility = 91.0
            risk_level = "Moderate"
        else:
            projected_utility = 96.0
            risk_level = "High"

        explanation = (
            f"With noise multiplier σ={noise_multiplier} and C={clipping_norm} over {epochs} epochs, "
            f"the expected privacy expenditure is ε={eps:.2f} at δ={target_delta}. "
            f"This provides {risk_level} disclosure risk with an estimated {projected_utility}% statistical utility retention."
        )

        return PrivacyTradeoffEstimate(
            noise_multiplier=noise_multiplier,
            clipping_norm=clipping_norm,
            epochs=epochs,
            batch_size=batch_size,
            dataset_size=dataset_size,
            estimated_epsilon=eps,
            estimated_delta=target_delta,
            projected_utility_score=projected_utility,
            privacy_risk_level=risk_level,
            explanation=explanation
        )

    def get_privacy_history(self, skip: int = 0, limit: int = 100) -> List[PrivacyAccountingResponse]:
        records = self.privacy_repo.get_privacy_records(skip=skip, limit=limit)
        return [PrivacyAccountingResponse.model_validate(r) for r in records]
