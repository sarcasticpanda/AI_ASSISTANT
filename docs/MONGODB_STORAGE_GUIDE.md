# 🗄️ MongoDB Storage Guide - Complete Data Architecture

## 📊 Database Overview

**Database Name**: `jarvis_db`

**Collections** (6 total):
1. ✅ `conversations` - Every user interaction
2. ✅ `app_commands` - App/website/file opens
3. ✅ `command_analytics` - Usage statistics
4. ✅ `user_settings` - User preferences
5. ✅ `pdf_summaries` - PDF metadata + summaries
6. ✅ `alarms` - Scheduled alarms/reminders

---

## 📚 Collection Schemas

### 1️⃣ **conversations** (Main conversation log)

**Purpose**: Track every interaction with Jarvis

**Schema**:
```json
{
  "_id": ObjectId("..."),
  "timestamp": ISODate("2025-11-05T13:09:00Z"),
  "unix_timestamp": 1730819340.123,
  "user_query": "What time is it?",
  "language_detected": "en",
  "jarvis_response": "It's 1:09 PM on Wednesday, November 5th, 2025.",
  "intent": "time",
  "expects_followup": false,
  "performance": {
    "stt_time": 0.54,
    "brain_time": 0.00,
    "tts_time": 2.31,
    "total_time": 2.85
  }
}
```

**Indexes**:
- `timestamp` (descending) - Fast recent queries
- `intent` - Filter by command type
- `language_detected` - Language analytics

**Use Cases**:
- Conversation history review
- Language usage analytics
- Performance tracking over time
- Context for follow-up questions

---

### 2️⃣ **app_commands** (App/Website/File Opens)

**Purpose**: Track what apps/websites user opens most

**Schema**:
```json
{
  "_id": ObjectId("..."),
  "timestamp": ISODate("2025-11-05T13:10:00Z"),
  "unix_timestamp": 1730819400.123,
  "command_type": "open_app",
  "target": "Chrome",
  "user_query": "open Chrome browser",
  "success": true,
  "error": null
}
```

**Indexes**:
- `timestamp` (descending) - Recent commands
- `target` - Group by app name

**Use Cases**:
- Quick access suggestions ("You usually open Chrome at this time")
- Frequency analytics ("You've opened VS Code 45 times this week")
- Error tracking (failed app opens)

**Query Examples**:
```python
# Most frequently opened apps
mongo_manager.get_frequent_apps(limit=10)
# Returns: [{"app": "Chrome", "count": 45}, ...]

# Recent commands
mongo_manager.get_recent_apps(limit=10)
```

---

### 3️⃣ **command_analytics** (Usage Statistics)

**Purpose**: Track command performance and success rates

**Schema**:
```json
{
  "_id": ObjectId("..."),
  "timestamp": ISODate("2025-11-05T13:10:00Z"),
  "intent": "open_app",
  "success": true,
  "response_time": 2.85
}
```

**Indexes**:
- `intent` - Group by command type
- `timestamp` (descending) - Time-based analytics

**Use Cases**:
- Success rate monitoring
- Performance benchmarking
- Identify problematic commands
- Usage trends over time

**Query Examples**:
```python
# Get comprehensive stats
stats = mongo_manager.get_command_stats()
# Returns:
# {
#   "total_commands": 150,
#   "success_rate": 0.96,
#   "top_intents": [
#     {"intent": "time", "count": 45, "success_rate": 1.0, "avg_response_time": 2.3},
#     ...
#   ]
# }
```

---

### 4️⃣ **user_settings** (User Preferences)

**Purpose**: Persistent user preferences

**Schema**:
```json
{
  "_id": ObjectId("..."),
  "key": "preferred_language",
  "value": "hi",
  "updated_at": ISODate("2025-11-05T13:10:00Z")
}
```

**Indexes**:
- `key` (unique) - Fast lookups, prevent duplicates

**Supported Settings**:
- `preferred_language`: "en" | "hi" | "mixed"
- `voice_speed`: 0.8 - 1.5 (TTS speed multiplier)
- `wake_word_sensitivity`: 0.0 - 1.0
- `noise_threshold_multiplier`: 1.0 - 3.0
- `auto_follow_up`: true | false
- `save_conversations`: true | false

**Query Examples**:
```python
# Save setting
mongo_manager.save_user_setting("preferred_language", "hi")

# Get setting
lang = mongo_manager.get_user_setting("preferred_language", default="en")

# Get all settings
all_settings = mongo_manager.get_all_settings()
# Returns: {"preferred_language": "hi", "voice_speed": 1.2, ...}
```

---

### 5️⃣ **pdf_summaries** (PDF Metadata + Summaries)

**Purpose**: Store PDF summaries and Firebase URLs

**Schema**:
```json
{
  "_id": ObjectId("..."),
  "filename": "AI_Research.pdf",
  "firebase_url": "https://firebasestorage.googleapis.com/...",
  "timestamp": ISODate("2025-11-05T13:10:00Z"),
  "summary": "This PDF discusses artificial intelligence research...",
  "chunks_count": 5,
  "chunks": ["chunk1 text...", "chunk2 text...", ...],
  "chunk_summaries": ["summary1...", "summary2...", ...],
  "questions_asked": [
    {
      "question": "What is the main topic?",
      "answer": "AI research",
      "timestamp": ISODate("2025-11-05T13:15:00Z")
    }
  ]
}
```

**Indexes**:
- `filename` (unique) - Fast lookups

**Use Cases**:
- Avoid re-summarizing same PDF
- Answer questions about previously read PDFs
- Track PDF usage analytics

**Query Examples**:
```python
# Save PDF summary
mongo_manager.save_pdf_summary(
    filename="AI_Research.pdf",
    summary="This PDF discusses...",
    chunks=["chunk1", "chunk2"],
    chunk_summaries=["summary1", "summary2"]
)

# Get PDF summary
summary = mongo_manager.get_pdf_summary("AI_Research.pdf")
```

---

### 6️⃣ **alarms** (Scheduled Alarms/Reminders)

**Purpose**: Persistent alarm storage

**Schema**:
```json
{
  "_id": ObjectId("..."),
  "description": "Morning standup meeting",
  "scheduled_time": ISODate("2025-11-06T09:00:00Z"),
  "repeat": false,
  "active": true,
  "created_at": ISODate("2025-11-05T13:10:00Z")
}
```

**Indexes**:
- `scheduled_time` - Fast time-based queries

**Query Examples**:
```python
# Save alarm
mongo_manager.save_alarm(
    description="Morning standup",
    scheduled_time=datetime(2025, 11, 6, 9, 0),
    repeat=False
)

# Get active alarms
alarms = mongo_manager.get_active_alarms()

# Deactivate alarm
mongo_manager.deactivate_alarm("Morning standup")
```

---

## 🔧 MongoDB Manager Functions

### Conversations
```python
# Save conversation
mongo_manager.save_conversation({
    "user_query": "What time is it?",
    "language_detected": "en",
    "jarvis_response": "It's 1:09 PM",
    "intent": "time",
    "expects_followup": False,
    "performance": {...}
})

# Get recent history
history = mongo_manager.get_recent_history(limit=20)

# Clear all history
mongo_manager.clear_history()
```

### App Commands
```python
# Save app command
mongo_manager.save_app_command({
    "command_type": "open_app",
    "target": "Chrome",
    "user_query": "open Chrome",
    "success": True
})

# Get frequent apps
apps = mongo_manager.get_frequent_apps(limit=10)

# Get recent apps
recent = mongo_manager.get_recent_apps(limit=10)
```

### Analytics
```python
# Save analytics
mongo_manager.save_command_analytics(
    intent="time",
    success=True,
    response_time=2.85
)

# Get stats
stats = mongo_manager.get_command_stats()
```

### User Settings
```python
# Save setting
mongo_manager.save_user_setting("preferred_language", "hi")

# Get setting
lang = mongo_manager.get_user_setting("preferred_language", default="en")

# Get all settings
settings = mongo_manager.get_all_settings()
```

---

## 📊 Viewing Your Data

### Method 1: Interactive Viewer (Recommended)
```powershell
python tests\view_mongodb_data.py
```

**Features**:
- View recent conversations
- See app command history
- Check most frequently used apps
- View command statistics
- Check user settings
- Full database report

### Method 2: MongoDB Compass (GUI)
1. Download: https://www.mongodb.com/try/download/compass
2. Install and open
3. Connect to: `mongodb://localhost:27017`
4. Navigate to `jarvis_db` database
5. Browse collections visually

### Method 3: MongoDB Shell (Terminal)
```bash
# Connect to MongoDB
mongosh

# Use jarvis_db
use jarvis_db

# View recent conversations
db.conversations.find().sort({timestamp: -1}).limit(5).pretty()

# Count total conversations
db.conversations.countDocuments()

# Get most frequent apps
db.app_commands.aggregate([
  {$group: {_id: "$target", count: {$sum: 1}}},
  {$sort: {count: -1}},
  {$limit: 10}
])
```

---

## 🎯 What Gets Saved Automatically

When you run `phase1_online.py`, these are saved **automatically**:

✅ **Every conversation** → `conversations` collection
✅ **App/website opens** → `app_commands` collection  
✅ **Command analytics** → `command_analytics` collection

**Not saved automatically** (you can add manually):
- User settings (use `save_user_setting()`)
- PDF summaries (Phase 2 - coming soon)
- Alarms (use `save_alarm()`)

---

## 📈 Analytics Insights You Can Get

### 1. Language Usage
```python
# Which language do I use most?
db.conversations.aggregate([
  {$group: {_id: "$language_detected", count: {$sum: 1}}},
  {$sort: {count: -1}}
])
```

### 2. Most Asked Questions
```python
# What do I ask Jarvis most?
db.command_analytics.aggregate([
  {$group: {_id: "$intent", count: {$sum: 1}}},
  {$sort: {count: -1}},
  {$limit: 10}
])
```

### 3. Performance Over Time
```python
# Average response time by intent
db.conversations.aggregate([
  {$group: {
    _id: "$intent",
    avg_time: {$avg: "$performance.total_time"}
  }},
  {$sort: {avg_time: -1}}
])
```

### 4. Most Opened Apps
```python
apps = mongo_manager.get_frequent_apps(limit=10)
# [{"app": "Chrome", "count": 45}, ...]
```

---

## 🔒 Privacy & Data Management

### Clear All Data
```python
from backend.core import mongo_manager

# Clear conversations
mongo_manager.clear_history()

# Or delete entire database (terminal)
# mongosh
# use jarvis_db
# db.dropDatabase()
```

### Backup Data
```bash
# Export all collections
mongodump --db jarvis_db --out ./backup/

# Import backup
mongorestore --db jarvis_db ./backup/jarvis_db/
```

### Data Retention
By default, data is kept **forever**. To auto-delete old data:

```python
# Delete conversations older than 30 days (add to phase1_online.py)
from datetime import datetime, timedelta

cutoff_date = datetime.utcnow() - timedelta(days=30)
mongo_manager._db.conversations.delete_many({
    "timestamp": {"$lt": cutoff_date}
})
```

---

## 🚀 Next Steps

1. ✅ **DONE**: MongoDB storage implemented
2. 🔜 **Firebase Setup**: Store PDF files in cloud
3. 🔜 **Phase 2**: PDF summarization with Firebase + MongoDB
4. 🔜 **Electron App**: Visual dashboard for all this data
5. 🔜 **Analytics Dashboard**: Graphs and insights

---

## 💡 Pro Tips

1. **Check your data regularly**:
   ```powershell
   python tests\view_mongodb_data.py
   ```

2. **Monitor storage size**:
   ```bash
   mongosh
   use jarvis_db
   db.stats()
   ```

3. **Create custom queries**:
   ```python
   from backend.core import mongo_manager
   
   # Your custom query
   result = mongo_manager._db.conversations.find({
       "intent": "time",
       "language_detected": "hi"
   })
   ```

4. **Export to JSON**:
   ```bash
   mongoexport --db jarvis_db --collection conversations --out conversations.json
   ```

---

## 📝 Summary

**6 Collections Created**:
- ✅ conversations (main log)
- ✅ app_commands (app opens)
- ✅ command_analytics (stats)
- ✅ user_settings (preferences)
- ✅ pdf_summaries (PDF data)
- ✅ alarms (reminders)

**Auto-Saved Data**:
- Every conversation
- Every app/website open
- Command success/failure
- Performance metrics

**View Data**:
```powershell
python tests\view_mongodb_data.py
```

**Your data is now being tracked!** 🎉
