"""Executable orchestration pipeline for Section 8 Synthetic Data Generation and Quality Assurance.
"""

import json
import os
from pathlib import Path
import pandas as pd

from .config import DataGenerationConfig
from .generator import SyntheticDataGenerator
from .validators import DataQualityValidator
from .splitter import DatasetSplitter
from .metadata import MetadataGenerator


def run_pipeline(output_base_dir: str = "data") -> dict:
    """Executes the complete generation, validation, splitting, and metadata pipeline."""
    print("=" * 60)
    print("STARTING SECTION 8 SYNTHETIC DATA GENERATION PIPELINE")
    print("=" * 60)

    config = DataGenerationConfig()
    base_path = Path(output_base_dir)
    raw_dir = base_path / "raw"
    proc_dir = base_path / "processed"
    splits_dir = base_path / "splits"

    raw_dir.mkdir(parents=True, exist_ok=True)
    proc_dir.mkdir(parents=True, exist_ok=True)
    splits_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generation
    print(f"\n[1/6] Generating {config.total_records} synthetic messages (Seed: {config.random_seed})...")
    generator = SyntheticDataGenerator(config)
    records = generator.generate_dataset()
    df_raw = pd.DataFrame(records)
    print(f"      Generated {len(df_raw)} records across {df_raw['category'].nunique()} categories.")

    raw_csv_path = raw_dir / "dataset_raw.csv"
    df_raw.to_csv(raw_csv_path, index=False)
    print(f"      Saved raw dataset to: {raw_csv_path}")

    # 2. Automated Quality Validation
    print("\n[2/6] Executing Automated Data Quality Validation Suite (DQ-01 to DQ-15)...")
    validator = DataQualityValidator(config)
    dq_report = validator.validate_dataset(df_raw)

    if not dq_report["passed"]:
        print("\n[CRITICAL ERROR] Data Quality Validation FAILED!")
        for err in dq_report["errors"]:
            print(f"  - {err}")
        raise RuntimeError("Dataset quality validation failed. See errors above.")
    else:
        print("      All Data Quality checks (DQ-01 to DQ-15) PASSED successfully!")
        print(f"      - Exact Duplicates: {dq_report['checks']['DQ-08_exact_duplicates']['count']}")
        print(f"      - PII Violations: {dq_report['checks']['DQ-14_pii_safety']['total_violations']}")
        print(f"      - Text Length: Mean={dq_report['checks']['DQ-13_length_metrics']['mean']} chars (Min={dq_report['checks']['DQ-13_length_metrics']['min']}, Max={dq_report['checks']['DQ-13_length_metrics']['max']})")

    # 3. Clean Processed Dataset
    clean_csv_path = proc_dir / "dataset_clean.csv"
    df_raw.to_csv(clean_csv_path, index=False)
    print(f"      Saved cleaned dataset to: {clean_csv_path}")

    # 4. Stratified Multi-Target Splitting
    print(f"\n[3/6] Partitioning dataset into Train ({int(config.train_ratio*100)}%), Val ({int(config.val_ratio*100)}%), and Test ({int(config.test_ratio*100)}%)...")
    splitter = DatasetSplitter(config)
    train_df, val_df, test_df = splitter.split(df_raw)

    print(f"      - Train records: {len(train_df)} ({len(train_df)/len(df_raw)*100:.1f}%)")
    print(f"      - Validation records: {len(val_df)} ({len(val_df)/len(df_raw)*100:.1f}%)")
    print(f"      - Test records: {len(test_df)} ({len(test_df)/len(df_raw)*100:.1f}%)")

    train_path = splits_dir / "train.csv"
    val_path = splits_dir / "validation.csv"
    test_path = splits_dir / "test.csv"

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)
    print("      Saved partition CSVs to data/splits/")

    # 5. Zero Split Leakage Audit
    print("\n[4/6] Auditing Splits for Data Leakage (DQ-16)...")
    leakage_report = DataQualityValidator.validate_split_leakage(train_df, val_df, test_df)
    if not leakage_report["passed"]:
        print("\n[CRITICAL ERROR] Split Data Leakage Audit FAILED!")
        raise RuntimeError(f"Split leakage detected: {leakage_report}")
    print("      DQ-16 Zero-Leakage Audit PASSED! (0 overlapping texts across all splits).")

    # 6. Generate Metadata Manifest
    print("\n[5/6] Building Dataset Metadata Manifest (dataset_metadata.json)...")
    metadata_manifest = MetadataGenerator.generate_manifest(
        config=config,
        full_df=df_raw,
        train_df=train_df,
        val_df=val_df,
        test_df=test_df,
        dq_report=dq_report,
        leakage_report=leakage_report,
    )

    metadata_path = base_path / "dataset_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata_manifest, f, indent=2)
    print(f"      Saved metadata manifest to: {metadata_path}")

    # 7. Distribution Summary
    print("\n[6/6] Finalizing Distribution Verification:")
    print("--- Category Distribution ---")
    for cat, cnt in df_raw["category"].value_counts().items():
        print(f"  {cat:<20}: {cnt} records")

    print("\n--- Urgency Distribution ---")
    for urg, cnt in df_raw["urgency"].value_counts().items():
        print(f"  {urg:<20}: {cnt} records ({cnt/len(df_raw)*100:.1f}%)")

    print("\n--- Category x Urgency Matrix ---")
    print(pd.crosstab(df_raw["category"], df_raw["urgency"]))

    print("\n" + "=" * 60)
    print("PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 60)

    return {
        "status": "SUCCESS",
        "total_records": len(df_raw),
        "train_records": len(train_df),
        "val_records": len(val_df),
        "test_records": len(test_df),
        "metadata_path": str(metadata_path),
        "dq_report": dq_report,
        "leakage_report": leakage_report,
    }


if __name__ == "__main__":
    run_pipeline()
