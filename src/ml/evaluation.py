"""Evaluation metrics, calibration assessment, and visualization utilities for PS-1 ML models.
"""

from pathlib import Path
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


class ModelEvaluator:
    """Computes comprehensive classification metrics and renders confusion matrix plots."""

    @staticmethod
    def evaluate_category(
        y_true: List[str],
        y_pred: List[str],
        labels: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """Calculates multi-class metrics for operational category classification."""
        if labels is None:
            labels = sorted(list(set(y_true)))

        acc = accuracy_score(y_true, y_pred)
        macro_p = precision_score(y_true, y_pred, average="macro", zero_division=0)
        macro_r = recall_score(y_true, y_pred, average="macro", zero_division=0)
        macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
        weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

        # Per-class metrics
        per_class = {}
        for label in labels:
            y_t_binary = [1 if y == label else 0 for y in y_true]
            y_p_binary = [1 if y == label else 0 for y in y_pred]
            per_class[label] = {
                "precision": round(float(precision_score(y_t_binary, y_p_binary, zero_division=0)), 4),
                "recall": round(float(recall_score(y_t_binary, y_p_binary, zero_division=0)), 4),
                "f1": round(float(f1_score(y_t_binary, y_p_binary, zero_division=0)), 4),
                "support": int(sum(y_t_binary)),
            }

        cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()

        return {
            "accuracy": round(float(acc), 4),
            "macro_precision": round(float(macro_p), 4),
            "macro_recall": round(float(macro_r), 4),
            "macro_f1": round(float(macro_f1), 4),
            "weighted_f1": round(float(weighted_f1), 4),
            "per_class": per_class,
            "confusion_matrix": cm,
            "labels": labels,
        }

    @staticmethod
    def evaluate_urgency(
        y_true: List[str],
        y_pred: List[str],
        y_probs: Optional[np.ndarray] = None,
        labels: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """Calculates binary metrics for operational urgency, emphasizing Urgent Recall."""
        if labels is None:
            labels = ["Routine", "Urgent"]

        acc = accuracy_score(y_true, y_pred)
        macro_p = precision_score(y_true, y_pred, average="macro", zero_division=0)
        macro_r = recall_score(y_true, y_pred, average="macro", zero_division=0)
        macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
        weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

        # Urgent class specific (Healthcare safety priority)
        y_t_urg = [1 if y == "Urgent" else 0 for y in y_true]
        y_p_urg = [1 if y == "Urgent" else 0 for y in y_pred]
        urgent_recall = recall_score(y_t_urg, y_p_urg, zero_division=0)
        urgent_precision = precision_score(y_t_urg, y_p_urg, zero_division=0)
        urgent_f1 = f1_score(y_t_urg, y_p_urg, zero_division=0)

        # Routine class specific
        y_t_rout = [1 if y == "Routine" else 0 for y in y_true]
        y_p_rout = [1 if y == "Routine" else 0 for y in y_pred]
        routine_recall = recall_score(y_t_rout, y_p_rout, zero_division=0)
        routine_precision = precision_score(y_t_rout, y_p_rout, zero_division=0)
        routine_f1 = f1_score(y_t_rout, y_p_rout, zero_division=0)

        cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()

        # Calibration assessment via Brier Score if probabilities provided
        brier = None
        if y_probs is not None:
            try:
                # Urgent probability column index
                urg_idx = labels.index("Urgent")
                urg_probs = y_probs[:, urg_idx]
                brier = round(float(brier_score_loss(y_t_urg, urg_probs)), 4)
            except Exception:
                brier = None

        return {
            "accuracy": round(float(acc), 4),
            "macro_precision": round(float(macro_p), 4),
            "macro_recall": round(float(macro_r), 4),
            "macro_f1": round(float(macro_f1), 4),
            "weighted_f1": round(float(weighted_f1), 4),
            "urgent_recall": round(float(urgent_recall), 4),
            "urgent_precision": round(float(urgent_precision), 4),
            "urgent_f1": round(float(urgent_f1), 4),
            "routine_recall": round(float(routine_recall), 4),
            "routine_precision": round(float(routine_precision), 4),
            "routine_f1": round(float(routine_f1), 4),
            "brier_score": brier,
            "confusion_matrix": cm,
            "labels": labels,
        }

    @staticmethod
    def plot_confusion_matrix(
        cm: List[List[int]],
        labels: List[str],
        title: str,
        output_filepath: str,
    ) -> None:
        """Plots and saves a clean, legible confusion matrix using Matplotlib."""
        Path(output_filepath).parent.mkdir(parents=True, exist_ok=True)
        cm_array = np.array(cm)

        fig, ax = plt.subplots(figsize=(7, 6))
        im = ax.imshow(cm_array, interpolation="nearest", cmap=plt.cm.Blues)
        ax.figure.colorbar(im, ax=ax)

        ax.set(
            xticks=np.arange(cm_array.shape[1]),
            yticks=np.arange(cm_array.shape[0]),
            xticklabels=labels,
            yticklabels=labels,
            title=title,
            ylabel="Actual Ground Truth",
            xlabel="Model Predicted Label",
        )

        plt.setp(ax.get_xticklabels(), rotation=35, ha="right", rotation_mode="anchor")

        # Loop over data dimensions and create text annotations
        thresh = cm_array.max() / 2.0
        for i in range(cm_array.shape[0]):
            for j in range(cm_array.shape[1]):
                ax.text(
                    j,
                    i,
                    format(cm_array[i, j], "d"),
                    ha="center",
                    va="center",
                    color="white" if cm_array[i, j] > thresh else "black",
                    fontsize=11,
                    fontweight="bold",
                )

        fig.tight_layout()
        plt.savefig(output_filepath, dpi=200)
        plt.close(fig)
