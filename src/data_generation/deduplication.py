"""Multi-tier duplicate and near-duplicate detection engine for dataset hygiene.
"""

import re
from typing import Dict, List, Set, Tuple


class DeduplicationEngine:
    """Detects exact duplicates, normalized duplicates, and lexical near-duplicates."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Lowercases, strips punctuation, and collapses whitespace."""
        if text is None or not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def get_char_ngrams(text: str, n: int = 3) -> Set[str]:
        """Extracts character n-grams for fuzzy similarity comparisons."""
        norm = DeduplicationEngine.normalize_text(text)
        if len(norm) < n:
            return {norm}
        return {norm[i:i + n] for i in range(len(norm) - n + 1)}

    @classmethod
    def jaccard_similarity(cls, text_a: str, text_b: str, n: int = 3) -> float:
        """Computes Jaccard similarity coefficient over character n-grams."""
        grams_a = cls.get_char_ngrams(text_a, n)
        grams_b = cls.get_char_ngrams(text_b, n)
        union = grams_a.union(grams_b)
        if not union:
            return 0.0
        return len(grams_a.intersection(grams_b)) / len(union)

    @classmethod
    def audit_duplicates(
        cls,
        records: List[Dict[str, str]],
        near_duplicate_threshold: float = 0.85
    ) -> Dict[str, any]:
        """Comprehensive scan across Level 1, Level 2, and Level 3 duplicate checks."""
        exact_seen: Dict[str, str] = {}
        exact_duplicates: List[Tuple[str, str, str]] = []

        norm_seen: Dict[str, str] = {}
        norm_duplicates: List[Tuple[str, str, str]] = []

        near_duplicates: List[Dict[str, any]] = []

        # 1. Exact and Normalized Pass
        normalized_records = []
        for rec in records:
            msg_id = rec["message_id"]
            raw_text = rec["message_text"]
            norm_text = cls.normalize_text(raw_text)

            # Exact Check
            if raw_text in exact_seen:
                exact_duplicates.append((msg_id, exact_seen[raw_text], raw_text))
            else:
                exact_seen[raw_text] = msg_id

            # Normalized Check
            if norm_text in norm_seen:
                norm_duplicates.append((msg_id, norm_seen[norm_text], raw_text))
            else:
                norm_seen[norm_text] = msg_id

            normalized_records.append((msg_id, raw_text))

        # 2. Near-Duplicate Pass (Pairwise on sample or within same category)
        # To avoid O(N^2) explosion on large files, we compare records
        n_records = len(normalized_records)
        for i in range(n_records):
            id_a, text_a = normalized_records[i]
            for j in range(i + 1, min(i + 50, n_records)):
                id_b, text_b = normalized_records[j]
                sim = cls.jaccard_similarity(text_a, text_b)
                if sim >= near_duplicate_threshold:
                    near_duplicates.append({
                        "id_a": id_a,
                        "id_b": id_b,
                        "similarity": round(sim, 4),
                        "snippet_a": text_a[:60] + "...",
                        "snippet_b": text_b[:60] + "...",
                    })

        return {
            "passed": len(exact_duplicates) == 0 and len(norm_duplicates) == 0,
            "exact_duplicate_count": len(exact_duplicates),
            "exact_duplicates": exact_duplicates,
            "norm_duplicate_count": len(norm_duplicates),
            "norm_duplicates": norm_duplicates,
            "near_duplicate_count": len(near_duplicates),
            "near_duplicates": near_duplicates,
        }
