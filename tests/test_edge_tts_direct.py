import edge_tts
import asyncio

async def test():
    text = "Hello, I am Jarvis. Testing Edge TTS."
    voice = "hi-IN-ArjunNeural"
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("test_edge.mp3")
    print("✅ Edge TTS works! File saved: test_edge.mp3")

asyncio.run(test())
