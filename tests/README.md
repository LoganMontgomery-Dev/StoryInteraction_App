# DOAMMO Tests

Automated test suite for the DOAMMO Narrative Engine.

## Overview

This directory contains comprehensive tests for the DOAMMO backend API, covering:
- Wiki CRUD operations
- Narrative generation
- Session management
- Error handling

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_wiki_api.py         # Wiki endpoint tests
├── test_narrative_api.py    # Narrative endpoint tests
└── README.md                # This file
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_wiki_api.py
pytest tests/test_narrative_api.py
```

### Run Specific Test Class

```bash
pytest tests/test_wiki_api.py::TestWikiCRUD
pytest tests/test_wiki_api.py::TestWikiPages
```

### Run Specific Test

```bash
pytest tests/test_wiki_api.py::TestWikiCRUD::test_create_wiki
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

### Run Only Fast Tests (skip slow ones)

```bash
pytest -m "not slow"
```

### Run Tests by Marker

```bash
pytest -m api       # Run all API tests
pytest -m wiki      # Run all wiki tests
pytest -m unit      # Run unit tests only
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.wiki` - Wiki functionality tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow running tests

## Test Fixtures

### Available Fixtures

- `client` - FastAPI test client for making HTTP requests
- `test_data_dir` - Temporary directory for test data
- `sample_wiki_data` - Sample wiki creation data
- `sample_session_data` - Sample session data
- `sample_wiki_page_data` - Sample wiki page content
- `sample_narrative_request` - Sample narrative generation request

### Using Fixtures

```python
def test_example(client, sample_wiki_data):
    response = client.post("/wiki/create", json=sample_wiki_data)
    assert response.status_code == 200
```

## Test Coverage

### Current Coverage

- ✅ Wiki CRUD operations (create, read, update, delete)
- ✅ Wiki page management
- ✅ Session save/load functionality
- ✅ Narrative generation (with mocking)
- ✅ Error handling for non-existent resources
- ✅ Health check endpoint

### Areas Not Yet Covered

- ⏳ ChromaDB integration
- ⏳ LangGraph workflow details
- ⏳ Vault reading functionality
- ⏳ Actual Claude API calls (should remain mocked)

## Writing New Tests

### Test Template

```python
import pytest


@pytest.mark.api
class TestNewFeature:
    """Test description."""

    def test_feature_basic(self, client):
        """Test basic functionality."""
        response = client.get("/endpoint")
        assert response.status_code == 200

    def test_feature_error_case(self, client):
        """Test error handling."""
        response = client.get("/endpoint/invalid")
        assert response.status_code == 404
```

### Best Practices

1. **Use descriptive test names** - Name should describe what is being tested
2. **One assertion per concept** - Test one thing at a time
3. **Use fixtures** - Reuse common setup code
4. **Test error cases** - Don't just test the happy path
5. **Mock external services** - Don't call real APIs in tests
6. **Clean up** - Fixtures should clean up after themselves

## Continuous Integration

### GitHub Actions (Recommended Setup)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest -v
```

## Troubleshooting

### Tests Fail with Import Errors

Make sure you're running tests from the project root:
```bash
cd DOAMMO_APP
pytest
```

### Tests Can't Find api_server Module

Ensure the project root is in PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

Or run with:
```bash
python -m pytest
```

### Database/File Conflicts

Tests use a separate `test_data` directory that's cleaned up automatically. If you see file conflicts:

```bash
rm -rf tests/test_data
pytest
```

## Maintenance

### Adding New Tests

1. Create test file in `tests/` with `test_*.py` pattern
2. Import pytest and necessary fixtures
3. Write test classes and methods
4. Run tests to verify

### Updating Fixtures

Edit `conftest.py` to add or modify shared fixtures.

### Skipping Tests Temporarily

```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
