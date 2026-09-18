"""Unit tests for synthetic dataset generator and schema enforcement.
"""

import pytest
from src.data_generation.config import DataGenerationConfig
from src.data_generation.schemas import PatientMessageRecord
from src.data_generation.generator import SyntheticDataGenerator


def test_generator_record_count_and_schema():
    config = DataGenerationConfig()
    generator = SyntheticDataGenerator(config)
    records = generator.generate_dataset()

    assert len(records) == 900
    for r in records:
        record_obj = PatientMessageRecord(**r)
        assert record_obj.message_id.startswith("MSG-")
        assert len(record_obj.message_text) >= config.min_message_length
        assert record_obj.category in config.categories
        assert record_obj.urgency in config.urgency_levels
        assert record_obj.department == config.category_to_department[record_obj.category]


def test_generator_deterministic_reproducibility():
    config1 = DataGenerationConfig(random_seed=42)
    config2 = DataGenerationConfig(random_seed=42)

    g1 = SyntheticDataGenerator(config1)
    g2 = SyntheticDataGenerator(config2)

    records1 = g1.generate_dataset()
    records2 = g2.generate_dataset()

    assert len(records1) == len(records2)
    for r1, r2 in zip(records1, records2):
        assert r1["message_id"] == r2["message_id"]
        assert r1["message_text"] == r2["message_text"]
        assert r1["category"] == r2["category"]
        assert r1["urgency"] == r2["urgency"]
