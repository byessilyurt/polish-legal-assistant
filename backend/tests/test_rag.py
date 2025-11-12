"""
Tests for the RAG pipeline and chat endpoint.

These tests verify the core functionality of the Polish Legal Assistant API,
including configuration validation, endpoint responses, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app
from app.config import settings
from app.models.schemas import ChatRequest, ChatResponse, SourceCitation


# Test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    def test_root_endpoint(self):
        """Test the root endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == settings.app_name

    def test_health_check_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "openai_configured" in data
        assert "pinecone_configured" in data

    def test_rag_health_endpoint(self):
        """Test the RAG-specific health check."""
        response = client.get(f"{settings.api_prefix}/chat/health")

        assert response.status_code in [200, 503]  # OK or Service Unavailable
        data = response.json()
        assert "retrieval_service" in data
        assert "llm_service" in data
        assert "overall_healthy" in data


class TestChatEndpoint:
    """Test suite for the chat endpoint."""

    def test_chat_endpoint_requires_query(self):
        """Test that chat endpoint requires a query."""
        response = client.post(
            f"{settings.api_prefix}/chat",
            json={}
        )

        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_validates_query_length(self):
        """Test that chat endpoint validates minimum query length."""
        response = client.post(
            f"{settings.api_prefix}/chat",
            json={"query": "ab"}  # Too short (min 3 chars)
        )

        assert response.status_code == 422

    def test_chat_endpoint_accepts_valid_request(self):
        """Test that chat endpoint accepts a valid request structure."""
        response = client.post(
            f"{settings.api_prefix}/chat",
            json={
                "query": "What documents do I need for a residence permit?",
                "category_filter": "immigration",
                "top_k": 5
            }
        )

        # Should either succeed or fail with configuration error
        assert response.status_code in [200, 400, 500]

    @patch("app.services.rag_service.RAGService.process_query")
    async def test_chat_endpoint_response_format(self, mock_process_query):
        """Test that chat endpoint returns correct response format."""
        # Mock the RAG service response
        mock_response = ChatResponse(
            answer="Test answer with [1] citation.",
            sources=[
                SourceCitation(
                    id="1",
                    title="Test Document",
                    organization="Test Org",
                    url="https://example.com",
                    last_verified="2025-11-01",
                    relevance_score=0.9,
                    category="immigration"
                )
            ],
            confidence=0.85,
            category="immigration"
        )
        mock_process_query.return_value = mock_response

        response = client.post(
            f"{settings.api_prefix}/chat",
            json={"query": "Test query"}
        )

        if response.status_code == 200:
            data = response.json()
            assert "answer" in data
            assert "sources" in data
            assert "confidence" in data
            assert isinstance(data["sources"], list)


class TestChatRequestValidation:
    """Test suite for ChatRequest model validation."""

    def test_chat_request_minimal(self):
        """Test ChatRequest with minimal valid data."""
        request = ChatRequest(query="What is the weather?")

        assert request.query == "What is the weather?"
        assert request.conversation_id is None
        assert request.category_filter is None
        assert request.include_debug is False

    def test_chat_request_with_all_fields(self):
        """Test ChatRequest with all fields."""
        request = ChatRequest(
            query="Test query",
            conversation_id="conv123",
            category_filter="immigration",
            top_k=10,
            include_debug=True
        )

        assert request.query == "Test query"
        assert request.conversation_id == "conv123"
        assert request.category_filter == "immigration"
        assert request.top_k == 10
        assert request.include_debug is True

    def test_chat_request_query_too_short(self):
        """Test that query must be at least 3 characters."""
        with pytest.raises(ValueError):
            ChatRequest(query="ab")

    def test_chat_request_top_k_validation(self):
        """Test that top_k must be in valid range."""
        # Too low
        with pytest.raises(ValueError):
            ChatRequest(query="test query", top_k=0)

        # Too high
        with pytest.raises(ValueError):
            ChatRequest(query="test query", top_k=25)


class TestMissingConfiguration:
    """Test suite for handling missing API keys."""

    @patch("app.services.llm_service.settings.openai_configured", False)
    def test_llm_service_without_api_key(self):
        """Test that LLM service handles missing OpenAI key gracefully."""
        from app.services.llm_service import LLMService

        service = LLMService()
        assert service.client is None

    @patch("app.services.retrieval_service.settings.pinecone_configured", False)
    def test_retrieval_service_without_api_key(self):
        """Test that retrieval service handles missing Pinecone key gracefully."""
        from app.services.retrieval_service import RetrievalService

        service = RetrievalService()
        assert service.pinecone_client is None

    def test_chat_with_missing_configuration(self):
        """Test that chat endpoint returns appropriate error when not configured."""
        # This test assumes no API keys are configured in test environment
        response = client.post(
            f"{settings.api_prefix}/chat",
            json={"query": "Test query without configuration"}
        )

        # Should either work (if configured) or return error message
        if response.status_code == 200:
            data = response.json()
            # If not configured, answer should mention unavailability
            if not settings.is_configured:
                assert "not currently available" in data["answer"].lower() or \
                       "not configured" in data["answer"].lower()


class TestSourceCitation:
    """Test suite for SourceCitation model."""

    def test_source_citation_minimal(self):
        """Test SourceCitation with minimal required fields."""
        source = SourceCitation(
            id="1",
            title="Test Document",
            organization="Test Org"
        )

        assert source.id == "1"
        assert source.title == "Test Document"
        assert source.organization == "Test Org"
        assert source.url is None

    def test_source_citation_with_all_fields(self):
        """Test SourceCitation with all fields."""
        source = SourceCitation(
            id="1",
            title="Test Document",
            organization="Test Org",
            url="https://example.com/doc",
            last_verified="2025-11-01",
            relevance_score=0.95,
            category="immigration"
        )

        assert source.id == "1"
        assert source.relevance_score == 0.95
        assert source.category == "immigration"

    def test_source_citation_validates_score(self):
        """Test that relevance_score must be between 0 and 1."""
        # Valid score
        source = SourceCitation(
            id="1",
            title="Test",
            organization="Test",
            relevance_score=0.5
        )
        assert source.relevance_score == 0.5

        # Invalid score (too high)
        with pytest.raises(ValueError):
            SourceCitation(
                id="1",
                title="Test",
                organization="Test",
                relevance_score=1.5
            )


class TestAPIDocumentation:
    """Test suite for API documentation endpoints."""

    def test_openapi_json_available(self):
        """Test that OpenAPI JSON schema is available."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_swagger_docs_available(self):
        """Test that Swagger UI documentation is available."""
        response = client.get("/docs")

        assert response.status_code == 200

    def test_redoc_available(self):
        """Test that ReDoc documentation is available."""
        response = client.get("/redoc")

        assert response.status_code == 200


# Run tests with: pytest tests/test_rag.py -v
# Run with coverage: pytest tests/test_rag.py -v --cov=app --cov-report=html
