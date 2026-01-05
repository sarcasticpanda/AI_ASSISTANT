"""
Alarms Skill - Set and manage alarms/reminders
Uses APScheduler for scheduling and MongoDB for persistence.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import re

logger = logging.getLogger(__name__)

# Try importing APScheduler
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.date import DateTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    logger.warning("APScheduler not installed. Install with: pip install APScheduler")
    APSCHEDULER_AVAILABLE = False
    BackgroundScheduler = None  # Define as None to prevent NameError in type hints

# Import core modules
try:
    from backend.core import mongo_manager, tts_offline
except ImportError:
    pass


# Global scheduler
_scheduler: Optional[BackgroundScheduler] = None


def _get_scheduler():
    """Get or create scheduler instance"""
    global _scheduler
    
    if _scheduler is None:
        if not APSCHEDULER_AVAILABLE:
            raise ImportError("APScheduler not available")
        
        _scheduler = BackgroundScheduler()
        _scheduler.start()
        logger.info("✓ Alarm scheduler started")
    
    return _scheduler


def _alarm_callback(description: str):
    """
    Called when alarm triggers.
    
    Args:
        description: Alarm description
    """
    logger.info(f"🔔 ALARM: {description}")
    
    # Speak the alarm
    try:
        message = f"Alarm: {description}"
        tts_offline.speak_local_simple(message)
    except Exception as e:
        logger.error(f"Failed to speak alarm: {e}")
    
    # Mark as triggered in database
    try:
        mongo_manager.deactivate_alarm(description)
    except:
        pass


def set_alarm(description: str, scheduled_time: datetime, repeat: bool = False) -> str:
    """
    Set an alarm.
    
    Args:
        description: What the alarm is for
        scheduled_time: When it should trigger
        repeat: Whether it repeats (not yet implemented)
    
    Returns:
        str: Status message
    
    Example:
        from datetime import datetime, timedelta
        
        # Set alarm for 30 minutes from now
        alarm_time = datetime.now() + timedelta(minutes=30)
        set_alarm("Check laundry", alarm_time)
    """
    try:
        scheduler = _get_scheduler()
        
        # Add job to scheduler
        scheduler.add_job(
            _alarm_callback,
            trigger=DateTrigger(run_date=scheduled_time),
            args=[description],
            id=f"alarm_{description}_{scheduled_time.timestamp()}",
            replace_existing=True
        )
        
        # Save to database
        mongo_manager.save_alarm(description, scheduled_time, repeat)
        
        time_str = scheduled_time.strftime("%I:%M %p on %B %d")
        
        logger.info(f"✓ Alarm set: {description} at {time_str}")
        
        return f"Alarm set for {time_str}: {description}"
    
    except Exception as e:
        logger.error(f"Failed to set alarm: {e}")
        return f"Error setting alarm: {e}"


def parse_alarm_from_text(text: str) -> tuple:
    """
    Parse alarm time and description from natural language.
    
    Args:
        text: Natural language alarm request
    
    Returns:
        tuple: (description, scheduled_time) or (None, None) if parsing failed
    
    Examples:
        "Set an alarm for 7 AM tomorrow" -> ("alarm", datetime(...))
        "Remind me to call mom in 30 minutes" -> ("call mom", datetime(...))
        "Wake me up at 6:30" -> ("wake up", datetime(...))
    """
    text = text.lower()
    
    # Try to extract time
    scheduled_time = None
    description = "alarm"
    
    # Pattern: "in X minutes/hours"
    match = re.search(r"in (\d+) (minute|hour)s?", text)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit == "minute":
            scheduled_time = datetime.now() + timedelta(minutes=value)
        else:  # hour
            scheduled_time = datetime.now() + timedelta(hours=value)
        
        # Extract description
        desc_match = re.search(r"(?:remind me to|for) (.+?) in", text)
        if desc_match:
            description = desc_match.group(1)
    
    # Pattern: "at HH:MM" or "for HH:MM" or "at Hpm/am"
    match = re.search(r"(?:at|for)\s+(\d{1,2}):?(\d{2})?\s*(am|pm)?", text)
    if match and not scheduled_time:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        am_pm = match.group(3)
        
        # If no AM/PM specified but hour <= 12, assume PM for convenience
        if not am_pm and 1 <= hour <= 12:
            am_pm = "pm"
        
        # Convert to 24-hour format
        if am_pm == "pm" and hour != 12:
            hour += 12
        elif am_pm == "am" and hour == 12:
            hour = 0
        
        # Create datetime for today or tomorrow
        now = datetime.now()
        scheduled_time = datetime(now.year, now.month, now.day, hour, minute)
        
        # If time has passed today, schedule for tomorrow
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)
        
        # Check for "tomorrow"
        if "tomorrow" in text:
            scheduled_time += timedelta(days=1)
    
    # Extract description if not already set
    if description == "alarm":
        # Try to find "to do X" or "for X"
        desc_match = re.search(r"(?:to |for )(.+?)(?:at|in|$)", text)
        if desc_match:
            description = desc_match.group(1).strip()
    
    if scheduled_time:
        return (description, scheduled_time)
    
    return (None, None)


def list_alarms() -> list:
    """
    Get list of active alarms.
    
    Returns:
        list: Active alarms from database
    """
    try:
        alarms = mongo_manager.get_active_alarms()
        return alarms
    except Exception as e:
        logger.error(f"Failed to get alarms: {e}")
        return []


def cancel_alarm(description: str) -> str:
    """
    Cancel an alarm by description.
    
    Args:
        description: Alarm description
    
    Returns:
        str: Status message
    """
    try:
        scheduler = _get_scheduler()
        
        # Remove from scheduler (search by description in job ID)
        jobs = scheduler.get_jobs()
        removed = False
        
        for job in jobs:
            if description.lower() in job.id.lower():
                scheduler.remove_job(job.id)
                removed = True
                logger.info(f"Removed job: {job.id}")
        
        # Remove from database
        mongo_manager.deactivate_alarm(description)
        
        if removed:
            return f"Cancelled alarm: {description}"
        else:
            return f"No alarm found with description: {description}"
    
    except Exception as e:
        logger.error(f"Failed to cancel alarm: {e}")
        return f"Error cancelling alarm: {e}"


# ============================================================================
# UTILITIES
# ============================================================================

def is_available() -> bool:
    """Check if alarm functionality is available"""
    return APSCHEDULER_AVAILABLE
