import pytest
import time
from fastapi.testclient import TestClient

def test_sleep_endpoint_unauthorized(client: TestClient):
    """Test that unauthorized access is rejected"""
    response = client.get("/api/v1/test/sleep/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_sleep_endpoint_authorized(client: TestClient, auth_headers, usage_service):
    """Test that authorized access works and usage is tracked"""
    sleep_time = 2
    start_time = time.time()
    
    response = client.get(f"/api/v1/test/sleep/{sleep_time}", headers=auth_headers)
    response_data = response.json()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_data["status"] == "OK"
    assert response_data["slept_for"] == sleep_time
    assert "user" in response_data
    assert elapsed_time >= sleep_time
    
    # Wait briefly for usage record to be stored
    time.sleep(0.1)
    
    # Get the token from auth headers
    token = auth_headers["Authorization"].split(" ")[1]
    
    # Get user_id from the response
    user_id = response_data["user"]["id"]
    
    # Verify usage tracking
    usages = usage_service.get_user_usage(user_id)
    assert len(usages) > 0
    latest_usage = usages[-1]
    assert latest_usage.token == token

@pytest.mark.parametrize("sleep_time", [-1, 0, 11])
def test_sleep_endpoint_invalid_duration(client: TestClient, auth_headers, sleep_time):
    """Test that invalid sleep durations are handled properly"""
    response = client.get(f"/api/v1/test/sleep/{sleep_time}", headers=auth_headers)
    assert response.status_code == 422  # Validation error

def test_sleep_endpoint_revoked_token(client: TestClient, auth_headers, token_service, sample_token):
    """Test that revoked tokens cannot access the endpoint"""
    # Verify initial token state
    token_before = token_service.get_token(sample_token.id)
    assert token_before.is_active is True
    
    # Revoke token
    success = token_service.deactivate_token(sample_token.id)
    assert success is True
    
    # Verify token was revoked
    token_after = token_service.get_token(sample_token.id)
    assert token_after.is_active is False
    
    # Wait briefly for changes to propagate
    time.sleep(0.1)
    
    # Try to use the revoked token
    response = client.get("/api/v1/test/sleep/1", headers=auth_headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Token is invalid or revoked" 