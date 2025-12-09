from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict
from app.utils.session import get_or_create_session_id, set_consent, save_user_profile


router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


class ConsentRequest(BaseModel):
    consent: bool
    session_id: Optional[str] = None
    onboarding_data: Optional[Dict] = None


@router.post("/consent")
async def update_consent(request: ConsentRequest):
    """Update user consent for storing conversation history and save onboarding data."""
    session_id = get_or_create_session_id(request.session_id)

    set_consent(session_id, request.consent)

    # Save onboarding data if provided
    if request.onboarding_data and request.consent:
        save_user_profile(session_id, request.onboarding_data)

    return {
        "success": True,
        "session_id": session_id,
        "consent": request.consent,
        "message": "Consent and profile updated successfully"
    }
