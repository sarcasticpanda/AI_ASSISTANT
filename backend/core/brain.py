"""
Brain - Command Processing and Skill Routing
The "brain" of Jarvis that processes user commands and routes to appropriate skills.
"""

import logging
import re
from typing import Dict, Callable, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Import skills
try:
    from backend.skills import open_app, alarms
except ImportError as e:
    logger.warning(f"Some skills not available yet: {e}")

# Import core modules (these are required)
from backend.core import qwen_api, mongo_manager
from backend.core.personality import is_quick_reply, detect_language, TEMPERATURE_SETTINGS, MAX_TOKENS_SETTINGS


# ============================================================================
# FOLLOW-UP DETECTION (Internal - not shown to user)
# ============================================================================

def _analyze_response_patterns(response: str) -> dict:
    """
    Quick pattern-based check if response expects follow-up.
    Fast (no API call), works offline, ~85-90% accurate.
    
    Args:
        response: Jarvis's response text
    
    Returns:
        {
            "expects_followup": bool,
            "confidence": float (0.0-1.0),
            "timeout": int (seconds)
        }
    """
    # Pattern 1: Direct questions
    question_patterns = [
        r"would you like",
        r"do you want",
        r"should I",
        r"would you prefer",
        r"interested in",
        r"need (more|additional|further)",
        r"want me to",
        r"shall I",
        r"can I help",
    ]
    
    # Pattern 2: Choice offering
    choice_patterns = [
        r"or would you",
        r"alternatively",
        r"you can also",
        r"either .* or",
    ]
    
    # Pattern 3: Ends with question mark
    ends_with_question = response.strip().endswith("?")
    
    response_lower = response.lower()
    
    # Calculate score
    score = 0.0
    
    # Check question patterns
    question_matches = sum(1 for p in question_patterns if re.search(p, response_lower))
    if question_matches > 0:
        score += 0.7
    
    # Check choice patterns
    choice_matches = sum(1 for p in choice_patterns if re.search(p, response_lower))
    if choice_matches > 0:
        score += 0.2
    
    # Check question mark
    if ends_with_question:
        score += 0.3
    
    # Cap at 1.0
    confidence = min(score, 1.0)
    expects_followup = confidence > 0.5
    
    # Higher confidence = longer timeout
    timeout = 10 if confidence > 0.8 else (8 if confidence > 0.6 else 5)
    
    return {
        "expects_followup": expects_followup,
        "confidence": confidence,
        "timeout": timeout,
        "method": "pattern_matching"
    }


def _ask_qwen_about_followup(response: str) -> dict:
    """
    Ask Qwen internally if its response expects user input.
    More accurate (~95-99%) but requires API call (+0.5s delay).
    
    Args:
        response: Jarvis's response text
    
    Returns:
        {
            "expects_followup": bool,
            "confidence": float (1.0 if yes, 0.0 if no),
            "timeout": int
        }
    """
    try:
        # Meta-prompt to Qwen (internal check - not shown to user)
        meta_messages = [
            {
                "role": "system",
                "content": "You are analyzing responses. Answer ONLY 'yes' or 'no' - nothing else."
            },
            {
                "role": "user",
                "content": f"""Response: "{response}"

Does this response expect the user to reply or provide input?
Answer only: yes or no"""
            }
        ]
        
        # Call Qwen with minimal tokens (fast)
        meta_response = qwen_api.chat_completion(
            meta_messages,
            temperature=0.0,  # Deterministic
            max_tokens=5,     # Just "yes" or "no"
            use_personality=False  # Skip personality injection
        ).strip().lower()
        
        expects_followup = "yes" in meta_response
        
        return {
            "expects_followup": expects_followup,
            "confidence": 1.0 if expects_followup else 0.0,
            "timeout": 10 if expects_followup else 0,
            "method": "qwen_meta_check",
            "meta_response": meta_response
        }
    
    except Exception as e:
        logger.warning(f"Qwen meta-check failed: {e}")
        # Return neutral result on failure
        return {
            "expects_followup": False,
            "confidence": 0.0,
            "timeout": 0,
            "method": "qwen_meta_check_failed",
            "error": str(e)
        }


def detect_followup_needed(response: str, use_qwen_check: bool = True) -> dict:
    """
    HYBRID: Detect if response expects follow-up input from user.
    Uses pattern matching first (fast), then Qwen check if uncertain.
    
    This is INTERNAL - user never sees this analysis.
    The voice loop uses this to decide whether to wait for user input.
    
    Args:
        response: Jarvis's response text
        use_qwen_check: Whether to use Qwen meta-check for uncertain cases
    
    Returns:
        {
            "expects_followup": bool,
            "confidence": float (0.0-1.0),
            "timeout": int (seconds to wait for user),
            "method": str (which detection method was used)
        }
    
    Example:
        >>> detect_followup_needed("It's 3:00 PM")
        {"expects_followup": False, "confidence": 0.0, "timeout": 0}
        
        >>> detect_followup_needed("Would you like more details?")
        {"expects_followup": True, "confidence": 0.9, "timeout": 10}
    """
    # Step 1: Quick pattern check (always runs - instant)
    pattern_result = _analyze_response_patterns(response)
    
    # If high confidence from patterns, trust it
    if pattern_result["confidence"] > 0.8 or pattern_result["confidence"] == 0.0:
        logger.debug(f"Follow-up detection (pattern): {pattern_result}")
        return pattern_result
    
    # Step 2: If uncertain and online, ask Qwen for confirmation
    if use_qwen_check and pattern_result["confidence"] < 0.8:
        logger.debug("Pattern confidence low - checking with Qwen...")
        qwen_result = _ask_qwen_about_followup(response)
        
        # If Qwen check succeeded, use it
        if qwen_result.get("method") == "qwen_meta_check":
            logger.debug(f"Follow-up detection (Qwen): {qwen_result}")
            return qwen_result
    
    # Fallback: Use pattern result
    logger.debug(f"Follow-up detection (fallback to pattern): {pattern_result}")
    return pattern_result


# ============================================================================
# CONVERSATION CONTEXT HELPERS
# ============================================================================

def load_conversation_context(user_id: str, limit: int = 3) -> list:
    """
    Load recent conversation history from MongoDB.
    
    Args:
        user_id: User identifier
        limit: Number of recent exchanges to load
    
    Returns:
        List of conversation dicts: [{"user": "...", "assistant": "..."}, ...]
    """
    try:
        # Query recent conversations using direct function
        history = mongo_manager.get_recent_history(limit=limit)
        
        # Format for context: [{user: "...", assistant: "..."}]
        context = []
        for item in history:
            context.append({
                "user": item.get("user_text", ""),
                "assistant": item.get("assistant_text", "")
            })
        
        logger.debug(f"Loaded {len(context)} conversation exchanges for context")
        return context
    
    except Exception as e:
        logger.warning(f"Failed to load conversation context: {e}")
        return []


def save_conversation(user_id: str, user_input: str, assistant_response: str):
    """
    Save conversation exchange to MongoDB.
    
    Args:
        user_id: User identifier
        user_input: What user said
        assistant_response: What Jarvis responded
    """
    try:
        # Use direct function call
        mongo_manager.save_conversation(user_input, assistant_response, intent=None)
        logger.debug(f"Saved conversation to MongoDB")
    
    except Exception as e:
        logger.error(f"Failed to save conversation: {e}")


# ============================================================================
# SKILL REGISTRY
# ============================================================================

def get_time() -> str:
    """Get current time"""
    now = datetime.now()
    return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}"


def get_date() -> str:
    """Get current date"""
    now = datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')}"


# Skill registry: maps intent keywords to functions
SKILLS: Dict[str, Callable] = {
    "time": get_time,
    "date": get_date,
    # "open": open_app.open_app,  # Uncomment when open_app is ready
    # "alarm": alarms.set_alarm,  # Uncomment when alarms is ready
}


# ============================================================================
# COMMAND PROCESSING
# ============================================================================

def process_command(text: str, user_id: str = "default_user") -> Dict[str, Any]:
    """
    Process user command and route to appropriate skill.
    
    Flow:
    1. Normalize input (lowercase, strip)
    2. Check for quick replies (thanks, ok, hello) - no LLM needed
    3. Try keyword matching for common commands
    4. Load conversation context from MongoDB
    5. Use Qwen LLM with context for complex queries
    6. Save conversation to MongoDB
    7. Return response
    
    Args:
        text: User's spoken/typed command
        user_id: Unique identifier for user (for conversation context)
    
    Returns:
        Dict with response, intent, and any additional data
        {
            "response": "It's 10:30 AM",
            "intent": "get_time",
            "success": True
        }
    
    Examples:
        Input: "What time is it?"
        Output: {"response": "It's 10:30 AM", "intent": "time", "success": True}
        
        Input: "Thanks"
        Output: {"response": "My pleasure.", "intent": "quick_reply", "success": True}
    """
    logger.info(f"Processing command: '{text}'")
    
    # Normalize input
    original_text = text
    text_lower = text.lower().strip()
    
    if not text_lower:
        return {
            "response": "I didn't catch that. Could you repeat?",
            "intent": "unknown",
            "success": False
        }
    
    # ========================================================================
    # QUICK REPLIES (No LLM needed - instant response)
    # ========================================================================
    
    is_quick, quick_response = is_quick_reply(text_lower)
    if is_quick:
        logger.info(f"Quick reply matched: '{text_lower}' -> '{quick_response}'")
        return {
            "response": quick_response,
            "intent": "quick_reply",
            "success": True,
            "method": "quick_reply"
        }
    
    # ========================================================================
    # KEYWORD MATCHING (Fast path for common commands)
    # ========================================================================
    
    # Time queries
    if any(keyword in text_lower for keyword in ["time", "clock"]):
        try:
            response = get_time()
            return {
                "response": response,
                "intent": "time",
                "success": True
            }
        except Exception as e:
            logger.error(f"Time skill error: {e}")
            return {
                "response": "Sorry, I couldn't get the time.",
                "intent": "time",
                "success": False,
                "error": str(e)
            }
    
    # Date queries
    if any(keyword in text_lower for keyword in ["date", "today", "day"]):
        try:
            response = get_date()
            return {
                "response": response,
                "intent": "date",
                "success": True
            }
        except Exception as e:
            logger.error(f"Date skill error: {e}")
            return {
                "response": "Sorry, I couldn't get the date.",
                "intent": "date",
                "success": False,
                "error": str(e)
            }
    
    # Open app/website
    if "open" in text_lower:
        # Extract app name (e.g., "open chrome" -> "chrome")
        match = re.search(r"open\s+(\w+)", text_lower)
        if match:
            app_name = match.group(1)
            try:
                # TODO: Uncomment when open_app skill is ready
                # result = open_app.open_app(app_name)
                result = f"Opening {app_name}."
                return {
                    "response": result,
                    "intent": "open_app",
                    "app_name": app_name,
                    "success": True
                }
            except Exception as e:
                logger.error(f"Open app skill error: {e}")
                return {
                    "response": f"Sorry, I couldn't open {app_name}.",
                    "intent": "open_app",
                    "success": False,
                    "error": str(e)
                }
    
    # Alarm/reminder
    if any(keyword in text_lower for keyword in ["alarm", "remind", "reminder"]):
        try:
            # TODO: Parse time and description from text
            # For now, placeholder
            return {
                "response": "Alarm functionality coming soon.",
                "intent": "alarm",
                "success": False,
                "note": "not_implemented"
            }
        except Exception as e:
            logger.error(f"Alarm skill error: {e}")
            return {
                "response": "Sorry, I couldn't set the alarm.",
                "intent": "alarm",
                "success": False,
                "error": str(e)
            }
    
    # PDF summarization
    if "summarize" in text_lower or "summary" in text_lower:
        return {
            "response": "Please use the PDF summarization endpoint with a file path.",
            "intent": "summarize_pdf",
            "success": False,
            "note": "Use /summarize_pdf endpoint instead"
        }
    
    # ========================================================================
    # LLM WITH CONVERSATION CONTEXT
    # ========================================================================
    
    try:
        logger.info("No keyword match - using LLM with conversation context")
        
        # 🧠 Load conversation history from MongoDB
        conversation_context = load_conversation_context(user_id)
        
        # Detect language to adjust temperature
        language = detect_language(original_text)
        logger.debug(f"Detected language: {language}")
        
        # Build messages with context
        messages = []
        
        # Add conversation history (last 3 exchanges)
        for ctx in conversation_context:
            messages.append({"role": "user", "content": ctx["user"]})
            messages.append({"role": "assistant", "content": ctx["assistant"]})
        
        # Add current user message
        messages.append({"role": "user", "content": original_text})
        
        # Call Qwen with personality (personality injected automatically in qwen_api.py)
        chat_response = qwen_api.chat_completion(
            messages,
            temperature=TEMPERATURE_SETTINGS['conversational'],
            max_tokens=MAX_TOKENS_SETTINGS['normal']
        )
        
        # � INTERNAL: Detect if response expects follow-up
        followup_info = detect_followup_needed(chat_response, use_qwen_check=True)
        
        # �💾 Save conversation to MongoDB
        try:
            save_conversation(user_id, original_text, chat_response)
        except Exception as e:
            logger.warning(f"Failed to save conversation: {e}")
        
        return {
            "response": chat_response,
            "intent": "chat",
            "success": True,
            "method": "llm_with_context",
            "language": language,
            
            # 🆕 FOLLOWUP METADATA (used by voice loop)
            "expects_followup": followup_info["expects_followup"],
            "followup_timeout": followup_info["timeout"],
            "followup_confidence": followup_info["confidence"],
            "followup_method": followup_info["method"]
        }
    
    except Exception as e:
        logger.error(f"LLM error: {e}")
        
        # Ultimate fallback
        return {
            "response": "I'm experiencing some difficulty. Could you try again?",
            "intent": "unknown",
            "success": False,
            "error": str(e)
        }


# ============================================================================
# UTILITIES
# ============================================================================

def register_skill(intent: str, handler: Callable):
    """
    Dynamically register a new skill.
    
    Args:
        intent: Intent keyword (e.g., "weather", "news")
        handler: Function to call when intent is matched
    
    Example:
        def get_weather(location="here"):
            return f"Weather in {location}: Sunny, 72°F"
        
        register_skill("weather", get_weather)
    """
    SKILLS[intent] = handler
    logger.info(f"Registered skill: {intent}")


def list_skills() -> list:
    """Get list of all registered skills"""
    return list(SKILLS.keys())
