# Section 1 — Problem Statement Understanding and Project Definition

**Project Title:** Patient Message Triage & Urgency Classifier (PS-1)  
**Track:** Healthcare & HealthTech  
**Author:** Implementation Engineer  
**Supervisor:** Senior Developer  
**Status:** Approved for Section 1 Definition  

---

## 1. Project Title
**PS-1: Patient Message Triage & Urgency Classifier**  
An AI-powered operational patient-message triage system designed for healthcare organizations (hospitals, clinics, and health systems).

---

## 2. Problem Statement
Healthcare organizations process high volumes of incoming patient-support messages daily via patient portals, email, SMS, and web forms. These messages span a wide spectrum of operational and administrative inquiries—such as scheduling appointments, requesting billing clarifications, ordering prescription refills, obtaining medical records, seeking technical assistance, or communicating urgent symptom updates.

Currently, manual sorting and routing of these messages create significant operational bottlenecks:
- Delay in prioritizing urgent inquiries due to first-in, first-out (FIFO) handling.
- Overburdening of clinical staff with non-clinical, administrative queries.
- Inconsistent message tagging and misrouting across departments.
- Lack of standardized urgency escalation and auditability.

PS-1 addresses this challenge by providing an automated, confidence-aware operational triage engine that categorizes incoming patient-support messages, assesses operational urgency, routes messages to the correct functional department queue, and flags low-confidence predictions for human operator review.

---

## 3. Problem Context
In modern healthtech infrastructure, administrative message flow directly impacts patient satisfaction and clinical efficiency. When non-urgent administrative queries flood clinical communication channels, staff experience operational fatigue, and critical communications risk being delayed. 

By separating **operational triage** from **clinical diagnosis**, PS-1 functions as an intelligent administrative switchboard. It operates upstream of clinical workflows, streamlining message distribution to front desk personnel, billing specialists, records managers, technical support teams, and urgent intake queues.

---

## 4. Core Objective
The primary objective of this project is to formalize, design, and build an **AI-powered operational patient-message triage system** that receives patient-support messages and determines:
1. **Message Category:** What the message is about (operational topic).
2. **Operational Urgency:** How quickly the message requires administrative/staff attention.
3. **Department Queue:** Which functional queue/department should receive the message.
4. **Prediction Confidence:** Numerical certainty/confidence score of the model's prediction.
5. **Human Review Escalation:** Whether the prediction must be routed to a human operator for manual verification due to low confidence or boundary edge cases.

---

## 5. What the System Does
- `[CONFIRMED]` Accepts incoming patient-support messages in plain text format.
- `[CONFIRMED]` Classifies message topics into predefined operational request categories.
- `[CONFIRMED]` Evaluates operational urgency level to support message prioritization.
- `[CONFIRMED]` Determines the appropriate department/operational destination queue.
- `[CONFIRMED]` Computes confidence metrics for both category and urgency predictions.
- `[CONFIRMED]` Automatically routes uncertain predictions (confidence below threshold) to a Human Review Queue.
- `[CONFIRMED]` Supports single message submission mode for real-time operational triage.
- `[CONFIRMED]` Supports batch CSV submission mode for processing historical or bulk message feeds.
- `[CONCEPTUAL]` Provides feature/keyword-based or summary explanations for model predictions.
- `[CONCEPTUAL]` Offers optional generative AI capabilities for short case summaries and draft responses (non-authoritative).

---

## 6. What the System Does NOT Do
To ensure clinical safety and legal compliance, the system explicitly **DOES NOT**:
- `[CONFIRMED]` Perform medical diagnosis or infer medical conditions.
- `[CONFIRMED]` Provide medical treatment recommendations or advice.
- `[CONFIRMED]` Issue, modify, or authorize pharmaceutical prescriptions.
- `[CONFIRMED]` Replace clinical triage protocols (e.g., ESI - Emergency Severity Index).
- `[CONFIRMED]` Act as a direct replacement for emergency medical services (e.g., 911 / ER instructions).
- `[CONFIRMED]` Allow generative AI models to serve as the primary or authoritative classification engine.
- `[CONFIRMED]` Make fully autonomous decisions on ambiguous or low-confidence medical communications without human oversight option.

---

## 7. Intended Users
The system is designed for operational and administrative healthcare personnel:
1. **Front Desk & Appointment Staff:** Receive appointment-related inquiries and rescheduling requests.
2. **Billing Specialists:** Handle payment questions, insurance inquiries, and invoice requests.
3. **Medical Records Clerks:** Fulfill records requests, lab report dispatches, and form requests.
4. **IT / Technical Support Staff:** Resolve patient portal access issues, password resets, and app glitches.
5. **Operational Triage Operators / Nurses:** Monitor the Urgent Review Queue and the Low-Confidence Human Review Queue.

*Patients interact with the system indirectly via message submission interfaces.*

---

## 8. Core Workflow
The end-to-end operational processing pipeline follows this sequential logic:

```
+-------------------------------------------------------+
|                 1. Patient Message                    |
+-------------------------------------------------------+
                           |
                           v
+-------------------------------------------------------+
|                 2. Message Validation                 |
|   (Sanitization, encoding check, empty string filter)  |
+-------------------------------------------------------+
                           |
                           v
+-------------------------------------------------------+
|                 3. Text Processing                    |
|       (Normalization, tokenization, cleaning)        |
+-------------------------------------------------------+
                           |
                           v
+-------------------------------------------------------+
|         4. Request Category Classification            |
|       (Supervised Multi-Class NLP Classifier)         |
+-------------------------------------------------------+
                           |
                           v
+-------------------------------------------------------+
|             5. Urgency Classification                 |
|            (Operational Urgency Scoring)              |
+-------------------------------------------------------+
                           |
                           v
+-------------------------------------------------------+
|            6. Confidence Evaluation                   |
|     (Model probability vs confidence threshold)       |
+-------------------------------------------------------+
                           |
            +--------------+--------------+
            |                             |
  Confidence >= Threshold       Confidence < Threshold
            |                             |
            v                             v
+-----------------------+     +-----------------------+
| 7. Department Routing |     | 8. Human Review Queue |
|  (Standard Queue Map) |     | (Manual Verification) |
+-----------------------+     +-----------------------+
            |                             |
            +--------------+--------------+
                           |
                           v
+-------------------------------------------------------+
|         9. Output & Optional Summary/Draft            |
|     (Predictions, Confidence, Explanation/Draft)      |
+-------------------------------------------------------+
```

---

## 9. Input Modes

### 9.1 Single Message Mode
- **Input:** Single patient-support message (text string) + metadata (timestamp, patient ID optional).
- **Expected Output:**
  - Predicted Category
  - Predicted Urgency Level
  - Confidence Score (%)
  - Destination Department / Queue
  - Human Review Flag (`TRUE` / `FALSE`)
  - Feature-based Explanation / Keyword Highlights
  - *(Optional)* Short Case Summary / Draft Response

### 9.2 Batch CSV Mode
- **Input:** Structured CSV file containing multiple patient messages (e.g., `message_id`, `message_text`, `timestamp`).
- **Expected Output:**
  - Augmented CSV / Structured Response Object containing row-by-row prediction results:
    - `message_id`
    - `predicted_category`
    - `predicted_urgency`
    - `confidence_score`
    - `assigned_queue`
    - `requires_human_review`

---

## 10. Message Classification Concept
The system classifies incoming messages into standardized operational categories defined in the official problem statement.

### Confirmed Categories:
1. **Appointment:** Scheduling, rescheduling, cancellations, clinic location questions.
2. **Billing:** Invoices, insurance coverage, co-pay inquiries, payment receipts.
3. **Medication Refill:** Rx renewal requests, dosage check questions, pharmacy updates.
4. **Report Request:** Lab results requests, imaging reports, doctor notes, medical records.
5. **Technical Issue:** Patient portal login errors, app crashes, password resets.
6. **Urgent Review:** Severe administrative alerts, sudden escalation inquiries requiring fast intake.

*Note: Any additional categories proposed during engineering must be clearly designated as `[TBD]` and require senior developer approval before implementation.*

---

## 11. Urgency Classification Concept
Operational urgency defines the priority with which a message must be processed by staff.

- **Primary Conceptual Dimensions:**
  - `Routine`: Standard administrative queries with standard turnaround times (e.g., 24-48 hours).
  - `Urgent`: High-priority operational communications requiring immediate staff review (e.g., same-day turnaround).
- **Status:** `[CONCEPTUAL]` - Conceptual distinction established. Final label set, multi-class vs binary structure, and quantitative threshold boundaries remain `[TBD]` and will be finalized during Data Contract & ML Design.

---

## 12. Routing Concept
Based on the predicted category and urgency level, messages are dispatched to designated operational queues.

### Conceptual Destination Queues:
- `Appointment / Front Desk Queue`
- `Billing Department Queue`
- `Medical Records / Reports Queue`
- `Technical Support Queue`
- `Medication / Refill Workflow Queue`
- `Urgent Review Queue`
- `Human Review / Exception Queue` (Fallback)

*Status:* `[TBD]` - Routing matrix mapping `(Category, Urgency) -> Department Queue` will be established during system/data design.

---

## 13. Confidence and Human Review Concept

### Confidence Score Calculation
The model computes a normalized probability score $P(\text{class} \mid \text{message}) \in [0, 1]$ for both category and urgency predictions.

### Decision Boundary Logic:
$$\text{Routing Action} = \begin{cases} \text{Automated Department Routing}, & \text{if } \text{Confidence} \ge \tau \\ \text{Human Review Queue}, & \text{if } \text{Confidence} < \tau \end{cases}$$

Where $\tau$ represents the predefined confidence threshold.

*Status:* `[TBD]` - Numerical value of threshold $\tau$ (e.g., 0.75 or 0.80) and fallback mechanisms will be confirmed during ML experiment evaluation.

---

## 14. Data Concept
The dataset will consist of synthetic or de-identified patient-support communications to adhere to privacy and health data governance principles (HIPAA / GDPR).

### Conceptual Data Dictionary:
| Field Name | Type | Description | Sample Value | Classification |
|---|---|---|---|---|
| `message_id` | String / UUID | Unique identifier for the message | `MSG-10042` | `[CONFIRMED]` |
| `message_text` | Text | Raw content of patient support inquiry | *"I need to reschedule my Friday visit."* | `[CONFIRMED]` |
| `category` | Categorical | Ground-truth or predicted message topic | `Appointment` | `[CONFIRMED]` |
| `urgency` | Categorical | Ground-truth or predicted operational urgency | `Routine` | `[CONFIRMED]` |
| `department` | Categorical | Assigned operational department queue | `Front Desk` | `[CONFIRMED]` |
| `timestamp` | Datetime | Submission timestamp | `2026-09-18T10:15:00Z` | `[CONFIRMED]` |
| `confidence` | Float | Model prediction probability score | `0.92` | `[CONCEPTUAL]` |
| `requires_review` | Boolean | Flag indicating low-confidence review status | `FALSE` | `[CONCEPTUAL]` |

---

## 15. Machine Learning Concept
Supervised Natural Language Processing (NLP) multi-class classification will form the baseline core model.

### Candidate ML Algorithms under Evaluation:
1. **TF-IDF + Logistic Regression:** Strong baseline for text classification with direct probability calibration.
2. **TF-IDF + Naive Bayes (MultinomialNB):** Fast probabilistic classifier suitable for sparse text vectors.
3. **Linear Support Vector Machine (LinearSVC / SGDClassifier):** Effective high-dimensional margin classifier.
4. **Random Forest Classifier:** Ensembles tree-based patterns for robust feature interaction learning.
5. **Gradient Boosting / Other Justified Classifiers:** Advanced tabular/text ensemble baselines.

*Status:* `[TBD]` - Model selection, hyperparameter tuning, vectorizer parameters, and feature engineering pipelines are strictly deferred to the ML Design phase.

---

## 16. Evaluation Concept
Model evaluation will prioritize standard multi-class NLP metrics with explicit healthcare operational weighting.

### Primary Metrics:
- **Precision:** Measures prediction exactness across categories.
- **Recall (Sensitivity):** Critical metric, especially for `Urgent Review` class to minimize false negatives (missed urgent cases).
- **F1-Score (Macro & Weighted):** Balanced measure of precision and recall.
- **Confusion Matrix:** Detailed analysis of misclassification rates across category and urgency labels.

*Safety Metric Goal:* Maximize Recall on `Urgent Review` and high-urgency classes to prevent critical delays in staff awareness.

---

## 17. Explainability Concept
To build operational trust with healthcare personnel, predictions will include feature attribution:
- **Keyword / N-gram Highlighting:** Extract top positive TF-IDF features contributing to predicted class scores.
- **Rule / Reason Snippet:** Short rationale (e.g., *"Triggered by keywords: 'reschedule', 'Friday', 'appointment'"*).
- **Generative Summary (Secondary/Optional):** Concise non-authoritative summary generated for lengthy messages.

---

## 18. Healthcare Safety Boundary
The healthcare safety boundary is the foundational design constraint of PS-1:

> **CRITICAL BOUNDARY:** PS-1 is an administrative and operational message router. It operates strictly on organizational logistics. It does NOT make clinical diagnoses, evaluate medical emergencies, recommend treatments, or modify prescriptions.

1. **Non-Clinical Guarantee:** The ML model predicts operational queues, not medical diagnoses.
2. **Human-in-the-Loop Fallback:** Ambiguous, low-confidence, or borderline messages are routed to human operators.
3. **Safety Disclaimers:** All staff-facing UI components must present triage output as operational recommendations subject to staff verification.
4. **No LLM Hallucination Risk for Routing:** Core classification decisions MUST rely on deterministic or supervised statistical ML models, NOT unconstrained generative LLM output.

---

## 19. Functional Requirements Identified So Far

| Req ID | Description | Classification |
|---|---|---|
| `FR-01` | System shall ingest plain text patient support messages | `[CONFIRMED]` |
| `FR-02` | System shall classify messages into defined operational categories | `[CONFIRMED]` |
| `FR-03` | System shall classify operational urgency of messages | `[CONFIRMED]` |
| `FR-04` | System shall assign target operational department queues | `[CONFIRMED]` |
| `FR-05` | System shall calculate numerical confidence scores for predictions | `[CONFIRMED]` |
| `FR-06` | System shall flag low-confidence predictions for human review | `[CONFIRMED]` |
| `FR-07` | System shall support single message triage interface | `[CONFIRMED]` |
| `FR-08` | System shall support batch CSV file upload and processing | `[CONFIRMED]` |
| `FR-09` | System shall evaluate models using Recall, Precision, F1, and Confusion Matrix | `[CONFIRMED]` |
| `FR-10` | System shall provide short explanations for predictions | `[CONFIRMED]` |
| `FR-11` | System shall enforce non-clinical healthcare safety boundaries | `[CONFIRMED]` |
| `FR-12` | System may generate non-authoritative draft acknowledgments / summaries | `[CONCEPTUAL]` |
| `FR-13` | System shall maintain an operational audit trail of triage actions | `[CONCEPTUAL]` |

---

## 20. Requirements That Are Still TBD

| TBD ID | Topic | Description / Open Decision | Required Action |
|---|---|---|---|
| `TBD-01` | Final Urgency Schema | Binary (`Routine`/`Urgent`) vs Multi-class (`Low`/`Medium`/`High`/`Urgent`) | Resolve during ML Data Contract phase |
| `TBD-02` | Routing Matrix | Exact deterministic mapping from `(Category, Urgency)` to `Department Queue` | Formulate during System Architecture phase |
| `TBD-03` | Confidence Threshold ($\tau$) | Exact numerical value (e.g., 0.70, 0.80) for triggering Human Review | Determine post Model Validation experiments |
| `TBD-04` | ML Algorithm Selection | Final benchmark choice among TF-IDF + LogReg / Naive Bayes / SVM / RF | Conduct baseline ML benchmark evaluation |
| `TBD-05` | Dataset Generation / Schema | Specific synthetic dataset generator rules and exact database schema | Build during Data Engineering section |
| `TBD-06` | Tech Stack & Frameworks | Selection of Web framework (FastAPI/Flask), DB (SQLite/PostgreSQL), UI (Vite/React) | Establish in Architecture & Tech Selection phase |
| `TBD-07` | Explainability Engine | Choice of TF-IDF feature weights vs LIME/SHAP vs keyword extraction | Select during ML Interpretability task |

---

## 21. Scope of Section 1
The scope of Section 1 is strictly limited to:
- Comprehensive problem statement documentation and formalization.
- Defining operational boundaries and healthcare safety constraints.
- Cataloging confirmed, conceptual, and TBD requirements.
- Defining core workflow, input modes, classification concepts, and evaluation criteria.
- Establishing an unambiguous specification document for senior developer review.

---

## 22. Scope Explicitly Deferred to Later Sections
The following tasks are **strictly deferred** to future project phases and **MUST NOT** be initiated during Section 1:

1. **Section 2 — Functional Requirements & System Architecture Specification:** Detailed API contracts, system flow diagrams, data model schemas.
2. **Data Engineering & Dataset Creation:** Synthetic dataset generation, text pre-processing pipelines, data split creation.
3. **ML Model Engineering:** Feature extraction (TF-IDF), model selection, training, hyperparameter tuning, evaluation scripts, saving `.pkl`/`.joblib` model artifacts.
4. **Backend API Engineering:** FastAPI/Flask server setup, endpoint development (`/predict`, `/batch_predict`), middleware configuration.
5. **Database Development:** Database schema migrations, ORM setup, storage for logs/reviews.
6. **Frontend UI Development:** Dashboard, single input form, batch CSV dropzone, triage queue management UI.
7. **Generative AI Integration:** LLM prompt engineering for optional draft summaries.
8. **DevOps & Infrastructure:** Dockerization, CI/CD pipeline setup, deployment configuration.

---

*Document completed as required for Section 1 — Problem Statement Understanding.*
