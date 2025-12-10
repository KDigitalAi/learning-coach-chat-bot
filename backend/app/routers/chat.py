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
    try:
        session_id = get_or_create_session_id(request.session_id)
        
        # Step 1: Triage (message received)
        message = request.message
        
        # Get conversation history for personalization
        conversation_history = []
        if get_consent(session_id):
            conversation_history = get_conversation_history(session_id)
        
        # Get user profile for personalization (even without consent)
        from app.utils.session import get_user_profile
        user_profile = get_user_profile(session_id)
        
        # Log profile for debugging
        if user_profile:
            print(f"✅ User profile loaded for session {session_id}: {user_profile}")
        else:
            print(f"⚠️ No user profile found for session {session_id} - personalization may be limited")
        
        # Step 2: Heuristic Check
        heuristic_flag = check_heuristics(message)
        
        # Step 3: Router Model (pass history for personalized routing)
        route_result = await route_message(message, heuristic_flag, conversation_history)
        route = route_result.get("route", "quality")  # Default to quality for personalized learning
        
        # Step 4: Specialist Model
        if route == "speed":
            # Use speed model
            async def generate_speed():
                try:
                    async for chunk in stream_speed_model_response(message, session_id):
                        yield f"data: {chunk}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    print(f"Error in speed model: {e}")
                    import traceback
                    traceback.print_exc()
                    yield f"data: I'm sorry, I encountered an error. Please try again.\n\n"
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
                    print(f"Error in quality model: {e}")
                    import traceback
                    traceback.print_exc()
                    yield f"data: I'm sorry, I encountered an error. Please try again.\n\n"
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
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        # Return error as SSE
        async def error_response():
            yield f"data: I'm sorry, I encountered an error. Please try again.\n\n"
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


