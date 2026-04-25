from __future__ import annotations
import os
from pathlib import Path
import streamlit as st
from ingestion import IngestionPipeline, RAW_DOCS_DIR
from retriever import RetrievalPipeline

NOT_FOUND_MESSAGE = "Answer not found in uploaded sources"
SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt"}

def ensure_state():
    if "session_id" not in st.session_state: st.session_state.session_id = None
    if "indexed_files" not in st.session_state: st.session_state.indexed_files = {}

@st.cache_resource(show_spinner=False)
def get_ingestion_pipeline(): return IngestionPipeline()

@st.cache_resource(show_spinner=False)
def get_retrieval_pipeline(): return RetrievalPipeline()

def persist_uploaded_file(uploaded_file, session_id):
    session_dir = RAW_DOCS_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    file_path = session_dir / Path(uploaded_file.name).name
    with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
    return file_path

def is_supported(filename):
    return Path(filename).suffix.lower().replace(".", "") in SUPPORTED_EXTENSIONS

def render_sources(result):
    if not result.sources: st.info("No retrieved chunks to display."); return
    st.subheader("Citations")
    for idx, chunk in enumerate(result.sources, start=1):
        page_display = chunk.page_number if chunk.page_number else "N/A"
        st.markdown(f"- Source {idx}: `{chunk.source_file}` | Page: `{page_display}` | Section: `{chunk.section or 'General'}` | Score: `{chunk.similarity_score:.4f}`")
    st.subheader("Retrieved Chunks")
    for idx, chunk in enumerate(result.sources, start=1):
        page_display = chunk.page_number if chunk.page_number else "N/A"
        with st.expander(f"Chunk {idx} - {chunk.source_file} | Page {page_display} | Score {chunk.similarity_score:.4f}"):
            st.write(chunk.text)

def main():
    st.set_page_config(page_title="Market Intelligence RAG", layout="wide")
    st.title("Market Intelligence RAG")
    st.caption("Powered by Groq llama-3.3-70b · Hybrid FAISS + BM25 Retrieval")
    ensure_state()

    with st.sidebar:
        st.header("Session")
        if st.session_state.session_id: st.success(f"Session: {st.session_state.session_id[:16]}...")
        else: st.warning("No active session yet.")

        if st.button("Check Groq Status"):
            pipeline = get_retrieval_pipeline()
            status = pipeline.get_groq_status()
            if status["online"]: st.success(f"✅ Groq online — {status['model']}")
            else: st.error("❌ Groq unreachable — check API key.")

        if st.session_state.indexed_files:
            st.subheader("Indexed Files")
            for name, cnt in st.session_state.indexed_files.items(): st.write(f"- {name}: {cnt} chunks")

        if st.button("Start New Session"):
            ip = get_ingestion_pipeline()
            st.session_state.session_id = ip.generate_session_id()
            st.session_state.indexed_files = {}
            st.success("New session created.")

    st.header("1) Upload and Index Documents")
    uploaded_files = st.file_uploader("Upload PDF, DOCX, or TXT files", type=["pdf", "docx", "txt"], accept_multiple_files=True)

    if st.button("Index Uploaded Documents", disabled=not uploaded_files):
        indexed_now = {}
        try:
            with st.spinner("Indexing documents..."):
                ip = get_ingestion_pipeline()
                if not st.session_state.session_id:
                    st.session_state.session_id = ip.generate_session_id()
                for uf in uploaded_files:
                    if not is_supported(uf.name): st.error(f"Unsupported: {uf.name}"); continue
                    try:
                        fp = persist_uploaded_file(uf, st.session_state.session_id)
                        cnt = ip.ingest(fp, st.session_state.session_id)
                        indexed_now[uf.name] = cnt
                    except Exception as exc: st.error(f"Failed to index {uf.name}: {exc}")
            st.session_state.indexed_files.update(indexed_now)
            if indexed_now:
                st.success("Documents indexed successfully")
                for name, cnt in indexed_now.items(): st.write(f"- {name}: {cnt} chunks")
            else: st.warning("No documents were indexed.")
        except Exception as exc: st.error(f"Indexing failed: {exc}")

    st.header("2) Ask Questions")
    question = st.text_input("Ask a question grounded only in uploaded documents")
    ask_disabled = not question.strip() or not st.session_state.session_id or not bool(st.session_state.indexed_files)

    if st.button("Get Answer", disabled=ask_disabled):
        try:
            rp = get_retrieval_pipeline()
            if not rp.check_session_ready(st.session_state.session_id):
                st.error("No indexed knowledge base found for this session."); return
            with st.spinner("Retrieving and generating answer with Groq llama-3.3-70b..."):
                result = rp.query(question=question.strip(), session_id=st.session_state.session_id)
            if not result.answer_found:
                st.warning(NOT_FOUND_MESSAGE)
            else:
                st.subheader("Answer")
                st.write(result.answer)
                if result.is_grounded: st.success("✅ Answer grounded with document citations.")
                else: st.info("ℹ️ Answer generated from retrieved context.")
            render_sources(result)
        except Exception as exc: st.error(f"Failed to answer question: {exc}")

if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    main()
