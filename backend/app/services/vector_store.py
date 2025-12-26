"""
Vector storage service for learning styles and onboarding data.
Uses Supabase PostgreSQL with pgvector extension for vector embeddings.
"""
from typing import Dict, List, Optional
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    logger.error("OpenAI package not found. Vector store will be disabled.")

from app.config import settings
from app.utils.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client for embeddings (lazy initialization)
_openai_client: Optional[OpenAI] = None


def get_openai_client() -> Optional[OpenAI]:
    """Get or create OpenAI client instance."""
    global _openai_client
    if OpenAI is None:
        return None
        
    if _openai_client is None:
        try:
            _openai_client = OpenAI(api_key=settings.openai_api_key)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return None
    return _openai_client


def get_embeddings(text: str) -> List[float]:
    """Generate embeddings for text using OpenAI."""
    try:
        client = get_openai_client()
        if not client:
            logger.warning("OpenAI client not available for embeddings")
            return []
            
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return []


def store_learning_style_vector(session_id: str, onboarding_data: Dict) -> bool:
    """
    Store onboarding data as vectors in Supabase PostgreSQL with pgvector.

    Args:
        session_id: Unique session identifier
        onboarding_data: Dictionary with learningLevel, interests, goals,
            preferredStyle

    Returns:
        bool: True if successful
    """
    try:
        client = get_supabase_client()

        # Create a comprehensive text representation of learning style
        learning_level = onboarding_data.get("learningLevel", "Unknown")
        interests = onboarding_data.get("interests", "")
        goals = onboarding_data.get("goals", "")
        preferred_style = onboarding_data.get("preferredStyle", "mixed")

        # Create rich text representation for embedding
        style_text = f"""
        Learning Level: {learning_level}
        Interests: {interests}
        Goals: {goals}
        Preferred Learning Style: {preferred_style}

        Teaching Instructions:
        - If visual: Use visual descriptions, diagrams, examples, code """
        style_text += """snippets. Say 'Imagine this visually...', 'Picture this...'
        - If hands-on: Provide practice exercises, encourage trying things. """
        style_text += """Say 'Try this yourself...', 'Let's practice...'
        - If theoretical: Explain concepts and principles first. """
        style_text += """Say 'The principle behind this is...', 'Conceptually...'
        - If mixed: Combine visual examples, hands-on practice, and theory
        - Match complexity to {learning_level} level
        - Reference interests: {interests}
        - Align with goals: {goals}
        """

        # Generate embedding
        embedding = get_embeddings(style_text)

        if not embedding:
            logger.warning(
                f"Failed to generate embedding for session {session_id}"
            )
            return False

        # Store in Supabase with pgvector
        # Note: Supabase handles vector storage via pgvector extension
        # UPSERT using Supabase RPC or direct SQL
        # Since Supabase client doesn't directly support vector types, use RPC
        try:
            # Delete existing if present
            client.table("learning_style_vectors").delete().eq(
                "session_id", session_id
            ).execute()

            # Insert new record
            # Note: We need to use raw SQL for vector insertion via Supabase RPC
            # For now, store as JSONB and use Supabase's vector RPC function
            client.rpc(
                "store_learning_style_vector",
                {
                    "p_session_id": session_id,
                    "p_learning_level": learning_level,
                    "p_interests": interests,
                    "p_goals": goals,
                    "p_preferred_style": preferred_style,
                    "p_style_text": style_text,
                    "p_embedding": embedding,
                    "p_onboarding_data": onboarding_data
                }
            ).execute()

            logger.info(f"Stored learning style vector for session {session_id}")
            return True

        except Exception as rpc_error:
            # Fallback: Store without vector (metadata only)
            logger.warning(f"RPC function not available, storing metadata only: {rpc_error}")
            # Store as JSONB in regular table as fallback
            client.table("learning_style_vectors").upsert({
                "session_id": session_id,
                "learning_level": learning_level,
                "interests": interests,
                "goals": goals,
                "preferred_style": preferred_style,
                "style_text": style_text,
                "onboarding_data": onboarding_data
            }).execute()
            return True

    except Exception as e:
        logger.error(f"Error storing learning style vector: {e}")
        import traceback
        traceback.print_exc()
        return False


def retrieve_learning_style_vector(session_id: str) -> Optional[Dict]:
    """
    Retrieve learning style vector and metadata for a session.

    Args:
        session_id: Unique session identifier

    Returns:
        Dict with learning style data and instructions, or None if not found
    """
    try:
        client = get_supabase_client()

        # Query by session_id
        result = (
            client.table("learning_style_vectors")
            .select("*")
            .eq("session_id", session_id)
            .execute()
        )

        if result.data and len(result.data) > 0:
            data = result.data[0]

            return {
                "session_id": session_id,
                "learning_level": data.get("learning_level"),
                "interests": data.get("interests"),
                "goals": data.get("goals"),
                "preferred_style": data.get("preferred_style"),
                "style_text": data.get("style_text"),
                "onboarding_data": data.get("onboarding_data") or {}
            }

        return None

    except Exception as e:
        logger.error(f"Error retrieving learning style vector: {e}")
        return None


def search_similar_learning_styles(query_text: str, limit: int = 3) -> List[Dict]:
    """
    Search for similar learning styles using vector similarity search.

    Args:
        query_text: Text to search for (e.g., "visual learner beginner Python")
        limit: Number of results to return

    Returns:
        List of similar learning style records
    """
    try:
        client = get_supabase_client()

        # Generate query embedding
        query_embedding = get_embeddings(query_text)

        if not query_embedding:
            return []

        # Use Supabase RPC for vector similarity search
        try:
            result = client.rpc(
                "search_similar_learning_styles",
                {
                    "p_query_embedding": query_embedding,
                    "p_limit": limit
                }
            ).execute()

            if result.data:
                return result.data
        except Exception as rpc_error:
            logger.warning(f"Vector search RPC not available: {rpc_error}")
            # Fallback: Simple text search
            result = (
                client.table("learning_style_vectors")
                .select("*")
                .limit(limit)
                .execute()
            )
            if result.data:
                return result.data

        return []

    except Exception as e:
        logger.error(f"Error searching learning styles: {e}")
        return []


def get_learning_style_instructions(session_id: str) -> str:
    """
    Get formatted learning style instructions for AI prompt.

    Args:
        session_id: Unique session identifier

    Returns:
        Formatted string with learning style instructions
    """
    style_data = retrieve_learning_style_vector(session_id)

    if not style_data:
        return ""

    instructions = "\n\n**LEARNING STYLE FROM VECTOR STORAGE (CRITICAL):**\n"
    level = style_data.get('learning_level', 'Unknown')
    instructions += f"- Learning Level: {level}\n"
    interests = style_data.get('interests', 'None')
    instructions += f"- Interests: {interests}\n"
    goals = style_data.get('goals', 'None')
    instructions += f"- Goals: {goals}\n"
    preferred = style_data.get('preferred_style', 'mixed')
    instructions += f"- Preferred Style: {preferred}\n"
    instructions += "\n**MANDATORY TEACHING STYLE (based on vector storage):**\n"

    preferred_style = style_data.get('preferred_style', 'mixed')

    if preferred_style == 'visual':
        instructions += "- MUST use visual descriptions, diagrams, examples, code snippets\n"
        instructions += "- MUST say: 'Imagine this visually...', 'Picture this...', 'Here's an example...'\n"
        instructions += "- MUST include visual analogies in every response\n"
    elif preferred_style == 'hands-on':
        instructions += "- MUST provide practice exercises, encourage trying things\n"
        instructions += "- MUST say: 'Try this yourself...', 'Let's practice...', 'Now you try...'\n"
        instructions += "- MUST include actionable steps in every response\n"
    elif preferred_style == 'theoretical':
        instructions += "- MUST explain concepts and principles first, then examples\n"
        instructions += "- MUST say: 'The principle behind this is...', 'Conceptually...', 'The theory is...'\n"
        instructions += "- MUST start with theory before practical examples\n"
    elif preferred_style == 'mixed':
        instructions += (
            "- MUST combine visual examples, hands-on practice, and theory\n"
        )
        instructions += (
            "- MUST alternate between explanations, examples, and practice "
            "suggestions\n"
        )

    level = style_data.get('learning_level', 'Intermediate')
    instructions += f"- MUST match complexity to {level} level\n"
    interests = style_data.get('interests', 'None')
    instructions += f"- MUST reference their interests: {interests}\n"
    goals = style_data.get('goals', 'None')
    instructions += f"- MUST align with their goals: {goals}\n"
    instructions += (
        "\n**CRITICAL:** Your response MUST follow the above learning style. "
        "This is not optional.\n"
    )

    return instructions
