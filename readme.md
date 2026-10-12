# Agentic AI: Autonomous Cognitive Architecture & Multi-Agent Systems

Implementasi praktis modul **Agentic AI** berbasis Python dan Streamlit, memadukan penalaran kognitif multi-langkah (*Multi-Hop Reasoning*), *Query Rewriting*, *Reciprocal Rank Fusion* (RRF), dan tata kelola otonom untuk kebutuhan industri enterprise.

## 🚀 Fitur Utama

- **Autonomous Cognitive Loop**: Siklus *Perceive-Reason-Act* dengan verifikasi status deterministik.
- **Agentic RAG Engine**: *Multi-Hop retrieval* dengan deteksi celah bukti (*information sufficiency grading*).
- **Tool Use & Function Calling**: Integrasi fungsi simbolik deterministik berbasis validasi skema Pydantic.
- **Interactive UI**: Dasbor evaluasi trajektori penalaran transparan berbasis Streamlit.

## 📁 Struktur Direktori

```text
├── data/               # Repositori korpus regulasi & transaksi
├── agent/              # Logika kognitif, retriever, grader, dan skema Pydantic
├── config.py           # Konfigurasi global dan parameter heuristik
├── requirements.txt    # Dependensi pustaka Python
├── app.py              # Antarmuka web interaktif Streamlit
└── .gitignore          # Proteksi berkas sensitif dan cache