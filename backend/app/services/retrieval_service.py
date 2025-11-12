"""
Retrieval Service for Pinecone vector database operations.

This service handles all vector search operations, including query embedding,
similarity search, and result reranking.
"""

import logging
from typing import Optional

from openai import AsyncOpenAI
from pinecone import Pinecone, ServerlessSpec
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings
from app.services.query_preprocessing import get_query_preprocessor

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Service for retrieving relevant documents from Pinecone vector database.

    Handles embedding generation, vector search, metadata filtering,
    and result reranking.
    """

    def __init__(self):
        """Initialize the retrieval service with Pinecone and OpenAI clients."""
        self.pinecone_client = None
        self.index = None
        self.openai_client = None
        self.query_preprocessor = get_query_preprocessor()
        self._index_initialized = False

        # Initialize Pinecone client (but not the index yet - lazy init)
        if settings.pinecone_configured:
            try:
                self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
                logger.info("Pinecone client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone client: {str(e)}")
        else:
            logger.warning("Pinecone not configured")

        # Initialize OpenAI for embeddings
        if settings.openai_configured:
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized for embeddings")
        else:
            logger.warning("OpenAI not configured for embeddings")

    def _ensure_index_connection(self):
        """
        Lazy initialization of Pinecone index connection.

        This method connects to the Pinecone index on first use,
        avoiding blocking network calls during service initialization.
        """
        if self._index_initialized:
            return

        if self.pinecone_client and settings.pinecone_configured:
            try:
                # Directly connect to the index without listing all indexes
                # This is faster and works better in serverless environments
                logger.info(f"Attempting to connect to Pinecone index: {settings.pinecone_index_name}")
                self.index = self.pinecone_client.Index(settings.pinecone_index_name)
                self._index_initialized = True
                logger.info(f"Successfully connected to Pinecone index: {settings.pinecone_index_name}")
            except Exception as e:
                logger.error(f"Failed to connect to Pinecone index '{settings.pinecone_index_name}': {str(e)}", exc_info=True)
                raise

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding vector for input text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats

        Raises:
            ValueError: If OpenAI is not configured
            Exception: If embedding generation fails
        """
        if not self.openai_client:
            raise ValueError(
                "OpenAI API key is not configured. "
                "Please set OPENAI_API_KEY environment variable."
            )

        try:
            logger.debug(f"Generating embedding for text: {text[:100]}...")

            response = await self.openai_client.embeddings.create(
                model=settings.openai_embedding_model,
                input=text,
                dimensions=1536  # Match Pinecone index dimension
            )

            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding with dimension: {len(embedding)}")

            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise

    async def retrieve_documents(
        self,
        query: str,
        top_k: Optional[int] = None,
        category_filter: Optional[str] = None,
        min_score: Optional[float] = None,
    ) -> list[dict]:
        """
        Retrieve relevant documents from Pinecone based on query.

        Args:
            query: User's search query
            top_k: Number of documents to retrieve (overrides default)
            category_filter: Filter by document category
            min_score: Minimum similarity score threshold

        Returns:
            List of retrieved documents with metadata and scores

        Raises:
            ValueError: If Pinecone is not configured or index not found
            Exception: If retrieval fails
        """
        # Ensure index is connected (lazy initialization)
        self._ensure_index_connection()

        if not self.pinecone_client or not self.index:
            raise ValueError(
                "Pinecone is not properly configured. "
                "Please set PINECONE_API_KEY and PINECONE_ENVIRONMENT, "
                "and ensure the index exists."
            )

        # Use provided values or defaults
        k = top_k if top_k is not None else settings.rag_top_k
        threshold = min_score if min_score is not None else settings.rag_similarity_threshold

        logger.info(
            f"Retrieving documents for query: {query[:100]}... "
            f"(top_k={k}, category={category_filter})"
        )

        try:
            # Preprocess query
            preprocessed_query = self.query_preprocessor.preprocess(query)
            logger.debug(f"Preprocessed query: '{query}' -> '{preprocessed_query}'")

            # Generate embedding for the query (use preprocessed version)
            query_embedding = await self.generate_embedding(preprocessed_query)

            # Build metadata filter if category specified
            filter_dict = {}
            if category_filter:
                filter_dict["category"] = {"$eq": category_filter}

            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )

            # Process and filter results
            documents = []
            for match in results.matches:
                score = match.score

                # Filter by similarity threshold
                if score < threshold:
                    logger.debug(f"Skipping document with score {score} < {threshold}")
                    continue

                metadata = match.metadata or {}

                document = {
                    "id": match.id,
                    "score": score,
                    "title": metadata.get("title", "Unknown"),
                    "content": metadata.get("content", ""),
                    "organization": metadata.get("organization", "Unknown"),
                    "url": metadata.get("url"),
                    "category": metadata.get("category"),
                    "last_verified": metadata.get("last_verified"),
                }

                documents.append(document)

            logger.info(f"Retrieved {len(documents)} documents above threshold")

            # Rerank documents by relevance
            documents = self._rerank_documents(documents, query)

            return documents

        except Exception as e:
            logger.error(f"Failed to retrieve documents: {str(e)}")
            raise

    async def retrieve_with_fallback(
        self,
        query: str,
        category_filter: Optional[str] = None,
    ) -> tuple[list[dict], str]:
        """
        Retrieve documents using two-tier fallback strategy.

        Tier 1 (Strict): higher threshold, fewer documents - for high confidence
        Tier 2 (Relaxed): lower threshold, more documents - fallback if Tier 1 insufficient

        Args:
            query: User's search query
            category_filter: Filter by document category

        Returns:
            Tuple of (documents, tier_used) where tier_used is "tier1", "tier2", or "no_context"

        Raises:
            ValueError: If Pinecone is not configured
            Exception: If retrieval fails
        """
        logger.info(f"Attempting two-tier retrieval for query: {query[:100]}...")

        # Tier 1: Strict retrieval
        try:
            tier1_docs = await self.retrieve_documents(
                query=query,
                top_k=settings.rag_tier1_top_k,
                category_filter=category_filter,
                min_score=settings.rag_tier1_threshold
            )

            # If we got at least 2 good results from Tier 1, use them
            if len(tier1_docs) >= 2:
                logger.info(f"Tier 1 successful: {len(tier1_docs)} documents retrieved")
                return tier1_docs, "tier1"

            logger.info(
                f"Tier 1 insufficient ({len(tier1_docs)} docs), "
                "falling back to Tier 2..."
            )

        except Exception as e:
            logger.warning(f"Tier 1 retrieval failed: {e}, falling back to Tier 2")

        # Tier 2: Relaxed retrieval
        try:
            tier2_docs = await self.retrieve_documents(
                query=query,
                top_k=settings.rag_tier2_top_k,
                category_filter=category_filter,
                min_score=settings.rag_tier2_threshold
            )

            if tier2_docs:
                logger.info(f"Tier 2 successful: {len(tier2_docs)} documents retrieved")
                return tier2_docs, "tier2"

            logger.warning("Tier 2 also returned no documents")
            return [], "no_context"

        except Exception as e:
            logger.error(f"Tier 2 retrieval failed: {e}")
            return [], "no_context"

    def _rerank_documents(
        self,
        documents: list[dict],
        query: str
    ) -> list[dict]:
        """
        Rerank documents based on relevance heuristics.

        This is a simple reranking based on:
        1. Similarity score (primary)
        2. Recency (if last_verified is available)
        3. Category match

        For production, consider using a dedicated reranking model.

        Args:
            documents: List of retrieved documents
            query: Original query

        Returns:
            Reranked list of documents
        """
        if not documents:
            return documents

        logger.debug(f"Reranking {len(documents)} documents")

        # For now, just sort by score (already done by Pinecone)
        # In production, you might want more sophisticated reranking:
        # - Cross-encoder models
        # - Recency boosting
        # - Diversity optimization

        return sorted(documents, key=lambda x: x["score"], reverse=True)

    async def check_availability(self) -> bool:
        """
        Check if the retrieval service is available and configured.

        Returns:
            True if both Pinecone and OpenAI are properly configured
        """
        try:
            # Attempt to connect to index if not already connected
            if self.pinecone_client and not self._index_initialized:
                self._ensure_index_connection()

            return (
                self.pinecone_client is not None
                and self.index is not None
                and self.openai_client is not None
            )
        except Exception as e:
            logger.error(f"Availability check failed: {str(e)}")
            return False

    async def get_index_stats(self) -> dict:
        """
        Get statistics about the Pinecone index.

        Returns:
            Dictionary with index statistics

        Raises:
            ValueError: If Pinecone is not configured
        """
        # Ensure index is connected (lazy initialization)
        self._ensure_index_connection()

        if not self.index:
            raise ValueError("Pinecone index not available")

        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "namespaces": stats.namespaces,
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            raise


# Singleton instance
_retrieval_service: Optional[RetrievalService] = None


def get_retrieval_service() -> RetrievalService:
    """
    Get or create the retrieval service singleton instance.

    Returns:
        RetrievalService instance
    """
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service
