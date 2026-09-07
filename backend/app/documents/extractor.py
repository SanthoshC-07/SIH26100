"""
Document Text & OCR Extraction Pipeline
Ministry of Petroleum & Natural Gas - Petroleum & Natural Gas Pipeline Procurement
"""
import os
import io
import re
import shutil
from typing import Dict, List, Any, Optional
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

from app.core.logging_config import logger
from app.nlp.text_normalizer import TextNormalizer

# Resolve Tessdata Path for PyMuPDF Embedded Tesseract C-Engine
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TESSDATA_DIR = os.path.join(BASE_DIR, "tessdata")
if not os.path.exists(TESSDATA_DIR):
    os.makedirs(TESSDATA_DIR, exist_ok=True)

PLACEHOLDER_PATTERNS = [
    r"\[Scanned Image Content:",
    r"\[Scanned Image Document:",
    r"\[Scanned Page",
    r"\[OCR FAILED",
    r"\[TEXT EXTRACTION FAILED",
    r"\[Image rendering retained"
]

class DocumentExtractor:
    """
    Extracts authentic text, metadata, and page structure from uploaded PDF and image documents.
    Pipeline:
      1. Digital PDF -> PyMuPDF Native Stream -> Text Density & Quality Analysis
      2. Scanned / Low-Density PDF -> Render Page at 300 DPI -> PyMuPDF Embedded Tesseract C-OCR
      3. Standalone Image (PNG, JPG, TIFF, BMP) -> In-Memory Conversion -> 300 DPI Tesseract OCR
      4. Text Normalization, Placeholder Rejection, and Logging Telemetry
    """

    @staticmethod
    def is_placeholder_text(text: Optional[str]) -> bool:
        """
        Validates if text contains synthetic placeholder or error strings.
        """
        if not text or not str(text).strip():
            return True
        clean = str(text).strip()
        for pat in PLACEHOLDER_PATTERNS:
            if re.search(pat, clean, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def get_tessdata_path() -> Optional[str]:
        """
        Returns absolute path to valid tessdata directory containing eng.traineddata.
        """
        candidate_dirs = [
            TESSDATA_DIR,
            os.path.join(os.getcwd(), "backend", "tessdata"),
            os.path.join(os.getcwd(), "tessdata"),
            r"C:\Program Files\Tesseract-OCR\tessdata",
            r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
            os.environ.get("TESSDATA_PREFIX", "")
        ]
        for c in candidate_dirs:
            if c and os.path.exists(os.path.join(c, "eng.traineddata")):
                return os.path.abspath(c)
        return os.path.abspath(TESSDATA_DIR) if os.path.exists(TESSDATA_DIR) else None

    @staticmethod
    def _run_ocr_on_pixmap(pix: fitz.Pixmap) -> str:
        """
        Executes OCR on a rendered fitz Pixmap using PyMuPDF embedded Tesseract or pytesseract.
        """
        tess_path = DocumentExtractor.get_tessdata_path()
        img_bytes = pix.tobytes("png")

        # Strategy 1: PyMuPDF Embedded Tesseract C-Engine
        try:
            temp_img_doc = fitz.open("png", img_bytes)
            temp_pdf_bytes = temp_img_doc.convert_to_pdf()
            temp_img_doc.close()

            doc_temp = fitz.open("pdf", temp_pdf_bytes)
            page_temp = doc_temp[0]
            if tess_path and os.path.exists(os.path.join(tess_path, "eng.traineddata")):
                tp = page_temp.get_textpage_ocr(language="eng", tessdata=tess_path, dpi=300)
            else:
                tp = page_temp.get_textpage_ocr(language="eng", dpi=300)
            ocr_text = page_temp.get_text(textpage=tp).strip()
            doc_temp.close()

            if ocr_text:
                return ocr_text
        except Exception as embedded_err:
            logger.debug(f"PyMuPDF embedded OCR pass notice: {embedded_err}")

        # Strategy 2: Fallback to pytesseract if installed
        try:
            img = Image.open(io.BytesIO(img_bytes))
            # Enhance image for OCR
            img = img.convert("L")
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            text = pytesseract.image_to_string(img).strip()
            if text:
                return text
        except Exception as pytess_err:
            logger.debug(f"pytesseract fallback notice: {pytess_err}")

        return ""

    @staticmethod
    def extract_document(file_path: str) -> Dict[str, Any]:
        """
        Extracts verified authentic content from a document file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found at {file_path}")

        filename = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        logger.info(f"[UPLOAD] filename={filename} extension={ext} path={file_path}")

        if ext == ".pdf":
            result = DocumentExtractor._extract_pdf(file_path)
        elif ext in [".txt", ".json", ".md", ".csv"]:
            result = DocumentExtractor._extract_text(file_path)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"]:
            result = DocumentExtractor._extract_image(file_path)
        else:
            result = DocumentExtractor._extract_generic(file_path)

        # Telemetry logging
        raw_len = len(result.get("full_text", ""))
        preview = result.get("full_text", "")[:120].replace("\n", " ")
        logger.info(f"[OCR] engine={result.get('extraction_method')} scanned={result.get('is_scanned')} pages={result.get('page_count')} raw_text_length={raw_len}")
        logger.info(f"[OCR] text_preview=\"{preview}\"")

        return result

    @staticmethod
    def extract_text_and_tables(file_path: str) -> Dict[str, Any]:
        return DocumentExtractor.extract_document(file_path)

    @staticmethod
    def _extract_pdf(file_path: str) -> Dict[str, Any]:
        pages_data = []
        raw_full_text_list = []
        norm_full_text_list = []
        is_scanned_overall = False
        overall_method = "PDF_TEXT"

        try:
            doc = fitz.open(file_path)
            page_count = len(doc)

            for page_idx in range(page_count):
                page = doc[page_idx]
                page_number = page_idx + 1
                native_text = page.get_text("text").strip()

                alpha_count = sum(1 for c in native_text if c.isalnum())
                ocr_applied = False
                method = "PDF_TEXT"
                confidence = 0.98
                final_text = native_text

                # Trigger OCR if page text is very sparse or contains scanned image figures
                images = page.get_images()
                if alpha_count < 40 or (len(images) > 0 and alpha_count < 80):
                    try:
                        pix = page.get_pixmap(dpi=300)
                        ocr_text = DocumentExtractor._run_ocr_on_pixmap(pix)
                        if ocr_text and len(ocr_text) > len(native_text):
                            final_text = ocr_text
                            ocr_applied = True
                            is_scanned_overall = True
                            method = "TESSERACT_OCR"
                            confidence = 0.94
                    except Exception as ocr_err:
                        logger.warning(f"OCR page {page_number} execution warning: {ocr_err}")

                # Reject any placeholder text
                if DocumentExtractor.is_placeholder_text(final_text):
                    final_text = ""

                norm_text = TextNormalizer.normalize_text(final_text) if final_text else ""
                has_tables = bool("table" in final_text.lower() or "\t" in final_text or " | " in final_text or "cr" in final_text.lower() or "fy " in final_text.lower())
                proc_status = "SUCCESS" if final_text else "INSUFFICIENT_TEXT"

                pages_data.append({
                    "page_number": page_number,
                    "text": final_text,
                    "raw_text": final_text,
                    "normalized_text": norm_text,
                    "has_tables": has_tables,
                    "ocr_applied": ocr_applied,
                    "extraction_method": method,
                    "processing_status": proc_status,
                    "confidence": confidence if final_text else 0.0
                })
                if final_text:
                    raw_full_text_list.append(final_text)
                    norm_full_text_list.append(norm_text)

            doc.close()

            if is_scanned_overall:
                overall_method = "TESSERACT_OCR"

            full_text = "\n\n--- Page Break ---\n\n".join(raw_full_text_list)
            full_norm = "\n\n--- Page Break ---\n\n".join(norm_full_text_list)

            return {
                "page_count": page_count,
                "is_scanned": is_scanned_overall,
                "extraction_method": overall_method,
                "full_text": full_text,
                "full_normalized_text": full_norm,
                "pages": pages_data
            }

        except Exception as e:
            logger.error(f"Error extracting PDF {file_path}: {e}")
            return {
                "page_count": 1,
                "is_scanned": False,
                "extraction_method": "MANUAL_REVIEW",
                "full_text": "",
                "full_normalized_text": "",
                "pages": [{
                    "page_number": 1,
                    "text": "",
                    "raw_text": "",
                    "normalized_text": "",
                    "has_tables": False,
                    "ocr_applied": False,
                    "extraction_method": "MANUAL_REVIEW",
                    "processing_status": "ERROR",
                    "confidence": 0.0
                }]
            }

    @staticmethod
    def _extract_image(file_path: str) -> Dict[str, Any]:
        """
        Extracts text from image files (PNG, JPG, TIFF, BMP) via 300 DPI OCR.
        Never returns placeholder strings.
        """
        raw_text = ""
        norm_text = ""
        confidence = 0.92
        proc_status = "SUCCESS"

        try:
            with open(file_path, "rb") as f:
                img_bytes = f.read()

            temp_img_doc = fitz.open(os.path.splitext(file_path)[1].lstrip(".").lower(), img_bytes)
            pix = temp_img_doc[0].get_pixmap(dpi=300)
            raw_text = DocumentExtractor._run_ocr_on_pixmap(pix)
            temp_img_doc.close()

            # If empty, try PIL fallback
            if not raw_text:
                img = Image.open(file_path).convert("L")
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
                raw_text = pytesseract.image_to_string(img).strip()

        except Exception as e:
            logger.warning(f"Image OCR execution notice on {file_path}: {e}")

        # Check for placeholder corruption
        if DocumentExtractor.is_placeholder_text(raw_text):
            raw_text = ""

        if raw_text:
            norm_text = TextNormalizer.normalize_text(raw_text)
            proc_status = "SUCCESS"
            confidence = 0.94
        else:
            proc_status = "INSUFFICIENT_TEXT"
            confidence = 0.0

        return {
            "page_count": 1,
            "is_scanned": True,
            "extraction_method": "TESSERACT_OCR",
            "full_text": raw_text,
            "full_normalized_text": norm_text,
            "pages": [{
                "page_number": 1,
                "text": raw_text,
                "raw_text": raw_text,
                "normalized_text": norm_text,
                "has_tables": bool("gst" in raw_text.lower() or "pan" in raw_text.lower() or "fy " in raw_text.lower()),
                "ocr_applied": True,
                "extraction_method": "TESSERACT_OCR",
                "processing_status": proc_status,
                "confidence": confidence
            }]
        }

    @staticmethod
    def _extract_text(file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        norm = TextNormalizer.normalize_text(content)
        return {
            "page_count": 1,
            "is_scanned": False,
            "extraction_method": "PYMUPDF",
            "full_text": content,
            "full_normalized_text": norm,
            "pages": [{
                "page_number": 1,
                "text": content,
                "raw_text": content,
                "normalized_text": norm,
                "has_tables": True,
                "ocr_applied": False,
                "extraction_method": "PDF_TEXT",
                "processing_status": "SUCCESS",
                "confidence": 1.0
            }]
        }

    @staticmethod
    def _extract_generic(file_path: str) -> Dict[str, Any]:
        return {
            "page_count": 1,
            "is_scanned": False,
            "extraction_method": "PDF_TEXT",
            "full_text": "",
            "full_normalized_text": "",
            "pages": [{
                "page_number": 1,
                "text": "",
                "raw_text": "",
                "normalized_text": "",
                "has_tables": False,
                "ocr_applied": False,
                "extraction_method": "PDF_TEXT",
                "processing_status": "UNSUPPORTED_FORMAT",
                "confidence": 0.0
            }]
        }
