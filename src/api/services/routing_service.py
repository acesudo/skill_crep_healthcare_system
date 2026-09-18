"""Deterministic operational routing service for PS-1.
Maps predicted category and urgency to approved operational department queues,
enforcing human review escalation for low-confidence or high-risk cases.
"""

from typing import Dict


class RoutingService:
    """Deterministic routing matrix based on confirmed project specifications (Section 4 & Section 8).
    NO generative LLM or heuristic guessing is permitted in the routing path.
    """

    CATEGORY_TO_QUEUE: Dict[str, str] = {
        "Appointment": "Front Desk / Appointment Queue",
        "Billing": "Billing Department Queue",
        "Medication Refill": "Medication / Refill Workflow Queue",
        "Report Request": "Medical Records / Reports Queue",
        "Technical Issue": "Technical Support Queue",
        "Urgent Review": "Urgent Review Queue",
    }

    HUMAN_REVIEW_QUEUE: str = "Human Review Queue"
    DEFAULT_FALLBACK_QUEUE: str = "General Operational Triage Queue"

    def route(
        self,
        predicted_category: str,
        predicted_urgency: str,
        requires_human_review: bool,
    ) -> str:
        """Determines the operational destination queue for an inquiry.
        
        If requires_human_review is True, the case is strictly routed to the Human Review Queue
        to ensure human-in-the-loop oversight before staff action.
        Otherwise, deterministic mapping to functional departmental queue is applied.
        """
        if requires_human_review:
            return self.HUMAN_REVIEW_QUEUE

        return self.CATEGORY_TO_QUEUE.get(predicted_category, self.DEFAULT_FALLBACK_QUEUE)

    def get_department_queue(self, category: str) -> str:
        """Returns the nominal departmental queue for a given category regardless of review status."""
        return self.CATEGORY_TO_QUEUE.get(category, self.DEFAULT_FALLBACK_QUEUE)
