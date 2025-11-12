"""
LLM Service for OpenAI GPT-4o integration.

This service handles all interactions with OpenAI's API, including
response generation and error handling.
"""

import logging
from typing import Optional

from openai import AsyncOpenAI, OpenAIError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for interacting with OpenAI's GPT models.

    Handles response generation with proper error handling,
    retry logic, and logging.
    """

    # System prompt template for the Polish Legal Assistant
    SYSTEM_PROMPT = """You are a helpful legal assistant specializing in Polish law and daily life information for foreigners living in Poland.

CRITICAL RULES:
1. ONLY use information from the provided context below
2. ALWAYS cite sources using inline citations like [1], [2], etc.
3. If the context doesn't contain enough information to answer the question, explicitly state this
4. When relevant, highlight whether information is from before or after the July 2025 legal changes
5. For complex legal matters, recommend consulting official sources or legal professionals
6. Use clear, simple English suitable for non-native speakers
7. Be precise and accurate - legal information must be correct
8. If you're uncertain about any detail, say so explicitly

RESPONSE FORMAT:
- Use inline citations [1], [2] after each factual statement
- Break down complex information into clear steps or bullet points
- Use simple language and explain legal terms when necessary
- Be direct and concise

Context:
{context}

User Query: {query}

Provide a helpful, accurate answer based ONLY on the context above:"""

    def __init__(self):
        """Initialize the LLM service with OpenAI client."""
        if not settings.openai_configured:
            logger.warning("OpenAI API key not configured")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            logger.info("LLM Service initialized with OpenAI")

    def _format_context(
        self,
        retrieved_docs: list[dict],
        max_length: Optional[int] = None
    ) -> str:
        """
        Format retrieved documents into context string.

        Args:
            retrieved_docs: List of retrieved documents with content and metadata
            max_length: Maximum context length in characters

        Returns:
            Formatted context string with source citations
        """
        if not retrieved_docs:
            return "No relevant information found in the knowledge base."

        context_parts = []
        max_length = max_length or settings.rag_max_context_length

        for idx, doc in enumerate(retrieved_docs, 1):
            title = doc.get("title", "Unknown")
            org = doc.get("organization", "Unknown")
            content = doc.get("content", "")

            # Format each document with clear source attribution
            doc_context = f"[Source {idx}: {title} - {org}]\n{content}\n"
            context_parts.append(doc_context)

            # Check if we're approaching max length
            current_length = sum(len(part) for part in context_parts)
            if current_length > max_length:
                logger.info(f"Context truncated at {current_length} characters")
                break

        return "\n".join(context_parts)

    @retry(
        retry=retry_if_exception_type(OpenAIError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def generate_response(
        self,
        query: str,
        retrieved_docs: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> tuple[str, dict]:
        """
        Generate a response using OpenAI GPT-4o.

        Args:
            query: User's question
            retrieved_docs: List of retrieved documents from vector DB
            temperature: Temperature for response generation (overrides default)
            max_tokens: Maximum tokens for response (overrides default)

        Returns:
            Tuple of (generated_response, metadata)

        Raises:
            ValueError: If OpenAI is not configured
            OpenAIError: If OpenAI API call fails
        """
        if not self.client:
            raise ValueError(
                "OpenAI API key is not configured. "
                "Please set OPENAI_API_KEY environment variable."
            )

        # Format context from retrieved documents
        context = self._format_context(retrieved_docs)

        # Format the system prompt with context and query
        system_message = self.SYSTEM_PROMPT.format(
            context=context,
            query=query
        )

        # Prepare API parameters
        temp = temperature if temperature is not None else settings.openai_temperature
        max_tok = max_tokens if max_tokens is not None else settings.openai_max_tokens

        logger.info(
            f"Generating response for query: {query[:100]}... "
            f"(temp={temp}, max_tokens={max_tok})"
        )

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": query}
                ],
                temperature=temp,
                max_tokens=max_tok,
            )

            # Extract response and metadata
            generated_text = response.choices[0].message.content
            metadata = {
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
            }

            logger.info(
                f"Response generated successfully. "
                f"Tokens used: {metadata['usage']['total_tokens']}"
            )

            return generated_text, metadata

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in LLM service: {str(e)}")
            raise

    async def check_availability(self) -> bool:
        """
        Check if the LLM service is available and configured.

        Returns:
            True if OpenAI is properly configured, False otherwise
        """
        return self.client is not None

    async def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text string.

        This is a simple estimation. For production, consider using tiktoken.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token for English
        return len(text) // 4


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get or create the LLM service singleton instance.

    Returns:
        LLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
