from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.tenders import router as tenders_router
from app.api.bidders import router as bidders_router
from app.api.bids import router as bids_router
from app.api.evidence import router as evidence_router
from app.api.verifications import router as verifications_router
from app.api.compliance import router as compliance_router
from app.api.audit import router as audit_router
from app.api.analytics import router as analytics_router
from app.api.settings import router as settings_router
from app.api.ml_router import router as ml_router
from app.api.intelligence import router as intelligence_router

from app.api.requirement_dataset_router import router as requirement_dataset_router
from app.api.risk import router as risk_router
from app.api.officer_review import router as officer_review_router
from app.api.reports import router as reports_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(tenders_router)
api_router.include_router(bidders_router)
api_router.include_router(bids_router)
api_router.include_router(evidence_router)
api_router.include_router(verifications_router)
api_router.include_router(compliance_router)
api_router.include_router(audit_router)
api_router.include_router(analytics_router)
api_router.include_router(settings_router)
api_router.include_router(ml_router)
api_router.include_router(intelligence_router)
api_router.include_router(requirement_dataset_router)
api_router.include_router(risk_router)
api_router.include_router(officer_review_router)
api_router.include_router(reports_router)

__all__ = ["api_router"]
