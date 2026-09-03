import re
from typing import List, Dict, Any, Optional

class EntityExtractor:
    """
    Extracts structured statutory, financial, and petroleum/pipeline domain entities
    from raw document text along with page location, confidence, and context snippets.
    """

    @staticmethod
    def extract_all_entities(pages_data: List[Dict[str, Any]], document_name: str = "") -> List[Dict[str, Any]]:
        extracted_entities = []
        
        for page in pages_data:
            page_num = page.get("page_number", 1)
            text = page.get("text", "")
            if not text:
                continue

            # 1. GSTIN
            gst_matches = EntityExtractor.extract_gstin(text)
            for val, snippet in gst_matches:
                extracted_entities.append({
                    "entity_type": "GSTIN",
                    "entity_value": val,
                    "normalized_value": val.upper(),
                    "confidence": 0.98,
                    "page_number": page_num,
                    "context_snippet": snippet
                })

            # 2. PAN
            pan_matches = EntityExtractor.extract_pan(text)
            for val, snippet in pan_matches:
                extracted_entities.append({
                    "entity_type": "PAN",
                    "entity_value": val,
                    "normalized_value": val.upper(),
                    "confidence": 0.98,
                    "page_number": page_num,
                    "context_snippet": snippet
                })

            # 3. UDYAM
            udyam_matches = EntityExtractor.extract_udyam(text)
            for val, snippet in udyam_matches:
                extracted_entities.append({
                    "entity_type": "UDYAM_NUMBER",
                    "entity_value": val,
                    "normalized_value": val.upper(),
                    "confidence": 0.99,
                    "page_number": page_num,
                    "context_snippet": snippet
                })

            # 4. CIN
            cin_matches = EntityExtractor.extract_cin(text)
            for val, snippet in cin_matches:
                extracted_entities.append({
                    "entity_type": "CIN",
                    "entity_value": val,
                    "normalized_value": val.upper(),
                    "confidence": 0.96,
                    "page_number": page_num,
                    "context_snippet": snippet
                })

            # 5. Financial Turnover / Audited figures
            turnover_items = EntityExtractor.extract_turnover_records(text)
            for item in turnover_items:
                extracted_entities.append({
                    "entity_type": "FINANCIAL_TURNOVER",
                    "entity_value": f"{item['fy']}: ₹{item['value_cr']:.2f} Cr",
                    "normalized_value": str(item['value_inr']),
                    "confidence": item['confidence'],
                    "page_number": page_num,
                    "context_snippet": item['context']
                })

            # 6. Oil & Gas / Hydrocarbon Project Experience
            oil_gas_items = EntityExtractor.extract_oil_gas_projects(text)
            for item in oil_gas_items:
                extracted_entities.append({
                    "entity_type": "OIL_GAS_PROJECT",
                    "entity_value": item['project_title'],
                    "normalized_value": item['project_title'],
                    "confidence": item['confidence'],
                    "page_number": page_num,
                    "context_snippet": item['context']
                })

            # 7. Similar Pipeline Specifications (Length in km, Diameter in inches)
            pipeline_specs = EntityExtractor.extract_pipeline_specs(text)
            for item in pipeline_specs:
                if "length_km" in item:
                    extracted_entities.append({
                        "entity_type": "PIPELINE_LENGTH_KM",
                        "entity_value": f"{item['length_km']:.1f} km",
                        "normalized_value": str(item['length_km']),
                        "confidence": item['confidence'],
                        "page_number": page_num,
                        "context_snippet": item['context']
                    })
                if "diameter_inch" in item:
                    extracted_entities.append({
                        "entity_type": "PIPELINE_DIAMETER_INCH",
                        "entity_value": f"{item['diameter_inch']:.1f} inch",
                        "normalized_value": str(item['diameter_inch']),
                        "confidence": item['confidence'],
                        "page_number": page_num,
                        "context_snippet": item['context']
                    })

            # 8. Technical Manpower & Engineering Personnel
            manpower_items = EntityExtractor.extract_manpower(text)
            for item in manpower_items:
                extracted_entities.append({
                    "entity_type": "MANPOWER_RECORD",
                    "entity_value": f"{item['name']} ({item['designation']} - {item['experience_years']} years)",
                    "normalized_value": str(item['experience_years']),
                    "confidence": item['confidence'],
                    "page_number": page_num,
                    "context_snippet": item['context']
                })

            # 9. HSE / Safety Management Certifications (ISO 45001 / ISO 14001)
            hse_items = EntityExtractor.extract_hse_certifications(text)
            for item in hse_items:
                extracted_entities.append({
                    "entity_type": "HSE_CERTIFICATION",
                    "entity_value": item['cert_name'],
                    "normalized_value": item['cert_name'],
                    "confidence": item['confidence'],
                    "page_number": page_num,
                    "context_snippet": item['context']
                })

            # 10. Local Content / Make in India Percentage
            local_content_matches = EntityExtractor.extract_local_content(text)
            for item in local_content_matches:
                extracted_entities.append({
                    "entity_type": "LOCAL_CONTENT_PERCENT",
                    "entity_value": f"{item['percent']}% ({item['classification']})",
                    "normalized_value": str(item['percent']),
                    "confidence": item['confidence'],
                    "page_number": page_num,
                    "context_snippet": item['context']
                })

            # 11. OEM Authorization details
            oem_matches = EntityExtractor.extract_oem_details(text)
            for item in oem_matches:
                extracted_entities.append({
                    "entity_type": "OEM_AUTHORIZATION",
                    "entity_value": f"OEM: {item.get('oem_name')}, Authorized: {item.get('authorized_bidder')}, Tender: {item.get('tender_ref')}",
                    "normalized_value": item.get('authorized_bidder', ''),
                    "confidence": item.get('confidence', 0.92),
                    "page_number": page_num,
                    "context_snippet": item.get('context', '')
                })

            # 12. Blacklisting / Non-Debarment declaration
            blacklist_decl = EntityExtractor.extract_blacklist_declaration(text)
            if blacklist_decl:
                extracted_entities.append({
                    "entity_type": "BLACKLIST_DECLARATION",
                    "entity_value": blacklist_decl["status"],
                    "normalized_value": "NOT_DEBARRED" if "not" in blacklist_decl["status"].lower() else "DEBARRED",
                    "confidence": 0.95,
                    "page_number": page_num,
                    "context_snippet": blacklist_decl["context"]
                })

            # 13. Company Legal Name candidates
            name_candidates = EntityExtractor.extract_company_names(text)
            for name, snippet in name_candidates:
                extracted_entities.append({
                    "entity_type": "COMPANY_NAME",
                    "entity_value": name,
                    "normalized_value": EntityExtractor.normalize_company_name(name),
                    "confidence": 0.90,
                    "page_number": page_num,
                    "context_snippet": snippet
                })

        return extracted_entities

    @staticmethod
    def extract_gstin(text: str) -> List[tuple]:
        pattern = r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})\b"
        matches = []
        for match in re.finditer(pattern, text, re.IGNORECASE):
            val = match.group(1).upper()
            start = max(0, match.start() - 60)
            end = min(len(text), match.end() + 60)
            matches.append((val, text[start:end].strip()))
        return matches

    @staticmethod
    def extract_pan(text: str) -> List[tuple]:
        pattern = r"\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b"
        matches = []
        for match in re.finditer(pattern, text, re.IGNORECASE):
            val = match.group(1).upper()
            start = max(0, match.start() - 60)
            end = min(len(text), match.end() + 60)
            matches.append((val, text[start:end].strip()))
        return matches

    @staticmethod
    def extract_udyam(text: str) -> List[tuple]:
        pattern = r"\b(UDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7})\b"
        matches = []
        for match in re.finditer(pattern, text, re.IGNORECASE):
            val = match.group(1).upper()
            start = max(0, match.start() - 60)
            end = min(len(text), match.end() + 60)
            matches.append((val, text[start:end].strip()))
        return matches

    @staticmethod
    def extract_cin(text: str) -> List[tuple]:
        pattern = r"\b([LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6})\b"
        matches = []
        for match in re.finditer(pattern, text, re.IGNORECASE):
            val = match.group(1).upper()
            start = max(0, match.start() - 60)
            end = min(len(text), match.end() + 60)
            matches.append((val, text[start:end].strip()))
        return matches

    @staticmethod
    def extract_turnover_records(text: str) -> List[Dict[str, Any]]:
        records = []
        fy_pattern = r"(?:FY|Financial Year)?\s*[:\s]?\s*(202[0-9](?:-|\s*to\s*|/)(?:2[0-9]|[0-9]{2}))\D{0,40}?([0-9]+(?:\.[0-9]+)?)\s*(?:Cr|Crore|Crores|Lakh|Lakhs|INR|Rs\.?)"
        for match in re.finditer(fy_pattern, text, re.IGNORECASE):
            fy = match.group(1).strip()
            val_str = match.group(2).strip()
            try:
                num = float(val_str)
                context_lower = text[match.start():match.end()+30].lower()
                if "lakh" in context_lower:
                    val_cr = num / 100.0
                    val_inr = num * 100000.0
                else:
                    val_cr = num
                    val_inr = num * 10000000.0
                    
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                records.append({
                    "fy": fy,
                    "value_cr": val_cr,
                    "value_inr": val_inr,
                    "confidence": 0.95,
                    "context": text[start:end].strip()
                })
            except ValueError:
                pass
        return records

    @staticmethod
    def extract_oil_gas_projects(text: str) -> List[Dict[str, Any]]:
        results = []
        keywords = ["natural gas", "oil and gas", "petroleum", "pipeline laying", "refinery", "hydrocarbon", "gas transmission", "iocl", "gail", "ongc"]
        text_lower = text.lower()
        if any(kw in text_lower for kw in keywords):
            # Extract sentence or block
            sentences = re.split(r"[\n\.]+", text)
            for s in sentences:
                s_clean = s.strip()
                if len(s_clean) > 25 and any(kw in s_clean.lower() for kw in keywords):
                    results.append({
                        "project_title": s_clean[:120],
                        "confidence": 0.94,
                        "context": s_clean
                    })
        return results[:4]

    @staticmethod
    def extract_pipeline_specs(text: str) -> List[Dict[str, Any]]:
        results = []
        # Match km: "135 km", "120.5 km pipeline", "60 kilometers"
        km_pattern = r"(\d+(?:\.\d+)?)\s*(?:km|kms|kilometers|kilometres)\b"
        for match in re.finditer(km_pattern, text, re.IGNORECASE):
            try:
                km_val = float(match.group(1))
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                results.append({
                    "length_km": km_val,
                    "confidence": 0.96,
                    "context": text[start:end].strip()
                })
            except ValueError:
                pass

        # Match diameter: "24 inch", "24\"", "18-inch diameter", "600 mm"
        dia_pattern = r"(\d+(?:\.\d+)?)\s*(?:inch|\"|-inch|NB|mm\s*dia)\b"
        for match in re.finditer(dia_pattern, text, re.IGNORECASE):
            try:
                dia_val = float(match.group(1))
                # Convert mm to inch if > 50
                if "mm" in text[match.start():match.end()].lower() and dia_val > 50:
                    dia_val = round(dia_val / 25.4, 1)
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                results.append({
                    "diameter_inch": dia_val,
                    "confidence": 0.94,
                    "context": text[start:end].strip()
                })
            except ValueError:
                pass

        return results

    @staticmethod
    def extract_manpower(text: str) -> List[Dict[str, Any]]:
        results = []
        # Look for names with years of experience
        # e.g., "Rajesh Sharma (Lead Pipeline Engineer) - 12 years experience"
        lines = text.split("\n")
        for line in lines:
            line_str = line.strip()
            exp_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?|yr)\b", line_str, re.IGNORECASE)
            has_title = any(t in line_str.lower() for t in ["engineer", "manager", "inspector", "officer", "ndt", "welding", "lead", "specialist"])
            
            if exp_match and has_title:
                name_match = re.search(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", line_str)
                name = name_match.group(1) if name_match else "Pipeline Engineer"
                
                results.append({
                    "name": name,
                    "designation": line_str[:60],
                    "experience_years": float(exp_match.group(1)),
                    "confidence": 0.95,
                    "context": line_str
                })
        return results

    @staticmethod
    def extract_hse_certifications(text: str) -> List[Dict[str, Any]]:
        results = []
        certs = ["ISO 45001", "ISO 14001", "OHSAS 18001", "ISO 9001", "HSE Policy", "Safety Manual"]
        for c in certs:
            if c.lower() in text.lower():
                start = max(0, text.lower().find(c.lower()) - 40)
                end = min(len(text), text.lower().find(c.lower()) + 80)
                results.append({
                    "cert_name": c,
                    "confidence": 0.96,
                    "context": text[start:end].strip()
                })
        return results

    @staticmethod
    def extract_local_content(text: str) -> List[Dict[str, Any]]:
        results = []
        pattern = r"(?:local\s+content|indigenous\s+content|domestic\s+value\s+addition)[^\n0-9]{0,40}?([0-9]{1,3}(?:\.[0-9]+)?)\s*%"
        for match in re.finditer(pattern, text, re.IGNORECASE):
            try:
                val = float(match.group(1))
                classification = "Class-I Local Supplier" if val >= 50 else ("Class-II Local Supplier" if val >= 20 else "Non-Local Supplier")
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                results.append({
                    "percent": val,
                    "classification": classification,
                    "confidence": 0.94,
                    "context": text[start:end].strip()
                })
            except ValueError:
                pass
        return results

    @staticmethod
    def extract_oem_details(text: str) -> List[Dict[str, Any]]:
        results = []
        lower = text.lower()
        if "manufacturer's authorization" in lower or "oem authorization" in lower or "maf" in lower or "authorized partner" in lower or "line pipe manufacturer" in lower:
            oem_match = re.search(r"(?:we|m/s|from)\s+([A-Z][A-Za-z0-9\s,\.&]{3,50}?(?:Pvt|Private|Ltd|Limited|Inc|Corp|LLC|Tubular|Steel|Valves))\b", text)
            oem_name = oem_match.group(1).strip() if oem_match else "OEM Line Pipe Manufacturer"
            
            auth_match = re.search(r"(?:authorize|appoint|confirm)\s+(?:M/s\s+)?([A-Z][A-Za-z0-9\s,\.&]{3,60}?(?:Pvt|Private|Ltd|Limited|LLP|Engineering))\b", text, re.IGNORECASE)
            auth_bidder = auth_match.group(1).strip() if auth_match else ""
            
            tender_match = re.search(r"(?:Tender\s*(?:No|Ref|Number)?[:\.\s]+)([A-Za-z0-9\/\-_]+)", text, re.IGNORECASE)
            tender_ref = tender_match.group(1).strip() if tender_match else ""
            
            results.append({
                "oem_name": oem_name,
                "authorized_bidder": auth_bidder,
                "tender_ref": tender_ref,
                "confidence": 0.93,
                "context": text[:300].strip()
            })
        return results

    @staticmethod
    def extract_blacklist_declaration(text: str) -> Optional[Dict[str, Any]]:
        lower = text.lower()
        if "blacklisted" in lower or "debarred" in lower or "non-conviction" in lower or "integrity pact" in lower:
            if "not been blacklisted" in lower or "never been debarred" in lower or "not debarred" in lower:
                return {
                    "status": "Declared NOT Blacklisted / Debarred",
                    "context": text[:250].strip()
                }
            elif "has been blacklisted" in lower or "debarred by" in lower:
                return {
                    "status": "FLAGGED: Blacklisting / Debarment Disclosed",
                    "context": text[:250].strip()
                }
        return None

    @staticmethod
    def extract_company_names(text: str) -> List[tuple]:
        pattern = r"\b([A-Z][A-Za-z0-9\s,\.&]{3,50}?(?:Private Limited|Pvt\.?\s*Ltd\.?|Limited|Ltd\.?|LLP|Hydrocarbon|Engineering|Projects))\b"
        matches = []
        for match in re.finditer(pattern, text):
            name = match.group(1).strip()
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            matches.append((name, text[start:end].strip()))
        return matches[:3]

    @staticmethod
    def normalize_company_name(name: str) -> str:
        if not name:
            return ""
        n = name.lower().strip()
        n = re.sub(r"\bprivate\s+limited\b", "pvt ltd", n)
        n = re.sub(r"\blimited\b", "ltd", n)
        n = re.sub(r"\bm\/s\.?\b", "", n)
        n = re.sub(r"[^\w\s]", "", n)
        return " ".join(n.split())
