PREDICTION_EXPLAINER_DISCLAIMER = (
    "This explanation is based on the current baseline model. It highlights terms that may have "
    "influenced the prediction, but it does not prove correctness and is not a hiring decision."
)


def safe_get(data, key, default=None):
    if not isinstance(data, dict):
        return default
    return data.get(key, default)


def normalize_probability(value, default=0.0) -> float:
    if value is None:
        score = float(default)
    elif isinstance(value, (int, float)):
        score = float(value)
    elif isinstance(value, str):
        cleaned = value.strip().replace("%", "")
        if not cleaned:
            score = float(default)
        else:
            try:
                score = float(cleaned)
            except ValueError:
                score = float(default)
    else:
        score = float(default)

    if 0 < score <= 1:
        score *= 100
    return max(0.0, min(100.0, score))


def interpret_confidence(confidence) -> dict:
    confidence_score = normalize_probability(confidence)
    if confidence_score >= 75:
        confidence_label = "High"
        message = "The classifier shows strong confidence for this role prediction."
        risk_note = "Review supporting terms and fit signals before relying on the role label."
    elif confidence_score >= 50:
        confidence_label = "Moderate"
        message = "The classifier shows moderate confidence. Review supporting evidence before relying on the role label."
        risk_note = "Use ATS, skill, semantic, and recruiter review signals alongside the prediction."
    elif confidence_score >= 25:
        confidence_label = "Low"
        message = "The classifier confidence is low, so the predicted role should be interpreted carefully."
        risk_note = "Model confidence should be interpreted carefully for this resume."
    else:
        confidence_label = "Very Low"
        message = (
            "The classifier confidence is very low. Treat the predicted role as a weak signal and rely more "
            "on ATS, skill, semantic, and recruiter review signals."
        )
        risk_note = "The predicted role is a weak signal for this resume."

    return {
        "confidence_score": round(confidence_score, 1),
        "confidence_label": confidence_label,
        "message": message,
        "risk_note": risk_note,
    }


def get_pipeline_parts(model_or_pipeline):
    if model_or_pipeline is None:
        return {
            "vectorizer": None,
            "classifier": None,
            "available": False,
            "message": "Prediction explanation is unavailable for the current model object.",
        }

    vectorizer = None
    classifier = None
    if isinstance(model_or_pipeline, dict):
        for key in ("tfidf", "vectorizer", "tfidfvectorizer"):
            if model_or_pipeline.get(key) is not None:
                vectorizer = model_or_pipeline.get(key)
                break
        for key in ("clf", "classifier", "model", "logreg", "logisticregression"):
            if model_or_pipeline.get(key) is not None:
                classifier = model_or_pipeline.get(key)
                break
    elif hasattr(model_or_pipeline, "named_steps"):
        named_steps = model_or_pipeline.named_steps
        for key in ("tfidf", "vectorizer", "tfidfvectorizer"):
            if key in named_steps:
                vectorizer = named_steps[key]
                break
        for key in ("clf", "classifier", "model", "logreg", "logisticregression"):
            if key in named_steps:
                classifier = named_steps[key]
                break
        if vectorizer is None:
            for step in named_steps.values():
                if hasattr(step, "get_feature_names_out") and hasattr(step, "transform"):
                    vectorizer = step
                    break
        if classifier is None:
            for step in reversed(list(named_steps.values())):
                if hasattr(step, "predict"):
                    classifier = step
                    break
    else:
        if hasattr(model_or_pipeline, "get_feature_names_out") and hasattr(model_or_pipeline, "transform"):
            vectorizer = model_or_pipeline
        if hasattr(model_or_pipeline, "predict"):
            classifier = model_or_pipeline

    available = vectorizer is not None and classifier is not None
    message = "TF-IDF vectorizer and classifier were found." if available else (
        "Prediction explanation is unavailable for the current model artifact."
    )
    return {
        "vectorizer": vectorizer,
        "classifier": classifier,
        "available": available,
        "message": message,
    }


def _tfidf_features(resume_text: str, vectorizer):
    feature_names = vectorizer.get_feature_names_out()
    features = vectorizer.transform([resume_text or ""])
    row = features.tocsr()[0]
    return feature_names, row


def extract_top_tfidf_terms(resume_text: str, model_or_pipeline=None, predicted_role=None, top_n: int = 12) -> dict:
    if not (resume_text or "").strip():
        return {
            "available": False,
            "supporting_terms": [],
            "message": "Prediction term explanation is unavailable because resume text is empty.",
        }

    parts = get_pipeline_parts(model_or_pipeline)
    vectorizer = parts.get("vectorizer")
    if vectorizer is None or not hasattr(vectorizer, "get_feature_names_out"):
        return {
            "available": False,
            "supporting_terms": [],
            "message": "Prediction term explanation is unavailable for the current model object.",
        }

    try:
        feature_names, row = _tfidf_features(resume_text, vectorizer)
        scored_terms = [
            {"term": str(feature_names[index]), "score": round(float(value), 4)}
            for index, value in zip(row.indices, row.data)
        ]
        scored_terms = sorted(scored_terms, key=lambda item: item["score"], reverse=True)[:top_n]
    except Exception:
        return {
            "available": False,
            "supporting_terms": [],
            "message": "Prediction term explanation is unavailable for the current model object.",
        }

    return {
        "available": bool(scored_terms),
        "supporting_terms": scored_terms,
        "message": "These terms were prominent in the resume text and may have contributed to the prediction.",
    }


def extract_linear_model_evidence(resume_text: str, model_or_pipeline=None, predicted_role=None, top_n: int = 12) -> dict:
    parts = get_pipeline_parts(model_or_pipeline)
    vectorizer = parts.get("vectorizer")
    classifier = parts.get("classifier")
    if (
        vectorizer is None
        or classifier is None
        or not hasattr(classifier, "coef_")
        or not hasattr(classifier, "classes_")
        or predicted_role is None
    ):
        fallback = extract_top_tfidf_terms(resume_text, model_or_pipeline, predicted_role, top_n)
        fallback["method"] = "Top TF-IDF terms"
        return fallback

    try:
        classes = list(classifier.classes_)
        if predicted_role not in classes:
            fallback = extract_top_tfidf_terms(resume_text, model_or_pipeline, predicted_role, top_n)
            fallback["method"] = "Top TF-IDF terms"
            return fallback

        class_index = classes.index(predicted_role)
        feature_names, row = _tfidf_features(resume_text, vectorizer)
        coefficients = classifier.coef_[class_index]
        scored_terms = []
        for index, tfidf_value in zip(row.indices, row.data):
            score = float(tfidf_value) * float(coefficients[index])
            if score > 0:
                scored_terms.append({"term": str(feature_names[index]), "score": round(score, 4)})
        scored_terms = sorted(scored_terms, key=lambda item: item["score"], reverse=True)[:top_n]
    except Exception:
        fallback = extract_top_tfidf_terms(resume_text, model_or_pipeline, predicted_role, top_n)
        fallback["method"] = "Top TF-IDF terms"
        return fallback

    if not scored_terms:
        fallback = extract_top_tfidf_terms(resume_text, model_or_pipeline, predicted_role, top_n)
        fallback["method"] = "Top TF-IDF terms"
        return fallback

    return {
        "available": True,
        "method": "TF-IDF x Logistic Regression coefficients",
        "supporting_terms": scored_terms,
        "message": "These terms had positive weight for the predicted role in the baseline classifier.",
    }


def build_prediction_explanation(
    resume_text: str,
    prediction_result=None,
    model_or_pipeline=None,
    top_n: int = 12,
) -> dict:
    prediction_result = prediction_result if isinstance(prediction_result, dict) else {}
    predicted_role = safe_get(prediction_result, "role", "Not available")
    confidence_value = safe_get(prediction_result, "confidence")
    if confidence_value is None:
        confidence_value = safe_get(prediction_result, "confidence_display")
    confidence = interpret_confidence(confidence_value)

    evidence = extract_linear_model_evidence(
        resume_text=resume_text,
        model_or_pipeline=model_or_pipeline,
        predicted_role=predicted_role,
        top_n=top_n,
    )

    strengths = []
    warnings = ["This explanation is based on the current baseline model."]
    if evidence.get("available") and evidence.get("supporting_terms"):
        strengths.append("Supporting terms were found in the resume text.")
    else:
        warnings.append(evidence.get("message", "Prediction explanation is unavailable for the current model artifact."))
    if confidence.get("confidence_label") in {"Low", "Very Low"}:
        warnings.append(confidence.get("risk_note"))
        warnings.append("Model confidence should be interpreted carefully.")

    return {
        "available": bool(evidence.get("available")) or confidence_value is not None,
        "predicted_role": predicted_role,
        "confidence": confidence,
        "explanation_method": evidence.get("method", "Top TF-IDF terms"),
        "supporting_terms": evidence.get("supporting_terms", []),
        "strengths": strengths,
        "warnings": list(dict.fromkeys([warning for warning in warnings if warning])),
        "message": evidence.get("message", ""),
        "disclaimer": PREDICTION_EXPLAINER_DISCLAIMER,
    }


def get_prediction_explanation_cards(explanation: dict) -> list[dict]:
    explanation = explanation if isinstance(explanation, dict) else {}
    confidence = safe_get(explanation, "confidence", {}) or {}
    return [
        {
            "title": "Predicted Role",
            "value": safe_get(explanation, "predicted_role", "Not available"),
            "helper_text": "Current classifier output.",
        },
        {
            "title": "Confidence Level",
            "value": safe_get(confidence, "confidence_label", "Not available"),
            "helper_text": f"{safe_get(confidence, 'confidence_score', 0)}% model confidence.",
        },
        {
            "title": "Explanation Method",
            "value": safe_get(explanation, "explanation_method", "Unavailable"),
            "helper_text": "Local baseline explanation.",
        },
    ]
