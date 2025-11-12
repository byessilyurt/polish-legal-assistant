#!/usr/bin/env python3
"""
Complete Knowledge Base Ingestion Script
Processes all collected knowledge and ingests into Pinecone
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_pipeline.processors.chunker import DocumentChunker
from knowledge_pipeline.processors.embedder import DocumentEmbedder
from knowledge_pipeline.ingest.pinecone_ingestion import PineconeIngestor


def load_all_knowledge_files(data_dir: str) -> dict:
    """Load all knowledge JSON files"""
    data_path = Path(data_dir)
    processed_path = data_path / "processed"

    if not processed_path.exists():
        raise FileNotFoundError(f"Processed data directory not found: {processed_path}")

    knowledge_files = {
        "immigration": processed_path / "immigration_knowledge.json",
        "employment": processed_path / "employment_knowledge.json",
        "healthcare_banking": processed_path / "healthcare_banking_knowledge.json",
        "police_traffic": processed_path / "police_traffic_knowledge.json"
    }

    all_documents = []

    for category, file_path in knowledge_files.items():
        if file_path.exists():
            print(f"Loading {category} knowledge...")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                documents = data.get('documents', [])
                all_documents.extend(documents)
                print(f"  ✓ Loaded {len(documents)} documents")
        else:
            print(f"  ⚠️  File not found: {file_path}")

    return all_documents


def main():
    """Main ingestion pipeline"""

    print("=" * 60)
    print("Polish Legal Assistant - Knowledge Base Ingestion")
    print("=" * 60)
    print()

    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set")
        print("Please set it: export OPENAI_API_KEY=your-key")
        return

    if not os.getenv("PINECONE_API_KEY"):
        print("❌ PINECONE_API_KEY not set")
        print("Please set it: export PINECONE_API_KEY=your-key")
        return

    # Configuration
    data_dir = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data"
    )

    chunk_size = int(os.getenv("CHUNK_SIZE", "600"))  # Updated from 800 to 600
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "100"))
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    embedding_dim = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    index_name = os.getenv("PINECONE_INDEX_NAME", "polish-legal-kb")

    print("Configuration:")
    print(f"  Chunk size: {chunk_size} tokens")
    print(f"  Chunk overlap: {chunk_overlap} tokens")
    print(f"  Embedding model: {embedding_model}")
    print(f"  Embedding dimension: {embedding_dim}")
    print(f"  Index name: {index_name}")
    print()

    # Step 1: Load all knowledge files
    print("Step 1: Loading knowledge files...")
    documents = load_all_knowledge_files(data_dir)
    print(f"✓ Total documents loaded: {len(documents)}")
    print()

    # Step 2: Chunk documents
    print("Step 2: Chunking documents...")
    chunker = DocumentChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = chunker.chunk_all_documents(documents, strategy="hybrid")
    print(f"✓ Created {len(chunks)} chunks")
    print()

    # Step 3: Generate embeddings
    print("Step 3: Generating embeddings...")
    embedder = DocumentEmbedder(
        model=embedding_model,
        dimension=embedding_dim,
        batch_size=100
    )
    embedded_chunks = embedder.embed_chunks_sync(chunks, show_progress=True)
    print(f"✓ Generated {len(embedded_chunks)} embeddings")
    print()

    # Step 4: Create Pinecone index
    print("Step 4: Setting up Pinecone index...")
    ingestor = PineconeIngestor(index_name=index_name)
    ingestor.create_index(dimension=embedding_dim, metric="cosine")
    print()

    # Step 5: Ingest to Pinecone
    print("Step 5: Ingesting to Pinecone...")
    ingestor.ingest_chunks(embedded_chunks, batch_size=100)
    print()

    # Final stats
    stats = ingestor.get_index_stats()
    print("=" * 60)
    print("Ingestion Complete!")
    print("=" * 60)
    print(f"Total vectors in Pinecone: {stats.total_vector_count}")
    print(f"Index name: {index_name}")
    print()
    print("Your Polish Legal Assistant is ready to use!")
    print()


if __name__ == "__main__":
    main()
