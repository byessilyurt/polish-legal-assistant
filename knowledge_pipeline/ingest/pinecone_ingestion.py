"""
Pinecone Ingestion Module
Loads embedded documents into Pinecone vector database
"""

import os
import json
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from tqdm import tqdm
import time


class PineconeIngestor:
    """Manages document ingestion into Pinecone"""

    def __init__(
        self,
        api_key: str = None,
        environment: str = None,
        index_name: str = "polish-legal-kb"
    ):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.environment = environment or os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        self.index_name = index_name

        if not self.api_key:
            raise ValueError("Pinecone API key required")

        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None

    def create_index(
        self,
        dimension: int = 1536,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1"
    ):
        """
        Create Pinecone index if it doesn't exist

        Args:
            dimension: Embedding dimension
            metric: Distance metric (cosine, euclidean, dotproduct)
            cloud: Cloud provider
            region: Cloud region
        """
        # Check if index exists
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]

        if self.index_name in existing_indexes:
            print(f"✓ Index '{self.index_name}' already exists")
            self.index = self.pc.Index(self.index_name)

            # Get stats
            stats = self.index.describe_index_stats()
            print(f"  Current vector count: {stats.total_vector_count}")
            return

        # Create new index
        print(f"Creating index '{self.index_name}'...")
        self.pc.create_index(
            name=self.index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(
                cloud=cloud,
                region=region
            )
        )

        # Wait for index to be ready
        print("Waiting for index to be ready...")
        while not self.pc.describe_index(self.index_name).status['ready']:
            time.sleep(1)

        print(f"✓ Index '{self.index_name}' created successfully")
        self.index = self.pc.Index(self.index_name)

    def prepare_vectors(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prepare chunks for Pinecone ingestion

        Args:
            chunks: List of chunks with embeddings

        Returns:
            List of vectors in Pinecone format
        """
        vectors = []

        for chunk in chunks:
            # Extract required fields
            vector_id = chunk.get("id")
            embedding = chunk.get("embedding")
            metadata = chunk.get("metadata", {})
            content = chunk.get("content", "")

            if not vector_id or not embedding:
                print(f"⚠️  Skipping chunk without id or embedding")
                continue

            # Add content to metadata (for retrieval)
            metadata["content"] = content[:1000]  # Limit to 1000 chars

            # Clean metadata (remove None values, ensure serializable)
            clean_metadata = {}
            for key, value in metadata.items():
                if value is not None:
                    # Convert to string if not primitive type
                    if isinstance(value, (str, int, float, bool)):
                        clean_metadata[key] = value
                    else:
                        clean_metadata[key] = str(value)

            # Create vector dict
            vector = {
                "id": vector_id,
                "values": embedding,
                "metadata": clean_metadata
            }

            vectors.append(vector)

        return vectors

    def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]],
        batch_size: int = 100,
        show_progress: bool = True
    ):
        """
        Upsert vectors to Pinecone index

        Args:
            vectors: List of vector dicts
            batch_size: Batch size for upserts
            show_progress: Show progress bar
        """
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")

        print(f"Upserting {len(vectors)} vectors to Pinecone...")

        # Upsert in batches
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]

            try:
                self.index.upsert(vectors=batch)

                if show_progress:
                    progress = (i + len(batch)) / len(vectors) * 100
                    print(f"Upserted {i + len(batch)}/{len(vectors)} vectors ({progress:.1f}%)")

            except Exception as e:
                print(f"❌ Error upserting batch {i}-{i+len(batch)}: {e}")
                raise

        print(f"✓ Successfully upserted {len(vectors)} vectors")

    def ingest_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 100
    ):
        """
        Complete ingestion pipeline

        Args:
            chunks: List of chunks with embeddings
            batch_size: Batch size for upserts
        """
        # Prepare vectors
        vectors = self.prepare_vectors(chunks)
        print(f"Prepared {len(vectors)} vectors for ingestion")

        # Upsert to Pinecone
        self.upsert_vectors(vectors, batch_size)

        # Get final stats
        stats = self.index.describe_index_stats()
        print(f"\n✓ Ingestion complete!")
        print(f"  Total vectors in index: {stats.total_vector_count}")

    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if not self.index:
            raise ValueError("Index not initialized")

        return self.index.describe_index_stats()

    def delete_index(self):
        """Delete the index (use with caution!)"""
        if self.index_name in [idx.name for idx in self.pc.list_indexes()]:
            self.pc.delete_index(self.index_name)
            print(f"✓ Deleted index '{self.index_name}'")
        else:
            print(f"Index '{self.index_name}' does not exist")


def load_knowledge_file(file_path: str) -> List[Dict[str, Any]]:
    """Load documents from JSON knowledge file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('documents', [])


if __name__ == "__main__":
    # Test ingestion (requires PINECONE_API_KEY)
    if not os.getenv("PINECONE_API_KEY"):
        print("⚠️  PINECONE_API_KEY not set.")
        print("To test: export PINECONE_API_KEY=your-key")
        exit(1)

    # Create test vectors
    test_vectors = [
        {
            "id": "test-1",
            "embedding": [0.1] * 1536,
            "content": "Test content 1",
            "metadata": {
                "category": "immigration",
                "source": "test"
            }
        },
        {
            "id": "test-2",
            "embedding": [0.2] * 1536,
            "content": "Test content 2",
            "metadata": {
                "category": "employment",
                "source": "test"
            }
        }
    ]

    # Initialize ingestor
    ingestor = PineconeIngestor(index_name="test-polish-legal")

    # Create index
    ingestor.create_index(dimension=1536)

    # Ingest test data
    ingestor.ingest_chunks(test_vectors)

    # Get stats
    stats = ingestor.get_index_stats()
    print(f"\nIndex stats: {stats}")

    # Clean up
    print("\nCleaning up test index...")
    ingestor.delete_index()
