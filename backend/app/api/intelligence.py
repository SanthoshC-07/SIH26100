import os
import sys
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Ensure workspace root is in sys.path for ml module resolution
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR = os.path.dirname(_THIS_DIR)
_BACKEND_DIR = os.path.dirname(_APP_DIR)
_WORKSPACE_ROOT = os.path.dirname(_BACKEND_DIR)
for _p in [_WORKSPACE_ROOT, _BACKEND_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app.core.database import get_db
from app.api.deps import get_current_user, require_any_role
from app.models.models import User, Requirement

try:
    from app.ml.requirement_extractor import unified_requirement_extractor
except ImportError:
    from ml.services.requirement_extractor import unified_requirement_extractor

router = APIRouter(prefix="/intelligence", tags=["Document Intelligence"])


class ExtractRequirementPayload(BaseModel):
    requirement_text: str
    category: Optional[str] = None


class ExtractRequirementResponse(BaseModel):
    requirement_text: str
    category: str
    threshold: Optional[float] = None
    unit: Optional[str] = None
    value: Optional[float] = None
    minimum_value: Optional[float] = None
    maximum_value: Optional[float] = None
    time_period_years: Optional[int] = None
    project_type: Optional[str] = None
    sector: Optional[str] = None
    diameter_inch: Optional[float] = None
    length_km: Optional[float] = None
    experience_years: Optional[int] = None
    required_count: Optional[int] = None
    role: Optional[str] = None
    qualification: Optional[str] = None
    scope: Optional[str] = None
    entities: List[str] = []
    extraction_method: str = "LLM_EXTRACTION"
    confidence: float = 0.0
    status: str = "VERIFICATION_READY"
    ml_predicted_class: Optional[str] = None
    ml_confidence: Optional[float] = None
    ml_scores: Optional[Dict[str, float]] = None


@router.post("/extract-requirement", response_model=ExtractRequirementResponse)
def extract_requirement_clause(
    payload: ExtractRequirementPayload,
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    """
    Extracts structured domain parameters from arbitrary tender clause text
    using LLM extraction with deterministic Regex fallback.
    """
    if not payload.requirement_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requirement clause text is required."
        )

    result = unified_requirement_extractor.extract(payload.requirement_text)
    if payload.category and not result.get("category"):
        result["category"] = payload.category

    return ExtractRequirementResponse(**result)


@router.post("/extract-requirement/{requirement_id}", response_model=ExtractRequirementResponse)
def extract_stored_requirement(
    requirement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    """
    Extracts structured parameters for a persistent database Requirement record.
    """
    req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID '{requirement_id}' not found."
        )

    text_to_extract = req.description or req.normalized_requirement or req.category
    result = unified_requirement_extractor.extract(text_to_extract)
    if req.category:
        result["category"] = req.category

    return ExtractRequirementResponse(**result)


class NvidiaVisionPayload(BaseModel):
    image_url_or_base64: str
    prompt: Optional[str] = "Analyze this procurement document, identify document type, issuing authority, dates, signatures, and compliance validity."
    mime_type: Optional[str] = "image/jpeg"


class NvidiaChatPayload(BaseModel):
    prompt: str
    system_prompt: Optional[str] = "You are an expert AI assistant for petroleum and natural gas procurement compliance."
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.2


@router.get("/nvidia-model-info")
def get_nvidia_model_info():
    """
    Returns the status and metadata for the configured NVIDIA NIM LLM & Vision model.
    """
    from app.services.nvidia_llm_service import nvidia_llm_service
    return nvidia_llm_service.get_info()


@router.post("/nvidia-vision-analyze")
def analyze_document_with_vision(
    payload: NvidiaVisionPayload,
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN", "BIDDER"))
):
    """
    Analyzes an uploaded document image or certificate using NVIDIA LLaMA 3.2 90B Vision Instruct.
    """
    from app.services.nvidia_llm_service import nvidia_llm_service
    res = nvidia_llm_service.analyze_document_vision(
        image_data=payload.image_url_or_base64,
        prompt=payload.prompt,
        mime_type=payload.mime_type
    )
    if not res.get("success"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=res.get("error", "Failed to analyze document with NVIDIA Vision model.")
        )
    return {
        "model": res.get("model"),
        "analysis": res.get("content"),
        "raw": res.get("raw")
    }


@router.post("/nvidia-chat")
def chat_with_nvidia_llm(
    payload: NvidiaChatPayload,
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN", "BIDDER"))
):
    """
    Direct text reasoning query using NVIDIA LLaMA 3.2 90B Vision Instruct.
    """
    from app.services.nvidia_llm_service import nvidia_llm_service
    messages = []
    if payload.system_prompt:
        messages.append({"role": "system", "content": payload.system_prompt})
    messages.append({"role": "user", "content": payload.prompt})

    res = nvidia_llm_service.chat_completion(
        messages=messages,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens
    )
    if not res.get("success"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=res.get("error", "NVIDIA NIM LLM invocation failed.")
        )
    return {
        "model": res.get("model"),
        "reply": res.get("content")
    }

