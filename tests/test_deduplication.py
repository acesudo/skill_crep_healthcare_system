"""Unit tests for DeduplicationEngine.
"""

import pytest
from src.data_generation.deduplication import DeduplicationEngine


def test_exact_duplicate_detection():
    records = [
        {"message_id": "MSG-000001", "message_text": "I need to reschedule my appointment for tomorrow."},
        {"message_id": "MSG-000002", "message_text": "I need to reschedule my appointment for tomorrow."},
        {"message_id": "MSG-000003", "message_text": "Different message regarding billing inquiry."},
    ]
    report = DeduplicationEngine.audit_duplicates(records)
    assert report["passed"] is False
    assert report["exact_duplicate_count"] == 1
    assert report["exact_duplicates"][0][0] == "MSG-000002"


def test_normalized_duplicate_detection():
    records = [
        {"message_id": "MSG-000001", "message_text": "Need a refill for my Lisinopril medication!"},
        {"message_id": "MSG-000002", "message_text": "need a refill for my lisinopril medication."},
    ]
    report = DeduplicationEngine.audit_duplicates(records)
    assert report["passed"] is False
    assert report["norm_duplicate_count"] == 1


def test_near_duplicate_jaccard_similarity():
    text1 = "I need to reschedule my cardiology appointment due to work."
    text2 = "I need to reschedule my cardiology appointment due to travel."
    sim = DeduplicationEngine.jaccard_similarity(text1, text2)
    assert sim > 0.70

    unrelated = "Why did my credit card get charged twice for lab tests?"
    assert DeduplicationEngine.jaccard_similarity(text1, unrelated) < 0.30
