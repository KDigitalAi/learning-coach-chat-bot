"""
Extract onboarding data from conversation history.
When onboarding questions are asked in chat, extract answers from history.
"""
from typing import Dict, List, Optional


def extract_onboarding_from_history(history: List[Dict]) -> Optional[Dict]:
    """
    Extract onboarding data from conversation history.

    Looks for patterns in the conversation history to extract:
    - Learning level (from answer to "What's your current learning level?")
    - Interests (from answer to "What topics are you interested in learning?")
    - Goals (from answer to "What are your learning goals?")
    - Preferred style (from answer to "How do you prefer to learn?")
    - Consent (from answer to consent question)
    
    Args:
        history: List of messages with 'role' and 'content'
    
    Returns:
        Dict with onboarding data or None if not found
    """
    if not history or len(history) < 10:  # Need at least 10 messages (5 Q&A pairs)
        return None
    
    onboarding_data = {
        'learningLevel': '',
        'interests': '',
        'goals': '',
        'preferredStyle': '',
        'consent': False
    }
    
    # Look for onboarding question patterns and extract answers
    for i, msg in enumerate(history):
        content = msg.get('content', '').lower()
        role = msg.get('role', '')
        
        # Check if this is an onboarding question
        if role == 'assistant':
            if 'learning level' in content or 'current learning level' in content:
                # Next user message should be the answer
                if i + 1 < len(history) and history[i + 1].get('role') == 'user':
                    answer = history[i + 1].get('content', '').strip()
                    if answer in ['Beginner', 'Intermediate', 'Advanced']:
                        onboarding_data['learningLevel'] = answer
            elif 'topics are you interested' in content or 'interests' in content:
                if i + 1 < len(history) and history[i + 1].get('role') == 'user':
                    onboarding_data['interests'] = history[i + 1].get('content', '').strip()
            elif 'learning goals' in content or 'hope to achieve' in content:
                if i + 1 < len(history) and history[i + 1].get('role') == 'user':
                    onboarding_data['goals'] = history[i + 1].get('content', '').strip()
            elif 'prefer to learn' in content or 'learning style' in content:
                if i + 1 < len(history) and history[i + 1].get('role') == 'user':
                    answer = history[i + 1].get('content', '').strip().lower()
                    # Extract style from answer
                    if 'visual' in answer or '🎨' in history[i + 1].get('content', ''):
                        onboarding_data['preferredStyle'] = 'visual'
                    elif 'hands-on' in answer or '✋' in history[i + 1].get('content', ''):
                        onboarding_data['preferredStyle'] = 'hands-on'
                    elif 'theoretical' in answer or '📚' in history[i + 1].get('content', ''):
                        onboarding_data['preferredStyle'] = 'theoretical'
                    elif 'mixed' in answer or '🔄' in history[i + 1].get('content', ''):
                        onboarding_data['preferredStyle'] = 'mixed'
            elif 'remember our conversation' in content or 'consent' in content:
                if i + 1 < len(history) and history[i + 1].get('role') == 'user':
                    answer = history[i + 1].get('content', '').strip().lower()
                    onboarding_data['consent'] = 'yes' in answer or 'ok' in answer or 'okay' in answer or 'true' in answer
    
    # Check if we have enough data
    if onboarding_data['learningLevel'] and onboarding_data['preferredStyle']:
        return onboarding_data
    
    return None


def extract_onboarding_from_recent_messages(messages: List[Dict]) -> Optional[Dict]:
    """
    Extract onboarding data from recent messages (last 20 messages).
    More efficient for checking recent onboarding.
    """
    return extract_onboarding_from_history(messages[-20:] if len(messages) > 20 else messages)


