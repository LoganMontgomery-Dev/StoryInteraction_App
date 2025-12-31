"""
Tests for Wiki API endpoints.
"""
import pytest


@pytest.mark.api
@pytest.mark.wiki
class TestWikiCRUD:
    """Test wiki CRUD operations."""

    def test_create_wiki(self, client, sample_wiki_data):
        """Test creating a new wiki."""
        response = client.post("/wiki/create", json=sample_wiki_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "wiki" in data
        assert data["wiki"]["name"] == sample_wiki_data["name"]

    def test_create_wiki_duplicate(self, client, sample_wiki_data):
        """Test creating a wiki with duplicate name."""
        # Create first wiki
        client.post("/wiki/create", json=sample_wiki_data)

        # Try to create duplicate
        response = client.post("/wiki/create", json=sample_wiki_data)

        assert response.status_code == 400
        data = response.json()
        # FastAPI HTTPException returns {"detail": "message"}
        assert "detail" in data
        assert "already exists" in data["detail"].lower()

    def test_list_wikis_empty(self, client):
        """Test listing wikis when none exist."""
        response = client.get("/wiki/list")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["wikis"], list)

    def test_list_wikis_with_data(self, client, sample_wiki_data):
        """Test listing wikis after creating some."""
        # Create a wiki
        client.post("/wiki/create", json=sample_wiki_data)

        # List wikis
        response = client.get("/wiki/list")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["wikis"]) >= 1

        # Verify wiki structure
        wiki = data["wikis"][0]
        assert "name" in wiki
        assert "description" in wiki
        assert "sessions" in wiki  # Should have sessions list, not session_count
        assert "created" in wiki

    def test_get_wiki_details(self, client, sample_wiki_data):
        """Test getting wiki details."""
        # Create wiki first
        client.post("/wiki/create", json=sample_wiki_data)

        # Get wiki details
        response = client.get(f"/wiki/{sample_wiki_data['name']}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "metadata" in data
        assert "sessions" in data
        assert "pages" in data

    def test_get_nonexistent_wiki(self, client):
        """Test getting details for wiki that doesn't exist."""
        response = client.get("/wiki/nonexistent_wiki")

        assert response.status_code == 404


@pytest.mark.api
@pytest.mark.wiki
class TestWikiPages:
    """Test wiki page operations."""

    def test_save_wiki_page(self, client, sample_wiki_data, sample_wiki_page_data):
        """Test saving a wiki page."""
        # Create wiki first
        client.post("/wiki/create", json=sample_wiki_data)

        # Save a page
        wiki_name = sample_wiki_data["name"]
        response = client.post(
            f"/wiki/{wiki_name}/page/characters/TestHero",
            json=sample_wiki_page_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_read_wiki_page(self, client, sample_wiki_data, sample_wiki_page_data):
        """Test reading a wiki page."""
        wiki_name = sample_wiki_data["name"]

        # Create wiki and save page
        client.post("/wiki/create", json=sample_wiki_data)
        client.post(
            f"/wiki/{wiki_name}/page/characters/TestHero",
            json=sample_wiki_page_data
        )

        # Read the page
        response = client.get(f"/wiki/{wiki_name}/page/characters/TestHero")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["content"] == sample_wiki_page_data["content"]

    def test_read_nonexistent_page(self, client, sample_wiki_data):
        """Test reading a page that doesn't exist."""
        client.post("/wiki/create", json=sample_wiki_data)
        wiki_name = sample_wiki_data["name"]

        response = client.get(f"/wiki/{wiki_name}/page/characters/NonExistent")

        assert response.status_code == 404

    def test_delete_wiki_page(self, client, sample_wiki_data, sample_wiki_page_data):
        """Test deleting a wiki page."""
        wiki_name = sample_wiki_data["name"]

        # Create wiki and save page
        client.post("/wiki/create", json=sample_wiki_data)
        client.post(
            f"/wiki/{wiki_name}/page/characters/TestHero",
            json=sample_wiki_page_data
        )

        # Delete the page
        response = client.delete(f"/wiki/{wiki_name}/page/characters/TestHero")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify page is gone
        get_response = client.get(f"/wiki/{wiki_name}/page/characters/TestHero")
        assert get_response.status_code == 404

    def test_update_wiki_page(self, client, sample_wiki_data, sample_wiki_page_data):
        """Test updating an existing wiki page."""
        wiki_name = sample_wiki_data["name"]

        # Create wiki and save page
        client.post("/wiki/create", json=sample_wiki_data)
        client.post(
            f"/wiki/{wiki_name}/page/characters/TestHero",
            json=sample_wiki_page_data
        )

        # Update the page
        updated_data = {"content": "# Updated Character\n\nThis is updated content."}
        response = client.post(
            f"/wiki/{wiki_name}/page/characters/TestHero",
            json=updated_data
        )

        assert response.status_code == 200

        # Verify update
        get_response = client.get(f"/wiki/{wiki_name}/page/characters/TestHero")
        assert get_response.json()["content"] == updated_data["content"]


@pytest.mark.api
@pytest.mark.wiki
class TestWikiSessions:
    """Test wiki session management."""

    @pytest.mark.skip(reason="Requires active session from narrative endpoint")
    def test_save_session_to_wiki(self, client, sample_wiki_data, sample_session_data):
        """Test saving a session to a wiki."""
        # Create wiki first
        client.post("/wiki/create", json=sample_wiki_data)
        wiki_name = sample_wiki_data["name"]

        # Note: This test would need an active session created via /narrative endpoint
        # Save session
        response = client.post(
            f"/wiki/{wiki_name}/save_session",
            json=sample_session_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.skip(reason="Requires active session from narrative endpoint")
    def test_load_session_from_wiki(self, client, sample_wiki_data, sample_session_data):
        """Test loading a session from a wiki."""
        wiki_name = sample_wiki_data["name"]
        session_id = sample_session_data["session_id"]

        # Create wiki and save session
        client.post("/wiki/create", json=sample_wiki_data)
        # Note: Would need to create session via /narrative endpoint first
        # client.post(f"/wiki/{wiki_name}/save_session", json=sample_session_data)

        # Load session
        response = client.get(f"/wiki/{wiki_name}/session/{session_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "conversation" in data

    def test_load_nonexistent_session(self, client, sample_wiki_data):
        """Test loading a session that doesn't exist."""
        client.post("/wiki/create", json=sample_wiki_data)
        wiki_name = sample_wiki_data["name"]

        response = client.get(f"/wiki/{wiki_name}/session/nonexistent_session")

        assert response.status_code == 404
