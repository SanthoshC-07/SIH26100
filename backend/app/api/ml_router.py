"""
SIH26100 — ML API Router
POST /ml/classify-requirement
POST /ml/classify-batch
GET  /ml/classifier-info
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.ml.requirement_classifier import requirement_classifier, REQUIREMENT_CLASSES
from app.api.deps import require_any_role
from app.models.models import User

router = APIRouter(prefix="/ml", tags=["ML Classifier"])


class ClassifyRequest(BaseModel):
    text: str


class ClassifyBatchRequest(BaseModel):
    texts: List[str]


class ClassifyResponse(BaseModel):
    text: str
    predicted_class: str
    confidence: float
    all_scores: Dict[str, float] = {}
    classifier_type: str = "scikit-learn domain classifier"
    model_ready: bool = True


@router.post("/classify-requirement", response_model=ClassifyResponse)
def classify_requirement(
    req: ClassifyRequest,
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    """
    Classify a tender/bid requirement clause text into one of 10 locked classes.

    Pipeline:
        Tender Clause → TF-IDF Vectorizer → Logistic Regression → Requirement Class

    Note: This uses a lightweight scikit-learn domain classifier trained on
    petroleum procurement examples. Not a large production-trained model.
    """
    result = requirement_classifier.classify(req.text)
    return ClassifyResponse(**result)


@router.post("/classify-batch")
def classify_batch(
    req: ClassifyBatchRequest,
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    """
    Classify multiple requirement clauses in a single request.
    Returns list of classification results.
    """
    if not req.texts:
        return []
    results = requirement_classifier.classify_batch(req.texts)
    return results


@router.get("/classifier-info")
def get_classifier_info():
    """
    Returns metadata about the requirement classifier.
    Used by the frontend to display the 'scikit-learn domain classifier' info banner.
    """
    return requirement_classifier.get_info()


@router.get("/classes")
def get_requirement_classes():
    """
    Returns the 10 locked requirement classification classes.
    """
    return {
        "classes": REQUIREMENT_CLASSES,
        "count": len(REQUIREMENT_CLASSES),
        "description": "Locked taxonomy for petroleum pipeline procurement bid compliance."
    }
