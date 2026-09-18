"""
Status cards component for Streamlit dashboard.
Displays live backend connectivity, health, readiness, and model metadata.
"""

import streamlit as st
from typing import Dict, Any, Optional


def render_backend_status_card(health_data: Optional[Dict[str, Any]], ready_data: Optional[Dict[str, Any]]):
    """Renders backend connectivity and operational health indicators."""
    col1, col2, col3 = st.columns(3)

    with col1:
        if health_data and health_data.get("success"):
            data = health_data.get("data", {})
            st.metric(
                label="API Connectivity",
                value="ONLINE ??",
                delta=f"Status: {data.get('status', 'ok')}",
            )
        else:
            err = health_data.get("error", "Unknown error") if health_data else "Offline"
            st.metric(
                label="API Connectivity",
                value="OFFLINE ??",
                delta=err[:25] if len(err) > 25 else err,
                delta_color="inverse",
            )

    with col2:
        if ready_data and ready_data.get("success"):
            data = ready_data.get("data", {})
            status = data.get("status", "unknown")
            is_ready = status == "ready"
            st.metric(
                label="Model Readiness",
                value="READY ??" if is_ready else "NOT READY ??",
                delta="Artifacts Loaded" if is_ready else "Check Artifacts",
            )
        else:
            st.metric(
                label="Model Readiness",
                value="UNAVAILABLE ?",
                delta="Backend Unreachable",
                delta_color="off",
            )

    with col3:
        if ready_data and ready_data.get("success"):
            data = ready_data.get("data", {})
            st.metric(
                label="Active Model Version",
                value=data.get("model_version", "v1.0.0"),
                delta=f"Data: {data.get('dataset_version', 'v1.0.0')}",
            )
        else:
            st.metric(
                label="Active Model Version",
                value="Unknown",
                delta="None",
                delta_color="off",
            )


def render_operational_overview(model_info_data: Optional[Dict[str, Any]]):
    """Renders operational configuration parameters including threshold and active classes."""
    if not model_info_data or not model_info_data.get("success"):
        st.info("?? Connect to FastAPI backend to view active operational parameters.")
        return

    data = model_info_data.get("data", {})
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Confidence Threshold (tau)",
            value=f"{data.get('threshold', 0.70):.2f}",
            help="Cases with confidence below this threshold require human review.",
        )
    with col2:
        categories = data.get("category_labels", [])
        st.metric(
            label="Operational Categories",
            value=len(categories),
            help=", ".join(categories),
        )
    with col3:
        urgencies = data.get("urgency_labels", [])
        st.metric(
            label="Urgency Levels",
            value=len(urgencies),
            help=", ".join(urgencies),
        )
    with col4:
        st.metric(
            label="Confidence Bottleneck",
            value="min(C_cat, C_urg)",
            help="Conservative joint confidence metric ensuring high safety.",
        )
