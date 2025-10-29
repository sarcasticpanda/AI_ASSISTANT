"""
Test Piper TTS directly to understand its API
"""
import tempfile

print("\n" + "="*70)
print("  TESTING PIPER TTS DIRECTLY")
print("="*70 + "\n")

try:
    import piper
    print("✓ Piper TTS imported successfully")
    print(f"  Version: {piper.__version__ if hasattr(piper, '__version__') else 'Unknown'}")
    print()
    
    # Check what's available in piper module
    print("Available in piper module:")
    for item in dir(piper):
        if not item.startswith('_'):
            print(f"  - {item}")
    print()
    
    # Try to use Piper
    print("Attempting to synthesize speech...")
    
    # Piper-tts uses a different API - it's a command-line tool wrapped in Python
    # We need to use subprocess or find the correct API
    
    from piper.voice import PiperVoice
    print("✓ PiperVoice class found")
    
    # Test synthesis
    text = "Hello, I am Jarvis. Testing Piper TTS."
    print(f"Text: '{text}'")
    print()
    
    # Try to load voice
    print("Loading voice: en_US-lessac-medium...")
    try:
        voice = PiperVoice.load("en_US-lessac-medium")
        print("✓ Voice loaded!")
        
        # Synthesize
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        output_path = temp_file.name
        temp_file.close()
        
        with open(output_path, 'wb') as f:
            voice.synthesize(text, f)
        
        print(f"✓ Audio generated: {output_path}")
        
        import subprocess
        subprocess.run(['start', output_path], shell=True)
        print("\n✨ Piper TTS works! Playing audio...")
        
    except FileNotFoundError as e:
        print(f"✗ Voice model not found: {e}")
        print("\nPiper needs voice models to be downloaded separately.")
        print("Voice files should be in one of these locations:")
        print("  - Current directory")
        print("  - ~/.local/share/piper/voices/")
        print("  - /usr/share/piper/voices/")
        print()
        print("Download voice from:")
        print("  https://github.com/rhasspy/piper/releases/")
        print("  Look for: en_US-lessac-medium.onnx")
        
except ImportError as e:
    print(f"✗ Failed to import Piper: {e}")
    print("\nPiper TTS might not be installed correctly.")
    print("Try: pip install piper-tts")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
