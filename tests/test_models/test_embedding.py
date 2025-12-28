"""Tests for Embedding model."""
import pytest
from uuid import uuid4
from app.models.embedding import Embedding


def test_embedding_creation():
    """Test Embedding model can be instantiated."""
    user_id = uuid4()
    object_id = uuid4()
    fake_vector = [0.1] * 1536
    
    embedding = Embedding(
        user_id=user_id,
        object_type="event",
        object_id=object_id,
        chunk_index=0,
        embedding_model="text-embedding-ada-002",
        embedding_dim=1536,
        embedding=fake_vector,
        content_hash="abc123"
    )
    
    assert embedding.user_id == user_id
    assert embedding.object_type == "event"
    assert embedding.object_id == object_id
    assert embedding.chunk_index == 0
    assert embedding.embedding_model == "text-embedding-ada-002"
    assert embedding.embedding_dim == 1536
    assert len(embedding.embedding) == 1536


def test_embedding_multi_chunk():
    """Test Embedding with chunk_index."""
    user_id = uuid4()
    object_id = uuid4()
    fake_vector = [0.2] * 1536
    
    embedding = Embedding(
        user_id=user_id,
        object_type="note",
        object_id=object_id,
        chunk_index=2,
        embedding_model="text-embedding-ada-002",
        embedding_dim=1536,
        embedding=fake_vector,
        content_hash="def456"
    )
    
    assert embedding.chunk_index == 2

