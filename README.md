# Patient Message Triage & Urgency Classifier (PS-1)

Track: **Healthcare & HealthTech**

## Project Status: Section 10 â€” FastAPI Backend Implementation Complete

This repository contains the complete specification, system architecture, technical design, ML design, synthetic dataset generation assets, trained machine learning models, evaluation reports, and production-grade FastAPI backend for the AI-powered Operational Patient Message Triage System.

### Documentation Index
- [Section 1 Specification](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION1_PROBLEM_STATEMENT.md) â€” Problem Statement Understanding, Core Objectives, Safety Boundaries, System Concepts, and Requirement Classification.
- [Section 2 Specification](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION2_FUNCTIONAL_REQUIREMENTS.md) â€” Functional Requirements Specification (FR-01 to FR-16), Single & Batch Flows, System States, and Traceability Matrix.
- [Section 3 Specification](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION3_ACTORS_ROLES_WORKFLOWS.md) â€” System Actors, User Roles, Component Responsibilities, End-to-End Workflows, State Machine, and Traceability.
- [Section 4 Specification](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION4_DATA_STRATEGY_AND_DATA_CONTRACT.md) â€” Data Source Strategy, Canonical Data Contract, Field Definitions, Category/Urgency Label Strategies, Synthetic Data Generation Principles, Data Quality Rules, Leakage/PII Prevention, and Open Data Decisions.
- [Section 5 Specification](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION5_SYSTEM_ARCHITECTURE.md) â€” Architectural Principles, Modular Monolith Evaluation, Component Specifications (Frontend, API, Validation, NLP, ML, Confidence, Routing, Human Review, Storage, Downstream GenAI), State Machine, Mermaid Diagrams, Requirement Traceability Matrix, and Open Architectural Decisions.
- [Section 6 Specification](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION6_TECHNOLOGY_STACK_AND_TECHNICAL_DESIGN.md) â€” Technology Stack Selection (Python, FastAPI, Streamlit, scikit-learn, TF-IDF, Supabase + PostgreSQL, joblib, pytest, Matplotlib, Google Gemini API), Security Boundaries, Architecture-to-Technology Mapping, and Open Decision Register.
- [Section 7 Specification](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION7_ML_NLP_DESIGN.md) â€” Machine Learning & NLP Design (Preprocessing Pipeline, TF-IDF Vectorizer Parameters, Dual Independent Classifiers, Urgency Schema, Candidate Benchmarks, Confidence Bottleneck Calculation, Calibration, Operational Threshold Tau, Linear Feature Attribution Explainability, and Implementation Contract).
- [Section 8 Specification](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION8_DATA_GENERATION_AND_ENGINEERING.md) â€” Data Generation & Engineering (900 Synthetic Records, 6 Categories, Binary Urgency, DQ-01 to DQ-16 Quality Suite, 70/15/15 Stratified Split, Zero-Leakage Audit, Metadata Manifest, and 14 Passing Unit Tests).
- [Section 9 Specification](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION9_ML_MODEL_TRAINING_AND_EVALUATION.md) â€” ML Model Training & Evaluation (Candidate Benchmarks, Logistic Regression Selection, Platt Calibration Check, Bottleneck Confidence System, Tau Optimization at 0.70, Unseen Test Set Evaluation, Model Artifacts v1.0.0, and 26 Passing Unit Tests).
- [Section 10 Specification](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION10_FASTAPI_BACKEND_IMPLEMENTATION.md) â€” FastAPI Backend Implementation (Lifespan Artifact Loading, /health, /ready, /model-info, /predict, /predict/batch, Pydantic v2 Schemas, Bottleneck Confidence Gating, Deterministic Routing, Latency Benchmarks, and 19 Passing API Unit Tests).

### Running the FastAPI Backend
```bash
# Start the local development API server with auto-reload
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Swagger Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Liveness Probe:** `GET /health`
- **Readiness Probe:** `GET /ready`
- **Model Metadata:** `GET /model-info`
- **Single Prediction:** `POST /predict`
- **Batch CSV Upload:** `POST /predict/batch`




### Section 13 — Patient-Facing Triage Assistant UI/UX
- **Application Name:** Patient Triage Assistant
- **Interface:** Modern light healthcare SaaS aesthetic with conversational presentation at `http://localhost:8501`.
- **Primary Questions Answered:**
  1. What type of request is this? (Operational Category)
  2. Is it operationally ROUTINE or URGENT? (Green vs. Red indicators)
  3. How confident is the urgency classification? (Urgency Confidence %)
  4. Where should this request be routed? (Recommended Destination Queue)
  5. Does it require human review? (Automatic escalation if confidence < 0.70)
- **Zero Model Duplication:** Streamlit remains strictly a presentation client consuming the FastAPI backend.
- **Specification Document:** See `SECTION13_PATIENT_FACING_TRIAGE_UI_UX.md`.

### Section 12 — End-to-End Integration & Testing
- **Purpose:** System-wide integration and demo validation from Streamlit frontend through FastAPI, ML inference, confidence gating, routing, and human review.
- **Integration Test Suite:** `tests/test_integration.py` (5 comprehensive end-to-end integration tests).
- **Execution:** All 57 unit, functional, and integration tests passing cleanly (100% pass rate, 0 regressions).
- **Startup Commands:**
  - Backend: `python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload`
  - Frontend: `python -m streamlit run src/ui/app.py --server.port 8501`
- **Hackathon Demo Workflow:** Complete 10-step zero-code demo journey validated across single triage, low-confidence gating, session review queue, batch triage with CSV download, model lineage, and system health status.
- **Specification Document:** See `SECTION12_END_TO_END_INTEGRATION_AND_TESTING.md`.

### Streamlit Operational Dashboard (Section 11)
- **Dashboard Interface:** `http://localhost:8501`
- **Architecture:** Zero model logic in UI layer; communicates exclusively via HTTP with FastAPI backend.
- **Pages:**
  1. `Dashboard Overview`: Health indicators, model version, operational threshold configuration.
  2. `Single Message Triage`: Interactive portal message triage with linear feature explanations.
  3. `Batch Triage`: CSV spreadsheet triage (up to 50 rows) with download capability.
  4. `Human Review Queue`: Session-scoped review queue for low-confidence ({overall} < 0.70$) cases.
  5. `Model & Evaluation`: Active artifact lineage and synthetic benchmark performance metrics.
  6. `System Status`: Diagnostic latency and raw JSON health probes.
- **Launch Command:**
  ``bash
  python -m streamlit run src/ui/app.py --server.port 8501
  ``

### Trained ML Model Artifacts (`models/v1.0.0/`)
- `tfidf_vectorizer.joblib` â€” Fitted TF-IDF Vectorizer (2,500 features, fitted strictly on Train split)
- `category_model.joblib` â€” Tuned Logistic Regression Classifier (6 operational categories, Macro F1: 1.0000)
- `urgency_model.joblib` â€” Tuned Logistic Regression Classifier (Binary urgency, Urgent Recall: 1.0000, Brier Score: 0.0341)
- `metadata.json` â€” Complete versioned model provenance and hyperparameter manifest

### Evaluation & Operational Reports (`reports/`)
- `reports/model_comparison.csv` â€” Validation candidate benchmarks across LogisticRegression, LinearSVC, and MultinomialNB
- `reports/validation_results.json` â€” Validation metrics and complete threshold tau grid evaluation ($0.60 \le \tau \le 0.90$)
- `reports/test_results.json` â€” Untouched test set metrics evaluated strictly once
- `reports/error_analysis.csv` â€” Test set error analysis (0 misclassifications)
- `reports/confusion_matrices/` â€” High-resolution confusion matrix plots for Category and Urgency on Validation and Test sets

### Generated Dataset Artifacts
- `data/raw/dataset_raw.csv` â€” 900 raw synthetic message records
- `data/processed/dataset_clean.csv` â€” 900 canonical validated records
- `data/splits/train.csv` â€” 630 stratified training records (70%)
- `data/splits/validation.csv` â€” 135 stratified validation records (15%)
- `data/splits/test.csv` â€” 135 held-out evaluation records (15%)
- `data/dataset_metadata.json` â€” Provenance, class distribution, and quality status manifest

> **Healthcare Safety Notice:** This system is designed solely for operational message routing and prioritization. It is NOT a medical diagnosis, treatment, or clinical decision system.


