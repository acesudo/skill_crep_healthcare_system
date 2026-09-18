"""

Prediction result component for Streamlit dashboard.

Displays operational triage results, confidence scores, assigned queue, and human review flags.

"""



import streamlit as st

from typing import Dict, Any





def render_prediction_result(prediction: Dict[str, Any]):

    """

    Renders structured triage results received from FastAPI POST /predict.

    Follows healthcare operational terminology: "Operationally classified as Routine/Urgent".

    """

    status = prediction.get("status", "UNKNOWN")

    cat = prediction.get("predicted_category", "N/A")

    urg = prediction.get("predicted_urgency", "N/A")

    c_overall = prediction.get("overall_confidence", 0.0)

    c_cat = prediction.get("category_confidence", 0.0)

    c_urg = prediction.get("urgency_confidence", 0.0)

    queue = prediction.get("assigned_queue", "N/A")

    human_review = prediction.get("requires_human_review", False)

    msg_id = prediction.get("message_id", "N/A")



    # Status banner & styling

    if status == "SUCCESS" and not human_review:

        st.success(f"### Status: {status} (Standard Operational Routing)", icon="⚠️")

    elif status == "LOW_CONFIDENCE" or human_review:

        st.warning(f"### Status: {status} â€” Human Review Required", icon="⚠️")

    elif status == "INVALID_INPUT":

        st.error(f"### Status: {status} â€” Invalid Input Message", icon="⚠️")

    else:

        st.error(f"### Status: {status} â€” Processing Issue", icon="⚠️")



    # Primary Operational Decision Cards

    col1, col2, col3 = st.columns(3)



    with col1:

        st.markdown("**Operational Category**")

        st.markdown(f"### `{cat}`")

        st.caption(f"Category Confidence: **{c_cat * 100:.1f}%**")

        st.progress(max(0.0, min(1.0, float(c_cat))))



    with col2:

        st.markdown("**Operational Urgency**")

        urg_badge = "?? URGENT" if str(urg).lower() == "urgent" else "?? ROUTINE"

        st.markdown(f"### {urg_badge}")

        st.caption(f"Urgency Confidence: **{c_urg * 100:.1f}%**")

        st.progress(max(0.0, min(1.0, float(c_urg))))



    with col3:

        st.markdown("**Assigned Target Queue**")

        st.markdown(f"### ?? `{queue}`")

        st.caption(f"Overall Confidence: **{c_overall * 100:.1f}%**")

        st.progress(max(0.0, min(1.0, float(c_overall))))



    # Detailed Decision Summary Table / Callouts

    st.markdown("---")

    st.markdown("#### Routing & Workflow Decision")



    detail_col1, detail_col2 = st.columns([3, 1])



    with detail_col1:

        if human_review:

            st.error(

                f"?? **ACTION REQUIRED:** Message `{msg_id}` has been automatically routed to **Human Review Queue** "

                f"because joint confidence ({c_overall*100:.1f}%) is below operational threshold (tau = 0.70).",

                icon="⚠️",

            )

        else:

            st.info(

                f"? Operationally classified as **{urg}** `{cat}` and routed directly to **{queue}** for staff processing.",

                icon="⚠️",

            )



    with detail_col2:

        st.metric(

            label="Message ID",

            value=msg_id,

        )


