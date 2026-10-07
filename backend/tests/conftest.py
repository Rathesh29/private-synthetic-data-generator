import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.session import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.dataset import Dataset, DatasetColumn
from app.core.config import settings

# In-memory test SQLite engine
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db_session):
    user = User(
        email="test_admin@test.example.com",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Test Administrator",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def analyst_user(db_session):
    user = User(
        email="test_analyst@test.example.com",
        hashed_password=get_password_hash("AnalystPass123!"),
        full_name="Test HR Analyst",
        role=UserRole.HR_ANALYST,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def viewer_user(db_session):
    user = User(
        email="test_viewer@test.example.com",
        hashed_password=get_password_hash("ViewerPass123!"),
        full_name="Test Viewer",
        role=UserRole.VIEWER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_token(admin_user):
    return create_access_token(subject=admin_user.id, role=admin_user.role.value)

@pytest.fixture
def analyst_token(analyst_user):
    return create_access_token(subject=analyst_user.id, role=analyst_user.role.value)

@pytest.fixture
def viewer_token(viewer_user):
    return create_access_token(subject=viewer_user.id, role=viewer_user.role.value)

@pytest.fixture
def sample_csv_content():
    """Generates small fictional CSV bytes for testing."""
    df = pd.DataFrame({
        "employee_id": [f"EMP{i:03d}" for i in range(1, 21)],
        "age": [25, 32, 45, 29, 38, 52, 41, 33, 27, 49, 36, 28, 44, 39, 50, 31, 26, 47, 35, 42],
        "gender": ["Female", "Male", "Female", "Male", "Non-Binary"] * 4,
        "department": ["Engineering", "Sales", "HR", "Finance"] * 5,
        "job_role": ["Developer", "Representative", "Specialist", "Analyst"] * 5,
        "years_at_company": [2, 5, 12, 3, 7, 18, 9, 4, 1, 15, 6, 2, 11, 8, 16, 4, 1, 13, 6, 10],
        "salary": [75000, 62000, 58000, 71000, 89000, 115000, 94000, 65000, 54000, 108000,
                   82000, 60000, 98000, 87000, 112000, 67000, 56000, 102000, 84000, 91000],
        "performance_rating": [3, 4, 3, 2, 4, 5, 3, 4, 2, 4, 3, 3, 4, 4, 5, 3, 2, 4, 3, 4],
        "attendance_rate": [96.5, 94.2, 98.1, 91.0, 95.5, 99.0, 93.8, 96.0, 92.5, 97.4,
                            95.0, 94.8, 98.0, 96.2, 98.5, 95.1, 93.0, 97.0, 96.0, 94.5],
        "overtime": ["No", "Yes", "No", "Yes"] * 5,
        "work_life_balance": [3, 2, 4, 1, 3, 4, 2, 3, 2, 3, 3, 2, 3, 3, 4, 2, 1, 3, 3, 2],
        "attrition": ["No", "No", "No", "Yes", "No", "No", "No", "No", "Yes", "No",
                      "No", "No", "No", "No", "No", "No", "Yes", "No", "No", "No"]
    })
    return df.to_csv(index=False).encode("utf-8")
