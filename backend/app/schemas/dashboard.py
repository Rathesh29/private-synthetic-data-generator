"""
Dashboard Statistics Schemas.
"""

from typing import List, Dict, Any
from pydantic import BaseModel

class DashboardStatsResponse(BaseModel):
    total_datasets: int
    total_generation_jobs: int
    completed_jobs: int
    active_users: int
    model_versions_count: int
    max_epsilon_budget: float
    total_epsilon_spent: float
    remaining_epsilon_budget: float
    privacy_budget_utilization_pct: float
    recent_activity: List[Dict[str, Any]]
    jobs_by_status: Dict[str, int]
    salary_distribution: List[Dict[str, Any]]
    department_distribution: List[Dict[str, Any]]
    experience_distribution: List[Dict[str, Any]]
    performance_distribution: List[Dict[str, Any]]
