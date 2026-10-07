# Architecture & Technical Design: Private Synthetic Data Generator for HR Records

## 1. High-Level Architecture

```
+-------------------------------------------------------------------------+
|                              REACT FRONTEND                             |
|  - Vite, Tailwind CSS, Recharts, Axios, Lucide Icons                   |
|  - Role-Based UI (Admin, HR Analyst, Viewer)                           |
|  - Interactive Privacy Budget Meter & Tradeoff Simulator               |
+------------------------------------+------------------------------------+
                                     |  REST API / JWT Bearer Tokens
                                     v
+-------------------------------------------------------------------------+
|                           FASTAPI BACKEND                               |
|  - Routers: Auth, Datasets, Preprocessing, Generation, Privacy, Audit   |
|  - Middleware: CORS, Redacting Logger, Global Exception Handler         |
|  - ORM: SQLAlchemy 2.0 with PostgreSQL & SQLite Fallback                |
+------------------+------------------------------+-----------------------+
                   |                              |
                   v                              v
+----------------------------------+  +-----------------------------------+
|      DATA PREPROCESSING & ML     |  |       DIFFERENTIAL PRIVACY        |
|  - Identifier Stripping          |  |  - Rényi DP Accountant (RDP)     |
|  - MinMax Scaler & Softmax OHE   |  |  - Subsampled Gaussian Mechanism  |
|  - Tabular VAE (Encoder/Decoder) |  |  - DP-SGD Optimizer Wrapper       |
|  - Baseline Gaussian Copula      |  |  - Cumulative Budget Enforcement  |
+------------------+---------------+  +-------------------+---------------+
                   |                                      |
                   +------------------+-------------------+
                                      |
                                      v
+-------------------------------------------------------------------------+
|                  STATISTICAL & PRIVACY RISK EVALUATION                  |
|  - Wasserstein Distance (Earth Mover's Distance)                        |
|  - Jensen-Shannon & Total Variation Divergence                          |
|  - Pearson & Spearman Correlation Frobenius Similarity                  |
|  - Nearest Neighbor / Distance to Closest Record (DCR) Analysis         |
|  - Simulated Shadow Membership Inference Attack Risk Metric             |
+-------------------------------------------------------------------------+
```

---

## 2. Machine Learning Generative Models

### Model 1: DP-SGD Tabular Variational Autoencoder (DP-Tabular-VAE)
- **Architecture**:
  - Encoder $q_\phi(z|x)$:
    - Linear(Input Dim $\to$ 64) $\to$ LeakyReLU(0.2)
    - Linear(64 $\to$ 32) $\to$ LeakyReLU(0.2)
    - Latent Heads: $\mu \in \mathbb{R}^{16}$, $\log \sigma^2 \in \mathbb{R}^{16}$
  - Reparameterization: $z = \mu + \epsilon \odot \sigma$, where $\epsilon \sim \mathcal{N}(0, I_{16})$
  - Decoder $p_\theta(x|z)$:
    - Linear(16 $\to$ 32) $\to$ LeakyReLU(0.2)
    - Linear(32 $\to$ 64) $\to$ LeakyReLU(0.2)
    - Linear(64 $\to$ Input Dim) $\to$ Sigmoid (normalized continuous outputs in $[0, 1]$)
- **Objective Function**:
  $$\mathcal{L}(x; \theta, \phi) = \mathbb{E}_{q_\phi(z|x)} [\|x - \hat{x}\|_2^2] + \beta \cdot D_{\mathrm{KL}}\left(q_\phi(z|x) \,||\, \mathcal{N}(0, I)\right)$$
- **DP-SGD Training Loop**:
  1. Microbatch/Sample gradient computation: $g_i = \nabla_{\theta, \phi} \ell(x_i)$.
  2. Per-sample $L_2$ gradient clipping: $\bar{g}_i = g_i \cdot \min\left(1, \frac{C}{\|g_i\|_2}\right)$.
  3. Calibrated Gaussian noise addition:
     $$\tilde{g} = \frac{1}{B} \left( \sum_{i=1}^B \bar{g}_i + \mathcal{N}(0, \sigma^2 C^2 I) \right)$$
  4. Adam optimizer update on model parameters $\theta, \phi$.

### Model 2: Baseline Gaussian Copula Synthesizer
- Estimates empirical correlation matrix and marginal distributions.
- Samples multivariate normal vectors with projected empirical ranks.
- **Explicit Classification**: Classified strictly as a statistical baseline without formal differential privacy guarantees.

---

## 3. Database Schema Overview

```
       +---------------+             +----------------+
       |     users     | 1         * |    datasets    |
       +---------------+<------------+----------------+
       | id            |             | id             |
       | email         |             | name           |
       | role          |             | quality_score  |
       +-------+-------+             +-------+--------+
               | 1                           | 1
               |                             |
               | *                           | *
       +-------v-------+             +-------v--------+
       |   audit_logs  |             | dataset_columns|
       +---------------+             +----------------+
       | action        |             | column_name    |
       | resource_type |             | data_type      |
       | ip_address    |             | is_identifier  |
       +---------------+             +----------------+
               ^                             ^
               | 1                           | 1
               |                             |
               | *                           | *
       +-------+-------+             +-------+--------+
       |generation_jobs| 1         * | model_versions |
       +---------------+<------------+----------------+
       | method        |             | version_tag    |
       | num_records   |             | epsilon_spent  |
       | status        |             | utility_score  |
       +-------+-------+             +----------------+
               | 1
               |
               | 1
       +-------v------------+
       | evaluation_reports |
       +--------------------+
       | overall_utility    |
       | privacy_risk       |
       | metrics_summary    |
       +--------------------+
```
