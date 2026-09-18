"""Direct sparse linear feature weight attribution engine for TF-IDF models.
Provides transparent keyword explanations without generative hallucination.
"""

from typing import List, Tuple
import numpy as np
import scipy.sparse as sp


class FeatureExplainer:
    """Extracts the top positive contributing n-grams/tokens from linear model coefficients."""

    def __init__(self, vectorizer, model, class_labels: List[str]):
        self.vectorizer = vectorizer
        self.model = model
        self.class_labels = list(class_labels)
        self.feature_names = np.array(vectorizer.get_feature_names_out())

    def explain_instance(
        self,
        text_vector: sp.csr_matrix,
        predicted_class: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """Extracts top K tokens with highest positive weight contribution for predicted class."""
        if predicted_class not in self.class_labels:
            return []

        class_idx = self.class_labels.index(predicted_class)

        # Get model coefficients
        # For CalibratedClassifierCV or base estimator
        actual_estimator = self.model
        if hasattr(self.model, "estimator"):
            actual_estimator = self.model.estimator
        elif hasattr(self.model, "calibrated_classifiers_"):
            actual_estimator = self.model.calibrated_classifiers_[0].estimator

        if not hasattr(actual_estimator, "coef_"):
            return []

        coefs = actual_estimator.coef_
        if coefs.shape[0] == 1 and len(self.class_labels) == 2:
            # Binary classifier: class_idx 1 (Urgent) is positive coef, class_idx 0 (Routine) is negative
            weights = coefs[0] if class_idx == 1 else -coefs[0]
        else:
            weights = coefs[class_idx]

        # Element-wise product of TF-IDF feature weight and model coefficient
        non_zero_indices = text_vector.indices
        text_values = text_vector.data

        feature_scores = []
        for idx, val in zip(non_zero_indices, text_values):
            contrib = val * weights[idx]
            if contrib > 0:  # Only positive contributing evidence
                feature_scores.append((self.feature_names[idx], round(float(contrib), 4)))

        # Sort descending by contribution score
        feature_scores.sort(key=lambda x: x[1], reverse=True)
        return feature_scores[:top_k]
