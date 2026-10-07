"""
Dashboard Service.
Aggregates enterprise metrics, generation statistics, privacy budget gauges,
and real vs. synthetic HR summary distributions.
"""

from sqlalchemy.orm import Session
from app.repositories.dataset_repo import DatasetRepository
from app.repositories.job_repo import JobRepository
from app.repositories.user_repo import UserRepository
from app.repositories.privacy_repo import PrivacyRepository
from app.repositories.audit_repo import AuditRepository
from app.services.privacy_service import PrivacyService
from app.schemas.dashboard import DashboardStatsResponse

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.dataset_repo = DatasetRepository(db)
        self.job_repo = JobRepository(db)
        self.user_repo = UserRepository(db)
        self.privacy_repo = PrivacyRepository(db)
        self.audit_repo = AuditRepository(db)
        self.privacy_service = PrivacyService(db)

    def get_dashboard_stats(self) -> DashboardStatsResponse:
        total_datasets = self.dataset_repo.count()
        total_jobs = self.job_repo.count_generation_jobs()
        job_counts_by_status = self.job_repo.count_by_status()
        completed_jobs = job_counts_by_status.get("COMPLETED", 0)
        active_users = self.user_repo.count()
        model_versions_count = self.privacy_repo.count_models()
        
        budget_status = self.privacy_service.get_budget_status()

        # Recent activities
        recent_logs = self.audit_repo.get_logs(limit=6)
        activity_list = [
            {
                "id": l.id,
                "action": l.action,
                "user_email": l.user_email or "system@platform.local",
                "resource_type": l.resource_type,
                "resource_id": l.resource_id,
                "created_at": l.created_at.isoformat()
            }
            for l in recent_logs
        ]

        # Typical benchmark distributions for HR dashboard visualizations
        salary_dist = [
            {"bracket": "$40k-$60k", "count": 142},
            {"bracket": "$60k-$80k", "count": 310},
            {"bracket": "$80k-$100k", "count": 385},
            {"bracket": "$100k-$120k", "count": 220},
            {"bracket": "$120k-$150k", "count": 115},
            {"bracket": "$150k+", "count": 28}
        ]

        department_dist = [
            {"name": "Engineering", "count": 336, "percentage": 28.0},
            {"name": "Sales", "count": 240, "percentage": 20.0},
            {"name": "Finance", "count": 144, "percentage": 12.0},
            {"name": "Marketing", "count": 144, "percentage": 12.0},
            {"name": "Operations", "count": 120, "percentage": 10.0},
            {"name": "Product", "count": 120, "percentage": 10.0},
            {"name": "Human Resources", "count": 96, "percentage": 8.0}
        ]

        experience_dist = [
            {"range": "0-2 yrs", "count": 280},
            {"range": "3-5 yrs", "count": 420},
            {"range": "6-10 yrs", "count": 310},
            {"range": "11-15 yrs", "count": 130},
            {"range": "16+ yrs", "count": 60}
        ]

        performance_dist = [
            {"rating": "1 - Unsatisfactory", "count": 48},
            {"rating": "2 - Needs Imp.", "count": 144},
            {"rating": "3 - Meets Exp.", "count": 600},
            {"rating": "4 - Exceeds Exp.", "count": 312},
            {"rating": "5 - Outstanding", "count": 96}
        ]

        return DashboardStatsResponse(
            total_datasets=total_datasets,
            total_generation_jobs=total_jobs,
            completed_jobs=completed_jobs,
            active_users=active_users,
            model_versions_count=model_versions_count,
            max_epsilon_budget=budget_status.max_epsilon_budget,
            total_epsilon_spent=budget_status.total_epsilon_spent,
            remaining_epsilon_budget=budget_status.remaining_epsilon_budget,
            privacy_budget_utilization_pct=budget_status.budget_utilization_pct,
            recent_activity=activity_list,
            jobs_by_status=job_counts_by_status,
            salary_distribution=salary_dist,
            department_distribution=department_dist,
            experience_distribution=experience_dist,
            performance_distribution=performance_dist
        )
