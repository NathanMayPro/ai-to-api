import pytest
from fastapi.testclient import TestClient
import datetime
import time

def test_usage_tracking_unauthorized(client: TestClient):
    """Test that unauthorized requests are tracked"""
    response = client.get("/api/v1/test/sleep/1")
    assert response.status_code == 401

def test_usage_tracking_authorized(client: TestClient, auth_headers, usage_service):
    """Test that authorized requests are tracked with token info"""
    # Get the token from auth headers
    token = auth_headers["Authorization"].split(" ")[1]

    # Make a test request
    response = client.get("/api/v1/test/sleep/1", headers=auth_headers)
    response_data = response.json()
    assert response.status_code == 200

    # Wait briefly for usage record to be stored
    time.sleep(0.1)

    # Get user_id from the response
    user_id = response_data["user"]["id"]

    # Get usage stats
    usages = usage_service.get_user_usage(user_id)
    assert len(usages) > 0
    latest_usage = usages[-1]
    assert latest_usage.token == token

def test_usage_stats_filtering(client: TestClient, auth_headers, usage_service):
    """Test usage statistics with date filtering"""
    # Create some usage data
    response = client.get("/api/v1/test/sleep/1", headers=auth_headers)
    response_data = response.json()
    assert response.status_code == 200

    # Wait briefly for usage record to be stored
    time.sleep(0.1)

    # Get user_id from the response
    user_id = response_data["user"]["id"]

    # Test with date filters
    start_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
    end_date = datetime.datetime.now(datetime.timezone.utc)

    usages = usage_service.get_user_usage(
        user_id,
        start_date=start_date,
        end_date=end_date
    )
    assert len(usages) > 0

def test_usage_costs(client: TestClient, auth_headers, usage_service):
    """Test usage cost calculation"""
    # Create some usage data
    response = client.get("/api/v1/test/sleep/1", headers=auth_headers)
    response_data = response.json()
    assert response.status_code == 200

    # Wait briefly for usage record to be stored
    time.sleep(0.1)

    # Get user_id from the response
    user_id = response_data["user"]["id"]

    # Calculate costs
    costs = usage_service.calculate_user_costs(user_id)
    assert len(costs) > 0
    assert "total_cost" in costs[0] 