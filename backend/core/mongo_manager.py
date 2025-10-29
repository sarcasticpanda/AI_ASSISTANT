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
        # Index on timestamp for conversation history
        _db.conversation_history.create_index([("timestamp", DESCENDING)])
        
        # Index on filename for PDF summaries
        _db.pdf_summaries.create_index("filename")
        
        # Index on scheduled_time for alarms
        _db.alarms.create_index("scheduled_time")
        
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

def save_conversation(user_text: str, assistant_text: str, intent: Optional[str] = None) -> str:
    """
    Save a conversation turn to database.
    
    Args:
        user_text: What the user said
        assistant_text: What Jarvis responded
        intent: Classified intent (e.g., "open_app", "summarize_pdf")
    
    Returns:
        str: Inserted document ID
    
    Example document:
    {
        "_id": ObjectId("..."),
        "timestamp": ISODate("2025-10-27T10:30:00Z"),
        "user_text": "Summarize this PDF",
        "assistant_text": "Sure, I'll summarize it for you...",
        "intent": "summarize_pdf"
    }
    """
    if _db is None:
        logger.warning("MongoDB not available - conversation not saved")
        return "no_db"
    
    try:
        document = {
            "timestamp": datetime.utcnow(),
            "user_text": user_text,
            "assistant_text": assistant_text,
            "intent": intent
        }
        
        result = _db.conversation_history.insert_one(document)
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
    
    Example:
    [
        {
            "timestamp": "2025-10-27T10:30:00",
            "user_text": "What time is it?",
            "assistant_text": "It's 10:30 AM",
            "intent": "get_time"
        },
        ...
    ]
    """
    if _db is None:
        logger.warning("MongoDB not available - returning empty history")
        return []
    
    try:
        cursor = _db.conversation_history.find(
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
