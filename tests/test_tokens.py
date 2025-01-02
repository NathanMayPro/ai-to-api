import pytest
from fastapi.testclient import TestClient
from app.models.token import Token

def test_list_tokens_unauthorized(client: TestClient):
    """Test that unauthorized users cannot list tokens"""
    response = client.get("/api/v1/tokens/")
    assert response.status_code == 401

def test_list_tokens(client: TestClient, auth_headers, sample_token):
    """Test listing user tokens"""
    response = client.get("/api/v1/tokens/", headers=auth_headers)
    assert response.status_code == 200
    tokens = response.json()
    assert len(tokens) > 0
    
    # Find our token in the list
    found_token = None
    for token in tokens:
        if token["id"] == sample_token.id:
            found_token = token
            break
            
    assert found_token is not None
    assert found_token["token"] == sample_token.token
    assert found_token["user_id"] == sample_token.user_id

def test_get_token_details(client: TestClient, auth_headers, sample_token):
    """Test getting specific token details"""
    response = client.get(f"/api/v1/tokens/{sample_token.id}", headers=auth_headers)
    assert response.status_code == 200
    token_data = response.json()
    assert token_data["id"] == sample_token.id
    assert token_data["token"] == sample_token.token

def test_get_nonexistent_token(client: TestClient, auth_headers):
    """Test getting a token that doesn't exist"""
    response = client.get("/api/v1/tokens/nonexistent", headers=auth_headers)
    assert response.status_code == 404

def test_revoke_token(client: TestClient, auth_headers, sample_token):
    """Test revoking a token"""
    response = client.delete(f"/api/v1/tokens/{sample_token.id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify token is deactivated
    response = client.get("/api/v1/test/sleep/1", headers=auth_headers)
    assert response.status_code == 401 