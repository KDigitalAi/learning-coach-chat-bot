"""
Supabase database client and helper functions.
Replaces Redis with Supabase PostgreSQL for persistent storage.
"""
from supabase import create_client, Client
from app.config import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase client
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        try:
            # Access settings with error handling
            try:
                supabase_url = settings.supabase_url
                supabase_key = settings.supabase_key
            except Exception as settings_error:
                logger.error(f"Failed to get settings: {settings_error}")
                raise ValueError(
                    f"Configuration error: {str(settings_error)}. "
                    "Please check your environment variables (SUPABASE_URL, SUPABASE_KEY)."
                ) from settings_error
            
            if not supabase_url or not supabase_key:
                raise ValueError(
                    "Supabase configuration missing. Please set SUPABASE_URL and SUPABASE_KEY environment variables."
                )
            
            _supabase_client = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    return _supabase_client


def ensure_session_exists(session_id: str) -> None:
    """Create session record if it doesn't exist."""
    try:
        client = get_supabase_client()
    except Exception as client_error:
        logger.error(f"Cannot ensure session exists - Supabase client unavailable: {client_error}")
        # Don't raise - allow the app to continue without database
        # The session will be created when database is available
        return
    
    try:
        # Try to get existing session
        result = (
            client.table("user_sessions")
            .select("session_id")
            .eq("session_id", session_id)
            .execute()
        )

        # If session doesn't exist, create it
        if not result.data:
            client.table("user_sessions").insert({
                "session_id": session_id,
                "has_consent": False
            }).execute()
            logger.debug(f"Created new session: {session_id}")
    except Exception as e:
        logger.error(f"Error ensuring session exists: {e}")
        # Don't raise - non-critical operation
        # The app can continue without creating the session record


def execute_query(query: str, params: Optional[Dict] = None) -> Any:
    """Execute a raw SQL query (if needed for complex operations)."""
    # Note: Supabase Python client doesn't support raw SQL directly
    # Use Supabase client methods instead
    raise NotImplementedError(
        "Use Supabase client methods instead of raw SQL"
    )
