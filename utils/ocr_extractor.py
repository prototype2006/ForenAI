
from PIL import Image
import pytesseract

# Tell Python where the Tesseract engine is installed
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def extract_text_from_image(file_path):
    try:
        with Image.open(file_path) as image:
            text = pytesseract.image_to_string(image, lang="eng")
        return text.strip()

    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}") from e
