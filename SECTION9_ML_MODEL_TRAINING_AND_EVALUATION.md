# Section 9 — Machine Learning Model Training & Evaluation

**Project Title:** Patient Message Triage & Urgency Classifier (PS-1)  
**Track:** Healthcare & HealthTech  
**Author:** Implementation & Research Engineer  
**Supervisor:** Senior Software Architect  
**Status:** Completed & Validated Specification  
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

---

## 1. Executive Summary

Section 9 realizes the complete training, cross-validated tuning, calibration, operational confidence threshold optimization, and final unseen evaluation of the dual machine learning models for **PS-1: Patient Message Triage & Urgency Classifier**.

Executing under the rigorous protocols established in Sections 7 and 8:
1. The system ingested the sealed, stratified dataset partitions (`data/splits/train.csv` [630], `validation.csv` [135], and `test.csv` [135]).
2. The NLP preprocessing pipeline and TF-IDF feature extractor were fitted strictly on the training partition, guaranteeing zero vocabulary or target leakage.
3. Three candidate algorithms (**Logistic Regression**, **Linear Support Vector Classifier**, and **Multinomial Naive Bayes**) were systematically benchmarked on the validation partition across both Category (6-class) and Urgency (binary) prediction tasks.
4. **Multinomial Logistic Regression** with balanced class weighting was selected as the superior architecture for both classification heads based on cross-validated Macro F1 and Urgent Recall, providing native probabilistic calibration without requiring auxiliary post-hoc fitting.
5. The joint confidence system ($C_{\text{overall}} = \min(C_{\text{cat}}, C_{\text{urg}})$) was tuned across candidate thresholds $\tau \in [0.60, 0.90]$ on the validation partition. Under the healthcare safety mandate of **zero false negatives on urgent inquiries auto-routed** while satisfying an operational review capacity $\le 25\%$, the optimal threshold was selected as **$\tau = 0.70$** (validation routing coverage: 80.0%, human review rate: 20.0%, missed urgent auto-routed cases: 0).
6. Final evaluation on the untouched test partition ($N=135$), executed strictly once, yielded:
   - **Category Macro F1:** $1.0000$ (Accuracy: $100\%$)
   - **Urgent Recall (Primary Healthcare Safety Metric):** $1.0000$ ($100\%$ detection of true urgent messages)
   - **Urgency Brier Score:** $0.0341$ (demonstrating outstanding posterior probability calibration)
   - **Test Routing Coverage:** $77.04\%$ ($104/135$ messages auto-routed)
   - **Test Human Review Rate:** $22.96\%$ ($31/135$ messages escalated to staff review)
   - **Missed Urgent Auto-Routed Messages:** $0$ ($0.00\%$)
7. All model artifacts and comprehensive provenance manifests were packaged into `models/v1.0.0/`, supported by a $100\%$ passing automated test suite (26 unit tests).

> **CRITICAL HEALTHCARE SAFETY BOUNDARY:** This machine learning system functions exclusively as an operational and administrative triage assistant. It does **NOT** provide clinical diagnoses, recommend pharmacological therapies, prescribe dosages, or replace licensed emergency medical triage.

---

## 2. Dataset Ingestion & Split Verification

The training and evaluation pipeline ingests the sealed dataset generated and quality-audited in Section 8:

| Partition | Row Count | Percentage | Class Balance (Category) | Class Balance (Urgency) | File Path |
|---|---|---|---|---|---|
| **Train** | 630 | 70.0% | 105 per category (6 classes) | 441 Routine (70%), 189 Urgent (30%) | `data/splits/train.csv` |
| **Validation** | 135 | 15.0% | 22–23 per category | 94 Routine (69.6%), 41 Urgent (30.4%) | `data/splits/validation.csv` |
| **Test** | 135 | 15.0% | 22–23 per category | 95 Routine (70.4%), 40 Urgent (29.6%) | `data/splits/test.csv` |
| **Total** | 900 | 100.0% | 150 per category | 630 Routine (70%), 270 Urgent (30%) | `data/processed/dataset_clean.csv` |

All records conform to Data Quality contracts DQ-01 through DQ-16, with null values = 0 and PII contamination = 0.

---

## 3. NLP Text Preprocessing Pipeline

The text preprocessing engine is implemented in `src/ml/preprocessing.py` as `TextPreprocessor`. It applies controlled normalization to preserve operational intent without semantic stripping:

1. **Unicode NFKD Normalization:** Standardizes multi-byte accents and special characters.
2. **Entity Normalization / Masking:**
   - Emails: Replaced with token `__email__`
   - URLs: Replaced with token `__url__`
   - Phone Numbers: Replaced with token `__phone__`
   - Long Numerical IDs ($\ge 4$ digits): Replaced with token `__num__`
3. **Contraction Expansion:** Resolves 20 common contractions (`can't` $\to$ `can not`, `won't` $\to$ `will not`, `don't` $\to$ `do not`, etc.) to preserve negation words critical for urgency assessment.
4. **Case Normalization:** Converts text to lowercase.
5. **Controlled Punctuation Sanitization:** Preserves operational markers (`$`, `?`, `!`, `.`, `-`, `#`) while stripping noisy symbols.
6. **Whitespace Normalization:** Collapses consecutive spaces into a single blank.

---

## 4. TF-IDF Feature Extraction & Anti-Leakage Verification

Feature extraction is implemented in `src/ml/features.py` as `TfidfFeatureExtractor`.

### 4.1 Hyperparameters
- **N-gram Range:** $(1, 2)$ (unigrams and bigrams, e.g., *"chest pain"*, *"refill prescription"*, *"portal app"*)
- **Minimum Document Frequency (`min_df`):** $2$ (suppresses idiosyncratic singletons)
- **Maximum Document Frequency (`max_df`):** $0.85$ (filters corpus-wide stop words)
- **Maximum Features:** $2,500$
- **Sublinear Term Frequency:** `True` (applies logarithmic scaling $1 + \log(\text{tf})$ to dampen word repetition)
- **Norm:** L2 normalization

### 4.2 Anti-Leakage Architecture
- `fit_transform()` is invoked strictly on `X_train_clean`.
- `transform()` is invoked on `X_val_clean` and `X_test_clean`.
- Verified vocabulary size: **2,500 features**. Zero test-set vocabulary influenced the vector space representation.

---

## 5. Candidate Models & Hyperparameter Spaces

In accordance with Section 7, three algorithms representing diverse inductive biases were implemented in `src/ml/models.py`:

```
1. Multinomial Logistic Regression (C in [1.0, 2.0, 0.5, 5.0, 0.1], class_weight in ['balanced', None])
2. Linear Support Vector Machine (C in [1.0, 0.5, 0.1, 2.0, 0.05], class_weight in ['balanced', None])
3. Multinomial Naive Bayes (alpha in [0.1, 0.05, 0.01, 0.5, 1.0])
```

---

## 6. Candidate Evaluation on Validation Partition

The candidates were benchmarked on the 135 validation samples:

### 6.1 Category Model Benchmarks

| Candidate Model | Validation Accuracy | Validation Macro F1 | Validation Weighted F1 | Selection Status |
|---|---|---|---|---|
| **Logistic Regression** | **1.0000** | **1.0000** | **1.0000** | **WINNER (Selected)** |
| LinearSVC | 1.0000 | 1.0000 | 1.0000 | Secondary Candidate |
| MultinomialNB | 1.0000 | 1.0000 | 1.0000 | Baseline Candidate |

*Primary Selection Metric:* Macro F1 on validation partition.

### 6.2 Urgency Model Benchmarks

| Candidate Model | Validation Accuracy | Urgent Recall | Urgent Precision | Urgent F1 | Macro F1 | Selection Status |
|---|---|---|---|---|---|---|
| **Logistic Regression** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **WINNER (Selected)** |
| LinearSVC | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | Secondary Candidate |
| MultinomialNB | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | Baseline Candidate |

*Primary Selection Metric:* Urgent Recall on validation partition (Zero False Negatives priority).

Report artifact saved to: `reports/model_comparison.csv`.

---

## 7. Winning Model Selection & Selection Justifications

**Selected for Category:** `LogisticRegression(C=1.0, class_weight='balanced')`  
**Selected for Urgency:** `LogisticRegression(C=1.0, class_weight='balanced')`

### Technical Justifications:
1. **Direct Posterior Calibration:** Unlike LinearSVC (which outputs signed hyperplane distances and requires secondary Platt scaling via `CalibratedClassifierCV`) and MultinomialNB (which exhibits extreme overconfidence near 0 and 1 due to word independence assumptions), Logistic Regression natively produces well-calibrated posterior probabilities through the logistic and softmax link functions.
2. **Deterministic Interpretability:** Logistic Regression weights $W_{k, j}$ provide direct, exact linear feature attribution ($x_j \cdot W_{k, j}$) without requiring approximations like LIME or kernel SHAP.
3. **Execution Latency:** Sub-millisecond CPU inference latency (<1ms per request), satisfying the real-time operational triage SLA (<500ms total API response).

---

## 8. Hyperparameter Optimization & Best Estimators

5-fold Stratified Cross-Validation was performed on the `Train` split using `GridSearchCV`:
- **Category Tuning:** Metric: `f1_macro`. Best parameters: `{'C': 1.0, 'class_weight': 'balanced'}`.
- **Urgency Tuning:** Metric: `recall` (with `pos_label="Urgent"`). Best parameters: `{'C': 1.0, 'class_weight': 'balanced'}`.

---

## 9. Probability Calibration & Platt Scaling Analysis

Because Logistic Regression was selected for both tasks, native probabilistic outputs were utilized. Calibration quality was audited using Brier Score Loss:
$$\text{BS} = \frac{1}{N} \sum_{i=1}^N (P_i - y_i)^2$$

- **Test Partition Brier Score:** **0.0341**
- An empirical Brier score of $0.0341$ confirms that predicted probabilities closely match empirical ground truth frequencies, providing reliable confidence signals for operational gating.

---

## 10. Confidence Scoring Architecture & Bottleneck Aggregation

The operational confidence system implements the conservative bottleneck aggregation policy defined in Section 7:

$$C_{\text{cat}} = \max_{k \in \{1 \dots 6\}} P(\text{category} = k \mid x)$$
$$C_{\text{urg}} = \max_{u \in \{\text{Routine}, \text{Urgent}\}} P(\text{urgency} = u \mid x)$$
$$C_{\text{overall}} = \min(C_{\text{cat}}, C_{\text{urg}})$$

### Architectural Rationale:
If the model is 95% confident the category is `Billing`, but only 62% confident whether the urgency is `Routine` or `Urgent`, the operational action remains uncertain. Taking the minimum guarantees that ambiguity on *either* dimension immediately triggers escalation to the Human Review Queue.

---

## 11. Confidence Threshold ($\tau$) Optimization

Threshold optimization was conducted exclusively on the Validation partition across candidate values $\tau \in [0.60, 0.90]$ with step size $0.02$:

### 11.1 Validation Threshold Evaluation Grid

| Threshold $\tau$ | Routing Coverage | Human Review Rate | Auto-Routed Cases | Human Review Cases | Missed Urgent Auto-Routed |
|---|---|---|---|---|---|
| 0.60 | 94.07% | 5.93% | 127 | 8 | 0 |
| 0.62 | 89.63% | 10.37% | 121 | 14 | 0 |
| 0.64 | 88.89% | 11.11% | 120 | 15 | 0 |
| 0.66 | 86.67% | 13.33% | 117 | 18 | 0 |
| 0.68 | 85.19% | 14.81% | 115 | 20 | 0 |
| **0.70** | **80.00%** | **20.00%** | **108** | **27** | **0** |
| 0.72 | 68.15% | 31.85% | 92 | 43 | 0 |
| 0.74 | 62.22% | 37.78% | 84 | 51 | 0 |
| 0.76 | 54.81% | 45.19% | 74 | 61 | 0 |
| 0.78 | 48.15% | 51.85% | 65 | 70 | 0 |
| 0.80 | 34.07% | 65.93% | 46 | 89 | 0 |
| 0.82 | 24.44% | 75.56% | 33 | 102 | 0 |
| 0.84 | 9.63% | 90.37% | 13 | 122 | 0 |
| 0.86 | 2.22% | 97.78% | 3 | 132 | 0 |
| 0.88 | 1.48% | 98.52% | 2 | 133 | 0 |
| 0.90 | 0.00% | 100.00% | 0 | 135 | 0 |

### 11.2 Optimal Threshold Selection Policy:
Under the Section 7 SLA policy:
1. $100\%$ Recall on validation Urgent cases (zero missed urgent auto-routed cases).
2. Human review rate $\le 25\%$ (routing coverage $\ge 75\%$).
3. Maximize $\tau$ within the feasible set to ensure the most safety-conservative gating.

**Selected Optimal Threshold:** **$\tau = 0.70$**  
- Validation Routing Coverage: **80.0%** (108/135 cases)  
- Validation Human Review Rate: **20.0%** (27/135 cases)  
- Missed Urgent Inquiries: **0**

---

## 12. Final Evaluation on Untouched Test Set

Following final model freeze and threshold selection, the system was evaluated **strictly once** on the untouched test partition ($N=135$):

### 12.1 Category Classification Metrics
- **Accuracy:** $1.0000$ ($100.0\%$)
- **Macro Precision:** $1.0000$
- **Macro Recall:** $1.0000$
- **Macro F1 Score:** $1.0000$
- **Weighted F1 Score:** $1.0000$

### 12.2 Urgency Classification Metrics
- **Accuracy:** $1.0000$ ($100.0\%$)
- **Urgent Recall (Primary Healthcare Safety Metric):** **$1.0000$** ($40/40$ true urgent cases detected)
- **Urgent Precision:** $1.0000$
- **Urgent F1 Score:** $1.0000$
- **Routine Recall:** $1.0000$ ($95/95$ routine cases detected)
- **Routine Precision:** $1.0000$
- **Routine F1 Score:** $1.0000$
- **Macro F1 Score:** $1.0000$
- **Brier Score:** **$0.0341$**

### 12.3 Operational Confidence & Human Review Escalation Metrics ($\tau = 0.70$)
- **Test Routing Coverage:** **$77.04\%$** ($104/135$ messages auto-routed)
- **Test Human Review Rate:** **$22.96\%$** ($31/135$ messages escalated to staff review)
- **Missed Urgent Cases Auto-Routed:** **$0$** ($0.00\%$)

---

## 13. Per-Class Performance Breakdown

Detailed test set performance across all 6 operational categories and 2 urgency levels:

| Target Class | Support | Precision | Recall | F1 Score | Confusion Errors |
|---|---|---|---|---|---|
| **Appointment** | 23 | 1.0000 | 1.0000 | 1.0000 | 0 |
| **Billing** | 22 | 1.0000 | 1.0000 | 1.0000 | 0 |
| **Medication Refill** | 23 | 1.0000 | 1.0000 | 1.0000 | 0 |
| **Report Request** | 22 | 1.0000 | 1.0000 | 1.0000 | 0 |
| **Technical Issue** | 22 | 1.0000 | 1.0000 | 1.0000 | 0 |
| **Urgent Review** | 23 | 1.0000 | 1.0000 | 1.0000 | 0 |
| **Urgency: Routine** | 95 | 1.0000 | 1.0000 | 1.0000 | 0 |
| **Urgency: Urgent** | 40 | 1.0000 | 1.0000 | 1.0000 | 0 |

---

## 14. Confusion Matrix Analysis

All confusion matrix visualizations were rendered via Matplotlib and saved to `reports/confusion_matrices/`:

1. **Category Validation Matrix:** `reports/confusion_matrices/category_validation_cm.png` (Diagonal: 23, 23, 23, 22, 22, 22; Off-diagonal: all 0).
2. **Urgency Validation Matrix:** `reports/confusion_matrices/urgency_validation_cm.png` (TN: 94, FP: 0, FN: 0, TP: 41).
3. **Category Test Matrix:** `reports/confusion_matrices/category_test_cm.png` (Diagonal: 23, 22, 23, 22, 22, 23; Off-diagonal: all 0).
4. **Urgency Test Matrix:** `reports/confusion_matrices/urgency_test_cm.png` (TN: 95, FP: 0, FN: 0, TP: 40).

---

## 15. Qualitative Error Analysis

The test partition was scanned for classification errors:
- **Misclassified Test Instances:** **0**
- Output file: `reports/error_analysis.csv` (contains zero error records).
- **Sub-Threshold Escalations Analysis:**
  While zero cases were misclassified, **31 cases** had $C_{\text{overall}} < 0.70$ and were escalated to the Human Review Queue. These cases typically contained multi-topic or blended operational inquiries (e.g., asking about an upcoming appointment schedule while simultaneously inquiring about a past billing statement). Escalating these 31 cases validates the effectiveness of the conservative bottleneck confidence system.

---

## 16. Feature Attribution & Explainability Engine

Implemented in `src/ml/explainability.py` as `FeatureExplainer`. It extracts direct linear feature weights:
$$\text{Score}(j, k) = x_j \cdot W_{k, j}$$

### Sample Explainability Verification:
- **Input Text:** *"hello it support the mobile portal app crashes every time i try to submit my pre..."*
- **Predicted Category:** `Technical Issue`
- **Top 5 Contributing Keywords:**
  1. `mobile` ($+0.1493$)
  2. `support` ($+0.1069$)
  3. `app` ($+0.1025$)
  4. `browser` ($+0.0907$)
  5. `portal` ($+0.0904$)

All feature attributions are deterministic, mathematically grounded, and strictly free from generative LLM hallucination.

---

## 17. Model Artifact Packaging & Metadata Manifest

All model artifacts are stored in `models/v1.0.0/`:

```
models/v1.0.0/
├── tfidf_vectorizer.joblib     # Serialized TF-IDF vectorizer (2,500 features)
├── category_model.joblib       # Serialized LogisticRegression (6 classes)
├── urgency_model.joblib        # Serialized LogisticRegression (binary)
└── metadata.json               # Complete training provenance manifest
```

### Metadata Manifest Structure (`metadata.json`):
- `model_version`: `"v1.0.0"`
- `dataset_version`: `"v1.0.0"`
- `training_seed`: `42`
- `training_timestamp`: `"2026-09-18T06:22:31.249791+00:00"`
- `sklearn_version`: `"1.9.1"`
- `python_version`: `"3.14.4"`
- `feature_count`: `2500`
- `confidence_system`: `{"selected_tau": 0.7, "aggregation_formula": "C_overall = min(C_cat, C_urg)"}`

---

## 18. Backward Compatibility & System Invariants Verification

- [x] **Invariant 1: Zero Target/Vocabulary Leakage:** TF-IDF vocabulary fitted exclusively on Train split.
- [x] **Invariant 2: Conservative Bottleneck Confidence:** $C_{\text{overall}} = \min(C_{\text{cat}}, C_{\text{urg}})$ strictly enforced.
- [x] **Invariant 3: Single Test Set Evaluation:** Test split evaluated exactly once after all tuning was frozen.
- [x] **Invariant 4: Reproducibility Seed:** `random_state=42` pinned across all candidate initializations and cross-validation splits.
- [x] **Invariant 5: Healthcare Safety Boundary:** Strictly non-clinical operational triage.

---

## 19. Performance vs Acceptance Criteria

| Metric / Objective | Acceptance Target (Section 7) | Achieved Test Result | Status |
|---|---|---|---|
| Category Macro F1 | $\ge 0.85$ | **1.0000** | **EXCEEDED** |
| Urgent Recall | $\ge 0.95$ (Safety critical) | **1.0000** | **EXCEEDED** |
| Urgency Brier Score | $\le 0.15$ | **0.0341** | **EXCEEDED** |
| Routing Coverage | $\ge 75\%$ | **77.04%** | **PASSED** |
| Human Review Rate | $\le 25\%$ | **22.96%** | **PASSED** |
| Missed Urgent Auto-Routed | **0** | **0** | **PASSED** |
| Inference Latency | $< 50\text{ms}$ | **< 1ms** | **EXCEEDED** |

---

## 20. Operational & Latency Benchmarks

- **Vectorization Latency:** $\sim 0.25\text{ms}$ per message
- **Inference Latency (Dual Models):** $\sim 0.35\text{ms}$ per message
- **Total ML Inference Time:** $\sim 0.60\text{ms}$ per message
- **Memory Footprint:** $\sim 14\text{MB}$ in RAM for all serialized artifacts
- **Cold Start Load Time:** $\sim 45\text{ms}$ via `joblib.load`

---

## 21. Limitations, Edge Cases, & Known Risks

1. **Synthetic Vocabulary Domain:** Models were trained on controlled synthetic patient messages. While engineered with comprehensive vocabulary variations, real-world clinical portal messages may exhibit unstructured colloquialisms or spelling corruptions.
2. **Ambiguous Multi-Intent Inquiries:** Messages presenting equal weight between two operational categories are caught by the confidence threshold ($\tau = 0.70$) and routed to the Human Review Queue.
3. **Out-of-Vocabulary (OOV) Terms:** Handled gracefully by TF-IDF vectorizer ignoring unknown tokens, with the lower posterior probability naturally triggering human review.

---

## 22. Technical Debt & Future Improvements

1. **Active Learning Feedback Loop:** Future iterations in Section 11/12 should incorporate human reviewer edits from the Human Review Queue into an incremental training store.
2. **Sub-word Tokenization / Byte-Pair Encoding:** If non-English patient communications are introduced in future phases, a multilingual sub-word tokenizer can replace whitespace-based n-grams.

---

## 23. Reproducibility Guide

To reproduce the exact Section 9 experimental results from scratch:

```bash
# 1. Activate project environment
cd C:\Users\hp\.gemini\antigravity\scratch\patient-message-triage

# 2. Run master experiment pipeline
python -u -m src.ml.run_experiments

# 3. Run automated ML test suite
python -m pytest -v
```

---

## 24. Transition Plan to Section 10 (FastAPI Backend)

The completion of Section 9 provides clean, validated artifacts ready for integration into the FastAPI application layer in Section 10:

1. `ArtifactManager.load_artifacts()` will be mounted as a startup lifecycle event (`@app.on_event("startup")` or `lifespan`) in FastAPI.
2. The FastAPI `/api/v1/triage` endpoint will ingest raw message JSON, pass it through `TextPreprocessor.transform()`, vectorize it via `TfidfFeatureExtractor.transform()`, query the dual models, compute $C_{\text{overall}}$, apply $\tau = 0.70$, and attach feature attribution keywords.
3. If $C_{\text{overall}} < 0.70$, the endpoint automatically sets `requires_human_review = True` and designates `routing_destination = "Human Review Queue"`.

---

## 25. Appendix: Complete Evaluation Tables & Schemas

### 25.1 Test Results Summary (`reports/test_results.json`)
```json
{
  "category": {
    "accuracy": 1.0,
    "macro_f1": 1.0,
    "weighted_f1": 1.0
  },
  "urgency": {
    "accuracy": 1.0,
    "urgent_recall": 1.0,
    "urgent_precision": 1.0,
    "brier_score": 0.0341
  },
  "confidence": {
    "selected_tau": 0.7,
    "val_human_review_rate": 0.2,
    "test_human_review_rate": 0.2296,
    "test_routing_coverage": 0.7704,
    "test_missed_urgent_auto_routed": 0
  }
}
```

### 25.2 Automated Test Summary
```
tests/test_artifacts.py          2 passed (save/load, explainability)
tests/test_confidence.py         4 passed (individual, bottleneck, grid, tau)
tests/test_data_generation.py    2 passed (schema, reproducibility)
tests/test_deduplication.py      3 passed (exact, normalized, jaccard)
tests/test_ml_pipeline.py        6 passed (preprocessor, tfidf, models, evaluator)
tests/test_pii_checker.py        4 passed (clean, email, ssn, mrn)
tests/test_splitter.py           2 passed (ratios, stratification)
tests/test_validation.py         3 passed (clean, nulls, invalid categories)
--------------------------------------------------------------------------------
Total: 26 passed in 21.48s (100% pass rate)
```
