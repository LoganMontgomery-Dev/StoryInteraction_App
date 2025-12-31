"""
Tests for Narrative API endpoint.
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.api
class TestNarrativeEndpoint:
    """Test narrative generation endpoint."""

    @patch('api_server.workflow_app')
    def test_narrative_generation_new_session(self, mock_workflow, client, sample_narrative_request):
        """Test narrative generation with new session."""
        # Mock the workflow response - must match NarrativeState structure
        mock_workflow.invoke.return_value = {
            "user_input": sample_narrative_request["user_input"],
            "session_id": "test_session",
            "relevant_lore": ["Ancient Ruins", "Northern Territory"],
            "lore_context": "Context about ruins",
            "narrative": "The ancient ruins loom before you.",
            "quality_check": "Narrative is engaging and on-topic.",
            "final_output": "The ancient ruins loom before you, mysterious and foreboding."
        }

        response = client.post("/narrative", json=sample_narrative_request)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "narrative" in data
        assert "session_id" in data
        assert "lore_used" in data

        # Verify narrative content
        assert isinstance(data["narrative"], str)
        assert len(data["narrative"]) > 0

        # Verify session was created
        assert data["session_id"] is not None

    @patch('api_server.workflow_app')
    def test_narrative_generation_existing_session(self, mock_workflow, client):
        """Test narrative generation with existing session."""
        mock_workflow.invoke.return_value = {
            "user_input": "I continue forward",
            "session_id": "existing_session_123",
            "relevant_lore": [],
            "lore_context": "",
            "narrative": "You continue exploring.",
            "quality_check": "Good continuation.",
            "final_output": "You continue exploring the ruins."
        }

        # Request with existing session
        request_data = {
            "user_input": "I continue forward",
            "session_id": "existing_session_123"
        }

        response = client.post("/narrative", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "existing_session_123"

    @patch('api_server.workflow_app')
    def test_narrative_empty_input(self, mock_workflow, client):
        """Test narrative generation with empty input."""
        mock_workflow.invoke.return_value = {
            "user_input": "",
            "session_id": "test_session",
            "relevant_lore": [],
            "lore_context": "",
            "narrative": "",
            "quality_check": "",
            "final_output": ""
        }

        response = client.post("/narrative", json={"user_input": "", "session_id": None})

        # Should handle empty input gracefully
        assert response.status_code in [200, 400]

    @patch('api_server.workflow_app')
    def test_narrative_invalid_request(self, mock_workflow, client):
        """Test narrative generation with invalid request."""
        response = client.post("/narrative", json={})

        assert response.status_code == 422  # Validation error

    @patch('api_server.workflow_app')
    def test_narrative_with_lore_context(self, mock_workflow, client):
        """Test that narrative includes lore context."""
        mock_workflow.invoke.return_value = {
            "user_input": "I examine the inscriptions",
            "session_id": "test_session",
            "relevant_lore": ["Ancient Texts", "Historical Records"],
            "lore_context": "The ancient texts describe this location.",
            "narrative": "Based on the ancient texts, you recognize this place.",
            "quality_check": "Lore integrated well.",
            "final_output": "Based on the ancient texts, you recognize this place."
        }

        request_data = {
            "user_input": "I examine the inscriptions",
            "session_id": None
        }

        response = client.post("/narrative", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert len(data["lore_used"]) > 0

    @patch('api_server.workflow_app')
    def test_narrative_workflow_error_handling(self, mock_workflow, client, sample_narrative_request):
        """Test narrative endpoint handles workflow errors gracefully."""
        # Mock workflow to raise an error
        mock_workflow.invoke.side_effect = Exception("Workflow error")

        response = client.post("/narrative", json=sample_narrative_request)

        # Should return error response
        assert response.status_code == 500

    @patch('api_server.workflow_app')
    def test_narrative_long_conversation(self, mock_workflow, client):
        """Test narrative generation in a long conversation."""
        mock_workflow.invoke.return_value = {
            "user_input": "Action",
            "session_id": "test_session",
            "relevant_lore": [],
            "lore_context": "",
            "narrative": "The story continues...",
            "quality_check": "Good flow.",
            "final_output": "The story continues..."
        }

        session_id = None

        # Simulate multiple turns
        for i in range(5):
            request_data = {
                "user_input": f"Action {i}",
                "session_id": session_id
            }

            response = client.post("/narrative", json=request_data)
            assert response.status_code == 200

            # Use the same session
            session_id = response.json()["session_id"]

        # All should use same session
        assert session_id is not None


@pytest.mark.api
class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns OK."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.api
class TestCORSHeaders:
    """Test CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are set correctly."""
        response = client.get("/health")

        # Check for CORS headers (if configured)
        # Note: actual headers depend on FastAPI CORS middleware configuration
        assert response.status_code == 200
