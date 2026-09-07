"""
SIH26100 — Authoritative ML Training Script
-------------------------------------------
Trains a scikit-learn TF-IDF + LogisticRegression pipeline on
petroleum procurement requirement examples for the 10 locked classes.

Authoritative Path:
    ml/scripts/train_requirement_classifier.py

Authoritative Outputs:
    ml/models/requirement_classifier.joblib
"""
import os
import sys
import csv
from collections import Counter

# Ensure project root is on path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ML_DIR = os.path.dirname(_THIS_DIR)
PROJECT_ROOT = os.path.dirname(_ML_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report, accuracy_score

# ── Authoritative Paths ────────────────────────────────────────────────────────
DATA_PATH = os.path.join(_ML_DIR, "datasets", "requirement_dataset.csv")
MODELS_DIR = os.path.join(_ML_DIR, "models")
CLASSIFIER_PATH = os.path.join(MODELS_DIR, "requirement_classifier.joblib")

# The 10 locked requirement classes — DO NOT CHANGE
REQUIREMENT_CLASSES = [
    "GST_TAX_COMPLIANCE",
    "MSME_UDYAM_ELIGIBILITY",
    "FINANCIAL_ELIGIBILITY",
    "EXPERIENCE_ELIGIBILITY",
    "OEM_AUTHORIZATION",
    "BLACKLISTING_DEBARMENT",
    "TECHNICAL_SPECIFICATION",
    "INDUSTRY_STANDARD_COMPLIANCE",
    "SAFETY_REGULATORY_COMPLIANCE",
    "MAKE_IN_INDIA_LOCAL_CONTENT",
]


def load_training_data(csv_path: str):
    texts, labels = [], []
    paths_to_try = [csv_path, os.path.join(PROJECT_ROOT, "data", "requirement_training_data.csv")]
    
    for path in paths_to_try:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row.get("text", "").strip() or row.get("original_text", "").strip()
                label = row.get("label", "").strip() or row.get("category", "").strip()
                status = row.get("review_status", "").upper()
                # If review_status is present, only train on APPROVED or trusted items
                if status and status not in ["APPROVED", "TRUSTED"]:
                    continue
                if text and label in REQUIREMENT_CLASSES:
                    texts.append(text)
                    labels.append(label)
        if len(texts) >= 10:
            break
            
    return texts, labels


def train_classifier(texts, labels):
    """
    Trains TF-IDF + LogisticRegression pipeline.
    Returns the fitted pipeline with calibrated probability output.
    """
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=8000,
            sublinear_tf=True,
            stop_words="english",
            min_df=1,
            analyzer="word"
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=5.0,
            solver="lbfgs",
            class_weight="balanced",
            random_state=42
        )),
    ])
    return pipeline


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    print("=" * 60)
    print("SIH26100 — ML Requirement Classifier Training")
    print("=" * 60)

    # Load data
    print(f"\n[1/5] Loading training data from: {DATA_PATH}")
    texts, labels = load_training_data(DATA_PATH)
    print(f"      Loaded {len(texts)} examples across {len(set(labels))} classes.")

    # Verify all 10 classes present
    missing = set(REQUIREMENT_CLASSES) - set(labels)
    if missing:
        print(f"      WARNING: Missing examples for classes: {missing}")
    else:
        print("      All 10 requirement classes represented in training data.")

    # Class distribution
    print("\n[2/5] Class distribution:")
    dist = Counter(labels)
    for cls in REQUIREMENT_CLASSES:
        print(f"      {cls}: {dist.get(cls, 0)} examples")

    # Train/test split
    print("\n[3/5] Splitting data (80% train / 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.20, random_state=42, stratify=labels
    )

    # Train
    print("\n[4/5] Training TF-IDF + LogisticRegression pipeline...")
    pipeline = train_classifier(texts, labels)
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n      Test accuracy: {acc * 100:.1f}%")
    print("\n      Classification Report:")
    print(classification_report(y_test, y_pred, target_names=sorted(set(labels))))

    # Cross-validation
    print("\n[4b] 5-fold cross-validation on full dataset...")
    cv_scores = cross_val_score(pipeline, texts, labels, cv=5, scoring="accuracy")
    print(f"      CV Accuracy: {cv_scores.mean() * 100:.1f}% (+/- {cv_scores.std() * 100:.1f}%)")

    # Fit on full data and save
    print("\n[5/5] Fitting on full dataset and saving model...")
    pipeline.fit(texts, labels)

    # Save full pipeline (classifier + vectorizer together)
    joblib.dump(pipeline, CLASSIFIER_PATH)
    print(f"      Saved authoritative model: {CLASSIFIER_PATH}")

    # Smoke test
    print("\n--- Smoke Test ---")
    test_cases = [
        ("The bidder shall have valid GST registration.", "GST_TAX_COMPLIANCE"),
        ("Average annual turnover of at least INR 25 crore.", "FINANCIAL_ELIGIBILITY"),
        ("Bidder must have completed natural gas pipeline projects.", "EXPERIENCE_ELIGIBILITY"),
        ("Valve shall conform to API 6D standard.", "INDUSTRY_STANDARD_COMPLIANCE"),
        ("The contractor shall comply with ISO 45001 HSE requirements.", "SAFETY_REGULATORY_COMPLIANCE"),
        ("Submit Manufacturer Authorization Form for line pipe supply.", "OEM_AUTHORIZATION"),
        ("Minimum 50 percent local content Make in India compliance.", "MAKE_IN_INDIA_LOCAL_CONTENT"),
        ("Affidavit confirming non-blacklisting status.", "BLACKLISTING_DEBARMENT"),
        ("Udyam Registration Certificate for MSME bidders.", "MSME_UDYAM_ELIGIBILITY"),
        ("Pipeline wall thickness per ASME B31.8 design standard.", "TECHNICAL_SPECIFICATION"),
    ]

    all_correct = True
    for text, expected in test_cases:
        proba = pipeline.predict_proba([text])[0]
        pred_idx = proba.argmax()
        pred_class = pipeline.classes_[pred_idx]
        confidence = proba[pred_idx]
        status = "OK" if pred_class == expected else "FAIL"
        if pred_class != expected:
            all_correct = False
        print(f"  [{status}] [{confidence:.2f}] {pred_class}  (expected: {expected})")

    print("\n" + "=" * 60)
    if all_correct:
        print("ALL SMOKE TESTS PASSED")
    else:
        print("Some smoke tests failed — review training data coverage.")
    print("=" * 60)
    print("\nTraining complete. Model ready for inference.")
    print(f"  Classifier : {CLASSIFIER_PATH}")


if __name__ == "__main__":
    main()
