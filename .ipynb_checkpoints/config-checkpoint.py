"""
Konfigurasi Global Sistem Agentic RAG Kepatuhan Regulasi.
© 2026 Muryan Awaludin. Seluruh hak cipta dilindungi undang-undang.
"""
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class AgenticRAGConfig:
    APP_TITLE: str = "Agentic RAG: Regulatory Compliance & AI Governance Advisor"
    AUTHOR_COPYRIGHT: str = "© 2026 Muryan Awaludin. Seluruh hak cipta dilindungi undang-undang."
    CORPUS_PATH: str = os.path.join(os.path.dirname(__file__), "data", "regulatory_knowledge_corpus.json")
    
    # Ambang Batas Evaluasi Kognitif
    RRF_K_PARAMETER: int = 60
    TOP_K_RETRIEVAL: int = 3
    SUFFICIENCY_THRESHOLD: float = 0.70
    AMBIGUITY_THRESHOLD: float = 0.40
    MAX_REASONING_HOPS: int = 3

CONFIG = AgenticRAGConfig()