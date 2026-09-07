"""
Text Normalization Layer
Ministry of Petroleum & Natural Gas - Petroleum & Natural Gas Pipeline Procurement
"""
import re
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

class TextNormalizer:
    """
    Standardizes procurement and petroleum engineering text while
    preserving raw text representations.
    """

    MONTH_MAP = {
        "january": "01", "jan": "01",
        "february": "02", "feb": "02",
        "march": "03", "mar": "03",
        "april": "04", "apr": "04",
        "may": "05",
        "june": "06", "jun": "06",
        "july": "07", "jul": "07",
        "august": "08", "aug": "08",
        "september": "09", "sep": "09", "sept": "09",
        "october": "10", "oct": "10",
        "november": "11", "nov": "11",
        "december": "12", "dec": "12"
    }

    @classmethod
    def normalize_text(cls, raw_text: str) -> str:
        """
        Applies comprehensive normalization to raw OCR / extracted text.
        """
        if not raw_text:
            return ""

        text = raw_text

        # 1. Normalize line endings and repair hyphenated words across linebreaks
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"(\b[a-zA-Z]{2,})-\s*\n\s*([a-zA-Z]{2,}\b)", r"\1\2", text)

        # 2. Collapse excessive whitespace and tabs
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 3. Clean common OCR mis-read punctuation / unicode quotes
        text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("`", "'")
        text = text.replace("—", "-").replace("–", "-")

        # 4. Standardize Currency (₹, Rs, Rs., INR)
        text = re.sub(r"(?:₹|\brs\b\.?|\brs\.|\binr\b)\s*", "INR ", text, flags=re.IGNORECASE)
        # Fix multiple INR INR
        text = re.sub(r"(?:INR\s+)+", "INR ", text)

        # 5. Standardize Crore & Lakh notations
        text = re.sub(r"\b(?:cr|crore|crores)\b\.?", "Crore", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(?:lakh|lakhs|lac|lacs)\b\.?", "Lakh", text, flags=re.IGNORECASE)

        # 6. Standardize Kilometer notations
        text = re.sub(r"\b(?:km|kms|kilometers?|kilometres?)\b\.?", "KM", text, flags=re.IGNORECASE)

        # 7. Standardize Inch notations
        text = re.sub(r'(\d+)\s*(?:\"|\'\'|inches|inch|in\b)\.?', r"\1 Inch", text, flags=re.IGNORECASE)

        # 8. Standardize Years notations
        text = re.sub(r"\b(?:yrs|years?)\b\.?", "Years", text, flags=re.IGNORECASE)


        # 9. Standardize Financial Year formats (e.g., FY 2023-24, FY 2023-2024, FY23-24)
        text = re.sub(r"\bfy\s*([0-9]{4})\s*[-/]\s*([0-9]{2,4})\b", r"FY \1-\2", text, flags=re.IGNORECASE)
        text = re.sub(r"\bfy\s*([0-9]{2})\s*[-/]\s*([0-9]{2})\b", r"FY 20\1-20\2", text, flags=re.IGNORECASE)

        return text.strip()

    @classmethod
    def parse_currency_amount(cls, text: str) -> Optional[Tuple[float, str]]:
        """
        Parses monetary expressions like 'INR 25 Crore', '₹ 82 Cr', 'Rs. 500 Lakhs'
        Returns: (amount_in_inr, canonical_display)
        Example: (250000000.0, "INR 25.00 Crore")
        """
        # Search for Crore
        m_cr = re.search(r"(?:inr|rs\.?|₹)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:crore|cr)\b", text, re.IGNORECASE)
        if m_cr:
            val = float(m_cr.group(1))
            return val * 10000000.0, f"INR {val:.2f} Crore"

        # Search for Lakh
        m_lakh = re.search(r"(?:inr|rs\.?|₹)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:lakh|lac)\b", text, re.IGNORECASE)
        if m_lakh:
            val = float(m_lakh.group(1))
            return val * 100000.0, f"INR {val:.2f} Lakh"

        # Plain number with INR
        m_num = re.search(r"(?:inr|rs\.?|₹)\s*([0-9,]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
        if m_num:
            num_str = m_num.group(1).replace(",", "")
            val = float(num_str)
            return val, f"INR {val:,.2f}"

        return None

    @classmethod
    def parse_distance_km(cls, text: str) -> Optional[float]:
        """
        Extracts distance in KM (e.g., '135 KM', '100.5 km', 'at least 100 kilometers').
        """
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:km|kms|kilometers?|kilometres?)\b", text, re.IGNORECASE)
        if m:
            return float(m.group(1))
        return None

    @classmethod
    def parse_diameter_inch(cls, text: str) -> Optional[float]:
        """
        Extracts diameter in inches (e.g., '24 Inch', '24\"', '24-inch NB').
        """
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*[-\s]?(?:inch|inches|\"|in\b)", text, re.IGNORECASE)
        if m:
            return float(m.group(1))
        return None


    @classmethod
    def parse_date(cls, text: str) -> Optional[str]:
        """
        Extracts and normalizes dates into ISO format 'YYYY-MM-DD'.
        Handles:
        - 15/03/2025, 15-03-2025, 15.03.2025
        - 2025-03-15, 2025/03/15
        - 15 March 2025, 15th March 2025, March 15, 2025
        """
        # 1. DD-MM-YYYY or DD/MM/YYYY
        m1 = re.search(r"\b([0-3]?[0-9])[-/\.]([0-1]?[0-9])[-/\.]([12][0-9]{3})\b", text)
        if m1:
            d, m, y = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
            if 1 <= m <= 12 and 1 <= d <= 31:
                return f"{y:04d}-{m:02d}-{d:02d}"

        # 2. YYYY-MM-DD
        m2 = re.search(r"\b([12][0-9]{3})[-/\.]([0-1]?[0-9])[-/\.]([0-3]?[0-9])\b", text)
        if m2:
            y, m, d = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
            if 1 <= m <= 12 and 1 <= d <= 31:
                return f"{y:04d}-{m:02d}-{d:02d}"

        # 3. 15th March 2025 or 15 March 2025
        m3 = re.search(r"\b([0-3]?[0-9])(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+([12][0-9]{3})\b", text)
        if m3:
            d = int(m3.group(1))
            month_str = m3.group(2).lower()
            y = int(m3.group(3))
            if month_str in cls.MONTH_MAP and 1 <= d <= 31:
                m = int(cls.MONTH_MAP[month_str])
                return f"{y:04d}-{m:02d}-{d:02d}"

        # 4. March 15, 2025
        m4 = re.search(r"\b([A-Za-z]+)\s+([0-3]?[0-9])(?:st|nd|rd|th)?,?\s+([12][0-9]{3})\b", text)
        if m4:
            month_str = m4.group(1).lower()
            d = int(m4.group(2))
            y = int(m4.group(3))
            if month_str in cls.MONTH_MAP and 1 <= d <= 31:
                m = int(cls.MONTH_MAP[month_str])
                return f"{y:04d}-{m:02d}-{d:02d}"

        return None
