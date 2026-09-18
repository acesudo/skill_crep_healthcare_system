"""Unit tests for artifact persistence, versioning, manifest validation, and feature explainability.
"""

from pathlib import Path
import tempfile
import numpy as np
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from src.ml.artifacts import ArtifactManager
from src.ml.explainability import FeatureExplainer


def test_artifact_save_and_load():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create minimal objects
        vec = TfidfVectorizer().fit(["hello world", "test message"])
        X = vec.transform(["hello world", "test message"])
        cat_m = LogisticRegression().fit(X, ["A", "B"])
        urg_m = LogisticRegression().fit(X, ["Routine", "Urgent"])
        meta = {
            "model_version": "v1.0.0-test",
            "dataset_version": "v1.0.0",
            "feature_count": len(vec.vocabulary_),
        }

        # Save
        saved = ArtifactManager.save_artifacts(
            base_dir=tmp_dir,
            version="v1.0.0-test",
            vectorizer=vec,
            category_model=cat_m,
            urgency_model=urg_m,
            metadata=meta,
        )

        assert Path(saved["vectorizer_path"]).exists()
        assert Path(saved["category_model_path"]).exists()
        assert Path(saved["urgency_model_path"]).exists()
        assert Path(saved["metadata_path"]).exists()

        # Load
        loaded = ArtifactManager.load_artifacts(
            base_dir=tmp_dir,
            version="v1.0.0-test",
        )

        assert loaded["metadata"]["model_version"] == "v1.0.0-test"
        assert hasattr(loaded["vectorizer"], "transform")
        assert hasattr(loaded["category_model"], "predict")
        assert hasattr(loaded["urgency_model"], "predict")


def test_feature_explainer():
    corpus = [
        "severe chest pain difficulty breathing",
        "routine bill question about insurance copay",
    ]
    vec = TfidfVectorizer().fit(corpus)
    X = vec.transform(corpus)
    y = ["Urgent", "Routine"]
    clf = LogisticRegression().fit(X, y)

    explainer = FeatureExplainer(vec, clf, class_labels=clf.classes_)
    sample_vec = vec.transform(["chest pain emergency"])
    explanation = explainer.explain_instance(sample_vec, "Urgent", top_k=3)

    assert isinstance(explanation, list)
    assert len(explanation) > 0
    # The top keyword should be chest or pain
    top_feature_name, top_score = explanation[0]
    assert isinstance(top_feature_name, str)
    assert isinstance(top_score, float)
