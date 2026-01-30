import pytest
from types import SimpleNamespace


@pytest.fixture
def dummy_session():
    """Simple dummy session with add/flush tracking."""
    calls = []

    class DummySession:
        def __init__(self):
            self.added = []

        async def execute(self, *args, **kwargs):
            calls.append(("execute", args, kwargs))
            return SimpleNamespace(
                all=lambda: [],
                scalars=lambda: [],
                fetchall=lambda: [],
                first=lambda: None,
            )

        async def flush(self):
            calls.append(("flush",))

        def add(self, obj):
            self.added.append(obj)
            calls.append(("add", obj))

    return DummySession()


@pytest.fixture
def dummy_vector_results():
    """Dummy vector results with recency scores for hybrid ranking."""

    class V:
        def __init__(
            self,
            object_type="event",
            object_id="obj",
            chunk_index=0,
            score=0.1,
            metadata=None,
            recency_score=0.8,
            semantic_score=0.9,
            final_score=0.85,
        ):
            self.object_type = object_type
            self.object_id = object_id
            self.chunk_index = chunk_index
            self.score = score
            self.metadata = metadata or {}
            self.id = "emb"
            # New fields for hybrid ranking
            self.recency_score = recency_score
            self.semantic_score = semantic_score
            self.final_score = final_score

    return [V()]
