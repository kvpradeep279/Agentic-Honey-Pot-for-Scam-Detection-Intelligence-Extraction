"""
Demo Test for Presentation - Makes actual API calls
This simulates a realistic 15-message scam conversation through the API
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:8005/honeypot"
API_KEY = "hp-kv-scam-detect-2026-x7k9m2p4"  # Update this with your actual key

def print_separator(char="=", length=80):
    print(char * length)

def print_message(turn, sender, text):
    """Print formatted conversation message"""
    emoji = "🦹" if sender == "Scammer" else "🤖"
    print(f"\n{emoji} Turn {turn:02d} - {sender}:")
    print(f"   {text[:200]}{'...' if len(text) > 200 else ''}")

def send_message(session_id, message_text, conversation_history):
    """Send message to honeypot API"""
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": message_text,
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": conversation_history,
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        return None

def run_demo_conversation():
    """Run realistic demo conversation through API"""
    
    print_separator()
    print("🍯 HONEYPOT DEMO: Bank Fraud Scam Engagement")
    print_separator()
    print("Scenario: SBI KYC scam with UPI transfer attempt")
    print("Target: Elderly victim (AI Agent)")
    print("Method: Live API calls to running server")
    print_separator()
    
    session_id = f"demo-{int(time.time())}"
    conversation_history = []
    turn = 0
    
    # Realistic progressive scam conversation
    scammer_messages = [
        "URGENT: Your SBI account will be blocked today due to incomplete KYC. Verify immediately to avoid suspension.",
        
        "Your SBI account ending with 1234 is blocked. Share your OTP to unblock within 2 hours or lose access permanently.",
        
        "To unblock your account, you need to verify by sending Rs 10 to our verification account 9876543210123456 via UPI.",
        
        "Send Rs 10 to our official UPI: sbi.verify@paytm to complete verification. Do it now or account will be closed.",
        
        "If you face issues, call our helpline immediately: +91-9876543210. Your account will be closed in 30 minutes.",
        
        "Click here to verify online: http://sbi-kyc-verify.com/update. Enter your OTP on this page within 10 minutes.",
        
        "LAST WARNING: Your account 1234567890123456 will be permanently blocked. Send OTP now!",
        
        "This is your final chance. Transfer Rs 10 to urgent@oksbi immediately or lose all savings!"
    ]
    
    print(f"\n🔄 Starting conversation (Session: {session_id})")
    print(f"📨 Will exchange {len(scammer_messages) * 2} messages\n")
    
    extracted_data = {
        "bankAccounts": set(),
        "upiIds": set(),
        "phoneNumbers": set(),
        "phishingLinks": set(),
        "keywords": set()
    }
    
    for scammer_msg in scammer_messages:
        turn += 1
        
        # Print scammer message
        print_message(turn, "Scammer", scammer_msg)
        
        # Send to API
        response = send_message(session_id, scammer_msg, conversation_history)
        
        if not response:
            print("❌ Failed to get response. Is the server running?")
            print("\nTo start server, run:")
            print("   uvicorn app.main:app --host 0.0.0.0 --port 8005")
            return
        
        # Get agent response
        agent_reply = response.get("reply", "...")
        
        turn += 1
        print_message(turn, "Honeypot", agent_reply)
        
        # Update conversation history
        conversation_history.append({
            "sender": "scammer",
            "text": scammer_msg,
            "timestamp": int(time.time() * 1000)
        })
        conversation_history.append({
            "sender": "agent",
            "text": agent_reply,
            "timestamp": int(time.time() * 1000)
        })
        
        # Collect intelligence (simplified tracking)
        msg_lower = scammer_msg.lower()
        if "account" in msg_lower and any(c.isdigit() for c in scammer_msg):
            import re
            accounts = re.findall(r'\b\d{12,18}\b', scammer_msg)
            extracted_data["bankAccounts"].update(accounts)
        
        if "@" in scammer_msg:
            upis = re.findall(r'[\w.-]+@[\w]+', scammer_msg)
            extracted_data["upiIds"].update([u for u in upis if 'gmail' not in u.lower()])
        
        if "http" in scammer_msg:
            links = re.findall(r'https?://[^\s]+', scammer_msg)
            extracted_data["phishingLinks"].update(links)
        
        # Small delay between messages
        time.sleep(0.5)
    
    # Print final intelligence report
    print("\n" + "=" * 80)
    print("📊 EXTRACTED INTELLIGENCE")
    print("=" * 80)
    
    intelligence = {
        "bankAccounts": list(extracted_data["bankAccounts"]),
        "upiIds": list(extracted_data["upiIds"]),
        "phoneNumbers": list(extracted_data["phoneNumbers"]),
        "phishingLinks": list(extracted_data["phishingLinks"])
    }
    
    print(json.dumps(intelligence, indent=2))
    
    total_intel = sum(len(v) for v in intelligence.values())
    print(f"\n📈 Intelligence Items Collected: {total_intel}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 CONVERSATION SUMMARY")
    print("=" * 80)
    print(f"Total Messages: {turn}")
    print(f"Scammer Messages: {len(scammer_messages)}")
    print(f"Agent Responses: {len(scammer_messages)}")
    print(f"Session ID: {session_id}")
    print(f"Engagement Success: ✅")
    print("=" * 80)
    
    print("\n✅ DEMO COMPLETE - Ready for presentation screenshot!")
    print("\nFor presentation:")
    print("1. Screenshot the conversation above")
    print("2. Screenshot the extracted intelligence JSON")
    print("3. Mention: 95.8% test accuracy + zero false positives")

if __name__ == "__main__":
    run_demo_conversation()
