#!/usr/bin/env python3
"""
Migration script to create polish-legal-kb-v2 index with improved chunking
This creates a new index for zero-downtime migration
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file manually
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set environment variable for new index name
os.environ['PINECONE_INDEX_NAME'] = 'polish-legal-kb-v2'

# Import and run the main ingestion script
from scripts.ingest_all_knowledge import main

if __name__ == "__main__":
    print("=" * 70)
    print("MIGRATION TO POLISH-LEGAL-KB-V2")
    print("=" * 70)
    print()
    print("This script will:")
    print("1. Create a new Pinecone index: polish-legal-kb-v2")
    print("2. Ingest all 248 documents with improved chunking (600 tokens)")
    print("3. Leave the old index intact for rollback if needed")
    print()
    print("Expected results:")
    print("- 248 documents → ~750-900 chunks (with chunk_size=600)")
    print("- Better retrieval precision with smaller chunks")
    print()

    response = input("Proceed with migration? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        sys.exit(0)

    print()
    print("Starting migration...")
    print()

    # Run ingestion
    main()

    print()
    print("=" * 70)
    print("MIGRATION COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Test queries against the new index")
    print("2. Update .env to use PINECONE_INDEX_NAME=polish-legal-kb-v2")
    print("3. Restart backend services")
    print("4. Monitor for 24-48 hours")
    print("5. Delete old index if successful")
    print()
