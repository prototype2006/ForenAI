import streamlit as st

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="ForenAI",
    page_icon="🕵️",
    layout="wide",
)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.title("🕵️ ForenAI")
st.caption("AI-Powered Digital Evidence Analyzer")

st.divider()

# --------------------------------------------------
# Introduction
# --------------------------------------------------
st.markdown("""
Welcome to **ForenAI**.

This application assists investigators in analyzing digital evidence using Artificial Intelligence.

### Core Features
- 📂 Upload Evidence
- 📄 Extract Text
- 🤖 AI Summarization
- 👤 Named Entity Recognition
- ⚠️ Suspicious Keyword Detection
- 📅 Timeline Generation
- 📊 Investigation Report
""")

st.divider()

# --------------------------------------------------
# Project Status
# --------------------------------------------------
st.subheader("Project Status")

st.progress(10)

st.info("✅ Phase 1: Project Setup Completed")