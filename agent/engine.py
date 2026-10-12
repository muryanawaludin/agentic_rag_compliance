"""
Orkestrator Agentic RAG: Navigasi Multilangkah dan Query Rewriting.
Mengatur siklus iteratif penarikan, evaluasi relevansi, penulisan ulang kueri, dan sintesis legal.
© 2026 Muryan Awaludin. Seluruh hak cipta dilindungi undang-undang.
"""
from typing import List, Tuple, Dict
from config import CONFIG
from agent.schema import HopTraceRecord, ComplianceAdvisoryOutput, ScoredDocument
from agent.retriever import HybridRetriever
from agent.grader import DocumentGrader

class AgenticRAGComplianceEngine:
    def __init__(self):
        self.retriever = HybridRetriever(CONFIG.CORPUS_PATH)
        self.grader = DocumentGrader()

    def _rewrite_query_for_gap(self, original_query: str, gap: str, hop: int) -> Tuple[str, str]:
        """Menghasilkan kueri baru berbasis teknik Step-Back atau Decomposed Gap Resolution."""
        gap_lower = gap.lower()
        if "sanksi" in gap_lower or "denda" in gap_lower:
            return (
                "Sanksi administratif dan denda maksimal pelanggaran data pribadi keputusan otomatis UU PDP",
                "DECOMPOSED_GAP_RESOLUTION"
            )
        elif "keberatan" in gap_lower or "intervensi manusia" in gap_lower:
            return (
                "Hak subjek data menolak keputusan otomatis profiling dan opsi human-in-the-loop OJK",
                "DECOMPOSED_GAP_RESOLUTION"
            )
        elif "dpia" in gap_lower:
            return (
                "Kewajiban Data Protection Impact Assessment DPIA pemrosesan data risiko tinggi teknologi baru",
                "STEP_BACK_ABSTRACTION"
            )
        else:
            return (
                f"Prinsip umum tata kelola kecerdasan buatan dan pelindungan data: {original_query}",
                "STEP_BACK_ABSTRACTION"
            )

    def execute_compliance_inquiry(self, inquiry_text: str) -> ComplianceAdvisoryOutput:
        hop_traces: List[HopTraceRecord] = []
        all_accumulated_docs: Dict[str, ScoredDocument] = {}
        
        current_query = inquiry_text
        current_strategy = "INITIAL_INTENT"
        hop = 1
        is_sufficient = False

        while hop <= CONFIG.MAX_REASONING_HOPS and not is_sufficient:
            # 1. Penarikan Hibrida Dokumen
            retrieved_docs = self.retriever.retrieve(current_query, top_k=CONFIG.TOP_K_RETRIEVAL)
            
            # 2. Evaluasi Relevansi dan Kecukupan
            graded_docs, sufficiency, gaps = self.grader.evaluate_documents(current_query, retrieved_docs)
            
            # Akumulasi dokumen relevan
            for d in graded_docs:
                if d.relevance_grade in ["HIGHLY_RELEVANT", "PARTIALLY_RELEVANT"]:
                    all_accumulated_docs[d.doc_id] = d

            trace = HopTraceRecord(
                hop_number=hop,
                query_used=current_query,
                strategy_applied=current_strategy,
                documents_retrieved=graded_docs,
                sufficiency_score=sufficiency,
                detected_gaps=gaps
            )
            hop_traces.append(trace)

            # 3. Keputusan Transisi State Agen
            if sufficiency >= CONFIG.SUFFICIENCY_THRESHOLD or not gaps:
                is_sufficient = True
                break
            else:
                primary_gap = gaps[0]
                current_query, current_strategy = self._rewrite_query_for_gap(inquiry_text, primary_gap, hop)
                hop += 1

        # 4. Sintesis Legal Komprehensif
        cited_ids = list(all_accumulated_docs.keys())
        advisory, verdict, mitigations = self._synthesize_advisory(inquiry_text, all_accumulated_docs, is_sufficient)

        return ComplianceAdvisoryOutput(
            original_inquiry=inquiry_text,
            total_hops_executed=len(hop_traces),
            is_fully_sufficient=is_sufficient,
            synthesized_advisory=advisory,
            cited_regulations=cited_ids,
            compliance_verdict=verdict,
            mitigation_checklist=mitigations,
            hop_traces=hop_traces
        )

    def _synthesize_advisory(self, inquiry: str, docs: Dict[str, ScoredDocument], sufficient: bool):
        has_pdp = any("REG-PDP" in k for k in docs)
        has_ojk = any("REG-OJK" in k for k in docs)
        has_iso = any("REG-ISO" in k for k in docs)

        advisory_paragraphs = []
        advisory_paragraphs.append(
            f"Berdasarkan analisis navigasi multi-hop regulasi terhadap pertanyaan: \"{inquiry}\", sistem memetakan temuan hukum berikut:\n"
        )

        if "REG-PDP-PASAL-40" in docs:
            advisory_paragraphs.append(
                "1. Hak Subjek Data & Larangan Otomasi Penuh [REG-PDP-PASAL-40]: Nasabah memiliki hak hukum mutlak untuk "
                "menolak keputusan yang diambil semata-mata oleh pemrosesan otomatis (seperti penolakan kredit berbasis model AI). "
                "Penerapan sistem otomatis tanpa persetujuan eksplisit merupakan pelanggaran hukum pelindungan data."
            )

        if "REG-PDP-PASAL-37" in docs:
            advisory_paragraphs.append(
                "2. Kewajiban Uji Dampak Risiko Tinggi [REG-PDP-PASAL-37]: Sebelum model AI diterapkan untuk profiling atau scoring, "
                "organisasi wajib melakukan Data Protection Impact Assessment (DPIA) guna mendokumentasikan mitigasi risiko."
            )

        if "REG-PDP-PASAL-57" in docs:
            advisory_paragraphs.append(
                "3. Risiko Sanksi & Denda Finansial [REG-PDP-PASAL-57]: Pelanggaran tata kelola ini mengekspos lembaga pada sanksi "
                "peringatan tertulis, pembekuan operasional pemrosesan, hingga denda administratif maksimal sebesar 2% dari pendapatan tahunan."
            )

        if "REG-OJK-AI-CREDIT" in docs:
            advisory_paragraphs.append(
                "4. Kewajiban Tata Kelola Sektor Keuangan [REG-OJK-AI-CREDIT]: Penyelenggara wajib menjamin transparansi algoritma "
                "serta menyediakan mekanisme banding dengan keterlibatan manusia (human-in-the-loop)."
            )

        if has_pdp and has_ojk:
            verdict = "NON_COMPLIANT_HIGH_RISK"
            summary_statement = (
                "PENGGUNAAN AI OTOMATIS PENUH BERISIKO TINGGI DAN TIDAK PATUH jika dijalankan tanpa mekanisme intervensi manusia dan pelaksanaan DPIA."
            )
        elif sufficient:
            verdict = "COMPLIANT_WITH_CONDITIONS"
            summary_statement = "Sistem dapat beroperasi dengan syarat seluruh klausul perlindungan data terpenuhi."
        else:
            verdict = "AUDIT_REQUIRED"
            summary_statement = "Bukti dokumen regulasi belum lengkap secara menyeluruh. Memerlukan audit kepatuhan mendalam."

        advisory_paragraphs.append(f"\nKESIMPULAN AUDITOR: {summary_statement}")

        mitigations = [
            "Laksanakan dokumen resmi Data Protection Impact Assessment (DPIA) sebelum peluncuran model.",
            "Integrasikan antarmuka Human-in-the-Loop: setiap penolakan otomatis harus dapat ditinjau ulang oleh analis kredit manusia.",
            "Perbarui Syarat & Ketentuan aplikasi untuk mencantumkan klausul persetujuan pemrosesan data otomatis (Explicit Consent).",
            "Jalankan audit bias dan verifikasi algoritma independen sekurang-kurangnya sekali dalam setahun sesuai ISO/IEC 42001."
        ]

        return "\n\n".join(advisory_paragraphs), verdict, mitigations