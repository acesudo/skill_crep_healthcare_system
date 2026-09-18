# SECTION 13 — PATIENT-FACING TRIAGE ASSISTANT UI/UX
## Conversational Urgency & Routing Experience

**Project:** Patient Message Triage & Urgency Classifier (PS-1)  
**Track:** Healthcare & HealthTech — AIML GLA Bootcamp '26 One-Day AI Hackathon  
**Phase Status:** Complete, Verified & Sealed  

---

## 1. Primary Objective & User Journey

Section 13 implements a complete frontend experience redesign, transforming the application from an internal technical switchboard into an intuitive, modern, patient-facing **"Patient Triage Assistant"**.

Normal patients and clinical receptionists do not need to understand feature weights, vectorizer vocabularies, or probability arrays. Instead, the interface immediately answers five critical operational questions:
1. **What type of request is this?** (Operational Category: Appointment, Billing, Medication Refill, Report Request, Technical Issue, Urgent Review)
2. **Is it operationally ROUTINE or URGENT?** (Clear Green vs. Red visual indicators)
3. **How confident is the urgency classification?** (Urgency confidence metric: $C_{\text{urg}} \times 100\%$)
4. **Where should this request be routed?** (Recommended destination queue)
5. **Does it require human review?** (Automatic escalation if $C_{\text{overall}} < 0.70$)

```
   Patient enters message
             ↓
      Analyze Message
             ↓
   Operational Classification
             ↓
     ROUTINE / URGENT
             ↓
     Confidence displayed
             ↓
   Recommended operational route
             ↓
   Human Review if confidence is insufficient
```

---

## 2. Healthcare Safety Boundary

**THIS SYSTEM IS STRICTLY AN OPERATIONAL DECISION-SUPPORT TOOL. IT IS NOT A MEDICAL DIAGNOSIS OR CLINICAL TRIAGE INSTRUMENT.**

The user interface rigorously upholds the following healthcare communication boundaries:
- **Operational Terminology:** All outputs are strictly presented as *"Operationally classified as ROUTINE"* or *"Operationally classified as URGENT"*.
- **No Clinical Claims:** The UI explicitly avoids claiming medical severity, condition safety, or diagnostic status (*"Your condition is safe"*, *"You do not need care"*, *"This is an emergency"*).
- **Persistent Safety Disclaimer:** A clean, non-intrusive operational notice is rendered on every view:
  > *ℹ️ Operational Notice: This tool classifies patient-support messages for operational routing and prioritization. It does not provide medical diagnosis, treatment recommendations, or replace clinical triage.*

---

## 3. UI/UX Design & Aesthetic

The interface was redesigned with a light, spacious healthcare SaaS aesthetic:
- **Color Palette:** Pure white background (`#FFFFFF`), slate dark text (`#1F2937`), healthcare navy blue accents (`#1E3A8A`), emerald green for ROUTINE (`#16A34A`), crimson red for URGENT (`#DC2626`), and amber for human review (`#B45309`).
- **Conversational Presentation:** An assistant greeting card introduces the interaction (*"Hello! Please describe what you need help with."*), followed by quick example pills and a clean multiline text area.
- **Card-Based Results:** Results are presented in clean, rounded cards (`border-radius: 12px`) with subtle borders and shadows.
- **Simplified Navigation:** Sidebar navigation exposes only 4 high-level options:
  1. `💬 Triage Assistant` (Primary patient interaction)
  2. `📁 Batch Upload` (CSV spreadsheet triage)
  3. `⚠️ Human Review` (Session review queue)
  4. `⚙️ System Information` (Technical diagnostics and model specifications)

---

## 4. Components & Architecture

### Files Created:
1. `src/ui/components/triage_card.py` — Patient-friendly outcome component displaying Category, Urgency badge, Urgency Confidence, Routing Confidence, and Recommended Destination Queue.
2. `src/ui/components/conversation_history.py` — Session-scoped conversational thread component tracking prior inquiries and results.
3. `tests/test_ui_section13.py` — Unit tests for triage outcome data handling and conversation history structure.
4. `SECTION13_PATIENT_FACING_TRIAGE_UI_UX.md` — Formal Section 13 specification document.

### Files Modified:
1. `src/ui/app.py` — Complete master app redesign with conversational layout, light theme, example pills, and simplified navigation.
2. `src/ui/components/header.py` — Updated branding to "Patient Triage Assistant" and streamlined concise safety disclaimer.
3. `src/ui/components/batch_results.py` — Aligned column labels and metrics with patient-friendly terminology.
4. `README.md` — Updated with Section 13 architecture and feature overview.

---

## 5. API Integration & Zero Model Duplication

The Streamlit layer remains exclusively a presentation client. Zero ML models or scoring logic are loaded into the UI:
- **Single Triage:** Directly queries `POST /predict`.
- **Batch Triage:** Directly queries `POST /predict/batch` (respecting the 50-row limit).
- **Readiness Probes:** Directly queries `GET /health`, `GET /ready`, and `GET /model-info`.
- **Confidence Values:** Urgency confidence ($C_{\text{urg}}$) and routing confidence ($C_{\text{overall}}$) come directly from the FastAPI response payload without any UI-side recalculation.

---

## 6. Verification & Test Results

The full regression test suite plus Section 13 tests was executed:
```
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
collected 59 items

tests/test_api_batch.py (5 tests) ............................. PASSED [  8%]
tests/test_api_health.py (4 tests) ............................ PASSED [ 15%]
tests/test_api_prediction.py (5 tests) ........................ PASSED [ 24%]
tests/test_api_validation.py (5 tests) ........................ PASSED [ 33%]
tests/test_artifacts.py (2 tests) ............................. PASSED [ 36%]
tests/test_confidence.py (4 tests) ............................ PASSED [ 43%]
tests/test_data_generation.py (2 tests) ....................... PASSED [ 47%]
tests/test_deduplication.py (3 tests) ......................... PASSED [ 52%]
tests/test_integration.py (5 tests) ........................... PASSED [ 61%]
tests/test_ml_pipeline.py (6 tests) ........................... PASSED [ 71%]
tests/test_pii_checker.py (4 tests) ........................... PASSED [ 78%]
tests/test_splitter.py (2 tests) .............................. PASSED [ 82%]
tests/test_ui_api_client.py (5 tests) ......................... PASSED [ 91%]
tests/test_ui_helpers.py (2 tests) ............................ PASSED [ 94%]
tests/test_ui_section13.py (2 tests) .......................... PASSED [ 98%]
tests/test_validation.py (3 tests) ............................ PASSED [100%]

============================= 59 passed in 21.59s =============================
```
- **Total Tests:** 59
- **Passed:** 59 (100%)
- **Failed:** 0
- **Regressions:** Zero.

---

## 7. Browser & Visual Verification
- **URL:** `http://localhost:8501` verified returning **HTTP 200 OK**.
- **Visual Design:** Light background, high contrast, clean typography, responsive layout.
- **UTF-8 & Icon Safety:** Zero UTF-8 decoding issues and zero invalid emoji errors (`StreamlitAPIException`).

---

## 8. Known Limitations
1. **Session Scope:** Conversation history and Human Review queue are maintained in `st.session_state`. They persist across navigation tabs, but reset on full browser refresh.
2. **Batch Cap:** Up to 50 records per CSV batch to maintain sub-second response times.
3. **Synthetic Domain Evaluation:** Synthetic benchmark metrics are clearly designated as synthetic on the System Information page and do not establish clinical efficacy.