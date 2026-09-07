"""
SIH26100 — Requirement Dataset & Review API Router
--------------------------------------------------
API endpoints for inspecting the generated tender PDF requirement dataset,
viewing the human-in-the-loop review queue, triggering pipeline runs, and
updating clause review decisions (APPROVED, REJECTED, NEEDS_REVIEW).

Authoritative Path:
    backend/app/api/requirement_dataset_router.py
"""
import os
import csv
import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.config import settings
from app.api.deps import get_current_user, get_current_admin, require_any_role, require_role
from app.models.models import User
from ml.scripts.tender_pdf_pipeline import (
    TenderPDFRequirementPipeline,
    REQUIREMENT_DATASET_CSV,
    REQUIREMENT_REVIEW_CSV,
    DATASET_COLUMNS,
    REVIEW_COLUMNS
)

router = APIRouter(prefix="/requirements-pipeline", tags=["Requirement Pipeline"])


class ReviewUpdateRequest(BaseModel):
    review_status: str  # APPROVED, REJECTED, NEEDS_REVIEW
    notes: Optional[str] = None


class PipelineRunRequest(BaseModel):
    input_dir: Optional[str] = None


def _load_csv_records(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        return []
    records = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    return records


def _save_csv_records(file_path: str, records: List[Dict[str, Any]], fieldnames: List[str]):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


@router.get("/dataset")
def get_requirement_dataset(
    category: Optional[str] = None,
    domain_relevance: Optional[str] = None,
    review_status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    """
    Returns paginated extracted requirements dataset with optional filters.
    Accessible to authorized Officers and Admins.
    """
    records = _load_csv_records(REQUIREMENT_DATASET_CSV)

    if category:
        records = [r for r in records if r.get("category", "").upper() == category.upper()]
    if domain_relevance:
        records = [r for r in records if r.get("domain_relevance", "").upper() == domain_relevance.upper()]
    if review_status:
        records = [r for r in records if r.get("review_status", "").upper() == review_status.upper()]
    if search:
        s_lower = search.lower()
        records = [
            r for r in records
            if s_lower in r.get("original_text", "").lower()
            or s_lower in r.get("source_document", "").lower()
            or s_lower in r.get("requirement_id", "").lower()
        ]

    total = len(records)
    paginated = records[skip: skip + limit]

    # Parse JSON entities for response
    for r in paginated:
        try:
            r["entities"] = json.loads(r.get("entities") or "[]")
        except Exception:
            r["entities"] = []

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": paginated
    }


@router.get("/reviews")
def get_review_queue(
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    """
    Returns items needing human verification from the review queue.
    """
    records = _load_csv_records(REQUIREMENT_REVIEW_CSV)
    if search:
        s_lower = search.lower()
        records = [
            r for r in records
            if s_lower in r.get("original_text", "").lower()
            or s_lower in r.get("review_reason", "").lower()
            or s_lower in r.get("source_document", "").lower()
        ]

    total = len(records)
    paginated = records[skip: skip + limit]
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": paginated
    }


@router.post("/review/{requirement_id}")
def update_requirement_review(
    requirement_id: str,
    review_data: ReviewUpdateRequest,
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER"))
):
    """
    Updates the review status of a requirement clause (APPROVED, REJECTED, NEEDS_REVIEW).
    Procurement Officer only.
    """
    valid_statuses = ["APPROVED", "REJECTED", "NEEDS_REVIEW", "PENDING"]
    status_upper = review_data.review_status.upper()
    if status_upper not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid review status '{review_data.review_status}'. Allowed: {valid_statuses}"
        )

    dataset_records = _load_csv_records(REQUIREMENT_DATASET_CSV)
    found = False
    for r in dataset_records:
        if r.get("requirement_id") == requirement_id:
            r["review_status"] = status_upper
            found = True
            break

    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement ID '{requirement_id}' not found in requirement dataset."
        )

    _save_csv_records(REQUIREMENT_DATASET_CSV, dataset_records, DATASET_COLUMNS)

    return {
        "success": True,
        "requirement_id": requirement_id,
        "new_status": status_upper,
        "updated_by": current_user.email
    }


@router.post("/run")
def trigger_pipeline_run(
    payload: PipelineRunRequest = PipelineRunRequest(),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Triggers the Tender PDF Requirement Extraction Pipeline on the uploaded PDFs.
    Admin only.
    """
    input_dir = payload.input_dir or os.path.join(settings.BASE_DIR, "uploads")
    if not os.path.exists(input_dir):
        input_dir = os.path.join(os.path.dirname(settings.BASE_DIR), "backend", "uploads")

    pipeline = TenderPDFRequirementPipeline()
    result = pipeline.process_directory(input_dir)

    return {
        "success": True,
        "stats": result["stats"],
        "dataset_count": len(result["dataset_rows"]),
        "review_count": len(result["review_rows"])
    }


@router.get("/stats")
def get_pipeline_stats(
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    """
    Returns summarized dataset counts, category distribution, and domain relevance counts.
    """
    records = _load_csv_records(REQUIREMENT_DATASET_CSV)
    review_records = _load_csv_records(REQUIREMENT_REVIEW_CSV)

    category_counts: Dict[str, int] = {}
    domain_counts: Dict[str, int] = {}
    status_counts: Dict[str, int] = {}

    for r in records:
        cat = r.get("category", "UNKNOWN")
        dom = r.get("domain_relevance", "UNKNOWN")
        st = r.get("review_status", "PENDING")

        category_counts[cat] = category_counts.get(cat, 0) + 1
        domain_counts[dom] = domain_counts.get(dom, 0) + 1
        status_counts[st] = status_counts.get(st, 0) + 1

    return {
        "total_requirements": len(records),
        "total_needing_review": len(review_records),
        "category_distribution": category_counts,
        "domain_relevance_distribution": domain_counts,
        "review_status_distribution": status_counts
    }
