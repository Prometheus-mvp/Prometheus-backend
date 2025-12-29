"""Integration tests for API flows."""

from fastapi.testclient import TestClient


def test_health_endpoint():
    """Test health check endpoint."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint():
    """Test root endpoint."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_prompts_endpoint_requires_auth():
    """Test prompts endpoint requires authentication."""
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/v1/prompts", json={"query": "summarize last 2 hours"})

    # Should return 403 (no auth header)
    assert response.status_code == 403


def test_tasks_endpoint_requires_auth():
    """Test tasks endpoint requires authentication."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/api/v1/tasks")

    # Should return 403 (no auth header)
    assert response.status_code == 403
