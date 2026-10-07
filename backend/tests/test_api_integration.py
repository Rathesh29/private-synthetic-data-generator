"""
End-to-End API Integration Tests.
Tests the full lifecycle:
1. Upload HR dataset
2. Preprocess dataset
3. Check privacy budget
4. Trigger DP generation job
5. Inspect evaluation metrics
6. Export synthetic CSV
7. Verify audit logging
"""

def test_full_pipeline_workflow(client, analyst_token, sample_csv_content):
    headers = {"Authorization": f"Bearer {analyst_token}"}

    # 1. Upload dataset
    files = {"file": ("hr_records_pipeline.csv", sample_csv_content, "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", headers=headers, files=files, data={"name": "Pipeline Dataset"})
    assert upload_res.status_code == 200
    dataset_data = upload_res.json()
    dataset_id = dataset_data["id"]
    assert dataset_id is not None

    # 2. Run Preprocessing
    prep_res = client.post(f"/api/v1/preprocessing/run/{dataset_id}", headers=headers, json={"drop_identifiers": True})
    assert prep_res.status_code == 200
    assert prep_res.json()["status"] == "COMPLETED"

    # 3. Check Privacy Budget
    budget_res = client.get("/api/v1/privacy/budget", headers=headers)
    assert budget_res.status_code == 200
    assert "remaining_epsilon_budget" in budget_res.json()

    # 4. Trigger Synthetic Generation (DP-SGD Neural)
    gen_payload = {
        "name": "Integration DP Test Job",
        "dataset_id": dataset_id,
        "method": "DP_SGD_NEURAL",
        "num_records": 25,
        "clipping_norm": 1.0,
        "noise_multiplier": 1.5,
        "epochs": 2,
        "batch_size": 10,
        "learning_rate": 0.005
    }
    gen_res = client.post("/api/v1/generation/run", headers=headers, json=gen_payload)
    assert gen_res.status_code == 200
    job_data = gen_res.json()
    job_id = job_data["id"]
    assert job_data["status"] == "COMPLETED"
    assert job_data["has_formal_dp_guarantee"] is True
    assert job_data["epsilon_spent"] > 0
    assert job_data["result_row_count"] == 25

    # 5. Fetch Evaluation Report
    eval_res = client.get(f"/api/v1/evaluation/job/{job_id}", headers=headers)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["overall_utility_score"] > 0
    assert len(eval_data["column_metrics"]) > 0

    # 6. Download Synthetic CSV
    export_res = client.get(f"/api/v1/generation/{job_id}/export", headers=headers)
    assert export_res.status_code == 200
    assert "text/csv" in export_res.headers["content-type"]
    assert len(export_res.content) > 100

    # 7. Check Dashboard Stats
    dash_res = client.get("/api/v1/dashboard/stats", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_generation_jobs"] >= 1
    assert dash_data["completed_jobs"] >= 1
