"""
Session-scoped conversation history component.
Displays prior user inquiries and assistant triage results in a clean,
lightweight conversational thread.
"""

import streamlit as st
from typing import List, Dict, Any


def render_conversation_history(history: List[Dict[str, Any]]):
    """Renders prior turns from session state in a conversational bubble format."""
    if not history:
        return

    st.markdown("---")
    st.markdown("### 💬 Recent Inquiries in this Session")
    st.caption("Lightweight session history. (No records are permanently stored).")

    for idx, turn in enumerate(reversed(history)):
        user_msg = turn.get("user_message", "")
        pred = turn.get("prediction", {})
        cat = pred.get("predicted_category", "General")
        urg = str(pred.get("predicted_urgency", "Routine")).upper()
        urg_conf = float(pred.get("urgency_confidence", 0.0))
        queue = pred.get("assigned_queue", "Front Desk")
        rev = pred.get("requires_human_review", False)

        badge_color = "#DC2626" if urg == "URGENT" else "#16A34A"
        if rev:
            badge_color = "#B45309"
            urg_label = "REVIEW PENDING"
        else:
            urg_label = urg

        with st.container():
            st.markdown(
                f"""
                <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px 18px; margin-bottom: 12px;">
                    <div style="font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 4px;">
                        👤 Patient Inquiry:
                    </div>
                    <div style="font-size: 14.5px; color: #0F172A; margin-bottom: 10px; font-style: italic;">
                        "{user_msg}"
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 12px; font-size: 13px; border-top: 1px solid #E2E8F0; padding-top: 8px;">
                        <span><strong>Category:</strong> {cat}</span>
                        <span><strong>Operational Urgency:</strong> <span style="color: {badge_color}; font-weight: 700;">{urg_label}</span></span>
                        <span><strong>Urgency Confidence:</strong> {urg_conf * 100:.0f}%</span>
                        <span><strong>Route:</strong> 📋 {queue}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
