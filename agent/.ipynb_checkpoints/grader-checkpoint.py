"""
Document Relevance and Sufficiency Grader:
Mengevaluasi kualitas dokumen yang diambil, menyaring noise, dan mendeteksi celah informasi.
© 2026 Muryan Awaludin.
"""
from typing import List, Tuple
from agent.schema import ScoredDocument
from config import CONFIG

class DocumentGrader:

    @staticmethod
    def evaluate_documents(query: str, docs: List[ScoredDocument]) -> Tuple[List[ScoredDocument], float, List[str]]:
        """
        Menilai relevansi setiap dokumen terhadap kueri dan mengevaluasi kecukupan bukti.
        Mengembalikan dokumen terklasifikasi, skor kecukupan (0.0-1.0), dan daftar gap informasi.
        """
        query_lower = query.lower()
        graded_docs: List[ScoredDocument] = []
        relevant_count = 0
        gaps: List[str] = []

        # Deteksi variabel hukum utama yang harus terpenuhi
        aspects_to_check = {
            "dpia_risk": any(k in query_lower for k in ["dpia", "risiko", "penilaian dampak", "otomatis"]),
            "human_in_loop": any(k in query_lower for k in ["banding", "keberatan", "intervensi manusia", "hak"]),
            "sanctions": any(k in query_lower for k in ["sanksi", "denda", "hukuman", "akibat hukum"]),
            "explainability": any(k in query_lower for k in ["transparansi", "kredit", "algoritma", "fairness"])
        }

        found_aspects = set()

        for doc in docs:
            content_lower = doc.content.lower()
            
            # Cek kecocokan semantik konten dokumen
            matches = [term for term in query_lower.split() if len(term) > 3 and term in content_lower]
            
            if len(matches) >= 3 or doc.rrf_score > 0.030:
                doc.relevance_grade = "HIGHLY_RELEVANT"
                doc.relevance_explanation = f"Memuat landasan substantif terkait terminologi: {', '.join(matches[:4])}."
                relevant_count += 1
            elif len(matches) >= 1:
                doc.relevance_grade = "PARTIALLY_RELEVANT"
                doc.relevance_explanation = "Memuat konteks pendukung sekunder terhadap kasus regulasi."
                relevant_count += 0.5
            else:
                doc.relevance_grade = "IRRELEVANT"
                doc.relevance_explanation = "Potongan teks tidak memuat keterkaitan langsung dengan isu hukum aktif."

            # Pencatatan aspek yang telah ditemukan buktinya
            if "dpia" in content_lower or "risiko tinggi" in content_lower:
                found_aspects.add("dpia_risk")
            if "hak" in content_lower or "menolak" in content_lower or "human-in-the-loop" in content_lower:
                found_aspects.add("human_in_loop")
            if "sanksi administratif" in content_lower or "denda" in content_lower:
                found_aspects.add("sanctions")
            if "transparansi" in content_lower or "explainability" in content_lower:
                found_aspects.add("explainability")

            graded_docs.append(doc)

        # Identifikasi celah bukti yang belum terpenuhi (Gaps)
        if aspects_to_check["sanctions"] and "sanctions" not in found_aspects:
            gaps.append("Ketentuan sanksi dan denda administratif belum teridentifikasi secara eksak.")
        if aspects_to_check["human_in_loop"] and "human_in_loop" not in found_aspects:
            gaps.append("Mekanisme keberatan nasabah atau intervensi manusia belum tercakup.")
        if aspects_to_check["dpia_risk"] and "dpia_risk" not in found_aspects:
            gaps.append("Kewajiban Penilaian Dampak Pelindungan Data (DPIA) belum diverifikasi.")

        # Perhitungan Skor Kecukupan Bukti
        total_required = max(1, sum(1 for v in aspects_to_check.values() if v))
        satisfied_count = sum(1 for k, v in aspects_to_check.items() if v and k in found_aspects)
        
        base_ratio = satisfied_count / float(total_required)
        relevance_weight = min(1.0, relevant_count / float(len(docs))) if docs else 0.0
        sufficiency_score = round((0.7 * base_ratio) + (0.3 * relevance_weight), 2)

        return graded_docs, sufficiency_score, gaps