"""Tests for User model."""
import pytest
from uuid import uuid4
from app.models.user import User


def test_user_model_creation():
    """Test User model can be instantiated."""
    user_id = uuid4()
    user = User(
        id=user_id,
        email="test@example.com",
        display_name="Test User",
        timezone="America/New_York"
    )
    
    assert user.id == user_id
    assert user.email == "test@example.com"
    assert user.display_name == "Test User"
    assert user.timezone == "America/New_York"


def test_user_model_defaults():
    """Test User model default values."""
    user = User(id=uuid4())
    assert user.email is None
    assert user.display_name is None
    # timezone has server default, not set here

