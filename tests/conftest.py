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
    class V:
        def __init__(
            self,
            object_type="event",
            object_id="obj",
            chunk_index=0,
            score=0.1,
            metadata=None,
        ):
            self.object_type = object_type
            self.object_id = object_id
            self.chunk_index = chunk_index
            self.score = score
            self.metadata = metadata or {}
            self.id = "emb"

    return [V()]
