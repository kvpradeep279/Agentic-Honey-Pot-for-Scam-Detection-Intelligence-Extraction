# ===========================================
# Main API Entry Point
# ===========================================
# WHY: This is the heart of your submission!
# GUVI will send requests here and evaluate your responses.
# 
# Flow:
# 1. Receive request → Validate API key
# 2. Detect scam intent
# 3. If scam → Engage with AI agent
# 4. Extract intelligence
# 5. Return response (and send callback when ready)
# ===========================================

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio

from app.models import (
    HoneypotRequest, 
    HoneypotResponse, 
    EngagementMetrics, 
    ExtractedIntelligence
)
from app.scam_detector import scam_detector
from app.agent import honeypot_agent
from app.session_manager import session_manager
from app.callback_handler import callback_handler
from app.config import config


# ----- Application Lifespan -----
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.
    
    WHY: 
    - Startup: Initialize connections, verify config
    - Shutdown: Clean up resources
    """
    # Startup
    print("🍯 Honeypot API starting up...")
    print(f"   API Key configured: {'✅' if config.HONEYPOT_API_KEY else '❌'}")
    print(f"   Gemini API configured: {'✅' if config.GEMINI_API_KEY else '❌'}")
    yield
    # Shutdown
    print("🛑 Honeypot API shutting down...")


# ----- FastAPI Application -----
app = FastAPI(
    title="Agentic Honey-Pot API",
    description="AI-powered honeypot for scam detection and intelligence extraction",
    version="1.0.0",
    lifespan=lifespan
)


# ----- CORS Middleware -----
# WHY: Allow GUVI's testing system to access your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- Helper Functions -----

def verify_api_key(x_api_key: str = Header(None)) -> bool:
    """
    Verify the API key from request header.
    
    WHY: 
    - Security requirement from problem statement
    - Only authorized requests should be processed
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401, 
            detail="Missing x-api-key header"
        )
    
    if x_api_key != config.HONEYPOT_API_KEY:
        raise HTTPException(
            status_code=401, 
            detail="Invalid API key"
        )
    
    return True


# ----- API Endpoints -----

@app.get("/")
async def root():
    """
    Root endpoint - basic health check.
    
    WHY: Quick way to verify API is running
    """
    return {
        "status": "online",
        "service": "Agentic Honey-Pot API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    WHY: Used by deployment platforms to verify service is alive
    """
    return {
        "status": "healthy",
        "ai_available": honeypot_agent.ai_available
    }


@app.post("/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(
    request: HoneypotRequest,
    x_api_key: str = Header(None)
):
    """
    Main honeypot endpoint - receives scam messages.
    
    This is the endpoint you submit to GUVI!
    
    Flow:
    1. Validate API key
    2. Get/create session for this conversation
    3. Detect if message is a scam
    4. Generate agent response if scam detected
    5. Extract intelligence from message
    6. Update session state
    7. Check if callback should be sent
    8. Return response
    """
    
    # Step 1: Verify API key
    verify_api_key(x_api_key)
    
    # Step 2: Get or create session
    session = session_manager.get_or_create_session(request.sessionId)
    session.add_message()
    
    # Step 3: Detect scam intent
    is_scam, confidence, reasons = scam_detector.detect(
        request.message.text,
        request.conversationHistory
    )
    
    # Update session with detection results
    if is_scam:
        session.scam_detected = True
        session.scam_confidence = max(session.scam_confidence, confidence)
        for reason in reasons:
            session.add_agent_note(reason)
    
    # Step 4: Generate agent response if scam detected
    agent_response = None
    if session.scam_detected:
        agent_response = honeypot_agent.generate_response(
            current_message=request.message,
            conversation_history=request.conversationHistory,
            metadata=request.metadata
        )
        
        # Analyze scammer tactics for notes
        tactics = honeypot_agent.analyze_scammer_tactics(request.message.text)
        for tactic in tactics:
            session.add_agent_note(tactic)
    
    # Step 5: Extract intelligence from current message
    new_intelligence = scam_detector.extract_intelligence(request.message.text)
    session.merge_intelligence(new_intelligence)
    
    # Also extract from conversation history if present
    for hist_msg in request.conversationHistory:
        if hist_msg.sender == "scammer":
            hist_intel = scam_detector.extract_intelligence(hist_msg.text)
            session.merge_intelligence(hist_intel)
    
    # Step 6: Build response
    response = HoneypotResponse(
        status="success",
        scamDetected=session.scam_detected,
        agentResponse=agent_response,
        engagementMetrics=EngagementMetrics(
            engagementDurationSeconds=session.get_duration_seconds(),
            totalMessagesExchanged=session.message_count
        ),
        extractedIntelligence=session.intelligence,
        agentNotes=session.get_agent_notes_summary()
    )
    
    # Step 7: Check if we should send callback
    if callback_handler.should_send_callback(session):
        # Send callback in background (don't block response)
        asyncio.create_task(
            callback_handler.send_callback_async(session)
        )
    
    return response


@app.post("/analyze")
async def analyze_message(
    request: HoneypotRequest,
    x_api_key: str = Header(None)
):
    """
    Analyze-only endpoint - doesn't engage, just detects.
    
    WHY: Useful for testing detection without engagement
    """
    verify_api_key(x_api_key)
    
    is_scam, confidence, reasons = scam_detector.detect(
        request.message.text,
        request.conversationHistory
    )
    
    intelligence = scam_detector.extract_intelligence(request.message.text)
    
    return {
        "is_scam": is_scam,
        "confidence": confidence,
        "reasons": reasons,
        "extracted_intelligence": intelligence
    }


# ----- Error Handlers -----

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully."""
    print(f"❌ Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": "Internal server error"
        }
    )


# ----- Run the server -----
if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    # WHY these settings:
    # - host="0.0.0.0": Accept connections from any IP (needed for deployment)
    # - port=8000: Standard port for web APIs
    # - reload=True: Auto-restart on code changes (dev only)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
