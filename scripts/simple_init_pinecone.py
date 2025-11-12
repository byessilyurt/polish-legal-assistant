#!/usr/bin/env python3
"""
Initialize Pinecone Index - Simplified Version
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import time

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def main():
    print("=" * 60)
    print("Pinecone Index Initialization")
    print("=" * 60)
    print()

    # Check API key
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ PINECONE_API_KEY not set")
        return

    # Configuration
    index_name = os.getenv("PINECONE_INDEX_NAME", "polish-legal-kb")
    dimension = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

    print("Configuration:")
    print(f"  Index name: {index_name}")
    print(f"  Dimension: {dimension}")
    print()

    # Initialize Pinecone
    pc = Pinecone(api_key=api_key)

    # Check if index exists
    existing_indexes = [idx.name for idx in pc.list_indexes()]

    if index_name in existing_indexes:
        print(f"✓ Index '{index_name}' already exists")
        index = pc.Index(index_name)
        stats = index.describe_index_stats()
        print(f"  Current vector count: {stats.total_vector_count}")
    else:
        # Create new index
        print(f"Creating index '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

        # Wait for index to be ready
        print("Waiting for index to be ready...")
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)

        print(f"✓ Index '{index_name}' created successfully")

    print()
    print("✓ Pinecone index initialized!")
    print()

if __name__ == "__main__":
    main()
