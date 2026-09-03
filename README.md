# SIH26100: AI-Powered Integrated Bid Compliance Verification Platform
## Domain: Petroleum & Natural Gas — Pipeline Procurement / Construction Tenders

[![Smart India Hackathon 2026](https://img.shields.io/badge/SIH-2026-orange.svg)](https://www.sih.gov.in/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
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

Rather than implementing 20–30 generic, shallow checks, the platform implements **7 deep, modular verification services**:

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

### Pluggable Extension Stubs
The modular architecture provides clean interface stubs (`BaseComplianceCheckExtension`) ready for future enterprise integrations:
- **Udyam / MSME**
- **EPFO Electronic Challan Remittance**
- **ESIC Contribution Verification**
- **Startup India Waiver Engine**
- **NSIC Single Point Registration**
- **DigiLocker Verification**
- **Equipment & Heavy Machinery (HDD Rigs / Sidebooms)**
- **ISO 9001 Quality Certifications**

---

## 3. Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts, Axios
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn
- **Database**: PostgreSQL (Docker Compose) / SQLite (zero-config local runtime)
- **Document AI & NLP**: PyMuPDF (Fitz), Tesseract OCR fallback, scikit-learn TF-IDF / Sentence Vector embeddings, Regex & Rule Heuristics
- **DevOps**: Docker, Docker Compose

---

## 4. Pre-Seeded Demonstration Tenders & Bidders

The system comes pre-seeded with the primary petroleum pipeline tender:
**GAIL/2026/PL-NC/4182: 150 km 24-inch API 5L X70 Cross-Country Natural Gas Pipeline Construction (Est. Value: ₹240.00 Cr)**

### 4 Distinct Evaluated Bidder Profiles:

| Bidder Entity | Turnover (Req: ₹10 Cr) | Similar Pipeline Exp. (Req: >=100 km) | Technical Manpower (Req: >=5 Engg) | Outcome & Score | Risk Level |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Larsen & Toubro Hydrocarbon Engineering** | **₹21.67 Cr** (Avg) | **165 km** 24" GAIL Line | **6 Engineers** (9-14 yrs exp) | **PASS (100/100)** | **LOW RISK** |
| **Indus Pipeline Infrastructure Ltd** | **₹6.83 Cr** (Shortfall ₹3.17 Cr) | **60 km** (Shortfall 40 km) | **3 Engineers** (Shortfall 2) | **FAIL (60/100)** | **HIGH RISK** |
| **PetroCon Energy Projects LLP** | **₹12.50 Cr** (Avg) | **95 km** CGD Network (Surat) | **5 Engineers** (1 with 7.5 yrs) | **REVIEW (85/100)** | **MEDIUM RISK** |
| **Vanguard Hydrocarbon Solutions** | **₹15.17 Cr** (Avg) | Verified in Technical Bid | Verified | **REVIEW (80/100)** | **CRITICAL RISK (Identity / Debarment Flag)** |

---

## 5. Getting Started & Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup:
```bash
cd backend
pip install -r requirements.txt
python seed_data.py
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

Run the full Pytest test suite covering all 7 core rules, adapters, scoring weights, risk classification, and end-to-end evaluation:

```bash
cd backend
pytest -v
```

---

## 7. Key Capabilities & Highlights

1. **Deterministic Financial Verification**: Turnover calculations (e.g. $\text{Avg} = \frac{18.50 + 22.00 + 24.50}{3} = 21.67\text{ Cr}$) use strict Python arithmetic with interactive breakdown cards.
2. **Semantic Experience Matching**: Identifies hydrocarbon, refinery, and gas pipeline projects semantically without relying solely on keywords.
3. **Pipeline Parameter Extraction**: Quantifies pipeline lengths (km), pipe diameters (inches/mm), and material specifications (API 5L X70).
4. **Interactive Ground-Truth Evidence Viewer**: Inspect exact document name, page number, confidence percentage, calculation table, and OCR text excerpt.
5. **Human-in-the-Loop Officer Override**: Officers can accept or override AI recommendations to `PASS`, `FAIL`, or `REVIEW` with mandatory remarks logged in the GFR-compliant audit trail.
