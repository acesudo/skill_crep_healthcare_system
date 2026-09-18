"""Metadata manifest generator for tracking dataset provenance, metrics, and quality status.
"""

from datetime import datetime
from typing import Dict
import pandas as pd
from .config import DataGenerationConfig


class MetadataGenerator:
    """Generates the standardized dataset_metadata.json artifact."""

    @staticmethod
    def generate_manifest(
        config: DataGenerationConfig,
        full_df: pd.DataFrame,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame,
        dq_report: Dict[str, any],
        leakage_report: Dict[str, any],
    ) -> Dict[str, any]:
        """Constructs full provenance and quality metadata."""
        now_iso = datetime.utcnow().isoformat() + "Z"

        cat_dist = full_df["category"].value_counts().to_dict()
        urg_dist = full_df["urgency"].value_counts().to_dict()
        cross_tab = pd.crosstab(full_df["category"], full_df["urgency"]).to_dict()

        manifest = {
            "dataset_version": config.dataset_version,
            "generator_version": config.generator_version,
            "schema_version": config.schema_version,
            "generation_timestamp": now_iso,
            "generation_method": "deterministic_templated_lexical_synthesis",
            "random_seed": config.random_seed,
            "total_records": len(full_df),
            "train_records": len(train_df),
            "validation_records": len(val_df),
            "test_records": len(test_df),
            "split_ratios": {
                "train": config.train_ratio,
                "validation": config.val_ratio,
                "test": config.test_ratio,
            },
            "category_distribution": cat_dist,
            "urgency_distribution": urg_dist,
            "category_urgency_matrix": cross_tab,
            "message_length_statistics": dq_report["checks"].get("DQ-13_length_metrics", {}),
            "validation_status": {
                "overall_passed": dq_report["passed"] and leakage_report["passed"],
                "quality_checks_passed": dq_report["passed"],
                "zero_leakage_passed": leakage_report["passed"],
                "pii_violations": dq_report["checks"]["DQ-14_pii_safety"]["total_violations"],
                "exact_duplicates": dq_report["checks"]["DQ-08_exact_duplicates"]["count"],
                "near_duplicates": dq_report["checks"]["DQ-09_near_duplicates"]["count"],
            },
            "field_definitions": {
                "message_id": "Unique synthetic message identifier (MSG-XXXXXX)",
                "message_text": "Synthetic patient support message string (Primary ML Feature)",
                "category": "Operational topic category (Target Label 1)",
                "urgency": "Operational turnaround priority: Routine or Urgent (Target Label 2)",
                "department": "Assigned operational department queue (Derived downstream)",
                "timestamp": "ISO 8601 synthetic submission timestamp",
                "generation_source": "Source provenance generator tag",
                "dataset_version": "Dataset release version identifier",
            },
            "prohibited_ml_features": [
                "message_id",
                "department",
                "timestamp",
                "generation_source",
                "dataset_version",
                "category",
                "urgency",
            ],
        }

        return manifest
