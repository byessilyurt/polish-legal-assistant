"""
RAG Service - Main orchestration of the RAG pipeline.

This service coordinates the retrieval and generation steps,
managing the complete flow from user query to final response.
"""

import logging
from typing import Optional

from app.config import settings
from app.models.schemas import ChatRequest, ChatResponse, SourceCitation
from app.services.llm_service import get_llm_service
from app.services.retrieval_service import get_retrieval_service
from app.services.metrics_service import get_metrics_collector

logger = logging.getLogger(__name__)


class RAGService:
    """
    Main RAG service orchestrating the entire pipeline.

    Pipeline flow:
    1. Receive user query
    2. Retrieve relevant documents from Pinecone
    3. Construct context with citations
    4. Generate response using LLM
    5. Format response with source citations
    """

    def __init__(self):
        """Initialize RAG service with retrieval and LLM services."""
        self.retrieval_service = get_retrieval_service()
        self.llm_service = get_llm_service()
        self.metrics_collector = get_metrics_collector()
        logger.info("RAG Service initialized")

    async def process_query(
        self,
        request: ChatRequest,
        include_debug: bool = False
    ) -> ChatResponse:
        """
        Process a user query through the complete RAG pipeline.

        Args:
            request: ChatRequest containing query and parameters
            include_debug: Whether to include debug information

        Returns:
            ChatResponse with answer and source citations

        Raises:
            ValueError: If services are not properly configured
            Exception: If processing fails
        """
        query = request.query
        logger.info(f"Processing query: {query[:100]}...")

        debug_info = {} if include_debug or request.include_debug else None

        try:
            # Step 1: Check service availability
            if not await self.retrieval_service.check_availability():
                return self._create_error_response(
                    "The knowledge base is not currently available. "
                    "Please ensure Pinecone and OpenAI are properly configured.",
                    debug_info
                )

            if not await self.llm_service.check_availability():
                return self._create_error_response(
                    "The response generation service is not currently available. "
                    "Please ensure OpenAI API key is configured.",
                    debug_info
                )

            # Step 2: Retrieve relevant documents using two-tier fallback
            logger.info("Retrieving relevant documents with two-tier fallback...")
            retrieved_docs, tier_used = await self.retrieval_service.retrieve_with_fallback(
                query=query,
                category_filter=request.category_filter
            )

            if debug_info is not None:
                debug_info["tier_used"] = tier_used
                debug_info["retrieved_docs_count"] = len(retrieved_docs)
                debug_info["retrieval_scores"] = [
                    {"id": doc["id"], "score": doc["score"]}
                    for doc in retrieved_docs
                ]

            # Handle case where no relevant documents found
            if not retrieved_docs:
                logger.warning("No relevant documents found for query")
                # Log metrics for failed query
                self.metrics_collector.log_query(
                    query=query,
                    tier="no_context",
                    documents=[],
                    category=request.category_filter,
                    confidence=0.0
                )
                return self._create_no_context_response(query, debug_info)

            # Step 3: Generate response using LLM
            logger.info("Generating response with LLM...")
            generated_answer, llm_metadata = await self.llm_service.generate_response(
                query=query,
                retrieved_docs=retrieved_docs
            )

            if debug_info is not None:
                debug_info["llm_metadata"] = llm_metadata

            # Step 4: Format source citations
            sources = self._format_sources(retrieved_docs)

            # Step 5: Calculate confidence score
            confidence = self._calculate_confidence(retrieved_docs, llm_metadata)

            # Step 6: Detect query category
            category = self._detect_category(retrieved_docs, request.category_filter)

            if debug_info is not None:
                debug_info["confidence_score"] = confidence
                debug_info["detected_category"] = category

            logger.info(
                f"Query processed successfully. "
                f"Confidence: {confidence:.2f}, Category: {category}, Tier: {tier_used}"
            )

            # Log metrics for successful query
            self.metrics_collector.log_query(
                query=query,
                tier=tier_used,
                documents=retrieved_docs,
                category=category,
                confidence=confidence
            )

            return ChatResponse(
                answer=generated_answer,
                sources=sources,
                confidence=confidence,
                category=category,
                debug_info=debug_info
            )

        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            return self._create_error_response(str(e), debug_info)
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return self._create_error_response(
                "An error occurred while processing your query. Please try again later.",
                debug_info,
                error_detail=str(e)
            )

    def _format_sources(self, retrieved_docs: list[dict]) -> list[SourceCitation]:
        """
        Format retrieved documents as source citations.

        Args:
            retrieved_docs: List of retrieved documents

        Returns:
            List of SourceCitation objects
        """
        sources = []

        for idx, doc in enumerate(retrieved_docs, 1):
            source = SourceCitation(
                id=str(idx),
                title=doc.get("title", "Unknown"),
                organization=doc.get("organization", "Unknown"),
                url=doc.get("url"),
                last_verified=doc.get("last_verified"),
                relevance_score=round(doc.get("score", 0.0), 3),
                category=doc.get("category")
            )
            sources.append(source)

        return sources

    def _calculate_confidence(
        self,
        retrieved_docs: list[dict],
        llm_metadata: dict
    ) -> float:
        """
        Calculate confidence score for the response.

        Confidence is based on:
        - Average similarity score of retrieved documents
        - Number of retrieved documents
        - LLM response completeness

        Args:
            retrieved_docs: List of retrieved documents
            llm_metadata: Metadata from LLM response

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not retrieved_docs:
            return 0.0

        # Average similarity score
        avg_score = sum(doc["score"] for doc in retrieved_docs) / len(retrieved_docs)

        # Boost confidence if we have multiple high-quality sources
        num_docs_factor = min(len(retrieved_docs) / 5, 1.0)  # Normalize to 5 docs

        # Check if LLM response was complete
        finish_reason = llm_metadata.get("finish_reason", "")
        completeness_factor = 1.0 if finish_reason == "stop" else 0.8

        # Combined confidence score
        confidence = avg_score * 0.6 + num_docs_factor * 0.2 + completeness_factor * 0.2

        return round(min(confidence, 1.0), 3)

    def _detect_category(
        self,
        retrieved_docs: list[dict],
        requested_category: Optional[str]
    ) -> Optional[str]:
        """
        Detect the most relevant category for the query.

        Args:
            retrieved_docs: List of retrieved documents
            requested_category: User-requested category filter

        Returns:
            Detected category or None
        """
        # If user specified a category, use it
        if requested_category:
            return requested_category

        # Otherwise, use the category of the highest-scoring document
        if retrieved_docs:
            return retrieved_docs[0].get("category")

        return None

    def _create_error_response(
        self,
        error_message: str,
        debug_info: Optional[dict],
        error_detail: Optional[str] = None
    ) -> ChatResponse:
        """
        Create an error response.

        Args:
            error_message: Human-readable error message
            debug_info: Debug information dictionary
            error_detail: Technical error details

        Returns:
            ChatResponse with error message
        """
        if debug_info is not None and error_detail:
            debug_info["error"] = error_detail

        return ChatResponse(
            answer=f"I apologize, but I encountered an issue: {error_message}",
            sources=[],
            confidence=0.0,
            debug_info=debug_info
        )

    def _create_no_context_response(
        self,
        query: str,
        debug_info: Optional[dict]
    ) -> ChatResponse:
        """
        Create response when no relevant documents are found.

        Args:
            query: Original user query
            debug_info: Debug information dictionary

        Returns:
            ChatResponse indicating no information available
        """
        answer = (
            "I apologize, but I couldn't find relevant information in my knowledge base "
            "to answer your question about Polish law and daily life.\n\n"
            "This could mean:\n"
            "1. The information hasn't been added to the knowledge base yet\n"
            "2. Your query might need to be rephrased\n"
            "3. This topic might not be covered in the current database\n\n"
            "I recommend:\n"
            "- Trying a different phrasing of your question\n"
            "- Checking official Polish government websites (gov.pl)\n"
            "- Consulting with a legal professional for specific cases"
        )

        return ChatResponse(
            answer=answer,
            sources=[],
            confidence=0.0,
            debug_info=debug_info
        )

    async def health_check(self) -> dict:
        """
        Check the health of the RAG service and its dependencies.

        Returns:
            Dictionary with health status information
        """
        return {
            "retrieval_service": await self.retrieval_service.check_availability(),
            "llm_service": await self.llm_service.check_availability(),
            "overall_healthy": (
                await self.retrieval_service.check_availability()
                and await self.llm_service.check_availability()
            )
        }


# Singleton instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """
    Get or create the RAG service singleton instance.

    Returns:
        RAGService instance
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
