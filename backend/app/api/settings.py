from fastapi import APIRouter, Depends
from app.core.config import settings
from app.schemas.schemas import SettingsUpdate
from app.models.models import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings & Configuration"])

@router.get("")
def get_system_settings():
    return {
        "scoring_weights": settings.SCORING_WEIGHTS,
        "confidence_high": settings.CONFIDENCE_HIGH,
        "confidence_medium": settings.CONFIDENCE_MEDIUM,
        "allowed_extensions": settings.ALLOWED_EXTENSIONS,
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        "use_mock_portals": settings.USE_MOCK_PORTALS,
        "government_source_label": settings.GOVERNMENT_SOURCE_LABEL
    }

@router.post("")
def update_system_settings(
    settings_in: SettingsUpdate,
    current_user: User = Depends(get_current_user)
):
    settings.SCORING_WEIGHTS = settings_in.scoring_weights
    settings.CONFIDENCE_HIGH = settings_in.confidence_high
    settings.CONFIDENCE_MEDIUM = settings_in.confidence_medium
    
    return {
        "message": "System compliance settings updated successfully",
        "scoring_weights": settings.SCORING_WEIGHTS,
        "confidence_high": settings.CONFIDENCE_HIGH,
        "confidence_medium": settings.CONFIDENCE_MEDIUM
    }
