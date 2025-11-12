"""
Document Chunking Module
Implements hybrid chunking strategy for legal documents
"""

import re
from typing import List, Dict, Any
import tiktoken


class DocumentChunker:
    """Chunks legal documents using hybrid semantic and structural approach"""

    def __init__(
        self,
        chunk_size: int = 600,  # Updated from 800 to 600 for better precision
        chunk_overlap: int = 100,
        encoding_name: str = "cl100k_base"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))

    def chunk_document(
        self,
        document: Dict[str, Any],
        strategy: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        Chunk a document based on strategy

        Args:
            document: Document dict with content and metadata
            strategy: "semantic", "structural", or "hybrid"

        Returns:
            List of chunk dicts with content and metadata
        """
        content = document.get("content", "")
        metadata = document.get("metadata", {})

        if strategy == "semantic":
            chunks = self._semantic_chunk(content)
        elif strategy == "structural":
            chunks = self._structural_chunk(content)
        else:  # hybrid
            chunks = self._hybrid_chunk(content)

        # Create chunk documents with metadata
        chunk_docs = []
        for idx, chunk_text in enumerate(chunks):
            chunk_doc = {
                "id": f"{document.get('id', 'doc')}__chunk_{idx}",
                "content": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                    "parent_document_id": document.get("id"),
                    "token_count": self.count_tokens(chunk_text)
                }
            }
            chunk_docs.append(chunk_doc)

        return chunk_docs

    def _semantic_chunk(self, text: str) -> List[str]:
        """
        Semantic chunking for narrative content
        Preserves context by chunking on sentence boundaries
        """
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)

            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                # Create chunk with overlap
                chunks.append(" ".join(current_chunk))

                # Calculate overlap sentences
                overlap_sentences = []
                overlap_tokens = 0
                for s in reversed(current_chunk):
                    s_tokens = self.count_tokens(s)
                    if overlap_tokens + s_tokens <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break

                current_chunk = overlap_sentences
                current_tokens = overlap_tokens

            current_chunk.append(sentence)
            current_tokens += sentence_tokens

        # Add remaining chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _structural_chunk(self, text: str) -> List[str]:
        """
        Structural chunking for procedural content
        Splits on structural markers (numbered lists, headers, etc.)
        """
        # Detect structural patterns
        patterns = [
            r'\n\n##\s+',  # Headers
            r'\n\n\d+\.\s+',  # Numbered lists
            r'\n\n[A-Z][a-z]+:\s+',  # Label patterns (Step:, Note:, etc.)
            r'\n\n-\s+',  # Bullet points
        ]

        # Split on structural markers
        sections = [text]
        for pattern in patterns:
            new_sections = []
            for section in sections:
                parts = re.split(pattern, section)
                new_sections.extend([p for p in parts if p.strip()])
            sections = new_sections

        # Group small sections to meet chunk_size
        chunks = []
        current_chunk = []
        current_tokens = 0

        for section in sections:
            section_tokens = self.count_tokens(section)

            # If single section exceeds chunk_size, use semantic chunking
            if section_tokens > self.chunk_size:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_tokens = 0

                # Semantic chunk this large section
                sub_chunks = self._semantic_chunk(section)
                chunks.extend(sub_chunks)

            elif current_tokens + section_tokens > self.chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [section]
                current_tokens = section_tokens

            else:
                current_chunk.append(section)
                current_tokens += section_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def _hybrid_chunk(self, text: str) -> List[str]:
        """
        Hybrid approach - tries structural first, falls back to semantic
        """
        # Check if content has structural markers
        has_structure = bool(re.search(
            r'(\n\n##\s+|\n\n\d+\.\s+|\n\n[A-Z][a-z]+:\s+|\n\n-\s+)',
            text
        ))

        if has_structure:
            return self._structural_chunk(text)
        else:
            return self._semantic_chunk(text)

    def chunk_all_documents(
        self,
        documents: List[Dict[str, Any]],
        strategy: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        Chunk multiple documents

        Args:
            documents: List of document dicts
            strategy: Chunking strategy

        Returns:
            List of all chunks from all documents
        """
        all_chunks = []

        for doc in documents:
            chunks = self.chunk_document(doc, strategy)
            all_chunks.extend(chunks)

        return all_chunks


if __name__ == "__main__":
    # Test chunking
    chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)

    test_doc = {
        "id": "test-1",
        "content": """
        Residence Permits in Poland

        ## Types of Permits

        1. Temporary residence permit - Valid for up to 3 years
        2. Permanent residence permit - Valid indefinitely
        3. EU long-term residence - Valid across EU

        ## Application Process

        Step 1: Gather required documents
        Step 2: Submit application at voivodeship office
        Step 3: Wait for decision (up to 60 days)

        Note: Always keep copies of all documents.
        """,
        "metadata": {
            "category": "immigration",
            "source": "test"
        }
    }

    chunks = chunker.chunk_document(test_doc)
    print(f"Created {len(chunks)} chunks")
    for chunk in chunks:
        print(f"\nChunk {chunk['metadata']['chunk_index']}:")
        print(f"Tokens: {chunk['metadata']['token_count']}")
        print(chunk['content'][:200])
