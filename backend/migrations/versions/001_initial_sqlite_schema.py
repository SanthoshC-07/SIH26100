"""Initial SQLite schema for SIH26100 GeM Bid Compliance Platform

Revision ID: 001_initial_sqlite_schema
Revises: 
Create Date: 2026-09-05 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_sqlite_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), server_default='PROCUREMENT_OFFICER'),
        sa.Column('department', sa.String(length=255), server_default='Ministry of Petroleum & Natural Gas - Tender Evaluation Cell'),
        sa.Column('is_active', sa.Boolean(), server_default='1'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    # 2. tenders
    op.create_table(
        'tenders',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tender_number', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('issuing_organization', sa.String(length=255), server_default='GAIL (India) Limited'),
        sa.Column('ministry', sa.String(length=255), server_default='Ministry of Petroleum & Natural Gas'),
        sa.Column('sector', sa.String(length=100), server_default='OIL_AND_GAS'),
        sa.Column('tender_type', sa.String(length=100), server_default='PIPELINE_PROCUREMENT'),
        sa.Column('project_type', sa.String(length=100), server_default='PIPELINE_CONSTRUCTION'),
        sa.Column('pipeline_type', sa.String(length=100), server_default='CROSS_COUNTRY_PIPELINE'),
        sa.Column('location', sa.String(length=255), server_default='National Gas Grid, India'),
        sa.Column('category', sa.String(length=100), server_default='Petroleum & Pipeline Infrastructure'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('estimated_value', sa.Float(), server_default='0.0'),
        sa.Column('tender_issue_date', sa.DateTime()),
        sa.Column('submission_deadline', sa.DateTime(), nullable=True),
        sa.Column('evaluation_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='ACTIVE'),
        sa.Column('raw_pdf_path', sa.String(length=500), nullable=True),
        sa.Column('created_by', sa.String(length=36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    op.create_index('ix_tenders_tender_number', 'tenders', ['tender_number'], unique=True)
    op.create_index('ix_tenders_status', 'tenders', ['status'])

    # 3. tender_clauses
    op.create_table(
        'tender_clauses',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tender_id', sa.String(length=36), sa.ForeignKey('tenders.id'), nullable=False),
        sa.Column('clause_number', sa.String(length=50), nullable=True),
        sa.Column('clause_type', sa.String(length=50), server_default='REQUIREMENT'),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('normalized_text', sa.Text(), nullable=True),
        sa.Column('page_number', sa.Integer(), server_default='1'),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('confidence', sa.Float(), server_default='1.0'),
        sa.Column('is_requirement', sa.Boolean(), server_default='1'),
        sa.Column('extracted_entities', sa.JSON()),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_tender_clauses_tender_id', 'tender_clauses', ['tender_id'])
    op.create_index('ix_tender_clauses_category', 'tender_clauses', ['category'])

    # 4. requirements
    op.create_table(
        'requirements',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tender_id', sa.String(length=36), sa.ForeignKey('tenders.id'), nullable=False),
        sa.Column('clause_number', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('original_text', sa.Text(), nullable=True),
        sa.Column('normalized_requirement', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('mandatory', sa.Boolean(), server_default='1'),
        sa.Column('threshold', sa.Float(), nullable=True),
        sa.Column('threshold_unit', sa.String(length=50), nullable=True),
        sa.Column('comparison_operator', sa.String(length=20), server_default='>='),
        sa.Column('required_years', sa.Float(), nullable=True),
        sa.Column('required_project_count', sa.Integer(), server_default='1'),
        sa.Column('required_pipeline_length_km', sa.Float(), nullable=True),
        sa.Column('required_project_value', sa.Float(), nullable=True),
        sa.Column('required_pipeline_type', sa.String(length=100), nullable=True),
        sa.Column('required_sector', sa.String(length=100), server_default='OIL_AND_GAS'),
        sa.Column('required_qualification', sa.String(length=255), nullable=True),
        sa.Column('required_manpower_count', sa.Integer(), server_default='5'),
        sa.Column('required_evidence_type', sa.String(length=100), nullable=True),
        sa.Column('conditions', sa.JSON()),
        sa.Column('extraction_confidence', sa.Float(), server_default='1.0'),
        sa.Column('period', sa.String(length=100), nullable=True),
        sa.Column('evidence_required', sa.JSON()),
        sa.Column('verification_method', sa.String(length=50), server_default='RULE_AND_PORTAL'),
        sa.Column('rule_version', sa.String(length=20), server_default='2.0'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    op.create_index('ix_requirements_tender_id', 'requirements', ['tender_id'])
    op.create_index('ix_requirements_category', 'requirements', ['category'])

    # 5. bidders
    op.create_table(
        'bidders',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tender_id', sa.String(length=36), sa.ForeignKey('tenders.id'), nullable=False),
        sa.Column('legal_name', sa.String(length=255), nullable=False),
        sa.Column('trade_name', sa.String(length=255), nullable=True),
        sa.Column('pan', sa.String(length=20), nullable=True),
        sa.Column('gstin', sa.String(length=50), nullable=True),
        sa.Column('registered_address', sa.Text(), nullable=True),
        sa.Column('contact_information', sa.JSON()),
        sa.Column('bidder_type', sa.String(length=100), server_default='INDIAN_EPC_CONTRACTOR'),
        sa.Column('country', sa.String(length=100), server_default='INDIA'),
        sa.Column('oil_gas_experience_years', sa.Float(), server_default='0.0'),
        sa.Column('pipeline_experience_years', sa.Float(), server_default='0.0'),
        sa.Column('udyam_number', sa.String(length=50), nullable=True),
        sa.Column('cin', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('contact_person', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='SUBMITTED'),
        sa.Column('submitted_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    op.create_index('ix_bidders_tender_id', 'bidders', ['tender_id'])
    op.create_index('ix_bidders_legal_name', 'bidders', ['legal_name'])
    op.create_index('ix_bidders_pan', 'bidders', ['pan'])
    op.create_index('ix_bidders_gstin', 'bidders', ['gstin'])
    op.create_index('ix_bidders_status', 'bidders', ['status'])

    # 6. bids
    op.create_table(
        'bids',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tender_id', sa.String(length=36), sa.ForeignKey('tenders.id'), nullable=False),
        sa.Column('bidder_id', sa.String(length=36), sa.ForeignKey('bidders.id'), nullable=False),
        sa.Column('bid_reference_number', sa.String(length=100), nullable=False),
        sa.Column('submission_date', sa.DateTime()),
        sa.Column('technical_bid_status', sa.String(length=50), server_default='UNDER_EVALUATION'),
        sa.Column('financial_bid_amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=10), server_default='INR'),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    op.create_index('ix_bids_tender_id', 'bids', ['tender_id'])
    op.create_index('ix_bids_bidder_id', 'bids', ['bidder_id'])
    op.create_index('ix_bids_bid_reference_number', 'bids', ['bid_reference_number'], unique=True)

    # 7. bidder_projects
    op.create_table(
        'bidder_projects',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('bidder_id', sa.String(length=36), sa.ForeignKey('bidders.id'), nullable=False),
        sa.Column('project_name', sa.String(length=500), nullable=False),
        sa.Column('client_name', sa.String(length=255), nullable=False),
        sa.Column('client_type', sa.String(length=100), server_default='PUBLIC_SECTOR_UNDERTAKING'),
        sa.Column('sector', sa.String(length=100), server_default='OIL_AND_GAS'),
        sa.Column('project_type', sa.String(length=100), server_default='PIPELINE_CONSTRUCTION'),
        sa.Column('pipeline_type', sa.String(length=100), server_default='NATURAL_GAS'),
        sa.Column('pipeline_length_km', sa.Float(), nullable=True),
        sa.Column('pipeline_diameter', sa.String(length=100), nullable=True),
        sa.Column('project_value', sa.Float(), server_default='0.0'),
        sa.Column('currency', sa.String(length=10), server_default='INR'),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('completion_date', sa.DateTime(), nullable=True),
        sa.Column('scope_of_work', sa.Text(), nullable=True),
        sa.Column('bidder_role', sa.String(length=100), server_default='EPC_CONTRACTOR'),
        sa.Column('contract_reference', sa.String(length=100), nullable=True),
        sa.Column('evidence_document_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    op.create_index('ix_bidder_projects_bidder_id', 'bidder_projects', ['bidder_id'])

    # 8. bidder_personnel
    op.create_table(
        'bidder_personnel',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('bidder_id', sa.String(length=36), sa.ForeignKey('bidders.id'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('designation', sa.String(length=255), nullable=False),
        sa.Column('qualification', sa.String(length=255), nullable=False),
        sa.Column('specialization', sa.String(length=255), nullable=True),
        sa.Column('years_of_experience', sa.Float(), server_default='0.0'),
        sa.Column('oil_gas_experience_years', sa.Float(), server_default='0.0'),
        sa.Column('pipeline_experience_years', sa.Float(), server_default='0.0'),
        sa.Column('certifications', sa.JSON()),
        sa.Column('relevant_projects', sa.JSON()),
        sa.Column('document_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    op.create_index('ix_bidder_personnel_bidder_id', 'bidder_personnel', ['bidder_id'])

    # 9. documents
    op.create_table(
        'documents',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('bidder_id', sa.String(length=36), sa.ForeignKey('bidders.id'), nullable=True),
        sa.Column('tender_id', sa.String(length=36), sa.ForeignKey('tenders.id'), nullable=True),
        sa.Column('document_name', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('document_type', sa.String(length=100), server_default='PIPELINE_PROJECT_DOCUMENT'),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), server_default='0'),
        sa.Column('mime_type', sa.String(length=100), server_default='application/pdf'),
        sa.Column('is_scanned', sa.Boolean(), server_default='0'),
        sa.Column('extraction_method', sa.String(length=50), server_default='PDF_TEXT'),
        sa.Column('page_count', sa.Integer(), server_default='1'),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('uploaded_by', sa.String(length=36), nullable=True),
        sa.Column('upload_timestamp', sa.DateTime()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    op.create_index('ix_documents_bidder_id', 'documents', ['bidder_id'])
    op.create_index('ix_documents_tender_id', 'documents', ['tender_id'])

    # 10. document_pages
    op.create_table(
        'document_pages',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('page_text', sa.Text(), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('normalized_text', sa.Text(), nullable=True),
        sa.Column('has_tables', sa.Boolean(), server_default='0'),
        sa.Column('ocr_applied', sa.Boolean(), server_default='0'),
        sa.Column('extraction_method', sa.String(length=50), server_default='PDF_TEXT'),
        sa.Column('processing_status', sa.String(length=50), server_default='SUCCESS'),
        sa.Column('confidence', sa.Float(), server_default='1.0'),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_document_pages_document_id', 'document_pages', ['document_id'])

    # 11. evidence_chunks
    op.create_table(
        'evidence_chunks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('bidder_id', sa.String(length=36), sa.ForeignKey('bidders.id'), nullable=True),
        sa.Column('requirement_id', sa.String(length=36), sa.ForeignKey('requirements.id'), nullable=True),
        sa.Column('page_number', sa.Integer(), server_default='1'),
        sa.Column('chunk_index', sa.Integer(), server_default='0'),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('normalized_text', sa.Text(), nullable=True),
        sa.Column('embedding_json', sa.JSON(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('confidence', sa.Float(), server_default='1.0'),
        sa.Column('similarity_score', sa.Float(), server_default='0.0'),
        sa.Column('metadata_payload', sa.JSON()),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_evidence_chunks_document_id', 'evidence_chunks', ['document_id'])
    op.create_index('ix_evidence_chunks_bidder_id', 'evidence_chunks', ['bidder_id'])
    op.create_index('ix_evidence_chunks_requirement_id', 'evidence_chunks', ['requirement_id'])
    op.create_index('ix_evidence_chunks_category', 'evidence_chunks', ['category'])

    # 12. extracted_entities
    op.create_table(
        'extracted_entities',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_value', sa.Text(), nullable=False),
        sa.Column('normalized_value', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), server_default='1.0'),
        sa.Column('page_number', sa.Integer(), server_default='1'),
        sa.Column('context_snippet', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_extracted_entities_document_id', 'extracted_entities', ['document_id'])
    op.create_index('ix_extracted_entities_entity_type', 'extracted_entities', ['entity_type'])

    # 13. portal_verifications
    op.create_table(
        'portal_verifications',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('bidder_id', sa.String(length=36), sa.ForeignKey('bidders.id'), nullable=False),
        sa.Column('portal_name', sa.String(length=100), nullable=False),
        sa.Column('identifier_queried', sa.String(length=100), nullable=False),
        sa.Column('verification_status', sa.String(length=50), nullable=False),
        sa.Column('response_payload', sa.JSON()),
        sa.Column('source_label', sa.String(length=100), server_default='DEMO / MOCK GOVERNMENT SOURCE'),
        sa.Column('verified_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_portal_verifications_bidder_id', 'portal_verifications', ['bidder_id'])
    op.create_index('ix_portal_verifications_portal_name', 'portal_verifications', ['portal_name'])

    # 14. compliance_checks
    op.create_table(
        'compliance_checks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('bidder_id', sa.String(length=36), sa.ForeignKey('bidders.id'), nullable=False),
        sa.Column('requirement_id', sa.String(length=36), sa.ForeignKey('requirements.id'), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Float(), server_default='1.0'),
        sa.Column('score_contribution', sa.Float(), server_default='0.0'),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('evidence_text', sa.Text(), nullable=True),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('documents.id'), nullable=True),
        sa.Column('document_name', sa.String(length=255), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('verification_source', sa.String(length=100), server_default='HYBRID'),
        sa.Column('verification_method', sa.String(length=50), server_default='RULE_AND_PORTAL'),
        sa.Column('rule_version', sa.String(length=20), server_default='1.0'),
        sa.Column('verified_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    op.create_index('ix_compliance_checks_bidder_id', 'compliance_checks', ['bidder_id'])
    op.create_index('ix_compliance_checks_requirement_id', 'compliance_checks', ['requirement_id'])
    op.create_index('ix_compliance_checks_status', 'compliance_checks', ['status'])

    # 15. evidences
    op.create_table(
        'evidences',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('compliance_check_id', sa.String(length=36), sa.ForeignKey('compliance_checks.id'), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=True),
        sa.Column('document_name', sa.String(length=255), nullable=True),
        sa.Column('page_number', sa.Integer(), server_default='1'),
        sa.Column('source_text', sa.Text(), nullable=False),
        sa.Column('extraction_method', sa.String(length=50), server_default='PDF_TEXT'),
        sa.Column('extracted_entities', sa.JSON()),
        sa.Column('confidence', sa.Float(), server_default='1.0'),
        sa.Column('calculation_breakdown', sa.JSON(), nullable=True),
        sa.Column('verified_source', sa.String(length=100), server_default='DEMO / MOCK GOVERNMENT SOURCE'),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_evidences_compliance_check_id', 'evidences', ['compliance_check_id'])

    # 16. compliance_scores
    op.create_table(
        'compliance_scores',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('bidder_id', sa.String(length=36), sa.ForeignKey('bidders.id'), unique=True, nullable=False),
        sa.Column('overall_score', sa.Float(), server_default='0.0'),
        sa.Column('statutory_score', sa.Float(), server_default='0.0'),
        sa.Column('financial_score', sa.Float(), server_default='0.0'),
        sa.Column('tender_specific_score', sa.Float(), server_default='0.0'),
        sa.Column('documentation_score', sa.Float(), server_default='0.0'),
        sa.Column('other_score', sa.Float(), server_default='0.0'),
        sa.Column('weights_applied', sa.JSON()),
        sa.Column('calculated_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime())
    )

    # 17. risk_assessments
    op.create_table(
        'risk_assessments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('bidder_id', sa.String(length=36), sa.ForeignKey('bidders.id'), unique=True, nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False),
        sa.Column('primary_risk_factors', sa.JSON()),
        sa.Column('risk_score', sa.Float(), server_default='0.0'),
        sa.Column('assessed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_risk_assessments_risk_level', 'risk_assessments', ['risk_level'])

    # 18. recommendations
    op.create_table(
        'recommendations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('bidder_id', sa.String(length=36), sa.ForeignKey('bidders.id'), unique=True, nullable=False),
        sa.Column('recommendation_type', sa.String(length=50), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('detailed_reasons', sa.JSON()),
        sa.Column('generated_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_recommendations_recommendation_type', 'recommendations', ['recommendation_type'])

    # 19. officer_reviews
    op.create_table(
        'officer_reviews',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('bidder_id', sa.String(length=36), sa.ForeignKey('bidders.id'), nullable=False),
        sa.Column('requirement_id', sa.String(length=36), sa.ForeignKey('requirements.id'), nullable=True),
        sa.Column('officer_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('officer_name', sa.String(length=255), nullable=False),
        sa.Column('previous_status', sa.String(length=50), nullable=False),
        sa.Column('new_status', sa.String(length=50), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_officer_reviews_bidder_id', 'officer_reviews', ['bidder_id'])
    op.create_index('ix_officer_reviews_requirement_id', 'officer_reviews', ['requirement_id'])
    op.create_index('ix_officer_reviews_officer_id', 'officer_reviews', ['officer_id'])

    # 20. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('user_name', sa.String(length=255), server_default='SYSTEM'),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=True),
        sa.Column('bidder_id', sa.String(length=36), nullable=True),
        sa.Column('previous_state', sa.JSON(), nullable=True),
        sa.Column('new_state', sa.JSON(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=100), server_default='MoPNG_PIPELINE_PORTAL'),
        sa.Column('model_version', sa.String(length=50), server_default='SIH26100-v2.0'),
        sa.Column('rule_version', sa.String(length=50), server_default='2.0'),
        sa.Column('ip_address', sa.String(length=50), server_default='127.0.0.1'),
        sa.Column('timestamp', sa.DateTime()),
        sa.Column('created_at', sa.DateTime())
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])
    op.create_index('ix_audit_logs_tender_id', 'audit_logs', ['tender_id'])
    op.create_index('ix_audit_logs_bidder_id', 'audit_logs', ['bidder_id'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('officer_reviews')
    op.drop_table('recommendations')
    op.drop_table('risk_assessments')
    op.drop_table('compliance_scores')
    op.drop_table('evidences')
    op.drop_table('compliance_checks')
    op.drop_table('portal_verifications')
    op.drop_table('extracted_entities')
    op.drop_table('evidence_chunks')
    op.drop_table('document_pages')
    op.drop_table('documents')
    op.drop_table('bidder_personnel')
    op.drop_table('bidder_projects')
    op.drop_table('bids')
    op.drop_table('bidders')
    op.drop_table('requirements')
    op.drop_table('tender_clauses')
    op.drop_table('tenders')
    op.drop_table('users')
