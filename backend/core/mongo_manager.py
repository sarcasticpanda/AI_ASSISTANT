"""
MongoDB Manager - Database connection and operations
Handles conversation history, PDF summaries, and alarms storage.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

# Global MongoDB client
_client: Optional[MongoClient] = None
_db = None


def initialize():
    """
    Initialize MongoDB connection.
    Reads MONGO_URI from environment and connects.
    """
    global _client, _db
    
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/jarvis_db")
    
    try:
        logger.info(f"Connecting to MongoDB: {mongo_uri}")
        _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Extract database name from URI or use default
        if "/" in mongo_uri:
            db_name = mongo_uri.split("/")[-1].split("?")[0]
        else:
            db_name = "jarvis_db"
        
        _db = _client[db_name]
        
        # Test connection
        _client.admin.command('ping')
        logger.info(f"✓ Connected to MongoDB database: {db_name}")
        
        # Create indexes for better performance
        _create_indexes()
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB connection failed: {e}")
        logger.warning("Running without database - history will not be saved")
        _client = None
        _db = None


def _create_indexes():
    """Create indexes for better query performance"""
    if _db is None:
        return
    
    try:
        # Index on timestamp for conversations
        _db.conversations.create_index([("timestamp", DESCENDING)])
        
        # Index on intent for conversations
        _db.conversations.create_index("intent")
        
        # Index on language for conversations
        _db.conversations.create_index("language_detected")
        
        # Index on filename for PDF summaries
        _db.pdf_summaries.create_index("filename")
        
        # Index on scheduled_time for alarms
        _db.alarms.create_index("scheduled_time")
        
        # Index on timestamp for app commands
        _db.app_commands.create_index([("timestamp", DESCENDING)])
        
        # Index on target (app name) for app commands
        _db.app_commands.create_index("target")
        
        # Index on intent for analytics
        _db.command_analytics.create_index("intent")
        
        # Index on timestamp for analytics
        _db.command_analytics.create_index([("timestamp", DESCENDING)])
        
        # Unique index on key for user settings
        _db.user_settings.create_index("key", unique=True)
        
        logger.info("✓ Database indexes created")
    except Exception as e:
        logger.warning(f"Index creation warning: {e}")


def ping():
    """
    Ping database to check connection.
    Raises exception if not connected.
    """
    if _client is None:
        raise ConnectionError("MongoDB not connected")
    
    _client.admin.command('ping')


def close():
    """Close MongoDB connection"""
    global _client, _db
    
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")
        _client = None
        _db = None


# ============================================================================
# CONVERSATION HISTORY
# ============================================================================

def save_conversation(conversation_data: Dict) -> str:
    """
    Save a conversation turn to database.
    
    Args:
        conversation_data: Dictionary with conversation details
            Required keys:
            - user_query: What the user said
            - jarvis_response: What Jarvis responded
            - intent: Classified intent
            Optional keys:
            - language_detected: Language code (en, hi, mixed)
            - expects_followup: Whether expecting follow-up
            - performance: Dict with stt_time, brain_time, tts_time, total_time
            - timestamp: Unix timestamp (will use current time if not provided)
    
    Returns:
        str: Inserted document ID
    
    Example:
        save_conversation({
            "user_query": "What time is it?",
            "jarvis_response": "It's 1:09 PM",
            "intent": "time",
            "language_detected": "en",
            "performance": {
                "stt_time": 0.54,
                "brain_time": 0.00,
                "tts_time": 2.31,
                "total_time": 2.85
            }
        })
    """
    if _db is None:
        logger.warning("MongoDB not available - conversation not saved")
        return "no_db"
    
    try:
        # Build document with required fields
        document = {
            "timestamp": datetime.utcnow(),
            "user_query": conversation_data.get("user_query", ""),
            "jarvis_response": conversation_data.get("jarvis_response", ""),
            "intent": conversation_data.get("intent", "unknown"),
            "language_detected": conversation_data.get("language_detected", "en"),
            "expects_followup": conversation_data.get("expects_followup", False),
            "performance": conversation_data.get("performance", {}),
        }
        
        # Add optional unix timestamp if provided
        if "timestamp" in conversation_data:
            document["unix_timestamp"] = conversation_data["timestamp"]
        
        result = _db.conversations.insert_one(document)
        logger.info(f"Saved conversation: {result.inserted_id}")
        
        return str(result.inserted_id)
    
    except Exception as e:
        logger.error(f"Failed to save conversation: {e}")
        return "error"


def get_recent_history(limit: int = 20) -> List[Dict]:
    """
    Get recent conversation history.
    
    Args:
        limit: Number of recent conversations to retrieve
    
    Returns:
        List of conversation documents (sorted newest first)
    """
    if _db is None:
        logger.warning("MongoDB not available - returning empty history")
        return []
    
    try:
        cursor = _db.conversations.find(
            {},
            {"_id": 0}  # Exclude _id from results
        ).sort("timestamp", DESCENDING).limit(limit)
        
        history = list(cursor)
        
        # Convert datetime to string for JSON serialization
        for item in history:
            if "timestamp" in item and isinstance(item["timestamp"], datetime):
                item["timestamp"] = item["timestamp"].isoformat()
        
        logger.info(f"Retrieved {len(history)} conversation items")
        return history
    
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        return []


def clear_history():
    """Clear all conversation history"""
    if _db is None:
        return
    
    try:
        result = _db.conversations.delete_many({})
        logger.info(f"Cleared {result.deleted_count} conversations")
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")


def search_conversations(query: str, limit: int = 10) -> List[Dict]:
    """
    Search conversations by text (user query or Jarvis response).
    
    Args:
        query: Text to search for
        limit: Maximum results to return
    
    Returns:
        List of matching conversation documents
    
    Example:
        results = search_conversations("time", limit=5)
        # Returns conversations mentioning "time"
    """
    if _db is None:
        return []
    
    try:
        # Case-insensitive regex search in both user_query and jarvis_response
        cursor = _db.conversations.find(
            {
                "$or": [
                    {"user_query": {"$regex": query, "$options": "i"}},
                    {"jarvis_response": {"$regex": query, "$options": "i"}}
                ]
            },
            {"_id": 0}
        ).sort("timestamp", DESCENDING).limit(limit)
        
        results = list(cursor)
        
        # Convert datetime to string
        for item in results:
            if "timestamp" in item and isinstance(item["timestamp"], datetime):
                item["timestamp"] = item["timestamp"].isoformat()
        
        logger.info(f"Found {len(results)} conversations matching '{query}'")
        return results
    
    except Exception as e:
        logger.error(f"Failed to search conversations: {e}")
        return []


def get_conversation_count() -> int:
    """Get total number of conversations stored"""
    if _db is None:
        return 0
    
    try:
        count = _db.conversations.count_documents({})
        return count
    except Exception as e:
        logger.error(f"Failed to count conversations: {e}")
        return 0


# ============================================================================
# APP/WEBSITE COMMANDS
# ============================================================================

def save_app_command(command_data: Dict) -> str:
    """
    Save app/website/file open command.
    
    Args:
        command_data: Dictionary with command details
            Required keys:
            - command_type: "open_app", "open_website", "open_file"
            - target: App/website/file name
            - user_query: Original user query
            Optional keys:
            - success: Whether command succeeded
            - error: Error message if failed
            - timestamp: Unix timestamp
    
    Returns:
        str: Inserted document ID
    
    Example:
        save_app_command({
            "command_type": "open_app",
            "target": "Chrome",
            "user_query": "open Chrome browser",
            "success": True
        })
    """
    if _db is None:
        logger.warning("MongoDB not available - app command not saved")
        return "no_db"
    
    try:
        document = {
            "timestamp": datetime.utcnow(),
            "command_type": command_data.get("command_type", "unknown"),
            "target": command_data.get("target", ""),
            "user_query": command_data.get("user_query", ""),
            "success": command_data.get("success", True),
            "error": command_data.get("error", None)
        }
        
        if "timestamp" in command_data:
            document["unix_timestamp"] = command_data["timestamp"]
        
        result = _db.app_commands.insert_one(document)
        logger.info(f"Saved app command: {command_data.get('target')}")
        
        return str(result.inserted_id)
    
    except Exception as e:
        logger.error(f"Failed to save app command: {e}")
        return "error"


def get_frequent_apps(limit: int = 10) -> List[Dict]:
    """
    Get most frequently opened apps/websites.
    
    Args:
        limit: Number of top apps to return
    
    Returns:
        List of {app_name, count} sorted by frequency
    
    Example:
        [
            {"app": "Chrome", "count": 45},
            {"app": "VS Code", "count": 32},
            ...
        ]
    """
    if _db is None:
        return []
    
    try:
        pipeline = [
            {"$group": {
                "_id": "$target",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "_id": 0,
                "app": "$_id",
                "count": "$count"
            }}
        ]
        
        result = list(_db.app_commands.aggregate(pipeline))
        return result
    
    except Exception as e:
        logger.error(f"Failed to get frequent apps: {e}")
        return []


def get_recent_apps(limit: int = 10) -> List[Dict]:
    """
    Get recently opened apps/websites.
    
    Args:
        limit: Number of recent apps to return
    
    Returns:
        List of recent app commands
    """
    if _db is None:
        return []
    
    try:
        cursor = _db.app_commands.find(
            {},
            {"_id": 0}
        ).sort("timestamp", DESCENDING).limit(limit)
        
        apps = list(cursor)
        
        # Convert datetime to string
        for app in apps:
            if "timestamp" in app and isinstance(app["timestamp"], datetime):
                app["timestamp"] = app["timestamp"].isoformat()
        
        return apps
    
    except Exception as e:
        logger.error(f"Failed to get recent apps: {e}")
        return []


# ============================================================================
# VOICE COMMAND ANALYTICS
# ============================================================================

def save_command_analytics(intent: str, success: bool = True, response_time: float = 0.0):
    """
    Track command analytics for insights.
    
    Args:
        intent: Command intent (time, alarm, open_app, etc.)
        success: Whether command succeeded
        response_time: Total response time in seconds
    """
    if _db is None:
        return
    
    try:
        document = {
            "timestamp": datetime.utcnow(),
            "intent": intent,
            "success": success,
            "response_time": response_time
        }
        
        _db.command_analytics.insert_one(document)
        logger.debug(f"Logged analytics: {intent}")
    
    except Exception as e:
        logger.error(f"Failed to save analytics: {e}")


def get_command_stats() -> Dict:
    """
    Get command usage statistics.
    
    Returns:
        Dict with intent counts and success rates
    
    Example:
        {
            "total_commands": 150,
            "success_rate": 0.96,
            "top_intents": [
                {"intent": "time", "count": 45, "success_rate": 1.0},
                {"intent": "open_app", "count": 32, "success_rate": 0.94},
                ...
            ]
        }
    """
    if _db is None:
        return {}
    
    try:
        # Total commands
        total = _db.command_analytics.count_documents({})
        
        # Success rate
        successful = _db.command_analytics.count_documents({"success": True})
        success_rate = successful / total if total > 0 else 0
        
        # Top intents with success rates
        pipeline = [
            {"$group": {
                "_id": "$intent",
                "count": {"$sum": 1},
                "successful": {
                    "$sum": {"$cond": ["$success", 1, 0]}
                },
                "avg_response_time": {"$avg": "$response_time"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10},
            {"$project": {
                "_id": 0,
                "intent": "$_id",
                "count": "$count",
                "success_rate": {
                    "$divide": ["$successful", "$count"]
                },
                "avg_response_time": {"$round": ["$avg_response_time", 2]}
            }}
        ]
        
        top_intents = list(_db.command_analytics.aggregate(pipeline))
        
        return {
            "total_commands": total,
            "success_rate": round(success_rate, 3),
            "top_intents": top_intents
        }
    
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {}


# ============================================================================
# USER SETTINGS
# ============================================================================

def save_user_setting(key: str, value) -> bool:
    """
    Save a user preference setting.
    
    Args:
        key: Setting name (e.g., "preferred_language", "voice_speed")
        value: Setting value
    
    Returns:
        bool: Success status
    
    Example:
        save_user_setting("preferred_language", "hi")
        save_user_setting("voice_speed", 1.2)
    """
    if _db is None:
        return False
    
    try:
        _db.user_settings.update_one(
            {"key": key},
            {
                "$set": {
                    "key": key,
                    "value": value,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        logger.info(f"Saved setting: {key} = {value}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to save setting: {e}")
        return False


def get_user_setting(key: str, default=None):
    """
    Get a user preference setting.
    
    Args:
        key: Setting name
        default: Default value if not found
    
    Returns:
        Setting value or default
    """
    if _db is None:
        return default
    
    try:
        result = _db.user_settings.find_one({"key": key})
        return result.get("value") if result else default
    
    except Exception as e:
        logger.error(f"Failed to get setting: {e}")
        return default


def get_all_settings() -> Dict:
    """
    Get all user settings.
    
    Returns:
        Dict of {key: value} pairs
    """
    if _db is None:
        return {}
    
    try:
        settings = {}
        cursor = _db.user_settings.find({}, {"_id": 0, "key": 1, "value": 1})
        
        for item in cursor:
            settings[item["key"]] = item["value"]
        
        return settings
    
    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        return {}


# ============================================================================
# PDF SUMMARIES
# ============================================================================

def save_pdf_summary(filename: str, summary: str, chunks: List[str], chunk_summaries: Optional[List[str]] = None) -> str:
    """
    Save PDF summary to database.
    
    Args:
        filename: PDF filename (e.g., "report.pdf")
        summary: Final merged summary
        chunks: List of text chunks extracted
        chunk_summaries: Individual summaries for each chunk (optional)
    
    Returns:
        str: Inserted document ID
    
    Example document:
    {
        "_id": ObjectId("..."),
        "filename": "report.pdf",
        "timestamp": ISODate("2025-10-27T10:30:00Z"),
        "summary": "This report discusses...",
        "chunks_count": 5,
        "chunks": ["chunk1...", "chunk2...", ...],
        "chunk_summaries": ["summary1...", "summary2...", ...]
    }
    """
    if _db is None:
        logger.warning("MongoDB not available - PDF summary not saved")
        return "no_db"
    
    try:
        document = {
            "filename": filename,
            "timestamp": datetime.utcnow(),
            "summary": summary,
            "chunks_count": len(chunks),
            "chunks": chunks,
            "chunk_summaries": chunk_summaries or []
        }
        
        # Update if exists, insert if new (upsert)
        result = _db.pdf_summaries.update_one(
            {"filename": filename},
            {"$set": document},
            upsert=True
        )
        
        logger.info(f"Saved PDF summary for {filename}")
        return str(result.upserted_id) if result.upserted_id else "updated"
    
    except Exception as e:
        logger.error(f"Failed to save PDF summary: {e}")
        return "error"


def get_pdf_summary(filename: str) -> Optional[Dict]:
    """
    Get PDF summary by filename.
    
    Args:
        filename: PDF filename to search for
    
    Returns:
        Dict with summary data or None if not found
    """
    if _db is None:
        logger.warning("MongoDB not available")
        return None
    
    try:
        result = _db.pdf_summaries.find_one(
            {"filename": filename},
            {"_id": 0}
        )
        
        # Convert datetime to string
        if result and "timestamp" in result:
            result["timestamp"] = result["timestamp"].isoformat()
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to get PDF summary: {e}")
        return None


# ============================================================================
# ALARMS
# ============================================================================

def save_alarm(description: str, scheduled_time: datetime, repeat: bool = False) -> str:
    """
    Save alarm to database.
    
    Args:
        description: What the alarm is for
        scheduled_time: When it should trigger
        repeat: Whether it repeats
    
    Returns:
        str: Inserted document ID
    
    Example document:
    {
        "_id": ObjectId("..."),
        "description": "Morning standup meeting",
        "scheduled_time": ISODate("2025-10-28T09:00:00Z"),
        "repeat": false,
        "active": true,
        "created_at": ISODate("2025-10-27T10:30:00Z")
    }
    """
    if _db is None:
        logger.warning("MongoDB not available - alarm not saved")
        return "no_db"
    
    try:
        document = {
            "description": description,
            "scheduled_time": scheduled_time,
            "repeat": repeat,
            "active": True,
            "created_at": datetime.utcnow()
        }
        
        result = _db.alarms.insert_one(document)
        logger.info(f"Saved alarm: {result.inserted_id}")
        
        return str(result.inserted_id)
    
    except Exception as e:
        logger.error(f"Failed to save alarm: {e}")
        return "error"


def get_active_alarms() -> List[Dict]:
    """
    Get all active alarms.
    
    Returns:
        List of alarm documents
    """
    if _db is None:
        return []
    
    try:
        cursor = _db.alarms.find(
            {"active": True},
            {"_id": 0}
        ).sort("scheduled_time", 1)
        
        alarms = list(cursor)
        
        # Convert datetime to string
        for alarm in alarms:
            if "scheduled_time" in alarm:
                alarm["scheduled_time"] = alarm["scheduled_time"].isoformat()
            if "created_at" in alarm:
                alarm["created_at"] = alarm["created_at"].isoformat()
        
        return alarms
    
    except Exception as e:
        logger.error(f"Failed to get alarms: {e}")
        return []


def deactivate_alarm(description: str):
    """Mark an alarm as inactive"""
    if _db is None:
        return
    
    try:
        _db.alarms.update_one(
            {"description": description},
            {"$set": {"active": False}}
        )
        logger.info(f"Deactivated alarm: {description}")
    
    except Exception as e:
        logger.error(f"Failed to deactivate alarm: {e}")
