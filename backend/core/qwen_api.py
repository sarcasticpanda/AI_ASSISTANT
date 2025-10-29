"""
Qwen API - OpenRouter Integration
Wrapper for calling Qwen LLM via OpenRouter for reasoning, summarization, and chat.
"""

import os
import logging
import json
from typing import List, Dict, Optional
import requests
from .personality import JARVIS_PERSONALITY

logger = logging.getLogger(__name__)

# OpenRouter endpoint
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Default model (you can change this)
DEFAULT_MODEL = "qwen/qwen-2.5-72b-instruct"  # or "qwen/qwen-2-7b-instruct" for faster responses


def _get_api_key() -> str:
    """
    Get OpenRouter API key from environment.
    Raises error if not set.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key or api_key == "or-sk-REPLACE_ME":
        raise ValueError(
            "OPENROUTER_API_KEY not set in .env file. "
            "Get your key from https://openrouter.ai/keys"
        )
    
    return api_key


# ============================================================================
# CORE LLM FUNCTIONS
# ============================================================================

def chat_completion(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    use_personality: bool = True
) -> str:
    """
    Call OpenRouter chat completion API.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
                 Example: [{"role": "user", "content": "Hello"}]
        model: Model to use (default: DEFAULT_MODEL)
        temperature: Randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum response length
        use_personality: Whether to inject Jarvis personality (default: True)
    
    Returns:
        str: The assistant's response text
    
    Example:
        response = chat_completion([
            {"role": "user", "content": "What is 2+2?"}
        ])
        # Returns: "That's 4, sir." (with Jarvis personality)
    
    curl equivalent:
        curl -X POST https://openrouter.ai/api/v1/chat/completions \
          -H "Authorization: Bearer YOUR_KEY" \
          -H "Content-Type: application/json" \
          -d '{
            "model": "qwen/qwen-2.5-72b-instruct",
            "messages": [{"role": "user", "content": "Hello"}]
          }'
    """
    try:
        api_key = _get_api_key()
    except ValueError as e:
        logger.error(str(e))
        return f"Error: {e}"
    
    if model is None:
        model = DEFAULT_MODEL
    
    # 🧠 INJECT PERSONALITY - Always add system prompt for Jarvis behavior
    if use_personality:
        # Check if there's already a system message
        has_system = any(msg.get("role") == "system" for msg in messages)
        
        if not has_system:
            # Add Jarvis personality at the beginning
            messages = [
                {"role": "system", "content": JARVIS_PERSONALITY},
                *messages
            ]
            logger.debug("Injected Jarvis personality into conversation")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jarvis-assistant.local",  # Optional: for OpenRouter analytics
        "X-Title": "Jarvis Assistant"  # Optional: shown in OpenRouter dashboard
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        logger.info(f"Calling OpenRouter API with model: {model}")
        
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()  # Raise error for 4xx/5xx status codes
        
        data = response.json()
        
        # Extract assistant's message
        assistant_message = data["choices"][0]["message"]["content"]
        
        logger.info(f"Received response ({len(assistant_message)} chars)")
        
        return assistant_message.strip()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return f"Error calling LLM: {e}"
    
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected API response format: {e}")
        return "Error: Unexpected response from LLM"


# ============================================================================
# SUMMARIZATION
# ============================================================================

def summarize_text(text: str, max_length: int = 500) -> str:
    """
    Summarize a text chunk using Qwen.
    
    Args:
        text: Text to summarize
        max_length: Maximum summary length in characters
    
    Returns:
        str: Summary of the text
    
    Example:
        summary = summarize_text("Long article text here...")
        # Returns: "This article discusses..."
    """
    logger.info(f"Summarizing text ({len(text)} chars)")
    
    prompt = f"""Summarize the following text concisely in {max_length} characters or less:

{text}

Summary:"""
    
    messages = [
        {"role": "system", "content": "You are an expert at creating concise, accurate summaries."},
        {"role": "user", "content": prompt}
    ]
    
    summary = chat_completion(
        messages,
        temperature=0.3,  # Lower temperature for more focused summaries
        max_tokens=max_length // 2  # Rough token estimate
    )
    
    return summary


def merge_summaries(summaries: List[str]) -> str:
    """
    Merge multiple chunk summaries into a final coherent summary.
    
    Args:
        summaries: List of individual chunk summaries
    
    Returns:
        str: Final merged summary
    
    Example:
        chunk_summaries = [
            "Chapter 1 discusses AI basics...",
            "Chapter 2 covers neural networks...",
            "Chapter 3 explains transformers..."
        ]
        final = merge_summaries(chunk_summaries)
        # Returns: "This document provides an overview of AI, starting with..."
    """
    logger.info(f"Merging {len(summaries)} summaries")
    
    combined = "\n\n".join([f"Part {i+1}: {s}" for i, s in enumerate(summaries)])
    
    prompt = f"""Create a cohesive summary from these individual summaries:

{combined}

Provide a single, well-structured summary that captures the main points:"""
    
    messages = [
        {"role": "system", "content": "You are an expert at synthesizing information from multiple sources."},
        {"role": "user", "content": prompt}
    ]
    
    merged = chat_completion(
        messages,
        temperature=0.4,
        max_tokens=800
    )
    
    return merged


# ============================================================================
# INTENT CLASSIFICATION
# ============================================================================

def classify_intent(text: str) -> Dict[str, any]:
    """
    Classify user's intent and extract parameters.
    
    Args:
        text: User's command/query
    
    Returns:
        Dict with 'intent' and 'params'
        {
            "intent": "open_app",
            "params": {"app_name": "chrome"}
        }
    
    Example:
        result = classify_intent("Open Chrome browser")
        # Returns: {"intent": "open_app", "params": {"app_name": "chrome"}}
        
        result = classify_intent("Set an alarm for 7 AM tomorrow")
        # Returns: {"intent": "alarm", "params": {"time": "07:00", "description": "alarm"}}
    """
    logger.info(f"Classifying intent for: '{text}'")
    
    prompt = f"""Classify the user's intent and extract relevant parameters from this command:

"{text}"

Return ONLY a JSON object with 'intent' and 'params' fields.

Possible intents:
- time: Get current time
- date: Get current date
- open_app: Open an application
- alarm: Set an alarm/reminder
- weather: Get weather information
- news: Get news
- email: Read/send emails
- chat: General conversation
- unknown: Cannot determine intent

Example outputs:
{{"intent": "open_app", "params": {{"app_name": "chrome"}}}}
{{"intent": "alarm", "params": {{"time": "07:00", "description": "morning alarm"}}}}
{{"intent": "time", "params": {{}}}}

JSON:"""
    
    messages = [
        {"role": "system", "content": "You are an intent classifier. Return only valid JSON."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = chat_completion(
            messages,
            temperature=0.1,  # Very low temperature for consistent JSON output
            max_tokens=200
        )
        
        # Parse JSON response
        # Try to extract JSON if wrapped in code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response)
        
        logger.info(f"Classified intent: {result.get('intent')}")
        
        return result
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse intent JSON: {e}")
        logger.debug(f"Raw response: {response}")
        
        # Fallback
        return {
            "intent": "unknown",
            "params": {}
        }


# ============================================================================
# UTILITIES
# ============================================================================

def is_online() -> bool:
    """
    Check if we can reach OpenRouter API.
    
    Returns:
        bool: True if online, False otherwise
    """
    try:
        response = requests.get("https://openrouter.ai", timeout=3)
        return response.status_code == 200
    except:
        return False


def test_connection() -> str:
    """
    Test OpenRouter API connection with a simple query.
    
    Returns:
        str: Success message or error
    """
    try:
        response = chat_completion([
            {"role": "user", "content": "Say 'Connection successful' if you can read this."}
        ])
        return f"✓ OpenRouter connection successful: {response}"
    except Exception as e:
        return f"✗ Connection failed: {e}"
