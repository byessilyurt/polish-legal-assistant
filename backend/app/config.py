"""
Configuration management for the Polish Legal Assistant API.

This module handles all environment variables and application settings
using Pydantic for type safety and validation.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Settings
    app_name: str = "Polish Legal Assistant API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # CORS Settings
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "https://frontend-9e5nnxcas-byessilyurts-projects.vercel.app",
            "https://*.vercel.app"  # Allow all Vercel preview deployments
        ],
        description="Allowed origins for CORS"
    )

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for GPT-4o and embeddings"
    )
    openai_model: str = Field(
        default="gpt-4o",
        description="OpenAI model for chat responses"
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-large",
        description="OpenAI model for text embeddings"
    )
    openai_temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Temperature for OpenAI responses (0.0-2.0)"
    )
    openai_max_tokens: int = Field(
        default=1500,
        ge=1,
        description="Maximum tokens for OpenAI responses"
    )

    # Pinecone Configuration
    pinecone_api_key: Optional[str] = Field(
        default=None,
        description="Pinecone API key for vector database"
    )
    pinecone_environment: Optional[str] = Field(
        default=None,
        description="Pinecone environment (e.g., us-west1-gcp)"
    )
    pinecone_index_name: str = Field(
        default="polish-legal-docs",
        description="Name of the Pinecone index"
    )

    # RAG Configuration
    rag_top_k: int = Field(
        default=10,  # Updated from 5 to 10 for better coverage
        ge=1,
        le=20,
        description="Number of documents to retrieve from vector DB"
    )
    rag_similarity_threshold: float = Field(
        default=0.55,  # Updated from 0.7 to 0.55 for better recall
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for retrieved documents"
    )
    # Two-tier fallback configuration
    rag_tier1_threshold: float = Field(
        default=0.65,
        ge=0.0,
        le=1.0,
        description="Tier 1 (strict) similarity threshold"
    )
    rag_tier1_top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Tier 1 top_k value"
    )
    rag_tier2_threshold: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Tier 2 (relaxed) similarity threshold"
    )
    rag_tier2_top_k: int = Field(
        default=15,
        ge=1,
        le=30,
        description="Tier 2 top_k value"
    )
    rag_max_context_length: int = Field(
        default=6000,
        ge=1000,
        description="Maximum context length in tokens"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    @property
    def is_configured(self) -> bool:
        """Check if all required API keys are configured."""
        return bool(self.openai_api_key and self.pinecone_api_key)

    @property
    def openai_configured(self) -> bool:
        """Check if OpenAI is configured."""
        return bool(self.openai_api_key)

    @property
    def pinecone_configured(self) -> bool:
        """Check if Pinecone is configured."""
        return bool(self.pinecone_api_key and self.pinecone_environment)


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are loaded only once.
    This is the recommended way to access settings throughout the app.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Convenience export
settings = get_settings()
