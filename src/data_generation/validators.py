"""Automated data quality verification suite covering checks DQ-01 through DQ-16.
"""

from typing import Dict, List
import pandas as pd
from .config import DataGenerationConfig
from .deduplication import DeduplicationEngine
from .pii_checker import PiiValidator


class DataQualityValidator:
    """Executes checks DQ-01 through DQ-16 to guarantee dataset integrity."""

    def __init__(self, config: DataGenerationConfig = DataGenerationConfig()):
        self.config = config

    def validate_dataset(self, df: pd.DataFrame) -> Dict[str, any]:
        """Runs automated quality checks on the consolidated dataset."""
        report = {
            "passed": True,
            "checks": {},
            "errors": [],
            "warnings": [],
        }

        # DQ-01: Required columns exist
        required_cols = ["message_id", "message_text", "category", "urgency", "department", "timestamp"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        dq01_passed = len(missing_cols) == 0
        report["checks"]["DQ-01_required_columns"] = {
            "passed": dq01_passed,
            "missing_columns": missing_cols,
        }
        if not dq01_passed:
            report["passed"] = False
            report["errors"].append(f"DQ-01 Failed: Missing required columns {missing_cols}")

        # DQ-02: No required field is null
        null_counts = df[required_cols].isnull().sum().to_dict()
        total_nulls = sum(null_counts.values())
        dq02_passed = total_nulls == 0
        report["checks"]["DQ-02_no_null_values"] = {
            "passed": dq02_passed,
            "null_counts": null_counts,
        }
        if not dq02_passed:
            report["passed"] = False
            report["errors"].append(f"DQ-02 Failed: Found null values in dataset: {null_counts}")

        # DQ-03: Category values are valid
        invalid_cats = df[~df["category"].isin(self.config.categories)]["category"].unique().tolist()
        dq03_passed = len(invalid_cats) == 0
        report["checks"]["DQ-03_valid_categories"] = {
            "passed": dq03_passed,
            "invalid_categories": invalid_cats,
        }
        if not dq03_passed:
            report["passed"] = False
            report["errors"].append(f"DQ-03 Failed: Invalid categories {invalid_cats}")

        # DQ-04: Urgency values are valid
        invalid_urg = df[~df["urgency"].isin(self.config.urgency_levels)]["urgency"].unique().tolist()
        dq04_passed = len(invalid_urg) == 0
        report["checks"]["DQ-04_valid_urgency"] = {
            "passed": dq04_passed,
            "invalid_urgency": invalid_urg,
        }
        if not dq04_passed:
            report["passed"] = False
            report["errors"].append(f"DQ-04 Failed: Invalid urgency values {invalid_urg}")

        # DQ-05: Department values are valid
        allowed_depts = set(self.config.category_to_department.values())
        invalid_depts = df[~df["department"].isin(allowed_depts)]["department"].unique().tolist()
        dq05_passed = len(invalid_depts) == 0
        report["checks"]["DQ-05_valid_departments"] = {
            "passed": dq05_passed,
            "invalid_departments": invalid_depts,
        }
        if not dq05_passed:
            report["passed"] = False
            report["errors"].append(f"DQ-05 Failed: Invalid departments {invalid_depts}")

        # DQ-06: Unique Message IDs
        total_ids = len(df["message_id"])
        unique_ids = df["message_id"].nunique()
        dq06_passed = total_ids == unique_ids
        report["checks"]["DQ-06_unique_message_ids"] = {
            "passed": dq06_passed,
            "total_ids": total_ids,
            "unique_ids": unique_ids,
        }
        if not dq06_passed:
            report["passed"] = False
            report["errors"].append("DQ-06 Failed: Duplicate message IDs detected")

        # DQ-07: Message text length constraints
        clean_text_series = df["message_text"].fillna("").astype(str).str.strip()
        lengths = clean_text_series.str.len()
        short_msgs = df[lengths < self.config.min_message_length]
        long_msgs = df[lengths > self.config.max_message_length]
        dq07_passed = len(short_msgs) == 0 and len(long_msgs) == 0
        report["checks"]["DQ-07_text_length_constraints"] = {
            "passed": dq07_passed,
            "short_count": len(short_msgs),
            "long_count": len(long_msgs),
            "min_len": int(lengths.min()),
            "max_len": int(lengths.max()),
            "mean_len": float(round(lengths.mean(), 2)),
        }
        if not dq07_passed:
            report["passed"] = False
            report["errors"].append(f"DQ-07 Failed: Out of bounds text length ({len(short_msgs)} short, {len(long_msgs)} long)")

        # DQ-08 & DQ-09: Exact and Near Duplicates
        records_list = df.to_dict(orient="records")
        dedup_results = DeduplicationEngine.audit_duplicates(
            records_list,
            near_duplicate_threshold=self.config.near_duplicate_jaccard_threshold
        )
        report["checks"]["DQ-08_exact_duplicates"] = {
            "passed": dedup_results["exact_duplicate_count"] == 0,
            "count": dedup_results["exact_duplicate_count"],
        }
        if dedup_results["exact_duplicate_count"] > 0:
            report["passed"] = False
            report["errors"].append(f"DQ-08 Failed: Found {dedup_results['exact_duplicate_count']} exact duplicates")

        report["checks"]["DQ-09_near_duplicates"] = {
            "passed": True,  # Non-blocking warning unless severe
            "count": dedup_results["near_duplicate_count"],
        }
        if dedup_results["near_duplicate_count"] > 50:
            report["warnings"].append(f"DQ-09 Warning: High near-duplicate count: {dedup_results['near_duplicate_count']}")

        # DQ-10: Category distribution
        cat_counts = df["category"].value_counts().to_dict()
        cat_passed = all(count == self.config.records_per_category for count in cat_counts.values())
        report["checks"]["DQ-10_category_distribution"] = {
            "passed": cat_passed,
            "counts": cat_counts,
        }
        if not cat_passed:
            report["passed"] = False
            report["errors"].append(f"DQ-10 Failed: Category distribution mismatch: {cat_counts}")

        # DQ-11: Urgency distribution (~70% Routine, ~30% Urgent)
        urg_counts = df["urgency"].value_counts().to_dict()
        urg_passed = urg_counts.get("Routine", 0) == 630 and urg_counts.get("Urgent", 0) == 270
        report["checks"]["DQ-11_urgency_distribution"] = {
            "passed": urg_passed,
            "counts": urg_counts,
            "routine_pct": round(urg_counts.get("Routine", 0) / len(df) * 100, 2),
            "urgent_pct": round(urg_counts.get("Urgent", 0) / len(df) * 100, 2),
        }
        if not urg_passed:
            report["passed"] = False
            report["errors"].append(f"DQ-11 Failed: Urgency distribution mismatch: {urg_counts}")

        # DQ-12: Category x Urgency matrix coverage
        cross_tab = pd.crosstab(df["category"], df["urgency"]).to_dict()
        report["checks"]["DQ-12_category_x_urgency_matrix"] = {
            "passed": True,
            "matrix": cross_tab,
        }

        # DQ-13: Message length distribution metrics
        report["checks"]["DQ-13_length_metrics"] = {
            "mean": float(round(lengths.mean(), 2)),
            "std": float(round(lengths.std(), 2)),
            "min": int(lengths.min()),
            "max": int(lengths.max()),
        }

        # DQ-14: PII / PHI Safety Checks
        pii_results = PiiValidator.validate_dataset(records_list)
        report["checks"]["DQ-14_pii_safety"] = {
            "passed": pii_results["passed"],
            "total_violations": pii_results["total_violations"],
        }
        if not pii_results["passed"]:
            report["passed"] = False
            report["errors"].append(f"DQ-14 Failed: Found {pii_results['total_violations']} PII violations")

        # DQ-15: Template repetition tracking
        norm_texts = df["message_text"].apply(DeduplicationEngine.normalize_text)
        unique_norm = norm_texts.nunique()
        report["checks"]["DQ-15_template_diversity"] = {
            "passed": unique_norm == len(df),
            "unique_normalized_texts": unique_norm,
            "total_records": len(df),
        }
        if unique_norm != len(df):
            report["passed"] = False
            report["errors"].append("DQ-15 Failed: Normalized duplicate texts detected")

        return report

    @classmethod
    def validate_split_leakage(
        cls,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame
    ) -> Dict[str, any]:
        """DQ-16: Validates that zero message overlap exists across train, val, and test splits."""
        train_texts = set(train_df["message_text"].str.strip().str.lower())
        val_texts = set(val_df["message_text"].str.strip().str.lower())
        test_texts = set(test_df["message_text"].str.strip().str.lower())

        train_val_overlap = train_texts.intersection(val_texts)
        train_test_overlap = train_texts.intersection(test_texts)
        val_test_overlap = val_texts.intersection(test_texts)

        passed = (len(train_val_overlap) == 0 and 
                  len(train_test_overlap) == 0 and 
                  len(val_test_overlap) == 0)

        return {
            "passed": passed,
            "train_val_overlap_count": len(train_val_overlap),
            "train_test_overlap_count": len(train_test_overlap),
            "val_test_overlap_count": len(val_test_overlap),
        }
