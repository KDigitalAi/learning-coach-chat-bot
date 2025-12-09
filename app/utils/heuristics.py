from typing import Optional


def check_heuristics(message: str) -> Optional[str]:
    """
    Check user message for heuristic indicators of confusion or confidence.

    Returns:
        "state_confused" if message indicates confusion
        "state_confident" if message indicates confidence
        None otherwise
    """
    message_lower = message.lower()

    # Confusion indicators
    confused_patterns = [
        "???",
        "i don't get it",
        "don't get it",
        "confusing",
        "confused",
        "don't understand",
        "doesn't make sense",
        "i give up",
        "this is hard",
        "stuck",
        "help",
        "what?",
        "huh?"
    ]

    # Confidence indicators
    confident_patterns = [
        "got it",
        "understand",
        "easy",
        "next",
        "clear",
        "makes sense",
        "i see",
        "okay",
        "ok",
        "perfect",
        "thanks"
    ]

    # Check for confusion first
    for pattern in confused_patterns:
        if pattern in message_lower:
            return "state_confused"

    # Check for confidence
    for pattern in confident_patterns:
        if pattern in message_lower:
            return "state_confident"

    return None


