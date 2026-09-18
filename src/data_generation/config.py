"""Configuration parameters for Section 8 Synthetic Data Generation and Engineering.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class DataGenerationConfig:
    # Dataset Identity
    dataset_version: str = "v1.0.0"
    generator_version: str = "1.0.0"
    schema_version: str = "1.0.0"
    random_seed: int = 42

    # Dataset Size Targets
    total_records: int = 900
    records_per_category: int = 150  # 6 categories * 150 = 900
    
    # Split Ratios
    train_ratio: float = 0.70
    val_ratio: float = 0.15
    test_ratio: float = 0.15

    # Categories (From Section 4 & 7)
    categories: List[str] = field(default_factory=lambda: [
        "Appointment",
        "Billing",
        "Medication Refill",
        "Report Request",
        "Technical Issue",
        "Urgent Review",
    ])

    # Urgency Levels (From Section 4 & 7)
    urgency_levels: List[str] = field(default_factory=lambda: [
        "Routine",
        "Urgent",
    ])

    # Department Mapping (From Section 4 & 5)
    category_to_department: Dict[str, str] = field(default_factory=lambda: {
        "Appointment": "Front Desk / Appointment Queue",
        "Billing": "Billing Department Queue",
        "Medication Refill": "Medication / Refill Workflow Queue",
        "Report Request": "Medical Records / Reports Queue",
        "Technical Issue": "Technical Support Queue",
        "Urgent Review": "Urgent Review Queue",
    })

    # Category x Urgency Target Matrix (Total: 900 records, 630 Routine (70%), 270 Urgent (30%))
    category_urgency_targets: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        "Appointment": {"Routine": 110, "Urgent": 40},       # Total: 150
        "Billing": {"Routine": 120, "Urgent": 30},           # Total: 150
        "Medication Refill": {"Routine": 100, "Urgent": 50}, # Total: 150
        "Report Request": {"Routine": 115, "Urgent": 35},    # Total: 150
        "Technical Issue": {"Routine": 120, "Urgent": 30},   # Total: 150
        "Urgent Review": {"Routine": 65, "Urgent": 85},      # Total: 150
    })

    # Validation Thresholds
    min_message_length: int = 10
    max_message_length: int = 2000
    near_duplicate_jaccard_threshold: float = 0.85
