"""
Dataset Upload and Validation Unit Tests.
"""

import io

def test_upload_valid_csv(client, analyst_token, sample_csv_content):
    headers = {"Authorization": f"Bearer {analyst_token}"}
    files = {"file": ("test_records.csv", sample_csv_content, "text/csv")}
    data = {"name": "Test HR Batch", "description": "Validation test dataset"}
    
    response = client.post("/api/v1/datasets/upload", headers=headers, files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["name"] == "Test HR Batch"
    assert res_data["row_count"] == 20
    assert res_data["column_count"] == 12
    assert "columns" in res_data
    assert "quality_report" in res_data
    assert res_data["quality_score"] > 80.0

def test_upload_invalid_extension_fails(client, analyst_token):
    headers = {"Authorization": f"Bearer {analyst_token}"}
    files = {"file": ("malicious.exe", b"binarycontent", "application/octet-stream")}
    
    response = client.post("/api/v1/datasets/upload", headers=headers, files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_upload_empty_file_fails(client, analyst_token):
    headers = {"Authorization": f"Bearer {analyst_token}"}
    files = {"file": ("empty.csv", b"", "text/csv")}
    
    response = client.post("/api/v1/datasets/upload", headers=headers, files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_delete_dataset(client, analyst_token, sample_csv_content):
    headers = {"Authorization": f"Bearer {analyst_token}"}
    files = {"file": ("to_delete.csv", sample_csv_content, "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", headers=headers, files=files)
    assert upload_res.status_code == 200
    dataset_id = upload_res.json()["id"]

    del_res = client.delete(f"/api/v1/datasets/{dataset_id}", headers=headers)
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/datasets/{dataset_id}", headers=headers)
    assert get_res.status_code == 404
