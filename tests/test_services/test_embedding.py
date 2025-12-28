import pytest

from app.services.embedding import chunk_text, compute_content_hash


def test_chunk_text_splits():
    text = "a" * 10
    chunks = chunk_text(text, max_chars=4)
    assert chunks == ["aaaa", "aaaa", "aa"]


def test_compute_content_hash_deterministic():
    assert compute_content_hash("hello") == compute_content_hash("hello")
    assert compute_content_hash("hello") != compute_content_hash("world")

