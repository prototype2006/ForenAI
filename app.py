 
import hashlib
import html
import os
import re
from datetime import datetime
from pathlib import Path

import streamlit as st

from utils.forensic_summary import generate_forensic_summary
from utils.text_extractor import extract_text


# ============================================================
# FORENAI | PROFESSIONAL DIGITAL FORENSICS WORKSPACE
# ============================================================

st.set_page_config(
    page_title="ForenAI | Digital Evidence Intelligence",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = APP_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

SUPPORTED_TYPES = ["pdf", "docx", "txt", "png", "jpg", "jpeg"]


# ============================================================
# DESIGN SYSTEM
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --bg: #0B1120;
        --sidebar: #0E1728;
        --surface: #121D2E;
        --surface-raised: #18263A;
        --border: #29394F;
        --text: #F1F5F9;
        --muted: #94A3B8;
        --blue: #60A5FA;
        --cyan: #38BDF8;
        --green: #34D399;
        --amber: #FBBF24;
        --red: #F87171;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
        font-family: "Segoe UI", sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 17, 32, 0.96);
    }

    [data-testid="stSidebar"] {
        background: var(--sidebar);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] > div {
        padding-top: 1.4rem;
    }

    .block-container {
        max-width: 1450px;
        padding: 2rem 2.3rem 3rem;
    }

    h1, h2, h3, h4 {
        color: var(--text) !important;
        letter-spacing: -0.025em;
    }

    h1 {
        font-size: 2rem !important;
        font-weight: 750 !important;
    }

    h2 {
        font-size: 1.45rem !important;
        font-weight: 700 !important;
    }

    h3 {
        font-size: 1.05rem !important;
        font-weight: 650 !important;
    }

    p, li, label {
        color: #D5DFEC;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    hr {
        border-color: var(--border);
    }

    /* Sidebar branding */

    .brand-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 5px 0 18px;
    }

    .brand-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 43px;
        height: 43px;
        border: 1px solid #315274;
        border-radius: 11px;
        background: #162B45;
        color: var(--cyan);
        font-size: 21px;
        font-weight: 800;
    }

    .brand-name {
        font-size: 20px;
        font-weight: 800;
        letter-spacing: 0.04em;
        color: var(--text);
    }

    .brand-subtitle {
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.13em;
        color: var(--muted);
        margin-top: 3px;
    }

    /* Page heading */

    .eyebrow {
        color: var(--cyan);
        font-size: 10px;
        font-weight: 750;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .page-title {
        color: var(--text);
        font-size: clamp(27px, 3vw, 37px);
        line-height: 1.2;
        font-weight: 780;
        letter-spacing: -0.04em;
        margin-bottom: 10px;
    }

    .page-description {
        max-width: 820px;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.75;
    }

    .top-divider {
        height: 1px;
        background: var(--border);
        margin: 23px 0 27px;
    }

    .section-label {
        color: var(--cyan);
        font-size: 10px;
        font-weight: 750;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    /* Metric cards */

    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 18px 19px;
        min-height: 118px;
        transition: border-color 0.2s ease;
    }

    .metric-card:hover {
        border-color: #46658A;
    }

    .metric-label {
        color: var(--muted);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .metric-value {
        color: var(--text);
        font-size: 28px;
        font-weight: 760;
        margin-top: 12px;
        line-height: 1.15;
        overflow-wrap: anywhere;
    }

    .metric-note {
        color: var(--muted);
        font-size: 11px;
        margin-top: 7px;
    }

    /* Content cards */

    .panel {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 19px;
        margin-bottom: 12px;
        height: 100%;
    }

    .panel-title {
        color: var(--text);
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .panel-description {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.75;
    }

    .empty-state {
        border: 1px dashed #3A506B;
        background: rgba(18, 29, 46, 0.65);
        border-radius: 12px;
        padding: 30px 20px;
        text-align: center;
        margin: 12px 0;
    }

    .empty-title {
        color: var(--text);
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .empty-description {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.7;
    }

    .status-pill {
        display: inline-block;
        padding: 4px 9px;
        border-radius: 20px;
        background: #12372F;
        border: 1px solid #1C5D4D;
        color: var(--green);
        font-size: 10px;
        font-weight: 700;
    }

    .finding-card {
        background: #101B2B;
        border: 1px solid var(--border);
        border-left: 3px solid var(--blue);
        border-radius: 8px;
        padding: 13px 15px;
        margin: 9px 0;
        color: #DCE6F2;
        font-size: 13px;
        line-height: 1.7;
        overflow-wrap: anywhere;
    }

    /* Controls */

    .stButton > button,
    .stDownloadButton > button {
        min-height: 40px;
        background: #1B3A5D;
        color: #F8FAFC;
        border: 1px solid #35577B;
        border-radius: 8px;
        font-weight: 650;
        transition: all 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #234A73;
        border-color: var(--blue);
        color: white;
    }

    [data-testid="stFileUploader"] {
        background: var(--surface);
        border: 1px dashed #3A536F;
        border-radius: 12px;
        padding: 14px;
    }

    [data-testid="stTextArea"] textarea,
    [data-testid="stTextInput"] input {
        background: #0D1727 !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    [data-baseweb="select"] > div {
        background: var(--surface) !important;
        border-color: var(--border) !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 9px;
        overflow: hidden;
    }

    [data-testid="stExpander"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 9px;
    }

    [data-testid="stAlert"] {
        border-radius: 9px;
    }

    /* Footer */

    .app-footer {
        color: #718198;
        font-size: 10px;
        letter-spacing: 0.08em;
        line-height: 1.8;
        border-top: 1px solid var(--border);
        padding-top: 18px;
        margin-top: 35px;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1.2rem 1rem 2rem;
        }

        .metric-card {
            padding: 14px;
            min-height: 105px;
        }

        .metric-value {
            font-size: 23px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "processed_evidence" not in st.session_state:
    st.session_state.processed_evidence = {}

if "active_evidence" not in st.session_state:
    st.session_state.active_evidence = None

if "workspace_page" not in st.session_state:
    st.session_state.workspace_page = "Overview"

records = st.session_state.processed_evidence


# ============================================================
# REUSABLE UI FUNCTIONS
# ============================================================

def page_header(kicker, title, description):
    st.markdown(
        f"""
        <div class="eyebrow">{html.escape(kicker)}</div>
        <div class="page-title">{html.escape(title)}</div>
        <div class="page-description">
            {html.escape(description)}
        </div>
        <div class="top-divider"></div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, detail=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="metric-note">{html.escape(str(detail))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel(title, description):
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">{html.escape(title)}</div>
            <div class="panel-description">
                {html.escape(description)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(title, description):
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-title">{html.escape(title)}</div>
            <div class="empty-description">
                {html.escape(description)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text):
    st.markdown(
        f'<div class="section-label">{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def navigate_to(page_name):
    st.session_state.navigation_target = page_name


# ============================================================
# EVIDENCE PROCESSING
# ============================================================

def process_upload(uploaded_file):
    content = uploaded_file.getvalue()
    original_name = os.path.basename(uploaded_file.name)
    extension = Path(original_name).suffix.lower()
    digest = hashlib.sha256(content).hexdigest()

    safe_stem = re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        Path(original_name).stem,
    ).strip("._") or "evidence"

    stored_name = f"{safe_stem}_{digest[:12]}{extension}"
    destination = UPLOAD_DIR / stored_name

    # Reuse an existing record for identical file contents.
    if digest in records:
        return digest

    if not destination.exists():
        destination.write_bytes(content)

    record = {
        "name": original_name,
        "stored_name": stored_name,
        "path": str(destination),
        "size": len(content),
        "hash": digest,
        "uploaded_at": datetime.now().astimezone().strftime(
            "%Y-%m-%d %H:%M:%S %Z"
        ),
        "status": "Processing",
        "text": "",
        "summary": None,
        "error": None,
        "file_type": extension.lstrip(".").upper(),
    }

    records[digest] = record

    try:
        with st.spinner(f"Processing {original_name}..."):
            extracted = extract_text(str(destination))

            if (
                extracted
                and extracted.strip()
                and extracted.strip() != "Unsupported file type."
            ):
                record["text"] = extracted.strip()
                record["summary"] = generate_forensic_summary(
                    record["text"]
                )
                record["status"] = "Processed"
            else:
                record["status"] = "No text"
                record["error"] = (
                    "No readable text was extracted from this file."
                )

    except Exception as exc:
        record["status"] = "Error"
        record["error"] = f"{type(exc).__name__}: {exc}"

    records[digest] = record
    return digest


def evidence_table():
    if not records:
        empty_state(
            "No evidence records yet",
            "Upload a supported file in Evidence Workspace to begin.",
        )
        return

    rows = []

    for rec in reversed(list(records.values())):
        rows.append({
            "Evidence": rec["name"],
            "Type": rec["file_type"],
            "Size (KB)": round(rec["size"] / 1024, 2),
            "Status": rec["status"],
            "Added": rec["uploaded_at"],
            "SHA-256": rec["hash"][:16] + "...",
        })

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


def evidence_choices():
    return {
        f'{rec["name"]} · {digest[:8]}': digest
        for digest, rec in records.items()
    }


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand-row">
            <div class="brand-icon">F</div>
            <div>
                <div class="brand-name">ForenAI</div>
                <div class="brand-subtitle">
                    Digital Evidence Intelligence
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("**WORKSPACE**")

    pages = [
        "Overview",
        "Evidence Workspace",
        "Text Extraction",
        "AI Analysis",
        "Entities",
        "Timeline",
        "Reports",
        "Settings",
    ]

    if "navigation_target" in st.session_state:
        st.session_state.workspace_page = (
        st.session_state.pop("navigation_target")
        )

    st.radio(
    "Navigation",
    pages,
    key="workspace_page",
    label_visibility="collapsed",
    )

    st.divider()

    st.markdown("**PROCESSING PIPELINE**")

    for step in [
        "01  Evidence intake",
        "02  Text extraction / OCR",
        "03  AI-assisted summary",
        "04  Rule-based indicators",
    ]:
        st.caption(step)

    st.divider()

    st.markdown(
        '<span class="status-pill">PROTOTYPE</span>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Use authorized evidence only. "
        "Verify all findings against original source material."
    )


page = st.session_state.workspace_page


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    page_header(
        "Digital Forensics / Workspace",
        "Evidence Command Center",
        (
            "Centralize digital evidence, extract document contents, "
            "and review AI-assisted summaries and structured indicators "
            "in one focused workspace."
        ),
    )

    total = len(records)
    processed = sum(
        rec["status"] == "Processed"
        for rec in records.values()
    )
    errors = sum(
        rec["status"] == "Error"
        for rec in records.values()
    )
    extracted_chars = sum(
        len(rec["text"])
        for rec in records.values()
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Evidence records",
            total,
            "Unique file contents in this session",
        )

    with c2:
        metric_card(
            "Processed",
            processed,
            "Files with extracted text and analysis",
        )

    with c3:
        metric_card(
            "Processing errors",
            errors,
            "Records requiring attention",
        )

    with c4:
        metric_card(
            "Characters extracted",
            f"{extracted_chars:,}",
            "Across available evidence text",
        )

    st.write("")

    section_label("WORKSPACE")
    st.subheader("Continue your investigation")

    a, b, c = st.columns(3)

    with a:
        panel(
            "Evidence intake",
            "Upload documents and images, inspect metadata, and review SHA-256 fingerprints.",
        )
        if st.button(
            "Open evidence workspace",
            use_container_width=True,
        ):
            navigate_to("Evidence Workspace")
            st.rerun()

    with b:
        panel(
            "Text extraction",
            "Inspect extracted source text separately from AI-generated interpretations.",
        )
        if st.button(
            "Review extracted text",
            use_container_width=True,
        ):
            navigate_to("Text Extraction")
            st.rerun()

    with c:
        panel(
            "AI-assisted analysis",
            "Review summaries, pattern-matched identifiers, timestamps, and candidate findings.",
        )
        if st.button(
            "Open AI analysis",
            use_container_width=True,
        ):
            navigate_to("AI Analysis")
            st.rerun()

    st.write("")
    section_label("RECENT EVIDENCE")
    st.subheader("Evidence register")

    evidence_table()

    if not records:
        empty_state(
            "Ready for your first file",
            (
                "Open Evidence Workspace to upload a PDF, DOCX, TXT, "
                "PNG, JPG, or JPEG file."
            ),
        )

    st.info(
        "Named Entity Recognition, a validated event timeline, "
        "and formal investigation-report export are not implemented yet."
    )


# ============================================================
# EVIDENCE WORKSPACE
# ============================================================

elif page == "Evidence Workspace":

    page_header(
        "Evidence Intake / Integrity",
        "Evidence Workspace",
        (
            "Add files, review processing status, and inspect file "
            "fingerprints. Files are processed individually."
        ),
    )

    section_label("ADD EVIDENCE")

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Evidence intake</div>
            <div class="panel-description">
                Supported formats: PDF, DOCX, TXT, PNG, JPG and JPEG.
                Upload only material you are authorized to analyze.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploads = st.file_uploader(
        "Choose evidence files",
        type=SUPPORTED_TYPES,
        accept_multiple_files=True,
        key="workspace_uploader",
    )

    if uploads:
        for uploaded_file in uploads:
            digest = process_upload(uploaded_file)
            rec = records[digest]

            if rec["status"] == "Processed":
                st.success(
                    f'{rec["name"]}: extraction and analysis completed.'
                )
            elif rec["status"] == "No text":
                st.warning(
                    f'{rec["name"]}: {rec["error"]}'
                )
            else:
                st.error(
                    f'{rec["name"]}: {rec["error"]}'
                )

    st.write("")
    section_label("EVIDENCE REGISTER")
    evidence_table()

    if records:
        choices = evidence_choices()

        selected = st.selectbox(
            "Select an evidence record",
            list(choices.keys()),
            key="evidence_select",
        )

        digest = choices[selected]
        rec = records[digest]

        with st.expander("Evidence metadata and integrity", expanded=True):
            left, right = st.columns(2)

            with left:
                st.markdown("**File name**")
                st.write(rec["name"])

                st.markdown("**File type**")
                st.write(rec["file_type"])

                st.markdown("**File size**")
                st.write(f'{rec["size"]:,} bytes')

            with right:
                st.markdown("**Processing status**")
                st.write(rec["status"])

                st.markdown("**Added to session**")
                st.write(rec["uploaded_at"])

                st.markdown("**SHA-256 fingerprint**")
                st.code(rec["hash"], language=None)

            st.caption(
                "A SHA-256 fingerprint can help identify a file version "
                "when compared with a trusted value. It does not by itself "
                "prove authenticity or establish chain of custody."
            )

            if st.button(
                "Set as active evidence",
                key="set_active_evidence",
            ):
                st.session_state.active_evidence = digest
                st.success("Active evidence selected for this session.")

        if rec["error"]:
            st.warning(rec["error"])

else:
    pass


# ============================================================
# TEXT EXTRACTION
# ============================================================

if page == "Text Extraction":

    page_header(
        "Extraction Workspace",
        "Source Text Review",
        (
            "Inspect extracted content separately from AI interpretation. "
            "Scanned PDFs and images require working OCR dependencies."
        ),
    )

    if not records:
        empty_state(
            "No evidence available",
            "Upload evidence in Evidence Workspace to inspect extracted text.",
        )

    else:
        choices = evidence_choices()
        values = list(choices.values())

        active = st.session_state.active_evidence
        default_index = values.index(active) if active in values else 0

        selected = st.selectbox(
            "Evidence record",
            list(choices.keys()),
            index=default_index,
            key="text_record",
        )

        digest = choices[selected]
        rec = records[digest]

        st.caption(
            f'{rec["file_type"]}  /  {rec["size"]:,} bytes  /  '
            f'Status: {rec["status"]}'
        )

        if rec["error"] and not rec["text"]:
            st.warning(rec["error"])

        if rec["text"]:
            section_label("SOURCE DOCUMENT")
            st.subheader("Extracted content")

            query = st.text_input(
                "Find within text",
                placeholder="Enter a word, email, ID, or phrase...",
                key="source_search",
            )

            if query:
                matches = len(
                    re.findall(
                        re.escape(query),
                        rec["text"],
                        flags=re.IGNORECASE,
                    )
                )
                st.caption(
                    f"{matches} matching occurrence(s) found."
                )

            st.text_area(
                "Extracted source text",
                value=rec["text"],
                height=450,
                key=f"text_view_{digest}",
            )

            st.download_button(
                "Download extracted text",
                data=rec["text"].encode("utf-8"),
                file_name=(
                    f'{Path(rec["name"]).stem}_extracted.txt'
                ),
                mime="text/plain",
                key=f"download_text_{digest}",
            )

        else:
            empty_state(
                "No extracted text",
                "This record does not currently have readable extracted text.",
            )


# ============================================================
# AI ANALYSIS
# ============================================================

elif page == "AI Analysis":

    page_header(
        "Analytical Review",
        "AI-Assisted Analysis",
        (
            "Review model-generated summaries and rule-based indicators. "
            "These outputs are investigative leads, not verified facts."
        ),
    )

    if not records:
        empty_state(
            "No evidence to analyze",
            "Upload a file in Evidence Workspace to generate analysis results.",
        )

    else:
        choices = evidence_choices()

        selected = st.selectbox(
            "Evidence record",
            list(choices.keys()),
            key="analysis_record",
        )

        digest = choices[selected]
        rec = records[digest]

        if rec["status"] != "Processed" or not rec["summary"]:
            st.warning(
                rec["error"]
                or "No analysis results are available for this record."
            )

        else:
            summary = rec["summary"]

            section_label("AI-GENERATED INTERPRETATION")
            st.subheader("Evidence overview")

            st.markdown(
                '<div class="panel">'
                '<div class="panel-title">Summary</div>'
                '<div class="panel-description">'
                'Generated from the extracted source text.'
                '</div></div>',
                unsafe_allow_html=True,
            )

            st.write(summary.get("overview", "No overview available."))

            st.caption(
                "AI summaries can omit context or misinterpret details. "
                "Compare the output with the original evidence."
            )

            st.download_button(
                "Download AI overview",
                data=summary.get("overview", "").encode("utf-8"),
                file_name=f'{Path(rec["name"]).stem}_overview.txt',
                mime="text/plain",
                key=f"download_overview_{digest}",
            )

            st.write("")
            left, right = st.columns(2)

            with left:
                section_label("PATTERN-BASED IDENTIFIERS")
                st.subheader("Detected identifiers")

                identifiers = summary.get("identifiers", [])

                if identifiers:
                    for item in identifiers:
                        st.code(str(item), language=None)
                else:
                    st.caption("No matching identifiers detected.")

            with right:
                section_label("DETECTED TIMESTAMPS")
                st.subheader("Timestamp references")

                timestamps = summary.get("timestamps", [])

                if timestamps:
                    for item in timestamps:
                        st.markdown(
                            f"- {html.escape(str(item))}"
                        )
                else:
                    st.caption("No matching timestamps detected.")

            st.write("")
            section_label("KEYWORD-BASED INDICATORS")
            st.subheader("Candidate source statements")

            findings = summary.get("findings", [])

            if findings:
                for index, item in enumerate(findings, start=1):
                    st.markdown(
                        f"""
                        <div class="finding-card">
                            <strong>Candidate {index:02d}</strong><br>
                            {html.escape(str(item))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption(
                    "No statements matched the current keyword rules."
                )

            st.caption(
                "Candidate statements are not verified conclusions. "
                "Timestamps have not been linked into a validated timeline."
            )

            with st.expander("Model and methodology"):
                st.write(
                    "Summary model: sshleifer/distilbart-cnn-12-6."
                )
                st.write(
                    "Identifiers and timestamps are extracted using "
                    "pattern-based rules."
                )
                st.write(
                    "Candidate findings are selected using keyword rules."
                )
                st.write(
                    "The prototype does not validate allegations, "
                    "determine intent, or prove evidence authenticity."
                )

            with st.expander("View original extracted text"):
                st.text_area(
                    "Source text",
                    value=rec["text"],
                    height=300,
                    key=f"analysis_source_{digest}",
                )


# ============================================================
# ENTITIES: PLANNED
# ============================================================

elif page == "Entities":

    page_header(
        "Feature Status",
        "Named Entities",
        "Named Entity Recognition is not implemented in this version.",
    )

    st.info(
        "This feature is planned and does not currently generate entities."
    )

    panel(
        "Planned implementation",
        (
            "Add a suitable NER model, entity categories, references to "
            "source text, and human review of extracted names and organizations."
        ),
    )


# ============================================================
# TIMELINE: PLANNED
# ============================================================

elif page == "Timeline":

    page_header(
        "Feature Status",
        "Event Timeline",
        "A validated event-linked timeline is not implemented yet.",
    )

    st.info(
        "ForenAI can detect timestamp patterns, but it does not yet "
        "associate those timestamps with validated events."
    )

    panel(
        "Planned implementation",
        (
            "Associate events with source passages, preserve original "
            "timestamps, handle time zones when known, and flag ambiguous "
            "dates for human review."
        ),
    )


# ============================================================
# REPORTS: PLANNED
# ============================================================

elif page == "Reports":

    page_header(
        "Feature Status",
        "Investigation Reports",
        "Formal investigation-report export is not implemented yet.",
    )

    st.info(
        "Extracted text and AI overviews can currently be downloaded "
        "from their respective workspaces."
    )

    panel(
        "Planned report structure",
        (
            "Evidence metadata, SHA-256 fingerprints, extraction methods, "
            "source-linked findings, timestamps, limitations, and analyst "
            "verification fields."
        ),
    )


# ============================================================
# SETTINGS
# ============================================================

elif page == "Settings":

    page_header(
        "Configuration",
        "Workspace Settings",
        "Review supported formats, processing components, and data handling.",
    )

    panel(
        "Supported input formats",
        "PDF, DOCX, TXT, PNG, JPG and JPEG.",
    )

    panel(
        "Processing components",
        (
            "Streamlit interface, PyPDF2, python-docx, Pillow, Tesseract OCR, "
            "Hugging Face Transformers, and rule-based indicator extraction."
        ),
    )

    panel(
        "Data handling",
        (
            "Uploaded files are stored locally in the uploads directory. "
            "Processed metadata is kept in Streamlit session state and is "
            "not a persistent case database."
        ),
    )

    st.warning(
        "Do not use real sensitive evidence in an unsecured development environment."
    )

    st.write("")

    if st.button(
        "Clear session evidence records",
        type="secondary",
    ):
        st.session_state.processed_evidence = {}
        st.session_state.active_evidence = None
        st.rerun()

    st.caption(
        "Clearing the session register does not delete files from the "
        "uploads directory. Review stored files separately when appropriate."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="app-footer">
        FORENAI &nbsp; / &nbsp;
        AI-ASSISTED DIGITAL EVIDENCE REVIEW<br>
        PROTOTYPE &nbsp; · &nbsp;
        VERIFY ALL ANALYTICAL OUTPUT AGAINST SOURCE MATERIAL
    </div>
    """,
    unsafe_allow_html=True,
)
