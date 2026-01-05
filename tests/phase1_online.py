"""
PHASE 1 - ONLINE VOICE ASSISTANT (COMPLETE)

Features:
✅ Auto noise calibration at startup
✅ Smart recording (silence detection, not fixed time)
✅ Groq STT (Whisper large-v3)
✅ Qwen Brain with follow-up detection
✅ Edge TTS Arjun voice
✅ All skills working (time, alarm, apps, email, etc.)
✅ MongoDB conversation storage
✅ Clean performance metrics
"""

import os
import sys
import wave
import pyaudio
import time
import struct
import threading
import msvcrt  # For keyboard interrupt detection on Windows
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
load_dotenv('backend/.env')

from backend.core import stt_online, brain, tts_manager, tts_online, mongo_manager

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Global thresholds (set by calibration)
SPEECH_THRESHOLD = 230
SILENCE_THRESHOLD = 150


# ============================================================================
# NOISE CALIBRATION
# ============================================================================

def auto_calibrate_noise(audio, duration=3):
    """
    Auto-calibrate microphone based on ambient noise.
    
    Returns:
        (speech_threshold, silence_threshold, environment)
    """
    print("\n" + "="*70)
    print("🎧 MICROPHONE CALIBRATION")
    print("="*70)
    print("\n⏳ Recording 3 seconds of ambient noise...")
    print("   Please stay SILENT...")
    
    import winsound
    winsound.Beep(800, 100)
    
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    frames = []
    total_chunks = int(RATE / CHUNK * duration)
    
    for i in range(total_chunks):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
        
        # Show progress
        if i % 5 == 0:
            progress = int((i / total_chunks) * 20)
            bar = "█" * progress + "░" * (20 - progress)
            print(f"\r   [{bar}] {int((i/total_chunks)*100)}%", end="", flush=True)
    
    print(f"\r   [{'█'*20}] 100%")
    stream.stop_stream()
    stream.close()
    
    # Advanced statistical analysis of ambient noise
    energies = []
    for frame in frames:
        samples = struct.unpack(f"{len(frame)//2}h", frame)
        energy = int((sum(s**2 for s in samples) / len(samples))**0.5)
        energies.append(energy)
    
    avg_energy = int(sum(energies) / len(energies))
    max_energy = max(energies)
    min_energy = min(energies)
    
    # Calculate standard deviation (noise variability)
    variance = sum((e - avg_energy) ** 2 for e in energies) / len(energies)
    std_dev = int(variance ** 0.5)
    
    # Noise floor = 95th percentile (2 standard deviations above mean)
    noise_floor = avg_energy + (2 * std_dev)
    
    # FIXED: High threshold to ignore fluctuating fan noise (10-200)
    # If fan noise fluctuates 10-200, speech needs to be 400+ to be detected clearly
    # Using PEAK noise (max_energy) instead of average to handle fluctuations
    
    # Calculate robust threshold based on MAXIMUM noise seen during calibration
    peak_noise = max_energy  # Highest noise spike seen
    
    if avg_energy < 15:  # Very quiet (library, night)
        # Use multiplier of peak noise to avoid false triggers
        speech_threshold = max(peak_noise * 2.5, 80)  # At least 2.5x peak noise, min 80
        silence_threshold = max(peak_noise * 1.2, 30)
        min_speech_chunks = 5  # ~0.3 seconds
        environment = "LIBRARY (Very Quiet)"
        
    elif avg_energy < 50:  # Quiet room with fan (your case: avg~20-60, peaks~200)
        # Fan fluctuates 10-200, so speech needs to be > peak noise consistently
        # Use lower multiplier so normal speech works (not shouting)
        speech_threshold = max(peak_noise * 1.5, 180)  # 1.5x peak noise, minimum 180
        silence_threshold = max(peak_noise * 1.2, 90)  # 1.2x peak noise
        min_speech_chunks = 3  # ~0.2 seconds of sustained speech
        environment = "QUIET with FAN NOISE"
        
        # Show helpful tip for user
        print(f"\n💡 TIP: Your fan noise peaks at {peak_noise}. Speak at energy > {max(peak_noise * 1.5, 180)} to trigger.")
        print(f"   Try speaking CLOSER to the microphone or slightly LOUDER.\n")
        
    elif avg_energy < 100:  # Normal room (PC fan, AC)
        speech_threshold = max(peak_noise * 1.8, 300)  # 1.8x peak noise, min 300
        silence_threshold = max(peak_noise * 1.3, 120)
        min_speech_chunks = 4  # ~0.25 seconds (reduced from 8)
        environment = "NORMAL (PC/AC)"
        
    else:  # Noisy (busy office, classroom, street)
        speech_threshold = max(peak_noise * 1.5, 400)  # 1.5x peak noise, min 400
        silence_threshold = max(peak_noise * 1.3, 150)
        min_speech_chunks = 6  # ~0.4 seconds (reduced from 10)
        environment = "NOISY (Classroom/Office)"
    
    snr = f"{speech_threshold}+ for speech vs {peak_noise} peak noise"
    
    print(f"\n\n✅ Calibration complete!")
    print(f"   Environment: {environment}")
    print(f"   Ambient avg: {avg_energy} | Range: {min_energy}-{max_energy}")
    print(f"   Noise floor (95%): {noise_floor} | Variability: ±{std_dev}")
    print(f"   ─" * 35)
    print(f"   Speech threshold: {speech_threshold} (START recording)")
    print(f"   Silence threshold: {silence_threshold} (STOP recording)")
    print(f"   Min speech time: {min_speech_chunks * 0.064:.1f}s continuous")
    print(f"   Target SNR: {snr}")
    print("="*70 + "\n")
    
    winsound.Beep(1000, 100)
    
    return speech_threshold, silence_threshold, min_speech_chunks, environment


# ============================================================================
# SMART RECORDING WITH VAD
# ============================================================================

def record_command(audio, speech_threshold, silence_threshold, min_speech_chunks):
    """
    Record voice command with advanced VAD.
    Requires sustained speech to avoid false triggers.
    
    Returns:
        audio_file: Path to saved WAV file or None if too short
    """
    print("\n🔴 Press ENTER to start recording...")
    print("💡 Or type 'test' to see your voice energy first")
    user_input = input().strip().lower()
    
    # Test mode - show live energy for 5 seconds
    if user_input == 'test':
        print("\n📊 VOICE TEST MODE - Speak to see your energy levels...")
        print("   Watch the numbers while you speak normally\n")
        
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        import time
        start = time.time()
        max_seen = 0
        
        while time.time() - start < 5:
            data = stream.read(CHUNK, exception_on_overflow=False)
            samples = struct.unpack(f"{len(data)//2}h", data)
            energy = int((sum(s**2 for s in samples) / len(samples))**0.5)
            max_seen = max(max_seen, energy)
            
            bar = "█" * min(50, energy // 10)
            print(f"\r   Energy: {energy:4d} | Max: {max_seen:4d} | {bar:50} ", end="", flush=True)
            time.sleep(0.05)
        
        stream.stop_stream()
        stream.close()
        
        print(f"\n\n✅ Your voice peaks at: {max_seen}")
        print(f"   Threshold needed: {speech_threshold}")
        if max_seen < speech_threshold:
            print(f"   ⚠️  You need to speak {speech_threshold - max_seen} louder or move closer to mic!")
        else:
            print(f"   ✅ Good! You're {max_seen - speech_threshold} above threshold!")
        
        print("\n🔴 Press ENTER to record for real...")
        input()
    
    print("\n🎙️  LISTENING... Speak your command!")
    print(f"   (Needs {min_speech_chunks * 0.064:.1f}s continuous speech to trigger)\n")
    
    import winsound
    winsound.Beep(1000, 100)
    
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    frames = []
    silence_chunks = 0
    max_silence = 24  # ~1.5 seconds at 16kHz
    speech_chunks_count = 0
    recording = False
    started = False
    
    # Energy smoothing to reduce fluctuations (moving average)
    energy_history = []
    smooth_window = 3  # Average last 3 chunks
    
    print(f"   Waiting for STRONG speech (energy > {speech_threshold})...")
    print(f"   (Minimum {min_speech_chunks * 0.064:.1f}s of continuous speech required)")
    print(f"   💡 TIP: Speak LOUDLY and CLEARLY to exceed threshold!\n")
    
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        
        # Calculate energy
        samples = struct.unpack(f"{len(data)//2}h", data)
        raw_energy = int((sum(s**2 for s in samples) / len(samples))**0.5)
        
        # Smooth energy to reduce fan noise fluctuations
        energy_history.append(raw_energy)
        if len(energy_history) > smooth_window:
            energy_history.pop(0)
        energy = int(sum(energy_history) / len(energy_history))  # Moving average
        
        # Visual feedback with 3 levels (show both raw and smoothed)
        bar = "█" * min(50, energy // 20)
        if energy > speech_threshold:
            status = "🎤 SPEECH!  "
        elif energy > silence_threshold:
            status = "📢 noise    "
        elif started:
            status = "⏸️  silence  "
        else:
            status = "⏳ waiting   "
        
        # Show raw energy too to see fluctuations
        print(f"\r   {status} | Smooth:{energy:4d} Raw:{raw_energy:4d} | {bar:50} ", end="", flush=True)
        
        # Start recording on strong speech
        if not started and energy > speech_threshold:
            started = True
            recording = True
            frames = [data]
            silence_chunks = 0
            speech_chunks_count = 1
            continue
        
        # Continue recording
        if recording:
            frames.append(data)
            
            # Count strong speech chunks
            if energy > speech_threshold:
                speech_chunks_count += 1
            
            # Silence detection
            if energy < silence_threshold:
                silence_chunks += 1
                if silence_chunks >= max_silence:
                    # Only accept if we had enough strong speech
                    if speech_chunks_count >= min_speech_chunks:
                        print("\n\n🔇 Silence detected - stopping...")
                        break
                    else:
                        # False trigger - reset and wait again
                        print(f"\n   ⚠️  Too short ({speech_chunks_count} chunks, need {min_speech_chunks}) - resetting...\n")
                        started = False
                        recording = False
                        frames = []
                        silence_chunks = 0
                        speech_chunks_count = 0
            else:
                silence_chunks = 0
    
    stream.stop_stream()
    stream.close()
    
    import winsound
    winsound.Beep(800, 100)
    
    print()
    
    # Save to file
    filename = "temp_voice_command.wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return filename


# ============================================================================
# FOLLOW-UP HANDLER
# ============================================================================

def handle_followup(timeout):
    """
    Wait for user follow-up response.
    
    Returns:
        True if user responded, False if timeout
    """
    print(f"\n⏰ Waiting {timeout}s for your response...")
    print("   Press ENTER to respond, or wait for timeout\n")
    
    responded = threading.Event()
    
    def wait_for_input():
        input()
        responded.set()
    
    thread = threading.Thread(target=wait_for_input, daemon=True)
    thread.start()
    thread.join(timeout=timeout)
    
    if responded.is_set():
        print("✅ You responded - continuing conversation\n")
        return True
    else:
        print("⏱️  Timeout - closing conversation")
        return False


# ============================================================================
# MAIN LOOP
# ============================================================================

def main():
    """Main voice assistant loop"""
    
    print("\n" + "="*70)
    print("🎙️  JARVIS PHASE 1 - ONLINE VOICE ASSISTANT")
    print("="*70)
    print("\n📋 FEATURES:")
    print("  ✅ Auto noise calibration")
    print("  ✅ Smart recording (silence detection)")
    print("  ✅ Groq STT (1-2 seconds)")
    print("  ✅ Qwen Brain with follow-up detection")
    print("  ✅ Edge TTS Arjun voice")
    print("  ✅ All skills (time, alarm, apps, email, etc.)")
    print("\n" + "="*70)
    
    # Initialize
    audio = pyaudio.PyAudio()
    
    # Check internet
    print("\n📡 Checking internet connection...")
    if not tts_manager.is_online():
        print("❌ No internet! Online mode requires internet.")
        print("   Please connect and try again.")
        audio.terminate()
        return
    print("✅ Online - Ready to start!\n")
    
    # Initialize MongoDB
    print("🗄️  Connecting to MongoDB...")
    try:
        mongo_manager.initialize()
        print("✅ MongoDB connected\n")
    except Exception as e:
        print(f"⚠️  MongoDB failed: {e}")
        print("   Continuing without conversation history...\n")
    
    # Auto-calibrate microphone
    global SPEECH_THRESHOLD, SILENCE_THRESHOLD
    SPEECH_THRESHOLD, SILENCE_THRESHOLD, MIN_SPEECH_CHUNKS, environment = auto_calibrate_noise(audio)
    
    print("🎯 Ready! Let's talk!")
    print("\n💡 TIP: Say things like:")
    print("   • 'What time is it?'")
    print("   • 'Set alarm for 5pm'")
    print("   • 'Open Chrome'")
    print("   • 'Explain quantum computing'")
    print("\n   Press Ctrl+C to exit\n")
    
    try:
        conversation_count = 0
        
        while True:
            conversation_count += 1
            print("─" * 70)
            print(f"💬 CONVERSATION #{conversation_count}")
            print("─" * 70)
            
            # 1. RECORD
            audio_file = record_command(audio, SPEECH_THRESHOLD, SILENCE_THRESHOLD, MIN_SPEECH_CHUNKS)
            
            # Check if user wants to quit
            if audio_file is None:
                print("\n👋 Exiting as requested...")
                break
            
            # 2. PARALLEL STT + BRAIN (for faster response)
            print("\n🎧 Transcribing...")
            stt_start = time.time()
            
            # Variables to share between threads
            transcription_result = {"text": None, "language": None, "done": False, "error": None}
            brain_result = {"response": None, "done": False}
            
            def run_stt():
                """STT in background thread"""
                try:
                    result = stt_online.transcribe_online(audio_file)
                    
                    if isinstance(result, dict):
                        transcription_result["text"] = result.get("text")
                        transcription_result["language"] = result.get("language")
                    else:
                        # Handle error string case
                        transcription_result["text"] = str(result)
                        transcription_result["language"] = "en"
                        
                    transcription_result["done"] = True
                    stt_elapsed = time.time() - stt_start
                    
                    if transcription_result["text"]:
                        # Map language codes to friendly names
                        lang_map = {
                            "en": "English",
                            "hi": "Hindi",
                            "unknown": "Mixed/Hinglish"
                        }
                        lang_name = lang_map.get(transcription_result["language"], transcription_result["language"])
                        print(f"\n   📝 You: {transcription_result['text']}")
                        print(f"   🌐 Language: {lang_name}")
                        print(f"   ⏱️  STT: {stt_elapsed:.2f}s")
                except Exception as e:
                    transcription_result["error"] = str(e)
                    transcription_result["done"] = True
            
            # Start STT in background
            stt_thread = threading.Thread(target=run_stt, daemon=True)
            stt_thread.start()
            
            # Wait for STT to complete
            print("   ⏳ Processing audio", end="", flush=True)
            while not transcription_result["done"]:
                print(".", end="", flush=True)
                time.sleep(0.2)
            print()
            
            # Check for errors
            if transcription_result["error"]:
                print(f"❌ STT Error: {transcription_result['error']}\n")
                os.remove(audio_file)
                continue
            
            text = transcription_result["text"]
            detected_language = transcription_result["language"]
            
            if not text or text.strip() == "":
                print("❌ No speech detected. Try speaking louder!\n")
                os.remove(audio_file)
                continue
            
            stt_time = time.time() - stt_start
            
            # 3. BRAIN (immediately after STT) - tell brain what language user spoke
            print("\n🧠 Processing...")
            brain_start = time.time()
            
            # Pass language hint to brain
            result = brain.process_command(text, user_language=detected_language)
            brain_time = time.time() - brain_start
            
            response = result.get("response", "")
            intent = result.get("intent", "unknown")
            expects_followup = result.get("expects_followup", False)
            followup_timeout = result.get("followup_timeout", 10)
            
            print(f"   💬 Jarvis: {response}")
            print(f"   🎯 Intent: {intent}")
            print(f"   ⏱️  Brain: {brain_time:.2f}s")
            
            if expects_followup:
                print(f"   ❓ Expects follow-up (timeout: {followup_timeout}s)")
            print()
            
            # 4. TTS - Use streaming for faster response with interrupt capability
            # Map Whisper language codes to TTS codes
            tts_lang = 'en'  # default
            if detected_language == 'hi':
                tts_lang = 'hi'
            elif detected_language in ['unknown', 'mixed']:
                tts_lang = 'mixed'  # Hinglish
            
            print("🔊 Speaking...")
            print("   💡 Press 'S' to skip/interrupt speech\n")
            start_time = time.time()
            
            # Flag to check if speech was interrupted
            interrupt_event = threading.Event()
            
            # Thread to check for keyboard interrupt
            def check_interrupt():
                while not interrupt_event.is_set():
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                        if key == 's':
                            interrupt_event.set()
                            print("\n   ⏭️  Speech interrupted by user!")
                            break
                    time.sleep(0.1)
            
            # Start interrupt listener thread
            interrupt_thread = threading.Thread(target=check_interrupt, daemon=True)
            interrupt_thread.start()
            
            # Use streaming TTS with interrupt capability
            tts_time, engine = tts_manager.speak_streaming(response, lang=tts_lang, interrupt_flag=interrupt_event)
            
            # Stop interrupt thread
            interrupt_event.set()
            
            # If streaming returned 0 (fallback to standard), calculate time manually
            if tts_time == 0.0:
                tts_time = time.time() - start_time
            
            print(f"   🔊 Engine: {engine}")
            print(f"   ⏱️  TTS: {tts_time:.2f}s\n")
            
            # 5. SAVE TO MONGODB
            try:
                # Save conversation
                mongo_manager.save_conversation({
                    "user_query": text,
                    "language_detected": detected_language,
                    "jarvis_response": response,
                    "intent": intent,
                    "expects_followup": expects_followup,
                    "performance": {
                        "stt_time": stt_time,
                        "brain_time": brain_time,
                        "tts_time": tts_time,
                        "total_time": stt_time + brain_time + tts_time
                    },
                    "timestamp": time.time()
                })
                
                # Save app/website commands separately for analytics
                if intent in ["open_app", "open_website", "open_file"]:
                    # Extract target from response or query
                    target = "unknown"
                    if "open" in text.lower():
                        words = text.lower().split()
                        if "open" in words:
                            idx = words.index("open")
                            if idx + 1 < len(words):
                                target = words[idx + 1]
                    
                    mongo_manager.save_app_command({
                        "command_type": intent,
                        "target": target,
                        "user_query": text,
                        "success": True,  # Assume success if no error
                        "timestamp": time.time()
                    })
                
                # Save command analytics
                mongo_manager.save_command_analytics(
                    intent=intent,
                    success=True,
                    response_time=stt_time + brain_time + tts_time
                )
                
                print("   💾 Saved to MongoDB")
            except Exception as e:
                print(f"   ⚠️  MongoDB save failed: {e}")
            print()
            
            # 6. PERFORMANCE SUMMARY
            total_time = stt_time + brain_time + tts_time
            print("=" * 70)
            print(f"⏱️  TOTAL: {total_time:.2f}s | STT: {stt_time:.1f}s | Brain: {brain_time:.1f}s | TTS: {tts_time:.1f}s")
            
            if total_time < 5:
                print("🚀 EXCELLENT - Very fast!")
            elif total_time < 10:
                print("✅ GOOD - Acceptable speed")
            else:
                print("⚠️  SLOW - Consider optimizations")
            print("=" * 70)
            
            # 6. CLEANUP
            try:
                os.remove(audio_file)
            except:
                pass
            
            # 7. ASK IF USER WANTS TO CONTINUE
            print("\n" + "─" * 70)
            print("❓ What would you like to do?")
            print("   [1] Press ENTER for another question")
            print("   [2] Press 'Q' to quit")
            print("─" * 70)
            
            # Wait for user input with timeout
            user_wants_continue = True
            
            def wait_for_choice():
                nonlocal user_wants_continue
                try:
                    # Clear any existing keypresses
                    while msvcrt.kbhit():
                        msvcrt.getch()
                    
                    print("\n⏳ Waiting for your choice (or auto-continue in 10s)...", end="", flush=True)
                    
                    start_wait = time.time()
                    while time.time() - start_wait < 10:
                        if msvcrt.kbhit():
                            key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                            if key == 'q':
                                user_wants_continue = False
                                print("\n✅ Quit selected")
                                return
                            elif key == '\r':  # Enter key
                                print("\n✅ Continuing...")
                                return
                        time.sleep(0.1)
                    
                    # Timeout - auto continue
                    print("\n⏱️  Auto-continuing (timeout)")
                    
                except:
                    pass
            
            wait_for_choice()
            
            if not user_wants_continue:
                print("\n💬 Jarvis: Goodbye! Have a great day!")
                closing_audio, _ = tts_manager.speak("Goodbye! Have a great day!")
                if closing_audio:
                    tts_online.play_audio(closing_audio)
                    try:
                        os.remove(closing_audio)
                    except:
                        pass
                break
            
            print()  # Clean spacing before next conversation
    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("👋 GOODBYE!")
        print("="*70)
        print(f"\n📊 Session Summary:")
        print(f"   Conversations: {conversation_count}")
        print(f"   Environment: {environment}")
        print("\n✅ Thank you for using Jarvis!\n")
    
    finally:
        audio.terminate()


if __name__ == "__main__":
    main()
