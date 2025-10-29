# 🧪 Jarvis Assistant - Test Suite

This folder contains all test scripts for validating Jarvis components.

---

## 📋 **Test Files**

### **1. test_api_keys.py** 🔑
**Purpose:** Validate API credentials  
**Tests:**
- OpenRouter API key (Qwen LLM)
- Groq API key (Whisper STT)

**Run:** `python tests\test_api_keys.py`

---

### **2. test_endpoints.py** 🌐
**Purpose:** Test all FastAPI backend endpoints  
**Tests:**
- GET `/` - Root endpoint
- GET `/health` - Health check + MongoDB + LLM status
- POST `/speak` - Text-to-Speech (online & offline)
- GET `/history` - Conversation history

**Run:** `python tests\test_endpoints.py`  
**Requires:** Backend server running (`python backend\app.py`)

---

### **3. test_mongodb.py** 💾
**Purpose:** Comprehensive MongoDB testing  
**Tests:**
- Connection status
- Database operations (CRUD)
- Collections & indexes
- Database statistics

**Run:** `python tests\test_mongodb.py`

---

### **4. test_qwen.py** 🤖
**Purpose:** Test Qwen LLM responses  
**Tests:**
- OpenRouter API connection
- Qwen model responses
- Multiple question types (factual, creative, math)

**Run:** `python tests\test_qwen.py`

---

### **5. test_tts.py** 🔊
**Purpose:** Test Text-to-Speech systems  
**Tests:**
- Online TTS (gTTS - Google)
- Offline TTS (Coqui TTS)
- Audio file generation
- Audio playback

**Run:** `python tests\test_tts.py`

---

### **6. test_stt.py** 🎤
**Purpose:** Test Speech-to-Text systems  
**Tests:**
- Online STT (Groq Whisper API)
- Offline STT (faster-whisper)
- Audio transcription accuracy

**Run:** `python tests\test_stt.py`

---

### **7. test_audio.py** 🎵
**Purpose:** Audio utilities testing  
**Tests:**
- Audio file operations
- Format conversions
- Playback functionality

**Run:** `python tests\test_audio.py`

---

## 🚀 **Quick Test All**

To run all tests in sequence:

```cmd
cd C:\Users\Lunar Panda\3-Main\assistant
venv\Scripts\activate

python tests\test_api_keys.py
python tests\test_mongodb.py
python tests\test_qwen.py
python tests\test_tts.py
python tests\test_stt.py
python tests\test_endpoints.py
```

---

## 📊 **Test Status**

| Test | Status | Notes |
|------|--------|-------|
| API Keys | ✅ PASS | Both OpenRouter & Groq working |
| Endpoints | ✅ PASS | All 5 endpoints responding |
| MongoDB | ✅ PASS | Connected, CRUD working |
| Qwen LLM | ✅ PASS | Responses accurate & fast |
| TTS Online | ✅ PASS | gTTS generating audio |
| TTS Offline | ⏳ PENDING | Coqui TTS installed, needs fix |
| STT Online | ⏳ PENDING | Groq API ready, needs test |
| STT Offline | ⏳ PENDING | faster-whisper ready, needs test |

---

## ⚙️ **Prerequisites**

Before running tests, ensure:

1. **Virtual environment activated:**
   ```cmd
   venv\Scripts\activate
   ```

2. **Backend server running** (for endpoint tests):
   ```cmd
   python backend\app.py
   ```

3. **Environment variables set** in `backend/.env`:
   - `OPENROUTER_API_KEY`
   - `GROQ_API_KEY`
   - `MONGO_URI`

4. **MongoDB running:**
   - Check: `net start | findstr MongoDB`
   - Start: `net start MongoDB`

---

## 🐛 **Troubleshooting**

### **No audio playing?**
Audio files are created in temp folder. To play manually:
```cmd
start C:\Users\LUNARP~1\AppData\Local\Temp\jarvis_tts_*.mp3
```

### **MongoDB connection failed?**
```cmd
REM Check if MongoDB is running
sc query MongoDB

REM Start MongoDB
net start MongoDB
```

### **Import errors?**
Make sure you're in the project root and venv is activated:
```cmd
cd C:\Users\Lunar Panda\3-Main\assistant
venv\Scripts\activate
```

---

## 📝 **Adding New Tests**

When creating new test files:

1. Name them `test_*.py`
2. Use colorama for colored output
3. Include clear success/error messages
4. Add entry to this README
5. Test with venv activated

---

**Last Updated:** October 28, 2025  
**Maintainer:** Jarvis Development Team
