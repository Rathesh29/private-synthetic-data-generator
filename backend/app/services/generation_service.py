"""
Synthetic Data Generation Service.
Orchestrates training, differential privacy accounting, synthetic record generation,
statistical/privacy evaluation, and export tracking.
"""

from datetime import datetime, timezone
import os
import uuid
from typing import Optional, List
import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.job import GenerationJob, JobStatus, GenerationMethod
from app.models.model_version import ModelVersion, PrivacyAccounting
from app.models.evaluation import EvaluationReport
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.generation import GenerationJobCreate, GenerationJobResponse
from app.schemas.evaluation import EvaluationReportResponse
from app.repositories.dataset_repo import DatasetRepository
from app.repositories.job_repo import JobRepository
from app.repositories.privacy_repo import PrivacyRepository
from app.repositories.audit_repo import AuditRepository
from app.ml.preprocessor import TabularDataPreprocessor
from app.ml.baseline_generator import BaselineStatisticalGenerator
from app.ml.dp_neural_generator import DPNeuralGenerator
from app.ml.evaluator import SyntheticDataEvaluator
from app.privacy.accountant import RDPAccountant
from app.services.privacy_service import PrivacyService

class GenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.dataset_repo = DatasetRepository(db)
        self.job_repo = JobRepository(db)
        self.privacy_repo = PrivacyRepository(db)
        self.audit_repo = AuditRepository(db)
        self.privacy_service = PrivacyService(db)

    def create_and_run_generation(
        self,
        job_in: GenerationJobCreate,
        user: User,
        ip_address: Optional[str] = None
    ) -> GenerationJobResponse:
        dataset = self.dataset_repo.get_by_id(job_in.dataset_id)
        if not dataset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source dataset not found")

        # Load real data
        if not os.path.exists(dataset.file_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset file missing on disk")

        if dataset.file_path.endswith(".csv"):
            real_df = pd.read_csv(dataset.file_path)
        else:
            real_df = pd.read_excel(dataset.file_path)

        dataset_size = len(real_df)
        effective_batch_size = min(job_in.batch_size, dataset_size)

        # Pre-check budget if DP method selected
        if job_in.method == GenerationMethod.DP_SGD_NEURAL:
            estimated_privacy = RDPAccountant.get_privacy_spent(
                dataset_size=dataset_size,
                batch_size=effective_batch_size,
                noise_multiplier=job_in.noise_multiplier or 1.1,
                epochs=job_in.epochs,
                target_delta=job_in.delta_target or 1e-5,
                clipping_norm=job_in.clipping_norm or 1.0
            )
            self.privacy_service.validate_budget_availability(estimated_privacy["epsilon"])

        # Create Job Record
        job = GenerationJob(
            name=job_in.name,
            dataset_id=dataset.id,
            user_id=user.id,
            method=job_in.method,
            num_records=job_in.num_records,
            status=JobStatus.PROCESSING,
            progress_percentage=10.0,
            epsilon_target=job_in.epsilon_target,
            delta_target=job_in.delta_target,
            clipping_norm=job_in.clipping_norm,
            noise_multiplier=job_in.noise_multiplier,
            epochs=job_in.epochs,
            batch_size=effective_batch_size,
            learning_rate=job_in.learning_rate,
            has_formal_dp_guarantee=(job_in.method == GenerationMethod.DP_SGD_NEURAL)
        )
        saved_job = self.job_repo.create_generation_job(job)

        try:
            # 1. Preprocess tabular data
            preprocessor = TabularDataPreprocessor({"drop_identifiers": True})
            preprocessor.fit(real_df)

            saved_job.progress_percentage = 30.0
            self.job_repo.update_generation_job(saved_job)

            # 2. Execute Generator
            if job_in.method == GenerationMethod.BASELINE_STATISTICAL:
                generator = BaselineStatisticalGenerator()
                generator.fit(real_df, preprocessor)
                synthetic_df = generator.generate(job_in.num_records)
                
                saved_job.has_formal_dp_guarantee = False
                saved_job.guarantee_disclaimer = generator.guarantee_statement
                saved_job.epsilon_spent = 0.0
                saved_job.delta_spent = 0.0
                training_loss_history = []
                arch_name = "Gaussian-Copula-Baseline"

            else: # DP_SGD_NEURAL
                generator = DPNeuralGenerator(
                    clipping_norm=job_in.clipping_norm or 1.0,
                    noise_multiplier=job_in.noise_multiplier or 1.1,
                    learning_rate=job_in.learning_rate,
                    epochs=job_in.epochs,
                    batch_size=effective_batch_size,
                    target_delta=job_in.delta_target or 1e-5
                )

                def on_progress(epoch, total_epochs, loss, eps):
                    pct = 30.0 + (epoch / float(total_epochs)) * 40.0
                    saved_job.progress_percentage = round(pct, 1)

                generator.fit(real_df, preprocessor, progress_callback=on_progress)
                synthetic_df = generator.generate(job_in.num_records)

                privacy_spent = generator.privacy_details
                saved_job.has_formal_dp_guarantee = True
                saved_job.epsilon_spent = privacy_spent["epsilon"]
                saved_job.delta_spent = privacy_spent["delta"]
                saved_job.guarantee_disclaimer = generator.guarantee_statement
                training_loss_history = generator.training_loss_history
                arch_name = "DP-Tabular-VAE"

            saved_job.progress_percentage = 75.0
            self.job_repo.update_generation_job(saved_job)

            # 3. Save Synthetic CSV to disk
            syn_filename = f"synthetic_{saved_job.id}_{uuid.uuid4().hex[:8]}.csv"
            syn_filepath = os.path.join(settings.SYNTHETIC_DIR, syn_filename)
            synthetic_df.to_csv(syn_filepath, index=False)
            saved_job.result_file_path = syn_filepath
            saved_job.result_row_count = len(synthetic_df)

            # 4. Run Statistical Quality & Privacy Risk Evaluation
            saved_job.progress_percentage = 85.0
            eval_results = SyntheticDataEvaluator.evaluate(real_df, synthetic_df)

            # 5. Create Model Version record
            model_ver = ModelVersion(
                name=f"{job_in.name} Model",
                version_tag=f"v_{saved_job.id}_{uuid.uuid4().hex[:6]}",
                architecture=arch_name,
                description=f"Generated via {job_in.method.value}",
                dataset_id=dataset.id,
                training_config={
                    "epochs": job_in.epochs,
                    "batch_size": effective_batch_size,
                    "learning_rate": job_in.learning_rate,
                    "clipping_norm": job_in.clipping_norm,
                    "noise_multiplier": job_in.noise_multiplier
                },
                epsilon_spent=saved_job.epsilon_spent,
                delta_spent=saved_job.delta_spent,
                has_formal_dp=saved_job.has_formal_dp_guarantee,
                training_loss_history=training_loss_history,
                utility_score=eval_results["overall_utility_score"],
                completed_at=datetime.now(timezone.utc)
            )
            saved_model = self.privacy_repo.create_model_version(model_ver)
            saved_job.model_version_id = saved_model.id

            # 6. Save Privacy Accounting if DP method
            if job_in.method == GenerationMethod.DP_SGD_NEURAL:
                total_prev = self.privacy_repo.get_total_epsilon_spent()
                record = PrivacyAccounting(
                    generation_job_id=saved_job.id,
                    model_version_id=saved_model.id,
                    user_id=user.id,
                    accountant_method="RDP_Subsampled_Gaussian",
                    epsilon_spent=saved_job.epsilon_spent,
                    delta_spent=saved_job.delta_spent,
                    sample_rate=effective_batch_size / float(dataset_size),
                    noise_multiplier=job_in.noise_multiplier or 1.1,
                    clipping_norm=job_in.clipping_norm or 1.0,
                    steps_computed=len(training_loss_history) * max(1, dataset_size // effective_batch_size),
                    cumulative_epsilon=round(total_prev + saved_job.epsilon_spent, 4),
                    cumulative_delta=job_in.delta_target or 1e-5,
                    assumptions_statement=generator.guarantee_statement
                )
                self.privacy_repo.create_privacy_record(record)

            # 7. Create Evaluation Report
            eval_report = EvaluationReport(
                generation_job_id=saved_job.id,
                dataset_id=dataset.id,
                overall_utility_score=eval_results["overall_utility_score"],
                privacy_risk_score=eval_results["privacy_risk_score"],
                metrics_summary=eval_results["metrics_summary"],
                column_metrics=eval_results["column_metrics"],
                correlation_metrics=eval_results["correlation_metrics"],
                distribution_comparisons=eval_results["distribution_comparisons"],
                nearest_neighbor_risk=eval_results["nearest_neighbor_risk"],
                membership_inference_risk=eval_results["membership_inference_risk"],
                limitations_disclosure=eval_results["limitations_disclosure"]
            )
            self.job_repo.create_evaluation_report(eval_report)

            # Mark completed
            saved_job.status = JobStatus.COMPLETED
            saved_job.progress_percentage = 100.0
            saved_job.completed_at = datetime.now(timezone.utc)
            self.job_repo.update_generation_job(saved_job)

            # Audit log
            self.audit_repo.create_log(AuditLog(
                user_id=user.id,
                user_email=user.email,
                action="SYNTHETIC_GENERATION_COMPLETED",
                resource_type="JOB",
                resource_id=str(saved_job.id),
                details={
                    "method": job_in.method.value,
                    "records_generated": job_in.num_records,
                    "epsilon_spent": saved_job.epsilon_spent,
                    "utility_score": eval_results["overall_utility_score"]
                },
                ip_address=ip_address
            ))

            return GenerationJobResponse.model_validate(saved_job)

        except Exception as e:
            saved_job.status = JobStatus.FAILED
            saved_job.error_message = str(e)
            saved_job.completed_at = datetime.now(timezone.utc)
            self.job_repo.update_generation_job(saved_job)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Generation job failed: {str(e)}"
            )

    def get_job(self, job_id: int) -> GenerationJobResponse:
        job = self.job_repo.get_generation_job(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return GenerationJobResponse.model_validate(job)

    def get_all_jobs(self, skip: int = 0, limit: int = 100) -> List[GenerationJobResponse]:
        jobs = self.job_repo.get_generation_jobs(skip=skip, limit=limit)
        return [GenerationJobResponse.model_validate(j) for j in jobs]

    def get_job_evaluation(self, job_id: int) -> EvaluationReportResponse:
        report = self.job_repo.get_evaluation_report_by_job_id(job_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation report not found for this job")
        return EvaluationReportResponse.model_validate(report)

    def export_synthetic_dataset(self, job_id: int, user: User, ip_address: Optional[str] = None) -> tuple[str, str]:
        job = self.job_repo.get_generation_job(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        if job.status != JobStatus.COMPLETED or not job.result_file_path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job result is not ready or failed")
        if not os.path.exists(job.result_file_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Synthetic result file missing on disk")

        download_name = f"synthetic_hr_data_job_{job.id}.csv"
        
        # Track export history and audit log
        from app.models.audit import ExportHistory
        exp = ExportHistory(
            generation_job_id=job.id,
            user_id=user.id,
            format="CSV",
            record_count=job.result_row_count
        )
        self.audit_repo.create_export(exp)

        self.audit_repo.create_log(AuditLog(
            user_id=user.id,
            user_email=user.email,
            action="EXPORT_SYNTHETIC_DATASET",
            resource_type="JOB",
            resource_id=str(job.id),
            details={"filename": download_name, "records": job.result_row_count},
            ip_address=ip_address
        ))

        return job.result_file_path, download_name
