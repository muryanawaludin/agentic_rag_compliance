"""
Hybrid Multi-Hop Retriever Engine:
Menggabungkan Pencarian Leksikal (BM25-Style) dan Pencarian Semantik Vektor (TF-IDF Cosine),
kemudian menyatukan peringkat menggunakan Reciprocal Rank Fusion (RRF).
© 2026 Muryan Awaludin.
"""
import json
import os
import math
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import CONFIG
from agent.schema import CorpusDocument, ScoredDocument

class HybridRetriever:
    def __init__(self, corpus_path: str = CONFIG.CORPUS_PATH):
        self.corpus: List[CorpusDocument] = []
        self._load_corpus(corpus_path)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        if self.corpus:
            corpus_texts = [f"{d.title} {d.content}" for d in self.corpus]
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus_texts)
        else:
            self.tfidf_matrix = None

    def _load_corpus(self, path: str):
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.corpus = [CorpusDocument(**item) for item in data]

    def _calculate_lexical_overlap(self, query: str, text: str) -> float:
        """Pencocokan term leksikal berbasis frekuensi kata kunci."""
        query_words = set(query.lower().split())
        text_words = text.lower().split()
        if not text_words or not query_words:
            return 0.0
        matches = sum(1 for word in text_words if word in query_words)
        return float(matches) / (len(text_words) + 1.0)

    def retrieve(self, query: str, top_k: int = CONFIG.TOP_K_RETRIEVAL) -> List[ScoredDocument]:
        if not self.corpus or self.tfidf_matrix is None:
            return []

        # 1. Peringkat Semantik (Cosine Similarity)
        query_vec = self.vectorizer.transform([query])
        semantic_sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        semantic_ranked_indices = np.argsort(semantic_sims)[::-1]
        semantic_rank_map = {idx: rank + 1 for rank, idx in enumerate(semantic_ranked_indices)}

        # 2. Peringkat Leksikal (Keyword Match)
        lexical_scores = [
            self._calculate_lexical_overlap(query, f"{d.title} {d.content}")
            for d in self.corpus
        ]
        lexical_ranked_indices = np.argsort(lexical_scores)[::-1]
        lexical_rank_map = {idx: rank + 1 for rank, idx in enumerate(lexical_ranked_indices)}

        # 3. Reciprocal Rank Fusion (RRF)
        scored_docs: List[ScoredDocument] = []
        for idx, doc in enumerate(self.corpus):
            r_sem = semantic_rank_map[idx]
            r_lex = lexical_rank_map[idx]
            
            rrf_score = (1.0 / (CONFIG.RRF_K_PARAMETER + r_sem)) + (1.0 / (CONFIG.RRF_K_PARAMETER + r_lex))

            scored_docs.append(ScoredDocument(
                doc_id=doc.doc_id,
                title=doc.title,
                category=doc.category,
                content=doc.content,
                lexical_rank=r_lex,
                semantic_rank=r_sem,
                rrf_score=round(rrf_score, 5)
            ))

        # Urutkan berdasarkan skor RRF tertinggi
        scored_docs.sort(key=lambda x: x.rrf_score, reverse=True)
        return scored_docs[:top_k]