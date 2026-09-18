"""Text preprocessing module for PS-1 operational patient-support messages.
Implements the preprocessing pipeline designed in Section 7.
"""

import re
import unicodedata
from typing import List


class TextPreprocessor:
    """Sanitizes text, expands contractions, normalizes entities, and preserves
    operationally meaningful keywords and negations.
    """

    # Common English contractions mapping
    CONTRACTIONS = {
        r"\bcan't\b": "can not",
        r"\bcannot\b": "can not",
        r"\bwon't\b": "will not",
        r"\bdon't\b": "do not",
        r"\bdidn't\b": "did not",
        r"\bdoesn't\b": "does not",
        r"\bisn't\b": "is not",
        r"\baren't\b": "are not",
        r"\bwasn't\b": "was not",
        r"\bweren't\b": "were not",
        r"\bhaven't\b": "have not",
        r"\bhasn't\b": "has not",
        r"\bhadn't\b": "had not",
        r"\bwouldn't\b": "would not",
        r"\bshouldn't\b": "should not",
        r"\bcouldn't\b": "could not",
        r"\bi'm\b": "i am",
        r"\bi've\b": "i have",
        r"\bi'll\b": "i will",
        r"\bi'd\b": "i would",
        r"\bthey're\b": "they are",
        r"\bwe're\b": "we are",
        r"\bit's\b": "it is",
    }

    # Regex patterns for entity masking
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
    URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
    PHONE_PATTERN = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b")
    NUM_PATTERN = re.compile(r"\b\d{4,}\b")  # Long numerical IDs

    def __init__(self):
        self._compiled_contractions = [
            (re.compile(pattern, re.IGNORECASE), replacement)
            for pattern, replacement in self.CONTRACTIONS.items()
        ]

    def clean(self, text: str) -> str:
        """Applies full preprocessing pipeline to a raw message text."""
        if not text or not isinstance(text, str):
            return ""

        # 1. Unicode NFKD normalization
        text = unicodedata.normalize("NFKD", text)

        # 2. Entity normalization / masking
        text = self.URL_PATTERN.sub(" __URL__ ", text)
        text = self.EMAIL_PATTERN.sub(" __EMAIL__ ", text)
        text = self.PHONE_PATTERN.sub(" __PHONE__ ", text)
        text = self.NUM_PATTERN.sub(" __NUM__ ", text)

        # 3. Contraction expansion
        for pattern, replacement in self._compiled_contractions:
            text = pattern.sub(replacement, text)

        # 4. Lowercase conversion
        text = text.lower()

        # 5. Clean noisy punctuation while preserving question/dollar/exclamation
        # Replace strange symbols with space, keep letters, numbers, basic operational punctuation
        text = re.sub(r"[^\w\s\$\?\!\.\-\#]", " ", text)

        # 6. Collapse repeated whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def transform(self, text: str) -> str:
        """Alias for clean() for scikit-learn transformer consistency."""
        return self.clean(text)

    def transform_batch(self, texts: List[str]) -> List[str]:
        """Preprocesses an iterable of strings."""
        return [self.clean(t) for t in texts]
