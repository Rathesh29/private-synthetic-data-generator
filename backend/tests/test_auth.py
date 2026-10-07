"""
Authentication and Role-Based Access Control Unit Tests.
"""

from app.models.user import UserRole

def test_user_registration(client):
    payload = {
        "email": "new_analyst@test.example.com",
        "password": "SecurePassword123!",
        "full_name": "New Analyst",
        "role": "HR_ANALYST"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new_analyst@test.example.com"
    assert data["role"] == "HR_ANALYST"
    assert "password" not in data

def test_duplicate_registration_fails(client):
    payload = {
        "email": "duplicate@test.example.com",
        "password": "SecurePassword123!",
        "full_name": "First User",
        "role": "HR_ANALYST"
    }
    r1 = client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 200
    r2 = client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 400

def test_login_success(client, analyst_user):
    payload = {
        "email": analyst_user.email,
        "password": "AnalystPass123!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == analyst_user.email

def test_login_invalid_password(client, analyst_user):
    payload = {
        "email": analyst_user.email,
        "password": "WrongPassword!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401

def test_get_current_user_profile(client, analyst_token):
    headers = {"Authorization": f"Bearer {analyst_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == UserRole.HR_ANALYST.value

def test_rbac_admin_route_forbidden_for_analyst(client, analyst_token):
    headers = {"Authorization": f"Bearer {analyst_token}"}
    response = client.get("/api/v1/audit/logs", headers=headers)
    assert response.status_code == 403

def test_rbac_admin_route_allowed_for_admin(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/v1/audit/logs", headers=headers)
    assert response.status_code == 200
