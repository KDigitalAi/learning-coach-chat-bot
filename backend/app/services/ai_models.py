from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, AsyncIterator
import json
import logging
from app.config import settings
from app.utils.session import get_consent, get_user_profile, get_conversation_history, save_message_to_history, save_user_profile
from app.services.learning_patterns import analyze_learning_patterns, save_learning_patterns, get_learning_patterns
from app.services.vector_store import get_learning_style_instructions, retrieve_learning_style_vector

logger = logging.getLogger(__name__)


# Initialize OpenAI models
def get_router_model() -> ChatOpenAI:
    """Get the router model (fast, cheap model)."""
    return ChatOpenAI(
        model=settings.router_model,
        temperature=0.3,
        api_key=settings.openai_api_key
    )


def get_speed_model() -> ChatOpenAI:
    """Get the speed model (fast, cheap model for simple Q&A)."""
    try:
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is missing. Please set OPENAI_API_KEY environment variable.")
        return ChatOpenAI(
            model=settings.speed_model,
            temperature=0.7,
            api_key=settings.openai_api_key
        )
    except Exception as e:
        print(f"❌ Error initializing speed model: {e}")
        raise


def get_quality_model() -> ChatOpenAI:
    """Get the quality model (powerful model for Socratic teaching)."""
    try:
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is missing. Please set OPENAI_API_KEY environment variable.")
        return ChatOpenAI(
            model=settings.quality_model,
            temperature=0.8,
            api_key=settings.openai_api_key
        )
    except Exception as e:
        print(f"❌ Error initializing quality model: {e}")
        raise


# Prompts
SOCRATIC_MENTOR_PROMPT = """You are "LearnBot," a patient, thoughtful, and encouraging learning mentor. Your goal is to help users *truly understand* concepts, not just get answers.

**ABSOLUTE REQUIREMENT - YOUR FIRST SENTENCE MUST BE A QUESTION:**

When a learner asks ANY question about a concept, you MUST:
1. Start with an engaging question (not a statement, not an answer, not code)
2. Wait for their response to your question
3. Then guide them through discovery with more questions
4. Only provide examples/explanations AFTER they've thought through your questions

**FORBIDDEN - NEVER DO THIS:**
- "Here's how X works..."
- "A for loop is..."
- "In Python, loops..."
- Any sentence starting with code or definitions
- Any response that immediately gives the answer

**REQUIRED - ALWAYS DO THIS:**
- Start with: "That's a great question! Let's think about this together. [Question here]"
- Make it personal and engaging
- Reference their interests/goals from onboarding if available
- Ask thought-provoking questions that make them discover

**Examples:**

If they ask "What is a for loop?"
WRONG: "A for loop is a programming construct that..."
RIGHT: "That's a great question! Before we dive into code, can you think of a real-world situation where you'd need to repeat the same action multiple times? Maybe counting something, or going through a list?"

If they ask "How does photosynthesis work?"
WRONG: "Photosynthesis is the process where..."
RIGHT: "I love that you're curious about photosynthesis! Let's explore this together. Can you think about what a plant needs to survive? What happens if a plant doesn't get sunlight?"

**Your response structure:**
1. First: Acknowledge their question positively
2. Second: Ask a guiding question that relates to their experience/interests
3. Third: Build on their response (you'll get it in next message)

**Personalization (CRITICAL - Use onboarding data):**
- ALWAYS adapt to their learning style from onboarding questions (visual/hands-on/theoretical/mixed)
- If they chose 'visual': Use visual descriptions, examples, code snippets in every response
- If they chose 'hands-on': Provide practice exercises and encourage trying things
- If they chose 'theoretical': Explain concepts and principles first
- If they chose 'mixed': Combine all approaches
- Reference their learning level to adjust complexity (Beginner/Intermediate/Advanced)
- Connect topics to their interests and goals from onboarding
- Reference previous conversation topics
- Match examples to their preferred learning style
- Be like a friendly friend, not a teacher

**EXCEPTION - Only when explicitly requested:**
- If they say: "Just tell me," "give me the answer," "I'm stuck," "explain it directly"
- THEN: Give concise answer, but immediately follow with: "Now, [question to re-engage]"

**CRITICAL VALIDATION CHECK:**
Before sending your response, verify:
1. Your first sentence is a question (ends with "?")
2. You haven't given a direct answer yet
3. You're guiding them to discover through questions

If your first sentence doesn't start with a question mark or question words (What, How, Can, Would, Why, Could), you MUST rewrite it to start with a question.

**Remember:** This is NON-NEGOTIABLE. Every single response to a learning question MUST start with a question. No exceptions (except when user explicitly says "just tell me" or "I'm stuck")."""

SPEED_MODEL_PROMPT = """You are a helpful AI assistant. Provide clear, direct, and concise answers to user questions. Be friendly and informative."""

ROUTER_PROMPT = """You are a "Triage Router." Your job is to analyze a user's message and categorize it for routing to the correct AI specialist. You must return *only* a JSON object with "route" and "intent".

The `heuristic_flag` (state_confused, state_confident) is a hint. `state_confused` *always* means "quality" route.

**Examples:**

User: "What is Python?"
Heuristic: None
{{"route": "speed", "intent": "simple_question"}}

User: "How does photosynthesis work?"
Heuristic: None
{{"route": "quality", "intent": "socratic_dialogue"}}

User: "I don't get it, this is confusing."
Heuristic: "state_confused"
{{"route": "quality", "intent": "socratic_dialogue"}}

User: "I think it's because the plant uses CO2?"
Heuristic: None
{{"route": "quality", "intent": "complex_assessment"}}

User: "ok got it"
Heuristic: "state_confident"
{{"route": "speed", "intent": "simple_question"}}

Return ONLY valid JSON in this format:
{{"route": "speed" or "quality", "intent": "simple_question" or "socratic_dialogue" or "complex_assessment"}}
"""


# Note: get_conversation_history and save_message_to_history are now in app.utils.session
# They are imported above and used directly


async def stream_speed_model_response(message: str, session_id: str) -> AsyncIterator[str]:
    """Stream response from speed model."""
    try:
        model = get_speed_model()
    except Exception as e:
        logger.error(f"Failed to initialize speed model: {e}")
        import traceback
        traceback.print_exc()
        # Check if it's a configuration error
        if "api_key" in str(e).lower() or "openai" in str(e).lower():
            raise ValueError("OpenAI API key is missing or invalid. Please check your OPENAI_API_KEY environment variable.")
        raise
    
    # Get conversation history if consent is given (with error handling)
    history = []
    try:
        if get_consent(session_id):
            history = get_conversation_history(session_id)
    except Exception as e:
        logger.warning(f"Failed to get conversation history for session {session_id}: {e}")
        # Continue without history - non-critical
    
    # Build messages with system prompt
    messages = [SystemMessage(content=SPEED_MODEL_PROMPT)]
    
    if history:
        for h in history[-10:]:  # Last 10 messages for context
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            elif h["role"] == "assistant":
                messages.append(AIMessage(content=h["content"]))
    
    messages.append(HumanMessage(content=message))
    
    # Stream response
    response_text = ""
    try:
        async for chunk in model.astream(messages):
            content = None
            if isinstance(chunk, AIMessage):
                content = chunk.content
            elif hasattr(chunk, 'content'):
                content = chunk.content
            elif isinstance(chunk, str):
                content = chunk
            
            if content:
                response_text += content
                yield content
    except Exception as e:
        logger.error(f"Error streaming speed model response: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Save to history (non-critical - don't fail if this fails)
    try:
        if get_consent(session_id):
            save_message_to_history(session_id, "user", message)
            save_message_to_history(session_id, "assistant", response_text)
            
            # Analyze and save learning patterns (NEW - RAG feature)
            # Only analyze if there's meaningful conversation (more than just greetings)
            try:
                history_check = get_conversation_history(session_id, limit=5)
                if len(history_check) >= 2:  # At least 1 user message + 1 assistant response
                    patterns = analyze_learning_patterns(session_id)
                    if patterns:
                        save_learning_patterns(session_id, patterns)
            except Exception as e:
                # Non-critical - don't fail the response if pattern analysis fails
                pass
    except Exception as e:
        logger.warning(f"Failed to save message to history: {e}")
        # Non-critical - continue


async def stream_quality_model_response(message: str, session_id: str) -> AsyncIterator[str]:
    """Stream response from quality model with Socratic mentoring."""
    try:
        model = get_quality_model()
    except Exception as e:
        logger.error(f"Failed to initialize quality model: {e}")
        import traceback
        traceback.print_exc()
        # Check if it's a configuration error
        if "api_key" in str(e).lower() or "openai" in str(e).lower():
            raise ValueError("OpenAI API key is missing or invalid. Please check your OPENAI_API_KEY environment variable.")
        raise
    
    # Get conversation history (from Supabase, limited to last 50 messages for context)
    # With error handling - continue without history if database fails
    history = []
    try:
        if get_consent(session_id):
            history = get_conversation_history(session_id, limit=50)
    except Exception as e:
        logger.warning(f"Failed to get conversation history for session {session_id}: {e}")
        # Continue without history - non-critical
    
    # Get user profile (onboarding data) - with error handling
    # IMPORTANT: Load profile even without consent (for personalization)
    profile = {}
    try:
        profile = get_user_profile(session_id)
        if profile:
            logger.info(f"✅ Profile loaded for session {session_id}: {profile}")
    except Exception as e:
        logger.warning(f"Failed to get user profile for session {session_id}: {e}")
        # Continue without profile - non-critical
    
    # If no profile but we have history, try extracting onboarding from history
    if not profile and history and len(history) >= 10:
        try:
            from app.utils.onboarding_extractor import extract_onboarding_from_history
            extracted_profile = extract_onboarding_from_history(history)
            if extracted_profile and extracted_profile.get('learningLevel'):
                # Save extracted profile
                try:
                    save_user_profile(session_id, extracted_profile)
                    profile = extracted_profile
                    print(f"✅ Extracted and saved onboarding from conversation history for session {session_id}")
                except Exception as e:
                    print(f"⚠️ Error saving extracted profile: {e}")
                    profile = extracted_profile  # Use it anyway
        except Exception as e:
            logger.warning(f"Failed to extract onboarding from history: {e}")
    
    # Get learning style from VECTOR STORAGE (priority) - with error handling
    vector_style_data = None
    try:
        if get_consent(session_id):
            vector_style_data = retrieve_learning_style_vector(session_id)
    except Exception as e:
        logger.warning(f"Failed to retrieve learning style vector for session {session_id}: {e}")
        # Continue without vector data - non-critical
    
    # Debug: Log profile data to verify it's being retrieved
    if profile:
        print(f"✅ Profile retrieved for session {session_id}: {profile}")
    if vector_style_data:
        print(f"✅ Vector learning style retrieved for session {session_id}: {vector_style_data.get('preferred_style')}")
    else:
        print(f"⚠️ No vector style found for session {session_id} (may not have completed onboarding)")
    
    # Get learning patterns (NEW - for enhanced personalization) - with error handling
    learning_patterns = {}
    try:
        if get_consent(session_id):
            learning_patterns = get_learning_patterns(session_id)
    except Exception as e:
        logger.warning(f"Failed to get learning patterns for session {session_id}: {e}")
        # Continue without patterns - non-critical
    
    # Build enhanced system prompt with personalization context
    system_prompt = SOCRATIC_MENTOR_PROMPT
    
    # PRIORITY: Add learning style from VECTOR STORAGE (most accurate)
    vector_style_context = ""
    if vector_style_data:
        vector_style_context = get_learning_style_instructions(session_id)
        print(f"✅ Using vector-based learning style instructions")
    
    # Add user profile context (from onboarding - fallback if no vector)
    # Use profile even if vector exists, to ensure all data is available
    profile_context = ""
    if profile:
        profile_context = "\n\n**About This Learner (from onboarding questions):**\n"
        if profile.get('learningLevel'):
            profile_context += f"- Learning Level: {profile['learningLevel']}\n"
            if profile['learningLevel'] == 'Beginner':
                profile_context += "  → Start with basics, use simple language, explain fundamentals\n"
            elif profile['learningLevel'] == 'Intermediate':
                profile_context += "  → They have some background, can build on existing knowledge\n"
            elif profile['learningLevel'] == 'Advanced':
                profile_context += "  → They have strong foundation, can dive deeper into concepts\n"
        
        if profile.get('interests'):
            profile_context += f"- Interests: {profile['interests']}\n"
            profile_context += "  → Reference these topics when creating examples and analogies\n"
        
        if profile.get('goals'):
            profile_context += f"- Learning Goals: {profile['goals']}\n"
            profile_context += "  → Keep their goals in mind, relate concepts to their objectives\n"
        
        if profile.get('preferredStyle'):
            style = profile['preferredStyle']
            profile_context += f"- Preferred Learning Style: {style}\n"
            if style == 'visual':
                profile_context += "  → CRITICAL: Use visual descriptions, diagrams, examples, code snippets\n"
                profile_context += "  → Say things like: 'Imagine this visually...', 'Picture this...', 'Here's an example...'\n"
            elif style == 'hands-on':
                profile_context += "  → CRITICAL: Provide practice exercises, encourage them to try things\n"
                profile_context += "  → Say things like: 'Try this yourself...', 'Let's practice...', 'Now you try...'\n"
            elif style == 'theoretical':
                profile_context += "  → CRITICAL: Explain concepts and principles first, then examples\n"
                profile_context += "  → Say things like: 'The principle behind this is...', 'Conceptually...', 'The theory is...'\n"
            elif style == 'mixed':
                profile_context += "  → CRITICAL: Combine visual examples, hands-on practice, and theory\n"
                profile_context += "  → Alternate between explanations, examples, and practice suggestions\n"
            profile_context += "  → ADAPT YOUR TEACHING STYLE TO MATCH THEIR PREFERENCE!\n"
        
        profile_context += "\n**CRITICAL PERSONALIZATION RULES:**\n"
        profile_context += "- ALWAYS reference their learning style when teaching\n"
        profile_context += "- Adapt examples to their interests and goals\n"
        profile_context += "- Match complexity to their learning level\n"
        profile_context += "- Use their preferred style in every response\n"
        profile_context += "- In your FIRST response, acknowledge their interests/goals if relevant\n"
        profile_context += "- Example: If they mentioned 'Python' in interests, say: 'I see Python is one of your interests!'\n"
    
    # Add learning patterns context (NEW - RAG-based personalization)
    patterns_context = ""
    if learning_patterns:
        patterns_context = "\n\n**Learning Patterns (from previous interactions):**\n"
        if learning_patterns.get('topics_learned'):
            topics = learning_patterns['topics_learned']
            if topics:
                patterns_context += f"- Topics they've explored: {', '.join(topics[:5])}\n"
        if learning_patterns.get('learning_pace'):
            patterns_context += f"- Learning Pace: {learning_patterns['learning_pace']}\n"
        if learning_patterns.get('strengths'):
            strengths = learning_patterns['strengths']
            if strengths:
                patterns_context += f"- Strengths (topics they understand well): {', '.join(strengths[:3])}\n"
        if learning_patterns.get('struggles'):
            struggles = learning_patterns['struggles']
            if struggles:
                patterns_context += f"- Areas they struggle with: {', '.join(struggles[:3])}\n"
        patterns_context += "\nUse these patterns to adapt your teaching style. Reference topics they've learned, "
        patterns_context += "build on their strengths, and be extra patient with areas they struggle with.\n"
    
    # Add conversation history context
    history_context = ""
    if history and len(history) > 0:
        history_context = "\n\n**Current Learning Context:**\n"
        history_context += f"You have had {len(history)} messages with this learner. "
        history_context += "Review their previous questions and responses to understand:\n"
        history_context += "- Their current level of understanding\n"
        history_context += "- Topics they're interested in\n"
        history_context += "- Concepts they've struggled with\n"
        history_context += "- Their learning style and pace\n"
        history_context += "\nPERSONALIZE your response based on this history. Reference their previous answers, "
        history_context += "build on what they've already said, and adapt your teaching to their specific needs."
    
    # Combine all contexts - VECTOR STYLE has highest priority
    if vector_style_context:
        system_prompt = SOCRATIC_MENTOR_PROMPT + vector_style_context + history_context + patterns_context
        logger.info(f"✅ Using VECTOR-based learning style for session {session_id}")
    elif profile_context or history_context or patterns_context:
        system_prompt = SOCRATIC_MENTOR_PROMPT + profile_context + history_context + patterns_context
        if profile_context:
            logger.info(f"✅ Using PROFILE-based learning style for session {session_id}")
            # Log the learning style being used
            if profile:
                style = profile.get('preferredStyle', 'not set')
                logger.info(f"   → Learning Style: {style}")
                logger.info(f"   → Learning Level: {profile.get('learningLevel', 'not set')}")
                logger.info(f"   → Interests: {profile.get('interests', 'not set')}")
                logger.info(f"   → Goals: {profile.get('goals', 'not set')}")
    else:
        system_prompt = SOCRATIC_MENTOR_PROMPT
        logger.warning(f"⚠️ No personalization context available for session {session_id} - using default prompt")
    
    # Log system prompt length for debugging (first 500 chars)
    logger.debug(f"System prompt preview (first 500 chars): {system_prompt[:500]}...")
    
    # Build messages with system prompt using LangChain message types
    messages = [SystemMessage(content=system_prompt)]
    
    if history:
        # Use more history for better personalization (last 15 messages)
        for h in history[-15:]:
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            elif h["role"] == "assistant":
                messages.append(AIMessage(content=h["content"]))
    
    messages.append(HumanMessage(content=message))
    
    # Stream response with validation check for quality model
    response_text = ""
    try:
        async for chunk in model.astream(messages):
            content = None
            if isinstance(chunk, AIMessage):
                content = chunk.content
            elif hasattr(chunk, 'content'):
                content = chunk.content
            elif isinstance(chunk, str):
                content = chunk
            
            if content:
                response_text += content
                yield content
    except Exception as e:
        logger.error(f"Error streaming quality model response: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Validate response starts with a question (after streaming complete)
    # Log warning if it doesn't - the prompt should enforce this
    if len(response_text) > 50:
        first_100 = response_text[:100].strip()
        starts_with_question = first_100.startswith(('What', 'How', 'Can', 'Would', 'Why', 'Could', "Let's", "That's", 'Do', 'Have', 'Did', 'Will', 'I\'m', 'I love', 'Great', 'That'))
        has_question_mark = '?' in first_100
        is_question = starts_with_question or has_question_mark
        
        # Exception: user explicitly asked for direct answer
        user_asked_directly = any(word in message.lower() for word in ['just tell', 'give me', 'i\'m stuck', 'i give up', 'explain it directly'])
        
        if not is_question and not user_asked_directly:
            print(f"⚠️ WARNING: Quality model response doesn't start with a question. First 100 chars: {first_100}")
    
    # Save to history (non-critical - don't fail if this fails)
    try:
        if get_consent(session_id):
            save_message_to_history(session_id, "user", message)
            save_message_to_history(session_id, "assistant", response_text)
            
            # Analyze and save learning patterns (NEW - RAG feature)
            # Only analyze if there's meaningful conversation (more than just greetings)
            try:
                history_check = get_conversation_history(session_id, limit=5)
                if len(history_check) >= 2:  # At least 1 user message + 1 assistant response
                    patterns = analyze_learning_patterns(session_id)
                    if patterns:
                        save_learning_patterns(session_id, patterns)
            except Exception as e:
                # Non-critical - don't fail the response if pattern analysis fails
                pass
    except Exception as e:
        logger.warning(f"Failed to save message to history: {e}")
        # Non-critical - continue

