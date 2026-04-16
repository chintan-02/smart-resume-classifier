
import json
import pickle
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "resume_dataset.csv"
ARTIFACT_DIR = BASE_DIR / "artifacts"

def main():
    df = pd.read_csv(DATA_PATH)
    if {"resume_text", "job_role"} - set(df.columns):
        raise ValueError("Dataset must contain 'resume_text' and 'job_role' columns.")

    X_train, X_test, y_train, y_test = train_test_split(
        df["resume_text"], df["job_role"], test_size=0.2, random_state=42, stratify=df["job_role"]
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=5000)),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    ARTIFACT_DIR.mkdir(exist_ok=True)
    with open(ARTIFACT_DIR / "resume_classifier.pkl", "wb") as f:
        pickle.dump(model, f)

    metrics = {
        "accuracy": float(accuracy_score(y_test, preds)),
        "report": classification_report(y_test, preds, output_dict=True)
    }
    with open(ARTIFACT_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("Training complete.")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print("Saved model to artifacts/resume_classifier.pkl")

if __name__ == "__main__":
    main()
