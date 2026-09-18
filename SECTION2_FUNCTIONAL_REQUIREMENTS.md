# Section 2 — Functional Requirements Specification

**Project Title:** Patient Message Triage & Urgency Classifier (PS-1)  
**Track:** Healthcare & HealthTech  
**Author:** Implementation Engineer  
**Supervisor:** Senior Developer  
**Status:** Functional Requirements Specification (Approved)  
**Authoritative Foundation:** [SECTION1_PROBLEM_STATEMENT.md](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION1_PROBLEM_STATEMENT.md)  

---

## 1. Document Overview & Objective

### 1.1 Purpose
This document defines the formal **Functional Requirements Specification (FRS)** for **PS-1 — Patient Message Triage & Urgency Classifier**. It specifies **WHAT** the system must accomplish from a functional, behavioral, and operational standpoint, independent of specific technology, framework, database, model selection, or implementation choices.

### 1.2 Authoritative Source & Alignment
This specification directly derives from [SECTION1_PROBLEM_STATEMENT.md](file:///C:/Users/hp/.gemini/antigravity/scratch/patient-message-triage/SECTION1_PROBLEM_STATEMENT.md). All requirements defined herein strictly preserve the scope, operational intent, and safety boundaries of the official hackathon problem statement PS-1. No structural contradictions or unauthorized conversions of `[TBD]` items into final decisions are permitted.

---

## 2. Core Functional Architecture & Pipeline Flow

The functional system operates as a deterministic, confidence-aware operational pipeline processing patient-support messages from ingestion to routing.

```
+-------------------------------------------------------------------+
|                   1. Message Ingestion                            |
|             (Single Message / Batch CSV Input)                    |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                   2. Input Validation                             |
|       (Sanitization, Null Check, Empty Check, CSV Schema)         |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                   3. Text Processing                              |
|       (Standardized Preprocessing & Feature Transformation)       |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|              4. Request Category Classification                   |
|       (Multi-Class Operational Topic Prediction)                  |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|              5. Urgency Classification                            |
|       (Operational Priority & Turnaround Assessment)              |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|              6. Confidence Evaluation                             |
|       (Model Probability vs System Threshold Tau)                 |
+-------------------------------------------------------------------+
                                  |
             +--------------------+--------------------+
             |                                         |
   Confidence >= Tau                         Confidence < Tau
             |                                         |
             v                                         v
+--------------------------+               +--------------------------+
| 7. Department Routing    |               | 8. Human Review Queue    |
| (Target Department Queue)|               |  (Manual Triage Override)|
+--------------------------+               +--------------------------+
             |                                         |
             +--------------------+--------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|              9. Explanation & Output Generation                   |
|     (Feature Highlights + Optional Non-Authoritative GenAI)       |
+-------------------------------------------------------------------+
```

---

## 3. Detailed Functional Requirements

---

### FR-01: Message Ingestion Mode Support
*Requirement Classification:* `[CONFIRMED]`

The system shall support two distinct input ingestion modes for incoming patient-support communications:

#### 1.1 Single Message Mode
- The system must accept an individual patient-support message provided via staff interface or API.
- The input shall consist of raw text representing the patient inquiry, along with optional metadata (e.g., `message_id`, `timestamp`).
- The system shall process the message in real time and return a structured response payload.

#### 1.2 Batch CSV Mode
- The system must accept a structured CSV file upload containing multiple patient-support messages.
- The input CSV must contain at minimum a message text field per row, with optional row identifiers and timestamps.
- The system shall iterate over valid rows, execute the triage pipeline per record, preserve row-level order and correlation, and return a structured bulk result object.

---

### FR-02: Input Data Validation
*Requirement Classification:* `[CONFIRMED]`

The system must validate all incoming data before passing it to text processing or classification.

#### 2.1 Validation Rules
- **Empty / Null Message Guard:** The system shall detect and reject messages containing empty strings, whitespace-only content, or `NULL` values.
- **Data Type Enforcement:** The system shall verify that message text fields contain valid text strings. Non-string types (e.g., numeric, binary) must be flagged as invalid.
- **CSV Structure Verification:** For CSV uploads, the system shall verify that the file is correctly formatted CSV data, non-empty, and includes the designated header column for message text.
- **Row-Level Integrity:** In batch mode, invalid or unparseable individual rows must be flagged as errors without aborting the entire batch file execution.

#### 2.2 Rejection Behavior
- The system shall return clear, non-cryptic error indicators for rejected inputs, categorizing them as `Invalid Input` state.

---

### FR-03: Text Processing Standardization
*Requirement Classification:* `[CONFIRMED]` *(Exact preprocessing algorithm marked `[TBD]`)*

The system shall transform valid raw text into a standardized representation suitable for downstream model inference.

#### 3.1 Preprocessing Consistency
- Preprocessing executed during inference must strictly mirror the transformations applied during offline model training to prevent distribution skew.
- Raw text transformation shall safely handle punctuation, case normalization, whitespace stripping, and encoding anomalies (e.g., UTF-8 sanitization).

#### 3.2 Exception Handling
- If text processing encounters unparseable tokens or encoding failures, the system shall intercept the error gracefully and route the message state to `Processing Failure` rather than throwing an unhandled exception.

---

### FR-04: Request Category Classification
*Requirement Classification:* `[CONFIRMED]` *(Additional categories marked `[TBD]`)*

The system shall classify the primary operational topic of each valid patient message.

#### 4.1 Established Operational Categories
The system shall categorize messages into the following core operational categories established by PS-1:
1. **Appointment:** Inquiries regarding scheduling, rescheduling, clinic hours, locations, or visit cancellations.
2. **Billing:** Inquiries regarding invoices, co-pays, insurance coverage, payment receipts, or financial assistance.
3. **Medication Refill:** Requests for prescription renewals, refill authorizations, pharmacy updates, or dosage clarifications.
4. **Report Request:** Requests for lab results, imaging diagnostic reports, immunization records, or physician chart notes.
5. **Technical Issue:** Technical problems regarding patient portal access, password resets, app errors, or digital forms.
6. **Urgent Review:** Operational messages containing time-sensitive inquiries or rapid escalation requests.

#### 4.2 Schema Governance
- Any additional category (e.g., `General Inquiry` or `Other`) is designated as `[TBD]` and requires senior developer and data contract approval prior to schema inclusion.

---

### FR-05: Operational Urgency Classification
*Requirement Classification:* `[CONCEPTUAL]` *(Schema & Thresholds marked `[TBD — ML/Data Design]`)*

The system shall evaluate the operational urgency level of each processed message.

#### 5.1 Independent Functional Dimension
- Operational urgency shall be evaluated as an independent functional dimension alongside request categorization.
- Urgency reflects staff turnaround requirements (e.g., same-day urgent intake vs standard 24–48 hour routine handling).

#### 5.2 Schema Deferral
- The exact target label schema (binary `Routine`/`Urgent` vs multi-class `Low`/`Medium`/`High`/`Urgent`) remains `[TBD — ML/Data Design]` and shall be finalized during the data contract phase.

---

### FR-06: Model Prediction Confidence Evaluation
*Requirement Classification:* `[CONFIRMED]` *(Calculation method marked `[TBD]`)*

The system shall compute and expose numerical confidence scores for all model predictions.

#### 6.1 Confidence Coverage
- The system must generate a normalized confidence score $P \in [0.0, 1.0]$ for the category prediction.
- If urgency classification is implemented via probabilistic model, an urgency confidence score shall also be generated.

#### 6.2 Safeguard Role
- The confidence score shall act as the quantitative decision variable for automated department routing vs human review escalation.

---

### FR-07: Low-Confidence Human Review Escalation
*Requirement Classification:* `[CONFIRMED]` *(Threshold $\tau$ marked `[TBD]`)*

The system shall enforce an operational safeguard by routing low-confidence predictions to human review.

#### 7.1 Decision Logic
- If the prediction confidence score is below a designated system threshold $\tau$ ($P < \tau$), the system shall flag the message with `requires_human_review = TRUE`.
- The message shall be dispatched to the **Human Review Queue** instead of an automated department queue.

#### 7.2 Non-Deceptive Reporting
- Low-confidence predictions must never be presented to staff as definitive or unconditionally correct.

---

### FR-08: Department Queue Routing
*Requirement Classification:* `[CONFIRMED]` *(Routing Matrix marked `[TBD]`)*

The system shall assign an operational destination queue for every validly processed message.

#### 8.1 Conceptual Department Queues
- **Front Desk / Appointment Queue**
- **Billing Department Queue**
- **Medical Records / Reports Queue**
- **Technical Support Queue**
- **Medication & Refill Workflow Queue**
- **Urgent Review Queue**
- **Human Review / Triage Override Queue** (Fallback)

#### 8.2 Matrix Routing Rule
- The routing assignment shall be determined by combining predicted `Category` and `Urgency`.
- The exact mapping lookup matrix `(Category, Urgency) -> Destination Queue` is marked `[TBD]` and will be established during system design.

---

### FR-09: Structured Output Payload Format
*Requirement Classification:* `[CONFIRMED]`

For every processed message, the system shall output a standardized, structured JSON/dictionary result.

#### 9.1 Mandatory Payload Fields `[CONFIRMED]`
- `message_id`: Unique identifier for the input message.
- `predicted_category`: Assigned operational category label.
- `predicted_urgency`: Assigned operational urgency label.
- `confidence_score`: Float value between `0.0` and `1.0`.
- `assigned_queue`: Destination operational queue.
- `requires_human_review`: Boolean flag (`TRUE` / `FALSE`).
- `status`: Execution state (`SUCCESS`, `LOW_CONFIDENCE`, `INVALID_INPUT`, `PROCESSING_FAILURE`).

#### 9.2 Optional / Secondary Fields `[CONCEPTUAL]`
- `explanation_highlights`: Extracted feature keywords or token attributions.
- `case_summary`: Optional short non-authoritative message summary.
- `draft_response`: Optional non-authoritative templated acknowledgement draft.

---

### FR-10: Prediction Explainability & Keyword Attribution
*Requirement Classification:* `[CONCEPTUAL]` *(Method marked `[TBD — Explainability Design]`)*

The system shall provide supporting evidence to explain model predictions.

#### 10.1 Attribution Boundaries
- The explanation must highlight key terms, n-grams, or feature weights that strongly influenced the category and urgency scores.
- Explanations serve strictly as supporting metadata for human operators and shall **never** override the core model's classification output.

---

### FR-11: Batch CSV Processing & Traceability
*Requirement Classification:* `[CONFIRMED]`

The system shall provide full batch execution capabilities for multi-message files.

#### 11.1 Execution Pipeline
1. Ingest CSV file and validate structural integrity.
2. Filter out malformed rows while recording row index error references.
3. Process valid message rows sequentially or concurrently through the core triage engine.
4. Generate category, urgency, confidence, routing, and review flags for each row.
5. Maintain 1-to-1 row index mapping and output an aggregated batch summary alongside row-level results.

---

### FR-12: System State & Error Classification
*Requirement Classification:* `[CONFIRMED]`

The system must explicitly distinguish between four functional execution states:

| System State | Condition | System Action |
|---|---|---|
| `SUCCESS` | Message valid, confidence $\ge \tau$ | Route to target department queue automatically |
| `LOW_CONFIDENCE` | Message valid, confidence $< \tau$ | Set `requires_human_review = TRUE`, route to Human Review Queue |
| `INVALID_INPUT` | Empty text, bad CSV, wrong data type | Reject input, return validation error payload |
| `PROCESSING_FAILURE` | Text encoding error, pipeline failure | Intercept exception, log error state, flag for system administrator |

---

### FR-13: Output Validation & Schema Enforcement
*Requirement Classification:* `[CONFIRMED]`

The system shall enforce strict schema boundaries on all outputs.
- Predicted `category` must belong strictly to the enumerated allowed category list.
- Predicted `urgency` must belong strictly to the enumerated allowed urgency list.
- Assigned `queue` must belong strictly to the enumerated allowed department queues.
- Out-of-vocabulary or unknown labels must trigger output validation failure.

---

### FR-14: Operational Auditability & Logging
*Requirement Classification:* `[CONCEPTUAL]` *(Logging schema marked `[TBD — Architecture/Security]`)*

The system shall record operational execution events to support quality auditability and performance evaluation.

#### 14.1 Log Scope
- The system must capture message predictions, confidence scores, queue assignments, and human review overrides.
- All logging must comply with healthcare privacy guidelines (HIPAA/GDPR) by avoiding unnecessary long-term storage of raw patient identifiers or unmasked protected health information (PHI).

---

### FR-15: Optional Downstream Generative AI Integration
*Requirement Classification:* `[CONCEPTUAL]` *(Architecture marked `[TBD — Technology Architecture]`)*

The system may optionally integrate a downstream generative AI component for administrative convenience.

#### 15.1 Permitted Scope
- Generating a 1-sentence concise case summary for long patient messages.
- Generating a draft acknowledgement response template for staff review.

#### 15.2 Strict Architectural Restriction
- The generative AI component **MUST NOT** perform categorization, assign urgency, determine routing, or evaluate confidence.
- The generative AI component **MUST NOT** override classifier predictions or make medical determinations.

---

### FR-16: Healthcare Safety Boundary Enforcement
*Requirement Classification:* `[CONFIRMED]`

The system is strictly an **operational message router** for healthcare administration.

#### 16.1 Non-Clinical Directives
- The system **SHALL NOT** perform medical diagnosis or infer health conditions.
- The system **SHALL NOT** recommend clinical treatments or medical procedures.
- The system **SHALL NOT** issue, modify, or authorize pharmaceutical prescriptions.
- The system **SHALL NOT** replace clinical emergency triage protocols (e.g., ESI).
- Messages containing severe medical symptoms must be routed strictly according to operational rules (`Urgent Review Queue` or `Human Review Queue`) for immediate clinical staff attention, without automated clinical diagnosis.

---

## 4. Single-Message Functional Workflow Flowchart

```
  [User Submits Single Message]
               |
               v
   < Is Input Valid Text? > -------------------------> (NO) ---> [Return INVALID_INPUT Error]
               |
             (YES)
               v
  [Execute Text Processing Pipeline]
               |
               v
  [Model Inferences Category & Urgency]
               |
               v
  [Compute Model Confidence Score P]
               |
               v
      < Is P >= Threshold Tau? >
        /                    \
     (YES)                   (NO)
      /                        \
     v                          v
[Assign Dept Queue]     [Flag Human Review = TRUE]
     |                          |
     |                  [Route Human Review Queue]
     \                          /
      v                        v
  [Format Structured Response Payload]
               |
               v
    [Return Result to User/API]
```

---

## 5. Batch CSV Functional Workflow Flowchart

```
  [User Uploads CSV File]
               |
               v
    < Is CSV File Valid? > --------------------------> (NO) ---> [Return File Validation Error]
               |
             (YES)
               v
  [Extract Message Column Rows]
               |
               v
  [Loop: For Each Row (Index i)]
               |
    +----------+----------+
    |                     |
<Valid Row?>        <Invalid Row?>
    |                     |
  (YES)                 (NO)
    |                     |
[Process Triage]    [Record Row Error State]
    |                     |
[Assign Queue]            |
    \                     /
     +---------+---------+
               |
               v
  < More Rows Remaining? > --(YES)--> [Next Row]
               |
              (NO)
               v
  [Assemble Aggregated Batch Payload]
               |
               v
  [Return Batch Execution Report & Download]
```

---

## 6. Functional Requirements Traceability Matrix

| Req ID | Requirement Title | Category | Status | Target Phase |
|---|---|---|---|---|
| `FR-01` | Message Ingestion Support | Ingestion | `[CONFIRMED]` | System Architecture |
| `FR-02` | Input Data Validation | Validation | `[CONFIRMED]` | Backend Engineering |
| `FR-03` | Text Processing Pipeline | Preprocessing | `[CONFIRMED]` | ML Engineering |
| `FR-04` | Request Category Classification | Intelligence | `[CONFIRMED]` | ML Engineering |
| `FR-05` | Operational Urgency Classification | Intelligence | `[CONCEPTUAL]` | ML/Data Design (`[TBD]`) |
| `FR-06` | Confidence Score Calculation | Safeguard | `[CONFIRMED]` | ML Engineering |
| `FR-07` | Human Review Escalation | Safeguard | `[CONFIRMED]` | Workflow Engineering |
| `FR-08` | Department Queue Routing | Logistics | `[CONFIRMED]` | Architecture (`[TBD]`) |
| `FR-09` | Structured Output Payload | Interface | `[CONFIRMED]` | API Engineering |
| `FR-10` | Prediction Explainability | Transparency | `[CONCEPTUAL]` | ML Interpretability (`[TBD]`) |
| `FR-11` | Batch CSV Processing | Ingestion | `[CONFIRMED]` | Backend Engineering |
| `FR-12` | System State & Error Classification | Reliability | `[CONFIRMED]` | API Engineering |
| `FR-13` | Output Schema Validation | Reliability | `[CONFIRMED]` | Backend Engineering |
| `FR-14` | Operational Audit Logging | Operations | `[CONCEPTUAL]` | Security Design (`[TBD]`) |
| `FR-15` | Optional Downstream GenAI | Assistance | `[CONCEPTUAL]` | Tech Selection (`[TBD]`) |
| `FR-16` | Healthcare Safety Enforcement | Safety | `[CONFIRMED]` | Core System Boundary |

---

## 7. Scope Boundaries & Deferrals for Section 2

### 7.1 Scope of Section 2
Section 2 is strictly limited to formalizing functional behavior (WHAT the system must do).

### 7.2 Deferral to Subsequent Sections
The following engineering tasks remain strictly deferred to subsequent project phases:
1. **Section 3 — Data Contract & Data Architecture:** Dataset creation, synthetic generation, exact schema definitions.
2. **Section 4 — System Architecture & Tech Stack:** Selecting web frameworks (FastAPI/Flask), database engine (SQLite/PostgreSQL), ORM, UI components.
3. **Section 5 — Machine Learning Model Engineering:** Model selection, vectorization, hyperparameter tuning, model serializations (`.joblib`/`.pkl`).
4. **Section 6 — API & Application Implementation:** Coding endpoints, routing logic, ORM models, frontend UI components.

---

*Document complete and approved for Section 2 — Functional Requirements Specification.*
