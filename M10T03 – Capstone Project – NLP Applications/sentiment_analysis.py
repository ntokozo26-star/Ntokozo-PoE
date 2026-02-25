"""
sentiment_analysis.py — Capstone Project: NLP Applications (Sentiment Analysis)

Introduction (what this script does)
-----------------------------------
This script performs lightweight sentiment analysis on a CSV of product reviews using spaCy
plus the spaCyTextBlob extension. For each review it:
  - computes polarity (negative..positive) and subjectivity (objective..subjective),
  - assigns a label: "positive", "neutral", or "negative" based on simple thresholds,
  - writes a scored CSV and short human-readable artifacts (top examples, a tiny similarity demo),
  - prints a compact summary of results to the terminal.

Why this approach?
------------------
  - Clear, modular functions: easy to read, test, and mark.
  - Defensive setup: helpful install messages if spaCy/model/extensions are missing.
  - Reproducibility: optional sampling knob (fixed random_state) and stable outputs.

How to run (Terminal)
---------------------
1) activate a virtual environment (recommended).
2) Install requirements and language model:
       pip install spacy spacytextblob pandas
       python -m spacy download en_core_web_md
       python -m textblob.download_corpora
3) Run:
       python sentiment_analysis.py
Outputs

  • outputs/sentiment_scored.csv 
  • outputs/example_snippets.txt 
  • outputs/similarity_demo.txt
  • Console printout

"""

from __future__ import annotations
import os, sys
from pathlib import Path
from typing import Tuple, List
import pandas as pd

# Column name that contains free-text reviews.
COL_REVIEW = "reviews.text"

# environment variable for explicitly setting the CSV path.
ENV_DATA_PATH = os.environ.get("AMAZON_REVIEWS_CSV", "")

# If no environment variable is provided, I look for these filenames next to the script.
DEFAULT_CSV_CANDIDATES = [
    "Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products_May19.csv",
    "amazon_reviews.csv",
]


def load_nlp():
    """
    Load spaCy + the 'en_core_web_md' model and add spaCyTextBlob to the pipeline.

    Returns:
        nlp: a configured spaCy Language object with spacytextblob enabled.

    Defensive notes:
        - If spaCy or spacytextblob are missing, I print clear install instructions.
        - 'en_core_web_md' is required here for better embeddings than the small model.
        - TextBlob corpora are fetched for sentiment subjectivity/polarity.
    """
    try:
        import spacy
    except ModuleNotFoundError:
        # Helpful install message if spaCy is not present.
        sys.stderr.write(
            "\n[error] Install spaCy & model:\n"
            "    pip install spacy spacytextblob pandas\n"
            "    python -m spacy download en_core_web_md\n"
            "    python -m textblob.download_corpora\n\n"
        )
        raise

    # Try to load the medium English model.
    try:
        nlp = spacy.load("en_core_web_md")
    except OSError:
        sys.stderr.write("[fatal] Missing model 'en_core_web_md'.\n")
        raise

    # Add spaCyTextBlob to the pipeline for polarity/subjectivity.
    try:
        from spacytextblob.spacytextblob import SpacyTextBlob  
    except ModuleNotFoundError:
        sys.stderr.write("[error] Install spacytextblob + textblob corpora.\n")
        raise

    # Avoid duplicate component if re-running in notebooks.
    if "spacytextblob" not in nlp.pipe_names:
        nlp.add_pipe("spacytextblob")

    return nlp


def resolve_csv_path() -> Path:
    """
    Resolve the reviews CSV location.
    """
    if ENV_DATA_PATH and Path(ENV_DATA_PATH).is_file():
        return Path(ENV_DATA_PATH)

    # Path to this file; I then check for candidate files next to it.
    here = Path(__file__).resolve().parent
    for name in DEFAULT_CSV_CANDIDATES:
        p = here / name
        if p.is_file():
            return p

    # No file found
    raise FileNotFoundError(
        "[fatal] Reviews CSV not found. Set AMAZON_REVIEWS_CSV or place file next to script."
    )


def preprocess_doc(nlp, text: str) -> str:
    """
    Lightweight text cleaning to produce a "cleaned" column for reference.

    Steps:
      - lowercasing & strip whitespace
      - tokenize with spaCy
      - lemmatize terms where available
      - keep alphabetic tokens only
      - drop stop words via spaCy's vocab

    Returns a single, space-joined string of cleaned tokens.
    """
    # Make a Doc cheaply, just to normalize case and spacing.
    doc = nlp.make_doc(str(text).strip().lower())

    # Re-run through pipeline tokenization so I can use lemmas and stopword flags.
    tokens = [t.lemma_ if t.lemma_ else t.text for t in nlp(doc.text)]

    # Keep only alphabetic terms that are not stop words.
    kept = [t for t in tokens if t.isalpha() and not nlp.vocab[t].is_stop]
    return " ".join(kept) if kept else ""


def label_from_polarity(p: float, pos: float = 0.1, neg: float = -0.1) -> str:
    """
    Map a continuous polarity score to a discrete sentiment label.
    """
    if p >= pos:
        return "positive"
    if p <= neg:
        return "negative"
    return "neutral"


def score_review(nlp, text: str) -> tuple[float, float, str]:
    
    # Run sentiment on one review and return (polarity, subjectivity, label).
    
    doc = nlp(text)
    pol = float(doc._.blob.polarity)
    sub = float(doc._.blob.subjectivity)
    return pol, sub, label_from_polarity(pol)


def score_series(nlp, s: pd.Series, sample: int | None = None) -> pd.DataFrame:
    
    # Score a whole Series of reviews.
    
    # Drop missing values and coerce to strings for predictable processing.
    data = s.dropna().astype(str)

    # Optional downsample for quicker runs; uses fixed seed for reproducibility.
    if sample is not None and 0 < sample < len(data):
        data = data.sample(sample, random_state=42)

    # Produce a "cleaned" companion column for inspection
    cleaned = data.apply(lambda x: preprocess_doc(nlp, x))

    # Compute sentiment per row and collect results.
    rows = []
    for raw, clean in zip(data, cleaned):
        pol, sub, lab = score_review(nlp, raw)
        rows.append((raw, clean, pol, sub, lab))

    return pd.DataFrame(rows, columns=["review", "cleaned", "polarity", "subjectivity", "label"])


def quick_summary(df: pd.DataFrame) -> str:
    """
    Create a compact, printable summary for markers:
      -label distribution
      - descriptive stats of polarity
    """
    parts = []
    parts.append("Label counts:\n" + df["label"].value_counts().to_string())
    parts.append("\nPolarity summary:\n" + df["polarity"].describe().to_string())
    return "\n\n".join(parts)


def write_examples(df: pd.DataFrame, path: Path, k: int = 3) -> None:
    # Persist a few example snippets (top positive and top negative by polarity).
    pos = df.sort_values("polarity", ascending=False).head(k)
    neg = df.sort_values("polarity", ascending=True).head(k)

    # Write short bullet points trimmed to 300 chars for readability.
    with open(path, "w", encoding="utf-8") as f:
        f.write("[Top positive examples]\n")
        for r in pos["review"]:
            f.write(f"- {r[:300].strip()}\n\n")
        f.write("\n[Top negative examples]\n")
        for r in neg["review"]:
            f.write(f"- {r[:300].strip()}\n\n")


def similarity_demo(nlp, reviews: list[str], out_path: Path) -> None:
    """
    Tiny semantic similarity demo using the first two reviews (if available).
    This showcases spaCy's Doc.similarity (driven by word vectors in 'md').
    """
    if len(reviews) < 2:
        return
    doc1, doc2 = nlp(reviews[0]), nlp(reviews[1])
    sim = doc1.similarity(doc2)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"Similarity between first two reviews: {sim:.4f}\n")


def main():
    #  Output directory for all artifacts.
    OUT_DIR = Path("outputs")
    OUT_DIR.mkdir(exist_ok=True, parents=True)

    #  Load CSV path, with clear setup guidance on failure.
    csv_path = resolve_csv_path()
    print(f"[info] Loading: {csv_path}")

    #  Read CSV and check that the expected text column exists.
    df = pd.read_csv(csv_path)
    if COL_REVIEW not in df.columns:
        raise KeyError(f"Expected column '{COL_REVIEW}' not found.")

    # Build NLP pipeline (spaCy + spaCyTextBlob).
    nlp = load_nlp()

    # Select the text column and drop missing values for clean processing.
    reviews = df[COL_REVIEW].dropna()
    print(f"[info] Non-null reviews: {len(reviews)}")

    # Score reviews → DataFrame with sentiment fields.
    scored = score_series(nlp, reviews, sample=None)

    # Persist the scored table to CSV for downstream analysis.
    out_csv = OUT_DIR / "sentiment_scored.csv"
    scored.to_csv(out_csv, index=False)
    print(f"[info] Saved: {out_csv}")

    # Print a compact summary (friendly for markers).
    print("\n" + quick_summary(scored) + "\n")

    # Save example snippets for qualitative inspection.
    examples_path = OUT_DIR / "example_snippets.txt"
    write_examples(scored, examples_path, k=3)
    print(f"[info] Saved examples: {examples_path}")

    # Save a tiny semantic similarity demo to show vector usage.
    sim_path = OUT_DIR / "similarity_demo.txt"
    similarity_demo(nlp, scored['review'].tolist(), sim_path)
    print(f"[info] Saved similarity demo: {sim_path}")


if __name__ == "__main__":
    main()
