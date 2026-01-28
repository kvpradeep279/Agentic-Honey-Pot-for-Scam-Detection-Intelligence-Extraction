# ===========================================
# Session Manager
# ===========================================
# WHY: Scam conversations happen over multiple messages
# We need to remember:
# - What intelligence we've extracted so far
# - How many messages exchanged
# - When the conversation started
# - Previous agent responses
# ===========================================

from typing import Dict, Optional
from datetime import datetime
from app.models import ExtractedIntelligence, Message
import threading


class ConversationSession:
    """
    Tracks a single conversation session with a scammer.
    
    WHY we need this:
    - Multi-turn: Scammer sends multiple messages
    - State: Need to accumulate extracted intelligence
    - Metrics: Track engagement duration and message count
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = datetime.now()
        self.message_count = 0
        self.scam_detected = False
        self.scam_confidence = 0.0
        self.intelligence = ExtractedIntelligence()
        self.agent_notes: list = []
        self.callback_sent = False  # Prevent duplicate callbacks
        
    def add_message(self):
        """Increment message count for each exchange."""
        self.message_count += 1
        
    def get_duration_seconds(self) -> int:
        """Calculate how long we've been engaging."""
        delta = datetime.now() - self.start_time
        return int(delta.total_seconds())
    
    def merge_intelligence(self, new_intel: ExtractedIntelligence):
        """
        Merge newly extracted intelligence with existing.
        
        WHY merge instead of replace:
        - Each message might reveal different info
        - We want to accumulate everything
        - Avoid losing previously found data
        """
        # Add unique bank accounts
        for account in new_intel.bankAccounts:
            if account not in self.intelligence.bankAccounts:
                self.intelligence.bankAccounts.append(account)
        
        # Add unique UPI IDs
        for upi in new_intel.upiIds:
            if upi not in self.intelligence.upiIds:
                self.intelligence.upiIds.append(upi)
        
        # Add unique phishing links
        for link in new_intel.phishingLinks:
            if link not in self.intelligence.phishingLinks:
                self.intelligence.phishingLinks.append(link)
        
        # Add unique phone numbers
        for phone in new_intel.phoneNumbers:
            if phone not in self.intelligence.phoneNumbers:
                self.intelligence.phoneNumbers.append(phone)
        
        # Add unique suspicious keywords
        for keyword in new_intel.suspiciousKeywords:
            if keyword not in self.intelligence.suspiciousKeywords:
                self.intelligence.suspiciousKeywords.append(keyword)
    
    def add_agent_note(self, note: str):
        """Add an observation about scammer behavior."""
        if note and note not in self.agent_notes:
            self.agent_notes.append(note)
    
    def get_agent_notes_summary(self) -> str:
        """Combine all notes into a summary string."""
        return "; ".join(self.agent_notes) if self.agent_notes else "Scam engagement in progress"


class SessionManager:
    """
    Manages all active conversation sessions.
    
    WHY a global manager:
    - GUVI sends requests with same sessionId for same conversation
    - Need to track state across multiple API calls
    - Thread-safe for concurrent requests
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern - only one session manager exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.sessions: Dict[str, ConversationSession] = {}
        return cls._instance
    
    def get_or_create_session(self, session_id: str) -> ConversationSession:
        """
        Get existing session or create new one.
        
        WHY:
        - First message: Create new session
        - Follow-up messages: Get existing session with accumulated data
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationSession(session_id)
        return self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get session if it exists, None otherwise."""
        return self.sessions.get(session_id)
    
    def remove_session(self, session_id: str):
        """Clean up session after callback is sent."""
        if session_id in self.sessions:
            del self.sessions[session_id]


# Global session manager instance
session_manager = SessionManager()
