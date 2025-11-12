#!/usr/bin/env python3
"""Check Pinecone index stats"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "polish-legal-kb"))

stats = index.describe_index_stats()
print("Pinecone Index Stats:")
print(f"  Total vectors: {stats.total_vector_count}")
print(f"  Dimension: {stats.dimension}")
print(f"  Namespaces: {stats.namespaces}")

# Try a test query
print("\nTesting query...")
try:
    results = index.query(
        vector=[0.1] * 1536,
        top_k=3,
        include_metadata=True
    )
    print(f"  Found {len(results.matches)} results")
    if results.matches:
        print(f"  First result score: {results.matches[0].score}")
        print(f"  First result metadata: {results.matches[0].metadata}")
except Exception as e:
    print(f"  Error: {e}")
