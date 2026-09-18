"""Candidate model definitions and hyperparameter search grids for Category and Urgency.
"""

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB


def get_candidate_models(random_state: int = 42):
    """Returns baseline instances of the 3 candidate algorithms for Category and Urgency."""
    category_candidates = {
        "LogisticRegression": LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=random_state,
        ),
        "LinearSVC": LinearSVC(
            C=1.0,
            max_iter=2000,
            class_weight="balanced",
            random_state=random_state,
        ),
        "MultinomialNB": MultinomialNB(
            alpha=0.1,
        ),
    }

    urgency_candidates = {
        "LogisticRegression": LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=random_state,
        ),
        "LinearSVC": LinearSVC(
            C=1.0,
            max_iter=2000,
            class_weight="balanced",
            random_state=random_state,
        ),
        "MultinomialNB": MultinomialNB(
            alpha=0.1,
        ),
    }

    return category_candidates, urgency_candidates


def get_hyperparameter_grids():
    """Returns lightweight search grids for 5-fold cross-validation tuning."""
    grids = {
        "LogisticRegression": {
            "C": [1.0, 2.0, 0.5, 5.0, 0.1],
            "class_weight": ["balanced", None],
        },
        "LinearSVC": {
            "C": [1.0, 0.5, 0.1, 2.0, 0.05],
            "class_weight": ["balanced", None],
        },
        "MultinomialNB": {
            "alpha": [0.1, 0.05, 0.01, 0.5, 1.0],
        },
    }
    return grids
