import pytest
from fastapi import HTTPException
from httpx import AsyncClient
import mongomock

from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService

@pytest.mark.asyncio
async def test_first_user_is_admin(client: AsyncClient, test_db):
    """Test that the first user created becomes an admin"""
    user_data = {
        "email": "first@example.com",
        "username": "firstuser",
        "password": "testpass123"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["is_admin"] is True

@pytest.mark.asyncio
async def test_second_user_not_admin(client: AsyncClient, test_db):
    """Test that subsequent users are not admins by default"""
    # Create first user
    first_user = {
        "email": "first@example.com",
        "username": "firstuser",
        "password": "testpass123"
    }
    await client.post("/api/v1/auth/register", json=first_user)
    
    # Create second user
    second_user = {
        "email": "second@example.com",
        "username": "seconduser",
        "password": "testpass123"
    }
    response = await client.post("/api/v1/auth/register", json=second_user)
    assert response.status_code == 200
    assert response.json()["is_admin"] is False

@pytest.mark.asyncio
async def test_admin_get_users(client: AsyncClient, test_db, admin_token):
    """Test that admin can get list of all users"""
    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0

@pytest.mark.asyncio
async def test_non_admin_get_users_forbidden(client: AsyncClient, test_db, normal_token):
    """Test that non-admin users cannot access user list"""
    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {normal_token}"}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_admin_get_users_costs(client: AsyncClient, test_db, admin_token):
    """Test that admin can get users costs"""
    response = await client.get(
        "/api/v1/users/costs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    user_costs = response.json()
    assert isinstance(user_costs, list)
    for user_cost in user_costs:
        assert "user_id" in user_cost
        assert "email" in user_cost
        assert "username" in user_cost
        assert "total_cost" in user_cost

@pytest.mark.asyncio
async def test_non_admin_get_users_costs_forbidden(client: AsyncClient, test_db, normal_token):
    """Test that non-admin users cannot access user costs"""
    response = await client.get(
        "/api/v1/users/costs",
        headers={"Authorization": f"Bearer {normal_token}"}
    )
    assert response.status_code == 403 