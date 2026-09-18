"""Inference service encapsulating the Section 9 ML pipeline for operational triage.
Connects text preprocessing, TF-IDF feature extraction, dual Logistic Regression models,
conservative confidence evaluation, deterministic routing, and feature explainability.
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4
import numpy as np

from src.ml.artifacts import ArtifactManager
from src.ml.explainability import FeatureExplainer
from src.ml.preprocessing import TextPreprocessor
from src.api.schemas import (
    BatchPredictResponse,
    BatchRecordItem,
    CategoryEnum,
    ExplanationModel,
    FeatureContribution,
    ModelInfoResponse,
    PredictResponse,
    StatusEnum,
    UrgencyEnum,
)
from src.api.services.routing_service import RoutingService


class InferenceService:
    """Production-style inference engine for PS-1 operational patient message triage.
    Loaded once during application startup/lifespan and stored in application state.
    """

    def __init__(
        self,
        vectorizer: Any,
        category_model: Any,
        urgency_model: Any,
        metadata: Dict[str, Any],
        threshold: float = 0.70,
        max_message_length: int = 4000,
    ):
        self.vectorizer = vectorizer
        self.category_model = category_model
        self.urgency_model = urgency_model
        self.metadata = metadata
        self.threshold = threshold
        self.max_message_length = max_message_length

        self.preprocessor = TextPreprocessor()
        self.routing_service = RoutingService()

        # Category explainer
        self.category_explainer = FeatureExplainer(
            vectorizer=self.vectorizer,
            model=self.category_model,
            class_labels=list(self.category_model.classes_),
        )

        # Urgency explainer
        self.urgency_explainer = FeatureExplainer(
            vectorizer=self.vectorizer,
            model=self.urgency_model,
            class_labels=list(self.urgency_model.classes_),
        )

    @classmethod
    def from_artifacts(
        cls,
        base_dir: str = "models",
        version: str = "v1.0.0",
        threshold: float = 0.70,
        max_message_length: int = 4000,
    ) -> "InferenceService":
        """Factory method loading serialized Section 9 artifacts via ArtifactManager."""
        artifacts = ArtifactManager.load_artifacts(base_dir=base_dir, version=version)
        return cls(
            vectorizer=artifacts["vectorizer"],
            category_model=artifacts["category_model"],
            urgency_model=artifacts["urgency_model"],
            metadata=artifacts["metadata"],
            threshold=threshold,
            max_message_length=max_message_length,
        )

    def predict_single(
        self,
        message_text: str,
        message_id: Optional[str] = None,
    ) -> PredictResponse:
        """Executes full operational triage inference on a single patient message."""
        if not message_id:
            message_id = f"MSG-{uuid4().hex[:8].upper()}"

        # 1. NLP Text Preprocessing
        clean_text = self.preprocessor.clean(message_text)

        # 2. TF-IDF Feature Extraction
        text_vec = self.vectorizer.transform([clean_text])

        # 3. Category Model Prediction & Probabilities
        cat_probs = self.category_model.predict_proba(text_vec)[0]
        cat_idx = int(np.argmax(cat_probs))
        pred_cat_str = str(self.category_model.classes_[cat_idx])
        cat_conf = round(float(cat_probs[cat_idx]), 4)

        # 4. Urgency Model Prediction & Probabilities
        urg_probs = self.urgency_model.predict_proba(text_vec)[0]
        urg_idx = int(np.argmax(urg_probs))
        pred_urg_str = str(self.urgency_model.classes_[urg_idx])
        urg_conf = round(float(urg_probs[urg_idx]), 4)

        # 5. Joint Confidence System: C_overall = min(C_cat, C_urg)
        overall_conf = round(float(min(cat_conf, urg_conf)), 4)

        # 6. Operational Gating Check against Threshold Tau
        requires_human_review = bool(overall_conf < self.threshold)
        status = StatusEnum.LOW_CONFIDENCE if requires_human_review else StatusEnum.SUCCESS

        # 7. Deterministic Routing Assignment
        assigned_queue = self.routing_service.route(
            predicted_category=pred_cat_str,
            predicted_urgency=pred_urg_str,
            requires_human_review=requires_human_review,
        )

        # 8. Feature Explainability (Top Positive Linear Attributions)
        cat_exp_raw = self.category_explainer.explain_instance(
            text_vector=text_vec,
            predicted_class=pred_cat_str,
            top_k=5,
        )
        urg_exp_raw = self.urgency_explainer.explain_instance(
            text_vector=text_vec,
            predicted_class=pred_urg_str,
            top_k=5,
        )

        explanation = ExplanationModel(
            category_features=[
                FeatureContribution(feature=feat, contribution=score)
                for feat, score in cat_exp_raw
            ],
            urgency_features=[
                FeatureContribution(feature=feat, contribution=score)
                for feat, score in urg_exp_raw
            ],
        )

        return PredictResponse(
            message_id=message_id,
            predicted_category=CategoryEnum(pred_cat_str),
            predicted_urgency=UrgencyEnum(pred_urg_str),
            category_confidence=cat_conf,
            urgency_confidence=urg_conf,
            overall_confidence=overall_conf,
            assigned_queue=assigned_queue,
            requires_human_review=requires_human_review,
            status=status,
            explanation=explanation,
        )

    def predict_batch(self, records: List[Dict[str, Any]]) -> BatchPredictResponse:
        """Executes row-level robust batch triage on an iterable of message records."""
        results: List[BatchRecordItem] = []
        successful_count = 0
        low_confidence_count = 0
        invalid_count = 0

        for row in records:
            row_idx = row.get("row_index", len(results) + 1)
            raw_text = row.get("message_text")
            msg_id = row.get("message_id") or f"MSG-BATCH-{row_idx:04d}"

            # Row-level validation
            if not raw_text or not str(raw_text).strip():
                invalid_count += 1
                results.append(
                    BatchRecordItem(
                        row_index=row_idx,
                        message_id=msg_id,
                        status=StatusEnum.INVALID_INPUT,
                        error_detail="Empty or missing message_text",
                    )
                )
                continue

            text_str = str(raw_text).strip()
            if len(text_str) > self.max_message_length:
                invalid_count += 1
                results.append(
                    BatchRecordItem(
                        row_index=row_idx,
                        message_id=msg_id,
                        status=StatusEnum.INVALID_INPUT,
                        error_detail=f"Message length ({len(text_str)}) exceeds maximum allowed ({self.max_message_length})",
                    )
                )
                continue

            # Run inference
            try:
                pred = self.predict_single(message_text=text_str, message_id=msg_id)
                if pred.status == StatusEnum.SUCCESS:
                    successful_count += 1
                else:
                    low_confidence_count += 1

                results.append(
                    BatchRecordItem(
                        row_index=row_idx,
                        message_id=pred.message_id,
                        status=pred.status,
                        predicted_category=pred.predicted_category,
                        predicted_urgency=pred.predicted_urgency,
                        category_confidence=pred.category_confidence,
                        urgency_confidence=pred.urgency_confidence,
                        overall_confidence=pred.overall_confidence,
                        assigned_queue=pred.assigned_queue,
                        requires_human_review=pred.requires_human_review,
                        explanation=pred.explanation,
                    )
                )
            except Exception as exc:
                invalid_count += 1
                results.append(
                    BatchRecordItem(
                        row_index=row_idx,
                        message_id=msg_id,
                        status=StatusEnum.PROCESSING_FAILURE,
                        error_detail=f"Inference processing failure: {str(exc)}",
                    )
                )

        return BatchPredictResponse(
            total_records=len(records),
            successful_records=successful_count,
            low_confidence_records=low_confidence_count,
            invalid_records=invalid_count,
            results=results,
        )

    def get_model_info(self) -> ModelInfoResponse:
        """Extracts non-sensitive model metadata for public inspection."""
        return ModelInfoResponse(
            model_version=str(self.metadata.get("model_version", "v1.0.0")),
            dataset_version=str(self.metadata.get("dataset_version", "v1.0.0")),
            category_labels=list(self.category_model.classes_),
            urgency_labels=list(self.urgency_model.classes_),
            threshold=float(self.threshold),
            model_type="Dual Multinomial Logistic Regression (TF-IDF)",
            feature_count=int(self.metadata.get("feature_count", 2500)),
            training_timestamp=self.metadata.get("training_timestamp"),
        )
