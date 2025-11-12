"""
Main FastAPI application for the Polish Legal Assistant API.

This is the entry point for the backend service, configuring FastAPI,
CORS, routes, and middleware.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import chat
from app.config import settings
from app.models.schemas import HealthCheckResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Handles initialization and cleanup of services.
    """
    # Startup
    logger.info("Starting Polish Legal Assistant API...")
    logger.info(f"OpenAI configured: {settings.openai_configured}")
    logger.info(f"Pinecone configured: {settings.pinecone_configured}")

    if not settings.is_configured:
        logger.warning(
            "API keys are not fully configured. "
            "Some endpoints may not function correctly."
        )

    yield

    # Shutdown
    logger.info("Shutting down Polish Legal Assistant API...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Polish Legal Assistant API provides AI-powered assistance for foreigners
    navigating Polish law and daily life.

    ## Features

    * **RAG-powered responses**: Retrieves relevant information from a curated
      knowledge base and generates accurate answers
    * **Source citations**: Every answer includes citations to official sources
    * **Category filtering**: Filter by topic (immigration, taxation, housing, etc.)
    * **Confidence scoring**: Understand how reliable each answer is

    ## Authentication

    Currently, this API does not require authentication. In production,
    consider implementing API key authentication.

    ## Rate Limiting

    No rate limiting is currently implemented. Consider adding rate limiting
    for production deployment.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get(
    "/",
    response_model=dict,
    summary="API Root",
    description="Get basic information about the API",
)
async def root():
    """
    Root endpoint providing API information.

    Returns:
        Dictionary with API name, version, and documentation links
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Check the health and configuration status of the API",
)
async def health_check():
    """
    Health check endpoint.

    Returns the status of the API and its dependencies.

    Returns:
        HealthCheckResponse with service status
    """
    return HealthCheckResponse(
        status="healthy" if settings.is_configured else "degraded",
        version=settings.app_version,
        openai_configured=settings.openai_configured,
        pinecone_configured=settings.pinecone_configured,
    )


# Include API routers
app.include_router(
    chat.router,
    prefix=settings.api_prefix,
    tags=["chat"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Args:
        request: The request that caused the error
        exc: The exception that was raised

    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


# Log startup message
@app.on_event("startup")
async def startup_message():
    """Log startup message with configuration info."""
    logger.info("=" * 60)
    logger.info(f"🚀 {settings.app_name} v{settings.app_version}")
    logger.info("=" * 60)
    logger.info(f"Environment: {'DEBUG' if settings.debug else 'PRODUCTION'}")
    logger.info(f"API Prefix: {settings.api_prefix}")
    logger.info(f"CORS Origins: {', '.join(settings.cors_origins)}")
    logger.info(f"OpenAI Model: {settings.openai_model}")
    logger.info(f"Embedding Model: {settings.openai_embedding_model}")
    logger.info(f"Pinecone Index: {settings.pinecone_index_name}")
    logger.info(f"RAG Top-K: {settings.rag_top_k}")
    logger.info(f"Similarity Threshold: {settings.rag_similarity_threshold}")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
