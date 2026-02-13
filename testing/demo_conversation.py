"""
Demo Conversation Generator for Presentation
Shows realistic 15-message exchange with scammer + extracted intelligence
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scam_detector import ScamDetector
from app.agent import HoneypotAgent
from app.session_manager import SessionManager
from app.models import Message, ExtractedIntelligence
import json
from datetime import datetime

def print_separator():
    print("=" * 80)

def print_message(turn: int, sender: str, text: str):
    """Print a conversation message with formatting"""
    emoji = "🦹" if sender == "Scammer" else "🤖"
    print(f"\n{emoji} Turn {turn} - {sender}:")
    print(f"   {text}")

def print_intelligence(intel: ExtractedIntelligence):
    """Print extracted intelligence in a formatted way"""
    print("\n" + "=" * 80)
    print("📊 EXTRACTED INTELLIGENCE")
    print("=" * 80)
    
    data = {
        "bankAccounts": intel.bankAccounts,
        "upiIds": intel.upiIds,
        "phishingLinks": intel.phishingLinks,
        "phoneNumbers": intel.phoneNumbers,
        "suspiciousKeywords": intel.suspiciousKeywords[:10]  # First 10 keywords
    }
    
    print(json.dumps(data, indent=2))
    
    # Summary
    total_intel = (len(intel.bankAccounts) + len(intel.upiIds) + 
                   len(intel.phishingLinks) + len(intel.phoneNumbers))
    print(f"\n📈 Intelligence Items Collected: {total_intel}")
    print(f"🔑 Keywords Detected: {len(intel.suspiciousKeywords)}")

def run_demo_conversation():
    """Run a realistic 15-message scam conversation"""
    
    print_separator()
    print("🍯 HONEYPOT DEMO: Bank Fraud Scam Engagement")
    print("=" * 80)
    print("Scenario: SBI KYC scam with UPI transfer attempt")
    print("Target: Elderly victim (AI Agent)")
    print_separator()
    
    # Initialize components
    detector = ScamDetector()
    agent = HoneypotAgent()
    session_manager = SessionManager()
    session = session_manager.get_or_create_session("demo-session-001")
    
    conversation_history = []
    
    # Realistic conversation flow
    conversation = [
        # Turn 1: Initial scam message
        "URGENT: Your SBI account will be blocked today due to incomplete KYC. Verify immediately to avoid suspension.",
        
        # Turn 3: Escalation with threat
        "Your SBI account ending with 1234 is blocked. Share your OTP to unblock within 2 hours or lose access permanently.",
        
        # Turn 5: Revealing bank account
        "To unblock your account, you need to verify by sending Rs 10 to our verification account 9876543210123456 via UPI.",
        
        # Turn 7: UPI ID reveal
        "Send Rs 10 to our official UPI: sbi.verify@paytm to complete verification. Do it now or account will be closed.",
        
        # Turn 9: Phone number reveal
        "If you face issues, call our helpline immediately: +91-9876543210. Your account will be closed in 30 minutes.",
        
        # Turn 11: Phishing link
        "Click here to verify online: http://sbi-kyc-verify.com/update. Enter your OTP on this page within 10 minutes.",
        
        # Turn 13: Final pressure
        "LAST WARNING: Your account 1234567890123456 will be permanently blocked. Send OTP 123456 to sbi.urgent@ybl NOW!",
        
        # Turn 15: Aggressive close
        "This is your final chance. All your savings will be frozen. Transfer Rs 10 to 9876543210123456 through our UPI urgent@oksbi immediately!"
    ]
    
    turn = 0
    
    for scammer_msg in conversation:
        turn += 1
        
        # Print scammer message
        print_message(turn, "Scammer", scammer_msg)
        
        # Detect scam
        result = detector.detect_scam(scammer_msg)
        
        # Extract intelligence
        intel = detector.extract_intelligence(scammer_msg)
        session.merge_intelligence(intel)
        
        # Show detection result (inline)
        if result.is_scam:
            print(f"   ⚠️  Scam Detected (Confidence: {result.confidence:.2f})")
        
        # Generate agent response
        message_obj = Message(
            sender="scammer",
            text=scammer_msg,
            timestamp=int(datetime.now().timestamp() * 1000)
        )
        
        agent_response = agent.generate_response(
            message_obj,
            conversation_history,
            result.confidence
        )
        
        turn += 1
        print_message(turn, "Honeypot Agent", agent_response)
        
        # Update session and conversation history
        session.add_message()
        conversation_history.append(message_obj)
        session_response = Message(
            sender="agent",
            text=agent_response,
            timestamp=int(datetime.now().timestamp() * 1000)
        )
        session.add_message()
        conversation_history.append(session_response)
    
    # Print final intelligence report
    print_intelligence(session.intelligence)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 CONVERSATION SUMMARY")
    print("=" * 80)
    print(f"Total Turns: {turn}")
    print(f"Scammer Messages: {len(conversation)}")
    print(f"Agent Responses: {len(conversation)}")
    print(f"Engagement Duration: ~15 minutes (estimated)")
    print(f"Scam Confidence: {result.confidence:.2f} (High)")
    print("=" * 80)

if __name__ == "__main__":
    run_demo_conversation()
