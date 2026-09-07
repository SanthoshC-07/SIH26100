"""
SIH26100 — Requirement Extractor Module (Backend Proxy)
-------------------------------------------------------
Exports unified_requirement_extractor for the backend app package.
"""
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_THIS_DIR)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from ml.services.requirement_extractor import (
    unified_requirement_extractor,
    UnifiedRequirementExtractor
)

__all__ = [
    "unified_requirement_extractor",
    "UnifiedRequirementExtractor"
]
