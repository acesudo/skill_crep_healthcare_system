"""
Batch results component for Streamlit dashboard.
Displays summary cards, interactive table, and CSV export for batch triage.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any


def render_batch_results(batch_response: Dict[str, Any]):
    """
    Renders batch triage results received from FastAPI POST /predict/batch.
    Provides operational summary cards, an interactive table, and export options.
    """
    total = batch_response.get("total_records", 0)
    successful = batch_response.get("successful_records", 0)
    low_conf = batch_response.get("low_confidence_records", 0)
    invalid = batch_response.get("invalid_records", 0)
    results = batch_response.get("results", [])

    st.markdown("### 📊 Batch Triage Summary")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Submitted", total)
    with col2:
        st.metric("Standard Routed", successful, help="Confidence >= 0.70")
    with col3:
        st.metric("Human Review Required", low_conf, help="Routed to Human Review Queue")
    with col4:
        st.metric("Invalid Records", invalid, help="Blank / Malformed rows")

    if not results:
        st.info("No items in batch results to display.")
        return

    st.markdown("---")
    st.markdown("#### Batch Results")

    # Build clean DataFrame
    rows = []
    for r in results:
        urg_conf = r.get("urgency_confidence")
        overall_conf = r.get("overall_confidence")
        rows.append({
            "Row": r.get("row_index"),
            "Message ID": r.get("message_id"),
            "Status": r.get("status"),
            "Operational Category": r.get("predicted_category") or "N/A",
            "Operational Urgency": r.get("predicted_urgency") or "N/A",
            "Urgency Confidence": f"{float(urg_conf) * 100:.0f}%" if urg_conf is not None else "N/A",
            "Routing Confidence": f"{float(overall_conf) * 100:.0f}%" if overall_conf is not None else "N/A",
            "Recommended Route": r.get("assigned_queue") or "N/A",
            "Human Review": "⚠️ YES" if r.get("requires_human_review") else "NO",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Export to CSV
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Results (CSV)",
        data=csv_bytes,
        file_name="patient_triage_batch_results.csv",
        mime="text/csv",
        type="primary",
    )
