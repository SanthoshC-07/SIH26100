"""Phase 5 models: risk_factors, officer_decisions, audit_events, compliance_reports

Revision ID: 002_phase5_models
Revises: 001_initial_sqlite_schema
Create Date: 2026-09-07 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_phase5_models'
down_revision: Union[str, None] = '001_initial_sqlite_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. risk_factors
    op.create_table(
        'risk_factors',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('risk_assessment_id', sa.String(length=36), sa.ForeignKey('risk_assessments.id', ondelete='CASCADE'), nullable=True),
        sa.Column('bid_id', sa.String(length=36), sa.ForeignKey('bidders.id'), nullable=False),
        sa.Column('requirement_id', sa.String(length=36), sa.ForeignKey('requirements.id'), nullable=True),
        sa.Column('compliance_check_id', sa.String(length=36), sa.ForeignKey('compliance_checks.id'), nullable=True),
        sa.Column('factor_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evidence_snippet', sa.Text(), nullable=True),
        sa.Column('source_document', sa.String(length=255), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_risk_factors_risk_assessment_id', 'risk_factors', ['risk_assessment_id'])
    op.create_index('ix_risk_factors_bid_id', 'risk_factors', ['bid_id'])
    op.create_index('ix_risk_factors_requirement_id', 'risk_factors', ['requirement_id'])
    op.create_index('ix_risk_factors_compliance_check_id', 'risk_factors', ['compliance_check_id'])
    op.create_index('ix_risk_factors_factor_type', 'risk_factors', ['factor_type'])
    op.create_index('ix_risk_factors_severity', 'risk_factors', ['severity'])

    # 2. officer_decisions
    op.create_table(
        'officer_decisions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('bid_id', sa.String(length=36), sa.ForeignKey('bidders.id'), nullable=False),
        sa.Column('requirement_id', sa.String(length=36), sa.ForeignKey('requirements.id'), nullable=True),
        sa.Column('compliance_check_id', sa.String(length=36), sa.ForeignKey('compliance_checks.id'), nullable=True),
        sa.Column('officer_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('officer_name', sa.String(length=255), nullable=False),
        sa.Column('decision_type', sa.String(length=50), server_default='REQUIREMENT_DECISION'),
        sa.Column('ai_status', sa.String(length=50), nullable=False),
        sa.Column('ai_confidence', sa.Float(), server_default='1.0'),
        sa.Column('officer_status', sa.String(length=50), nullable=False),
        sa.Column('officer_reason', sa.Text(), nullable=False),
        sa.Column('is_override', sa.Boolean(), server_default='0'),
        sa.Column('decision_timestamp', sa.DateTime()),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_officer_decisions_bid_id', 'officer_decisions', ['bid_id'])
    op.create_index('ix_officer_decisions_requirement_id', 'officer_decisions', ['requirement_id'])
    op.create_index('ix_officer_decisions_compliance_check_id', 'officer_decisions', ['compliance_check_id'])
    op.create_index('ix_officer_decisions_officer_id', 'officer_decisions', ['officer_id'])
    op.create_index('ix_officer_decisions_decision_type', 'officer_decisions', ['decision_type'])
    op.create_index('ix_officer_decisions_decision_timestamp', 'officer_decisions', ['decision_timestamp'])

    # 3. audit_events
    op.create_table(
        'audit_events',
        sa.Column('event_id', sa.String(length=36), primary_key=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('user_name', sa.String(length=255), server_default='SYSTEM'),
        sa.Column('role', sa.String(length=50), server_default='SYSTEM'),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=True),
        sa.Column('bidder_id', sa.String(length=36), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('metadata_payload', sa.JSON()),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_audit_events_timestamp', 'audit_events', ['timestamp'])
    op.create_index('ix_audit_events_user_id', 'audit_events', ['user_id'])
    op.create_index('ix_audit_events_role', 'audit_events', ['role'])
    op.create_index('ix_audit_events_action', 'audit_events', ['action'])
    op.create_index('ix_audit_events_entity_type', 'audit_events', ['entity_type'])
    op.create_index('ix_audit_events_entity_id', 'audit_events', ['entity_id'])
    op.create_index('ix_audit_events_tender_id', 'audit_events', ['tender_id'])
    op.create_index('ix_audit_events_bidder_id', 'audit_events', ['bidder_id'])

    # 4. compliance_reports
    op.create_table(
        'compliance_reports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('bid_id', sa.String(length=36), sa.ForeignKey('bidders.id'), nullable=False),
        sa.Column('tender_id', sa.String(length=36), sa.ForeignKey('tenders.id'), nullable=True),
        sa.Column('report_number', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('generated_by_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('generated_by_name', sa.String(length=255), server_default='SYSTEM'),
        sa.Column('assessment_date', sa.DateTime()),
        sa.Column('compliance_score', sa.Float(), server_default='0.0'),
        sa.Column('risk_level', sa.String(length=50), server_default='LOW'),
        sa.Column('risk_score', sa.Float(), server_default='0.0'),
        sa.Column('ai_recommendation', sa.String(length=100), server_default='Recommended for Officer Review'),
        sa.Column('final_officer_decision', sa.String(length=50), nullable=True),
        sa.Column('executive_summary', sa.JSON()),
        sa.Column('requirement_summary', sa.JSON()),
        sa.Column('detailed_findings', sa.JSON()),
        sa.Column('officer_decisions', sa.JSON()),
        sa.Column('risk_analysis', sa.JSON()),
        sa.Column('audit_information', sa.JSON()),
        sa.Column('pdf_path', sa.String(length=500), nullable=True),
        sa.Column('html_content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_compliance_reports_bid_id', 'compliance_reports', ['bid_id'])
    op.create_index('ix_compliance_reports_tender_id', 'compliance_reports', ['tender_id'])
    op.create_index('ix_compliance_reports_report_number', 'compliance_reports', ['report_number'], unique=True)


def downgrade() -> None:
    op.drop_table('compliance_reports')
    op.drop_table('audit_events')
    op.drop_table('officer_decisions')
    op.drop_table('risk_factors')
