
import re
from utils.summarizer import generate_summary


def extract_identifiers(text):
    patterns = [
        r"\b(?:Case|Evidence|Incident|Reference|Report)\s*ID\s*[:#-]?\s*[A-Z0-9-]+\b",
        r"\b[A-Z]{1,5}-\d{2,}\b",
    ]

    found = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text, re.IGNORECASE))

    # Remove duplicates while preserving order
    return list(dict.fromkeys(item.strip() for item in found))


def extract_timestamps(text):
    patterns = [
        r"\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|IST|UTC)?\b",
        r"\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b",
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
    ]

    found = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text, re.IGNORECASE))

    return list(dict.fromkeys(item.strip() for item in found))


def extract_key_findings(text):
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    keywords = [
        "transfer", "meeting", "payment", "login",
        "access", "sent", "received", "deleted",
        "password", "account", "suspect", "threat",
        "incident", "review", "evidence", "location",
    ]

    findings = []

    for sentence in sentences:
        sentence = sentence.strip()

        if (
            sentence
            and len(sentence) > 12
            and any(word in sentence.lower() for word in keywords)
        ):
            if sentence not in findings:
                findings.append(sentence)

    return findings[:8]


def generate_forensic_summary(text):
    if not text or not text.strip():
        return {
            "overview": "No text available for analysis.",
            "identifiers": [],
            "timestamps": [],
            "findings": [],
        }

    try:
        overview = generate_summary(text)
    except Exception as e:
        overview = f"AI summary unavailable: {e}"

    return {
        "overview": overview,
        "identifiers": extract_identifiers(text),
        "timestamps": extract_timestamps(text),
        "findings": extract_key_findings(text),
    }
