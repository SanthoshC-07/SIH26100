"""
Petroleum Domain Vocabulary & Semantic Ontology Dictionary
Ministry of Petroleum & Natural Gas - Petroleum & Natural Gas Pipeline Procurement
"""
from typing import Dict, List, Set, Any

class PetroleumVocabulary:
    """
    Configurable domain lexicon and ontological mapping for Oil & Gas
    and Pipeline Procurement terminology.
    """

    # Primary Petroleum Sectors
    SECTORS: Dict[str, List[str]] = {
        "OIL_AND_GAS": [
            "oil & gas", "oil and gas", "petroleum", "hydrocarbon", "hydrocarbons",
            "refinery", "petrochemical", "upstream", "midstream", "downstream",
            "lng terminal", "lpg terminal", "city gas distribution", "cgd"
        ],
        "NATURAL_GAS": [
            "natural gas", "gas transmission", "gas pipeline", "regasified lng",
            "cng", "piped natural gas", "png", "trunk pipeline"
        ],
        "CRUDE_OIL": [
            "crude oil", "crude transmission", "petroleum product", "hsd", "ms",
            "atf", "cross-country crude pipeline"
        ]
    }

    # Pipeline Infrastructure & Engineering Terms
    PIPELINE_CONSTRUCTION_TERMS: Set[str] = {
        "pipeline", "gas pipeline", "oil pipeline", "transmission pipeline",
        "cross-country pipeline", "cross country pipeline", "pipeline construction",
        "pipeline laying", "epc", "epc contractor", "turnkey", "hydrotesting",
        "hydrostatic testing", "hdd", "horizontal directional drilling",
        "welding", "pipeline welding", "trenching", "backfilling",
        "commissioning", "pre-commissioning", "scada", "cathodic protection",
        "right of way", "row", "pressure testing", "golden tie-in",
        "cased crossing", "sv station", "sectionalizing valve", "ip station",
        "intermediate pigging station", "compressor station", "metering station"
    }

    # Technical Standards & Specifications
    STANDARDS: Dict[str, str] = {
        "oisd-141": "OISD-141 (Design and Construction Requirements for Cross Country Hydrocarbon Pipelines)",
        "oisd 141": "OISD-141",
        "asme b31.8": "ASME B31.8 (Gas Transmission and Distribution Piping Systems)",
        "asme b31.4": "ASME B31.4 (Pipeline Transportation Systems for Liquids and Slurries)",
        "api 5l": "API Spec 5L (Specification for Line Pipe)",
        "api 1104": "API 1104 (Welding of Pipelines and Related Facilities)",
        "pngrb": "Petroleum and Natural Gas Regulatory Board Regulations",
        "iso 45001": "ISO 45001:2018 (Occupational Health & Safety Management System)",
        "iso 14001": "ISO 14001:2015 (Environmental Management System)",
        "iso 9001": "ISO 9001:2015 (Quality Management System)"
    }

    # Technical Manpower Roles & Certifications
    MANPOWER_ROLES: List[str] = [
        "pipeline engineer", "lead pipeline engineer", "project manager",
        "welding engineer", "welding inspector", "qa/qc engineer", "qa/qc manager",
        "hse officer", "safety officer", "safety manager", "ndt engineer",
        "cathodic protection engineer", "commissioning engineer", "site incharge",
        "resident construction manager", "pipeline superintendent"
    ]

    ENGINEERING_QUALIFICATIONS: List[str] = [
        "b.tech mechanical", "b.e. mechanical", "b.tech civil", "b.e. civil",
        "b.tech chemical", "b.e. chemical", "m.tech pipeline", "diploma mechanical",
        "bachelor of engineering", "bachelor of technology", "b.e.", "b.tech"
    ]

    CERTIFICATIONS: List[str] = [
        "ndt level ii", "ndt level iii", "asnt level ii", "asnt level iii",
        "cswip 3.1", "cswip 3.2", "aws cwi", "nebosh", "nebosh igc",
        "nace cp level 1", "nace cp level 2", "iso 45001 lead auditor",
        "iso 14001 lead auditor"
    ]

    # Major Petroleum PSU Clients
    PSU_CLIENTS: List[str] = [
        "gail", "gail (india) limited", "iocl", "indian oil corporation limited",
        "ongc", "oil and natural gas corporation", "bpcl", "bharat petroleum",
        "hpcl", "hindustan petroleum", "oil india limited", "oil",
        "gspc", "gujarat state petroleum corporation", "adani total gas",
        "torrent gas", "indraprastha gas", "igl", "mahanagar gas", "mgl"
    ]

    # Primary Requirement Categories for Phase 2 MVP
    PRIMARY_CATEGORIES: Dict[str, str] = {
        "GST": "Statutory GST Registration & Filing Compliance",
        "PAN": "Income Tax Permanent Account Number Compliance",
        "TURNOVER": "Annual Average Financial Turnover Criterion",
        "OIL_GAS_EXPERIENCE": "Oil & Gas / Hydrocarbon Sector Prior Experience",
        "SIMILAR_PIPELINE_EXPERIENCE": "Cross-Country High-Pressure Transmission Pipeline Execution",
        "TECHNICAL_MANPOWER": "Qualified Technical Key Personnel & Pipeline Engineers",
        "TENDER_SPECIFIC": "Tender Specific Conditions (HSE, OEM Authorization, Local Content)"
    }

    TENDER_SPECIFIC_SUBTYPES: Dict[str, str] = {
        "HSE_SAFETY": "Occupational Health, Safety & Environmental Management (ISO 45001 / ISO 14001)",
        "OEM_AUTHORIZATION": "Original Equipment Manufacturer (OEM) Line Pipe / Valve Authorization",
        "LOCAL_CONTENT": "Class-I / Class-II Local Content (Make in India - DPIIT Order)"
    }

    @classmethod
    def contains_petroleum_concept(cls, text: str) -> bool:
        """Returns True if text mentions petroleum or pipeline domain concepts."""
        lower = text.lower()
        if any(term in lower for term in cls.PIPELINE_CONSTRUCTION_TERMS):
            return True
        for sector_terms in cls.SECTORS.values():
            if any(term in lower for term in sector_terms):
                return True
        if any(client in lower for client in cls.PSU_CLIENTS):
            return True
        return False

    @classmethod
    def get_canonical_sector(cls, text: str) -> str:
        """Normalizes sector text into standard OIL_AND_GAS or subcategory."""
        lower = text.lower()
        for sector_name, terms in cls.SECTORS.items():
            if any(t in lower for t in terms):
                return sector_name
        return "OIL_AND_GAS"
