"""Tests for user schemas."""
import pytest
from uuid import uuid4
from app.schemas.user import UserCreate, UserUpdate, UserResponse


def test_user_create():
    """Test UserCreate schema."""
    user_id = uuid4()
    user = UserCreate(
        id=user_id,
        email="test@example.com",
        display_name="Test User",
        timezone="UTC"
    )
    
    assert user.id == user_id
    assert user.email == "test@example.com"


def test_user_update():
    """Test UserUpdate schema."""
    user = UserUpdate(
        display_name="Updated Name",
        timezone="America/New_York"
    )
    
    assert user.display_name == "Updated Name"
    assert user.timezone == "America/New_York"


def test_user_response():
    """Test UserResponse schema."""
    from datetime import datetime, timezone
    
    user = UserResponse(
        id=uuid4(),
        email="test@example.com",
        display_name="Test",
        timezone="UTC",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    assert user.email == "test@example.com"

