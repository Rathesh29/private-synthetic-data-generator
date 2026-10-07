# Private Synthetic Data Generator for HR Records

A production-oriented, privacy-preserving web platform that generates realistic synthetic HR datasets from sensitive workforce records using **Differential Privacy (DP-SGD)**, **PyTorch Deep Variational Autoencoders (DP-Tabular-VAE)**, **Rényi Privacy Accounting**, and **Empirical Copula baselines**. 

Designed for enterprise HR analytics and people data teams to share and analyze synthetic data without exposing actual employee identities.

---

## Key Capabilities

1. **Authentication & Role-Based Access Control (RBAC)**:
   - Secure JWT tokens (Access & Refresh), Bcrypt password hashing.
   - Roles: `ADMIN`, `HR_ANALYST`, `VIEWER`.
   - Comprehensive compliance audit logs with PII sanitization.
2. **HR Dataset Ingestion & Quality Validation**:
   - Ingest CSV and Excel (`.xlsx`, `.xls`) files up to 25MB.
   - Automated schema detection, missing value analysis, duplicate row detection, and data quality scoring.
   - Automatic detection of personal direct identifiers (`employee_id`, badge, SSN, name).
3. **Data Preprocessing Pipeline**:
   - Stripping of direct identifiers from model training features.
   - MinMax and Robust normalization for continuous variables.
   - One-hot categorical encoding with reversible inverse transformers.
4. **Differential Privacy & Generative ML Engines**:
   - **DP-SGD Neural Engine**: PyTorch Tabular VAE trained with per-sample $L_2$ gradient clipping, calibrated Gaussian noise injection, and exact Rényi DP accounting.
   - **Baseline Statistical Engine**: Gaussian Copula empirical distribution synthesizer for speed benchmarks (clearly flagged as having no formal DP guarantee).
5. **Organizational Privacy Budget Management**:
   - Cumulative tracking of privacy expenditures $(\varepsilon, \delta)$ against organizational caps.
   - Blocks jobs exceeding budget limits to prevent mathematical leakage.
   - Real-time privacy-utility trade-off estimation preview.
6. **Data Utility & Privacy Risk Assessment**:
   - Feature-level statistical comparison (Mean, Median, Std Dev, Wasserstein distance, TVD).
   - Pairwise correlation matrix preservation (Frobenius norm similarity).
   - Nearest Neighbor / Distance to Closest Record (DCR) analysis to detect exact memorization.
   - Empirical Membership Inference Risk evaluation vs. random baseline.
   - Export approved synthetic datasets as CSV.

---

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, PyJWT, Bcrypt
- **Machine Learning & Privacy**: PyTorch 2.x, pandas, NumPy, scikit-learn, SciPy
- **Frontend**: React 18, Vite, Tailwind CSS, Recharts, Axios, Lucide React
- **Database**: PostgreSQL (with automatic SQLite fallback for zero-dependency local dev)
- **Deployment**: Docker, Docker Compose, Nginx
- **Testing**: Pytest (19 unit & integration tests)

---

## Demo Accounts

The database automatically seeds the following demo users upon first startup:

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@hrprivacy.org` | `Admin@123456` | Full system control, audit logs, dataset deletion, user management |
| **HR Analyst** | `analyst@hrprivacy.org` | `Analyst@123456` | Upload datasets, run preprocessing, train models, export synthetic CSVs |
| **Viewer** | `viewer@hrprivacy.org` | `Viewer@123456` | View dashboards, model versions, evaluation reports (read-only) |

*Tip: The web interface includes 1-click demo login buttons on the login screen.*

---

## Local Development Setup (Windows PowerShell / VS Code)

### 1. Prerequisites
- Python 3.12+ installed (`python --version`)
- Node.js 18+ and npm installed (`node --version`)
- Git

### 2. Backend Setup
Open Windows PowerShell in the project directory:

```powershell
cd private-synthetic-hr/backend

# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 3. Initialize and seed database
python -m app.database.seed

# 4. Run backend server
uvicorn app.main:app --reload --port 8000
```

The FastAPI backend will be available at:
- API Base URL: `http://localhost:8000/api/v1`
- Interactive Swagger Documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 3. Frontend Setup
In a new terminal window:

```powershell
cd private-synthetic-hr/frontend

# 1. Install npm packages
npm install

# 2. Run Vite dev server
npm run dev
```

The web application will open at:
- Web App: `http://localhost:5173`

---

## Running with Docker Compose

You can launch the complete production stack (PostgreSQL + FastAPI + React with Nginx) with a single command:

```powershell
cd private-synthetic-hr
docker compose up --build
```

- Web Interface: `http://localhost:3000`
- Backend API & Docs: `http://localhost:8000/docs`

---

## Running the Automated Test Suite

Run the complete Pytest suite covering authentication, validation, preprocessing, privacy accounting, ML generation, and end-to-end API workflows:

```powershell
cd private-synthetic-hr/backend
$env:PYTHONPATH="."
.\.venv\Scripts\pytest tests -v
```

All 19 tests will execute and validate the complete pipeline:
```
tests/test_api_integration.py::test_full_pipeline_workflow PASSED
tests/test_auth.py::test_user_registration PASSED
tests/test_auth.py::test_login_success PASSED
tests/test_auth.py::test_rbac_admin_route_allowed_for_admin PASSED
tests/test_ml_generation.py::test_baseline_generator PASSED
tests/test_ml_generation.py::test_dp_neural_generator_training_and_guarantee PASSED
tests/test_ml_generation.py::test_evaluator_metrics PASSED
tests/test_preprocessing.py::test_preprocessor_detection_and_transform PASSED
tests/test_privacy_accounting.py::test_rdp_accountant_calculation PASSED
tests/test_privacy_accounting.py::test_higher_noise_yields_lower_epsilon PASSED
tests/test_validation.py::test_upload_valid_csv PASSED
tests/test_validation.py::test_delete_dataset PASSED
======================= 19 passed in 9.51s =======================
```

---

## Sample API Requests & Responses

### 1. Authenticate & Obtain JWT
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "analyst@hrprivacy.org",
  "password": "Analyst@123456"
}
```
**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "email": "analyst@hrprivacy.org",
    "full_name": "Senior HR Analyst",
    "role": "HR_ANALYST"
  }
}
```

### 2. Trigger DP-SGD Synthetic Generation Job
```http
POST /api/v1/generation/run
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "name": "Q3 Engineering Compensation Synthesis",
  "dataset_id": 1,
  "method": "DP_SGD_NEURAL",
  "num_records": 1000,
  "clipping_norm": 1.0,
  "noise_multiplier": 1.1,
  "epochs": 20,
  "batch_size": 64,
  "learning_rate": 0.001
}
```
**Response:**
```json
{
  "id": 1,
  "name": "Q3 Engineering Compensation Synthesis",
  "dataset_id": 1,
  "method": "DP_SGD_NEURAL",
  "num_records": 1000,
  "status": "COMPLETED",
  "has_formal_dp_guarantee": true,
  "epsilon_spent": 1.1423,
  "delta_spent": 0.00001,
  "result_row_count": 1000,
  "guarantee_disclaimer": "FORMAL DIFFERENTIAL PRIVACY GUARANTEE: Trained under (1.1423, 1e-05)-Differential Privacy using DP-SGD with per-sample L2 clipping norm 1.0 and Gaussian noise multiplier 1.1."
}
```

### 3. Fetch Evaluation Report
```http
GET /api/v1/evaluation/job/1
Authorization: Bearer <TOKEN>
```
**Response:**
```json
{
  "overall_utility_score": 89.4,
  "privacy_risk_score": 12.0,
  "metrics_summary": {
    "columns_evaluated": 11,
    "average_column_fidelity": 91.2,
    "correlation_matrix_fidelity": 85.3,
    "exact_replica_detected": false
  },
  "nearest_neighbor_risk": {
    "exact_replica_count": 0,
    "median_distance_to_closest_record": 0.428,
    "risk_interpretation": "Safe: No exact duplicates detected and adequate distance maintained."
  },
  "membership_inference_risk": {
    "simulated_attack_accuracy_pct": 51.4,
    "threat_level": "Low"
  }
}
```

---

## Differential Privacy Tuning Guide

| Objective | Recommended Noise ($\sigma$) | Clipping Norm ($C$) | Target ($\varepsilon$) | Expected Utility |
| :--- | :--- | :--- | :--- | :--- |
| **High Security / Sensitive Health or PII** | $2.0 - 2.5$ | $0.8 - 1.0$ | $\varepsilon < 0.5$ | $\sim 72-78\%$ |
| **Balanced Enterprise Analytics (Recommended)** | $1.0 - 1.2$ | $1.0$ | $\varepsilon \in [0.8, 1.5]$ | $\sim 88-93\%$ |
| **High Fidelity Modeling** | $0.5 - 0.7$ | $1.2$ | $\varepsilon \in [2.5, 4.5]$ | $\sim 94-98\%$ |

---

## Security Best Practices Enforced
- **Zero Raw PII Exposure**: Direct employee identifiers (`employee_id`, names) are automatically detected and omitted from model training.
- **Redacting Logger**: Console and disk logs scrub passwords, tokens, and employee IDs using regex masking.
- **Immutability of Audit Trails**: Every data ingestion, parameter change, and dataset export is cryptographically recorded with client metadata.
