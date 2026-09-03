from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.tenders import router as tenders_router
from app.api.bidders import router as bidders_router
from app.api.bids import router as bids_router
from app.api.evidence import router as evidence_router
from app.api.verifications import router as verifications_router
from app.api.compliance import router as compliance_router
from app.api.audit import router as audit_router
from app.api.analytics import router as analytics_router
from app.api.settings import router as settings_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(tenders_router)
api_router.include_router(bidders_router)
api_router.include_router(bids_router)
api_router.include_router(evidence_router)
api_router.include_router(verifications_router)
api_router.include_router(compliance_router)
api_router.include_router(audit_router)
api_router.include_router(analytics_router)
api_router.include_router(settings_router)

__all__ = ["api_router"]
