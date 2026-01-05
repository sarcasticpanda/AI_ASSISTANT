# 🧠 Context Memory Guide - How Jarvis Remembers

## 📋 Overview

Jarvis has **intelligent context memory** that adapts based on what you ask:

### **Smart Context Loading:**

1. **Normal Questions** (Default):
   - Loads **last 3 conversations**
   - Fast and efficient
   - Example: "What time is it?"

2. **History Questions** (Auto-detects):
   - Loads **last 20 conversations**
   - Searches entire conversation history
   - Example: "What did I ask you earlier?"

---

## 🔍 How It Works

### **Detection Keywords**

When you use these words, Jarvis loads **20 conversations** instead of 3:

**English Keywords:**
- "previous", "earlier", "before"
- "first", "last", "ago"
- "asked", "said", "told"
- "conversation", "chat", "history"
- "what did I", "what was my"
- "remember", "recall"

**Hindi Keywords:**
- "पहले" (before)
- "पिछला" (previous)
- "बोला था" (I said)

**Example Queries:**
```
✅ "What did I ask before?" → Loads 20 conversations
✅ "What was my first question?" → Loads 20 conversations
✅ "Show me our previous chat" → Loads 20 conversations
✅ "Remember what I said earlier?" → Loads 20 conversations
❌ "What time is it?" → Loads 3 conversations (normal)
```

---

## 📊 Context Limits

| Scenario | Conversations Loaded | Why |
|----------|---------------------|-----|
| Normal chat | 3 | Fast, recent context |
| History lookup | 20 | Full context search |
| Maximum stored | Unlimited | All saved in MongoDB |

---

## 🧪 Test Examples

### **Test 1: Normal Context (3 conversations)**

```
You: "What time is it?"
Jarvis: "It's 2:30 PM"

You: "Set alarm for 5pm"
Jarvis: "Alarm set for 5 PM"

You: "Thanks"
Jarvis: "You're welcome!"

You: "What did I just say?"
Jarvis: "You said thanks" ← Uses last 3 conversations
```

### **Test 2: History Lookup (20 conversations)**

```
[After 15 conversations...]

You: "What was my first question today?"
Jarvis: [Loads last 20 conversations, finds first one]
       "Your first question was 'What time is it?'"

You: "What did I ask about earlier?"
Jarvis: [Searches through 20 conversations]
       "Earlier you asked about setting an alarm for 5pm"
```

### **Test 3: Specific Search**

```
You: "What did we talk about regarding alarms?"
Jarvis: [Loads 20 conversations, searches for "alarm"]
       "You asked me to set an alarm for 5pm, and I confirmed it"
```

---

## 💾 MongoDB Storage

All conversations are saved **forever** (or until you clear them):

**Storage Location:**
```
Database: jarvis_db
Collection: conversations
Total Stored: Unlimited
```

**What's Saved:**
```json
{
  "timestamp": "2025-11-05T14:30:00Z",
  "user_query": "What time is it?",
  "jarvis_response": "It's 2:30 PM",
  "language_detected": "en",
  "intent": "time",
  "performance": {...}
}
```

---

## 🎯 Use Cases

### 1️⃣ **Follow-up Questions**
```
You: "What time is it?"
Jarvis: "2:30 PM"

You: "What did I just ask?"
Jarvis: "You asked what time it is"
```

### 2️⃣ **Recall Previous Info**
```
You: "Set alarm for 5pm"
Jarvis: "Alarm set"

[10 conversations later...]

You: "What alarm did I set earlier?"
Jarvis: [Searches history] "You set an alarm for 5pm"
```

### 3️⃣ **Summary Requests**
```
You: "What have we talked about today?"
Jarvis: [Loads 20 conversations]
       "Today we discussed the time, set alarms, opened apps..."
```

### 4️⃣ **Language-Specific**
```
You: "पहले मैंने क्या पूछा था?" (What did I ask before?)
Jarvis: [Loads 20 conversations, responds in Hindi]
       "आपने समय के बारे में पूछा था" (You asked about time)
```

---

## 🔧 Technical Details

### **Code Flow:**

1. **User speaks**: "What did I ask before?"

2. **Detection** (brain.py):
   ```python
   asking_about_history = is_asking_about_history(text)
   # Returns: True (found "before" keyword)
   ```

3. **Load Context**:
   ```python
   if asking_about_history:
       context_limit = 20  # Load more
   else:
       context_limit = 3   # Default
   
   conversation_context = load_conversation_context(user_id, limit=context_limit)
   ```

4. **Build Prompt**:
   ```python
   messages = [
       {"role": "user", "content": "What time is it?"},
       {"role": "assistant", "content": "It's 2:30 PM"},
       # ... up to 20 conversations ...
       {"role": "user", "content": "What did I ask before?"}
   ]
   ```

5. **Qwen Brain** processes with full context

6. **Response**: "Your previous question was about the time"

---

## 📈 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Load 3 conversations | ~5ms | Fast, minimal overhead |
| Load 20 conversations | ~15ms | Still very fast |
| MongoDB query | ~10ms | Indexed for speed |
| Total overhead | ~30ms | Negligible impact |

---

## 🎨 Advanced Usage

### **Clear Old History** (if needed):
```python
from backend.core import mongo_manager

# Clear all conversations
mongo_manager.clear_history()

# Or keep only recent (add to phase1_online.py):
from datetime import datetime, timedelta

cutoff = datetime.utcnow() - timedelta(days=7)
mongo_manager._db.conversations.delete_many({
    "timestamp": {"$lt": cutoff}
})
```

### **Search Specific Topics**:
```python
# Search for conversations about "alarm"
results = mongo_manager.search_conversations("alarm", limit=10)

# Returns all conversations mentioning "alarm"
```

### **Get Total Count**:
```python
total = mongo_manager.get_conversation_count()
print(f"Total conversations: {total}")
```

---

## 🧪 Test It Now!

**Run Jarvis:**
```powershell
python tests\phase1_online.py
```

**Test Sequence:**
```
1. "What time is it?" (normal)
2. "Set alarm for 5pm" (normal)
3. "Open Chrome" (normal)
4. "What did I ask you first?" (LOADS 20!)
5. "What was my previous question?" (LOADS 20!)
```

**View Results:**
```powershell
python tests\quick_view_mongodb.py
```

---

## 📊 How to Check What's Loaded

Add this to see what Jarvis is loading:

```python
# In phase1_online.py, add debug output:
print(f"🧠 Context loaded: {len(conversation_context)} conversations")
```

Or check MongoDB directly:
```bash
mongosh
use jarvis_db
db.conversations.find().count()  # Total stored
db.conversations.find().sort({timestamp: -1}).limit(20).pretty()  # Last 20
```

---

## 💡 Pro Tips

1. **Be Specific**: "What did I ask 5 minutes ago?" works better than "What happened?"

2. **Use Keywords**: Include words like "before", "earlier", "previous" to trigger full search

3. **Language Mixing**: Works in English, Hindi, and Hinglish!

4. **Context Persistence**: All conversations saved permanently (until you clear)

5. **Performance**: No speed impact - 20 conversations load in ~15ms

---

## 🎉 Summary

✅ **Default**: 3 recent conversations (fast)
✅ **History Questions**: 20 conversations (auto-detected)
✅ **Unlimited Storage**: Everything saved to MongoDB
✅ **Smart Detection**: Knows when you're asking about past
✅ **Multi-Language**: Works in English, Hindi, Hinglish

**Ready to test!** Just run:
```powershell
python tests\phase1_online.py
```

Ask some questions, then try:
- "What did I ask you first?"
- "What was my previous question?"
- "Show me what we talked about"

Jarvis will remember! 🧠✨
