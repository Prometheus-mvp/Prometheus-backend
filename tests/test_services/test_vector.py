import pytest

from app.services.vector import VectorStore, VectorRecord


@pytest.mark.asyncio
async def test_vector_record_creation():
    vr = VectorRecord(
        id="1",
        object_type="event",
        object_id="obj",
        chunk_index=0,
        score=0.1,
        metadata={"k": "v"},
    )
    assert vr.object_type == "event"
    assert vr.score == 0.1


@pytest.mark.asyncio
async def test_store_embedding_statement(monkeypatch, dummy_session):
    vs = VectorStore()

    async def fake_execute(stmt):
        # ensure key fields are present in compiled params
        params = stmt.compile().params
        assert params["user_id"] == "u1"
        assert params["object_type"] == "event"
        return None

    monkeypatch.setattr(dummy_session, "execute", fake_execute)
    await vs.store_embedding(
        dummy_session,
        user_id="u1",
        object_type="event",
        object_id="obj",
        chunk_index=0,
        embedding=[0.1, 0.2],
        embedding_model="text-embedding-ada-002",
        content_hash="hash",
        metadata={},
    )

