# SIH26100: AI-Powered Integrated Bid Compliance Verification Platform
## Domain: Petroleum & Natural Gas — Pipeline Procurement / Construction Tenders

[![Smart India Hackathon 2026](https://img.shields.io/badge/SIH-2026-orange.svg)](https://www.sih.gov.in/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/Database-SQLite%203%20%2F%20SQLAlchemy-003B57.svg)](https://sqlite.org/)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript%20%2B%20Vite-61DAFB.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MoPNG%20%2F%20GeM%20Compliant-blue.svg)]()

---

## 1. Executive Summary & Problem Statement

In major public procurement for **Petroleum & Natural Gas pipeline construction** (e.g. GAIL, IOCL, ONGC cross-country transmission pipelines), evaluating vendor bids against complex statutory, financial, technical experience, and safety criteria requires scrutinizing hundreds of pages of engineering certificates, audited financial reports, and statutory filings.

**SIH26100** provides an **AI-Assisted Decision Support Platform for the Procurement Officer**. It focuses deeply on **7 Core Modular Compliance Checks**, enforcing deterministic arithmetic for financial thresholds, semantic NLP for experience matching, and an immutable GFR Section 4 audit trail.

> [!IMPORTANT]
> **Human-in-the-Loop Governance**:
> The AI system serves as **decision support** and **does not unilaterally disqualify or qualify** bidders. The authorized Procurement Officer retains full final authority to accept, reject, or override any compliance determination with recorded justifications.

---

## 2. The 7 Core Compliance Checks Architecture

Rather than implementing shallow, generic checks, the platform implements **7 deep, modular verification services**:

```
                                  Tender Specification (PDF)
                                             ↓
                                Hybrid PyMuPDF & Tesseract OCR
                                             ↓
                               NLP Tender Clause Matrix Parser
                                             ↓
                            Bidder Document Dossier (PDFs/Images)
                                             ↓
                    Entity Extraction & FAISS/Cosine Semantic Index
                                             ↓
       ┌─────────────────────────────────────┴─────────────────────────────────────┐
       │                       7 CORE VERIFICATION SERVICES                        │
       ├───────────────────────────────────────────────────────────────────────────┤
       │ 1. GST CHECK               → Format, Active Status, Legal Name Match     │
       │ 2. PAN CHECK               → Format, Extracted Entity, Identity Alignment │
       │ 3. TURNOVER CHECK          → Deterministic Python 3-Year Arithmetic Avg   │
       │ 4. OIL & GAS EXPERIENCE    → Semantic Hydrocarbon/Refinery/Gas Match      │
       │ 5. SIMILAR PIPELINE EXP.   → Length (km) & Diameter Gating (e.g. >=100km) │
       │ 6. TECHNICAL MANPOWER      → Lead Engineers Counting (e.g. >=5 with >=8yr)│
       │ 7. CONFIGURABLE CHECK      → Auto-Detected: HSE / OEM MAF / Local Content │
       └─────────────────────────────────────┬─────────────────────────────────────┘
                                             ↓
                                Cross-Document Consistency
                                             ↓
                    Confidence Gating (>=0.90 PASS, 0.70-0.89 REVIEW)
                                             ↓
                   Weighted Compliance Score (0–100) & Risk Level (LOW-CRIT)
                                             ↓
                    Evidence-Backed Recommendation with Page Citations
                                             ↓
                   Procurement Officer Review / Override & Audit Log
```

---

## 3. Technology Stack & Database Architecture

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn
- **Database**: **SQLite 3** (Default zero-config database stack: `DATABASE_URL=sqlite:///./app.db` with `PRAGMA foreign_keys=ON` and Alembic migrations). SQLAlchemy ORM abstraction keeps the persistence layer 100% portable for production scaling to PostgreSQL.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts, Axios
- **Document AI & NLP**: PyMuPDF (Fitz), Tesseract OCR fallback, Sentence Transformers (`all-MiniLM-L6-v2`), FAISS vector retrieval, scikit-learn cosine similarity
- **DevOps**: Docker, Docker Compose (Clean two-tier architecture: Backend + Frontend + Persistent volume mounted at `./data`)

---

## 4. Demonstration Bidders & Petroleum Data

The platform comes with pre-seeded demo data including the primary pipeline tender:
**MOPNG/PIPE/2026/017: 150 km, 24-inch Outer Diameter API 5L Grade X70 Cross-Country Natural Gas Transmission Pipeline (Est. Value: ₹240.00 Cr)**

### Evaluated Bidder Profiles:

| Bidder Entity | Turnover (Req: ₹25 Cr Avg) | Similar Pipeline Exp. (Req: >=100 km, 24") | Technical Manpower (Req: >=5 Engg) | Outcome & Score | Risk Level |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PRAVEEN B S ENGINEERING SERVICES** | **₹27.00 Cr** (Avg) | **135 km** 24" GAIL Pipeline | **5 Engineers** (8-12 yrs exp) | **PASS (100/100)** | **LOW RISK** |
| **Indus Pipeline Infrastructure Ltd** | **₹6.83 Cr** (Shortfall ₹18.17 Cr) | **60 km** (Shortfall 40 km) | **3 Engineers** (Shortfall 2) | **FAIL (60/100)** | **CRITICAL RISK** |
| **PetroCon Energy Projects LLP** | **₹12.50 Cr** (Avg) | **95 km** CGD Network (Surat) | **5 Engineers** (1 with 7.5 yrs) | **REVIEW (60/100)** | **CRITICAL RISK** |
| **Vanguard Hydrocarbon Solutions** | **₹15.17 Cr** (Avg) | Verified in Technical Bid | Verified | **REVIEW (60/100)** | **CRITICAL RISK (Debarment Flag)** |

---

## 5. Getting Started & Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup:
```bash
cd backend
pip install -r requirements.txt

# Run Alembic migrations (Optional on fresh install as FastAPI auto-initializes)
python -m alembic upgrade head

# Seed petroleum pipeline tenders & demo bidders
python seed_data.py

# Start FastAPI dev server
uvicorn app.main:app --reload --port 8000
```
Backend Swagger API Documentation: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```
Frontend Web Dashboard: `http://localhost:5173`

### 3. Officer Credentials:
- **Username**: `procurement_officer`
- **Password**: `password123`
*(Or click "Instant Demo Access" on the login screen)*

---

## 6. Running Automated Tests

Run the full Pytest test suite covering all 65 tests (SQLite persistence, core checkers, NLP extraction, scoring, confidence gating, adapters):

```bash
cd backend
pytest -v
```

---

## 7. Key Capabilities

1. **Zero-Configuration SQLite Persistence**: Out-of-the-box local database with full foreign key constraints and migration support.
2. **Deterministic Financial Verification**: Turnover arithmetic $(Y_1 + Y_2 + Y_3) / 3 \ge \text{Threshold}$ with interactive formula breakdown cards.
3. **Semantic Pipeline Scope Matching**: Sentence Transformers embeddings compare project scopes against petroleum pipeline specifications.
4. **Interactive Evidence Viewer**: Auditable page-level citations citing exact document filename, page number, and OCR text excerpt.
5. **Human-in-the-Loop Officer Override**: Officers can review, accept, or override AI recommendations with mandatory justification logs.
