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
        
        Per doc: "The AI Agent has completed sufficient engagement"
        Example shows 18 messages exchanged - we should wait for substantial engagement.
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
        real_intel_count = (
            len(intel.bankAccounts) +
            len(intel.upiIds) +
            len(intel.phishingLinks) +
            len(intel.phoneNumbers)
        )
        
        has_real_intel = real_intel_count > 0
        has_multiple_intel = real_intel_count >= 2  # Multiple pieces of real intel
        has_rich_intel = real_intel_count >= 3  # Rich intelligence (3+ items)
        has_keywords = len(intel.suspiciousKeywords) >= 2
        
        # Strategy (adjusted for 18-message conversations):
        # 1. Force send at max turns (35 = ~18 scammer messages)
        # 2. With rich intel (3+ items) - send at 10+ turns (~5 scammer msgs)
        # 3. With multiple intel (2 items) - send at 15+ turns (~8 scammer msgs)
        # 4. With single real intel - send at 20+ turns (~10 scammer msgs)
        # 5. Keywords only - send at 25+ turns (~13 scammer msgs)
        
        msg_count = session.message_count
        max_turns_reached = msg_count >= config.MAX_CONVERSATION_TURNS
        
        if max_turns_reached:
            # Force send at max turns
            return True
        
        if has_rich_intel and msg_count >= 10:
            # Rich intel (3+ items) + decent engagement
            return True
        
        if has_multiple_intel and msg_count >= 15:
            # Multiple intel items (2) + good engagement
            return True
        
        if has_real_intel and msg_count >= 20:
            # Single real intel + substantial engagement
            return True
        
        if has_keywords and msg_count >= 25:
            # Only keywords? Need very long engagement
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
            # Build payload matching GUVI's expected format
            payload = {
                "sessionId": session.session_id,
                "scamDetected": session.scam_detected,
                "totalMessagesExchanged": session.message_count,
                "extractedIntelligence": {
                    "bankAccounts": session.intelligence.bankAccounts,
                    "upiIds": session.intelligence.upiIds,
                    "phishingLinks": session.intelligence.phishingLinks,
                    "phoneNumbers": session.intelligence.phoneNumbers,
                    "suspiciousKeywords": session.intelligence.suspiciousKeywords
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
            payload = {
                "sessionId": session.session_id,
                "scamDetected": session.scam_detected,
                "totalMessagesExchanged": session.message_count,
                "extractedIntelligence": {
                    "bankAccounts": session.intelligence.bankAccounts,
                    "upiIds": session.intelligence.upiIds,
                    "phishingLinks": session.intelligence.phishingLinks,
                    "phoneNumbers": session.intelligence.phoneNumbers,
                    "suspiciousKeywords": session.intelligence.suspiciousKeywords
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
