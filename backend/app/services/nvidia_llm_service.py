"""
SIH26100 — Authoritative NVIDIA NIM LLM & Vision Service
---------------------------------------------------------
Integrates NVIDIA NIM endpoint (meta/llama-3.2-90b-vision-instruct)
for petroleum procurement document inspection, tender requirement extraction,
and visual compliance verification.
"""
import os
import json
import base64
import requests
from typing import Dict, Any, Optional, List, Union
from app.core.config import settings
from app.core.logging_config import logger

class NvidiaLLMService:
    """
    Client for NVIDIA NIM Hosted LLM and Multimodal Vision API.
    Default Model: meta/llama-3.2-90b-vision-instruct
    Endpoint: https://integrate.api.nvidia.com/v1/chat/completions
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        invoke_url: Optional[str] = None,
        timeout: int = 30
    ):
        self.api_key = api_key or getattr(settings, "NVIDIA_API_KEY", None) or os.getenv("NVIDIA_API_KEY")
        self.model = model or getattr(settings, "NVIDIA_MODEL", None) or os.getenv("NVIDIA_MODEL", "meta/llama-3.2-90b-vision-instruct")
        self.invoke_url = invoke_url or getattr(settings, "NVIDIA_INVOKE_URL", None) or os.getenv("NVIDIA_INVOKE_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.startswith("nvapi-"))

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        top_p: float = 1.0,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Executes a standard or multimodal chat completion against NVIDIA NIM API.
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "NVIDIA API key not configured.",
                "content": ""
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream
        }

        try:
            response = requests.post(
                self.invoke_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"NVIDIA NIM API error {response.status_code}: {response.text}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text,
                    "content": ""
                }

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {
                "success": True,
                "content": content,
                "raw": data,
                "model": self.model
            }
        except requests.exceptions.Timeout:
            logger.warning(f"NVIDIA NIM API call timed out ({self.timeout}s).")
            return {
                "success": False,
                "error": f"NVIDIA NIM API request timed out ({self.timeout}s)",
                "content": ""
            }
        except Exception as exc:
            logger.error(f"Failed to communicate with NVIDIA NIM: {exc}")
            return {
                "success": False,
                "error": str(exc),
                "content": ""
            }

    def extract_requirement(self, requirement_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured petroleum procurement requirement parameters from clause text
        using NVIDIA LLaMA 3.2 90B Vision Instruct.
        """
        system_instruction = (
            "You are an expert AI parser for Indian Petroleum and Natural Gas procurement tenders (IOCL, ONGC, GAIL, HPCL, BPCL). "
            "Extract structured parameters from the clause into a clean JSON object.\n"
            "JSON schema keys:\n"
            "- category: One of ['GST_TAX_COMPLIANCE', 'MSME_UDYAM_ELIGIBILITY', 'FINANCIAL_ELIGIBILITY', "
            "'EXPERIENCE_ELIGIBILITY', 'OEM_AUTHORIZATION', 'BLACKLISTING_DEBARMENT', 'TECHNICAL_SPECIFICATION', "
            "'INDUSTRY_STANDARD_COMPLIANCE', 'SAFETY_REGULATORY_COMPLIANCE', 'MAKE_IN_INDIA_LOCAL_CONTENT']\n"
            "- threshold: float or null (numerical value in base units e.g. INR or KM)\n"
            "- unit: string or null ('INR', 'CRORE', 'LAKH', 'KM', 'INCH', 'YEARS', 'PERCENT')\n"
            "- value: float or null\n"
            "- minimum_value: float or null\n"
            "- time_period_years: int or null\n"
            "- project_type: string or null\n"
            "- sector: string or null\n"
            "- diameter_inch: float or null\n"
            "- length_km: float or null\n"
            "- experience_years: int or null\n"
            "- required_count: int or null\n"
            "- role: string or null\n"
            "- qualification: string or null\n"
            "- scope: string or null\n"
            "- entities: list of strings\n"
            "Output ONLY valid JSON with no markdown formatting or extra text."
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Extract parameters for this requirement clause:\n{requirement_text}"}
        ]

        res = self.chat_completion(messages, temperature=0.1, max_tokens=512)
        if not res["success"] or not res["content"]:
            return None

        content = res["content"].strip()
        # Clean markdown if present
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            extracted_json = json.loads(content)
            extracted_json["requirement_text"] = requirement_text
            extracted_json["extraction_method"] = "NVIDIA_NIM_LLM"
            return extracted_json
        except Exception as json_err:
            logger.warning(f"Failed to parse LLM JSON output: {json_err} | Output: {content[:100]}")
            return None

    def analyze_document_vision(
        self,
        image_data: Union[str, bytes],
        prompt: str = "Analyze this procurement document, identify document type, issuing authority, dates, signatures, and compliance validity.",
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Analyze an image (scanned certificate, tender page, MAF, stamp) using LLaMA 3.2 90B Vision.
        Accepts:
          - image_data: base64 string, URL, or raw bytes
        """
        if isinstance(image_data, str) and os.path.isfile(image_data):
            ext = os.path.splitext(image_data)[1].lower()
            detected_mime = "image/png" if ext == ".png" else "image/jpeg"
            with open(image_data, "rb") as img_file:
                b64_str = base64.b64encode(img_file.read()).decode("utf-8")
            image_url = f"data:{detected_mime};base64,{b64_str}"
        elif isinstance(image_data, bytes):
            b64_str = base64.b64encode(image_data).decode("utf-8")
            image_url = f"data:{mime_type};base64,{b64_str}"
        elif isinstance(image_data, str) and (image_data.startswith("http://") or image_data.startswith("https://") or image_data.startswith("data:")):
            image_url = image_data
        else:
            # Assume base64 string
            image_url = f"data:{mime_type};base64,{image_data}"

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]

        res = self.chat_completion(messages, temperature=0.2, max_tokens=1024)
        return res

    def get_info(self) -> Dict[str, Any]:
        """Return model metadata and configuration status."""
        return {
            "name": "NVIDIA NIM LLaMA 3.2 90B Vision Instruct",
            "provider": "NVIDIA API Catalog",
            "model": self.model,
            "invoke_url": self.invoke_url,
            "is_configured": self.is_configured,
            "multimodal_vision": True,
            "status": "READY" if self.is_configured else "API_KEY_REQUIRED"
        }


# Global instance singleton
nvidia_llm_service = NvidiaLLMService()
