"""
Learning pattern analysis and storage.
Analyzes user conversations to extract learning patterns and stores them in Supabase.
"""
from typing import List, Dict
from app.utils.database import get_supabase_client, ensure_session_exists
from app.utils.session import get_conversation_history
import logging

logger = logging.getLogger(__name__)


def extract_topics_from_conversation(conversation_history: List[Dict]) -> List[str]:
    """Extract topics discussed from conversation history."""
    topics = []

    # Simple keyword-based extraction (can be enhanced with NLP)
    topic_keywords = {
        "programming": ["code", "programming", "function", "variable", "loop", "class", "python", "javascript", "java"],
        "algorithms": ["algorithm", "sort", "search", "data structure", "array", "list", "tree"],
        "web development": ["html", "css", "react", "vue", "frontend", "backend", "api", "http"],
        "machine learning": ["machine learning", "ai", "neural network", "model", "training", "data science"],
        "mathematics": ["math", "calculus", "algebra", "equation", "formula", "derivative"],
        "science": ["physics", "chemistry", "biology", "photosynthesis", "atom", "molecule"]
    }

    all_text = " ".join([msg.get("content", "").lower() for msg in conversation_history])

    for topic, keywords in topic_keywords.items():
        if any(keyword in all_text for keyword in keywords):
            if topic not in topics:
                topics.append(topic)

    return topics


def analyze_learning_pace(conversation_history: List[Dict]) -> str:
    """Analyze user's learning pace based on conversation patterns."""
    if not conversation_history:
        return "medium"

    user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]

    if len(user_messages) < 3:
        return "medium"

    # Analyze question patterns
    question_count = sum(1 for msg in user_messages if "?" in msg.get("content", ""))
    question_ratio = question_count / len(user_messages)

    # Analyze response length (shorter might indicate faster understanding)
    total_length = sum(len(msg.get("content", "")) for msg in user_messages)
    avg_response_length = total_length / len(user_messages)

    # Determine pace
    if question_ratio > 0.7 or avg_response_length < 50:
        return "fast"  # Many questions or short responses = fast learner
    elif question_ratio < 0.3 and avg_response_length > 200:
        return "slow"  # Few questions and long responses = slower learner
    else:
        return "medium"


def identify_strengths(conversation_history: List[Dict]) -> List[str]:
    """Identify topics user understands quickly (strengths)."""
    strengths = []

    # Look for patterns where user provides correct answers or shows understanding
    user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]

    confidence_indicators = [
        "got it", "understand", "clear", "makes sense", "i see", "that's", "yes"
    ]

    for msg in user_messages:
        content_lower = msg.get("content", "").lower()
        if any(indicator in content_lower for indicator in confidence_indicators):
            # Extract topic from context (simplified)
            topics = extract_topics_from_conversation([msg])
            strengths.extend(topics)

    # Remove duplicates
    return list(set(strengths))


def identify_struggles(conversation_history: List[Dict]) -> List[str]:
    """Identify topics user struggles with (asks about repeatedly)."""
    struggles = []

    user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]

    confusion_indicators = [
        "confused", "don't understand", "not clear", "help", "explain", "??", "stuck"
    ]

    # Count topics mentioned with confusion
    topic_confusion_count = {}

    for msg in user_messages:
        content_lower = msg.get("content", "").lower()
        if any(indicator in content_lower for indicator in confusion_indicators):
            topics = extract_topics_from_conversation([msg])
            for topic in topics:
                topic_confusion_count[topic] = topic_confusion_count.get(topic, 0) + 1

    # Topics mentioned with confusion 2+ times are struggles
    struggles = [
        topic for topic, count in topic_confusion_count.items() if count >= 2
    ]

    return struggles


def analyze_learning_patterns(session_id: str) -> Dict:
    """Analyze conversation history and extract learning patterns."""
    try:
        # Get recent conversation history (limit to last 20 messages)
        history = get_conversation_history(session_id, limit=20)

        if not history or len(history) < 2:
            return {}

        patterns = {
            "topics_learned": extract_topics_from_conversation(history),
            "learning_pace": analyze_learning_pace(history),
            "strengths": identify_strengths(history),
            "struggles": identify_struggles(history),
            "interaction_count": len([
                msg for msg in history if msg.get("role") == "user"
            ])
        }

        return patterns
    except Exception as e:
        logger.error(
            f"Error analyzing learning patterns for session {session_id}: {e}"
        )
        return {}


def save_learning_patterns(session_id: str, patterns: Dict) -> None:
    """Save or update learning patterns in Supabase."""
    try:
        client = get_supabase_client()
        ensure_session_exists(session_id)

        # Get existing patterns if any
        existing = (
            client.table("learning_patterns")
            .select("*")
            .eq("session_id", session_id)
            .execute()
        )

        if existing.data and len(existing.data) > 0:
            # Update existing patterns
            existing_patterns = existing.data[0]

            # Merge topics (avoid duplicates)
            existing_topics = existing_patterns.get("topics_learned", []) or []
            new_topics = patterns.get("topics_learned", [])
            merged_topics = list(set(existing_topics + new_topics))

            # Merge strengths
            existing_strengths = existing_patterns.get("strengths", []) or []
            new_strengths = patterns.get("strengths", [])
            merged_strengths = list(set(existing_strengths + new_strengths))

            # Merge struggles
            existing_struggles = existing_patterns.get("struggles", []) or []
            new_struggles = patterns.get("struggles", [])
            merged_struggles = list(set(existing_struggles + new_struggles))

            # Update interaction count
            existing_count = existing_patterns.get("interaction_count", 0)
            new_count = patterns.get("interaction_count", 0)
            interaction_count = existing_count + new_count

            # Update patterns
            client.table("learning_patterns").update({
                "topics_learned": merged_topics,
                "learning_pace": (
                    patterns.get("learning_pace") or
                    existing_patterns.get("learning_pace")
                ),
                "strengths": merged_strengths,
                "struggles": merged_struggles,
                "interaction_count": interaction_count
            }).eq("session_id", session_id).execute()
        else:
            # Insert new patterns
            client.table("learning_patterns").insert({
                "session_id": session_id,
                "topics_learned": patterns.get("topics_learned", []),
                "learning_pace": patterns.get("learning_pace", "medium"),
                "strengths": patterns.get("strengths", []),
                "struggles": patterns.get("struggles", []),
                "interaction_count": patterns.get("interaction_count", 0)
            }).execute()

        logger.debug(f"Saved learning patterns for session {session_id}")
    except Exception as e:
        logger.error(
            f"Error saving learning patterns for session {session_id}: {e}"
        )
        # Don't raise - pattern saving is non-critical


def get_learning_patterns(session_id: str) -> Dict:
    """Get learning patterns for a session."""
    try:
        client = get_supabase_client()
        result = (
            client.table("learning_patterns")
            .select("*")
            .eq("session_id", session_id)
            .execute()
        )

        if result.data and len(result.data) > 0:
            patterns = result.data[0]
            return {
                "topics_learned": patterns.get("topics_learned") or [],
                "learning_pace": patterns.get("learning_pace", "medium"),
                "strengths": patterns.get("strengths") or [],
                "struggles": patterns.get("struggles") or [],
                "interaction_count": patterns.get("interaction_count", 0)
            }
        return {}
    except Exception as e:
        logger.error(
            f"Error getting learning patterns for session {session_id}: {e}"
        )
        return {}
