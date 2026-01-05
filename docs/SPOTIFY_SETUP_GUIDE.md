# 🎵 Spotify API Setup Guide

## Why Use Spotify API?

**Current Problem:**
- Window focusing is unreliable
- Keyboard automation (pressing Enter) is flaky
- Sometimes types in wrong window

**Spotify API Solution:**
- ✅ Direct playback control (like Alexa/Google Home)
- ✅ 100% reliable - no window focusing needed
- ✅ Can control playback: play, pause, skip, volume
- ✅ Get currently playing track
- ✅ Search tracks and play instantly

---

## Setup Steps (5 minutes)

### Step 1: Create Spotify Developer Account

1. Go to: https://developer.spotify.com/dashboard
2. Log in with your Spotify account (same one you use on your PC)
3. Click **"Create an App"**
4. Fill in:
   - **App name**: Jarvis Assistant
   - **App description**: Voice assistant for music playback
   - **Redirect URI**: `http://localhost:8888/callback`
5. Accept terms and click **"Create"**

### Step 2: Get API Credentials

1. Click on your new app
2. Click **"Settings"**
3. You'll see:
   - **Client ID**: (copy this)
   - **Client Secret**: (click "View client secret", copy this)

### Step 3: Add to .env File

Open `c:\Users\Lunar Panda\3-Main\assistant\.env` and add:

```env
# Spotify API (for music playback)
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

### Step 4: Install Spotipy

```cmd
pip install spotipy
```

### Step 5: First-Time Authorization (one-time)

Run the setup script:
```cmd
python tests\spotify_auth_setup.py
```

This will:
1. Open browser to Spotify login
2. You authorize the app
3. Get redirected to localhost (URL will fail, that's OK)
4. Copy the FULL URL from browser
5. Paste it into the terminal
6. Done! Token saved for future use

---

## Requirements

- **Spotify Account**: Free or Premium (both work)
- **Spotify Desktop App**: Must be open and logged in
- **Internet**: Needed for API calls

---

## Features You'll Get

### Direct Playback
```python
"play shape of you on spotify"
→ Instantly starts playing (no window focusing!)
```

### Playback Control
```python
"pause spotify"
"resume spotify"
"skip song"
"previous song"
"volume 50"
```

### Currently Playing
```python
"what's playing on spotify"
→ "Currently playing: Shape of You by Ed Sheeran"
```

### Queue Management
```python
"add despacito to queue"
"clear queue"
```

---

## How It Works

```
Voice Command: "play tears on spotify"
       ↓
[Spotipy] → Spotify Web API
       ↓
Spotify App on your PC → Starts playing immediately
```

**No window focusing, no keyboard automation, no timing issues!**

---

## Next Steps

After setup is complete, I'll update `music_player.py` to use Spotipy instead of the unreliable window focusing method.

Your Spotify will work **exactly like Alexa/Google Home** - instant, reliable, professional! 🎵
