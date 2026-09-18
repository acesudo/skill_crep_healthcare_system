"""Unit tests for DataQualityValidator and quality checks (DQ-01 through DQ-15).
"""

import pandas as pd
import pytest
from src.data_generation.config import DataGenerationConfig
from src.data_generation.validators import DataQualityValidator


def test_validator_on_clean_data():
    config = DataGenerationConfig()
    df = pd.read_csv("data/processed/dataset_clean.csv")
    validator = DataQualityValidator(config)
    report = validator.validate_dataset(df)

    assert report["passed"] is True
    assert len(report["errors"]) == 0
    assert report["checks"]["DQ-01_required_columns"]["passed"] is True
    assert report["checks"]["DQ-02_no_null_values"]["passed"] is True
    assert report["checks"]["DQ-03_valid_categories"]["passed"] is True
    assert report["checks"]["DQ-04_valid_urgency"]["passed"] is True
    assert report["checks"]["DQ-06_unique_message_ids"]["passed"] is True
    assert report["checks"]["DQ-08_exact_duplicates"]["count"] == 0
    assert report["checks"]["DQ-14_pii_safety"]["total_violations"] == 0


def test_validator_catches_null_values():
    config = DataGenerationConfig()
    df = pd.read_csv("data/processed/dataset_clean.csv").copy()
    df.loc[0, "message_text"] = None
    validator = DataQualityValidator(config)
    report = validator.validate_dataset(df)

    assert report["passed"] is False
    assert report["checks"]["DQ-02_no_null_values"]["passed"] is False


def test_validator_catches_invalid_category():
    config = DataGenerationConfig()
    df = pd.read_csv("data/processed/dataset_clean.csv").copy()
    df.loc[0, "category"] = "NonExistentCategory"
    validator = DataQualityValidator(config)
    report = validator.validate_dataset(df)

    assert report["passed"] is False
    assert report["checks"]["DQ-03_valid_categories"]["passed"] is False
