"""
Chat API endpoints.

This module defines the /chat endpoint for the Polish Legal Assistant,
handling user queries through the RAG pipeline.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.services.rag_service import get_rag_service
from app.services.metrics_service import get_metrics_collector

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a chat query",
    description="Process a user query through the RAG pipeline and return an answer with source citations.",
    responses={
        200: {
            "description": "Successful response with answer and sources",
            "model": ChatResponse,
        },
        400: {
            "description": "Invalid request",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
    },
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a user query and return an AI-generated response.

    This endpoint orchestrates the entire RAG pipeline:
    1. Validates the incoming request
    2. Retrieves relevant documents from the vector database
    3. Generates a response using the LLM
    4. Returns the answer with source citations

    Args:
        request: ChatRequest containing the user's query and optional parameters

    Returns:
        ChatResponse with the generated answer, source citations, and metadata

    Raises:
        HTTPException: If the request is invalid or processing fails
    """
    try:
        logger.info(f"Received chat request: {request.query[:100]}...")

        # Get the RAG service
        rag_service = get_rag_service()

        # Process the query through the RAG pipeline
        response = await rag_service.process_query(
            request=request,
            include_debug=request.include_debug
        )

        logger.info(
            f"Chat request processed successfully. "
            f"Sources: {len(response.sources)}, "
            f"Confidence: {response.confidence}"
        )

        return response

    except ValueError as e:
        # Configuration or validation errors
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ValidationError",
                "message": str(e),
            }
        )
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "An unexpected error occurred while processing your request.",
            }
        )


@router.get(
    "/chat/health",
    summary="Check RAG service health",
    description="Check if the RAG service and its dependencies are healthy and properly configured.",
)
async def check_rag_health() -> dict:
    """
    Check the health of the RAG service.

    Returns:
        Dictionary with health status of RAG components

    Example response:
        {
            "retrieval_service": true,
            "llm_service": true,
            "overall_healthy": true
        }
    """
    try:
        rag_service = get_rag_service()
        health_status = await rag_service.health_check()

        status_code = (
            status.HTTP_200_OK
            if health_status["overall_healthy"]
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return JSONResponse(
            status_code=status_code,
            content=health_status
        )

    except Exception as e:
        logger.error(f"Error checking RAG health: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "retrieval_service": False,
                "llm_service": False,
                "overall_healthy": False,
                "error": str(e)
            }
        )


@router.get(
    "/metrics",
    summary="Get RAG performance metrics",
    description="Retrieve collected metrics about query performance, response rates, and tier distribution.",
)
async def get_metrics() -> dict:
    """
    Get RAG performance metrics.

    Returns detailed metrics about:
    - Total queries processed
    - Response rate (queries with context found)
    - Tier distribution (tier1 vs tier2 vs no_context)
    - Average similarity scores by tier
    - Category distribution
    - Recent failed queries

    Returns:
        Dictionary with comprehensive metrics summary
    """
    try:
        metrics_collector = get_metrics_collector()
        summary = metrics_collector.get_summary()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=summary
        )

    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "MetricsError",
                "message": "Failed to retrieve metrics",
            }
        )


@router.post(
    "/metrics/reset",
    summary="Reset metrics collection",
    description="Clear all collected metrics. Use with caution.",
)
async def reset_metrics() -> dict:
    """
    Reset all collected metrics.

    Returns:
        Confirmation message
    """
    try:
        metrics_collector = get_metrics_collector()
        metrics_collector.reset_metrics()

        logger.info("Metrics reset successfully")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Metrics reset successfully"}
        )

    except Exception as e:
        logger.error(f"Error resetting metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "MetricsError",
                "message": "Failed to reset metrics",
            }
        )


@router.get(
    "/debug/pinecone",
    summary="Debug Pinecone connection",
    description="Test Pinecone connectivity and return detailed debug information",
)
async def debug_pinecone() -> dict:
    """
    Debug endpoint to test Pinecone connection and report detailed status.

    Returns:
        Detailed debug information about Pinecone connectivity
    """
    import traceback
    from app.services.retrieval_service import get_retrieval_service
    from app.config import settings

    debug_info = {
        "config": {
            "pinecone_api_key_set": bool(settings.pinecone_api_key),
            "pinecone_api_key_length": len(settings.pinecone_api_key) if settings.pinecone_api_key else 0,
            "pinecone_environment": settings.pinecone_environment,
            "pinecone_index_name": settings.pinecone_index_name,
            "pinecone_configured": settings.pinecone_configured,
        },
        "retrieval_service": {},
        "connection_test": {}
    }

    try:
        # Get retrieval service
        retrieval_service = get_retrieval_service()
        debug_info["retrieval_service"] = {
            "pinecone_client_exists": retrieval_service.pinecone_client is not None,
            "index_exists": retrieval_service.index is not None,
            "index_initialized": retrieval_service._index_initialized,
        }

        # Test availability
        try:
            available = await retrieval_service.check_availability()
            debug_info["connection_test"]["available"] = available
        except Exception as e:
            debug_info["connection_test"]["availability_error"] = str(e)
            debug_info["connection_test"]["availability_traceback"] = traceback.format_exc()

        # Try to get index stats
        try:
            if retrieval_service.index:
                stats = retrieval_service.index.describe_index_stats()
                debug_info["connection_test"]["index_stats"] = {
                    "total_vectors": stats.total_vector_count,
                    "dimension": stats.dimension,
                }
            else:
                debug_info["connection_test"]["index_stats_error"] = "Index is None"
        except Exception as e:
            debug_info["connection_test"]["index_stats_error"] = str(e)
            debug_info["connection_test"]["index_stats_traceback"] = traceback.format_exc()

    except Exception as e:
        debug_info["error"] = str(e)
        debug_info["traceback"] = traceback.format_exc()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=debug_info
    )
