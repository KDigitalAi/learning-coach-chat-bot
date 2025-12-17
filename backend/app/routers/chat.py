from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from app.utils.session import get_or_create_session_id, get_consent, save_message_to_history, set_consent
from app.utils.heuristics import check_heuristics
from app.services.router import route_message
from app.services.ai_models import stream_speed_model_response, stream_quality_model_response
from app.utils.session import get_conversation_history
from app.utils.session import save_user_profile


router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


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
    # Validate request
    if not request.message or not request.message.strip():
        async def empty_message_response():
            yield f"data: Please provide a message.\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(empty_message_response(), media_type="text/event-stream")
    
    try:
        # Check environment variables early
        from app.config import settings
        if not settings.openai_api_key:
            async def config_error_response():
                error_msg = "Configuration error: OpenAI API key is missing. Please check your environment variables."
                yield f"data: {error_msg}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(config_error_response(), media_type="text/event-stream")
        
        session_id = get_or_create_session_id(request.session_id)
        
        # Step 1: Triage (message received)
        message = request.message.strip()
        
        # Get conversation history for personalization (with error handling)
        conversation_history = []
        try:
            if get_consent(session_id):
                conversation_history = get_conversation_history(session_id)
        except Exception as e:
            print(f"⚠️ Warning: Failed to get conversation history: {e}")
            # Continue without history - non-critical
        
        # Get user profile for personalization (even without consent) - with error handling
        user_profile = None
        try:
            from app.utils.session import get_user_profile
            user_profile = get_user_profile(session_id)
            
            # Log profile for debugging
            if user_profile:
                print(f"✅ User profile loaded for session {session_id}: {user_profile}")
            else:
                print(f"⚠️ No user profile found for session {session_id} - personalization may be limited")
        except Exception as e:
            print(f"⚠️ Warning: Failed to get user profile: {e}")
            # Continue without profile - non-critical
        
        # Step 2: Heuristic Check (with error handling)
        try:
            heuristic_flag = check_heuristics(message)
        except Exception as e:
            print(f"⚠️ Warning: Heuristic check failed: {e}")
            heuristic_flag = None
        
        # Step 3: Router Model (pass history for personalized routing) - with error handling
        try:
            route_result = await route_message(message, heuristic_flag, conversation_history)
            route = route_result.get("route", "quality")  # Default to quality for personalized learning
        except Exception as e:
            print(f"⚠️ Warning: Router failed, defaulting to quality: {e}")
            import traceback
            traceback.print_exc()
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
                    print(f"❌ Error in speed model: {e}")
                    import traceback
                    traceback.print_exc()
                    error_msg = f"I'm sorry, I encountered an error while processing your message. Please try again. (Error: {str(e)[:100]})"
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
                    print(f"❌ Error in quality model: {e}")
                    import traceback
                    traceback.print_exc()
                    # Provide more helpful error message
                    error_type = type(e).__name__
                    if "API" in error_type or "key" in str(e).lower():
                        error_msg = "I'm sorry, there's an issue with the AI service configuration. Please check that all environment variables are set correctly."
                    elif "timeout" in str(e).lower():
                        error_msg = "I'm sorry, the request timed out. Please try again with a shorter message."
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
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        # Return error as SSE with detailed message
        async def error_response():
            error_type = type(e).__name__
            error_msg = f"I'm sorry, I encountered an error. Please try again. (Error: {error_type})"
            yield f"data: {error_msg}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(error_response(), media_type="text/event-stream")


@router.post("/save")
async def save_message(request: SaveMessageRequest):
    """Save a message to conversation history (used for onboarding messages)."""
    try:
        session_id = request.session_id
        
        # If this is an onboarding message, ensure consent is set
        if request.is_onboarding:
            set_consent(session_id, True)
        
        # Save message to history
        save_message_to_history(session_id, request.role, request.content)
        
        return {"success": True, "message": "Message saved"}
    except Exception as e:
        print(f"Error saving message: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


