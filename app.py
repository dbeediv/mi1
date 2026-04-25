from __future__ import annotations
import os
from datetime import datetime
from pathlib import Path
import streamlit as st
from ingestion import IngestionPipeline, RAW_DOCS_DIR
from retriever import RetrievalPipeline

NOT_FOUND_MESSAGE = "Answer not found in uploaded sources"
SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt"}

# ── Custom CSS ─────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}

.stApp {
    background: #0d0f14;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,60,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,90,40,0.06) 0%, transparent 60%);
}

h1, h2, h3, .stApp h1, .stApp h2, .stApp h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em;
}

.stApp header + div h1 {
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #ff8c3c 0%, #ff5a28 60%, #ffb347 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0 !important;
}

.stApp .stCaption p {
    color: #6b6860 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.stApp h2 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #ff8c3c !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    border-bottom: 1px solid rgba(255,140,60,0.2);
    padding-bottom: 0.5rem;
    margin-top: 2rem !important;
}

.stApp h3 {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: #c8c0b4 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

[data-testid="stSidebar"] {
    background: #10131a !important;
    border-right: 1px solid rgba(255,140,60,0.1) !important;
}

[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #ff8c3c !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border-bottom: none;
}

.stButton > button {
    background: linear-gradient(135deg, #ff8c3c, #ff5a28) !important;
    color: #0d0f14 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 12px rgba(255,90,40,0.25) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(255,90,40,0.4) !important;
    background: linear-gradient(135deg, #ffaa5c, #ff7040) !important;
}

.stButton > button:disabled {
    background: #1e2330 !important;
    color: #3d4255 !important;
    box-shadow: none !important;
    transform: none !important;
}

[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: #ff8c3c !important;
    border: 1.5px solid rgba(255,140,60,0.4) !important;
    box-shadow: none !important;
    font-size: 0.75rem !important;
    padding: 0.4rem 1rem !important;
}

[data-testid="stDownloadButton"] > button:hover {
    background: rgba(255,140,60,0.08) !important;
    border-color: #ff8c3c !important;
    color: #ffb347 !important;
    transform: none !important;
    box-shadow: none !important;
}

.stTextInput > div > div > input {
    background: #141720 !important;
    border: 1px solid rgba(255,140,60,0.2) !important;
    border-radius: 8px !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1rem !important;
    transition: border-color 0.2s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: rgba(255,140,60,0.6) !important;
    box-shadow: 0 0 0 3px rgba(255,140,60,0.08) !important;
}

.stTextInput > label {
    color: #6b6860 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

[data-testid="stFileUploader"] {
    background: #141720 !important;
    border: 1.5px dashed rgba(255,140,60,0.25) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    transition: border-color 0.2s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(255,140,60,0.5) !important;
}

[data-testid="stFileUploader"] label {
    color: #6b6860 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.stAlert { border-radius: 8px !important; border: none !important; font-size: 0.88rem !important; }
div[data-baseweb="notification"] { border-radius: 8px !important; }
.stSuccess { background: rgba(60,200,120,0.1) !important; border-left: 3px solid #3cc878 !important; color: #3cc878 !important; }
.stWarning { background: rgba(255,180,50,0.1) !important; border-left: 3px solid #ffb432 !important; color: #ffb432 !important; }
.stError { background: rgba(255,70,70,0.1) !important; border-left: 3px solid #ff4646 !important; color: #ff7070 !important; }
.stInfo { background: rgba(60,130,255,0.08) !important; border-left: 3px solid #3c82ff !important; color: #7ab0ff !important; }

.streamlit-expanderHeader {
    background: #141720 !important;
    border: 1px solid rgba(255,140,60,0.12) !important;
    border-radius: 8px !important;
    color: #c8c0b4 !important;
    font-size: 0.82rem !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: background 0.2s ease;
}

.streamlit-expanderHeader:hover {
    background: #1a1e2a !important;
    border-color: rgba(255,140,60,0.25) !important;
}

.streamlit-expanderContent {
    background: #0f1219 !important;
    border: 1px solid rgba(255,140,60,0.08) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    color: #a09890 !important;
    font-size: 0.88rem !important;
}

.stSpinner > div { border-top-color: #ff8c3c !important; }
.stMarkdown p, .stMarkdown li { color: #a09890 !important; font-size: 0.9rem !important; line-height: 1.7; }

code {
    background: #1a1e2a !important;
    color: #ff8c3c !important;
    border-radius: 4px !important;
    padding: 0.15em 0.4em !important;
    font-size: 0.82em !important;
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #2a2d3a; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #ff8c3c; }

hr { border-color: rgba(255,140,60,0.1) !important; margin: 1.5rem 0 !important; }

.main .block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 960px;
}
</style>
"""


# ── Notes helpers ──────────────────────────────────────────────────────────────

def build_markdown_notes(notes: list[dict]) -> str:
    lines = [
        "# Market Intelligence — Research Notes",
        f"_Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
        "---",
        "",
    ]
    for i, entry in enumerate(notes, start=1):
        lines.append(f"## Note {i}")
        lines.append(f"**🕐 {entry['timestamp']}**")
        lines.append("")
        lines.append("### ❓ Question")
        lines.append(entry["question"])
        lines.append("")
        lines.append("### 💡 Answer")
        lines.append(entry["answer"])
        lines.append("")
        if entry.get("sources"):
            lines.append("### 📎 Sources")
            for src in entry["sources"]:
                lines.append(
                    f"- `{src['file']}` · Page {src['page']} · "
                    f"Section: {src['section']} · Score: {src['score']:.4f}"
                )
            lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def build_txt_notes(notes: list[dict]) -> str:
    lines = [
        "MARKET INTELLIGENCE — RESEARCH NOTES",
        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
        "",
    ]
    for i, entry in enumerate(notes, start=1):
        lines.append(f"NOTE {i}  [{entry['timestamp']}]")
        lines.append("-" * 60)
        lines.append(f"QUESTION:\n{entry['question']}")
        lines.append("")
        lines.append(f"ANSWER:\n{entry['answer']}")
        lines.append("")
        if entry.get("sources"):
            lines.append("SOURCES:")
            for src in entry["sources"]:
                lines.append(
                    f"  - {src['file']} | Page {src['page']} | "
                    f"Section: {src['section']} | Score: {src['score']:.4f}"
                )
            lines.append("")
        lines.append("=" * 60)
        lines.append("")
    return "\n".join(lines)


def build_pdf_notes(notes: list[dict]) -> bytes:
    """Generate a styled PDF of all research notes using fpdf2."""
    from fpdf import FPDF

    # ── Colour helpers ───────────────────────────────────────────────────────
    def hex2rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    BG     = hex2rgb("0d0f14")
    CARD   = hex2rgb("141720")
    BORDER = hex2rgb("2a2d3a")
    ORANGE = hex2rgb("ff8c3c")
    LIGHT  = hex2rgb("e8e4dc")
    MUTED  = hex2rgb("a09890")
    DIM    = hex2rgb("6b6860")

    class NotesPDF(FPDF):
        def header(self):
            # dark background on every page
            self.set_fill_color(*BG)
            self.rect(0, 0, 210, 297, "F")

        def footer(self):
            self.set_y(-12)
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(*DIM)
            self.cell(0, 6, f"Market Intelligence Research Notes  -  Page {self.page_no()}", align="C")

    pdf = NotesPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(20, 18, 20)
    pdf.add_page()

    W = 170  # usable width

    # ── Cover title ──────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*ORANGE)
    pdf.cell(W, 10, "Market Intelligence", ln=True)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(W, 8, "Research Notes", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*DIM)
    n = len(notes)
    pdf.cell(W, 5, f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}  -  {n} note{'s' if n != 1 else ''}", ln=True)
    pdf.ln(3)

    # orange rule
    pdf.set_draw_color(*ORANGE)
    pdf.set_line_width(0.5)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    # ── Notes ────────────────────────────────────────────────────────────────
    for i, entry in enumerate(notes, start=1):

        # Note header bar
        pdf.set_fill_color(*CARD)
        pdf.set_draw_color(*BORDER)
        pdf.set_line_width(0.3)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*ORANGE)
        pdf.cell(W, 7, f"  Note {i}", border=1, fill=True, ln=False)
        pdf.ln(7)

        # Timestamp
        pdf.set_font("Helvetica", "I", 7)
        pdf.set_text_color(*DIM)
        pdf.cell(W, 4, f"  {entry['timestamp']}", ln=True)
        pdf.ln(2)

        # Question label + body
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*LIGHT)
        pdf.cell(W, 5, "QUESTION", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(W, 5, entry["question"])
        pdf.ln(2)

        # Answer label + body
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*LIGHT)
        pdf.cell(W, 5, "ANSWER", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(W, 5, entry["answer"])
        pdf.ln(2)

        # Sources
        if entry.get("sources"):
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*LIGHT)
            pdf.cell(W, 5, "SOURCES", ln=True)
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(*DIM)
            for src in entry["sources"]:
                # FIX: replaced \u2022 bullet (unsupported by Helvetica) with plain ASCII "-"
                line = (f"  -  {src['file']}  |  Page {src['page']}  |  "
                        f"Section: {src['section']}  |  Score: {src['score']:.4f}")
                pdf.multi_cell(W, 4.5, line)
            pdf.ln(1)

        # Divider
        pdf.set_draw_color(*BORDER)
        pdf.set_line_width(0.3)
        pdf.line(20, pdf.get_y() + 2, 190, pdf.get_y() + 2)
        pdf.ln(6)

    return bytes(pdf.output())


def add_to_notes(question: str, answer: str, result) -> None:
    sources = []
    if result.sources:
        for chunk in result.sources:
            sources.append({
                "file": chunk.source_file,
                "page": chunk.page_number if chunk.page_number else "N/A",
                "section": chunk.section or "General",
                "score": chunk.similarity_score,
            })
    st.session_state.notes.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "answer": answer,
        "sources": sources,
    })


# ── App state ──────────────────────────────────────────────────────────────────

def ensure_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "indexed_files" not in st.session_state:
        st.session_state.indexed_files = {}
    if "notes" not in st.session_state:
        st.session_state.notes = []


@st.cache_resource(show_spinner=False)
def get_ingestion_pipeline(): return IngestionPipeline()


@st.cache_resource(show_spinner=False)
def get_retrieval_pipeline(): return RetrievalPipeline()


def persist_uploaded_file(uploaded_file, session_id):
    session_dir = RAW_DOCS_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    file_path = session_dir / Path(uploaded_file.name).name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def is_supported(filename):
    return Path(filename).suffix.lower().replace(".", "") in SUPPORTED_EXTENSIONS


def render_sources(result):
    if not result.sources:
        st.info("No retrieved chunks to display.")
        return
    st.subheader("Citations")
    for idx, chunk in enumerate(result.sources, start=1):
        page_display = chunk.page_number if chunk.page_number else "N/A"
        st.markdown(
            f"- Source {idx}: `{chunk.source_file}` | Page: `{page_display}` "
            f"| Section: `{chunk.section or 'General'}` | Score: `{chunk.similarity_score:.4f}`"
        )
    st.subheader("Retrieved Chunks")
    for idx, chunk in enumerate(result.sources, start=1):
        page_display = chunk.page_number if chunk.page_number else "N/A"
        with st.expander(
            f"Chunk {idx} - {chunk.source_file} | Page {page_display} | Score {chunk.similarity_score:.4f}"
        ):
            st.write(chunk.text)


# ── Voice helper ──────────────────────────────────────────────────────────────

def speak_answer(answer_text: str) -> None:
    """Inject a Web Speech API block that auto-plays the answer and shows a Stop button."""
    # Escape backticks and backslashes so the text is safe inside a JS template literal
    safe = answer_text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    html = f"""
<div id="voice-bar" style="
    display:flex; align-items:center; gap:12px;
    background:#141720; border:1px solid rgba(255,140,60,0.25);
    border-radius:8px; padding:10px 16px; margin:8px 0 4px;
    font-family:'DM Sans',sans-serif;">

  <span id="voice-icon" style="font-size:1.3rem;">🔊</span>

  <span id="voice-status" style="
    color:#ff8c3c; font-size:0.82rem; font-weight:600;
    letter-spacing:0.06em; text-transform:uppercase; flex:1;">
    Speaking answer...
  </span>

  <button id="stop-btn" onclick="stopSpeech()" style="
    background:transparent; color:#ff8c3c;
    border:1.5px solid rgba(255,140,60,0.45);
    border-radius:6px; padding:5px 14px;
    font-family:'DM Sans',sans-serif; font-size:0.78rem;
    font-weight:600; letter-spacing:0.06em;
    text-transform:uppercase; cursor:pointer;
    transition:all .2s ease;">
    Stop
  </button>
</div>

<script>
(function() {{
  // Cancel any previous utterance first
  window.speechSynthesis.cancel();

  const text    = `{safe}`;
  const utter   = new SpeechSynthesisUtterance(text);
  utter.rate    = 1.0;
  utter.pitch   = 1.0;
  utter.volume  = 1.0;

  // Prefer a natural-sounding English voice if available
  function pickVoice() {{
    const voices = window.speechSynthesis.getVoices();
    const preferred = ["Google US English", "Google UK English Female",
                       "Microsoft Aria", "Samantha", "Karen", "Moira"];
    for (const name of preferred) {{
      const v = voices.find(v => v.name === name);
      if (v) return v;
    }}
    return voices.find(v => v.lang.startsWith("en")) || voices[0] || null;
  }}

  function startSpeech() {{
    const voice = pickVoice();
    if (voice) utter.voice = voice;
    window.speechSynthesis.speak(utter);
  }}

  // voices may load async
  if (window.speechSynthesis.getVoices().length === 0) {{
    window.speechSynthesis.onvoiceschanged = startSpeech;
  }} else {{
    startSpeech();
  }}

  utter.onend = function() {{
    const status = document.getElementById("voice-status");
    const icon   = document.getElementById("voice-icon");
    const btn    = document.getElementById("stop-btn");
    if (status) status.textContent = "Done speaking";
    if (icon)   icon.textContent   = "OK";
    if (btn)    btn.style.display  = "none";
  }};

  window.stopSpeech = function() {{
    window.speechSynthesis.cancel();
    const status = document.getElementById("voice-status");
    const icon   = document.getElementById("voice-icon");
    const btn    = document.getElementById("stop-btn");
    if (status) status.textContent = "Stopped";
    if (icon)   icon.textContent   = "X";
    if (btn)    btn.style.display  = "none";
  }};
}})();
</script>
"""
    import streamlit.components.v1 as components
    components.html(html, height=70)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="Market Intelligence RAG", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.title("Market Intelligence RAG")
    st.caption("Powered by Groq llama-3.3-70b · Hybrid FAISS + BM25 Retrieval")
    ensure_state()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Session")
        if st.session_state.session_id:
            st.success(f"Session: {st.session_state.session_id[:16]}...")
        else:
            st.warning("No active session yet.")

        if st.button("Check Groq Status"):
            pipeline = get_retrieval_pipeline()
            status = pipeline.get_groq_status()
            if status["online"]:
                st.success(f"Groq online - {status['model']}")
            else:
                st.error("Groq unreachable - check API key.")

        if st.session_state.indexed_files:
            st.subheader("Indexed Files")
            for name, cnt in st.session_state.indexed_files.items():
                st.write(f"- {name}: {cnt} chunks")

        if st.button("Start New Session"):
            ip = get_ingestion_pipeline()
            st.session_state.session_id = ip.generate_session_id()
            st.session_state.indexed_files = {}
            st.session_state.notes = []
            st.success("New session created.")

        # ── Notes panel ────────────────────────────────────────────────────
        st.markdown("---")
        note_count = len(st.session_state.notes)
        st.subheader(f"Research Notes ({note_count})")

        if note_count == 0:
            st.caption("No notes yet. Answers are saved here automatically.")
        else:
            st.caption(f"{note_count} note{'s' if note_count != 1 else ''} · scroll down to Section 3 to download")

            if st.button("Clear All Notes"):
                st.session_state.notes = []
                st.rerun()

            for i, entry in enumerate(reversed(st.session_state.notes), start=1):
                with st.expander(f"#{note_count - i + 1} · {entry['timestamp']}"):
                    st.markdown(f"**Q:** {entry['question']}")
                    st.markdown(
                        f"**A:** {entry['answer'][:280]}{'...' if len(entry['answer']) > 280 else ''}"
                    )

    # ── Upload & Index ────────────────────────────────────────────────────────
    st.header("1) Upload and Index Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, or TXT files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    if st.button("Index Uploaded Documents", disabled=not uploaded_files):
        indexed_now = {}
        try:
            with st.spinner("Indexing documents..."):
                ip = get_ingestion_pipeline()
                if not st.session_state.session_id:
                    st.session_state.session_id = ip.generate_session_id()
                for uf in uploaded_files:
                    if not is_supported(uf.name):
                        st.error(f"Unsupported: {uf.name}")
                        continue
                    try:
                        fp = persist_uploaded_file(uf, st.session_state.session_id)
                        cnt = ip.ingest(fp, st.session_state.session_id)
                        indexed_now[uf.name] = cnt
                    except Exception as exc:
                        st.error(f"Failed to index {uf.name}: {exc}")
            st.session_state.indexed_files.update(indexed_now)
            if indexed_now:
                st.success("Documents indexed successfully")
                for name, cnt in indexed_now.items():
                    st.write(f"- {name}: {cnt} chunks")
            else:
                st.warning("No documents were indexed.")
        except Exception as exc:
            st.error(f"Indexing failed: {exc}")

    # ── Ask Questions ─────────────────────────────────────────────────────────
    st.header("2) Ask Questions")
    question = st.text_input("Ask a question grounded only in uploaded documents")
    ask_disabled = (
        not question.strip()
        or not st.session_state.session_id
        or not bool(st.session_state.indexed_files)
    )

    if st.button("Get Answer", disabled=ask_disabled):
        try:
            rp = get_retrieval_pipeline()
            if not rp.check_session_ready(st.session_state.session_id):
                st.error("No indexed knowledge base found for this session.")
                return
            with st.spinner("Retrieving and generating answer with Groq llama-3.3-70b..."):
                result = rp.query(
                    question=question.strip(), session_id=st.session_state.session_id
                )
            if not result.answer_found:
                st.warning(NOT_FOUND_MESSAGE)
            else:
                st.subheader("Answer")
                st.write(result.answer)
                speak_answer(result.answer)
                if result.is_grounded:
                    st.success("Answer grounded with document citations.")
                else:
                    st.info("Answer generated from retrieved context.")

                # Auto-save to notes
                add_to_notes(question.strip(), result.answer, result)
                n = len(st.session_state.notes)
                st.success(f"Saved to Research Notes - {n} note{'s' if n != 1 else ''} total. Scroll down to Section 3 to download.")

            render_sources(result)
        except Exception as exc:
            st.error(f"Failed to answer question: {exc}")

    # ── Research Notes (main area) ────────────────────────────────────────────
    if st.session_state.notes:
        st.markdown("---")
        st.header("3) Research Notes")

        note_count = len(st.session_state.notes)
        fname_base = f"notes_{datetime.now().strftime('%Y%m%d_%H%M')}"

        # Download row — always visible when notes exist
        dl_col, spacer = st.columns([2, 6])
        with dl_col:
            st.download_button(
                label="Download Notes as PDF",
                data=build_pdf_notes(st.session_state.notes),
                file_name=f"{fname_base}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        st.caption(f"{note_count} note{'s' if note_count != 1 else ''} captured this session")

        for i, entry in enumerate(st.session_state.notes, start=1):
            label = (
                f"Note {i} · {entry['timestamp']} · "
                f"{entry['question'][:65]}{'...' if len(entry['question']) > 65 else ''}"
            )
            with st.expander(label):
                st.markdown("**Question**")
                st.write(entry["question"])
                st.markdown("**Answer**")
                st.write(entry["answer"])
                if entry["sources"]:
                    st.markdown("**Sources**")
                    for src in entry["sources"]:
                        st.markdown(
                            f"- `{src['file']}` · Page {src['page']} · "
                            f"Section: {src['section']} · Score: `{src['score']:.4f}`"
                        )


if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    main()
