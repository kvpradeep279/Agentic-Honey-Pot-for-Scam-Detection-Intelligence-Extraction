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
    
    def should_send_callback(self, session: ConversationSession) -> bool:
        """
        Determine if we should send the final callback.
        
        WHY conditions:
        - Must have detected scam (no point reporting non-scams)
        - Must have some engagement (not just first message)
        - Prevent duplicate callbacks
        - Have some intelligence to report
        """
        
        if session.callback_sent:
            return False
        
        if not session.scam_detected:
            return False
        
        # Wait for minimum engagement before callback
        if session.message_count < config.MIN_TURNS_BEFORE_CALLBACK:
            return False
        
        # Check if we have meaningful intelligence
        intel = session.intelligence
        has_intelligence = (
            len(intel.bankAccounts) > 0 or
            len(intel.upiIds) > 0 or
            len(intel.phishingLinks) > 0 or
            len(intel.phoneNumbers) > 0 or
            len(intel.suspiciousKeywords) > 2
        )
        
        # Send if max turns reached OR we have good intelligence
        max_turns_reached = session.message_count >= config.MAX_CONVERSATION_TURNS
        
        return max_turns_reached or has_intelligence
    
    def send_callback(self, session: ConversationSession) -> bool:
        """
        Send final results to GUVI endpoint (synchronous version).
        
        Returns:
            True if callback was successful, False otherwise
        """
        
        if session.callback_sent:
            print(f"⚠️ Callback already sent for session {session.session_id}")
            return False
        
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
                session.callback_sent = True
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
        
        if session.callback_sent:
            return False
        
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
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.callback_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
            
            if response.status_code == 200:
                session.callback_sent = True
                return True
            return False
            
        except Exception as e:
            print(f"❌ Async callback error: {e}")
            return False


# Global callback handler instance
callback_handler = CallbackHandler()
