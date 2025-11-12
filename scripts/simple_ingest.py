#!/usr/bin/env python3
"""
Simple Knowledge Base Ingestion Script
Ingests all knowledge documents into Pinecone
"""

import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pinecone import Pinecone
import tiktoken

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "polish-legal-kb")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))

# Initialize clients
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)
encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Count tokens in text"""
    return len(encoding.encode(text))


def chunk_text(text: str, max_tokens: int = CHUNK_SIZE) -> list:
    """Simple chunking by sentences"""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

        if current_tokens + sentence_tokens > max_tokens and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_tokens = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


async def generate_embedding(text: str) -> list:
    """Generate embedding for text"""
    try:
        response = await openai_client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL,
            dimensions=EMBEDDING_DIM
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"  ⚠️  Error generating embedding: {e}")
        return None


async def process_document(doc: dict, doc_idx: int) -> list:
    """Process a single document into chunks with embeddings"""
    content = doc.get("content", "")
    metadata = doc.get("metadata", {})
    doc_id = doc.get("id", f"doc-{doc_idx}")

    # Chunk the document
    chunks = chunk_text(content)

    # Process each chunk
    vectors = []
    for chunk_idx, chunk_content in enumerate(chunks):
        # Generate embedding
        embedding = await generate_embedding(chunk_content)
        if not embedding:
            continue

        # Prepare metadata
        chunk_metadata = {
            **metadata,
            "content": chunk_content[:1000],  # Limit content length
            "chunk_index": chunk_idx,
            "total_chunks": len(chunks),
            "parent_document_id": doc_id
        }

        # Clean metadata
        clean_metadata = {}
        for key, value in chunk_metadata.items():
            if value is not None:
                if isinstance(value, (str, int, float, bool)):
                    clean_metadata[key] = value
                else:
                    clean_metadata[key] = str(value)

        # Create vector
        vector_id = f"{doc_id}__chunk_{chunk_idx}"
        vector = {
            "id": vector_id,
            "values": embedding,
            "metadata": clean_metadata
        }
        vectors.append(vector)

    return vectors


async def main():
    print("=" * 60)
    print("Polish Legal Assistant - Knowledge Base Ingestion")
    print("=" * 60)
    print()

    # Check API keys
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set")
        return
    if not PINECONE_API_KEY:
        print("❌ PINECONE_API_KEY not set")
        return

    # Load knowledge files
    data_dir = Path(__file__).parent.parent / "data" / "processed"

    knowledge_files = {
        "immigration": data_dir / "immigration_knowledge.json",
        "employment": data_dir / "employment_knowledge.json",
        "healthcare_banking": data_dir / "healthcare_banking_knowledge.json",
        "police_traffic": data_dir / "police_traffic_knowledge.json"
    }

    all_documents = []

    print("Loading knowledge files...")
    for category, file_path in knowledge_files.items():
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                documents = data.get('documents', [])
                all_documents.extend(documents)
                print(f"  ✓ Loaded {len(documents)} documents from {category}")
        else:
            print(f"  ⚠️  File not found: {file_path}")

    print(f"\nTotal documents: {len(all_documents)}")
    print()

    # Process documents
    print("Processing documents (generating embeddings)...")
    all_vectors = []

    for idx, doc in enumerate(all_documents):
        if idx % 10 == 0:
            print(f"  Processing document {idx+1}/{len(all_documents)}...")

        vectors = await process_document(doc, idx)
        all_vectors.extend(vectors)

    print(f"✓ Generated {len(all_vectors)} vector embeddings")
    print()

    # Upsert to Pinecone
    print("Uploading to Pinecone...")
    batch_size = 100

    for i in range(0, len(all_vectors), batch_size):
        batch = all_vectors[i:i + batch_size]
        try:
            index.upsert(vectors=batch)
            print(f"  Uploaded {min(i + batch_size, len(all_vectors))}/{len(all_vectors)} vectors")
        except Exception as e:
            print(f"  ❌ Error upserting batch: {e}")

    # Get final stats
    stats = index.describe_index_stats()

    print()
    print("=" * 60)
    print("Ingestion Complete!")
    print("=" * 60)
    print(f"Total vectors in Pinecone: {stats.total_vector_count}")
    print(f"Index name: {INDEX_NAME}")
    print()
    print("Your Polish Legal Assistant is ready to use!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
