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
    session_id = None
    try:
        # Validate request
        if request.session_id and len(request.session_id.strip()) == 0:
            request.session_id = None
        
        # Get or create session ID
        try:
            session_id = get_or_create_session_id(request.session_id)
            logger.info(f"Processing consent for session: {session_id}")
        except Exception as session_error:
            logger.error(f"Failed to get/create session: {session_error}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize session: {str(session_error)[:200]}"
            )

        # Set consent (even if False, we still want to save the preference)
        try:
            set_consent(session_id, request.consent)
            logger.info(f"Set consent for session {session_id}: {request.consent}")
        except Exception as consent_error:
            logger.error(f"Failed to set consent: {consent_error}", exc_info=True)
            # Don't fail completely - continue with profile save
            # But return a warning in the response
            return {
                "success": False,
                "session_id": session_id,
                "consent": request.consent,
                "warning": f"Consent update failed: {str(consent_error)[:200]}",
                "message": "Profile may be saved but consent status may not be updated"
            }

        # IMPORTANT: Save onboarding data even if consent is False
        # This allows personalization without storing conversation history
        profile_saved = False
        profile_error = None
        if request.onboarding_data:
            try:
                save_user_profile(session_id, request.onboarding_data)
                profile_saved = True
                logger.info(f"Saved onboarding data for session {session_id}")
            except Exception as profile_error_exc:
                profile_error = str(profile_error_exc)
                logger.error(f"Error saving profile: {profile_error_exc}", exc_info=True)
                # Don't fail the entire request if profile save fails
                # But log it for debugging

        response = {
            "success": True,
            "session_id": session_id,
            "consent": request.consent,
            "profile_saved": profile_saved,
            "message": "Consent and profile updated successfully"
        }
        
        if profile_error:
            response["warning"] = f"Profile save failed: {profile_error[:200]}"
            response["success"] = False  # Partial success
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in onboarding consent endpoint: {e}", exc_info=True)
        logger.error(f"Session ID: {session_id}")
        logger.error(f"Request data: consent={request.consent}, has_onboarding_data={bool(request.onboarding_data)}")
        
        # Return detailed error response
        error_detail = {
            "error": "Failed to process onboarding consent",
            "message": str(e)[:200],
            "type": type(e).__name__,
            "session_id": session_id
        }
        
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )
