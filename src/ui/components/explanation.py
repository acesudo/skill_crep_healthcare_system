"""
Feature attribution explanation component for Streamlit dashboard.
Visualizes top contributing words for Category and Urgency predictions as returned by FastAPI.
Supports both schema variations (dict of items or list of FeatureContribution objects).
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List


def render_feature_explanations(explanation_data: Any):
    """
    Renders feature contribution tables for Category and Urgency.
    Values represent linear contribution x_j * W_{k, j} calculated in FastAPI backend.
    """
    if not explanation_data:
        st.info("No feature explanation data available for this prediction.")
        return

    st.markdown("#### ?? Model Explainability & Token Contributions")
    st.caption("Top linguistic tokens driving the model's operational decision (linear feature contribution):")

    cat_rows: List[Dict[str, Any]] = []
    urg_rows: List[Dict[str, Any]] = []

    # Handle if explanation_data has category_features / urgency_features (FastAPI schema)
    if isinstance(explanation_data, dict):
        # Format A: {"category_features": [{"feature": "x", "contribution": 0.5}]}
        if "category_features" in explanation_data:
            for item in explanation_data.get("category_features", []):
                if isinstance(item, dict):
                    cat_rows.append({
                        "Token / Feature": item.get("feature", ""),
                        "Contribution Score": round(float(item.get("contribution", 0.0)), 4)
                    })
        elif "category_top_features" in explanation_data:
            top_feats = explanation_data.get("category_top_features") or {}
            for k, v in top_feats.items():
                cat_rows.append({"Token / Feature": k, "Contribution Score": round(float(v), 4)})

        if "urgency_features" in explanation_data:
            for item in explanation_data.get("urgency_features", []):
                if isinstance(item, dict):
                    urg_rows.append({
                        "Token / Feature": item.get("feature", ""),
                        "Contribution Score": round(float(item.get("contribution", 0.0)), 4)
                    })
        elif "urgency_top_features" in explanation_data:
            top_feats = explanation_data.get("urgency_top_features") or {}
            for k, v in top_feats.items():
                urg_rows.append({"Token / Feature": k, "Contribution Score": round(float(v), 4)})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Category Attributions**")
        if cat_rows:
            cat_df = pd.DataFrame(cat_rows).sort_values(by="Contribution Score", ascending=False)
            st.dataframe(cat_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No significant category features identified.")

    with col2:
        st.markdown("**Urgency Attributions**")
        if urg_rows:
            urg_df = pd.DataFrame(urg_rows).sort_values(by="Contribution Score", ascending=False)
            st.dataframe(urg_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No significant urgency features identified.")
