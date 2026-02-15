# ===========================================
# Callback Handler
# ===========================================
# WHY: This is MANDATORY for scoring!
# When engagement is complete, we must report
# our findings back to GUVI's evaluation endpoint.
# Without this, your solution cannot be evaluated!
# ===========================================

import httpx
import requests
from typing import Optional
from app.models import FinalResultCallback, ExtractedIntelligence
from app.session_manager import ConversationSession
from app.config import config
import asyncio


class CallbackHandler:
    """
    Handles sending final results to GUVI evaluation endpoint.
    
    WHY this is critical:
    - GUVI uses this data to measure your score
    - Without callback, no evaluation happens
    - This proves your honeypot actually works
    """
    
    def __init__(self):
        self.callback_url = config.GUVI_CALLBACK_URL
        # Track sent callbacks to prevent duplicates (even across requests)
        self.sent_sessions = set()
    
    def should_send_callback(self, session: ConversationSession) -> bool:
        """
        Determine if we should send the final callback.
        
        WHY conditions:
        - Must have detected scam (no point reporting non-scams)
        - Must have meaningful engagement (sufficient turns)
        - Must have extracted real intelligence (not just keywords)
        - Prevent duplicate callbacks
        
        FINALS: Max 10 turns! Callback timing adjusted accordingly.
        """
        
        # Prevent duplicate callbacks
        if session.session_id in self.sent_sessions:
            return False
        
        if session.callback_sent:
            return False
        
        if not session.scam_detected:
            return False
        
        # Check what intelligence we've gathered
        intel = session.intelligence
        
        # Count "real" extracted data (not just keywords)
        # Include emailAddresses in count!
        real_intel_count = (
            len(intel.bankAccounts) +
            len(intel.upiIds) +
            len(intel.phishingLinks) +
            len(intel.phoneNumbers) +
            len(intel.emailAddresses)
        )
        
        has_real_intel = real_intel_count > 0
        has_multiple_intel = real_intel_count >= 2  # Multiple pieces of real intel
        has_rich_intel = real_intel_count >= 3  # Rich intelligence (3+ items)
        has_keywords = len(intel.suspiciousKeywords) >= 2
        
        # FINALS STRATEGY (max 10 turns!):
        # Evaluator does UP TO 10 turns - we need to callback before conversation ends
        # Each turn = 1 scammer msg + 1 agent reply = 2 messages in history
        # So 10 turns = ~20 messages max
        # 
        # AGGRESSIVE TIMING - Send callback early with any intel:
        # 1. Force send at turn 8+ (16 messages) - leave buffer before max
        # 2. With ANY real intel - send at turn 3+ (6 messages)
        # 3. With keywords only - send at turn 5+ (10 messages)
        # 4. Max safety - send at turn 10 (20 messages)
        
        msg_count = session.message_count
        
        # Force send at max turns (safety net)
        if msg_count >= config.MAX_CONVERSATION_TURNS:
            return True
        
        # AGGRESSIVE: Any real intel + 3+ turns - SEND NOW!
        if has_real_intel and msg_count >= 6:
            return True
        
        # Multiple intel found - send immediately at turn 2+
        if has_multiple_intel and msg_count >= 4:
            return True
        
        # Rich intel - send at turn 2
        if has_rich_intel and msg_count >= 4:
            return True
        
        # Only keywords - wait a bit longer but not too long
        if has_keywords and msg_count >= 10:
            return True
        
        # Safety: Force send at turn 8 even with no intel
        if msg_count >= 16:
            return True
        
        # Keep engaging - not ready yet
        return False
    
    def send_callback(self, session: ConversationSession) -> bool:
        """
        Send final results to GUVI endpoint (synchronous version).
        
        Returns:
            True if callback was successful, False otherwise
        """
        
        if session.callback_sent or session.session_id in self.sent_sessions:
            print(f"⚠️ Callback already sent for session {session.session_id}")
            return False
        
        # Mark as sent immediately to prevent race conditions
        self.sent_sessions.add(session.session_id)
        session.callback_sent = True
        
        try:
            # Build payload matching GUVI's expected format (FINALS VERSION)
            # Required fields: status, scamDetected, extractedIntelligence
            # Optional fields: engagementMetrics, agentNotes, scamType
            payload = {
                "sessionId": session.session_id,
                "status": "completed",  # Required for Response Structure points!
                "scamDetected": session.scam_detected,
                "scamType": session.scam_type,  # bank_fraud, upi_fraud, phishing, etc.
                "totalMessagesExchanged": session.message_count,
                "extractedIntelligence": {
                    "bankAccounts": session.intelligence.bankAccounts,
                    "upiIds": session.intelligence.upiIds,
                    "phishingLinks": session.intelligence.phishingLinks,
                    "phoneNumbers": session.intelligence.phoneNumbers,
                    "emailAddresses": session.intelligence.emailAddresses,  # Added for finals!
                    "suspiciousKeywords": session.intelligence.suspiciousKeywords
                },
                "engagementMetrics": {  # Added for finals! (5 points)
                    "engagementDurationSeconds": session.get_duration_seconds(),
                    "totalMessagesExchanged": session.message_count
                },
                "agentNotes": session.get_agent_notes_summary()
            }
            
            print(f"📤 Sending callback for session {session.session_id}")
            print(f"   Payload: {payload}")
            
            # Send POST request to GUVI
            response = requests.post(
                self.callback_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Callback successful for session {session.session_id}")
                return True
            else:
                print(f"❌ Callback failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Callback error: {e}")
            return False
    
    async def send_callback_async(self, session: ConversationSession) -> bool:
        """
        Send final results to GUVI endpoint (async version).
        
        WHY async:
        - Non-blocking operation
        - Faster API response times
        - Better for concurrent requests
        """
        
        if session.callback_sent or session.session_id in self.sent_sessions:
            return False
        
        # Mark as sent immediately to prevent race conditions
        self.sent_sessions.add(session.session_id)
        session.callback_sent = True
        
        try:
            # Build payload matching GUVI's expected format (FINALS VERSION)
            payload = {
                "sessionId": session.session_id,
                "status": "completed",  # Required for Response Structure points!
                "scamDetected": session.scam_detected,
                "scamType": session.scam_type,  # bank_fraud, upi_fraud, phishing, etc.
                "totalMessagesExchanged": session.message_count,
                "extractedIntelligence": {
                    "bankAccounts": session.intelligence.bankAccounts,
                    "upiIds": session.intelligence.upiIds,
                    "phishingLinks": session.intelligence.phishingLinks,
                    "phoneNumbers": session.intelligence.phoneNumbers,
                    "emailAddresses": session.intelligence.emailAddresses,  # Added for finals!
                    "suspiciousKeywords": session.intelligence.suspiciousKeywords
                },
                "engagementMetrics": {  # Added for finals! (5 points)
                    "engagementDurationSeconds": session.get_duration_seconds(),
                    "totalMessagesExchanged": session.message_count
                },
                "agentNotes": session.get_agent_notes_summary()
            }
            
            print(f"📤 [ASYNC] Sending callback for session {session.session_id}")
            print(f"   Payload: {payload}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.callback_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
            
            if response.status_code == 200:
                print(f"✅ [ASYNC] Callback successful for session {session.session_id}")
                return True
            else:
                print(f"❌ [ASYNC] Callback failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"❌ Async callback error: {e}")
            return False


# Global callback handler instance
callback_handler = CallbackHandler()
