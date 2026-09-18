"""
Review queue component for Streamlit dashboard.
Displays low-confidence and escalated cases captured in session state.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any


def render_review_queue(review_cases: List[Dict[str, Any]]):
    """
    Renders the session-scoped human review queue.
    Allows hospital staff to inspect, filter, and clear pending human review cases.
    """
    st.markdown("### ?? Session Human Review Queue")
    st.caption(
        "Cases automatically routed here due to confidence below operational threshold (tau = 0.70) "
        "or validation anomalies. (Note: MVP review queue is session-scoped)."
    )

    if not review_cases:
        st.success("? The human review queue is currently empty! All incoming cases have met confidence criteria.")
        return

    st.markdown(f"**Total Cases Pending Review:** `{len(review_cases)}`")

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("??? Clear Review Queue", type="secondary"):
            st.session_state["review_queue"] = []
            st.rerun()

    # Convert cases to DataFrame for inspection
    display_rows = []
    for idx, case in enumerate(review_cases):
        display_rows.append({
            "Queue ID": f"REV-{idx+1:03d}",
            "Message ID": case.get("message_id", f"MSG-{idx+1:03d}"),
            "Message Snippet": (case.get("text", "")[:60] + "...") if len(case.get("text", "")) > 60 else case.get("text", ""),
            "Candidate Category": case.get("predicted_category", "N/A"),
            "Candidate Urgency": case.get("predicted_urgency", "N/A"),
            "Overall Conf": f"{case.get('overall_confidence', 0.0) * 100:.1f}%",
            "Cat Conf": f"{case.get('category_confidence', 0.0) * 100:.1f}%",
            "Urg Conf": f"{case.get('urgency_confidence', 0.0) * 100:.1f}%",
            "Assigned Queue": case.get("assigned_queue", "N/A"),
            "Status": case.get("status", "LOW_CONFIDENCE"),
        })

    df = pd.DataFrame(display_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Detailed inspection expander
    with st.expander("?? Inspect Full Case Details & Features"):
        selected_idx = st.selectbox(
            "Select Case to Inspect:",
            options=range(len(review_cases)),
            format_func=lambda i: f"REV-{i+1:03d} | {review_cases[i].get('predicted_category')} | Conf: {review_cases[i].get('overall_confidence', 0.0)*100:.1f}%"
        )
        if selected_idx is not None and 0 <= selected_idx < len(review_cases):
            selected = review_cases[selected_idx]
            st.markdown(f"**Full Message Text:**")
            st.info(selected.get("text", ""))
            st.json(selected)
