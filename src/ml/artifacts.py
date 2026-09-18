"""Model artifact serialization, persistence, and loading utilities using joblib.
"""

import json
from pathlib import Path
from typing import Any, Dict
import joblib


class ArtifactManager:
    """Manages saving and loading of model artifacts, vectorizers, and metadata manifests."""

    @staticmethod
    def save_artifacts(
        base_dir: str,
        version: str,
        vectorizer: Any,
        category_model: Any,
        urgency_model: Any,
        metadata: Dict[str, Any],
    ) -> Dict[str, str]:
        """Serializes models, vectorizer, and metadata manifest to disk."""
        target_dir = Path(base_dir) / version
        target_dir.mkdir(parents=True, exist_ok=True)

        vec_path = target_dir / "tfidf_vectorizer.joblib"
        cat_path = target_dir / "category_model.joblib"
        urg_path = target_dir / "urgency_model.joblib"
        meta_path = target_dir / "metadata.json"

        joblib.dump(vectorizer, vec_path, compress=3)
        joblib.dump(category_model, cat_path, compress=3)
        joblib.dump(urgency_model, urg_path, compress=3)

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return {
            "model_directory": str(target_dir),
            "vectorizer_path": str(vec_path),
            "category_model_path": str(cat_path),
            "urgency_model_path": str(urg_path),
            "metadata_path": str(meta_path),
        }

    @staticmethod
    def load_artifacts(base_dir: str, version: str) -> Dict[str, Any]:
        """Loads serialized model pipeline and metadata from disk."""
        target_dir = Path(base_dir) / version
        if not target_dir.exists():
            raise FileNotFoundError(f"Model directory '{target_dir}' does not exist.")

        vec_path = target_dir / "tfidf_vectorizer.joblib"
        cat_path = target_dir / "category_model.joblib"
        urg_path = target_dir / "urgency_model.joblib"
        meta_path = target_dir / "metadata.json"

        vectorizer = joblib.load(vec_path)
        category_model = joblib.load(cat_path)
        urgency_model = joblib.load(urg_path)

        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        return {
            "vectorizer": vectorizer,
            "category_model": category_model,
            "urgency_model": urgency_model,
            "metadata": metadata,
        }
