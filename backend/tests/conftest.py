"""
Pytest configuration and fixtures for testing
"""

import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.core.config import settings
from app.models import *  # Import all models

# Test database URL - use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    # Create tables
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    # Clean up
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client"""
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    
    client = TestClient(app)
    yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_department(session: Session):
    """Create a sample department for testing"""
    from app.models import Department
    
    department = Department(
        name="測試部門",
        code="TEST",
        description="用於測試的部門",
        is_active=True
    )
    session.add(department)
    session.commit()
    session.refresh(department)
    return department

@pytest.fixture  
def sample_user(session: Session, sample_department):
    """Create a sample user for testing"""
    from app.models import User
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        username="testuser",
        name="測試使用者",
        email="test@example.com",
        employee_id="TEST001",
        role="employee",
        department_id=sample_department.id,
        hashed_password=pwd_context.hash("testpass"),
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture
def sample_admin_user(session: Session, sample_department):
    """Create a sample admin user for testing"""
    from app.models import User
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        username="admin",
        name="管理員",
        email="admin@example.com",
        employee_id="ADMIN001",
        role="admin",
        department_id=sample_department.id,
        hashed_password=pwd_context.hash("adminpass"),
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture
def sample_rule_pack(session: Session):
    """Create a sample rule pack for testing"""
    from app.models import RulePack
    from datetime import date
    
    rule_pack = RulePack(
        name="測試規則包",
        version="1.0",
        description="用於測試的規則包",
        status="active",
        scope="company",
        effective_from=date(2024, 1, 1)
    )
    session.add(rule_pack)
    session.commit()
    session.refresh(rule_pack)
    return rule_pack

@pytest.fixture
def sample_rule(session: Session, sample_rule_pack):
    """Create a sample rule for testing"""
    from app.models import Rule
    
    rule = Rule(
        rule_pack_id=sample_rule_pack.id,
        name="測試規則",
        code="TEST_RULE",
        description="用於測試的規則",
        category="test",
        base_score=10,
        weight=1.0,
        evidence_required=False,
        active=True
    )
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return rule

@pytest.fixture
def auth_headers(client: TestClient, sample_user):
    """Get authentication headers for API testing"""
    # Login to get token
    response = client.post(
        "/api/auth/login",
        data={"username": sample_user.username, "password": "testpass"}
    )
    assert response.status_code == 200
    token_data = response.json()
    
    return {"Authorization": f"Bearer {token_data['access_token']}"}

@pytest.fixture
def admin_auth_headers(client: TestClient, sample_admin_user):
    """Get admin authentication headers for API testing"""
    # Login to get token
    response = client.post(
        "/api/auth/login",
        data={"username": sample_admin_user.username, "password": "adminpass"}
    )
    assert response.status_code == 200
    token_data = response.json()
    
    return {"Authorization": f"Bearer {token_data['access_token']}"}

class TestHelpers:
    """Helper utilities for testing"""
    
    @staticmethod
    def assert_dict_contains(actual: dict, expected: dict):
        """Assert that actual dict contains all key-value pairs from expected dict"""
        for key, value in expected.items():
            assert key in actual
            assert actual[key] == value
    
    @staticmethod
    def assert_response_success(response):
        """Assert that API response is successful"""
        assert 200 <= response.status_code < 300
        
    @staticmethod
    def assert_response_error(response, status_code: int = None):
        """Assert that API response contains error"""
        if status_code:
            assert response.status_code == status_code
        else:
            assert response.status_code >= 400

@pytest.fixture
def helpers():
    """Provide test helpers"""
    return TestHelpers