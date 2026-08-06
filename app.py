import streamlit as st
import os
from datetime import datetime
from utils.text_extractor import extract_text
from utils.summarizer import generate_summary

# --------------------------------------------------
# Page Configuration
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
st.subheader("🚀 Core Features")

st.markdown("""
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

# --------------------------------------------------
# Evidence Upload
# --------------------------------------------------

st.divider()
st.header("📂 Upload Evidence")

uploaded_files = st.file_uploader(
    "Choose evidence files",
    type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)
# --------------------------------------------------
# Create Upload Folder
# --------------------------------------------------

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --------------------------------------------------
# Save Uploaded Files
# --------------------------------------------------
if uploaded_files:

    for uploaded_file in uploaded_files:

        name, extension = os.path.splitext(uploaded_file.name)

        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

        counter = 1

        while os.path.exists(file_path):
            new_filename = f"{name}_{counter}{extension}"
            file_path = os.path.join(UPLOAD_FOLDER, new_filename)
            counter += 1

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ {os.path.basename(file_path)} uploaded successfully!")

        # Everything below is STILL inside the loop
        file_size_kb = uploaded_file.size / 1024

        st.write("### 📋 File Details")
        st.write(f"**File Name:** {os.path.basename(file_path)}")
        st.write(f"**File Type:** {extension.upper()}")
        st.write(f"**File Size:** {file_size_kb:.2f} KB")
        st.write(f"**Uploaded At:** {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        extracted_text = extract_text(file_path)
        st.write("Reached summarizer")

        summary = generate_summary(extracted_text)

        st.write("Summary generated")
        st.subheader("📄 Extracted Text")

        st.text_area(
            "Document Content",
            extracted_text,
            height=300
        )
        st.subheader("🤖 AI Summary")

        st.text_area(
        "Summary",
        summary,
        height=200
        )