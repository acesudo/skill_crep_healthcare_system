"""
Patient-facing triage result component.
Renders clean, modern, patient-friendly outcome cards with clear operational
urgency, urgency confidence, recommended routing, and human-review states.
Strictly adheres to healthcare safety: operational classification only, never clinical diagnoses.
"""

import streamlit as st
from typing import Dict, Any


def render_triage_result_card(prediction: Dict[str, Any]):
    """
    Renders modern patient-facing result cards answering:
    1. What type of request is this? (Operational Category)
    2. Is it operationally ROUTINE or URGENT?
    3. How confident is the urgency classification?
    4. Where should this request be routed?
    5. Does it require human review?
    """
    category = prediction.get("predicted_category", "General Inquiry")
    urgency = str(prediction.get("predicted_urgency", "Routine")).upper()
    urg_conf = float(prediction.get("urgency_confidence", 0.0))
    overall_conf = float(prediction.get("overall_confidence", 0.0))
    queue = prediction.get("assigned_queue", "Front Desk / General Queue")
    requires_review = prediction.get("requires_human_review", False)
    status = prediction.get("status", "SUCCESS")
    is_urgent = urgency == "URGENT"

    urg_pct = f"{urg_conf * 100:.0f}%"
    overall_pct = f"{overall_conf * 100:.0f}%"

    # 1. State: Low Confidence / Human Review Required
    if requires_review or status == "LOW_CONFIDENCE" or overall_conf < 0.70:
        st.markdown(
            f"""
            <div style="background-color: #FFFBEB; border: 1px solid #FCD34D; border-radius: 12px; padding: 24px; margin-top: 16px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <span style="font-size: 20px;">⚠️</span>
                    <span style="font-size: 13px; font-weight: 700; letter-spacing: 0.05em; color: #B45309; text-transform: uppercase;">
                        Human Review Required
                    </span>
                </div>
                <h3 style="color: #92400E; margin: 0 0 8px 0; font-size: 1.25rem;">
                    Routed for Manual Staff Confirmation
                </h3>
                <p style="color: #78350F; font-size: 0.95rem; margin: 0 0 16px 0; line-height: 1.5;">
                    This message could not be classified with sufficient confidence for automatic operational routing. 
                    A healthcare staff member will review your request directly.
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; background-color: #FFFFFF; padding: 16px; border-radius: 8px; border: 1px solid #FDE68A;">
                    <div>
                        <div style="font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase;">Identified Category</div>
                        <div style="font-size: 16px; color: #1F2937; font-weight: 600; margin-top: 2px;">{category}</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase;">Operational Urgency</div>
                        <div style="font-size: 16px; color: #B45309; font-weight: 600; margin-top: 2px;">Review Pending</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase;">Recommended Destination</div>
                        <div style="font-size: 16px; color: #1E3A8A; font-weight: 700; margin-top: 2px;">📋 {queue}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # 2. State: Urgent Operational Request
    if is_urgent:
        st.markdown(
            f"""
            <div style="background-color: #FEF2F2; border: 1px solid #FCA5A5; border-radius: 12px; padding: 24px; margin-top: 16px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 20px;">🚨</span>
                        <span style="font-size: 13px; font-weight: 700; letter-spacing: 0.05em; color: #DC2626; text-transform: uppercase;">
                            Urgent Operational Review
                        </span>
                    </div>
                    <span style="background-color: #EF4444; color: white; padding: 3px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700;">
                        URGENT
                    </span>
                </div>
                <h2 style="color: #991B1B; margin: 0 0 6px 0; font-size: 1.4rem;">
                    Operationally Classified as URGENT
                </h2>
                <p style="color: #7F1D1D; font-size: 0.95rem; margin: 0 0 20px 0;">
                    This inquiry has been flagged for priority operational attention by the triage switchboard.
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; background-color: #FFFFFF; padding: 18px; border-radius: 8px; border: 1px solid #FECACA;">
                    <div>
                        <div style="font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase;">Request Category</div>
                        <div style="font-size: 17px; color: #111827; font-weight: 700; margin-top: 2px;">{category}</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase;">Urgency Confidence</div>
                        <div style="font-size: 17px; color: #DC2626; font-weight: 700; margin-top: 2px;">{urg_pct}</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase;">Routing Confidence</div>
                        <div style="font-size: 17px; color: #4B5563; font-weight: 600; margin-top: 2px;">{overall_pct}</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase;">Where should this go?</div>
                        <div style="font-size: 17px; color: #991B1B; font-weight: 800; margin-top: 2px;">📋 {queue}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # 3. State: Routine Operational Request
    st.markdown(
        f"""
        <div style="background-color: #F0FDF4; border: 1px solid #86EFAC; border-radius: 12px; padding: 24px; margin-top: 16px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 20px;">✅</span>
                    <span style="font-size: 13px; font-weight: 700; letter-spacing: 0.05em; color: #16A34A; text-transform: uppercase;">
                        Routine Operational Request
                    </span>
                </div>
                <span style="background-color: #22C55E; color: white; padding: 3px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700;">
                    ROUTINE
                </span>
            </div>
            <h2 style="color: #166534; margin: 0 0 6px 0; font-size: 1.4rem;">
                Operationally Classified as ROUTINE
            </h2>
            <p style="color: #14532D; font-size: 0.95rem; margin: 0 0 20px 0;">
                Standard administrative request routed to appropriate healthcare coordination department.
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; background-color: #FFFFFF; padding: 18px; border-radius: 8px; border: 1px solid #BBF7D0;">
                <div>
                    <div style="font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase;">Request Category</div>
                    <div style="font-size: 17px; color: #111827; font-weight: 700; margin-top: 2px;">{category}</div>
                </div>
                <div>
                    <div style="font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase;">Urgency Confidence</div>
                    <div style="font-size: 17px; color: #16A34A; font-weight: 700; margin-top: 2px;">{urg_pct}</div>
                </div>
                <div>
                    <div style="font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase;">Routing Confidence</div>
                    <div style="font-size: 17px; color: #4B5563; font-weight: 600; margin-top: 2px;">{overall_pct}</div>
                </div>
                <div>
                    <div style="font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase;">Where should this go?</div>
                    <div style="font-size: 17px; color: #1E3A8A; font-weight: 800; margin-top: 2px;">📋 {queue}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
