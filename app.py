
import streamlit as st
import os
import re
import hashlib
from datetime import datetime

from utils.text_extractor import extract_text
from utils.forensic_summary import generate_forensic_summary


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="ForenAI | Evidence Command Center",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #0b1120;
        color: #e5edf7;
    }

    [data-testid="stSidebar"] {
        background-color: #101a2b;
        border-right: 1px solid #26354a;
    }

    [data-testid="stHeader"] {
        background-color: rgba(11, 17, 32, 0.9);
    }

    h1, h2, h3 {
        color: #f1f5f9 !important;
        letter-spacing: -0.4px;
    }

    p, li, label {
        color: #cbd5e1;
    }

    .hero {
        padding: 28px;
        border: 1px solid #263b50;
        border-radius: 18px;
        background: linear-gradient(120deg, #14283b, #101827 70%);
        margin-bottom: 22px;
    }

    .eyebrow {
        color: #42d6c3;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .hero-title {
        color: #f8fafc;
        font-size: 38px;
        font-weight: 800;
        margin: 8px 0;
    }

    .hero-description {
        color: #a8b9cc;
        font-size: 15px;
        line-height: 1.6;
    }

    .metric-card {
        background: #121e30;
        border: 1px solid #26364b;
        border-radius: 14px;
        padding: 18px;
        min-height: 112px;
    }

    .metric-label {
        color: #91a4ba;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-value {
        color: #f1f5f9;
        font-size: 25px;
        font-weight: 750;
        margin-top: 8px;
    }

    .section-label {
        color: #42d6c3;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .panel {
        background: #111c2d;
        border: 1px solid #26364b;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .panel-title {
        color: #f1f5f9;
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .muted {
        color: #91a4ba;
        font-size: 13px;
    }

    div[data-testid="stFileUploader"] {
        background: #111c2d;
        border: 1px dashed #3b6477;
        border-radius: 14px;
        padding: 14px;
    }

    div[data-testid="stTextArea"] textarea {
        background-color: #0e1726;
        color: #dbeafe;
        border: 1px solid #304258;
        border-radius: 10px;
        font-family: Consolas, monospace;
    }

    div.stButton > button {
        background: #19b7a5;
        color: #071923;
        border: none;
        border-radius: 9px;
        font-weight: 700;
    }

    div.stButton > button:hover {
        background: #42d6c3;
        color: #071923;
    }

    hr {
        border-color: #26364b;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "processed_evidence" not in st.session_state:
    st.session_state.processed_evidence = {}


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.markdown("## 🔎 FORENAI")
    st.caption("DIGITAL FORENSICS INTELLIGENCE")
    st.divider()

    st.markdown("### Navigation")
    page = st.radio(
        "Workspace",
        [
            "Evidence Dashboard",
            "About ForenAI",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### Processing Pipeline")
    st.markdown("📂 Evidence upload")
    st.markdown("📄 Text extraction + OCR")
    st.markdown("🤖 AI summarization")
    st.markdown("🧾 Structured findings")

    st.divider()

    st.caption("Development prototype")
    st.caption("AI-generated results require human verification.")


# --------------------------------------------------
# ABOUT PAGE
# --------------------------------------------------
if page == "About ForenAI":
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">Project Overview</div>
        <div class="hero-title">About ForenAI</div>
        <div class="hero-description">
            An AI-assisted digital evidence analyzer designed to extract
            document text, summarize content, and organize useful details
            for investigation and review.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Current Capabilities")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">📄 Evidence Processing</div>
            <p>PDF, DOCX, TXT and image uploads.</p>
            <p>Text extraction and OCR for images and scanned PDFs.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">🤖 Text Analysis</div>
            <p>Pretrained DistilBART summarization with a source-sentence fallback.</p>
            <p>Rule-based extraction of identifiers, timestamps and key findings.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Planned Enhancements")

    st.markdown("""
    - Named Entity Recognition (NER)
    - Suspicious keyword detection
    - Investigation timeline generation
    - Investigation report export
    - Case management and evidence integrity tracking
    """)

    st.info(
        "ForenAI is a development prototype. "
        "Planned features are not yet implemented."
    )

    st.stop()


# --------------------------------------------------
# MAIN DASHBOARD HEADER
# --------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="eyebrow">Digital Forensics Intelligence</div>
    <div class="hero-title">Evidence Command Center</div>
    <div class="hero-description">
        Upload digital evidence, extract its contents, and review
        AI-assisted summaries and structured findings in one workspace.
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------
processed_count = len(st.session_state.processed_evidence)

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Evidence Analyzed</div>
        <div class="metric-value">{processed_count}</div>
    </div>
    """, unsafe_allow_html=True)

with metric2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Supported Formats</div>
        <div class="metric-value">06</div>
    </div>
    """, unsafe_allow_html=True)

with metric3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Analysis Engine</div>
        <div class="metric-value" style="font-size:20px;">
            OCR + NLP
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")


# --------------------------------------------------
# CURRENT CAPABILITIES
# --------------------------------------------------
st.markdown('<div class="section-label">Workspace</div>',
            unsafe_allow_html=True)
st.header("Evidence Processing")

feature1, feature2, feature3 = st.columns(3)

with feature1:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">📂 Evidence Intake</div>
        <div class="muted">Upload documents and images for processing.</div>
    </div>
    """, unsafe_allow_html=True)

with feature2:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">🔍 Text Extraction</div>
        <div class="muted">Extract embedded text or recognize scanned text using OCR.</div>
    </div>
    """, unsafe_allow_html=True)

with feature3:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">🧠 AI-Assisted Review</div>
        <div class="muted">Review an overview, identifiers, timestamps and source statements.</div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# EVIDENCE UPLOAD
# --------------------------------------------------
st.divider()

st.markdown('<div class="section-label">Evidence Intake</div>',
            unsafe_allow_html=True)
st.header("Upload Evidence")

st.caption(
    "Supported formats: PDF, DOCX, TXT, PNG, JPG and JPEG. "
    "You can select multiple files."
)

uploaded_files = st.file_uploader(
    "Drop evidence files here or browse your computer",
    type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
    key="evidence_uploader",
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------
# PROCESS EACH FILE INDEPENDENTLY
# --------------------------------------------------
if uploaded_files:
    st.write("")

    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.getvalue()
        original_name = os.path.basename(uploaded_file.name)
        name, extension = os.path.splitext(original_name)

        # Deterministic name based on content to avoid creating
        # another copy on every Streamlit rerun.
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", name).strip("._")
        safe_name = safe_name or "evidence"
        stored_name = f"{safe_name}_{file_hash[:10]}{extension.lower()}"
        file_path = os.path.join(UPLOAD_FOLDER, stored_name)

        # Save only if this exact content is not already present.
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(file_bytes)

        evidence_key = file_hash

        st.markdown(f"""
        <div class="panel">
            <div class="section-label">Evidence Record</div>
            <div class="panel-title">📄 {original_name}</div>
            <div class="muted">
                {extension.upper().replace(".", "")} file
                &nbsp;•&nbsp; {len(file_bytes) / 1024:.2f} KB
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Cache the result in session state so reruns do not
        # repeatedly execute OCR and the AI model for the same file.
        if evidence_key not in st.session_state.processed_evidence:
            try:
                with st.spinner(f"Extracting and analyzing {original_name}..."):
                    extracted_text = extract_text(file_path)

                    if not extracted_text or not extracted_text.strip():
                        st.session_state.processed_evidence[evidence_key] = {
                            "name": original_name,
                            "path": file_path,
                            "size": len(file_bytes),
                            "hash": file_hash,
                            "uploaded_at": datetime.now().strftime(
                                "%d-%m-%Y %H:%M:%S"
                            ),
                            "text": "",
                            "summary": {
                                "overview": "No text could be extracted.",
                                "identifiers": [],
                                "timestamps": [],
                                "findings": [],
                            },
                            "error": None,
                        }
                    else:
                        forensic_summary = generate_forensic_summary(
                            extracted_text
                        )

                        st.session_state.processed_evidence[evidence_key] = {
                            "name": original_name,
                            "path": file_path,
                            "size": len(file_bytes),
                            "hash": file_hash,
                            "uploaded_at": datetime.now().strftime(
                                "%d-%m-%Y %H:%M:%S"
                            ),
                            "text": extracted_text,
                            "summary": forensic_summary,
                            "error": None,
                        }

            except Exception as e:
                st.session_state.processed_evidence[evidence_key] = {
                    "name": original_name,
                    "path": file_path,
                    "size": len(file_bytes),
                    "hash": file_hash,
                    "uploaded_at": datetime.now().strftime(
                        "%d-%m-%Y %H:%M:%S"
                    ),
                    "text": "",
                    "summary": None,
                    "error": str(e),
                }

        record = st.session_state.processed_evidence[evidence_key]

        if record["error"]:
            st.error(f"Processing failed: {record['error']}")
            continue

        if not record["text"]:
            st.warning("No readable text was extracted from this file.")
            continue

        st.success("Evidence processing completed.")

        # --------------------------------------------------
        # FILE DETAILS
        # --------------------------------------------------
        with st.expander("📋 Evidence Metadata", expanded=False):
            detail1, detail2 = st.columns(2)

            with detail1:
                st.write(f"**File name:** {record['name']}")
                st.write(f"**File type:** {extension.upper()}")
                st.write(f"**File size:** {record['size'] / 1024:.2f} KB")

            with detail2:
                st.write(f"**Processed at:** {record['uploaded_at']}")
                st.write("**SHA-256 fingerprint:**")
                st.code(record["hash"], language=None)

            st.caption(
                "The SHA-256 value identifies the uploaded file's content. "
                "It does not, by itself, establish authenticity or chain of custody."
            )

        # --------------------------------------------------
        # ANALYSIS RESULTS
        # --------------------------------------------------
        st.markdown("### 🔎 Analysis Results")

        summary = record["summary"]

        overview_col, identifiers_col, timestamps_col = st.columns(3)

        with overview_col:
            st.markdown("""
            <div class="panel-title">🤖 AI Overview</div>
            """, unsafe_allow_html=True)
            st.write(summary["overview"])

        with identifiers_col:
            st.markdown("""
            <div class="panel-title">🆔 Identifiers</div>
            """, unsafe_allow_html=True)

            if summary["identifiers"]:
                for item in summary["identifiers"]:
                    st.markdown(f"- `{item}`")
            else:
                st.caption("No identifiers detected.")

        with timestamps_col:
            st.markdown("""
            <div class="panel-title">🕒 Timestamps</div>
            """, unsafe_allow_html=True)

            if summary["timestamps"]:
                for item in summary["timestamps"]:
                    st.markdown(f"- {item}")
            else:
                st.caption("No timestamps detected.")

        st.markdown("#### 📌 Key Findings")

        if summary["findings"]:
            for index, finding in enumerate(summary["findings"], start=1):
                st.markdown(f"**{index}.** {finding}")
        else:
            st.info("No matching statements detected.")

        with st.expander("📄 View Complete Extracted Text", expanded=False):
            st.text_area(
                f"Extracted text: {original_name}",
                record["text"],
                height=300,
                key=f"extracted_{evidence_key}",
            )

        st.divider()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("""
<div style="text-align:center; padding:20px 0 10px 0;">
    <div style="color:#42d6c3; font-weight:700; letter-spacing:2px;">
        FORENAI
    </div>
    <div style="color:#91a4ba; font-size:12px; margin-top:6px;">
        AI-ASSISTED DIGITAL EVIDENCE ANALYSIS
    </div>
    <div style="color:#718096; font-size:11px; margin-top:6px;">
        Prototype for investigation support. Verify all results against source evidence.
    </div>
</div>
""", unsafe_allow_html=True)
