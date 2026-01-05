"""
Test Spotify API Integration
"""

import sys
import os
sys.path.insert(0, r'c:\Users\Lunar Panda\3-Main\assistant')

# Load environment variables
from dotenv import load_dotenv
load_dotenv(r'c:\Users\Lunar Panda\3-Main\assistant\backend\.env')

print("\n" + "="*70)
print("🎵 SPOTIFY API TEST")
print("="*70)

# Check credentials
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

if not client_id or not client_secret:
    print("\n❌ Spotify credentials not found in .env file")
    sys.exit(1)

print(f"\n✅ Credentials loaded:")
print(f"   Client ID: {client_id[:20]}...")
print(f"   Client Secret: {client_secret[:20]}...")

print("\n⚠️  REQUIREMENTS:")
print("   1. Spotify desktop app must be OPEN")
print("   2. You must be logged in to Spotify")
print("   3. Browser will open for authorization (first time only)")

input("\nPress ENTER to continue...")

print("\n🔧 Setting up Spotify API...")

from backend.skills.spotify_api import get_spotify_player

player = get_spotify_player()

if not player:
    print("\n❌ Spotify API authentication failed")
    print("\n� Make sure:")
    print("   1. Spotify app is OPEN and logged in")
    print("   2. You completed the browser authorization")
    print("   3. Redirect URI matches: http://127.0.0.1:8888/callback")
    sys.exit(1)

print("✅ Spotify API authenticated!")

# Test search and play
print("\n🎵 Testing playback...")
song = input("Enter song name (or press ENTER for 'shape of you'): ").strip()
if not song:
    song = "shape of you"

print(f"\nSearching for: {song}")
result = player.search_and_play(song)

if result['success']:
    print(f"\n✅ SUCCESS!")
    print(f"   Playing: {result.get('track', 'Unknown')}")
    print(f"   By: {result.get('artist', 'Unknown')}")
    print(f"\n🎉 Spotify API working perfectly!")
    print(f"   Now say: 'play {song} on spotify' in voice assistant")
else:
    print(f"\n❌ FAILED: {result['message']}")
    
    if "No active Spotify devices" in result['message']:
        print("\n💡 FIX: Open Spotify desktop app first, then try again")
    elif "No results found" in result['message']:
        print("\n💡 FIX: Try a different song name")

print("\n" + "="*70)
