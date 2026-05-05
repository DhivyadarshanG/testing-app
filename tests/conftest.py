"""Pytest configuration and fixtures."""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.utils.security import get_password_hash

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("adminpass123"),
        is_admin=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_token(client, test_user):
    """Get authentication token for test user."""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpass123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, admin_user):
    """Get authentication token for admin user."""
    response = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "adminpass123"}
    )
    return response.json()["access_token"]


def enable_bug(bug_id: str):
    """Helper to enable a specific bug."""
    os.environ[f"BUG_{bug_id}_ENABLED"] = "true"


def disable_bug(bug_id: str):
    """Helper to disable a specific bug."""
    os.environ[f"BUG_{bug_id}_ENABLED"] = "false"


def disable_all_bugs():
    """Helper to disable all bugs."""
    for i in range(1, 16):
        bug_id = f"{i:03d}"
        disable_bug(bug_id)

# Made with Bob
