# SECTION 11 — STREAMLIT FRONTEND & OPERATIONAL DASHBOARD

**Project:** Patient Message Triage & Urgency Classifier (PS-1)  
**Track:** Healthcare & HealthTech — AIML GLA Bootcamp '26 One-Day AI Hackathon  
**Phase Status:** Complete & Verified  

---

## 1. Executive Summary & Architectural Separation

Section 11 implements the complete, production-style Streamlit frontend and operational dashboard for the **Patient Message Triage & Urgency Classifier (PS-1)**. 

In strict compliance with architectural constraints:
- **Zero Model Duplication:** Streamlit operates solely as a presentation and workflow dashboard. No scikit-learn models, vectorizers, scalers, or inference pipelines are loaded or executed within the Streamlit process.
- **Strict API Boundary:** The frontend communicates with the ML decision engine exclusively through HTTP requests directed to the Section 10 FastAPI backend (`http://127.0.0.1:8000`).
- **Safety Boundary Enforcement:** The application reinforces at every screen that this platform is an **operational decision support tool** for administrative routing and coordination, explicitly not a clinical diagnosis or treatment instrument.

---

## 2. Directory Structure & Files Created/Modified

### Files Created:
1. `src/ui/__init__.py` — Package initialization for UI layer.
2. `src/ui/config.py` — Frontend configuration dataclass (`UIConfig`), managing backend URL (`FASTAPI_BASE_URL`), app metadata, and HTTP timeouts.
3. `src/ui/api_client.py` — Robust HTTP client (`FastAPIClient`) wrapping `httpx`, providing structured error handling, connection error resilience, timeouts, and JSON serialization.
4. `src/ui/helpers.py` — Formatting utilities for confidence scores and operational status badges.
5. `src/ui/components/__init__.py` — Component package initialization.
6. `src/ui/components/header.py` — Top-level branding and persistent healthcare safety disclaimer banner.
7. `src/ui/components/status_cards.py` — Visual cards displaying live backend connectivity, artifact readiness, model version, and operational threshold parameters.
8. `src/ui/components/prediction_result.py` — Triage outcome cards displaying Category, Urgency, assigned routing queue, confidence progress bars, and latency.
9. `src/ui/components/explanation.py` — Token-level linear feature attribution tables ($x_j \cdot W_{k, j}$) for Category and Urgency.
10. `src/ui/components/review_queue.py` — Session-scoped human review queue with detailed JSON inspection and queue clearing.
11. `src/ui/components/batch_results.py` — Batch summary metric cards, interactive results table, and one-click CSV export.
12. `src/ui/app.py` — Master Streamlit application featuring multi-page navigation across 6 distinct views.
13. `tests/test_ui_api_client.py` — Unit tests for HTTP API client error handling, timeouts, and successful responses.
14. `tests/test_ui_helpers.py` — Unit tests for UI formatting helpers.
15. `SECTION11_STREAMLIT_FRONTEND_IMPLEMENTATION.md` — Formal implementation specification document.

### Files Modified:
1. `requirements.txt` — Appended `streamlit==1.56.0`.
2. `.env.example` — Added `FASTAPI_BASE_URL=http://127.0.0.1:8000`.
3. `README.md` — Updated with Section 11 dashboard architecture, run commands, and feature overview.

---

## 3. Streamlit Pages Implemented

The application provides 6 distinct operational views accessible via the sidebar navigation:

1. **?? Dashboard Overview:**
   - Real-time backend status metrics (API connectivity, model readiness, model version).
   - Operational parameters overview (Confidence threshold $\tau = 0.70$, 5 categories, 2 urgency levels, $\min(C_{\text{cat}}, C_{\text{urg}})$ rule).
   - Quick navigation links to core operational workflows.

2. **?? Single Message Triage:**
   - Interactive message input with pre-populated healthcare inquiry samples.
   - Real-time classification via `POST /predict`.
   - Visual output: Category, Urgency (?? Urgent / ?? Non-Urgent), Assigned Queue, confidence meters, latency metric.
   - Linear feature explainability tables displaying top linguistic tokens driving decisions.
   - Automatic escalation of low-confidence cases to the Human Review Queue.

3. **?? Batch Triage:**
   - CSV spreadsheet uploader with flexible column mapping (`message_text`, `text`, `message`, `body`).
   - Operational batch cap enforcement ($\le 50$ rows per batch).
   - Multipart upload to `POST /predict/batch`.
   - Summary metrics (Total submitted, standard routed, low confidence, invalid, total latency).
   - Interactive results table and one-click CSV export (`batch_triage_results.csv`).

4. **?? Human Review Queue:**
   - Displays all cases where overall confidence fell below threshold ($C_{\text{overall}} < 0.70$) or input validation failed.
   - Interactive data table and deep case inspector with raw payload inspection.
   - "Clear Review Queue" operational button.
   - Prominently notes that the review queue is session-scoped for this MVP stage.

5. **?? Model & Evaluation:**
   - Displays active production model artifact lineage queried live from `GET /model-info`.
   - Section 9 benchmark evaluation report cards (Category Macro F1: 1.000, Category Accuracy: 100.0%, Urgent Recall: 1.000, Confidence Gate: 0.700).
   - Prominent Synthetic Benchmark Disclaimer explaining that metrics reflect synthetic test partition consistency rather than clinical efficacy.
   - Schema reference for the 5 operational categories and 2 urgency levels.

6. **?? System Status:**
   - Diagnostic panel with one-click refresh button.
   - Live connectivity and readiness checks.
   - Interactive JSON inspection tabs for raw responses from `GET /health`, `GET /ready`, and `GET /model-info`.

---

## 4. FastAPI Endpoints Integrated

The Streamlit UI communicates exclusively with the following Section 10 FastAPI endpoints:
- `GET /health` — Liveness check and API version verification.
- `GET /ready` — Readiness check ensuring ML pipeline artifacts are loaded in memory.
- `GET /model-info` — Public model metadata, feature extractor details, vocabulary size, and routing queues.
- `POST /predict` — Real-time single message classification, confidence evaluation, routing, and explainability.
- `POST /predict/batch` — Multipart CSV file upload processing up to 50 patient messages in a single batch.

---

## 5. Verification & Testing

### Test Execution Summary:
- **Total Test Cases:** 52
- **Passing:** 52 (100%)
- **Failing:** 0
- **Execution Time:** ~21.7s
- **Regression Status:** All 45 tests from Sections 8, 9, and 10 continue to pass with zero regressions.
- **Section 11 Specific Tests:** 7 passing tests covering UI formatting helpers and `FastAPIClient` connection resilience, timeouts, and JSON serialization.

---

## 6. How to Run the System

### Step 1: Start the FastAPI Backend
In your terminal, launch the backend using Python module syntax:
```bash
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API docs are accessible at: `http://127.0.0.1:8000/docs`

### Step 2: Start the Streamlit Operational Dashboard
In a separate terminal window, launch the Streamlit dashboard:
```bash
python -m streamlit run src/ui/app.py --server.port 8501
```
The operational dashboard will open in your web browser at: `http://localhost:8501`

---

## 7. Known Limitations & Deviations

1. **Session-Scoped Review Queue:** In this MVP phase, cases routed to the Human Review Queue are stored in Streamlit's `st.session_state`. They persist across view navigation within the session, but will reset upon a full browser refresh. Permanent cross-session persistence will be addressed in future database integration phases.
2. **Batch Cap:** Batches are capped at 50 records per request as specified by the Section 10 API contract to guarantee low latency and prevent resource starvation.
3. **No Deviations:** The implementation adheres 100% to the Section 11 specifications with zero architectural deviations.
