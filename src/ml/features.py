"""TF-IDF feature extraction module for operational patient messages.
Strictly enforces anti-leakage training isolation.
"""

from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse as sp


class TfidfFeatureExtractor:
    """Extracts unigram and bigram TF-IDF sparse features."""

    def __init__(
        self,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
        max_features=2500,
        sublinear_tf=True,
    ):
        self.params = {
            "ngram_range": ngram_range,
            "min_df": min_df,
            "max_df": max_df,
            "max_features": max_features,
            "sublinear_tf": sublinear_tf,
            "strip_accents": "unicode",
            "norm": "l2",
        }
        self.vectorizer = TfidfVectorizer(**self.params)
        self.is_fitted = False

    def fit(self, texts: List[str]) -> "TfidfFeatureExtractor":
        """Fits vocabulary exclusively on training texts."""
        self.vectorizer.fit(texts)
        self.is_fitted = True
        return self

    def transform(self, texts: List[str]) -> sp.csr_matrix:
        """Transforms preprocessed texts into TF-IDF sparse matrix."""
        if not self.is_fitted:
            raise RuntimeError("Cannot transform before vectorizer has been fitted on training data.")
        return self.vectorizer.transform(texts)

    def fit_transform(self, texts: List[str]) -> sp.csr_matrix:
        """Fits and transforms on training texts."""
        self.is_fitted = True
        return self.vectorizer.fit_transform(texts)

    @property
    def feature_names(self) -> List[str]:
        """Returns vocabulary feature names."""
        if not self.is_fitted:
            return []
        return self.vectorizer.get_feature_names_out().tolist()

    @property
    def vocabulary_size(self) -> int:
        """Returns size of fitted vocabulary."""
        return len(self.feature_names)
