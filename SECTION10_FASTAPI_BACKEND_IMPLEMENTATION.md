# Section 10 — FastAPI Backend Implementation

**Project Title:** Patient Message Triage & Urgency Classifier (PS-1)  
**Track:** Healthcare & HealthTech  
**Author:** Implementation & Research Engineer  
**Supervisor:** Senior Software Architect  
**Status:** Completed, Verified, and Production-Ready Specification  
**API Version:** `v1.0.0`  
**Model Version:** `v1.0.0`  
**Dataset Version:** `v1.0.0`  
**Authoritative References:**  
- [SECTION1_PROBLEM_STATEMENT.md](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION1_PROBLEM_STATEMENT.md)  
- [SECTION2_FUNCTIONAL_REQUIREMENTS.md](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION2_FUNCTIONAL_REQUIREMENTS.md)  
- [SECTION3_ACTORS_ROLES_WORKFLOWS.md](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION3_ACTORS_ROLES_WORKFLOWS.md)  
- [SECTION4_DATA_STRATEGY_AND_DATA_CONTRACT.md](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION4_DATA_STRATEGY_AND_DATA_CONTRACT.md)  
- [SECTION5_SYSTEM_ARCHITECTURE.md](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION5_SYSTEM_ARCHITECTURE.md)  
- [SECTION6_TECHNOLOGY_STACK_AND_TECHNICAL_DESIGN.md](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION6_TECHNOLOGY_STACK_AND_TECHNICAL_DESIGN.md)  
- [SECTION7_ML_NLP_DESIGN.md](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION7_ML_NLP_DESIGN.md)  
- [SECTION8_DATA_GENERATION_AND_ENGINEERING.md](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION8_DATA_GENERATION_AND_ENGINEERING.md)  
- [SECTION9_ML_MODEL_TRAINING_AND_EVALUATION.md](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION9_ML_MODEL_TRAINING_AND_EVALUATION.md)  

---

## 1. Purpose & Scope

Section 10 implements the official production-grade **FastAPI Backend Application** for the **Patient Message Triage & Urgency Classifier (PS-1)**. 

The backend encapsulates and serves the trained machine learning models, vectorizer, deterministic routing policies, confidence gating system, and feature explainability mechanisms established and sealed in Sections 7, 8, and 9. It provides an asynchronous, strongly validated, high-throughput REST API interface for downstream clients (such as the upcoming Streamlit user interface in Section 11).

> **CRITICAL HEALTHCARE SAFETY NOTICE:** This API serves strictly as an operational and administrative triage switchboard. It does **NOT** diagnose clinical conditions, prescribe medications, suggest pharmacological treatments, or replace formal emergency clinical triage protocols (such as the Emergency Severity Index). The urgency predictions represent administrative turnaround prioritization, not medical severity.

---

## 2. System Architecture & Component Interactions

```
+-----------------------------------------------------------------------------------+
|                           CLIENT LAYER (Future Streamlit UI)                      |
+-----------------------------------------------------------------------------------+
                                         |  HTTP / JSON / CSV
                                         v
+-----------------------------------------------------------------------------------+
|                        FASTAPI BACKEND SERVICE (Section 10)                       |
|                                                                                   |
|  [ Middleware Pipeline ]                                                          |
|    - CORS Middleware (Configurable Allowed Origins)                               |
|    - Request Correlation ID Injection (X-Request-ID Header)                       |
|    - Structured Latency & Audit Logging (Strict Zero-PHI Logging)                 |
|                                                                                   |
|  [ Global Exception Handlers ]                                                    |
|    - 422 RequestValidationError (Structured Input Validation Failure)             |
|    - 400 / 413 / 503 HTTPException Handling                                       |
|    - 500 Generic Failsafe (Zero Stack Trace Leakage)                              |
|                                                                                   |
|  [ Route Controllers ]                                                            |
|    - GET  /health          -> Liveness Probe                                      |
|    - GET  /ready           -> Readiness Probe (ML Artifact Check)                 |
|    - GET  /model-info      -> Safe Public Metadata Descriptor                     |
|    - POST /predict         -> Single Patient Message Triage                       |
|    - POST /predict/batch   -> Batch CSV Multi-Message Triage                      |
|                                                                                   |
|  [ Application Lifespan State Container (app.state.inference_service) ]           |
|                                                                                   |
|         +---------------------------------------------------------------+         |
|         |                   INFERENCE SERVICE LAYER                     |         |
|         |                                                               |         |
|         |  [ NLP Text Preprocessor ]                                    |         |
|         |    - Unicode NFKD, Entity Masking, Contraction Expansion      |         |
|         |                                                               |         |
|         |  [ TF-IDF Vectorizer (2,500 features) ]                       |         |
|         |                                                               |         |
|         |  [ Dual Scikit-Learn Classifiers ]                            |         |
|         |    * Category: Multinomial LogisticRegression (6 classes)     |         |
|         |    * Urgency: Binary LogisticRegression (Routine vs Urgent)   |         |
|         |                                                               |         |
|         |  [ Confidence & Gating Engine ]                               |         |
|         |    * C_overall = min(C_cat, C_urg)                            |         |
|         |    * Threshold Check: C_overall >= 0.70                       |         |
|         |                                                               |         |
|         |  [ Deterministic Routing Service ]                            |         |
|         |    * High Confidence -> Functional Departmental Queue         |         |
|         |    * Low Confidence  -> Human Review Queue                    |         |
|         |                                                               |         |
|         |  [ Linear Feature Explainer ]                                 |         |
|         |    * Top 3–5 linear attribution weights (x_j * W_kj)          |         |
|         +---------------------------------------------------------------+         |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        SEALED ML MODEL STORAGE (models/v1.0.0/)                   |
|  - tfidf_vectorizer.joblib (26.8 KB)                                              |
|  - category_model.joblib (59.4 KB)                                                |
|  - urgency_model.joblib (11.3 KB)                                                 |
|  - metadata.json (1.96 KB)                                                        |
+-----------------------------------------------------------------------------------+
```

---

## 3. API Design Principles & Standards

1. **Strict Separation of Concerns:** Route handlers perform HTTP parsing, file streaming, and status code dispatch. All business and machine learning logic is encapsulated within the `InferenceService` and `RoutingService`.
2. **Deterministic & Hallucination-Free:** All operational decisions, probabilities, queue assignments, and keyword attributions are derived strictly from scikit-learn models and fixed lookup tables. No generative LLMs are present on the prediction path.
3. **Fail-Fast Readiness:** If model artifacts are missing or unreadable at startup, the application lifecycle logs a critical alert, and `/ready` returns HTTP 503 instead of pretending the system is operational.
4. **Strict Zero-PHI Logging:** The server logs request method, URL path, HTTP status, execution latency, and request correlation IDs. Raw message text is strictly excluded from log streams.

---

## 4. Complete Endpoint Directory

| Method | Endpoint | Summary | Response Codes | Description |
|---|---|---|---|---|
| `GET` | `/health` | Liveness check | `200` | Verifies web server process is alive. |
| `GET` | `/ready` | Readiness check | `200`, `503` | Verifies ML models are loaded and memory-resident. |
| `GET` | `/model-info` | Model metadata | `200`, `503` | Returns safe model configuration and class labels. |
| `POST` | `/predict` | Single message triage | `200`, `422`, `500`, `503` | Triages an individual patient inquiry. |
| `POST` | `/predict/batch` | Batch CSV triage | `200`, `400`, `413`, `503` | Uploads and processes a multi-message CSV file. |

---

## 5. Request Schemas & Input Constraints

Defined in [`src/api/schemas.py`](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/src/api/schemas.py):

### 5.1 Single Prediction Request (`PredictRequest`)
```json
{
  "message_text": "I need to reschedule my Friday appointment with Dr. Smith to next week.",
  "message_id": "MSG-100402"
}
```
- `message_text` (String, required): Min length 1, max length 4000 characters. Rejects empty strings and pure whitespace via custom Pydantic validator.
- `message_id` (String, optional): Client-provided correlation ID. If omitted, automatically generated by server as `MSG-<HEX8>`.
- `extra = "forbid"`: Disallows unrecognized injected JSON fields.

### 5.2 Batch Prediction Request (`UploadFile`)
- Multipart form-data with key `file`.
- Extension must be `.csv`.
- Maximum file size: $5\text{ MB}$.
- Maximum rows: $1,000$ lines.
- Required CSV header: `message_text`. Optional: `message_id`.

---

## 6. Response Schemas & Data Contracts

### 6.1 Single Prediction Response (`PredictResponse`)
```json
{
  "message_id": "MSG-100402",
  "predicted_category": "Appointment",
  "predicted_urgency": "Routine",
  "category_confidence": 0.9412,
  "urgency_confidence": 0.9105,
  "overall_confidence": 0.9105,
  "assigned_queue": "Front Desk / Appointment Queue",
  "requires_human_review": false,
  "status": "SUCCESS",
  "explanation": {
    "category_features": [
      { "feature": "appointment", "contribution": 0.2373 },
      { "feature": "reschedule", "contribution": 0.1561 }
    ],
    "urgency_features": [
      { "feature": "appointment", "contribution": 0.1480 },
      { "feature": "for", "contribution": 0.1395 }
    ]
  }
}
```

### 6.2 Low-Confidence Escalation Response
When $C_{\text{overall}} < 0.70$:
```json
{
  "message_id": "MSG-35A5F88F",
  "predicted_category": "Appointment",
  "predicted_urgency": "Routine",
  "category_confidence": 0.4257,
  "urgency_confidence": 0.5853,
  "overall_confidence": 0.4257,
  "assigned_queue": "Human Review Queue",
  "requires_human_review": true,
  "status": "LOW_CONFIDENCE",
  "explanation": {
    "category_features": [ ... ],
    "urgency_features": [ ... ]
  }
}
```

### 6.3 Batch Prediction Response (`BatchPredictResponse`)
```json
{
  "total_records": 3,
  "successful_records": 2,
  "low_confidence_records": 1,
  "invalid_records": 0,
  "results": [
    {
      "row_index": 1,
      "message_id": "MSG-B1",
      "status": "SUCCESS",
      "predicted_category": "Appointment",
      "predicted_urgency": "Routine",
      "category_confidence": 0.892,
      "urgency_confidence": 0.854,
      "overall_confidence": 0.854,
      "assigned_queue": "Front Desk / Appointment Queue",
      "requires_human_review": false,
      "explanation": { ... },
      "error_detail": null
    }
  ]
}
```

---

## 7. ML Artifact Loading & Lifespan Architecture

Artifact loading is executed once during FastAPI lifespan startup in [`src/api/main.py`](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/src/api/main.py) using `ArtifactManager.load_artifacts`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    try:
        inference_service = InferenceService.from_artifacts(
            base_dir=settings.model_base_path,
            version=settings.model_version,
            threshold=settings.confidence_threshold,
            max_message_length=settings.max_message_length,
        )
        app.state.inference_service = inference_service
    except Exception as exc:
        logger.critical("FATAL: Failed to load ML model artifacts: %s", exc)
        app.state.inference_service = None
    yield
```

### Loaded Model Inventory:
1. `tfidf_vectorizer.joblib`: 2,500 n-gram features (scikit-learn `TfidfVectorizer`)
2. `category_model.joblib`: 6-class `LogisticRegression(C=1.0, class_weight='balanced')`
3. `urgency_model.joblib`: Binary `LogisticRegression(C=1.0, class_weight='balanced')`
4. `metadata.json`: Provenance manifest verifying `model_version == "v1.0.0"` and `threshold == 0.70`

---

## 8. Single Message Inference Flow

Every call to `POST /predict` executes through a 10-stage sequential pipeline:
1. **Pydantic Validation:** Body parsed against `PredictRequest`; rejection of empty strings.
2. **Correlation Tagging:** `message_id` extracted or synthesized (`MSG-<HEX8>`).
3. **NLP Preprocessing:** Text normalized using `TextPreprocessor.clean()` (Unicode NFKD, entity masking, contraction expansion).
4. **TF-IDF Vectorization:** Normalized text transformed into sparse vector $x \in \mathbb{R}^{2500}$.
5. **Category Prediction:** Evaluates $P(\text{category} \mid x) \in \mathbb{R}^6$; computes argmax class and $C_{\text{cat}} = \max_k P_k$.
6. **Urgency Prediction:** Evaluates $P(\text{urgency} \mid x) \in \mathbb{R}^2$; computes argmax class and $C_{\text{urg}} = \max_u P_u$.
7. **Joint Confidence Evaluation:** Computes $C_{\text{overall}} = \min(C_{\text{cat}}, C_{\text{urg}})$.
8. **Operational Threshold Gating:**
   - If $C_{\text{overall}} \ge 0.70$: `requires_human_review = False`, `status = StatusEnum.SUCCESS`.
   - If $C_{\text{overall}} < 0.70$: `requires_human_review = True`, `status = StatusEnum.LOW_CONFIDENCE`.
9. **Deterministic Routing:** Resolves assigned queue using `RoutingService.route()`.
10. **Explainability Extraction:** Computes top 5 positive contributing linear feature weights for Category and Urgency; returns `PredictResponse`.

---

## 9. Confidence Calculation & Conservative Bottleneck Aggregation

Implemented in [`src/api/services/inference_service.py`](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/src/api/services/inference_service.py):

$$C_{\text{cat}} = \max_{k \in \{1 \dots 6\}} P(\text{category} = k \mid x)$$
$$C_{\text{urg}} = \max_{u \in \{\text{Routine}, \text{Urgent}\}} P(\text{urgency} = u \mid x)$$
$$C_{\text{overall}} = \min(C_{\text{cat}}, C_{\text{urg}})$$

### Operational Rationale:
If the model is 92% confident that a message pertains to `Appointment`, but only 55% confident whether it is `Routine` or `Urgent`, the operational decision remains uncertain. Taking the minimum guarantees that ambiguity on *either* axis triggers human oversight.

---

## 10. Operational Threshold ($\tau = 0.70$) Logic

The operational gating rule is strictly enforced:

$$\text{Routing Decision} = \begin{cases} \text{Departmental Queue Routing}, & \text{if } C_{\text{overall}} \ge 0.70 \\ \text{Human Review Queue Escalation}, & \text{if } C_{\text{overall}} < 0.70 \end{cases}$$

This threshold was empirically validated in Section 9 to yield:
- **0 missed urgent auto-routed cases** ($100\%$ safety recall)
- **$80.0\%$ automated routing throughput** on validation partition
- **$20.0\%$ human review volume** (well within the $\le 25\%$ staff capacity SLA)

---

## 11. Human Review Escalation Protocol

When $C_{\text{overall}} < 0.70$:
1. `requires_human_review` is set to `True`.
2. `assigned_queue` is overwritten to `"Human Review Queue"`.
3. `status` is set to `StatusEnum.LOW_CONFIDENCE`.
4. Predictions (`predicted_category`, `predicted_urgency`) and `explanation` are still returned to provide operational context to the human triage officer, but the response contract clearly communicates that the prediction is untrusted and unrouted.

---

## 12. Deterministic Routing Service

Implemented in [`src/api/services/routing_service.py`](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/src/api/services/routing_service.py):

| Predicted Category | Operational Destination Queue (High Confidence) | Destination Queue (Low Confidence) |
|---|---|---|
| `Appointment` | `Front Desk / Appointment Queue` | `Human Review Queue` |
| `Billing` | `Billing Department Queue` | `Human Review Queue` |
| `Medication Refill` | `Medication / Refill Workflow Queue` | `Human Review Queue` |
| `Report Request` | `Medical Records / Reports Queue` | `Human Review Queue` |
| `Technical Issue` | `Technical Support Queue` | `Human Review Queue` |
| `Urgent Review` | `Urgent Review Queue` | `Human Review Queue` |

No LLM or heuristic heuristics are allowed to dynamically alter or invent destination queues.

---

## 13. Batch CSV Processing Pipeline

Implemented in [`src/api/routes/batch.py`](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/src/api/routes/batch.py):
1. Streams uploaded CSV into memory (verifying $< 5\text{ MB}$).
2. Decodes text using UTF-8 (with fallback to Latin-1).
3. Validates that the CSV contains a `message_text` header.
4. Enforces row limit $\le 1,000$ lines.
5. Executes row-level fault-tolerant triage:
   - Malformed or empty rows produce `BatchRecordItem(status="INVALID_INPUT", error_detail=...)`.
   - Valid rows produce complete predictions.
   - Faults on row $i$ never terminate processing for row $i+1$.
6. Aggregates results into `BatchPredictResponse`.

---

## 14. Validation Engine & Reject Conditions

The API enforces strict input rejection rules:
- **Empty or Whitespace-Only Text:** Returns HTTP 422 Unprocessable Content.
- **Text Length $> 4,000$ Characters:** Returns HTTP 422 Unprocessable Content.
- **Disallowed Additional JSON Fields:** Returns HTTP 422 Unprocessable Content.
- **Non-CSV Uploads to `/predict/batch`:** Returns HTTP 400 Bad Request.
- **Missing `message_text` Column in CSV:** Returns HTTP 400 Bad Request.
- **Batch Upload $> 5\text{ MB}$ or $> 1,000$ Rows:** Returns HTTP 413 Payload Too Large.

---

## 15. Error Handling & Failsafe Architecture

All error responses adhere to the standardized `ErrorResponse` contract:
```json
{
  "status": "INVALID_INPUT",
  "detail": "Request validation failed: Field 'body -> message_text': Value error, message_text cannot be empty or solely whitespace.",
  "request_id": "REQ-c671c18f0a84"
}
```
- **Zero Stack Trace Leakage:** Internal Python tracebacks are logged server-side but stripped from HTTP responses.
- **Zero Internal Path Exposure:** No internal directories, file paths, or credentials are exposed in client errors.

---

## 16. Structured Logging & PHI Protection

Logging is configured via Python's `logging` module:
- **Logged Event Attributes:** Method, URL Path, Response HTTP Status, Latency (ms), and Request ID.
- **Zero-PHI Guarantee:** The raw text of patient messages (`message_text`) is **NEVER** logged to standard output or log files.
- **Audit Format:**
  ```
  2026-09-18 12:09:14,709 [INFO] [triage_api] Handled request: method=POST path=/predict status=200 duration=5.43ms request_id=REQ-61492c713ddd
  ```

---

## 17. Security & Input Sanitization

1. **Payload Size Guardrails:** $4,000$-character limit on individual text; $5\text{ MB}$ upload ceiling on batch CSVs.
2. **In-Memory Buffering:** CSV files are processed in memory without writing arbitrary client files to disk.
3. **No Dynamic Code Evaluation:** Explanations and predictions use static scikit-learn matrices without `eval()` or unvetted deserializers.
4. **No Hardcoded Credentials:** Zero API keys or secrets exist in the source code.

---

## 18. Cross-Origin Resource Sharing (CORS)

CORS is configured via FastAPI's `CORSMiddleware` in `src/api/main.py`:
- **Allowed Origins:** Configurable via `CORS_ALLOWED_ORIGINS` environment variable.
- **Default Local Origins:** `http://localhost:8501`, `http://127.0.0.1:8501`, `http://localhost:3000`, `http://127.0.0.1:3000`.
- **Preflight Verification:** Validated via automated test `test_cors_preflight_headers`.

---

## 19. Configuration Layer

Centralized in [`src/api/config.py`](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/src/api/config.py):

| Variable Name | Default Value | Purpose |
|---|---|---|
| `APP_ENV` | `"development"` | Operational runtime environment (`development`, `production`, `test`) |
| `MODEL_VERSION` | `"v1.0.0"` | Expected model artifact directory name |
| `MODEL_BASE_PATH` | `"models"` | Base directory containing versioned artifacts |
| `CONFIDENCE_THRESHOLD` | `0.70` | Operational confidence gating threshold $\tau$ |
| `MAX_MESSAGE_LENGTH` | `4000` | Maximum character length for single inquiries |
| `MAX_BATCH_ROWS` | `1000` | Maximum rows permitted in batch CSV upload |
| `MAX_UPLOAD_SIZE_MB` | `5` | Maximum upload size ceiling in megabytes |
| `CORS_ALLOWED_ORIGINS` | Comma-separated URLs | Allowed client browser origins |

Template file provided at [`.env.example`](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/.env.example).

---

## 20. Automated Test Suite Results

Automated API tests are implemented across 4 dedicated test suites using `pytest` and `httpx`:
- [`tests/test_api_health.py`](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/tests/test_api_health.py) (4 tests)
- [`tests/test_api_prediction.py`](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/tests/test_api_prediction.py) (5 tests)
- [`tests/test_api_batch.py`](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/tests/test_api_batch.py) (5 tests)
- [`tests/test_api_validation.py`](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/tests/test_api_validation.py) (5 tests)

### Regression Test Suite Results:
```
tests/test_api_batch.py .....                                            [ 11%]
tests/test_api_health.py ....                                            [ 20%]
tests/test_api_prediction.py .....                                       [ 31%]
tests/test_api_validation.py .....                                       [ 42%]
tests/test_artifacts.py ..                                               [ 46%]
tests/test_confidence.py ....                                            [ 55%]
tests/test_data_generation.py ..                                         [ 60%]
tests/test_deduplication.py ...                                          [ 66%]
tests/test_ml_pipeline.py ......                                         [ 80%]
tests/test_pii_checker.py ....                                           [ 88%]
tests/test_splitter.py ..                                                [ 93%]
tests/test_validation.py ...                                             [100%]
============================= 45 passed in 20.87s =============================
```
**Total Pass Rate:** **45/45 tests passed (100%)**. Zero regressions against Sections 1–9.

---

## 21. Performance & Latency Measurements

Measured using real requests on local hardware (Python 3.14.4 / Windows 11):

| Measurement Scenario | Observed Duration | Target SLA | Status |
|---|---|---|---|
| **Model Startup Load Time** | **41.25 ms** | $< 500\text{ ms}$ | Exceeded |
| **Single Predict Latency (Average)** | **4.82 ms** | $< 50\text{ ms}$ | Exceeded |
| **Single Predict Latency (Min / Max)** | **3.80 ms / 9.01 ms** | $< 50\text{ ms}$ | Exceeded |
| **Batch Predict (10 rows)** | **23.53 ms** ($2.35\text{ ms/row}$) | $< 200\text{ ms}$ | Exceeded |
| **Batch Predict (50 rows)** | **71.28 ms** ($1.43\text{ ms/row}$) | $< 1000\text{ ms}$ | Exceeded |

---

## 22. Local Running Guide

To run the API locally in development mode:

```bash
# 1. Navigate to project root
cd C:\Users\hp\.gemini\antigravity\scratch\patient-message-triage

# 2. Start Uvicorn development server
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

### Verification Endpoints:
- **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Liveness Probe:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Readiness Probe:** [http://127.0.0.1:8000/ready](http://127.0.0.1:8000/ready)

---

## 23. OpenAPI Documentation Compliance

The generated OpenAPI 3.1.0 specification accurately documents:
- Detailed schema titles, descriptions, constraints, and field examples.
- Complete HTTP status codes (`200`, `400`, `413`, `422`, `500`, `503`).
- Descriptive summary tags: `Health & System`, `Triage Inference`, and `Batch Triage`.

---

## 24. Known Limitations

1. **In-Memory Batch Processing:** Batch CSVs are streamed into memory. While appropriate for the hackathon limit ($1,000$ rows / $5\text{ MB}$), enterprise production scaling ($100,000+$ rows) would require asynchronous background task queues (e.g., Celery + Redis).
2. **Deterministic Routing Rigidity:** The routing matrix maps categories directly to functional queues without accounting for shift rotations, provider on-call rosters, or clinic holiday closures.
3. **No Authentication Layer:** API access is currently unauthenticated as specified for the hackathon MVP; enterprise deployment requires OAuth2 / JWT bearer tokens.

---

## 25. Handoff to Section 11 (Streamlit Frontend)

Section 10 delivers a fully verified, stable, and documented backend contract ready for frontend consumption in Section 11:
- The Streamlit frontend can issue standard `httpx` or `requests` calls to `POST /predict` and `POST /predict/batch`.
- Response payloads provide pre-computed `overall_confidence`, `requires_human_review`, `assigned_queue`, and `explanation` keywords, enabling clean dashboard visual rendering without duplicated client-side business logic.
