# ===========================================
# Data Models (Pydantic)
# ===========================================
# WHY: Models define the shape of our data
# - Automatic validation (reject bad data)
# - Clear documentation (see exactly what fields exist)
# - Type hints (IDE autocomplete works!)
# - Auto-generates JSON schemas
# ===========================================

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ----- Input Models (What we receive) -----

class Message(BaseModel):
    """
    Represents a single message in the conversation.
    
    WHY these fields:
    - sender: Know if it's from "scammer" or "user" (our agent)
    - text: The actual message content we analyze
    - timestamp: Track timing for engagement duration
    """
    sender: str = Field(..., description="Who sent the message: 'scammer' or 'user'")
    text: str = Field(..., description="The message content")
    timestamp: str = Field(..., description="ISO-8601 formatted timestamp")


class Metadata(BaseModel):
    """
    Optional context about the conversation.
    
    WHY: Helps our agent adapt its behavior
    - SMS might use shorter messages
    - WhatsApp might have different patterns
    - Language/locale helps with understanding
    """
    channel: Optional[str] = Field(default="SMS", description="SMS/WhatsApp/Email/Chat")
    language: Optional[str] = Field(default="English", description="Language of messages")
    locale: Optional[str] = Field(default="IN", description="Country or region code")


class HoneypotRequest(BaseModel):
    """
    The main request body we receive from GUVI's test system.
    
    This is exactly what the problem statement defines!
    """
    sessionId: str = Field(..., description="Unique conversation identifier")
    message: Message = Field(..., description="The latest incoming message")
    conversationHistory: List[Message] = Field(
        default=[], 
        description="Previous messages in this conversation"
    )
    metadata: Optional[Metadata] = Field(default=None, description="Context metadata")


# ----- Output Models (What we return) -----

class ExtractedIntelligence(BaseModel):
    """
    All the scam-related information we extract.
    
    WHY these specific fields:
    - These are exactly what GUVI expects
    - Each represents actionable intelligence for law enforcement
    """
    bankAccounts: List[str] = Field(default=[], description="Bank account numbers found")
    upiIds: List[str] = Field(default=[], description="UPI IDs like 'name@bank'")
    phishingLinks: List[str] = Field(default=[], description="Malicious URLs")
    phoneNumbers: List[str] = Field(default=[], description="Phone numbers mentioned")
    suspiciousKeywords: List[str] = Field(default=[], description="Keywords indicating scam")


class EngagementMetrics(BaseModel):
    """
    Metrics about our conversation with the scammer.
    
    WHY track these:
    - Longer engagement = more intelligence gathered
    - More messages = deeper scammer commitment
    """
    engagementDurationSeconds: int = Field(default=0, description="How long we engaged")
    totalMessagesExchanged: int = Field(default=0, description="Total message count")


class HoneypotResponse(BaseModel):
    """
    The response we send back to GUVI.
    
    This matches exactly what the problem statement requires!
    """
    status: str = Field(default="success", description="'success' or 'error'")
    scamDetected: bool = Field(..., description="Did we detect a scam?")
    agentResponse: Optional[str] = Field(default=None, description="Our agent's reply to scammer")
    engagementMetrics: EngagementMetrics = Field(default_factory=EngagementMetrics)
    extractedIntelligence: ExtractedIntelligence = Field(default_factory=ExtractedIntelligence)
    agentNotes: str = Field(default="", description="Summary of scammer tactics observed")


# ----- Callback Model (What we send to GUVI at the end) -----

class FinalResultCallback(BaseModel):
    """
    Final payload sent to GUVI's callback endpoint.
    
    WHY: This is MANDATORY for scoring!
    Without this, your solution cannot be evaluated.
    """
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: dict  # Use dict for flexibility
    agentNotes: str
