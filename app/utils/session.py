"""
Session management utilities using Supabase PostgreSQL.
Replaces Redis with persistent database storage.
"""
import uuid
from typing import Optional, Dict, List
from app.utils.database import get_supabase_client, ensure_session_exists
import logging

logger = logging.getLogger(__name__)


def get_or_create_session_id(session_id: Optional[str] = None) -> str:
    """Get existing session ID or create a new one."""
    if session_id:
        ensure_session_exists(session_id)
        return session_id
    new_session_id = str(uuid.uuid4())
    ensure_session_exists(new_session_id)
    return new_session_id


def get_consent(session_id: str) -> bool:
    """Check if user has consented."""
    try:
        client = get_supabase_client()
        result = client.table("user_sessions").select("has_consent").eq("session_id", session_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0].get("has_consent", False)
        return False
    except Exception as e:
        logger.error(f"Error getting consent for session {session_id}: {e}")
        return False


def set_consent(session_id: str, consent: bool) -> None:
    """Set user consent."""
    try:
        client = get_supabase_client()
        # Ensure session exists first
        ensure_session_exists(session_id)
        
        # UPSERT: Update if exists, insert if not
        client.table("user_sessions").upsert({
            "session_id": session_id,
            "has_consent": consent
        }).execute()
        logger.debug(f"Updated consent for session {session_id}: {consent}")
    except Exception as e:
        logger.error(f"Error setting consent for session {session_id}: {e}")
        raise


def save_user_profile(session_id: str, profile_data: dict) -> None:
    """Save user onboarding/profile data to Supabase and vector store."""
    try:
        client = get_supabase_client()
        # Ensure session exists first
        ensure_session_exists(session_id)
        
        # Extract individual fields from profile_data
        profile_record = {
            "session_id": session_id,
            "learning_level": profile_data.get("learningLevel"),
            "interests": profile_data.get("interests"),
            "goals": profile_data.get("goals"),
            "preferred_style": profile_data.get("preferredStyle"),
            "profile_data": profile_data  # Store full data as JSONB
        }
        
        # UPSERT profile in Supabase
        client.table("user_profiles").upsert(profile_record).execute()
        logger.debug(f"Saved profile for session {session_id}")
        
        # ALSO store as vector in ChromaDB
        try:
            from app.services.vector_store import store_learning_style_vector
            store_learning_style_vector(session_id, profile_data)
            logger.debug(f"Stored learning style vector for session {session_id}")
        except Exception as e:
            logger.warning(f"Failed to store vector for session {session_id}: {e}")
            # Don't raise - vector storage is optional enhancement
            
    except Exception as e:
        logger.error(f"Error saving profile for session {session_id}: {e}")
        raise


def get_user_profile(session_id: str) -> dict:
    """Get user profile data from Supabase."""
    try:
        client = get_supabase_client()
        result = client.table("user_profiles").select("*").eq("session_id", session_id).execute()
        
        if result.data and len(result.data) > 0:
            profile = result.data[0]
            # Return in the format expected by the rest of the code
            # Use profile_data JSONB if available, otherwise construct from fields
            if profile.get("profile_data"):
                return profile["profile_data"]
            else:
                # Fallback: construct from individual fields
                return {
                    "learningLevel": profile.get("learning_level"),
                    "interests": profile.get("interests"),
                    "goals": profile.get("goals"),
                    "preferredStyle": profile.get("preferred_style")
                }
        return {}
    except Exception as e:
        logger.error(f"Error getting profile for session {session_id}: {e}")
        return {}


def get_conversation_history(session_id: str, limit: Optional[int] = None) -> List[Dict]:
    """Get conversation history from Supabase."""
    if not get_consent(session_id):
        return []
    
    try:
        client = get_supabase_client()
        query = client.table("conversation_history").select("*").eq("session_id", session_id).order("created_at", desc=False)
        
        if limit:
            query = query.limit(limit)
        
        result = query.execute()
        
        history = []
        for msg in result.data:
            history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return history
    except Exception as e:
        logger.error(f"Error getting conversation history for session {session_id}: {e}")
        return []


def save_message_to_history(session_id: str, role: str, content: str) -> None:
    """Save a message to conversation history in Supabase."""
    if not get_consent(session_id):
        return
    
    try:
        client = get_supabase_client()
        # Ensure session exists first
        ensure_session_exists(session_id)
        
        client.table("conversation_history").insert({
            "session_id": session_id,
            "role": role,
            "content": content
        }).execute()
        logger.debug(f"Saved {role} message to history for session {session_id}")
    except Exception as e:
        logger.error(f"Error saving message to history for session {session_id}: {e}")
        # Don't raise - history saving is non-critical
