
from transformers import pipeline

# Load the summarization model once
summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)


def generate_summary(text):
    if not text or not text.strip():
        return "No text available."

    try:
        # Keep the input within a manageable length
        text = text[:3000]

        summary = summarizer(
            text,
            max_length=100,
            min_length=15,
            do_sample=False
        )

        return summary[0]["summary_text"]

    except Exception as e:
        return f"Summary generation failed: {e}"
