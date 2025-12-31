"""
Pytest configuration and shared fixtures for DOAMMO tests.
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import shutil
import os

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ["TESTING"] = "true"
    yield
    # Cleanup after all tests
    user_data_dir = Path("user_data")
    sessions_dir = Path("sessions")
    for dir_path in [user_data_dir, sessions_dir, TEST_DATA_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)


@pytest.fixture(autouse=True)
def test_data_dir():
    """Clean up wiki data between tests, but preserve sessions directory structure."""
    user_data_dir = Path("user_data")

    # Clean up user_data (wikis) before each test for isolation
    if user_data_dir.exists():
        shutil.rmtree(user_data_dir)

    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    yield TEST_DATA_DIR

    # Cleanup user_data after test
    if user_data_dir.exists():
        shutil.rmtree(user_data_dir)
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)

    # Note: sessions directory is cleaned up at session scope in setup_test_environment


@pytest.fixture
def client():
    """Create FastAPI test client."""
    # Import here to avoid issues with module-level imports
    from api_server import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_wiki_data():
    """Sample wiki data for testing."""
    return {
        "name": "test_wiki",  # API expects 'name' not 'wiki_name'
        "description": "A test wiki for automated testing"
    }


@pytest.fixture
def sample_session_data():
    """Sample session data for testing."""
    return {
        "session_id": "test_session_123",
        "messages": [
            {"role": "user", "content": "Hello, start a story"},
            {"role": "assistant", "content": "Once upon a time..."}
        ]
    }


@pytest.fixture
def sample_wiki_page_data():
    """Sample wiki page data for testing."""
    return {
        "content": "# Test Character\n\nA brave adventurer from the northern lands."
    }


@pytest.fixture
def sample_narrative_request():
    """Sample narrative generation request."""
    return {
        "user_input": "I explore the ancient ruins",
        "session_id": None
    }
