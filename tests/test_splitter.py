"""Unit tests for DatasetSplitter and split leakage checks (DQ-16).
"""

import pandas as pd
import pytest
from src.data_generation.config import DataGenerationConfig
from src.data_generation.splitter import DatasetSplitter
from src.data_generation.validators import DataQualityValidator


def test_splitter_ratios_and_stratification():
    config = DataGenerationConfig()
    df = pd.read_csv("data/processed/dataset_clean.csv")
    splitter = DatasetSplitter(config)
    train_df, val_df, test_df = splitter.split(df)

    assert len(train_df) == 630  # 70% of 900
    assert len(val_df) == 135    # 15% of 900
    assert len(test_df) == 135   # 15% of 900

    # Verify zero overlap (DQ-16)
    leakage = DataQualityValidator.validate_split_leakage(train_df, val_df, test_df)
    assert leakage["passed"] is True
    assert leakage["train_val_overlap_count"] == 0
    assert leakage["train_test_overlap_count"] == 0
    assert leakage["val_test_overlap_count"] == 0


def test_splitter_preserves_urgency_ratio():
    train_df = pd.read_csv("data/splits/train.csv")
    val_df = pd.read_csv("data/splits/validation.csv")
    test_df = pd.read_csv("data/splits/test.csv")

    # Target: 70% Routine, 30% Urgent (+/- 1.5%)
    for split_df in [train_df, val_df, test_df]:
        urg_counts = split_df["urgency"].value_counts()
        routine_ratio = urg_counts["Routine"] / len(split_df)
        urgent_ratio = urg_counts["Urgent"] / len(split_df)

        assert 0.68 <= routine_ratio <= 0.72
        assert 0.28 <= urgent_ratio <= 0.32
