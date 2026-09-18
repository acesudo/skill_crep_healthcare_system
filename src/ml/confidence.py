"""Confidence scoring, joint aggregation, and validation threshold optimization.
"""

from typing import Dict, List, Tuple
import numpy as np


class ConfidenceManager:
    """Computes individual model confidence, applies conservative bottleneck aggregation,
    and conducts grid search for operational threshold tau on validation data.
    """

    @staticmethod
    def compute_individual_confidence(probs: np.ndarray) -> np.ndarray:
        """Returns the maximum class probability per prediction vector."""
        return np.max(probs, axis=1)

    @staticmethod
    def compute_overall_confidence(cat_probs: np.ndarray, urg_probs: np.ndarray) -> np.ndarray:
        """Computes joint operational confidence: C_overall = min(C_cat, C_urg).
        Enforces conservative bottleneck aggregation: ambiguity on either dimension triggers review.
        """
        c_cat = np.max(cat_probs, axis=1)
        c_urg = np.max(urg_probs, axis=1)
        return np.minimum(c_cat, c_urg)

    @classmethod
    def evaluate_threshold_grid(
        cls,
        overall_confidences: np.ndarray,
        y_true_urgency: List[str],
        y_pred_urgency: List[str],
        tau_range: Tuple[float, float] = (0.60, 0.90),
        step: float = 0.02,
    ) -> List[Dict[str, any]]:
        """Evaluates operational metrics across candidate threshold values tau on VALIDATION data."""
        results = []
        n_total = len(overall_confidences)
        taus = np.arange(tau_range[0], tau_range[1] + 1e-5, step)

        for tau in taus:
            tau = round(float(tau), 4)
            # High confidence mask (auto-routed)
            auto_routed_mask = overall_confidences >= tau
            human_review_mask = overall_confidences < tau

            n_auto_routed = int(np.sum(auto_routed_mask))
            n_human_review = int(np.sum(human_review_mask))

            routing_coverage = round(n_auto_routed / n_total, 4)
            human_review_rate = round(n_human_review / n_total, 4)

            # Check false negatives among auto-routed cases
            # A false negative is when an Urgent case is predicted Routine and auto-routed!
            auto_true = [y_true_urgency[i] for i in range(n_total) if auto_routed_mask[i]]
            auto_pred = [y_pred_urgency[i] for i in range(n_total) if auto_routed_mask[i]]

            missed_urgents = sum(1 for t, p in zip(auto_true, auto_pred) if t == "Urgent" and p == "Routine")
            total_urgents = sum(1 for t in y_true_urgency if t == "Urgent")
            
            # Urgent Recall preserved under auto-routing
            auto_urgent_caught = sum(1 for t, p in zip(auto_true, auto_pred) if t == "Urgent" and p == "Urgent")
            effective_auto_urgent_recall = round(auto_urgent_caught / total_urgents, 4) if total_urgents > 0 else 1.0

            results.append({
                "tau": tau,
                "routing_coverage": routing_coverage,
                "human_review_rate": human_review_rate,
                "auto_routed_count": n_auto_routed,
                "human_review_count": n_human_review,
                "missed_urgent_auto_routed": missed_urgents,
                "total_urgents": total_urgents,
            })

        return results

    @classmethod
    def select_optimal_tau(
        cls,
        threshold_evals: List[Dict[str, any]],
        max_review_rate: float = 0.25,
    ) -> Dict[str, any]:
        """Selects optimal operational threshold balancing zero missed urgent cases with SLA review volume.
        Policy (Section 7.12.2):
        1. 100% Urgent Recall on validation (zero missed urgent cases auto-routed).
        2. Routing coverage >= 75% (human review rate <= 25%).
        3. Maximize tau within the feasible set to ensure conservative safety gating.
        """
        # Candidates achieving zero missed urgent cases and conforming to review budget
        eligible = [
            r for r in threshold_evals
            if r["missed_urgent_auto_routed"] == 0 and r["human_review_rate"] <= max_review_rate
        ]

        if eligible:
            # Safest conservative threshold within acceptable SLA review capacity
            best = max(eligible, key=lambda x: x["tau"])
            reason = f"Selected maximum safe threshold ({best['tau']}) achieving 0 missed urgent cases with human review rate ({best['human_review_rate']*100:.1f}%) <= {max_review_rate*100:.0f}% SLA capacity."
        else:
            # Fallback 1: Any zero missed urgents, pick minimum review rate
            zero_miss = [r for r in threshold_evals if r["missed_urgent_auto_routed"] == 0]
            if zero_miss:
                best = min(zero_miss, key=lambda x: x["human_review_rate"])
                reason = f"Fallback: Selected zero-miss threshold ({best['tau']}) minimizing human review rate ({best['human_review_rate']*100:.1f}%)."
            else:
                best = min(threshold_evals, key=lambda x: (x["missed_urgent_auto_routed"], x["human_review_rate"]))
                reason = f"Fallback: Selected threshold ({best['tau']}) minimizing missed urgent cases."

        return {
            "selected_tau": best["tau"],
            "metrics": best,
            "selection_reason": reason,
        }
