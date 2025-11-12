"""
Pydantic models for request/response validation.

These models define the API contract between the frontend and backend,
ensuring type safety and automatic validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class SourceCitation(BaseModel):
    """
    Represents a source document citation.

    This model contains all metadata about a source document that was used
    to generate the response, allowing users to verify information.
    """

    id: str = Field(
        ...,
        description="Unique identifier for the citation (e.g., '1', '2', '3')"
    )
    title: str = Field(
        ...,
        description="Title of the source document",
        min_length=1
    )
    organization: str = Field(
        ...,
        description="Organization that published the document",
        min_length=1
    )
    url: Optional[HttpUrl] = Field(
        default=None,
        description="URL to the original source document"
    )
    last_verified: Optional[str] = Field(
        default=None,
        description="Date when information was last verified (YYYY-MM-DD)",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    relevance_score: Optional[float] = Field(
        default=None,
        description="Similarity score from vector search (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    category: Optional[str] = Field(
        default=None,
        description="Category of the document (e.g., 'immigration', 'taxation')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "1",
                "title": "Temporary Residence Permit Requirements",
                "organization": "Polish Ministry of Interior",
                "url": "https://www.gov.pl/web/mswia/temporary-residence",
                "last_verified": "2025-11-01",
                "relevance_score": 0.92,
                "category": "immigration"
            }
        }


class ChatRequest(BaseModel):
    """
    Request model for the chat endpoint.

    Contains the user's query and optional parameters for customizing
    the RAG pipeline behavior.
    """

    query: str = Field(
        ...,
        description="User's question or query",
        min_length=3,
        max_length=1000
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation ID for tracking context"
    )
    category_filter: Optional[str] = Field(
        default=None,
        description="Filter results by category (e.g., 'immigration', 'taxation')"
    )
    top_k: Optional[int] = Field(
        default=None,
        description="Number of documents to retrieve (overrides default)",
        ge=1,
        le=20
    )
    include_debug: bool = Field(
        default=False,
        description="Include debug information in response"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What documents do I need for a temporary residence permit?",
                "category_filter": "immigration",
                "top_k": 5,
                "include_debug": False
            }
        }


class ChatResponse(BaseModel):
    """
    Response model for the chat endpoint.

    Contains the assistant's answer along with source citations and metadata.
    """

    answer: str = Field(
        ...,
        description="Generated response with inline citations [1], [2], etc."
    )
    sources: list[SourceCitation] = Field(
        default_factory=list,
        description="List of source documents used to generate the response"
    )
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score for the response (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    category: Optional[str] = Field(
        default=None,
        description="Detected category of the query"
    )
    debug_info: Optional[dict] = Field(
        default=None,
        description="Debug information (only included if requested)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the response"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "To apply for a temporary residence permit in Poland, you need the following documents [1]:\n\n1. Valid passport\n2. Completed application form\n3. Photographs (3.5cm x 4.5cm)\n4. Proof of health insurance\n5. Document justifying the purpose of stay [2]\n\nProcessing time is typically 1-2 months [1].",
                "sources": [
                    {
                        "id": "1",
                        "title": "Temporary Residence Permit Requirements",
                        "organization": "Polish Ministry of Interior",
                        "url": "https://www.gov.pl/web/mswia/temporary-residence",
                        "last_verified": "2025-11-01",
                        "relevance_score": 0.92,
                        "category": "immigration"
                    }
                ],
                "confidence": 0.89,
                "category": "immigration",
                "timestamp": "2025-11-11T10:30:00Z"
            }
        }


class LegalDocument(BaseModel):
    """
    Represents a legal document in the knowledge base.

    Used internally for processing and potentially for bulk operations.
    """

    id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document text content")
    url: Optional[HttpUrl] = Field(default=None, description="Source URL")
    organization: str = Field(..., description="Publishing organization")
    category: str = Field(..., description="Document category")
    last_verified: Optional[str] = Field(
        default=None,
        description="Last verification date"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_001",
                "title": "Tax Obligations for Foreign Workers",
                "content": "Foreign workers in Poland are subject to...",
                "url": "https://www.gov.pl/web/kas/tax-obligations",
                "organization": "Polish Tax Authority",
                "category": "taxation",
                "last_verified": "2025-10-15",
                "metadata": {
                    "language": "en",
                    "effective_date": "2025-07-01"
                }
            }
        }


class HealthCheckResponse(BaseModel):
    """Response model for the health check endpoint."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    openai_configured: bool = Field(..., description="OpenAI API configured")
    pinecone_configured: bool = Field(..., description="Pinecone configured")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "openai_configured": True,
                "pinecone_configured": True,
                "timestamp": "2025-11-11T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[dict] = Field(
        default=None,
        description="Additional error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ConfigurationError",
                "message": "OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable.",
                "timestamp": "2025-11-11T10:30:00Z"
            }
        }
