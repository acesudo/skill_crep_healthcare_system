"""
Header and safety banner UI component for Streamlit dashboard.
Redesigned for Section 13: Light, clean, patient-friendly presentation.
Strictly adheres to Healthcare Safety Boundary: Operational decision support only.
"""

import streamlit as st


def render_header():
    """Renders the top-level patient-facing title and concise operational subtitle."""
    st.markdown(
        """
        <div style="padding-top: 0.5rem; padding-bottom: 0.8rem; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.2rem;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 2rem;">🏥</span>
                <div>
                    <h1 style="margin: 0; font-size: 1.85rem; font-weight: 700; color: #1E3A8A; letter-spacing: -0.02em;">
                        Patient Triage Assistant
                    </h1>
                    <p style="font-size: 0.98rem; color: #4B5563; margin: 2px 0 0 0;">
                        Describe your request and we'll identify the operational urgency and the appropriate routing destination.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_safety_disclaimer():
    """Renders a concise, non-intrusive operational safety boundary disclaimer."""
    st.info(
        "ℹ️ **Operational Notice:** This tool classifies patient-support messages for operational routing "
        "and prioritization. It does not provide medical diagnosis, treatment recommendations, or replace clinical triage.",
        icon="ℹ️",
    )
