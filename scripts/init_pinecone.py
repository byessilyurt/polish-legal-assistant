#!/usr/bin/env python3
"""
Initialize Pinecone Index
Creates a new Pinecone index for the Polish Legal Assistant
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_pipeline.ingest.pinecone_ingestion import PineconeIngestor


def main():
    """Initialize Pinecone index"""

    print("=" * 60)
    print("Pinecone Index Initialization")
    print("=" * 60)
    print()

    # Check API key
    if not os.getenv("PINECONE_API_KEY"):
        print("❌ PINECONE_API_KEY not set")
        print("Please set it: export PINECONE_API_KEY=your-key")
        return

    # Configuration
    index_name = os.getenv("PINECONE_INDEX_NAME", "polish-legal-kb")
    dimension = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    metric = os.getenv("PINECONE_METRIC", "cosine")
    cloud = os.getenv("PINECONE_CLOUD", "aws")
    region = os.getenv("PINECONE_REGION", "us-east-1")

    print("Configuration:")
    print(f"  Index name: {index_name}")
    print(f"  Dimension: {dimension}")
    print(f"  Metric: {metric}")
    print(f"  Cloud: {cloud}")
    print(f"  Region: {region}")
    print()

    # Create index
    ingestor = PineconeIngestor(index_name=index_name)

    try:
        ingestor.create_index(
            dimension=dimension,
            metric=metric,
            cloud=cloud,
            region=region
        )
        print()
        print("✓ Pinecone index initialized successfully!")
        print()
        print("Next steps:")
        print("  1. Run: python scripts/ingest_all_knowledge.py")
        print("  2. Start the backend: cd backend && uvicorn app.main:app --reload")
        print("  3. Start the frontend: cd frontend && npm run dev")
        print()

    except Exception as e:
        print(f"❌ Error creating index: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
