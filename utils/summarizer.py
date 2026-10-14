
from transformers import pipeline
import re


# Load the model once, when this module is first imported.
summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)


GENERIC_PHRASES = [
    "this page is an image embedded in a pdf",
    "the image is required to extract the text",
    "this document is a scanned",
    "ocr is required to extract the text",
    "the image is embedded in a pdf",
    "review the attached log before",
    "the image is required",
]


def is_generic_sentence(sentence):
    """Identify OCR boilerplate that should not drive the summary."""
    sentence_lower = sentence.lower()
    return any(
        phrase in sentence_lower
        for phrase in GENERIC_PHRASES
    )


def split_sentences(text):
    """Split extracted text while retaining useful line-based records."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def generate_summary(text):
    if not text or not text.strip():
        return "No text available."

    try:
        original_text = text.strip()
        sentences = split_sentences(original_text)

        # Remove generic OCR instructions.
        useful_sentences = [
            sentence
            for sentence in sentences
            if not is_generic_sentence(sentence)
            and len(sentence) > 5
        ]

        if not useful_sentences:
            return "No useful evidence text found."

        # Prioritize sentences likely to contain evidence details.
        priority_terms = [
            "case id",
            "evidence id",
            "transaction",
            "transfer",
            "location",
            "collection time",
            "observation",
            "timestamp",
            "amount",
            "recipient",
            "status",
            "email",
            "message",
            "incident",
        ]

        priority_sentences = [
            sentence
            for sentence in useful_sentences
            if any(
                term in sentence.lower()
                for term in priority_terms
            )
        ]

        # Keep original order and avoid duplicate sentences.
        selected = priority_sentences + [
            sentence
            for sentence in useful_sentences
            if sentence not in priority_sentences
        ]

        model_input = " ".join(selected)[:3000]

        # Very short inputs are better returned directly.
        if len(model_input.split()) < 40:
            return " ".join(useful_sentences[:8])

        result = summarizer(
            model_input,
            max_length=100,
            min_length=15,
            do_sample=False,
            truncation=True,
        )[0]["summary_text"].strip()

        # Reject summaries dominated by generic OCR instructions.
        if not result or is_generic_sentence(result):
            return " ".join(useful_sentences[:8])

        return result

    except Exception as exc:
        return f"Summary generation failed: {exc}"
