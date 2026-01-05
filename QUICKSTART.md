# 🎙️ Jarvis Voice Assistant - Quick Start

## 🚀 ONE-COMMAND SETUP

```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Run setup script
.\setup_professional.ps1

# 3. Run Jarvis
python tests\phase1_professional.py
```

---

## ✅ What This Does

**Installs**:
- `webrtcvad` - Professional voice detection (Google Meet uses this)
- `noisereduce` - Removes fan/AC/background noise
- `pydub` - Normalizes audio volume
- `numpy` - Array processing for audio

**Fixes**:
- ✅ "Listening forever" issue → Auto-stops after 600ms silence
- ✅ Fan noise triggering → Noise reduction removes it
- ✅ Fluctuating energy → WebRTC VAD ignores background noise
- ✅ Inconsistent volume → Audio normalization

---

## 📖 Full Documentation

See **[FINAL_SETUP_GUIDE.md](docs/FINAL_SETUP_GUIDE.md)** for:
- Complete technical explanation
- Troubleshooting guide
- How WebRTC VAD works
- Environment setup
- API key configuration
- Future roadmap

---

## 🎯 Quick Test

```powershell
python tests\phase1_professional.py
```

1. Press ENTER when ready
2. Say: **"What time is it?"**
3. System auto-detects speech (300ms)
4. System auto-stops when you stop (600ms)
5. Jarvis responds!

---

## 🔧 Requirements

- **Python 3.10+**
- **Virtual Environment** (venv)
- **MongoDB** (running locally)
- **Internet** (for Groq STT + Qwen + Edge TTS)
- **API Keys** in `backend/.env`:
  - `GROQ_API_KEY`
  - `OPENROUTER_API_KEY`

---

## 📊 Performance

- **STT**: 1-2 seconds (Groq Whisper)
- **Brain**: 1-10 seconds (Qwen AI)
- **TTS**: 3-5 seconds (Edge TTS)
- **Total**: 5-20 seconds per conversation

---

## 🐛 Issues?

1. **Check venv is activated**: `(venv)` should appear in prompt
2. **Check packages installed**: Run `pip list | grep webrtcvad`
3. **Check API keys**: Verify `backend/.env` file
4. **Check MongoDB**: Run `mongod` service
5. **See full guide**: Read `docs/FINAL_SETUP_GUIDE.md`

---

**Status**: ✅ Production Ready  
**Last Updated**: October 29, 2025  
**Version**: 1.0 (Professional with WebRTC VAD)
