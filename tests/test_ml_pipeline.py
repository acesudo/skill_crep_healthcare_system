"""Unit tests for ML pipeline components: preprocessing, TF-IDF feature extraction,
candidate models, and evaluation utilities.
"""

import numpy as np
import pytest
from src.ml.preprocessing import TextPreprocessor
from src.ml.features import TfidfFeatureExtractor
from src.ml.models import get_candidate_models, get_hyperparameter_grids
from src.ml.evaluation import ModelEvaluator


def test_text_preprocessor_basic():
    preprocessor = TextPreprocessor()
    raw_text = "Hello! I can't access my portal at (555) 123-4567 or user@clinic.org."
    cleaned = preprocessor.transform(raw_text)

    # Verifications
    assert "can not" in cleaned
    assert "__phone__" in cleaned
    assert "__email__" in cleaned
    assert cleaned == cleaned.lower()
    assert len(cleaned) > 0


def test_text_preprocessor_batch():
    preprocessor = TextPreprocessor()
    batch = [
        "Please refill my lisinopril 10mg.",
        "Need to reschedule appointment for next Tuesday.",
    ]
    cleaned_batch = preprocessor.transform_batch(batch)
    assert len(cleaned_batch) == 2
    assert isinstance(cleaned_batch[0], str)
    assert isinstance(cleaned_batch[1], str)


def test_tfidf_feature_extractor_anti_leakage():
    train_docs = [
        "refill blood pressure medication lisinopril",
        "schedule annual physical checkup appointment",
        "billing statement question copay insurance",
    ]
    val_docs = [
        "refill lisinopril urgently",
        "appointment cancellation",
    ]

    extractor = TfidfFeatureExtractor(ngram_range=(1, 1), min_df=1, max_features=50)
    X_train = extractor.fit_transform(train_docs)
    X_val = extractor.transform(val_docs)

    assert extractor.vocabulary_size > 0
    assert X_train.shape[0] == len(train_docs)
    assert X_val.shape[0] == len(val_docs)
    assert X_train.shape[1] == X_val.shape[1] == extractor.vocabulary_size


def test_candidate_models_structure():
    cat_models, urg_models = get_candidate_models(random_state=42)
    assert "LogisticRegression" in cat_models
    assert "LinearSVC" in cat_models
    assert "MultinomialNB" in cat_models

    assert "LogisticRegression" in urg_models
    assert "LinearSVC" in urg_models
    assert "MultinomialNB" in urg_models

    grids = get_hyperparameter_grids()
    assert "LogisticRegression" in grids
    assert "LinearSVC" in grids
    assert "MultinomialNB" in grids


def test_model_evaluator_category():
    y_true = ["Appointment", "Billing", "Medication Refill", "Appointment"]
    y_pred = ["Appointment", "Billing", "Appointment", "Appointment"]
    labels = ["Appointment", "Billing", "Medication Refill"]

    eval_result = ModelEvaluator.evaluate_category(y_true, y_pred, labels=labels)
    assert "accuracy" in eval_result
    assert "macro_f1" in eval_result
    assert "per_class" in eval_result
    assert eval_result["accuracy"] == 0.75
    assert len(eval_result["confusion_matrix"]) == 3


def test_model_evaluator_urgency():
    y_true = ["Routine", "Urgent", "Routine", "Urgent"]
    y_pred = ["Routine", "Urgent", "Urgent", "Urgent"]
    probs = np.array([[0.8, 0.2], [0.1, 0.9], [0.4, 0.6], [0.2, 0.8]])

    eval_result = ModelEvaluator.evaluate_urgency(y_true, y_pred, y_probs=probs)
    assert eval_result["urgent_recall"] == 1.0
    assert eval_result["brier_score"] is not None
    assert 0.0 <= eval_result["brier_score"] <= 1.0
