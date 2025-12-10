import pytest
from fastapi.testclient import TestClient
import uuid

@pytest.fixture(scope="session", autouse=True)
def configure_faker():
    """Configure Faker at session start"""
    from faker import Faker
    Faker.seed(0)

@pytest.fixture(autouse=True)
def reset_faker_unique(faker):
    """Clear Faker unique between each test"""
    faker.unique.clear()

# ======================================================
# DATABASE FIXTURE
# ======================================================
@pytest.fixture(scope="function")
def db_session():
    """
    Fresh SQLite DB for every test.
    """
    from app.database import Base, test_engine, TestingSessionLocal

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================================================
# MANAGED DB SESSION FIXTURE (for test_user.py)
# ======================================================
@pytest.fixture
def managed_db_session(db_session):
    """
    Provides a managed session for tests that explicitly
    expect rollback behavior.
    """
    try:
        yield db_session
    except Exception:
        db_session.rollback()
        raise

# ======================================================
# FAKE USER FIXTURE
# ======================================================
@pytest.fixture
def fake_user_data():
    """Generate unique user data without relying on Faker's unique"""
    def _create():
        unique_id = uuid.uuid4().hex[:8]
        return {
            "first_name": "Test",
            "last_name": "User",
            "email": f"test_{unique_id}@example.com",
            "username": f"user_{unique_id}",
            "password": "TestPass123"
        }
    return _create


# ======================================================
# REAL USER FIXTURE
# ======================================================
@pytest.fixture
def test_user(db_session, fake_user_data):
    from app.models.user import User
    data = fake_user_data()
    user = User.register(db_session, data)
    db_session.commit()
    db_session.refresh(user)
    return user


# ======================================================
# FASTAPI CLIENT OVERRIDE
# ======================================================
@pytest.fixture(scope="function")
def client(db_session):
    from app.main import app
    from app.database import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ======================================================
# REAL FASTAPI SERVER FOR E2E TESTS
# ======================================================
import multiprocessing
import time
import requests
import uvicorn

@pytest.fixture(scope="session")
def fastapi_server():
    """
    Launch a real FastAPI server in a background process
    so E2E tests can hit actual HTTP endpoints.
    """

    from app.main import app

    host = "127.0.0.1"
    port = 8005
    base_url = f"http://{host}:{port}"

    # Function to run the server
    def run_server():
        uvicorn.run(app, host=host, port=port, log_level="info")

    # Start the server in a background process
    process = multiprocessing.Process(target=run_server, daemon=True)
    process.start()

    # Wait for server to become reachable
    for _ in range(20):
        try:
            requests.get(base_url + "/health")
            break
        except Exception:
            time.sleep(0.3)

    yield base_url

    # Shutdown server after tests
    process.terminate()
    process.join()


# ======================================================
# AUTH TOKEN FIXTURE (used in calculator tests)
# ======================================================
@pytest.fixture
def auth_token(test_user):
    """
    Create a fully populated JWT token so dependencies.py
    recognizes it as a complete UserResponse.
    """
    from app.auth.jwt import create_token
    from app.schemas.token import TokenType

    payload = {
        "sub": str(test_user.id),
        "username": test_user.username,
        "email": test_user.email,
        "first_name": test_user.first_name,
        "last_name": test_user.last_name,
        "is_active": test_user.is_active,
        "is_verified": test_user.is_verified,
    }

    return create_token(payload, TokenType.ACCESS)

@pytest.fixture
def managed_db_session(db_session):
    """Provide a managed session for tests expecting it."""
    try:
        yield db_session
    except Exception:
        db_session.rollback()
        raise