"""
Weather Skill - Get current weather using wttr.in (No API Key Required)
"""

import logging
import requests
import re
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

def get_weather(location: str = None) -> str:
    """
    Get weather for a specific location or auto-detect if None.
    Uses wttr.in which is free and requires no key.
    
    Args:
        location: City name (e.g., "London", "New York") or None for auto-IP
    
    Returns:
        str: Human readable weather summary
    """
    try:
        # Prepare URL
        # format=3 gives a one-line text summary: "London: ⛅️ +12°C"
        # format=j1 gives detailed JSON
        
        url = "https://wttr.in"
        
        if location:
            # Clean location string
            location = location.strip()
            url = f"{url}/{location}"
        
        # Use format=3 for simple one-line summary first
        params = {"format": "3"}
        
        logger.info(f"Fetching weather for: {location or 'Auto-IP'}")
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            weather_text = response.text.strip()
            
            # Sometimes wttr.in returns HTML on error or not found
            if "<html" in weather_text.lower():
                return f"Sorry, I couldn't find weather data for {location}."
                
            return f"Current weather: {weather_text}"
        else:
            logger.error(f"Weather API error: {response.status_code}")
            return "Sorry, I couldn't fetch the weather right now."
            
    except Exception as e:
        logger.error(f"Weather skill error: {e}")
        return "I encountered an error checking the weather."

def parse_weather_command(text: str) -> str:
    """
    Extract location from weather command.
    
    Examples:
        "weather in London" -> "London"
        "what is the weather like in New York" -> "New York"
        "check weather" -> None
    """
    text = text.lower()
    
    # Pattern 1: "in [Location]"
    match = re.search(r"weather.*?in\s+(.+)", text)
    if match:
        return match.group(1).strip()
        
    # Pattern 2: "for [Location]"
    match = re.search(r"weather.*?for\s+(.+)", text)
    if match:
        return match.group(1).strip()
        
    # If just "weather", return None (implies current location)
    return None
