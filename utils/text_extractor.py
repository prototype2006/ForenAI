
from docx import Document
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import os


# -----------------------------
# Tesseract Configuration
# -----------------------------
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

POPPLER_PATH = (
    r"C:\Users\ADNIM\OneDrive\Documents\Projects"
    r"\ForenAi\Release-26.09.0-0\poppler-26.09.0\Library\bin"
)


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
    return "\n".join(
        paragraph.text for paragraph in document.paragraphs
    )


# -----------------------------
# Image OCR
# -----------------------------
def extract_image(file_path):
    try:
        with Image.open(file_path) as image:
            return pytesseract.image_to_string(
                image, lang="eng"
            ).strip()
    except Exception as e:
        raise RuntimeError(f"Image OCR failed: {e}") from e


# -----------------------------
# Scanned PDF OCR
# -----------------------------
def extract_scanned_pdf(file_path):
    try:
        pages = convert_from_path(
            file_path,
            poppler_path=POPPLER_PATH
        )

        extracted_pages = []

        for page in pages:
            text = pytesseract.image_to_string(
                page, lang="eng"
            )
            extracted_pages.append(text)

        return "\n".join(extracted_pages).strip()

    except Exception as e:
        raise RuntimeError(
            f"Scanned PDF OCR failed: {e}"
        ) from e


# -----------------------------
# PDF Extraction with OCR Fallback
# -----------------------------
def extract_pdf(file_path):
    reader = PdfReader(file_path)
    extracted_pages = []
    needs_ocr = False

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text and page_text.strip():
            extracted_pages.append(page_text)
        else:
            extracted_pages.append("")
            needs_ocr = True

    # If any page lacks text, OCR the PDF and use OCR
    # for the pages where ordinary extraction found none.
    if needs_ocr:
        try:
            ocr_pages = convert_from_path(
                file_path,
                poppler_path=POPPLER_PATH
            )

            for index, page in enumerate(reader.pages):
                if not extracted_pages[index].strip():
                    if index < len(ocr_pages):
                        extracted_pages[index] = (
                            pytesseract.image_to_string(
                                ocr_pages[index], lang="eng"
                            )
                        )
        except Exception as e:
            raise RuntimeError(
                f"PDF OCR fallback failed: {e}"
            ) from e
    
    return "\n".join(extracted_pages).strip()


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

    elif extension in [".png", ".jpg", ".jpeg"]:
        return extract_image(file_path)

    else:
        return "Unsupported file type."
