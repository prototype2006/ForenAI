
import re

from utils.summarizer import generate_summary


# ============================================================
# IDENTIFIER EXTRACTION
# ============================================================

def extract_identifiers(text):
    """
    Extract case IDs, evidence IDs, incident IDs, reference IDs,
    report IDs, and general alphanumeric identifiers.
    """

    patterns = [
        r"\b(?:Case|Evidence|Incident|Reference|Report)\s+ID\s*[:#-]?\s*[A-Z0-9][A-Z0-9_-]*\b",
        r"\b[A-Z]{1,5}-\d{2,}\b",
    ]

    found = []

    for pattern in patterns:
        found.extend(
            re.findall(pattern, text, re.IGNORECASE)
        )

    # Preserve order while removing duplicates.
    unique = []
    seen = set()

    for item in found:
        item = item.strip()
        key = item.casefold()

        if key not in seen:
            unique.append(item)
            seen.add(key)

    return unique


# ============================================================
# TIMESTAMP EXTRACTION
# ============================================================

def extract_timestamps(text):
    """
    Extract time references and common date formats.
    These are pattern matches, not a validated event timeline.
    """

    patterns = [
        # 11:42 AM, 14:30, 11:42:05 PM IST
        r"\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|IST|UTC)?\b",

        # 15 October 2026, 15 Oct 2026
        r"\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b",

        # 15/10/2026, 15-10-26
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

        # 2026-10-15
        r"\b\d{4}-\d{2}-\d{2}\b",
    ]

    found = []

    for pattern in patterns:
        found.extend(
            re.findall(pattern, text, re.IGNORECASE)
        )

    # Preserve order while removing duplicates.
    unique = []
    seen = set()

    for item in found:
        item = item.strip()

        if item and item not in seen:
            unique.append(item)
            seen.add(item)

    return unique


# ============================================================
# KEY FINDINGS EXTRACTION
# ============================================================

def extract_key_findings(text):
    """
    Identify candidate statements using keywords.

    These statements are not verified facts or conclusions.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        text
    )

    keywords = [
        "transfer",
        "meeting",
        "payment",
        "login",
        "access",
        "sent",
        "received",
        "deleted",
        "password",
        "account",
        "suspect",
        "threat",
        "incident",
        "review",
        "evidence",
        "location",
        "transaction",
        "email",
        "message",
        "dispute",
        "failed",
        "successful",
        "unauthorized",
        "alert",
    ]

    findings = []
    seen = set()

    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence) <= 12:
            continue

        sentence_lower = sentence.casefold()

        if not any(
            keyword in sentence_lower
            for keyword in keywords
        ):
            continue

        key = sentence_lower

        if key not in seen:
            findings.append(sentence)
            seen.add(key)

    return findings[:8]


# ============================================================
# STRUCTURED FORENSIC SUMMARY
# ============================================================

def generate_forensic_summary(text):
    """
    Generate an AI overview and rule-based evidence indicators.

    Returns the same dictionary structure expected by app.py.
    """

    if not text or not text.strip():
        return {
            "overview": "No text available for analysis.",
            "identifiers": [],
            "timestamps": [],
            "findings": [],
        }

    try:
        overview = generate_summary(text)

    except Exception as exc:
        overview = f"AI summary unavailable: {exc}"

    return {
        "overview": overview,
        "identifiers": extract_identifiers(text),
        "timestamps": extract_timestamps(text),
        "findings": extract_key_findings(text),
    }
