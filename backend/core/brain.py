"""
Brain - Command Processing and Skill Routing
The "brain" of Jarvis that processes user commands and routes to appropriate skills.
"""

import logging
import re
import time
from typing import Dict, Callable, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Import skills
try:
    from backend.skills import open_app, alarms, youtube_skill, file_ops, system_info, music_player, weather_skill
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
            # Use correct field names from new schema
            context.append({
                "user": item.get("user_query", ""),
                "assistant": item.get("jarvis_response", "")
            })
        
        # Reverse to get chronological order (oldest first)
        context.reverse()
        
        logger.debug(f"Loaded {len(context)} conversation exchanges for context")
        return context
    
    except Exception as e:
        logger.warning(f"Failed to load conversation context: {e}")
        return []


def is_asking_about_history(text: str) -> bool:
    """
    Detect if user is asking about previous conversations.
    
    Args:
        text: User's query
    
    Returns:
        bool: True if asking about conversation history
    
    Examples:
        "what did I ask before?" → True
        "what was my first question?" → True
        "show me our previous chat" → True
        "what time is it?" → False
    """
    text_lower = text.lower()
    
    # Keywords indicating history lookup
    history_keywords = [
        "previous", "earlier", "before", "first", "last",
        "ago", "asked", "said", "told", "conversation",
        "chat", "history", "what did i", "what was my",
        "remember", "recall", "पहले", "पिछला", "बोला था"
    ]
    
    return any(keyword in text_lower for keyword in history_keywords)


def save_conversation(user_id: str, user_input: str, assistant_response: str):
    """
    Save conversation exchange to MongoDB.
    
    Args:
        user_id: User identifier
        user_input: What user said
        assistant_response: What Jarvis responded
    """
    try:
        # Use new Dict-based signature
        mongo_manager.save_conversation({
            "user_query": user_input,
            "jarvis_response": assistant_response,
            "intent": "chat",  # Default intent for brain.py internal saves
            "language_detected": "unknown",
            "expects_followup": False,
            "performance": {},
            "timestamp": time.time()
        })
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
    # skills registered dynamically below if available
}


# ============================================================================
# COMMAND PROCESSING
# ============================================================================

def process_command(text: str, user_id: str = "default_user", user_language: str = "en") -> Dict[str, Any]:
    """
    Process user command and route to appropriate skill.
    
    Flow:
    1. Normalize input (lowercase, strip)
    2. Check for quick replies (thanks, ok, hello) - no LLM needed
    3. Try keyword matching for common commands
    4. Load conversation context from MongoDB
    5. Use Qwen LLM with context for complex queries (in user's language)
    6. Save conversation to MongoDB
    7. Return response
    
    Args:
        text: User's spoken/typed command
        user_id: Unique identifier for user (for conversation context)
        user_language: Language user spoke in ('en', 'hi', 'unknown'/'mixed')
    
    Returns:
        Dict with response, intent, and any additional data
        {
            "response": "It's 10:30 AM",
            "intent": "get_time",
            "success": True
        }
    
    Examples:
        Input: "What time is it?", user_language="en"
        Output: {"response": "It's 10:30 AM", "intent": "time", "success": True}
        
        Input: "समय क्या है?", user_language="hi"
        Output: {"response": "अभी 10:30 AM है", "intent": "time", "success": True}
    """
    logger.info(f"Processing command: '{text}' (language: {user_language})")
    
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
                # Check if it looks like a website (contains .com, .org, etc.)
                if "." in original_text or any(tld in text_lower for tld in [".com", ".org", ".net", ".io", "youtube", "google", "github", "reddit"]):
                    # Extract full URL/domain
                    url_match = re.search(r"open\s+(.+)", text_lower)
                    if url_match and 'music_player' in globals():
                        url = url_match.group(1).strip()
                        res = music_player.open_link(url)
                        return {
                            "response": res,
                            "intent": "open_website",
                            "url": url,
                            "success": True
                        }
                
                # Use open_app skill if available
                if 'open_app' in globals():
                    try:
                        result = open_app.open_app(app_name)
                    except Exception:
                        result = f"Opening {app_name}."
                else:
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
            # Parse alarm and set using alarms skill if available
            if 'alarms' in globals():
                desc, scheduled_time = alarms.parse_alarm_from_text(original_text)
                if desc and scheduled_time:
                    res = alarms.set_alarm(desc, scheduled_time)
                    return {
                        "response": res,
                        "intent": "alarm",
                        "success": True
                    }
                else:
                    return {
                        "response": "I couldn't parse the alarm time. Please say 'Set alarm for 5pm' or 'Remind me in 10 minutes'.",
                        "intent": "alarm",
                        "success": False,
                        "note": "parse_failed"
                    }
            else:
                return {
                    "response": "Alarm functionality not available.",
                    "intent": "alarm",
                    "success": False,
                    "note": "not_available"
                }
        except Exception as e:
            logger.error(f"Alarm skill error: {e}")
            return {
                "response": "Sorry, I couldn't set the alarm.",
                "intent": "alarm",
                "success": False,
                "error": str(e)
            }
    
    # YouTube playback and Music (Spotify/YouTube)
    if any(keyword in text_lower for keyword in ["play", "youtube", "spotify", "song"]):
        try:
            # Use AI to extract both song name AND platform intelligently
            query = None
            platform = None
            
            try:
                from backend.core.qwen_api import chat_completion
                
                extraction_prompt = f"""Analyze this music command and extract the song name and platform.

Command: "{original_text}"

Return in this exact format:
SONG: [song name here]
PLATFORM: [spotify/youtube/default]

Rules:
- Extract the actual song/artist name (remove: "play", "on", "song", "the")
- Detect platform: If command mentions "spotify", return "spotify". If mentions "youtube", return "youtube". Otherwise return "default"
- Be smart about extraction

Examples:
"play tears on spotify" → 
SONG: tears
PLATFORM: spotify

"song tears on youtube" →
SONG: tears
PLATFORM: youtube

"the song tears" →
SONG: tears
PLATFORM: default

"play shape of you" →
SONG: shape of you
PLATFORM: default

Now analyze:"""

                messages = [
                    {"role": "system", "content": "You are a music command analyzer. Extract song name and platform. Return in the exact format requested."},
                    {"role": "user", "content": extraction_prompt}
                ]
                
                ai_response = chat_completion(messages, temperature=0.1, max_tokens=100, use_personality=False)
                
                # Parse AI response
                if ai_response and not ai_response.startswith("Error"):
                    lines = ai_response.strip().split('\n')
                    for line in lines:
                        if line.startswith("SONG:"):
                            query = line.replace("SONG:", "").strip().strip('"').strip("'")
                        elif line.startswith("PLATFORM:"):
                            platform = line.replace("PLATFORM:", "").strip().lower()
                    
                    if query:
                        logger.info(f"AI extracted - Song: '{query}', Platform: '{platform}' from '{original_text}'")
                    else:
                        raise ValueError("AI failed to extract song name")
                else:
                    raise ValueError("AI returned error or invalid response")
                
            except Exception as e:
                logger.warning(f"AI extraction failed, using regex fallback: {e}")
                # Fallback to regex if AI fails
                query = None
                platform = None
                
                # Detect platform first
                if "spotify" in text_lower:
                    platform = "spotify"
                elif "youtube" in text_lower:
                    platform = "youtube"
                else:
                    platform = "default"
                
                # Pattern 1: "play X on spotify/youtube" 
                match = re.search(r"play\s+(.+?)\s+on\s+(?:spotify|youtube)", text_lower)
                if match:
                    query = match.group(1).strip()
                
                # Pattern 2: "song X on spotify/youtube"
                if not query:
                    match = re.search(r"song\s+(.+?)\s+on\s+(?:spotify|youtube)", text_lower)
                    if match:
                        query = match.group(1).strip()
                
                # Pattern 3: "play X spotify/youtube" (without "on")
                if not query:
                    match = re.search(r"play\s+(.+?)\s+(?:spotify|youtube)", text_lower)
                    if match:
                        query = match.group(1).strip()
                
                # Pattern 4: "the song X on spotify/youtube"
                if not query:
                    match = re.search(r"(?:the\s+)?song\s+(.+?)\s+on\s+(?:spotify|youtube)", text_lower)
                    if match:
                        query = match.group(1).strip()
                
                # Pattern 5: "the song X" (any remaining text)
                if not query:
                    match = re.search(r"(?:the\s+)?song\s+(.+)", text_lower)
                    if match:
                        # Remove platform keywords if present
                        query = match.group(1).strip()
                        query = query.replace("spotify", "").replace("youtube", "").strip()
                
                # Pattern 6: Just "play X" (any remaining text)
                if not query:
                    match = re.search(r"play\s+(.+)", text_lower)
                    if match:
                        # Remove platform keywords if present
                        query = match.group(1).strip()
                        query = query.replace("spotify", "").replace("youtube", "").strip()
                
                logger.info(f"Regex extracted - Song: '{query}', Platform: '{platform}' from '{original_text}'")
            
            if not query:
                return {
                    "response": "What would you like me to play?",
                    "intent": "music",
                    "success": False,
                    "note": "no_query"
                }
            
            # Use music_player skill
            if 'music_player' in globals():
                # Route based on detected platform
                if platform == "spotify":
                    res = music_player.play_on_spotify(query)
                    intent = "spotify"
                elif platform == "youtube":
                    res = music_player.play_on_youtube(query)
                    intent = "youtube"
                else:
                    # Default to YouTube when no platform specified (FREE, no premium needed!)
                    res = music_player.play_on_youtube(query)
                    intent = "youtube"
                
                return {
                    "response": res,
                    "intent": intent,
                    "query": query,
                    "platform": platform,
                    "success": True
                }
            else:
                return {
                    "response": "Music playback not available.",
                    "intent": "music",
                    "success": False,
                    "note": "not_available"
                }
        except Exception as e:
            logger.error(f"Music playback error: {e}")
            return {
                "response": "Sorry, I couldn't play that.",
                "intent": "music",
                "success": False,
                "error": str(e)
            }
    
    # Open website/link
    if any(keyword in text_lower for keyword in [".com", ".org", ".net", ".io", "http", "www"]) or \
       (text_lower.startswith("open ") and "." in text_lower):
        try:
            # Extract URL
            url = original_text.replace("open", "").replace("Open", "").strip()
            
            if 'music_player' in globals():
                res = music_player.open_link(url)
                return {
                    "response": res,
                    "intent": "open_link",
                    "url": url,
                    "success": True
                }
            else:
                import webbrowser
                if not url.startswith("http"):
                    url = f"https://{url}"
                webbrowser.open(url)
                return {
                    "response": f"Opened {url}",
                    "intent": "open_link",
                    "url": url,
                    "success": True
                }
        except Exception as e:
            logger.error(f"Open link error: {e}")
            return {
                "response": "Sorry, I couldn't open that link.",
                "intent": "open_link",
                "success": False,
                "error": str(e)
            }
    
    # File operations
    if any(keyword in text_lower for keyword in ["create file", "open file"]):
        try:
            if 'file_ops' in globals():
                operation, filepath, content = file_ops.parse_file_command(original_text)
                
                if operation == "create":
                    res = file_ops.create_file(filepath, content or "")
                    return {
                        "response": res,
                        "intent": "file_create",
                        "filepath": filepath,
                        "success": True
                    }
                elif operation == "open":
                    res = file_ops.open_file(filepath)
                    return {
                        "response": res,
                        "intent": "file_open",
                        "filepath": filepath,
                        "success": True
                    }
                else:
                    return {
                        "response": "I couldn't understand the file command. Try 'Create file named test.txt' or 'Open file document.pdf'",
                        "intent": "file_ops",
                        "success": False,
                        "note": "parse_failed"
                    }
            else:
                return {
                    "response": "File operations not available.",
                    "intent": "file_ops",
                    "success": False,
                    "note": "not_available"
                }
        except Exception as e:
            logger.error(f"File ops error: {e}")
            return {
                "response": "Sorry, I couldn't complete the file operation.",
                "intent": "file_ops",
                "success": False,
                "error": str(e)
            }
    
    # System info
    if any(keyword in text_lower for keyword in ["battery", "cpu", "memory", "ram", "disk", "system info"]):
        try:
            if 'system_info' in globals():
                if "battery" in text_lower:
                    res = system_info.get_battery_status()
                    intent = "battery"
                elif "cpu" in text_lower:
                    res = system_info.get_cpu_usage()
                    intent = "cpu"
                elif any(kw in text_lower for kw in ["memory", "ram"]):
                    res = system_info.get_memory_usage()
                    intent = "memory"
                elif "disk" in text_lower:
                    res = system_info.get_disk_usage()
                    intent = "disk"
                else:
                    res = system_info.get_system_info()
                    intent = "system_info"
                
                return {
                    "response": res,
                    "intent": intent,
                    "success": True
                }
            else:
                return {
                    "response": "System info not available.",
                    "intent": "system_info",
                    "success": False,
                    "note": "not_available"
                }
        except Exception as e:
            logger.error(f"System info error: {e}")
            return {
                "response": "Sorry, I couldn't get system information.",
                "intent": "system_info",
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

    # Weather skill
    if "weather" in text_lower:
        try:
            if 'weather_skill' in globals():
                location = weather_skill.parse_weather_command(original_text)
                res = weather_skill.get_weather(location)
                return {
                    "response": res,
                    "intent": "weather",
                    "location": location or "current",
                    "success": True
                }
            else:
                return {
                    "response": "Weather skill not available.",
                    "intent": "weather",
                    "success": False,
                    "note": "not_available"
                }
        except Exception as e:
            logger.error(f"Weather skill error: {e}")
            return {
                "response": "Sorry, I couldn't check the weather.",
                "intent": "weather",
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # LLM WITH CONVERSATION CONTEXT
    # ========================================================================
    
    try:
        logger.info("No keyword match - using LLM with conversation context")
        
        # 🧠 Detect if user is asking about previous conversations
        asking_about_history = is_asking_about_history(original_text)
        
        # Load conversation history from MongoDB
        # If asking about history, load more (last 20); otherwise last 3
        context_limit = 20 if asking_about_history else 3
        conversation_context = load_conversation_context(user_id, limit=context_limit)
        
        if asking_about_history:
            logger.info(f"User asking about history - loaded {len(conversation_context)} conversations")
        
        # Detect language to adjust temperature
        language = detect_language(original_text)
        logger.debug(f"Detected language: {language}")
        
        # Build messages with context
        messages = []
        
        # Add conversation history
        for ctx in conversation_context:
            messages.append({"role": "user", "content": ctx["user"]})
            messages.append({"role": "assistant", "content": ctx["assistant"]})
        
        # Build language instruction based on detected language
        language_instruction = ""
        max_tokens = MAX_TOKENS_SETTINGS['normal']  # Default 500
        
        if user_language == "hi":
            language_instruction = "\n\nIMPORTANT: User spoke in Hindi. Respond in Hindi (Devanagari script). Keep responses concise and clear."
            max_tokens = 800  # Hindi needs more tokens
        elif user_language in ["unknown", "mixed"]:
            language_instruction = "\n\nIMPORTANT: User spoke in Hinglish (Hindi-English mix). Respond in Hinglish using Roman script. Mix Hindi and English naturally - use English words for technical/difficult terms (like 'multithreading', 'computer', 'internet') and Hindi for simple conversational words. Example: 'Multithreading ek technique hai jisme ek saath kaafi saare tasks run hote hain.'"
            max_tokens = 600  # Hinglish needs slightly more
        # If English, no special instruction needed
        
        # Add special instruction if asking about history
        if asking_about_history:
            language_instruction += "\n\nNOTE: User is asking about our previous conversation. Reference the conversation history provided above to answer accurately."
        
        # Add current user message with language hint
        user_message = original_text + language_instruction
        messages.append({"role": "user", "content": user_message})
        
        # Call Qwen with personality (personality injected automatically in qwen_api.py)
        chat_response = qwen_api.chat_completion(
            messages,
            temperature=TEMPERATURE_SETTINGS['conversational'],
            max_tokens=max_tokens  # Use language-specific token limit
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
