"""Unit tests for confidence scoring, bottleneck aggregation, and threshold selection.
"""

import numpy as np
import pytest
from src.ml.confidence import ConfidenceManager


def test_individual_confidence():
    probs = np.array([
        [0.1, 0.7, 0.2],
        [0.85, 0.10, 0.05],
    ])
    conf = ConfidenceManager.compute_individual_confidence(probs)
    assert np.allclose(conf, [0.7, 0.85])


def test_overall_confidence_bottleneck():
    cat_probs = np.array([
        [0.9, 0.1],  # cat conf = 0.90
        [0.6, 0.4],  # cat conf = 0.60
    ])
    urg_probs = np.array([
        [0.55, 0.45],  # urg conf = 0.55
        [0.95, 0.05],  # urg conf = 0.95
    ])

    overall = ConfidenceManager.compute_overall_confidence(cat_probs, urg_probs)
    # Conservative bottleneck aggregation: min(0.9, 0.55) = 0.55; min(0.6, 0.95) = 0.60
    assert np.allclose(overall, [0.55, 0.60])


def test_evaluate_threshold_grid():
    overall_conf = np.array([0.65, 0.75, 0.85, 0.92])
    y_true = ["Routine", "Urgent", "Routine", "Urgent"]
    y_pred = ["Routine", "Urgent", "Routine", "Urgent"]

    grid = ConfidenceManager.evaluate_threshold_grid(
        overall_conf,
        y_true,
        y_pred,
        tau_range=(0.70, 0.80),
        step=0.05,
    )

    assert len(grid) == 3
    # At tau = 0.70: 3 cases >= 0.70 (0.75, 0.85, 0.92) -> auto_routed = 3, review = 1
    assert grid[0]["tau"] == 0.70
    assert grid[0]["auto_routed_count"] == 3
    assert grid[0]["human_review_count"] == 1
    assert grid[0]["missed_urgent_auto_routed"] == 0


def test_select_optimal_tau_sla_policy():
    evals = [
        {"tau": 0.60, "routing_coverage": 0.95, "human_review_rate": 0.05, "missed_urgent_auto_routed": 0},
        {"tau": 0.70, "routing_coverage": 0.80, "human_review_rate": 0.20, "missed_urgent_auto_routed": 0},
        {"tau": 0.80, "routing_coverage": 0.60, "human_review_rate": 0.40, "missed_urgent_auto_routed": 0},
    ]

    opt = ConfidenceManager.select_optimal_tau(evals, max_review_rate=0.25)
    # Tau 0.60 (rev 0.05) and Tau 0.70 (rev 0.20) meet <= 0.25 budget; max conservative tau is 0.70
    assert opt["selected_tau"] == 0.70
    assert opt["metrics"]["human_review_rate"] == 0.20
