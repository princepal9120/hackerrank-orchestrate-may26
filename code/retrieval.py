"""Deterministic BM25-style retrieval over local corpus chunks."""
from __future__ import annotations

import math
from collections import Counter

from models import Chunk, RetrievalHit
from text_utils import tokenize


class BM25Retriever:
    """Small dependency-free BM25 implementation with domain-aware scoring."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.size = max(1, len(chunks))
        self.avg_doc_len = sum(len(chunk.tokens) for chunk in chunks) / self.size if chunks else 1.0
        document_frequency: Counter[str] = Counter()
        for chunk in chunks:
            document_frequency.update(set(chunk.tokens))
        self.idf = {token: math.log(1 + (self.size - freq + 0.5) / (freq + 0.5)) for token, freq in document_frequency.items()}

    def search(self, query: str, company: str = "", limit: int = 6) -> list[RetrievalHit]:
        query_terms = Counter(tokenize(query))
        if not query_terms:
            return []
        company = (company or "").strip().lower()
        hits: list[RetrievalHit] = []
        for chunk in self.chunks:
            domain_penalty = 1.0
            if company in {"hackerrank", "claude", "visa"} and chunk.domain.lower() != company:
                domain_penalty = 0.35
            term_frequency = Counter(chunk.tokens)
            doc_len = len(chunk.tokens) or 1
            score = 0.0
            for term in query_terms:
                if term not in term_frequency:
                    continue
                freq = term_frequency[term]
                score += self.idf.get(term, 0.0) * (freq * 2.0) / (freq + 1.2 * (1 - 0.75 + 0.75 * doc_len / self.avg_doc_len))
            title_text = f"{chunk.title} {chunk.path}".lower()
            for term in query_terms:
                if term in title_text:
                    score += 0.7
            score *= domain_penalty
            if score > 0:
                hits.append(RetrievalHit(score=score, chunk=chunk))
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return hits[:limit]
