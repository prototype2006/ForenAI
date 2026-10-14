
import os
from pathlib import Path

from docx import Document
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from pdf2image import convert_from_path


# ============================================================
# TESSERACT AND POPPLER CONFIGURATION
# ============================================================

TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

POPPLER_PATH = Path(
    r"C:\Users\ADNIM\OneDrive\Documents\Projects"
    r"\ForenAi\Release-26.09.0-0\poppler-26.09.0\Library\bin"
)

# Configure Tesseract if the executable exists.
if TESSERACT_PATH.is_file():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)


# ============================================================
# TXT EXTRACTION
# ============================================================

def extract_txt(file_path):
    """Extract text from a UTF-8 text file."""
    try:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            return file.read()

    except Exception as exc:
        raise RuntimeError(
            f"TXT extraction failed: {exc}"
        ) from exc


# ============================================================
# DOCX EXTRACTION
# ============================================================

def extract_docx(file_path):
    """Extract paragraph text from a Word document."""
    try:
        document = Document(file_path)

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

    except Exception as exc:
        raise RuntimeError(
            f"DOCX extraction failed: {exc}"
        ) from exc


# ============================================================
# IMAGE OCR
# ============================================================

def extract_image(file_path):
    """Extract English text from a supported image."""
    try:
        if not TESSERACT_PATH.is_file():
            raise FileNotFoundError(
                f"Tesseract executable not found: {TESSERACT_PATH}"
            )

        with Image.open(file_path) as image:
            image = image.convert("RGB")

            text = pytesseract.image_to_string(
                image,
                lang="eng",
            )

        return text.strip()

    except Exception as exc:
        raise RuntimeError(
            f"Image OCR failed: {exc}"
        ) from exc


# ============================================================
# SCANNED PDF OCR
# ============================================================

def extract_scanned_pdf(file_path):
    """OCR every page of a scanned PDF."""
    try:
        if not POPPLER_PATH.is_dir():
            raise FileNotFoundError(
                f"Poppler directory not found: {POPPLER_PATH}"
            )

        if not TESSERACT_PATH.is_file():
            raise FileNotFoundError(
                f"Tesseract executable not found: {TESSERACT_PATH}"
            )

        pages = convert_from_path(
            file_path,
            poppler_path=str(POPPLER_PATH),
        )

        extracted_pages = []

        for page_number, page in enumerate(pages, start=1):
            text = pytesseract.image_to_string(
                page,
                lang="eng",
            )

            extracted_pages.append(
                f"[Page {page_number}]\n{text.strip()}"
            )

        return "\n\n".join(extracted_pages).strip()

    except Exception as exc:
        raise RuntimeError(
            f"Scanned PDF OCR failed: {exc}"
        ) from exc


# ============================================================
# PDF EXTRACTION WITH OCR FALLBACK
# ============================================================

def extract_pdf(file_path):
    """
    Extract embedded PDF text first.

    If a page has no embedded text, use OCR for that page.
    Pages with embedded text are not OCRed again.
    """
    try:
        reader = PdfReader(file_path)

        extracted_pages = []
        pages_needing_ocr = []

        for index, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""

            extracted_pages.append(page_text.strip())

            if not page_text.strip():
                pages_needing_ocr.append(index)

        if pages_needing_ocr:
            if not POPPLER_PATH.is_dir():
                raise FileNotFoundError(
                    f"Poppler directory not found: {POPPLER_PATH}"
                )

            if not TESSERACT_PATH.is_file():
                raise FileNotFoundError(
                    f"Tesseract executable not found: {TESSERACT_PATH}"
                )

            ocr_pages = convert_from_path(
                file_path,
                poppler_path=str(POPPLER_PATH),
            )

            for index in pages_needing_ocr:
                if index < len(ocr_pages):
                    ocr_text = pytesseract.image_to_string(
                        ocr_pages[index],
                        lang="eng",
                    ).strip()

                    extracted_pages[index] = ocr_text

        # Preserve page order and make page boundaries clear.
        result_pages = []

        for index, text in enumerate(extracted_pages, start=1):
            if text:
                result_pages.append(
                    f"[Page {index}]\n{text}"
                )

        return "\n\n".join(result_pages).strip()

    except Exception as exc:
        raise RuntimeError(
            f"PDF extraction failed: {exc}"
        ) from exc


# ============================================================
# MASTER DISPATCHER
# ============================================================

def extract_text(file_path):
    """Dispatch supported files to the appropriate extractor."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Evidence file not found: {path}"
        )

    extension = path.suffix.lower()

    if extension == ".txt":
        return extract_txt(path)

    elif extension == ".docx":
        return extract_docx(path)

    elif extension == ".pdf":
        return extract_pdf(path)

    elif extension in {".png", ".jpg", ".jpeg"}:
        return extract_image(path)

    else:
        return "Unsupported file type."
