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
