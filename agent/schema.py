"""
Definisi Skema Pydantic untuk Komponen Kognitif Agentic RAG.
© 2026 Muryan Awaludin.
"""
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

class CorpusDocument(BaseModel):
    doc_id: str
    title: str
    category: str
    content: str

class ScoredDocument(BaseModel):
    doc_id: str
    title: str
    category: str
    content: str
    lexical_rank: int
    semantic_rank: int
    rrf_score: float
    relevance_grade: Literal["HIGHLY_RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT"] = "PARTIALLY_RELEVANT"
    relevance_explanation: str = ""

class HopTraceRecord(BaseModel):
    hop_number: int
    query_used: str
    strategy_applied: Literal["INITIAL_INTENT", "STEP_BACK_ABSTRACTION", "DECOMPOSED_GAP_RESOLUTION"]
    documents_retrieved: List[ScoredDocument]
    sufficiency_score: float
    detected_gaps: List[str]

class ComplianceAdvisoryOutput(BaseModel):
    original_inquiry: str
    total_hops_executed: int
    is_fully_sufficient: bool
    synthesized_advisory: str
    cited_regulations: List[str]
    compliance_verdict: Literal["COMPLIANT_WITH_CONDITIONS", "NON_COMPLIANT_HIGH_RISK", "AUDIT_REQUIRED"]
    mitigation_checklist: List[str]
    hop_traces: List[HopTraceRecord]