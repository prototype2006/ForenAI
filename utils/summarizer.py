print(">>> summarizer.py is being imported")

from transformers import pipeline

print(">>> Creating pipeline...")

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)

print(">>> Pipeline created!")

def generate_summary(text):
    try:
        if not text.strip():
            return "No text available."

        text = text[:3000]

        summary = summarizer(
            text,
            max_length=60,
            min_length=10,
            do_sample=False
        )

        return summary[0]["summary_text"]

    except Exception as e:
        return f"ERROR: {e}"