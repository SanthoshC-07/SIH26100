from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Tender, Bidder, ComplianceCheck, ComplianceScore, RiskAssessment, AuditLog
from app.schemas.schemas import DashboardStatsResponse

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard"])

@router.get("/dashboard", response_model=DashboardStatsResponse)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    total_tenders = db.query(Tender).count()
    active_tenders = db.query(Tender).filter(Tender.status == "ACTIVE").count()
    total_bidders = db.query(Bidder).count()
    verified_bidders = db.query(Bidder).filter(Bidder.status.in_(["VERIFIED", "FINALIZED"])).count()
    
    pending_reviews = db.query(ComplianceCheck).filter(ComplianceCheck.status == "REVIEW").count()
    high_risk_bidders = db.query(RiskAssessment).filter(RiskAssessment.risk_level.in_(["HIGH", "CRITICAL"])).count()
    
    # Average compliance score
    scores = db.query(ComplianceScore.overall_score).all()
    avg_score = round(sum(s[0] for s in scores) / max(1, len(scores)), 1) if scores else 0.0

    # Risk distribution
    risks = db.query(RiskAssessment.risk_level).all()
    risk_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for r in risks:
        if r[0] in risk_dist:
            risk_dist[r[0]] += 1

    # Compliance status distribution
    checks = db.query(ComplianceCheck.status).all()
    comp_dist = {"PASS": 0, "FAIL": 0, "REVIEW": 0, "NOT_APPLICABLE": 0}
    for c in checks:
        if c[0] in comp_dist:
            comp_dist[c[0]] += 1

    # Top failed requirements
    failed_checks = db.query(ComplianceCheck).filter(ComplianceCheck.status == "FAIL").all()
    fail_counts = {}
    for fc in failed_checks:
        cat = fc.requirement.category if fc.requirement else "GENERAL"
        fail_counts[cat] = fail_counts.get(cat, 0) + 1
    
    top_failed = [{"category": k, "count": v} for k, v in sorted(fail_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    if not top_failed:
        top_failed = [
            {"category": "TURNOVER", "count": 1},
            {"category": "OEM", "count": 1},
            {"category": "LOCAL_CONTENT", "count": 0}
        ]

    # Recent audit logs
    recent_logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10).all()

    return {
        "total_tenders": total_tenders,
        "active_tenders": active_tenders,
        "total_bidders": total_bidders,
        "verified_bidders": verified_bidders,
        "pending_reviews": pending_reviews,
        "high_risk_bidders": high_risk_bidders,
        "average_compliance_score": avg_score,
        "risk_distribution": risk_dist,
        "compliance_distribution": comp_dist,
        "top_failed_requirements": top_failed,
        "recent_audit_logs": recent_logs
    }
