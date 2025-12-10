from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.utils.session import get_or_create_session_id, set_consent, save_user_profile
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


class ConsentRequest(BaseModel):
    consent: bool
    session_id: Optional[str] = None
    onboarding_data: Optional[Dict] = None


@router.post("/consent")
async def update_consent(request: ConsentRequest):
    """Update user consent for storing conversation history and save onboarding data."""
    try:
        session_id = get_or_create_session_id(request.session_id)

        # Set consent (even if False, we still want to save the preference)
        set_consent(session_id, request.consent)

        # IMPORTANT: Save onboarding data even if consent is False
        # This allows personalization without storing conversation history
        if request.onboarding_data:
            try:
                save_user_profile(session_id, request.onboarding_data)
                logger.info(f"Saved onboarding data for session {session_id}: {request.onboarding_data}")
            except Exception as profile_error:
                logger.error(f"Error saving profile: {profile_error}", exc_info=True)
                # Don't fail the entire request if profile save fails
                # But log it for debugging

        return {
            "success": True,
            "session_id": session_id,
            "consent": request.consent,
            "message": "Consent and profile updated successfully"
        }
    except Exception as e:
        logger.error(f"Error in onboarding consent endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing onboarding: {str(e)}"
        )
