from docx import Document
from PyPDF2 import PdfReader
import os


# -----------------------------
# TXT Extraction
# -----------------------------
def extract_txt(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# -----------------------------
# DOCX Extraction
# -----------------------------
def extract_docx(file_path):

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


# -----------------------------
# PDF Extraction
# -----------------------------
def extract_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# -----------------------------
# Master Dispatcher
# -----------------------------
def extract_text(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".txt":
        return extract_txt(file_path)

    elif extension == ".docx":
        return extract_docx(file_path)

    elif extension == ".pdf":
        return extract_pdf(file_path)

    else:
        return "Unsupported file type."