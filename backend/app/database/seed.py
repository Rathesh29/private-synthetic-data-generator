"""
Database Initialization and Seed Data Script.
Seeds default demonstration users and loads initial sample HR dataset.
"""

import os
import pandas as pd
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import get_password_hash
from app.database.session import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.dataset import Dataset, DatasetColumn
from app.repositories.user_repo import UserRepository
from app.repositories.dataset_repo import DatasetRepository

def init_db():
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    try:
        user_repo = UserRepository(db)
        dataset_repo = DatasetRepository(db)

        # 1. Seed Demo Users
        admin_user = user_repo.get_by_email(settings.FIRST_SUPERUSER_EMAIL)
        if not admin_user:
            admin_user = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                full_name="Enterprise Admin",
                role=UserRole.ADMIN,
                is_active=True
            )
            admin_user = user_repo.create(admin_user)
            print(f"Created admin account: {settings.FIRST_SUPERUSER_EMAIL}")

        analyst_user = user_repo.get_by_email(settings.FIRST_ANALYST_EMAIL)
        if not analyst_user:
            analyst_user = User(
                email=settings.FIRST_ANALYST_EMAIL,
                hashed_password=get_password_hash(settings.FIRST_ANALYST_PASSWORD),
                full_name="Senior HR Analyst",
                role=UserRole.HR_ANALYST,
                is_active=True
            )
            analyst_user = user_repo.create(analyst_user)
            print(f"Created analyst account: {settings.FIRST_ANALYST_EMAIL}")

        viewer_user = user_repo.get_by_email(settings.FIRST_VIEWER_EMAIL)
        if not viewer_user:
            viewer_user = User(
                email=settings.FIRST_VIEWER_EMAIL,
                hashed_password=get_password_hash(settings.FIRST_VIEWER_PASSWORD),
                full_name="Compliance Viewer",
                role=UserRole.VIEWER,
                is_active=True
            )
            user_repo.create(viewer_user)
            print(f"Created viewer account: {settings.FIRST_VIEWER_EMAIL}")

        # 2. Seed Sample Dataset if none exists
        if dataset_repo.count() == 0:
            sample_csv_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../sample_data/synthetic_hr_sample.csv")
            )
            if os.path.exists(sample_csv_path):
                df = pd.read_csv(sample_csv_path)
                target_dest = os.path.join(settings.UPLOAD_DIR, "seeded_synthetic_hr_sample.csv")
                df.to_csv(target_dest, index=False)

                seed_dataset = Dataset(
                    name="Global Workforce HR Baseline",
                    description="Fictional enterprise HR record sample covering 1,200 employee records with demographic, compensation, tenure, and attrition indicators.",
                    original_filename="synthetic_hr_sample.csv",
                    file_path=target_dest,
                    file_size_bytes=os.path.getsize(target_dest),
                    row_count=len(df),
                    column_count=len(df.columns),
                    status="PROCESSED",
                    is_preprocessed=True,
                    quality_score=98.5,
                    user_id=admin_user.id
                )
                saved_dataset = dataset_repo.create(seed_dataset)

                # Seed columns
                cols = []
                for col in df.columns:
                    col_str = str(col)
                    series = df[col]
                    is_id = ("id" in col_str.lower())
                    is_num = pd.api.types.is_numeric_dtype(series)

                    if is_num:
                        stats = {
                            "min": float(series.min()),
                            "max": float(series.max()),
                            "mean": round(float(series.mean()), 2),
                            "median": round(float(series.median()), 2),
                            "std": round(float(series.std()), 2)
                        }
                        dtype_label = "numerical"
                    else:
                        stats = {
                            "categories_count": series.nunique(),
                            "top_categories": series.value_counts().head(5).to_dict()
                        }
                        dtype_label = "categorical"

                    cols.append(DatasetColumn(
                        dataset_id=saved_dataset.id,
                        column_name=col_str,
                        data_type=dtype_label,
                        is_identifier=is_id,
                        is_target=(col_str.lower() in ["attrition", "performance_rating"]),
                        is_nullable=False,
                        missing_count=0,
                        unique_count=series.nunique(),
                        sample_values=["***REDACTED***"] if is_id else [str(x) for x in series.head(3).tolist()],
                        stats=stats
                    ))
                dataset_repo.add_columns(cols)
                print(f"Seeded sample dataset '{seed_dataset.name}' with {len(cols)} columns.")

    finally:
        db.close()

if __name__ == "__main__":
    init_db()
