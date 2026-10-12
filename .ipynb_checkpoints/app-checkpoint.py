"""
Aplikasi Antarmuka Pengguna Streamlit:
Dasbor Agentic RAG: Navigasi Pengetahuan Multilangkah & Query Rewriting.
© 2026 Muryan Awaludin. Seluruh hak cipta dilindungi undang-undang.
"""
import streamlit as st
import json
from config import CONFIG
from agent.engine import AgenticRAGComplianceEngine

st.set_page_config(
    page_title=CONFIG.APP_TITLE,
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Agentic RAG: Regulatory Compliance & AI Governance")
st.caption("Navigasi Pengetahuan Multilangkah (Multi-Hop Retrieval), Evaluasi Relevansi Kognitif, dan Query Rewriting Otonom")

# Inisialisasi Engine
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = AgenticRAGComplianceEngine()

# Pilihan Pertanyaan Standar Audit Industri
sample_inquiries = [
    "Apakah penggunaan model AI prediktif untuk membatalkan fasilitas kredit nasabah secara otomatis dapat terkena sanksi administratif dan apa syarat legal agar sistem patuh?",
    "Bagaimana kewajiban pelaksanaan Data Protection Impact Assessment (DPIA) pada sistem machine learning dan berapa batas denda jika diabaikan?",
    "Apakah nasabah perbankan berhak mengajukan banding atau menolak keputusan penolakan pinjaman yang murni dihasilkan oleh algoritma komputer?"
]

# Sidebar: Pengaturan dan Masukan Kueri
with st.sidebar:
    st.header("📋 Pengaturan Audit Regulasi")
    st.markdown("Pilih skenario kepatuhan atau masukkan kueri kustom:")
    
    preset_choice = st.selectbox("Contoh Kueri Kepatuhan:", sample_inquiries)
    custom_inquiry = st.text_area("Kueri Audit Aktif:", value=preset_choice, height=120)
    
    btn_run_rag = st.button("🚀 Jalankan Agentic RAG Multi-Hop", type="primary", use_container_width=True)

    st.divider()
    st.markdown(f"**Batas Maksimal Hop:** `{CONFIG.MAX_REASONING_HOPS} Putaran`")
    st.markdown(f"**Ambang Batas Kecukupan:** `{CONFIG.SUFFICIENCY_THRESHOLD * 100}%`")
    st.markdown(f"**Metode Penggabungan:** `Reciprocal Rank Fusion (k={CONFIG.RRF_K_PARAMETER})`")
    
    st.divider()
    st.markdown("© 2026 **Muryan Awaludin**  \nHak Cipta Dilindungi.")

# Area Kerja Utama
col_left, col_right = st.columns([1.1, 0.9])

with col_left:
    st.subheader("🔍 Jejak Penalaran Kognitif & Multi-Hop Trajectory")
    
    if btn_run_rag:
        with st.spinner("Agen sedang menjalankan navigasi berulang, rewriting kueri, dan evaluasi relevansi..."):
            compliance_result = st.session_state.rag_engine.execute_compliance_inquiry(custom_inquiry)
            st.session_state.compliance_result = compliance_result

    if "compliance_result" in st.session_state and st.session_state.compliance_result is not None:
        res = st.session_state.compliance_result
        
        for trace in res.hop_traces:
            with st.expander(f"📍 **Hop {trace.hop_number}: Strategi `{trace.strategy_applied}`**", expanded=True):
                st.markdown(f"**Kueri yang Dieksekusi:** `{trace.query_used}`")
                st.markdown(f"**Skor Kecukupan Bukti:** `{trace.sufficiency_score * 100:.1f}%`")
                
                if trace.detected_gaps:
                    st.warning("**Celah Informasi (Gaps) Terdeteksi:**\n" + "\n".join([f"• {g}" for g in trace.detected_gaps]))
                else:
                    st.success("Seluruh celah pembuktian telah tertutup secara memadai.")

                st.markdown("**Dokumen yang Ditarik & Hasil Penilaian (Grader):**")
                for d in trace.documents_retrieved:
                    with st.container(border=True):
                        st.markdown(f"**[{d.doc_id}] {d.title}** ({d.category})")
                        st.caption(f"Skor RRF: `{d.rrf_score}` | Peringkat Leksikal: `#{d.lexical_rank}` | Peringkat Semantik: `#{d.semantic_rank}`")
                        badge_color = "🟢" if d.relevance_grade == "HIGHLY_RELEVANT" else ("🟡" if d.relevance_grade == "PARTIALLY_RELEVANT" else "🔴")
                        st.markdown(f"{badge_color} **Status:** `{d.relevance_grade}` — *{d.relevance_explanation}*")
                        st.text(f"Isi: {d.content}")
    else:
        st.info("Pilih kueri audit di panel samping lalu klik **'Jalankan Agentic RAG Multi-Hop'** untuk melihat trajektori penalaran agen.")

with col_right:
    st.subheader("📊 Hasil Penasihat Kepatuhan & Sintesis Hukum")
    
    if "compliance_result" in st.session_state and st.session_state.compliance_result is not None:
        res = st.session_state.compliance_result
        
        # Banner Putusan
        if res.compliance_verdict == "NON_COMPLIANT_HIGH_RISK":
            st.error("🚨 **PUTUSAN: NON-COMPLIANT / HIGH RISK EXPOSURE**")
        elif res.compliance_verdict == "COMPLIANT_WITH_CONDITIONS":
            st.warning("⚠️ **PUTUSAN: COMPLIANT WITH STRICT CONDITIONS**")
        else:
            st.info("ℹ️ **PUTUSAN: AUDIT TAMBAHAN DIPERLUKAN**")

        st.metric("Total Iterasi Hop Kognitif", f"{res.total_hops_executed} Putaran")
        st.markdown("**Sitasi Regulasi Terverifikasi:**")
        st.write(", ".join([f"`{cid}`" for cid in res.cited_regulations]))

        st.markdown("### Ringkasan Pendapat Hukum (Legal Advisory)")
        st.info(res.synthesized_advisory)

        st.markdown("### Checklist Mitigasi Kepatuhan Perusahaan")
        for m in res.mitigation_checklist:
            st.markdown(f"- [x] {m}")
    else:
        st.info("Hasil sintesis opini regulasi dan rekomendasi mitigasi akan ditampilkan di sini.")

# Footer Hak Cipta
st.divider()
st.caption(CONFIG.AUTHOR_COPYRIGHT)