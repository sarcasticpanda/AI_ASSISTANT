"""
Spotify Auto-Play Debug Test
Tests different approaches to verify what works
"""

import sys
import os
import time
sys.path.insert(0, r'c:\Users\Lunar Panda\3-Main\assistant')

from backend.skills.music_player import play_on_spotify

def check_dependencies():
    """Check if required libraries are installed"""
    print("\n" + "="*70)
    print("🔍 CHECKING DEPENDENCIES")
    print("="*70)
    
    deps = {
        'pyautogui': False,
        'pygetwindow': False,
    }
    
    try:
        import pyautogui
        deps['pyautogui'] = True
        print("✅ pyautogui installed")
    except:
        print("❌ pyautogui NOT installed")
    
    try:
        import pygetwindow
        deps['pygetwindow'] = True
        print("✅ pygetwindow installed")
    except:
        print("❌ pygetwindow NOT installed")
    
    if not all(deps.values()):
        print("\n⚠️  Missing dependencies! Install with:")
        if not deps['pyautogui']:
            print("   pip install pyautogui")
        if not deps['pygetwindow']:
            print("   pip install pygetwindow")
        print()
    
    return all(deps.values())


def test_basic_spotify_open():
    """Test 1: Just open Spotify (no auto-play)"""
    print("\n" + "="*70)
    print("TEST 1: Basic Spotify Open")
    print("="*70)
    print("\n📌 This test just opens Spotify search - NO auto-play")
    print("   You should see Spotify open with search results")
    print("   You'll need to manually press Enter to play\n")
    
    input("Press ENTER to start test...")
    
    import subprocess
    import urllib.parse
    
    song = "shape of you"
    query = urllib.parse.quote(song)
    spotify_uri = f"spotify:search:{query}"
    
    print(f"\n🎵 Opening Spotify: {song}")
    subprocess.Popen(['cmd', '/c', 'start', '', spotify_uri], shell=True)
    
    print("✅ Spotify should be opening now...")
    time.sleep(3)
    
    response = input("\n❓ Did Spotify open with search results? (y/n): ").lower()
    if response == 'y':
        print("✅ Basic open works!")
        return True
    else:
        print("❌ Basic open failed - Spotify might not be installed")
        return False


def test_window_detection():
    """Test 2: Check if we can detect Spotify window"""
    print("\n" + "="*70)
    print("TEST 2: Window Detection")
    print("="*70)
    print("\n📌 This test checks if we can find Spotify window")
    print("   Make sure Spotify is already open!\n")
    
    input("Press ENTER to start test...")
    
    try:
        import pygetwindow as gw
        
        print("\n🔍 Searching for Spotify window...")
        all_windows = gw.getAllWindows()
        
        print(f"\nFound {len(all_windows)} total windows")
        
        # Try different patterns
        patterns = ['Spotify Premium', 'Spotify Free', 'Spotify']
        found = False
        
        for pattern in patterns:
            windows = gw.getWindowsWithTitle(pattern)
            if windows:
                print(f"✅ Found window with '{pattern}': {windows[0].title}")
                found = True
                break
        
        if not found:
            print("❌ No Spotify window found")
            print("\n📋 All window titles containing 'Spot' or 'Music':")
            for w in all_windows:
                if 'spot' in w.title.lower() or 'music' in w.title.lower():
                    print(f"   - {w.title}")
        
        return found
        
    except ImportError:
        print("❌ pygetwindow not installed!")
        print("   Install: pip install pygetwindow")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_full_autoplay():
    """Test 3: Full auto-play test with timing details"""
    print("\n" + "="*70)
    print("TEST 3: Full Auto-Play")
    print("="*70)
    print("\n📌 This test does the complete auto-play flow")
    print("   Opens Spotify → Waits → Focuses → Presses Enter\n")
    
    song = input("Enter song name (or press ENTER for 'tears'): ").strip()
    if not song:
        song = "tears"
    
    print(f"\n🎵 Testing auto-play for: {song}")
    print("\n⏱️  Timeline:")
    print("   0.0s - Opening Spotify...")
    
    result = play_on_spotify(song)
    
    print(f"\n📊 Result: {result}")
    
    time.sleep(2)
    response = input("\n❓ Did the song start playing automatically? (y/n): ").lower()
    
    if response == 'y':
        print("✅ AUTO-PLAY WORKS!")
        return True
    else:
        print("❌ Auto-play failed")
        print("\n🔧 Possible issues:")
        print("   1. Timing too fast - Spotify didn't finish loading")
        print("   2. Window focus failed - Enter pressed wrong window")
        print("   3. Spotify UI changed - Enter doesn't play anymore")
        return False


def test_multiple_songs():
    """Test 4: Test with multiple songs"""
    print("\n" + "="*70)
    print("TEST 4: Multiple Songs")
    print("="*70)
    print("\n📌 Tests 3 different songs to verify consistency\n")
    
    songs = ["shape of you", "despacito", "bohemian rhapsody"]
    
    input("Press ENTER to start (will take ~30 seconds)...")
    
    results = []
    for i, song in enumerate(songs, 1):
        print(f"\n[{i}/3] Testing: {song}")
        result = play_on_spotify(song)
        print(f"   Result: {result}")
        
        if i < len(songs):
            print("   Waiting 8 seconds before next song...")
            time.sleep(8)
        
        response = input(f"   Did '{song}' play? (y/n): ").lower()
        results.append(response == 'y')
    
    success_rate = (sum(results) / len(results)) * 100
    print(f"\n📊 Success Rate: {success_rate:.0f}% ({sum(results)}/{len(results)} songs played)")
    
    return success_rate >= 66  # At least 2/3 should work


def main():
    print("="*70)
    print("🎵 SPOTIFY AUTO-PLAY DEBUG SUITE 🎵")
    print("="*70)
    
    # Check dependencies first
    if not check_dependencies():
        choice = input("\n⚠️  Continue anyway? (y/n): ").lower()
        if choice != 'y':
            print("Exiting...")
            return
    
    print("\n📋 Available Tests:")
    print("   1. Basic Spotify Open (no auto-play)")
    print("   2. Window Detection Test")
    print("   3. Full Auto-Play Test (single song)")
    print("   4. Multiple Songs Test (3 songs)")
    print("   5. Run All Tests")
    
    choice = input("\nSelect test (1-5): ").strip()
    
    if choice == '1':
        test_basic_spotify_open()
    elif choice == '2':
        test_window_detection()
    elif choice == '3':
        test_full_autoplay()
    elif choice == '4':
        test_multiple_songs()
    elif choice == '5':
        print("\n🔄 Running all tests...\n")
        t1 = test_basic_spotify_open()
        t2 = test_window_detection()
        t3 = test_full_autoplay()
        t4 = test_multiple_songs()
        
        print("\n" + "="*70)
        print("📊 FINAL RESULTS")
        print("="*70)
        print(f"Basic Open:        {'✅ PASS' if t1 else '❌ FAIL'}")
        print(f"Window Detection:  {'✅ PASS' if t2 else '❌ FAIL'}")
        print(f"Full Auto-Play:    {'✅ PASS' if t3 else '❌ FAIL'}")
        print(f"Multiple Songs:    {'✅ PASS' if t4 else '❌ FAIL'}")
        
        if all([t1, t2, t3, t4]):
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print("\n⚠️  Some tests failed - see above for details")
    else:
        print("Invalid choice!")
    
    print("\n" + "="*70)
    print("Test complete!")
    print("="*70)


if __name__ == "__main__":
    main()
