# 🎯 JARVIS SKILLS - COMPLETE TEST GUIDE

## 📦 Installed Libraries (All Ready!)

```
✅ pywhatkit        - YouTube, WhatsApp automation
✅ pytz             - Timezone support
✅ requests         - Web requests, APIs
✅ beautifulsoup4   - Web scraping
✅ APScheduler      - Alarms and timers
✅ playsound        - Play alarm sounds
✅ pyautogui        - App control, mouse/keyboard
✅ webbrowser       - Open URLs
✅ psutil           - System info
```

---

## 🧪 SKILLS TESTING CHECKLIST

### **1. Time & Date Commands**

| Command | Expected Result | Test Status |
|---------|----------------|-------------|
| "What time is it?" | Current time in 12-hour format | ⬜ |
| "Tell me the time" | Current time | ⬜ |
| "What's today's date?" | Current date | ⬜ |
| "What day is it?" | Day of week + date | ⬜ |

**Example Responses:**
- "It's 3:45 PM on Tuesday, November 5, 2025"
- "The time is 15:45"

---

### **2. Alarm & Timer Commands**

| Command | Expected Result | Test Status |
|---------|----------------|-------------|
| "Set alarm for 5pm" | Alarm scheduled for 17:00 | ⬜ |
| "Set alarm for 10:30 AM tomorrow" | Alarm for next day 10:30 | ⬜ |
| "Wake me up at 6 AM" | Alarm for 6:00 AM | ⬜ |
| "Remind me in 5 minutes" | Timer for 5 minutes | ⬜ |
| "Set timer for 10 seconds" | 10-second countdown | ⬜ |
| "Show my alarms" | List all scheduled alarms | ⬜ |
| "Cancel alarm 1" | Delete specific alarm | ⬜ |

**MongoDB Storage:**
- Collection: `alarms`
- Fields: `time`, `message`, `status`, `created_at`

---

### **3. Open Application Commands**

| Command | Expected App | Test Status |
|---------|-------------|-------------|
| "Open Chrome" | Google Chrome browser | ⬜ |
| "Open Firefox" | Firefox browser | ⬜ |
| "Open Edge" | Microsoft Edge | ⬜ |
| "Open Notepad" | Notepad text editor | ⬜ |
| "Open Calculator" | Windows Calculator | ⬜ |
| "Open File Explorer" | Windows Explorer | ⬜ |
| "Open Word" | Microsoft Word | ⬜ |
| "Open Excel" | Microsoft Excel | ⬜ |
| "Open PowerPoint" | PowerPoint | ⬜ |
| "Open VS Code" | Visual Studio Code | ⬜ |
| "Open Spotify" | Spotify app | ⬜ |
| "Open Discord" | Discord app | ⬜ |

**MongoDB Storage:**
- Collection: `app_commands`
- Fields: `command_type`, `target`, `success`, `timestamp`

---

### **4. Open Website Commands**

| Command | Expected URL | Test Status |
|---------|-------------|-------------|
| "Open YouTube" | https://youtube.com | ⬜ |
| "Open Google" | https://google.com | ⬜ |
| "Open Gmail" | https://gmail.com | ⬜ |
| "Open GitHub" | https://github.com | ⬜ |
| "Open Twitter" | https://twitter.com | ⬜ |
| "Open Instagram" | https://instagram.com | ⬜ |
| "Open Facebook" | https://facebook.com | ⬜ |
| "Open LinkedIn" | https://linkedin.com | ⬜ |
| "Open Reddit" | https://reddit.com | ⬜ |
| "Open Stack Overflow" | https://stackoverflow.com | ⬜ |

---

### **5. YouTube Commands** (Using pywhatkit)

| Command | Expected Result | Test Status |
|---------|----------------|-------------|
| "Play despacito on YouTube" | Opens YouTube with search | ⬜ |
| "Search Python tutorial on YouTube" | YouTube search results | ⬜ |
| "Show me cat videos" | YouTube cat videos | ⬜ |

---

### **6. File Operations Commands**

| Command | Expected Result | Test Status |
|---------|----------------|-------------|
| "Open my documents" | Opens Documents folder | ⬜ |
| "Open downloads folder" | Opens Downloads | ⬜ |
| "Open desktop" | Opens Desktop folder | ⬜ |
| "Create a file called test.txt" | Creates text file | ⬜ |
| "Create folder called MyFolder" | Creates directory | ⬜ |

---

### **7. System Info Commands**

| Command | Expected Result | Test Status |
|---------|----------------|-------------|
| "What's my battery level?" | Battery percentage | ⬜ |
| "How much RAM am I using?" | Memory usage stats | ⬜ |
| "What's my CPU usage?" | CPU percentage | ⬜ |
| "Check system status" | Full system report | ⬜ |

---

### **8. Email Commands** (Gmail API)

| Command | Expected Result | Test Status |
|---------|----------------|-------------|
| "Read my latest email" | Shows newest email | ⬜ |
| "Check my inbox" | Email count/summary | ⬜ |
| "Send email to John" | Compose email | ⬜ |

**Note:** Requires Gmail API credentials in `.env`

---

### **9. PDF Summarization** (Phase 2)

| Command | Expected Result | Test Status |
|---------|----------------|-------------|
| "Summarize this PDF" | PDF text extraction | ⬜ |
| "Read page 5 of document.pdf" | Specific page read | ⬜ |

**MongoDB Storage:**
- Collection: `pdf_summaries`
- Fields: `filename`, `summary`, `page_count`, `uploaded_at`

---

### **10. Weather Commands** (Optional - Needs API)

| Command | Expected Result | Test Status |
|---------|----------------|-------------|
| "What's the weather?" | Current weather | ⬜ |
| "Weather in Mumbai" | City-specific weather | ⬜ |

**Requires:** OpenWeatherMap API key in `.env`

---

## 🔧 **How to Test Each Skill**

### **Step 1: Run Voice Assistant**
```bash
python tests\phase1_online.py
```

### **Step 2: Test Each Command**
- Press ENTER to start recording
- Speak the command clearly
- Wait for Jarvis response
- Mark ✅ or ❌ in Test Status column

### **Step 3: Verify in MongoDB**
```bash
python tests\quick_view_mongodb.py
```

Check that commands are saved in appropriate collections:
- `conversations` - All interactions
- `app_commands` - App/website opens
- `alarms` - Scheduled alarms
- `command_analytics` - Usage statistics

---

## 📊 **Expected Intents**

Each command should be classified with correct intent:

| Command Type | Intent |
|-------------|--------|
| "What time is it?" | `time` |
| "Set alarm for 5pm" | `alarm` |
| "Open Chrome" | `open_app` |
| "Open YouTube" | `open_website` |
| "Play song on YouTube" | `youtube` |
| "Read my email" | `email` |
| "What's the weather?" | `weather` |
| General questions | `chat` |

---

## 🐛 **Common Issues & Fixes**

### **Issue 1: App Not Opening**
```
Error: Application not found
```
**Fix:** Check app installation path in `backend/skills/open_app.py`

### **Issue 2: Permission Denied**
```
Error: Access denied to file/folder
```
**Fix:** Run as Administrator (Windows)

### **Issue 3: Alarm Not Triggering**
```
APScheduler not installed
```
**Fix:** Already installed! ✅

### **Issue 4: Browser Opens Wrong Tab**
```
webbrowser opens default browser
```
**Fix:** Set default browser in Windows settings

---

## 📝 **MongoDB Verification Queries**

After testing, run these in MongoDB Compass:

### **1. View All App Commands**
```javascript
// In app_commands collection
{ "command_type": "open_app" }
```

### **2. View All Alarms**
```javascript
// In alarms collection
{ "status": "scheduled" }
```

### **3. Find Slow Commands**
```javascript
// In conversations collection
{ "performance.total_time": { "$gt": 5 } }
```

### **4. Count Commands by Intent**
```javascript
// In command_analytics collection
db.command_analytics.aggregate([
  { $group: { _id: "$intent", count: { $sum: 1 } } }
])
```

---

## 🎯 **Success Criteria**

✅ **All skills working** when:
1. **Time/Date** - Returns correct current time
2. **Alarms** - Saves to MongoDB, triggers at scheduled time
3. **Open Apps** - Launches correct application
4. **Open Websites** - Opens in default browser
5. **YouTube** - Searches and plays videos
6. **Files** - Creates/opens files and folders
7. **System Info** - Returns accurate stats
8. **MongoDB** - All commands logged with correct intent

---

## 🚀 **Next Steps After Testing**

1. ✅ Fix any failed tests
2. ✅ Add missing app paths for your system
3. ✅ Configure Gmail API for email skills
4. ✅ Add weather API key for weather commands
5. ✅ Test interrupt feature (Press 'S' during speech)
6. ✅ Test continuous loop (Press ENTER for next question)
7. ✅ Verify MongoDB data in Compass
8. ✅ Ready for Electron app integration!

---

## 📞 **Test Commands Summary**

**Quick Test Sequence (5 minutes):**
1. "What time is it?"
2. "Set alarm for 5 minutes from now"
3. "Open Chrome"
4. "Open YouTube"
5. "What's my battery level?"
6. Press 'S' to interrupt speech
7. Check MongoDB: `python tests\quick_view_mongodb.py`

**Full Test (15 minutes):**
- Test all commands in each category
- Verify MongoDB storage
- Check interrupt and loop features
- Test language detection (speak in Hindi)

---

**Ready to test!** 🎉

Run: `python tests\phase1_online.py`

Then speak each command and mark the results in this guide!
