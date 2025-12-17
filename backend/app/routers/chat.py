from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from typing import Optional
from app.utils.session import get_or_create_session_id, get_consent, save_message_to_history, set_consent
from app.utils.heuristics import check_heuristics
from app.services.router import route_message
from app.services.ai_models import stream_speed_model_response, stream_quality_model_response
from app.utils.session import get_conversation_history
from app.utils.session import save_user_profile
import logging
import traceback

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    session_id: Optional[str] = Field(None, max_length=200, description="Session ID")
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v


class SaveMessageRequest(BaseModel):
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    is_onboarding: Optional[bool] = False


@router.post("")
async def chat(request: ChatRequest):
    """
    Main chat endpoint with Dynamic Model Router.
    
    Flow:
    1. Triage: Receive message
    2. Heuristic Check: Detect confusion/confidence
    3. Router Model: Determine route (speed/quality)
    4. Specialist Model: Generate response
    """
    session_id = None
    message = None
    
    try:
        # Validate message (already validated by Pydantic, but double-check)
        message = request.message
        if not message or len(message.strip()) == 0:
            async def empty_message_response():
                yield f"data: Please provide a non-empty message.\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(empty_message_response(), media_type="text/event-stream")
        
        logger.info(f"Chat request received - message length: {len(message)}, session_id: {request.session_id}")
        
        # Check environment variables early
        try:
            from app.config import get_settings_instance
            settings = get_settings_instance()
            if not settings.openai_api_key:
                logger.error("OpenAI API key is missing")
                async def config_error_response():
                    error_msg = "Configuration error: OpenAI API key is missing. Please check your environment variables."
                    yield f"data: {error_msg}\n\n"
                    yield "data: [DONE]\n\n"
                return StreamingResponse(config_error_response(), media_type="text/event-stream")
        except Exception as config_error:
            logger.error(f"Failed to load configuration: {config_error}", exc_info=True)
            async def config_error_response():
                error_msg = f"Configuration error: {str(config_error)[:200]}. Please check your environment variables."
                yield f"data: {error_msg}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(config_error_response(), media_type="text/event-stream")
        
        # Get or create session ID
        try:
            session_id = get_or_create_session_id(request.session_id)
            logger.info(f"Session ID: {session_id}")
        except Exception as session_error:
            logger.error(f"Failed to get/create session: {session_error}", exc_info=True)
            async def session_error_response():
                error_msg = f"Failed to initialize session: {str(session_error)[:200]}"
                yield f"data: {error_msg}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(session_error_response(), media_type="text/event-stream")
        
        # Get conversation history for personalization (with error handling)
        conversation_history = []
        try:
            if get_consent(session_id):
                conversation_history = get_conversation_history(session_id)
                logger.debug(f"Loaded {len(conversation_history)} messages from history")
        except Exception as e:
            logger.warning(f"Failed to get conversation history: {e}")
            # Continue without history - non-critical
        
        # Get user profile for personalization (even without consent) - with error handling
        user_profile = None
        try:
            from app.utils.session import get_user_profile
            user_profile = get_user_profile(session_id)
            if user_profile:
                logger.info(f"User profile loaded for session {session_id}")
            else:
                logger.debug(f"No user profile found for session {session_id}")
        except Exception as e:
            logger.warning(f"Failed to get user profile: {e}")
            # Continue without profile - non-critical
        
        # Step 2: Heuristic Check (with error handling)
        heuristic_flag = None
        try:
            heuristic_flag = check_heuristics(message)
        except Exception as e:
            logger.warning(f"Heuristic check failed: {e}")
            # Continue without heuristic flag
        
        # Step 3: Router Model (pass history for personalized routing) - with error handling
        route = "quality"  # Default route
        try:
            route_result = await route_message(message, heuristic_flag, conversation_history)
            route = route_result.get("route", "quality")
            logger.info(f"Router selected route: {route}")
        except Exception as e:
            logger.warning(f"Router failed, defaulting to quality: {e}", exc_info=True)
            route = "quality"  # Default to quality on error
        
        # Step 4: Specialist Model
        if route == "speed":
            # Use speed model
            async def generate_speed():
                try:
                    async for chunk in stream_speed_model_response(message, session_id):
                        yield f"data: {chunk}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    logger.error(f"Error in speed model: {e}", exc_info=True)
                    error_msg = f"I'm sorry, I encountered an error while processing your message. Please try again. (Error: {type(e).__name__})"
                    yield f"data: {error_msg}\n\n"
                    yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate_speed(),
                media_type="text/event-stream",
                headers={
                    "X-Session-ID": session_id,
                    "X-Route": "speed"
                }
            )
        else:
            # Use quality model (Socratic mentor)
            async def generate_quality():
                try:
                    async for chunk in stream_quality_model_response(message, session_id):
                        yield f"data: {chunk}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    logger.error(f"Error in quality model: {e}", exc_info=True)
                    # Provide more helpful error message
                    error_type = type(e).__name__
                    error_str = str(e).lower()
                    if "api" in error_str or "key" in error_str or "authentication" in error_str:
                        error_msg = "I'm sorry, there's an issue with the AI service configuration. Please check that all environment variables are set correctly."
                    elif "timeout" in error_str:
                        error_msg = "I'm sorry, the request timed out. Please try again with a shorter message."
                    elif "rate limit" in error_str or "quota" in error_str:
                        error_msg = "I'm sorry, the service is currently rate-limited. Please try again in a moment."
                    else:
                        error_msg = f"I'm sorry, I encountered an error while processing your message. Please try again. (Error: {error_type})"
                    yield f"data: {error_msg}\n\n"
                    yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate_quality(),
                media_type="text/event-stream",
                headers={
                    "X-Session-ID": session_id,
                    "X-Route": "quality"
                }
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        logger.error(f"Session ID: {session_id}, Message length: {len(message) if message else 0}")
        
        # Return error as SSE with detailed message
        async def error_response():
            error_type = type(e).__name__
            error_msg = f"I'm sorry, I encountered an unexpected error. Please try again. (Error: {error_type})"
            yield f"data: {error_msg}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(error_response(), media_type="text/event-stream")


@router.post("/save")
async def save_message(request: SaveMessageRequest):
    """Save a message to conversation history (used for onboarding messages)."""
    try:
        # Validate request
        if not request.session_id or len(request.session_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="session_id is required")
        
        if request.role not in ["user", "assistant"]:
            raise HTTPException(status_code=400, detail="role must be 'user' or 'assistant'")
        
        if not request.content or len(request.content.strip()) == 0:
            raise HTTPException(status_code=400, detail="content cannot be empty")
        
        session_id = request.session_id.strip()
        logger.info(f"Saving message for session {session_id}, role: {request.role}")
        
        # If this is an onboarding message, ensure consent is set
        if request.is_onboarding:
            try:
                set_consent(session_id, True)
                logger.info(f"Set consent for session {session_id}")
            except Exception as consent_error:
                logger.warning(f"Failed to set consent: {consent_error}")
                # Continue - consent setting is not critical for saving messages
        
        # Save message to history
        try:
            save_message_to_history(session_id, request.role, request.content)
            logger.info(f"Message saved successfully for session {session_id}")
            return {"success": True, "message": "Message saved"}
        except Exception as save_error:
            logger.error(f"Failed to save message: {save_error}", exc_info=True)
            return {
                "success": False,
                "error": str(save_error)[:200],
                "message": "Message may not have been saved"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save message: {str(e)[:200]}"
        )


