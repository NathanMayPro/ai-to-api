import pytest
import logging
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models.token import Token
from app.services.token_service import TokenService
from app.services.usage_service import UsageService
import mongomock
import motor.motor_asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_logging():
    yield

class MockMotorClient:
    def __init__(self):
        self.mock_db = mongomock.MongoClient().db
        self.db = self.mock_db

    def get_database(self):
        return self.db

@pytest.fixture
async def test_db():
    """Create a mock MongoDB database for testing"""
    mock_client = MockMotorClient()
    db = mock_client.get_database()
    # Clear all collections before tests
    db.users.delete_many({})
    db.tokens.delete_many({})
    db.usage.delete_many({})
    return db

@pytest.fixture
def override_get_db(test_db):
    """Override the database dependency"""
    async def _override_get_db():
        return test_db
    app.dependency_overrides[get_database] = _override_get_db
    yield
    app.dependency_overrides = {}

@pytest.fixture
async def client(override_get_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def test_user():
    return {
        "email": settings.TEST_EMAIL,
        "username": settings.TEST_USERNAME,
        "password": settings.TEST_PASSWORD
    }

@pytest.fixture
def admin_user():
    return {
        "email": "admin@example.com",
        "username": "admin",
        "password": "adminpass123"
    }

@pytest.fixture
def normal_user():
    return {
        "email": "normal@example.com",
        "username": "normal",
        "password": "normalpass123"
    }

@pytest.fixture
def token_service():
    return TokenService()

@pytest.fixture
def usage_service():
    return UsageService()

@pytest.fixture
async def admin_token(client, admin_user, test_db):
    """Get token for admin user (first user registered)"""
    # Register admin user (first user is automatically admin)
    register_response = await client.post("/api/v1/auth/register", json=admin_user)
    assert register_response.status_code == 200
    
    # Login to get token
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": admin_user["email"],
            "password": admin_user["password"]
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
async def normal_token(client, normal_user, admin_token, test_db):
    """Get token for normal user (second user registered)"""
    # Register normal user (second user is not admin)
    register_response = await client.post("/api/v1/auth/register", json=normal_user)
    assert register_response.status_code == 200
    
    # Login to get token
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": normal_user["email"],
            "password": normal_user["password"]
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
async def auth_headers_and_token(client, test_user, test_db):
    """Returns both auth headers and the token object"""
    # Register user
    register_response = await client.post("/api/v1/auth/register", json=test_user)
    
    # Login to get token
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers, token

@pytest.fixture
async def auth_headers(auth_headers_and_token):
    """Returns just the auth headers"""
    headers, _ = await auth_headers_and_token
    return headers

@pytest.fixture
async def sample_token(auth_headers_and_token) -> Token:
    """Returns just the token object"""
    _, token = await auth_headers_and_token
    return token 