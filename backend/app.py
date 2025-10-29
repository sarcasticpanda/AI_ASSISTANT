"""
Jarvis Assistant - FastAPI Backend
Main application entry point with REST API endpoints.

Endpoints:
- GET  /health          - Health check
- POST /listen          - Trigger speech-to-text
- POST /summarize_pdf   - Summarize a PDF file
- POST /speak           - Text-to-speech
- GET  /history         - Get conversation history
"""

import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG_MODE", "false").lower() == "true" else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Jarvis Assistant API",
    description="Hybrid Voice Assistant Backend",
    version="1.0.0"
)

# Enable CORS for Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify Electron's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import core modules
try:
    from core import mongo_manager, brain, qwen_api
    from core import stt_local, stt_online, tts_online, tts_offline
    from skills import pdf_summarizer
except ImportError as e:
    logger.warning(f"Some modules not yet available: {e}")


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SpeakRequest(BaseModel):
    """Request model for text-to-speech"""
    text: str
    online: bool = True
    lang: str = "en"


class PDFSummarizeRequest(BaseModel):
    """Request model for PDF summarization"""
    path: str  # Absolute path to PDF file


class ListenRequest(BaseModel):
    """Request model for speech-to-text"""
    online: bool = True
    audio_path: Optional[str] = None  # If provided, transcribe from file


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Jarvis Assistant API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": ["/health", "/listen", "/speak", "/summarize_pdf", "/history"]
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns system status and available services.
    """
    try:
        # Check MongoDB connection
        mongo_status = "connected"
        try:
            mongo_manager.ping()
        except Exception as e:
            mongo_status = f"disconnected: {str(e)}"
        
        return {
            "status": "healthy",
            "services": {
                "api": "online",
                "mongodb": mongo_status,
                "llm": "openrouter" if os.getenv("OPENROUTER_API_KEY") else "not_configured"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/listen")
async def listen(request: ListenRequest):
    """
    Speech-to-text endpoint.
    Converts audio to text using online (Groq) or offline (Vosk/Whisper) STT.
    
    Args:
        request: ListenRequest with online flag and optional audio_path
    
    Returns:
        {"text": "transcribed text", "method": "online|offline"}
    """
    try:
        logger.info(f"Listen request: online={request.online}, path={request.audio_path}")
        
        if request.audio_path and os.path.exists(request.audio_path):
            # Transcribe from file
            if request.online:
                text = stt_online.transcribe_online(request.audio_path)
                method = "groq_whisper"
            else:
                text = stt_local.transcribe_file(request.audio_path)
                method = "local_whisper"
        else:
            # TODO: Record from microphone and transcribe
            # For now, return a placeholder
            text = "Microphone recording not yet implemented"
            method = "placeholder"
        
        # Process command through brain
        response = brain.process_command(text)
        
        # Save to conversation history
        mongo_manager.save_conversation(
            user_text=text,
            assistant_text=response.get("response", ""),
            intent=response.get("intent", "unknown")
        )
        
        return {
            "text": text,
            "method": method,
            "response": response
        }
    
    except Exception as e:
        logger.error(f"Listen failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/speak")
async def speak(request: SpeakRequest, background_tasks: BackgroundTasks):
    """
    Text-to-speech endpoint.
    Converts text to speech using online (gTTS) or offline (Coqui/pyttsx3) TTS.
    
    Args:
        request: SpeakRequest with text, online flag, and language
    
    Returns:
        {"status": "speaking", "method": "online|offline", "audio_path": "path/to/audio"}
    """
    try:
        logger.info(f"Speak request: online={request.online}, text='{request.text[:50]}...'")
        
        if request.online:
            audio_path = tts_online.speak_online(request.text, request.lang)
            method = "gtts"
        else:
            audio_path = tts_offline.speak_offline(request.text, request.lang)
            method = "coqui"
        
        # Play audio in background (don't block response)
        # background_tasks.add_task(play_audio, audio_path)
        
        return {
            "status": "speaking",
            "method": method,
            "audio_path": audio_path,
            "text": request.text
        }
    
    except Exception as e:
        logger.error(f"Speak failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summarize_pdf")
async def summarize_pdf(request: PDFSummarizeRequest):
    """
    PDF summarization endpoint.
    Extracts text from PDF, chunks it, and generates summary using Qwen LLM.
    
    Args:
        request: PDFSummarizeRequest with PDF file path
    
    Returns:
        {"filename": "file.pdf", "summary": "...", "chunks_processed": 5}
    """
    try:
        logger.info(f"Summarize PDF request: {request.path}")
        
        if not os.path.exists(request.path):
            raise HTTPException(status_code=404, detail=f"PDF file not found: {request.path}")
        
        # Call PDF summarizer skill
        result = pdf_summarizer.summarize_pdf(request.path)
        
        return result
    
    except Exception as e:
        logger.error(f"PDF summarization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history(limit: int = 20):
    """
    Get conversation history from MongoDB.
    
    Args:
        limit: Number of recent conversations to retrieve (default: 20)
    
    Returns:
        {"history": [...], "total": 100}
    """
    try:
        logger.info(f"Get history request: limit={limit}")
        
        history = mongo_manager.get_recent_history(limit=limit)
        
        return {
            "history": history,
            "total": len(history)
        }
    
    except Exception as e:
        logger.error(f"Get history failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Jarvis Assistant API starting up...")
    
    # Initialize MongoDB connection
    try:
        mongo_manager.initialize()
        logger.info("✓ MongoDB connected")
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}")
    
    # TODO: Initialize wake word detection in background thread
    # wakeword.start_listener()
    
    logger.info("✓ Jarvis Assistant API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Jarvis Assistant API shutting down...")
    
    # Close MongoDB connection
    try:
        mongo_manager.close()
        logger.info("✓ MongoDB disconnected")
    except:
        pass


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", 5000))
    
    logger.info(f"Starting Jarvis Assistant API on {host}:{port}")
    
    # Run the server
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,  # Auto-reload on code changes (disable in production)
        log_level="info"
    )
