import json
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings
from app.services.ai_models import ROUTER_PROMPT


def get_router_model() -> ChatOpenAI:
    """Get the router model."""
    return ChatOpenAI(
        model=settings.router_model,
        temperature=0.1,
        api_key=settings.openai_api_key,
        model_kwargs={"response_format": {"type": "json_object"}}
    )


async def route_message(message: str, heuristic_flag: Optional[str] = None, conversation_history: list = None) -> Dict[str, str]:
    """
    Route a user message to the appropriate model.
    
    Returns:
        {"route": "speed" or "quality", "intent": "simple_question" or "socratic_dialogue" or "complex_assessment"}
    """
    message_lower = message.lower().strip()
    
    # If state_confused, always route to quality
    if heuristic_flag == "state_confused":
        return {"route": "quality", "intent": "socratic_dialogue"}
    
    # FAST PATH: Simple greetings and casual messages → route to speed immediately (no API call)
    simple_greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "thanks", "thank you", "bye", "goodbye"]
    if message_lower in simple_greetings or len(message_lower) < 5:
        return {"route": "speed", "intent": "simple_question"}
    
    # If user has conversation history, use quality for personalized learning
    if conversation_history and len(conversation_history) > 0:
        # For first message after greeting, use quality
        if len(conversation_history) <= 2:
            return {"route": "quality", "intent": "socratic_dialogue"}
        # For ongoing conversations, use quality
        return {"route": "quality", "intent": "socratic_dialogue"}
    
    # For learning-related questions (loops, concepts, how/why questions), always use quality
    learning_keywords = ["loop", "function", "variable", "class", "how", "why", "explain", "understand", "learn", "teach", "what is", "what are", "define", "concept", "work", "does"]
    if any(keyword in message_lower for keyword in learning_keywords):
        return {"route": "quality", "intent": "socratic_dialogue"}
    
    # DEFAULT: Use quality for personalized learning (unless it's a simple factual lookup)
    # Simple factual lookups would be: "What is the capital of France?" or "Who invented X?"
    # But for coding/learning questions, always use quality
    if "what is" in message_lower or "what are" in message_lower or "how" in message_lower:
        return {"route": "quality", "intent": "socratic_dialogue"}
    
    model = get_router_model()
    
    # Build messages with system prompt
    context_note = ""
    if conversation_history and len(conversation_history) > 0:
        context_note = "\n\nNote: This user has an ongoing conversation. For personalized learning, route to 'quality' unless it's a simple factual lookup."
    
    user_prompt = f"""User message: "{message}"
Heuristic flag: {heuristic_flag or "None"}
{context_note}

IMPORTANT ROUTING GUIDELINES:
- Simple factual questions like "What is X?" or "Who invented Y?" → route "speed"
- Learning questions, concept explanations, "How does X work?", "Why...", "Explain..." → route "quality"
- Questions that build on previous conversation → ALWAYS route "quality"
- Any question requiring understanding or teaching → route "quality"

Return ONLY a JSON object with "route" and "intent" keys."""
    
    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=user_prompt)
    ]
    
    try:
        response = await model.ainvoke(messages)
        result = json.loads(response.content)
        
        # Validate response
        if "route" not in result or "intent" not in result:
            raise ValueError("Invalid router response")
        
        # OVERRIDE: Force quality model for all learning/concept questions
        # Only allow "speed" for truly simple factual lookups (like "What is the capital of France?")
        # For programming, coding, learning, or "how/why/what is [concept]" questions → ALWAYS quality
        message_lower = message.lower()
        is_learning_question = any([
            "loop" in message_lower,
            "function" in message_lower,
            "variable" in message_lower,
            "class" in message_lower,
            "how" in message_lower,
            "why" in message_lower,
            "explain" in message_lower,
            "what is" in message_lower,
            "what are" in message_lower,
            "define" in message_lower,
            "concept" in message_lower,
            "learn" in message_lower,
            "teach" in message_lower
        ])
        
        if is_learning_question:
            result["route"] = "quality"
            result["intent"] = "socratic_dialogue"
        
        # If there's conversation history, always use quality for personalization
        if conversation_history and len(conversation_history) > 0:
            result["route"] = "quality"
            result["intent"] = "socratic_dialogue"
        
        return result
    except Exception as e:
        # Default to quality route on error (for personalized learning)
        print(f"Router error: {e}")
        return {"route": "quality", "intent": "socratic_dialogue"}

