"""Master ML training, candidate benchmarking, threshold optimization, and final evaluation pipeline.
Implements the experimental protocol specified in Section 7 and Section 9.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import make_scorer, recall_score
from sklearn.model_selection import GridSearchCV

from .artifacts import ArtifactManager
from .confidence import ConfidenceManager
from .evaluation import ModelEvaluator
from .explainability import FeatureExplainer
from .features import TfidfFeatureExtractor
from .models import get_candidate_models, get_hyperparameter_grids
from .preprocessing import TextPreprocessor


def run_experiments(
    data_dir: str = "data/splits",
    models_dir: str = "models",
    reports_dir: str = "reports",
    random_state: int = 42,
) -> dict:
    print("=" * 70)
    print("STARTING SECTION 9: MACHINE LEARNING MODEL TRAINING & EVALUATION")
    print("=" * 70)

    # 1. Paths and Directories
    data_path = Path(data_dir)
    reports_path = Path(reports_dir)
    cm_path = reports_path / "confusion_matrices"
    reports_path.mkdir(parents=True, exist_ok=True)
    cm_path.mkdir(parents=True, exist_ok=True)

    # 2. Load Sealed Section 8 Data
    print("\n[1/8] Loading Sealed Section 8 Dataset Partitions...")
    train_df = pd.read_csv(data_path / "train.csv")
    val_df = pd.read_csv(data_path / "validation.csv")
    test_df = pd.read_csv(data_path / "test.csv")

    print(f"      - Train: {len(train_df)} rows")
    print(f"      - Validation: {len(val_df)} rows")
    print(f"      - Test: {len(test_df)} rows")

    # 3. Text Preprocessing
    print("\n[2/8] Executing NLP Text Preprocessing Pipeline...")
    preprocessor = TextPreprocessor()
    X_train_raw = train_df["message_text"].tolist()
    X_val_raw = val_df["message_text"].tolist()
    X_test_raw = test_df["message_text"].tolist()

    X_train_clean = preprocessor.transform_batch(X_train_raw)
    X_val_clean = preprocessor.transform_batch(X_val_raw)
    X_test_clean = preprocessor.transform_batch(X_test_raw)

    y_train_cat = train_df["category"].tolist()
    y_val_cat = val_df["category"].tolist()
    y_test_cat = test_df["category"].tolist()

    y_train_urg = train_df["urgency"].tolist()
    y_val_urg = val_df["urgency"].tolist()
    y_test_urg = test_df["urgency"].tolist()

    # 4. TF-IDF Feature Extraction (Fit ONLY on Train)
    print("\n[3/8] Fitting TF-IDF Vectorizer Exclusively on Train Partition...")
    feature_extractor = TfidfFeatureExtractor(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
        max_features=2500,
        sublinear_tf=True,
    )
    X_train_vec = feature_extractor.fit_transform(X_train_clean)
    X_val_vec = feature_extractor.transform(X_val_clean)
    X_test_vec = feature_extractor.transform(X_test_clean)

    print(f"      Vocabulary size: {feature_extractor.vocabulary_size} features")
    print("      Anti-leakage verified: Vectorizer fitted strictly on Train split.")

    # 5. Candidate Benchmarking on Validation Set
    print("\n[4/8] Benchmarking Candidate Classifiers on Validation Set...")
    cat_candidates, urg_candidates = get_candidate_models(random_state)
    comparison_rows = []

    # Category Benchmarks
    print("\n--- Category Model Candidates ---")
    cat_val_metrics = {}
    fitted_cat_models = {}

    for name, model in cat_candidates.items():
        # Train on train
        model.fit(X_train_vec, y_train_cat)
        val_pred = model.predict(X_val_vec)
        metrics = ModelEvaluator.evaluate_category(y_val_cat, val_pred)
        cat_val_metrics[name] = metrics
        fitted_cat_models[name] = model

        print(f"  {name:<20}: Accuracy={metrics['accuracy']:.4f}, Macro F1={metrics['macro_f1']:.4f}, Weighted F1={metrics['weighted_f1']:.4f}")

        comparison_rows.append({
            "Target": "Category",
            "Model": name,
            "Accuracy": metrics["accuracy"],
            "Macro_F1": metrics["macro_f1"],
            "Weighted_F1": metrics["weighted_f1"],
            "Urgent_Recall": "N/A",
            "Urgent_Precision": "N/A",
        })

    # Select Best Category Model (Primary Selection Metric: Validation Macro F1)
    best_cat_name = max(cat_val_metrics, key=lambda k: cat_val_metrics[k]["macro_f1"])
    best_cat_model = fitted_cat_models[best_cat_name]
    print(f"  ==> WINNER for Category: {best_cat_name} (Macro F1 = {cat_val_metrics[best_cat_name]['macro_f1']:.4f})")

    # Urgency Benchmarks
    print("\n--- Urgency Model Candidates ---")
    urg_val_metrics = {}
    fitted_urg_models = {}

    for name, model in urg_candidates.items():
        model.fit(X_train_vec, y_train_urg)
        val_pred = model.predict(X_val_vec)

        # Get probabilities for Brier score if supported
        val_probs = None
        if hasattr(model, "predict_proba"):
            val_probs = model.predict_proba(X_val_vec)

        metrics = ModelEvaluator.evaluate_urgency(y_val_urg, val_pred, val_probs)
        urg_val_metrics[name] = metrics
        fitted_urg_models[name] = model

        print(f"  {name:<20}: Accuracy={metrics['accuracy']:.4f}, Urgent Recall={metrics['urgent_recall']:.4f}, Urgent F1={metrics['urgent_f1']:.4f}, Macro F1={metrics['macro_f1']:.4f}")

        comparison_rows.append({
            "Target": "Urgency",
            "Model": name,
            "Accuracy": metrics["accuracy"],
            "Macro_F1": metrics["macro_f1"],
            "Weighted_F1": metrics["weighted_f1"],
            "Urgent_Recall": metrics["urgent_recall"],
            "Urgent_Precision": metrics["urgent_precision"],
        })

    # Select Best Urgency Model (Primary Selection Metric: Validation Urgent Recall, then Macro F1)
    best_urg_name = max(
        urg_val_metrics,
        key=lambda k: (urg_val_metrics[k]["urgent_recall"], urg_val_metrics[k]["macro_f1"]),
    )
    best_urg_model = fitted_urg_models[best_urg_name]
    print(f"  ==> WINNER for Urgency: {best_urg_name} (Urgent Recall = {urg_val_metrics[best_urg_name]['urgent_recall']:.4f})")

    # Save Model Comparison CSV
    comp_df = pd.DataFrame(comparison_rows)
    comp_csv_path = reports_path / "model_comparison.csv"
    comp_df.to_csv(comp_csv_path, index=False)
    print(f"      Saved candidate comparison table to: {comp_csv_path}")

    # 6. Hyperparameter Tuning on Selected Models
    print("\n[5/8] Performing Cross-Validated Hyperparameter Tuning on Selected Models...")
    grids = get_hyperparameter_grids()

    # Category Tuning
    cat_grid = grids[best_cat_name]
    clf_cat_base = get_candidate_models(random_state)[0][best_cat_name]
    grid_search_cat = GridSearchCV(
        clf_cat_base,
        cat_grid,
        cv=5,
        scoring="f1_macro",
        n_jobs=-1,
    )
    grid_search_cat.fit(X_train_vec, y_train_cat)
    final_cat_model = grid_search_cat.best_estimator_
    print(f"      Best Category Params ({best_cat_name}): {grid_search_cat.best_params_}")

    # Urgency Tuning
    urg_grid = grids[best_urg_name]
    clf_urg_base = get_candidate_models(random_state)[1][best_urg_name]
    grid_search_urg = GridSearchCV(
        clf_urg_base,
        urg_grid,
        cv=5,
        scoring=make_scorer(recall_score, pos_label="Urgent"),
        n_jobs=-1,
    )
    grid_search_urg.fit(X_train_vec, y_train_urg)
    final_urg_model = grid_search_urg.best_estimator_
    print(f"      Best Urgency Params ({best_urg_name}): {grid_search_urg.best_params_}")

    # Probability Calibration check
    print("\n--- Probability Calibration Check ---")
    # If LinearSVC was chosen, wrap in CalibratedClassifierCV
    if best_cat_name == "LinearSVC":
        print("      Applying Platt Scaling (CalibratedClassifierCV) to Category LinearSVC...")
        cal_cat = CalibratedClassifierCV(estimator=final_cat_model, cv=5, method="sigmoid")
        cal_cat.fit(X_train_vec, y_train_cat)
        final_cat_model = cal_cat

    if best_urg_name == "LinearSVC":
        print("      Applying Platt Scaling (CalibratedClassifierCV) to Urgency LinearSVC...")
        cal_urg = CalibratedClassifierCV(estimator=final_urg_model, cv=5, method="sigmoid")
        cal_urg.fit(X_train_vec, y_train_urg)
        final_urg_model = cal_urg

    # 7. Confidence Evaluation & Threshold Tau Tuning on VALIDATION Set
    print("\n[6/8] Tuning Confidence Threshold Tau on VALIDATION Set...")
    # Get probabilities on validation set
    val_cat_probs = final_cat_model.predict_proba(X_val_vec)
    val_urg_probs = final_urg_model.predict_proba(X_val_vec)

    val_cat_preds = final_cat_model.predict(X_val_vec).tolist()
    val_urg_preds = final_urg_model.predict(X_val_vec).tolist()

    val_overall_conf = ConfidenceManager.compute_overall_confidence(val_cat_probs, val_urg_probs)
    threshold_evals = ConfidenceManager.evaluate_threshold_grid(
        overall_confidences=val_overall_conf,
        y_true_urgency=y_val_urg,
        y_pred_urgency=val_urg_preds,
        tau_range=(0.60, 0.90),
        step=0.02,
    )

    opt_tau_info = ConfidenceManager.select_optimal_tau(threshold_evals)
    selected_tau = opt_tau_info["selected_tau"]

    print(f"      Optimal Threshold Tau Selected: {selected_tau}")
    print(f"      - Validation Human Review Rate: {opt_tau_info['metrics']['human_review_rate'] * 100:.1f}%")
    print(f"      - Validation Routing Coverage: {opt_tau_info['metrics']['routing_coverage'] * 100:.1f}%")
    print(f"      - Missed Urgent Auto-Routed: {opt_tau_info['metrics']['missed_urgent_auto_routed']} cases")

    # Generate Validation Confusion Matrices
    val_cat_eval = ModelEvaluator.evaluate_category(y_val_cat, val_cat_preds)
    val_urg_eval = ModelEvaluator.evaluate_urgency(y_val_urg, val_urg_preds, val_urg_probs)

    ModelEvaluator.plot_confusion_matrix(
        val_cat_eval["confusion_matrix"],
        val_cat_eval["labels"],
        f"Category Validation CM ({best_cat_name})",
        str(cm_path / "category_validation_cm.png"),
    )
    ModelEvaluator.plot_confusion_matrix(
        val_urg_eval["confusion_matrix"],
        val_urg_eval["labels"],
        f"Urgency Validation CM ({best_urg_name})",
        str(cm_path / "urgency_validation_cm.png"),
    )

    # 8. Final Evaluation on UNTOUCHED TEST SET
    print("\n[7/8] Executing Final Evaluation on Untouched TEST Set (Executed Exactly Once)...")
    test_cat_probs = final_cat_model.predict_proba(X_test_vec)
    test_urg_probs = final_urg_model.predict_proba(X_test_vec)

    test_cat_preds = final_cat_model.predict(X_test_vec).tolist()
    test_urg_preds = final_urg_model.predict(X_test_vec).tolist()

    test_cat_eval = ModelEvaluator.evaluate_category(y_test_cat, test_cat_preds)
    test_urg_eval = ModelEvaluator.evaluate_urgency(y_test_urg, test_urg_preds, test_urg_probs)

    test_overall_conf = ConfidenceManager.compute_overall_confidence(test_cat_probs, test_urg_probs)
    test_auto_routed = test_overall_conf >= selected_tau
    test_human_review = test_overall_conf < selected_tau

    n_test = len(test_df)
    test_review_rate = round(float(np.sum(test_human_review) / n_test), 4)
    test_coverage = round(float(np.sum(test_auto_routed) / n_test), 4)

    # Missed urgent cases on Test
    test_missed_urgent = sum(
        1 for i in range(n_test)
        if test_auto_routed[i] and y_test_urg[i] == "Urgent" and test_urg_preds[i] == "Routine"
    )

    print("\n================ FINAL TEST RESULTS ================")
    print(f"CATEGORY ({best_cat_name}):")
    print(f"  Accuracy:         {test_cat_eval['accuracy']:.4f}")
    print(f"  Macro Precision:  {test_cat_eval['macro_precision']:.4f}")
    print(f"  Macro Recall:     {test_cat_eval['macro_recall']:.4f}")
    print(f"  Macro F1:         {test_cat_eval['macro_f1']:.4f}")
    print(f"  Weighted F1:      {test_cat_eval['weighted_f1']:.4f}")
    print(f"\nURGENCY ({best_urg_name}):")
    print(f"  Accuracy:         {test_urg_eval['accuracy']:.4f}")
    print(f"  Urgent Recall:    {test_urg_eval['urgent_recall']:.4f}  <-- PRIMARY HEALTHCARE SAFETY METRIC")
    print(f"  Urgent Precision: {test_urg_eval['urgent_precision']:.4f}")
    print(f"  Urgent F1:        {test_urg_eval['urgent_f1']:.4f}")
    print(f"  Routine F1:       {test_urg_eval['routine_f1']:.4f}")
    print(f"  Macro F1:         {test_urg_eval['macro_f1']:.4f}")
    print(f"  Brier Score:      {test_urg_eval['brier_score']}")
    print(f"\nCONFIDENCE & HUMAN REVIEW (Tau = {selected_tau}):")
    print(f"  Human Review Rate: {test_review_rate * 100:.1f}% ({int(np.sum(test_human_review))}/{n_test} cases)")
    print(f"  Routing Coverage:  {test_coverage * 100:.1f}% ({int(np.sum(test_auto_routed))}/{n_test} cases)")
    print(f"  Missed Urgent Cases Auto-Routed: {test_missed_urgent}")

    # Plot Test Confusion Matrices
    ModelEvaluator.plot_confusion_matrix(
        test_cat_eval["confusion_matrix"],
        test_cat_eval["labels"],
        f"Category Test CM ({best_cat_name})",
        str(cm_path / "category_test_cm.png"),
    )
    ModelEvaluator.plot_confusion_matrix(
        test_urg_eval["confusion_matrix"],
        test_urg_eval["labels"],
        f"Urgency Test CM ({best_urg_name})",
        str(cm_path / "urgency_test_cm.png"),
    )

    # 9. Qualitative Error Analysis
    print("\n[8/8] Conducting Qualitative Error Analysis & Artifact Export...")
    error_records = []
    for i in range(n_test):
        cat_err = y_test_cat[i] != test_cat_preds[i]
        urg_err = y_test_urg[i] != test_urg_preds[i]
        if cat_err or urg_err:
            error_records.append({
                "message_id": test_df.iloc[i]["message_id"],
                "text": test_df.iloc[i]["message_text"],
                "actual_category": y_test_cat[i],
                "pred_category": test_cat_preds[i],
                "actual_urgency": y_test_urg[i],
                "pred_urgency": test_urg_preds[i],
                "cat_confidence": round(float(np.max(test_cat_probs[i])), 4),
                "urg_confidence": round(float(np.max(test_urg_probs[i])), 4),
                "overall_confidence": round(float(test_overall_conf[i]), 4),
                "escalated_to_human_review": bool(test_human_review[i]),
            })

    error_df = pd.DataFrame(error_records)
    error_csv_path = reports_path / "error_analysis.csv"
    error_df.to_csv(error_csv_path, index=False)
    print(f"      Recorded {len(error_df)} misclassified test instances to: {error_csv_path}")

    # Feature Explainability Smoke Test
    explainer = FeatureExplainer(
        vectorizer=feature_extractor.vectorizer,
        model=final_cat_model,
        class_labels=test_cat_eval["labels"],
    )
    sample_text = X_test_clean[0]
    sample_vec = X_test_vec[0]
    sample_pred = test_cat_preds[0]
    sample_explanation = explainer.explain_instance(sample_vec, sample_pred, top_k=5)

    # 10. Persist Model Artifacts
    metadata_manifest = {
        "model_version": "v1.0.0",
        "dataset_version": "v1.0.0",
        "training_seed": random_state,
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "sklearn_version": "1.9.1",
        "python_version": "3.14.4",
        "tfidf_parameters": feature_extractor.params,
        "feature_count": feature_extractor.vocabulary_size,
        "category_model": {
            "algorithm": best_cat_name,
            "best_params": grid_search_cat.best_params_,
            "labels": test_cat_eval["labels"],
            "validation_macro_f1": cat_val_metrics[best_cat_name]["macro_f1"],
            "test_macro_f1": test_cat_eval["macro_f1"],
            "test_accuracy": test_cat_eval["accuracy"],
        },
        "urgency_model": {
            "algorithm": best_urg_name,
            "best_params": grid_search_urg.best_params_,
            "labels": test_urg_eval["labels"],
            "validation_urgent_recall": urg_val_metrics[best_urg_name]["urgent_recall"],
            "test_urgent_recall": test_urg_eval["urgent_recall"],
            "test_accuracy": test_urg_eval["accuracy"],
            "test_brier_score": test_urg_eval["brier_score"],
        },
        "confidence_system": {
            "aggregation_formula": "C_overall = min(C_cat, C_urg)",
            "selected_tau": selected_tau,
            "val_human_review_rate": opt_tau_info["metrics"]["human_review_rate"],
            "test_human_review_rate": test_review_rate,
            "test_routing_coverage": test_coverage,
            "test_missed_urgent_auto_routed": test_missed_urgent,
        },
        "sample_explainability": {
            "input_text": sample_text[:80] + "...",
            "predicted_category": sample_pred,
            "top_features": sample_explanation,
        },
    }

    saved_paths = ArtifactManager.save_artifacts(
        base_dir=models_dir,
        version="v1.0.0",
        vectorizer=feature_extractor.vectorizer,
        category_model=final_cat_model,
        urgency_model=final_urg_model,
        metadata=metadata_manifest,
    )
    print(f"      Saved all model artifacts to: {saved_paths['model_directory']}")

    # Save results JSON
    with open(reports_path / "validation_results.json", "w", encoding="utf-8") as f:
        json.dump({"category": val_cat_eval, "urgency": val_urg_eval, "tau_tuning": threshold_evals}, f, indent=2)

    with open(reports_path / "test_results.json", "w", encoding="utf-8") as f:
        json.dump({"category": test_cat_eval, "urgency": test_urg_eval, "confidence": metadata_manifest["confidence_system"]}, f, indent=2)

    print("\n" + "=" * 70)
    print("SECTION 9 EXPERIMENTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

    return {
        "status": "SUCCESS",
        "best_category_model": best_cat_name,
        "best_urgency_model": best_urg_name,
        "selected_tau": selected_tau,
        "test_cat_macro_f1": test_cat_eval["macro_f1"],
        "test_urg_urgent_recall": test_urg_eval["urgent_recall"],
        "test_human_review_rate": test_review_rate,
        "saved_paths": saved_paths,
    }


if __name__ == "__main__":
    run_experiments()
