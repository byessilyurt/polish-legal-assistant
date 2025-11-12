"""
Embedding Generation Module
Generates OpenAI embeddings for document chunks
"""

import os
from typing import List, Dict, Any
import asyncio
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm


class DocumentEmbedder:
    """Generates embeddings for document chunks using OpenAI"""

    def __init__(
        self,
        api_key: str = None,
        model: str = "text-embedding-3-large",
        dimension: int = 1536,
        batch_size: int = 100
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self.dimension = dimension
        self.batch_size = batch_size

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for single text with retry logic"""
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.model,
                dimensions=self.dimension
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    async def embed_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add embedding to chunk document

        Args:
            chunk: Chunk dict with content and metadata

        Returns:
            Chunk dict with added 'embedding' field
        """
        content = chunk.get("content", "")

        # Generate embedding
        embedding = await self._generate_embedding(content)

        # Add to chunk
        chunk["embedding"] = embedding

        return chunk

    async def embed_chunks_batch(
        self,
        chunks: List[Dict[str, Any]],
        show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Embed multiple chunks in batches

        Args:
            chunks: List of chunk dicts
            show_progress: Show progress bar

        Returns:
            List of chunks with embeddings
        """
        embedded_chunks = []

        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]

            # Create tasks for batch
            tasks = [self.embed_chunk(chunk) for chunk in batch]

            # Execute batch
            batch_results = await asyncio.gather(*tasks)
            embedded_chunks.extend(batch_results)

            if show_progress:
                progress = (i + len(batch)) / len(chunks) * 100
                print(f"Embedded {i + len(batch)}/{len(chunks)} chunks ({progress:.1f}%)")

        return embedded_chunks

    def embed_chunks_sync(
        self,
        chunks: List[Dict[str, Any]],
        show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Synchronous wrapper for embed_chunks_batch

        Args:
            chunks: List of chunk dicts
            show_progress: Show progress bar

        Returns:
            List of chunks with embeddings
        """
        return asyncio.run(self.embed_chunks_batch(chunks, show_progress))


async def embed_documents_pipeline(
    chunks: List[Dict[str, Any]],
    api_key: str = None,
    model: str = "text-embedding-3-large",
    dimension: int = 1536,
    batch_size: int = 100
) -> List[Dict[str, Any]]:
    """
    Complete embedding pipeline for document chunks

    Args:
        chunks: List of chunk dicts
        api_key: OpenAI API key
        model: Embedding model
        dimension: Embedding dimension
        batch_size: Batch size for API calls

    Returns:
        List of chunks with embeddings
    """
    embedder = DocumentEmbedder(
        api_key=api_key,
        model=model,
        dimension=dimension,
        batch_size=batch_size
    )

    print(f"Generating embeddings for {len(chunks)} chunks...")
    embedded_chunks = await embedder.embed_chunks_batch(chunks)
    print(f"✓ Generated {len(embedded_chunks)} embeddings")

    return embedded_chunks


if __name__ == "__main__":
    # Test embedding generation
    test_chunks = [
        {
            "id": "test-1",
            "content": "How to apply for residence permit in Poland",
            "metadata": {"category": "immigration"}
        },
        {
            "id": "test-2",
            "content": "B2B contract vs employment contract comparison",
            "metadata": {"category": "employment"}
        }
    ]

    # Check if API key available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Skipping embedding test.")
        print("To test: export OPENAI_API_KEY=your-key")
    else:
        embedder = DocumentEmbedder()
        embedded = embedder.embed_chunks_sync(test_chunks)
        print(f"\nGenerated {len(embedded)} embeddings")
        print(f"Embedding dimension: {len(embedded[0]['embedding'])}")
