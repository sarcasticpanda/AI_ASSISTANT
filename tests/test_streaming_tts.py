"""
Quick test for streaming TTS functionality
Tests sentence-by-sentence audio generation and playback
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core import tts_streaming

def test_sentence_splitting():
    """Test sentence splitting for different languages"""
    print("\n" + "="*70)
    print("🧪 TEST 1: Sentence Splitting")
    print("="*70)
    
    # English
    text_en = "Hello! How are you doing today? I hope you're having a great time. This is amazing."
    sentences_en = tts_streaming.split_into_sentences(text_en)
    print(f"\n📝 English text: {text_en}")
    print(f"✂️  Split into {len(sentences_en)} sentences:")
    for i, s in enumerate(sentences_en, 1):
        print(f"   {i}. {s}")
    
    # Hindi (Devanagari)
    text_hi = "नमस्ते। आप कैसे हैं? मुझे आशा है कि आपका दिन अच्छा जा रहा है।"
    sentences_hi = tts_streaming.split_into_sentences(text_hi)
    print(f"\n📝 Hindi text: {text_hi}")
    print(f"✂️  Split into {len(sentences_hi)} sentences:")
    for i, s in enumerate(sentences_hi, 1):
        print(f"   {i}. {s}")
    
    # Hinglish
    text_mixed = "Hello! मैं Jarvis हूँ। How can I help you today? क्या मैं कुछ कर सकता हूँ?"
    sentences_mixed = tts_streaming.split_into_sentences(text_mixed)
    print(f"\n📝 Hinglish text: {text_mixed}")
    print(f"✂️  Split into {len(sentences_mixed)} sentences:")
    for i, s in enumerate(sentences_mixed, 1):
        print(f"   {i}. {s}")


def test_streaming_playback():
    """Test actual streaming TTS playback"""
    print("\n" + "="*70)
    print("🧪 TEST 2: Streaming TTS Playback")
    print("="*70)
    
    if not tts_streaming.is_available():
        print("❌ Streaming TTS not available!")
        print("   Install: pip install edge-tts pygame")
        return
    
    print("\n✅ Streaming TTS available!")
    
    # Test 1: Short response (English)
    print("\n" + "-"*70)
    print("Test 2.1: Short English Response")
    print("-"*70)
    
    text1 = "Hello! How are you? I'm doing great today."
    print(f"📝 Text: {text1}")
    print(f"🎵 Starting streaming playback...")
    
    start = time.time()
    total_time, sentence_count = tts_streaming.speak_streaming(text1, lang='en')
    elapsed = time.time() - start
    
    print(f"✅ Complete!")
    print(f"   Sentences: {sentence_count}")
    print(f"   Streaming time: {total_time:.2f}s")
    print(f"   Total time: {elapsed:.2f}s")
    
    time.sleep(1)
    
    # Test 2: Longer response (English)
    print("\n" + "-"*70)
    print("Test 2.2: Longer English Response")
    print("-"*70)
    
    text2 = "The current time is 1:09 PM on Wednesday, November 5th, 2025. It's a beautiful day outside. Would you like me to set an alarm for later?"
    print(f"📝 Text: {text2}")
    print(f"🎵 Starting streaming playback...")
    
    start = time.time()
    total_time, sentence_count = tts_streaming.speak_streaming(text2, lang='en')
    elapsed = time.time() - start
    
    print(f"✅ Complete!")
    print(f"   Sentences: {sentence_count}")
    print(f"   Streaming time: {total_time:.2f}s")
    print(f"   Total time: {elapsed:.2f}s")
    
    time.sleep(1)
    
    # Test 3: Hindi response
    print("\n" + "-"*70)
    print("Test 2.3: Hindi Response")
    print("-"*70)
    
    text3 = "नमस्ते। मैं Jarvis हूँ। मैं आपकी कैसे मदद कर सकता हूँ?"
    print(f"📝 Text: {text3}")
    print(f"🎵 Starting streaming playback...")
    
    start = time.time()
    total_time, sentence_count = tts_streaming.speak_streaming(text3, lang='hi')
    elapsed = time.time() - start
    
    print(f"✅ Complete!")
    print(f"   Sentences: {sentence_count}")
    print(f"   Streaming time: {total_time:.2f}s")
    print(f"   Total time: {elapsed:.2f}s")


def test_performance_comparison():
    """Compare streaming vs standard TTS"""
    print("\n" + "="*70)
    print("🧪 TEST 3: Performance Comparison (Streaming vs Standard)")
    print("="*70)
    
    if not tts_streaming.is_available():
        print("❌ Cannot run performance test - streaming not available")
        return
    
    from backend.core import tts_online
    
    text = "Quantum computing represents a paradigm shift in computational technology. Unlike classical computers that use bits, quantum computers use quantum bits or qubits. This allows them to perform certain calculations exponentially faster."
    
    print(f"\n📝 Test text ({len(text)} chars):")
    print(f"   {text}")
    
    # Test streaming
    print("\n" + "-"*70)
    print("🎵 Streaming TTS:")
    print("-"*70)
    
    start = time.time()
    stream_time, sentences = tts_streaming.speak_streaming(text, lang='en')
    total_stream = time.time() - start
    
    print(f"✅ Streaming: {sentences} sentences in {stream_time:.2f}s (total: {total_stream:.2f}s)")
    
    time.sleep(2)
    
    # Test standard
    print("\n" + "-"*70)
    print("🔊 Standard TTS:")
    print("-"*70)
    
    start = time.time()
    audio_path = tts_online.speak_online(text, lang='en')
    gen_time = time.time() - start
    
    if audio_path:
        tts_online.play_audio(audio_path)
        total_standard = time.time() - start
        
        print(f"✅ Standard: Generated in {gen_time:.2f}s, total: {total_standard:.2f}s")
        
        # Cleanup
        try:
            os.remove(audio_path)
        except:
            pass
        
        # Comparison
        print("\n" + "="*70)
        print("📊 PERFORMANCE COMPARISON")
        print("="*70)
        print(f"Streaming:  {total_stream:.2f}s")
        print(f"Standard:   {total_standard:.2f}s")
        improvement = ((total_standard - total_stream) / total_standard) * 100
        print(f"Improvement: {improvement:.1f}% faster!")
    else:
        print("❌ Standard TTS failed")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 STREAMING TTS TEST SUITE")
    print("="*70)
    
    try:
        # Run tests
        test_sentence_splitting()
        
        input("\n⏸️  Press ENTER to test streaming playback (audio will play)...")
        test_streaming_playback()
        
        input("\n⏸️  Press ENTER to run performance comparison...")
        test_performance_comparison()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETE!")
        print("="*70)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
