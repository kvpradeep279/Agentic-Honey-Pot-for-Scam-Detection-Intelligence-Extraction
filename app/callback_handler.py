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
        
        FINALS: Max 10 turns! Wait until late (turn 9) for complete intel extraction.
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
        
        has_rich_intel = real_intel_count >= 3  # Rich intelligence (3+ items)
        has_keywords = len(intel.suspiciousKeywords) >= 2
        
        # FINALS STRATEGY (max 10 turns = 20 messages):
        # WAIT LONGER - scammers reveal UPI/links late in conversation!
        # 
        # Conservative timing - maximize intelligence extraction:
        # 1. Turn 9 (18+ messages): Send with ANY intel found
        # 2. Turn 10 (20 messages): Force send (max turns)
        # 3. Rich intel (3+ items) at turn 7: OK to send early
        
        msg_count = session.message_count
        
        # Force send at max turns (safety net)
        if msg_count >= config.MAX_CONVERSATION_TURNS:
            return True
        
        # Turn 9+: Send with any intel or keywords
        if msg_count >= 18 and (real_intel_count > 0 or has_keywords):
            return True
        
        # Rich intel (3+ items) - OK to send at turn 7+
        if has_rich_intel and msg_count >= 14:
            return True
        
        # Absolute minimum: turn 9 even with nothing
        if msg_count >= 18:
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
            # Build payload matching GUVI's expected format (Feb 19 VERSION)
            # Required: sessionId, scamDetected, extractedIntelligence
            # Optional: scamType, confidenceLevel, engagementMetrics, agentNotes
            payload = {
                "sessionId": session.session_id,
                "status": "completed",
                "scamDetected": session.scam_detected,
                "scamType": session.scam_type,
                "confidenceLevel": session.scam_confidence,  # Feb 19 (1 pt)
                "totalMessagesExchanged": session.message_count,
                "engagementDurationSeconds": session.get_duration_seconds(),
                "extractedIntelligence": {
                    "bankAccounts": session.intelligence.bankAccounts,
                    "upiIds": session.intelligence.upiIds,
                    "phishingLinks": session.intelligence.phishingLinks,
                    "phoneNumbers": session.intelligence.phoneNumbers,
                    "emailAddresses": session.intelligence.emailAddresses,
                    "caseIds": session.intelligence.caseIds,  # Feb 19
                    "policyNumbers": session.intelligence.policyNumbers,  # Feb 19
                    "orderNumbers": session.intelligence.orderNumbers,  # Feb 19
                    "suspiciousKeywords": session.intelligence.suspiciousKeywords
                },
                "engagementMetrics": {
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
            # Build payload matching GUVI's expected format (Feb 19 VERSION)
            payload = {
                "sessionId": session.session_id,
                "status": "completed",
                "scamDetected": session.scam_detected,
                "scamType": session.scam_type,
                "confidenceLevel": session.scam_confidence,  # Feb 19 (1 pt)
                "totalMessagesExchanged": session.message_count,
                "engagementDurationSeconds": session.get_duration_seconds(),
                "extractedIntelligence": {
                    "bankAccounts": session.intelligence.bankAccounts,
                    "upiIds": session.intelligence.upiIds,
                    "phishingLinks": session.intelligence.phishingLinks,
                    "phoneNumbers": session.intelligence.phoneNumbers,
                    "emailAddresses": session.intelligence.emailAddresses,
                    "caseIds": session.intelligence.caseIds,  # Feb 19
                    "policyNumbers": session.intelligence.policyNumbers,  # Feb 19
                    "orderNumbers": session.intelligence.orderNumbers,  # Feb 19
                    "suspiciousKeywords": session.intelligence.suspiciousKeywords
                },
                "engagementMetrics": {
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
