"""Tests for main application."""
import pytest
from fastapi.testclient import TestClient


def test_app_creation():
    """Test FastAPI app can be created."""
    from app.main import app
    
    assert app is not None
    assert app.title == "Prometheus v1 Backend API"


def test_health_check():
    """Test health check endpoint."""
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint."""
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_docs_available():
    """Test OpenAPI docs are available."""
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/docs")
    
    assert response.status_code == 200


def test_openapi_schema():
    """Test OpenAPI schema is generated."""
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/openapi.json")
    
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema

