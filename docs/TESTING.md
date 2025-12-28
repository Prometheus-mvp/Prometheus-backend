# Testing Guide

## Overview

The Prometheus v1 Backend has comprehensive test coverage targeting **90%+ code coverage** across all modules.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── test_core/                     # Core module tests
│   ├── test_config.py
│   ├── test_crypto.py
│   ├── test_logging.py
│   └── test_security.py
├── test_db/                       # Database layer tests
│   ├── test_rls.py
│   └── test_session.py
├── test_models/                   # Model tests
│   ├── test_user.py
│   ├── test_linked_account.py
│   ├── test_event.py
│   ├── test_task.py
│   └── test_embedding.py
├── test_schemas/                  # Schema validation tests
│   ├── test_user.py
│   ├── test_task.py
│   └── test_connector.py
├── test_services/                 # Service layer tests
│   ├── test_embedding.py
│   ├── test_vector.py
│   ├── test_connector_base.py
│   └── test_connector_slack.py
├── test_agents/                   # Agent tests
│   ├── test_prompt_router.py
│   └── test_summarize_task_agents.py
├── test_api/                      # API endpoint tests
│   ├── test_prompts.py
│   ├── test_tasks.py
│   ├── test_calendar.py
│   └── test_connectors.py
├── test_jobs/                     # Background job tests
│   ├── test_ingestion.py
│   ├── test_embedding.py
│   ├── test_summarization.py
│   └── test_retention.py
├── test_utils/                    # Utility tests
│   └── test_datetime.py
├── test_integration/              # Integration tests
│   └── test_api_flow.py
└── test_main.py                   # Main app tests
```

## Running Tests

### Run all tests

```bash
pytest
```

### Run with coverage report

```bash
pytest --cov=app --cov-report=term-missing
```

### Run specific test file

```bash
pytest tests/test_core/test_crypto.py
```

### Run specific test function

```bash
pytest tests/test_core/test_crypto.py::test_encrypt_decrypt_roundtrip
```

### Run tests with markers

```bash
# Run only async tests
pytest -m asyncio

# Run integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Generate HTML coverage report

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Test Coverage Goals

- **Minimum**: 90% coverage across all modules
- **Target**: 95%+ coverage for critical paths (auth, crypto, connectors)
- **Exclusions**: Abstract methods, type checking blocks, `__repr__` methods

## Writing Tests

### Basic Test Structure

```python
"""Tests for module_name."""
import pytest
from unittest.mock import Mock, AsyncMock, patch


def test_function_name():
    """Test description."""
    # Arrange
    input_data = "test"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await async_function()
    assert result is not None
```

### Mocking External Dependencies

```python
@pytest.mark.asyncio
async def test_with_mock():
    """Test with mocked dependency."""
    with patch('app.module.external_service') as mock_service:
        mock_service.return_value = "mocked_value"
        
        result = await function_using_service()
        
        assert result == "expected"
        mock_service.assert_called_once()
```

### Testing API Endpoints

```python
def test_api_endpoint():
    """Test API endpoint."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/api/v1/endpoint")
    
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

## Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `mock_db_session`: Mock database session
- `mock_vector_results`: Mock vector search results
- `sample_user_id`: Sample UUID for tests

## Coverage Requirements

### Core Modules (95%+ target)
- `app/core/config.py`
- `app/core/crypto.py`
- `app/core/security.py`
- `app/core/logging.py`

### Database Layer (90%+ target)
- `app/db/engine.py`
- `app/db/session.py`
- `app/db/base.py`
- `app/db/rls.py`

### Models (85%+ target)
- All model files in `app/models/`

### Services (95%+ target)
- `app/services/vector.py`
- `app/services/embedding.py`
- All connector services

### Agents (95%+ target)
- `app/agents/base.py`
- `app/agents/prompt_router.py`
- `app/agents/summarize_graph.py`
- `app/agents/task_graph.py`

### API Endpoints (90%+ target)
- All endpoint files in `app/api/v1/`

### Jobs (90%+ target)
- All job files in `app/jobs/`

## Continuous Integration

Tests run automatically on:
- Every pull request
- Every commit to main
- Nightly builds

CI pipeline includes:
1. Lint checks (ruff, black)
2. Type checks (mypy)
3. Unit tests
4. Integration tests
5. Coverage report (must meet 90% minimum)

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Services**: Don't make real API calls or database connections
3. **Use Fixtures**: Share common setup via fixtures
4. **Descriptive Names**: Test names should describe what they test
5. **Arrange-Act-Assert**: Follow AAA pattern
6. **Test Edge Cases**: Include error paths and boundary conditions
7. **Keep Tests Fast**: Mock slow operations
8. **Update Tests**: When code changes, update tests

## Common Patterns

### Testing Error Handling

```python
def test_error_handling():
    """Test error is raised correctly."""
    with pytest.raises(ValueError) as exc_info:
        function_that_raises_error()
    
    assert "expected error message" in str(exc_info.value)
```

### Testing Database Operations

```python
@pytest.mark.asyncio
async def test_db_operation():
    """Test database operation."""
    mock_db = AsyncMock()
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    result = await db_function(mock_db)
    
    assert result is None
```

### Testing Authentication

```python
def test_requires_auth():
    """Test endpoint requires authentication."""
    client = TestClient(app)
    response = client.get("/api/v1/protected")
    
    assert response.status_code == 403
```

## Troubleshooting

### Tests failing locally but passing in CI
- Check Python version matches CI
- Ensure all dependencies are installed
- Clear pytest cache: `pytest --cache-clear`

### Coverage not reaching 90%
- Run `pytest --cov=app --cov-report=html`
- Open `htmlcov/index.html` to see uncovered lines
- Add tests for missing coverage

### Async tests hanging
- Ensure `pytest-asyncio` is installed
- Check `asyncio_mode = auto` in `pytest.ini`
- Use `@pytest.mark.asyncio` decorator

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)

