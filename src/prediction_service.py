import pickle
from pathlib import Path
from typing import Any, Optional, Tuple

import pandas as pd

from src.app_config import MODEL_PATH, VECTORIZER_PATH


def load_model_artifacts(
    model_path: Path = MODEL_PATH,
    vectorizer_path: Optional[Path] = VECTORIZER_PATH,
) -> Tuple[Any, Optional[Any]]:
    if not model_path.exists():
        raise FileNotFoundError(f"Model artifact not found: {model_path}")

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    vectorizer = None
    if vectorizer_path and vectorizer_path.exists():
        with open(vectorizer_path, "rb") as f:
            vectorizer = pickle.load(f)

    return model, vectorizer


def _prediction_input(text: str, vectorizer: Optional[Any] = None):
    if vectorizer is None:
        return [text]
    return vectorizer.transform([text])


def predict_resume_role(text: str, model: Any, vectorizer: Optional[Any] = None) -> dict:
    if not (text or "").strip():
        return {"role": "", "confidence": None, "top_predictions": pd.DataFrame()}

    features = _prediction_input(text, vectorizer)
    role = model.predict(features)[0]
    top_predictions = get_top_predictions(text, model, vectorizer)

    confidence = None
    if not top_predictions.empty:
        confidence = float(top_predictions.iloc[0]["Confidence %"])

    return {"role": role, "confidence": confidence, "top_predictions": top_predictions}


def get_top_predictions(
    text: str,
    model: Any,
    vectorizer: Optional[Any] = None,
    top_n: int = 5,
) -> pd.DataFrame:
    if not hasattr(model, "predict_proba"):
        return pd.DataFrame()

    try:
        features = _prediction_input(text, vectorizer)
        probs = model.predict_proba(features)[0]
        classes = model.classes_ if hasattr(model, "classes_") else model.named_steps["clf"].classes_
    except Exception:
        return pd.DataFrame()

    df = pd.DataFrame({"Role": classes, "Probability": probs})
    df = df.sort_values("Probability", ascending=False).head(top_n)
    df["Confidence %"] = (df["Probability"] * 100).round(2)
    return df[["Role", "Confidence %"]]
