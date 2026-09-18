"""
Patient Triage Assistant (PS-1)
Conversational Urgency and Routing Experience (Section 13).
Modern, light healthcare SaaS aesthetic.
Operates strictly as a presentation layer consuming FastAPI endpoints.
Zero ML models or inference logic loaded in Streamlit.
"""

import os
import sys
from pathlib import Path

# Ensure repository root is on sys.path regardless of execution context or Streamlit Cloud runner
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import io
import streamlit as st
import pandas as pd
from typing import List, Dict, Any

from src.ui.config import ui_config
from src.ui.api_client import FastAPIClient
from src.ui.components.header import render_header, render_safety_disclaimer
from src.ui.components.status_cards import render_backend_status_card, render_operational_overview
from src.ui.components.triage_card import render_triage_result_card
from src.ui.components.conversation_history import render_conversation_history
from src.ui.components.review_queue import render_review_queue
from src.ui.components.batch_results import render_batch_results


# Page Configuration - White background, clean layout
st.set_page_config(
    page_title="Patient Triage Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Light Styling
st.markdown(
    """
    <style>
    /* Clean white background and typography */
    .stApp {
        background-color: #FFFFFF;
        color: #1F2937;
    }
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    /* Example pill buttons */
    div[data-testid="stHorizontalBlock"] button {
        background-color: #F3F4F6;
        color: #374151;
        border: 1px solid #E5E7EB;
        font-size: 13px;
        padding: 4px 10px;
    }
    div[data-testid="stHorizontalBlock"] button:hover {
        background-color: #E5E7EB;
        border-color: #D1D5DB;
        color: #111827;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []

if "review_queue" not in st.session_state:
    st.session_state["review_queue"] = []

if "latest_prediction" not in st.session_state:
    st.session_state["latest_prediction"] = None

if "input_text_val" not in st.session_state:
    st.session_state["input_text_val"] = ""

if "latest_batch_result" not in st.session_state:
    st.session_state["latest_batch_result"] = None

# Initialize API Client
client = FastAPIClient(base_url=ui_config.fastapi_base_url, timeout=ui_config.request_timeout_seconds)


# Primary Navigation
st.sidebar.markdown("## 🏥 Navigation")
nav_page = st.sidebar.radio(
    "Go to",
    options=[
        "💬 Triage Assistant",
        "📁 Batch Upload",
        "⚠️ Human Review",
        "⚙️ System Information",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
review_count = len(st.session_state["review_queue"])
if review_count > 0:
    st.sidebar.warning(f"⚠️ **{review_count}** cases require human review.")

st.sidebar.caption("Operational Triage Switchboard • AIML GLA Bootcamp '26")


# Render Global Header and Concise Disclaimer
render_header()
render_safety_disclaimer()


# =========================================================================
# 1. TRIAGE ASSISTANT (PRIMARY CONVERSATIONAL EXPERIENCE)
# =========================================================================
if nav_page == "💬 Triage Assistant":
    # Assistant Greeting
    st.markdown(
        """
        <div style="display: flex; align-items: flex-start; gap: 12px; margin-top: 10px; margin-bottom: 18px;">
            <div style="font-size: 26px; background-color: #EFF6FF; border-radius: 50%; padding: 6px 10px;">🤖</div>
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 18px; max-width: 650px;">
                <div style="font-weight: 600; font-size: 14px; color: #1E3A8A; margin-bottom: 2px;">Assistant</div>
                <div style="color: #334155; font-size: 15px;">
                    Hello! Please describe what you need help with. I will determine the operational urgency and route your request to the appropriate healthcare department.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick Example Pills
    st.markdown("<p style='font-size: 13px; font-weight: 600; color: #64748B; margin-bottom: 6px;'>Quick Examples:</p>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        if st.button("📅 Book appointment", use_container_width=True):
            st.session_state["input_text_val"] = "I need to schedule an appointment for next Monday morning."
            st.rerun()
    with c2:
        if st.button("💳 Billing issue", use_container_width=True):
            st.session_state["input_text_val"] = "I have a question about an unexpected charge on my latest hospital bill."
            st.rerun()
    with c3:
        if st.button("💊 Medication refill", use_container_width=True):
            st.session_state["input_text_val"] = "I need to refill my Lisinopril prescription before I run out this week."
            st.rerun()
    with c4:
        if st.button("📄 Medical report", use_container_width=True):
            st.session_state["input_text_val"] = "Can you please email me the lab test results and blood work from yesterday?"
            st.rerun()
    with c5:
        if st.button("📱 Technical problem", use_container_width=True):
            st.session_state["input_text_val"] = "The patient portal mobile app keeps crashing every time I try to log in."
            st.rerun()
    with c6:
        if st.button("🚨 Urgent review", use_container_width=True):
            st.session_state["input_text_val"] = "Please review this immediately, I am having acute severe chest pains and shortness of breath."
            st.rerun()

    # Conversational Input Form
    with st.form("triage_input_form", clear_on_submit=False):
        user_input = st.text_area(
            "Enter Patient Message:",
            value=st.session_state.get("input_text_val", ""),
            placeholder="Type or paste the patient message here...",
            height=120,
            label_visibility="collapsed",
        )
        submit_btn = st.form_submit_button("🔍 Analyze Message", type="primary", use_container_width=False)

    if submit_btn:
        cleaned_input = user_input.strip()
        if not cleaned_input:
            st.error("Please enter a message before analyzing.")
        else:
            with st.spinner("Analyzing message..."):
                resp = client.predict_single(cleaned_input)

            if resp.get("success"):
                pred_data = resp.get("data", {})
                st.session_state["latest_prediction"] = pred_data

                # If low confidence, automatically route to Human Review Queue
                if pred_data.get("requires_human_review") or pred_data.get("status") == "LOW_CONFIDENCE" or float(pred_data.get("overall_confidence", 0.0)) < 0.70:
                    st.session_state["review_queue"].append({
                        "message_id": pred_data.get("message_id"),
                        "text": cleaned_input,
                        "predicted_category": pred_data.get("predicted_category"),
                        "predicted_urgency": pred_data.get("predicted_urgency"),
                        "overall_confidence": pred_data.get("overall_confidence", 0.0),
                        "category_confidence": pred_data.get("category_confidence", 0.0),
                        "urgency_confidence": pred_data.get("urgency_confidence", 0.0),
                        "assigned_queue": pred_data.get("assigned_queue"),
                        "status": pred_data.get("status"),
                        "explanation": pred_data.get("explanation"),
                    })

                # Append to session conversation history
                st.session_state["conversation_history"].append({
                    "user_message": cleaned_input,
                    "prediction": pred_data,
                })

                render_triage_result_card(pred_data)
            else:
                status_code = resp.get("status_code", 503)
                err_text = resp.get("error", "Unable to connect to the triage service. Please try again.")
                if status_code in [503, 0]:
                    st.error("Unable to connect to the triage service. Please ensure the backend is running and try again.")
                elif status_code == 422:
                    st.error("Please check your message and try again.")
                else:
                    st.error(f"Triage request failed [{status_code}]: {err_text}")

    elif st.session_state.get("latest_prediction"):
        render_triage_result_card(st.session_state["latest_prediction"])

    # Render Conversation History
    render_conversation_history(st.session_state["conversation_history"])


# =========================================================================
# 2. BATCH UPLOAD
# =========================================================================
elif nav_page == "📁 Batch Upload":
    st.markdown("## 📁 Batch Message Triage")
    st.markdown("Upload a CSV file containing patient messages to automatically classify operational urgency and routing.")

    uploaded_file = st.file_uploader(
        "Upload CSV Spreadsheet (must have a column named `message_text` or `text`):",
        type=["csv"],
    )

    if uploaded_file is not None:
        try:
            file_bytes = uploaded_file.getvalue()
            df_in = pd.read_csv(io.BytesIO(file_bytes))
            st.markdown(f"**Uploaded rows:** `{len(df_in)}`")

            candidate_cols = [c for c in df_in.columns if c.lower() in ["message_text", "text", "message", "body", "content"]]
            if not candidate_cols:
                st.error(f"Could not find a valid message column. Found columns: {list(df_in.columns)}. Ensure a 'message_text' or 'text' column exists.")
            else:
                target_col = candidate_cols[0]
                if target_col != "message_text":
                    df_in = df_in.rename(columns={target_col: "message_text"})
                    csv_buffer = io.StringIO()
                    df_in.to_csv(csv_buffer, index=False)
                    file_bytes = csv_buffer.getvalue().encode("utf-8")

                if len(df_in) > 50:
                    st.warning("⚠️ File contains more than 50 rows. The operational batch limit is 50 records per request. Processing first 50 rows.")
                    df_trimmed = df_in.head(50)
                    csv_buffer = io.StringIO()
                    df_trimmed.to_csv(csv_buffer, index=False)
                    file_bytes = csv_buffer.getvalue().encode("utf-8")

                if st.button("🚀 Process Batch Messages", type="primary"):
                    with st.spinner("Classifying batch via triage backend..."):
                        resp = client.predict_batch(file_bytes, filename=uploaded_file.name)

                    if resp.get("success"):
                        batch_data = resp.get("data", {})
                        st.session_state["latest_batch_result"] = batch_data

                        for item in batch_data.get("results", []):
                            if item.get("requires_human_review") or item.get("status") == "LOW_CONFIDENCE":
                                st.session_state["review_queue"].append(item)

                        render_batch_results(batch_data)
                    else:
                        st.error(f"Batch Processing Failed [{resp.get('status_code')}]: {resp.get('error')}")

        except Exception as e:
            st.error(f"Failed to read CSV file: {str(e)}")

    elif st.session_state.get("latest_batch_result"):
        render_batch_results(st.session_state["latest_batch_result"])


# =========================================================================
# 3. HUMAN REVIEW
# =========================================================================
elif nav_page == "⚠️ Human Review":
    render_review_queue(st.session_state["review_queue"])


# =========================================================================
# 4. SYSTEM INFORMATION (ADMIN AND METRICS)
# =========================================================================
elif nav_page == "⚙️ System Information":
    st.markdown("## ⚙️ System Information and Operational Metadata")
    st.caption("Technical provenance and operational diagnostics for administrative oversight.")

    health = client.health()
    ready = client.ready()
    model_info = client.model_info()

    render_backend_status_card(health, ready)
    st.markdown("---")
    render_operational_overview(model_info)

    st.markdown("---")
    st.markdown("### 📈 Model Performance Specifications")

    st.info(
        "**Synthetic Benchmark Disclaimer:** "
        "Measured on the project's synthetic evaluation dataset ($N_{\\text{test}} = 135$). "
        "This benchmark does not represent real-world clinical effectiveness."
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Urgent Recall", "100%", help="Synthetic benchmark")
    with m2:
        st.metric("Macro F1", "1.000", help="Synthetic benchmark")
    with m3:
        st.metric("Accuracy", "100%", help="Synthetic benchmark")
    with m4:
        st.metric("Confidence Gate", "0.700", help="Threshold tau")

    st.markdown("---")
    st.markdown("### 📋 Routing Architecture Reference")
    st.markdown(
        """
        - **Appointment** ➔ Front Desk / Appointment Queue
        - **Billing** ➔ Billing Department Queue
        - **Medication Refill** ➔ Medication / Refill Workflow Queue
        - **Report Request** ➔ Medical Records / Reports Queue
        - **Technical Issue** ➔ Technical Support Queue
        - **Urgent Review** ➔ Urgent Review Queue
        - **Low Confidence ($< 0.70$)** ➔ Human Review Queue
        """
    )