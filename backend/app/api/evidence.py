"""
Evidence & Semantic Retrieval Endpoints
Ministry of Petroleum & Natural Gas - Petroleum & Natural Gas Pipeline Procurement
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, require_any_role, verify_bidder_ownership
from app.models.models import Evidence, ComplianceCheck, EvidenceChunk, Document, DocumentPage, ExtractedEntity, Bidder, Tender, User
from app.schemas.schemas import (
    EvidenceResponse,
    EvidenceChunkResponse,
    EvidenceSearchRequest,
    EvidenceSearchResult,
    DocumentResponse,
    DocumentDetailResponse,
    ExtractedEntityResponse
)
from app.ml.vector_store import vector_store
from app.documents.entity_extractor import EntityExtractor

router = APIRouter(tags=["Evidence"])

@router.get("/documents")
def list_all_documents(
    bidder_id: Optional[str] = None,
    tender_id: Optional[str] = None,
    document_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists documents with extraction details and extracted entity counts.
    """
    query = db.query(Document)
    if bidder_id:
        query = query.filter(Document.bidder_id == bidder_id)
    if tender_id:
        query = query.filter(Document.tender_id == tender_id)
    if document_type:
        query = query.filter(Document.document_type == document_type)

    docs = query.order_by(Document.upload_timestamp.desc()).all()
    results = []
    for d in docs:
        bidder = db.query(Bidder).filter(Bidder.id == d.bidder_id).first() if d.bidder_id else None
        tender = db.query(Tender).filter(Tender.id == d.tender_id).first() if d.tender_id else None
        entities = db.query(ExtractedEntity).filter(ExtractedEntity.document_id == d.id).all()
        results.append({
            "id": d.id,
            "bidder_id": d.bidder_id,
            "bidder_name": bidder.legal_name if bidder else None,
            "tender_id": d.tender_id,
            "tender_title": tender.title if tender else None,
            "document_name": d.document_name,
            "original_filename": d.original_filename,
            "document_type": d.document_type,
            "file_size": d.file_size or 0,
            "mime_type": d.mime_type or "application/pdf",
            "is_scanned": d.is_scanned or False,
            "page_count": d.page_count or 1,
            "extraction_method": d.extraction_method or ("TESSERACT_OCR" if d.is_scanned else "PYMUPDF"),
            "upload_timestamp": d.upload_timestamp,
            "entities_count": len(entities),
            "entities": [
                {
                    "id": e.id,
                    "document_id": e.document_id,
                    "entity_type": e.entity_type,
                    "entity_value": e.entity_value,
                    "normalized_value": e.normalized_value,
                    "confidence": e.confidence,
                    "page_number": e.page_number,
                    "context_snippet": e.context_snippet,
                    "created_at": e.created_at
                }
                for e in entities
            ],
            "extracted_text_snippet": (d.extracted_text[:250] + "...") if d.extracted_text else ""
        })
    return results

@router.get("/documents/{document_id}/entities", response_model=List[ExtractedEntityResponse])
def get_document_entities(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.bidder_id:
        verify_bidder_ownership(doc.bidder_id, current_user, db)
    return db.query(ExtractedEntity).filter(ExtractedEntity.document_id == document_id).all()

@router.get("/extracted-entities")
def list_extracted_entities(
    bidder_id: Optional[str] = None,
    document_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Queries extracted domain entities (GSTIN, PAN, Turnover, Pipeline Length, Manpower, HSE) across documents.
    """
    query = db.query(ExtractedEntity).join(Document, ExtractedEntity.document_id == Document.id)
    if bidder_id:
        query = query.filter(Document.bidder_id == bidder_id)
    if document_id:
        query = query.filter(ExtractedEntity.document_id == document_id)
    if entity_type:
        query = query.filter(ExtractedEntity.entity_type == entity_type)

    entities = query.order_by(ExtractedEntity.confidence.desc()).all()
    results = []
    for e in entities:
        doc = e.document
        bidder = db.query(Bidder).filter(Bidder.id == doc.bidder_id).first() if doc and doc.bidder_id else None
        results.append({
            "id": e.id,
            "document_id": e.document_id,
            "document_name": doc.document_name if doc else "Document",
            "bidder_id": doc.bidder_id if doc else None,
            "bidder_name": bidder.legal_name if bidder else None,
            "entity_type": e.entity_type,
            "entity_value": e.entity_value,
            "normalized_value": e.normalized_value,
            "confidence": e.confidence,
            "page_number": e.page_number,
            "context_snippet": e.context_snippet,
            "created_at": e.created_at
        })
    return results

@router.get("/evidence", response_model=List[EvidenceResponse])
def list_evidence(
    compliance_check_id: Optional[str] = None,
    document_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    query = db.query(Evidence)
    if compliance_check_id:
        query = query.filter(Evidence.compliance_check_id == compliance_check_id)
    if document_id:
        query = query.filter(Evidence.document_id == document_id)
    return query.order_by(Evidence.created_at.desc()).all()

@router.get("/evidence/{id}", response_model=EvidenceResponse)
def get_evidence_item(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    ev = db.query(Evidence).filter(Evidence.id == id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence item not found")
    return ev

# Phase 2: Requirements Evidence Search Endpoint
@router.post("/requirements/{requirement_id}/evidence/search", response_model=List[EvidenceSearchResult])
def search_evidence_by_requirement(
    requirement_id: str,
    payload: Optional[EvidenceSearchRequest] = None,
    bidder_id: Optional[str] = Query(None),
    top_k: int = Query(5),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    query_text = payload.query if payload else ""
    target_bidder = payload.bidder_id if (payload and payload.bidder_id) else bidder_id
    k = payload.top_k if payload else top_k

    results = vector_store.search_evidence_for_requirement(
        db=db,
        requirement_id=requirement_id,
        bidder_id=target_bidder,
        query=query_text,
        top_k=k
    )
    return results

@router.post("/evidence/search", response_model=List[EvidenceSearchResult])
def search_evidence_general(
    payload: EvidenceSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    results = vector_store.search_evidence_for_requirement(
        db=db,
        requirement_id=payload.requirement_id,
        bidder_id=payload.bidder_id,
        query=payload.query,
        top_k=payload.top_k,
        category=payload.category
    )
    return results

@router.get("/documents/{document_id}/chunks", response_model=List[EvidenceChunkResponse])
def get_document_chunks(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.bidder_id:
        verify_bidder_ownership(doc.bidder_id, current_user, db)
    chunks = db.query(EvidenceChunk).filter(EvidenceChunk.document_id == document_id).order_by(EvidenceChunk.chunk_index.asc()).all()
    return chunks

@router.get("/documents/{document_id}/pages")
def get_document_pages(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.bidder_id:
        verify_bidder_ownership(doc.bidder_id, current_user, db)
    pages = db.query(DocumentPage).filter(DocumentPage.document_id == document_id).order_by(DocumentPage.page_number.asc()).all()
    return [
        {
            "id": p.id,
            "document_id": p.document_id,
            "page_number": p.page_number,
            "text": p.page_text,
            "raw_text": p.raw_text or p.page_text,
            "normalized_text": p.normalized_text,
            "extraction_method": p.extraction_method,
            "ocr_applied": p.ocr_applied,
            "processing_status": p.processing_status or "SUCCESS",
            "confidence": p.confidence
        }
        for p in pages
    ]


# ==============================================================================
# Phase 3: FAISS Evidence Indexing & Neural Retrieval Endpoints
# ==============================================================================

@router.post("/evidence/index/{bid_id}")
def index_bidder_evidence(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    """
    Indexes all document pages and evidence chunks for a bidder in the FAISS vector index.
    Preserves document name, page number, and extraction method provenance.
    """
    from ml.services.faiss_service import faiss_evidence_index
    from app.models.models import Bidder, Bid

    # Resolve bidder id
    bidder = db.query(Bidder).filter(Bidder.id == bid_id).first()
    if not bidder:
        bid = db.query(Bid).filter(Bid.id == bid_id).first()
        if bid:
            bidder = db.query(Bidder).filter(Bidder.id == bid.bidder_id).first()

    effective_bidder_id = bidder.id if bidder else bid_id

    # Fetch all documents for this bidder
    docs = db.query(Document).filter(Document.bidder_id == effective_bidder_id).all()
    indexed_chunks = []

    for doc in docs:
        pages = db.query(DocumentPage).filter(DocumentPage.document_id == doc.id).all()
        if pages:
            for page in pages:
                text = page.page_text or page.raw_text or ""
                if text.strip():
                    indexed_chunks.append({
                        "chunk_id": f"{doc.id}-p{page.page_number}",
                        "document_id": doc.id,
                        "document_name": doc.filename or "Bidder_Evidence.pdf",
                        "page_number": page.page_number,
                        "text": text.strip(),
                        "extraction_method": page.extraction_method or "PDF_TEXT",
                        "bidder_id": effective_bidder_id
                    })
        else:
            # Document level fallback
            if doc.extracted_text and doc.extracted_text.strip():
                indexed_chunks.append({
                    "chunk_id": f"{doc.id}-full",
                    "document_id": doc.id,
                    "document_name": doc.document_name or doc.original_filename or "Bidder_Evidence.pdf",
                    "page_number": 1,
                    "text": doc.extracted_text.strip(),
                    "extraction_method": doc.extraction_method or "PDF_TEXT",
                    "bidder_id": effective_bidder_id
                })

    count = faiss_evidence_index.add_chunks(indexed_chunks)
    return {
        "success": True,
        "bid_id": bid_id,
        "bidder_id": effective_bidder_id,
        "documents_count": len(docs),
        "chunks_indexed": count,
        "total_faiss_index_size": faiss_evidence_index.get_count()
    }


@router.get("/evidence/search/{bid_id}")
def search_bidder_evidence(
    bid_id: str,
    q: str = Query(..., description="Semantic search query string"),
    top_k: int = Query(5, description="Number of results to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    """
    Executes dense vector FAISS search across a bidder's indexed documents.
    Returns matching evidence chunks with document and page attribution.
    """
    from ml.services.embedding_service import embedding_service
    from ml.services.faiss_service import faiss_evidence_index
    from app.models.models import Bidder, Bid

    # Resolve bidder id
    bidder = db.query(Bidder).filter(Bidder.id == bid_id).first()
    if not bidder:
        bid = db.query(Bid).filter(Bid.id == bid_id).first()
        if bid:
            bidder = db.query(Bidder).filter(Bidder.id == bid.bidder_id).first()

    effective_bidder_id = bidder.id if bidder else bid_id

    query_vec = embedding_service.embed_text(q)
    results = faiss_evidence_index.search(
        query_vector=query_vec,
        top_k=top_k,
        bidder_id=effective_bidder_id
    )

    # If in-memory FAISS had no chunks for this bidder, fallback to DB vector store
    if not results:
        results = vector_store.search_evidence_for_requirement(
            db=db,
            bidder_id=effective_bidder_id,
            query=q,
            top_k=top_k
        )

    return {
        "bid_id": bid_id,
        "query": q,
        "results_count": len(results),
        "results": results
    }


@router.post("/evidence/retrieve/{bid_id}/{requirement_id}")
def retrieve_evidence_for_bidder_requirement(
    bid_id: str,
    requirement_id: str,
    top_k: int = Query(5),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    """
    Retrieves and attributes top bidder evidence for a specific tender requirement.
    Preserves strict separation between semantic similarity and compliance decision.
    """
    from ml.services.evidence_retriever import evidence_retriever_service
    from app.models.models import Requirement, Bidder, Bid

    # Resolve bidder
    bidder = db.query(Bidder).filter(Bidder.id == bid_id).first()
    if not bidder:
        bid = db.query(Bid).filter(Bid.id == bid_id).first()
        if bid:
            bidder = db.query(Bidder).filter(Bidder.id == bid.bidder_id).first()

    effective_bidder_id = bidder.id if bidder else bid_id

    req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    req_text = req.description or req.normalized_requirement if req else f"Requirement {requirement_id}"
    req_category = req.category if req else None

    # First ensure bidder documents are indexed
    index_bidder_evidence(effective_bidder_id, db)

    retrieval_res = evidence_retriever_service.retrieve_evidence_for_requirement(
        requirement_text=req_text,
        requirement_id=requirement_id,
        bidder_id=effective_bidder_id,
        category=req_category,
        top_k=top_k
    )

    # Fallback to database vector store if FAISS results empty
    if not retrieval_res["evidence"]:
        db_results = vector_store.search_evidence_for_requirement(
            db=db,
            requirement_id=requirement_id,
            bidder_id=effective_bidder_id,
            query=req_text,
            top_k=top_k,
            category=req_category
        )
        if db_results:
            retrieval_res["evidence"] = db_results
            retrieval_res["top_similarity"] = db_results[0].get("similarity_score", 0.75)
            retrieval_res["evidence_status"] = "VERIFICATION_READY"

    return retrieval_res


