"""
PQC-Day and the Machine — Chapter 13
Pattern: RAG service for PQC intelligence — chunking, search, and reranking

This is a didactic example from the book, not production code.
See chapter 13 for full context and explanation.

Requires: pip install anthropic tiktoken
"""

import os
import zlib
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

try:
    import tiktoken
except ImportError:
    tiktoken = None

try:
    import anthropic
except ImportError:
    anthropic = None


# --- Chunker ---

class RAGChunker:
    """Document chunker with controlled overlap."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if tiktoken:
            self.encoder = tiktoken.get_encoding("cl100k_base")
        else:
            self.encoder = None

    def _count_tokens(self, text: str) -> int:
        if self.encoder:
            return len(self.encoder.encode(text))
        # Fallback: approximate 1 token per 4 characters
        return len(text) // 4

    def chunk_document(self, content: str, title: str) -> List[Dict]:
        """Split document into chunks with metadata.

        Respects section boundaries when possible.
        """
        if isinstance(content, bytes):
            # Decompress if stored as compressed bytes
            content = zlib.decompress(content).decode('utf-8')

        if self.encoder:
            tokens = self.encoder.encode(content)
            total_tokens = len(tokens)
        else:
            # Fallback to character-based chunking
            tokens = list(content)
            total_tokens = len(tokens)

        chunks = []
        start = 0
        chunk_index = 0

        while start < total_tokens:
            end = min(start + self.chunk_size, total_tokens)

            if self.encoder:
                chunk_tokens = tokens[start:end]
                chunk_text = self.encoder.decode(chunk_tokens)
            else:
                chunk_text = ''.join(tokens[start:end])

            # Try to cut at a paragraph boundary
            if end < total_tokens:
                chunk_text = self._adjust_boundary(chunk_text)

            chunks.append({
                'index': chunk_index,
                'text': chunk_text,
                'token_count': self._count_tokens(chunk_text),
                'source_title': title,
                'start_token': start,
                'end_token': end,
            })

            # Advance with overlap
            start = end - self.chunk_overlap
            chunk_index += 1

        return chunks

    def _adjust_boundary(self, text: str) -> str:
        """Adjust cut to the last complete paragraph."""
        last_para = text.rfind('\n\n')
        if last_para > len(text) * 0.7:
            return text[:last_para]
        last_sentence = text.rfind('. ')
        if last_sentence > len(text) * 0.8:
            return text[:last_sentence + 1]
        return text


# --- PQC synonym expansion ---

PQC_SYNONYMS = {
    'Kyber': 'Kyber ML-KEM FIPS-203 CRYSTALS-Kyber',
    'ML-KEM': 'ML-KEM Kyber FIPS-203',
    'Dilithium': 'Dilithium ML-DSA FIPS-204 CRYSTALS-Dilithium',
    'ML-DSA': 'ML-DSA Dilithium FIPS-204',
    'SPHINCS+': 'SPHINCS+ SLH-DSA FIPS-205',
    'SLH-DSA': 'SLH-DSA SPHINCS+ FIPS-205',
    'RSA': 'RSA RSA-2048 RSA-4096',
    'ECDSA': 'ECDSA ECC elliptic-curve P-256 P-384',
}


# --- Search service ---

class RAGSearchService:
    """Search service for PQC knowledge base with reranking."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self._knowledge_base: List[Dict] = []

    def load_documents(self, documents: List[Dict]):
        """Load pre-chunked documents into the knowledge base.

        Each document: {'title': str, 'text': str, 'collection_type': str}
        """
        chunker = RAGChunker()
        for doc in documents:
            chunks = chunker.chunk_document(doc['text'], doc['title'])
            for chunk in chunks:
                chunk['collection_type'] = doc.get('collection_type', 'custom')
                chunk['source_url'] = doc.get('source_url', '')
            self._knowledge_base.extend(chunks)

    def search(
        self,
        query: str,
        collection_types: Optional[List[str]] = None,
        max_chunks: int = 5
    ) -> List[Dict]:
        """Search for relevant chunks in the knowledge base.

        1. Expand query with PQC synonyms
        2. Filter collections by type
        3. Score by keyword match
        4. Rerank with Claude
        """
        # Step 1: Synonym expansion
        expanded_query = self._expand_crypto_synonyms(query)
        query_terms = set(expanded_query.lower().split())

        # Step 2: Filter by collection type
        candidates = self._knowledge_base
        if collection_types:
            candidates = [c for c in candidates
                          if c.get('collection_type') in collection_types]

        if not candidates:
            return []

        # Step 3: Score by keyword overlap
        scored = []
        for chunk in candidates:
            text_lower = chunk['text'].lower()
            score = sum(1 for term in query_terms if term in text_lower)
            if score > 0:
                scored.append({**chunk, '_score': score})

        scored.sort(key=lambda x: x['_score'], reverse=True)

        # Step 4: Rerank top candidates with Claude
        if len(scored) > max_chunks and anthropic and self.api_key:
            scored = self._rerank_with_llm(query, scored[:max_chunks * 3])

        return scored[:max_chunks]

    def _expand_crypto_synonyms(self, query: str) -> str:
        """Expand PQC terminology synonyms."""
        expanded = query
        for term, expansion in PQC_SYNONYMS.items():
            if term.lower() in query.lower():
                expanded = f"{expanded} {expansion}"
        return expanded

    def _rerank_with_llm(self, query: str,
                          candidates: List[Dict]) -> List[Dict]:
        """Rerank candidates using Claude as relevance judge."""
        if not anthropic:
            return candidates

        chunks_text = "\n---\n".join([
            f"[{i}] {c['text'][:500]}"
            for i, c in enumerate(candidates)
        ])

        client = anthropic.Anthropic(api_key=self.api_key)

        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    f"Given the query: '{query}'\n\n"
                    f"Rank these fragments from most to least relevant. "
                    f"Respond only with indices separated by commas:\n\n"
                    f"{chunks_text}"
                )
            }]
        )

        try:
            indices = [
                int(x.strip())
                for x in message.content[0].text.split(',')
                if x.strip().isdigit()
            ]
            reranked = [candidates[i] for i in indices if i < len(candidates)]
            return reranked if reranked else candidates
        except (ValueError, IndexError):
            return candidates


# --- RAG prompt builder ---

def build_rag_prompt(
    user_message: str,
    rag_chunks: list,
    system_base: str
) -> tuple:
    """Build messages with RAG context injected.

    Chunks are added to the system prompt so the model treats them
    as a source of truth.
    """
    context_block = "\n\n---\n\n".join([
        f"**Source:** {chunk['source_title']}\n"
        f"**Type:** {chunk.get('collection_type', 'N/A')}\n\n"
        f"{chunk['text']}"
        for chunk in rag_chunks
    ])

    system_prompt = (
        f"{system_base}\n\n"
        f"## Knowledge base (verified sources)\n\n"
        f"Use the following information as primary source to "
        f"answer questions about standards, regulations, and "
        f"PQC migration requirements. Cite the source when "
        f"you use it.\n\n{context_block}"
    )

    return system_prompt, [{"role": "user", "content": user_message}]


# --- Main ---
if __name__ == '__main__':
    # Example: load sample documents and search
    sample_docs = [
        {
            'title': 'NIST FIPS 203 - ML-KEM Standard',
            'text': (
                'ML-KEM (Module-Lattice-Based Key Encapsulation Mechanism) '
                'is the NIST standard for post-quantum key encapsulation. '
                'It replaces RSA and ECDH for key exchange. ML-KEM-768 '
                'offers security equivalent to AES-192. The standard was '
                'finalized in August 2024 as FIPS 203.'
            ),
            'collection_type': 'documentation',
            'source_url': 'https://csrc.nist.gov/pubs/fips/203/final'
        },
        {
            'title': 'CNSA 2.0 Timeline',
            'text': (
                'The NSA CNSA 2.0 suite establishes deadlines for migrating '
                'to post-quantum cryptography. By 2030, all software and '
                'firmware signing must use ML-DSA or SLH-DSA. By 2033, all '
                'key establishment must use ML-KEM. Legacy algorithms like '
                'RSA and ECDSA must be phased out according to this timeline.'
            ),
            'collection_type': 'framework',
            'source_url': 'https://media.defense.gov/2022/Sep/07/cnsa-2.0.pdf'
        },
        {
            'title': 'DORA PQC Requirements',
            'text': (
                'The Digital Operational Resilience Act (DORA) requires '
                'financial entities to implement cryptographic controls that '
                'ensure long-term data confidentiality. This includes preparing '
                'for the transition to post-quantum cryptography to protect '
                'against harvest-now-decrypt-later attacks on financial data.'
            ),
            'collection_type': 'framework',
        },
    ]

    service = RAGSearchService()
    service.load_documents(sample_docs)

    print(f"Knowledge base loaded: {len(service._knowledge_base)} chunks\n")

    # Search
    query = "What are the CNSA 2.0 deadlines for PQC migration?"
    results = service.search(
        query=query,
        collection_types=['framework', 'documentation'],
        max_chunks=3
    )

    print(f"Query: {query}")
    print(f"Results: {len(results)}\n")

    for r in results:
        print(f"  [{r.get('collection_type', 'N/A')}] {r['source_title']}")
        print(f"  {r['text'][:100]}...\n")

    # Build RAG prompt
    system, messages = build_rag_prompt(
        user_message=query,
        rag_chunks=results,
        system_base="You are a PQC migration expert."
    )
    print(f"System prompt length: {len(system)} chars")
    print(f"Context sources: {len(results)}")
