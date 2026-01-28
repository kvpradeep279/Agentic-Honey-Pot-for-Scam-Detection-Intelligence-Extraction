# ===========================================
# Local Test Script
# ===========================================
# WHY: Test your API locally before deploying
# Run this after starting the server to verify everything works
# ===========================================

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("HONEYPOT_API_KEY", "")  # Reads from .env file - NEVER hardcode!

if not API_KEY:
    print("❌ ERROR: HONEYPOT_API_KEY not found in .env file!")
    print("   Please create a .env file with: HONEYPOT_API_KEY=your-key-here")
    exit(1)

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}


def test_health():
    """Test if server is running."""
    print("\n🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    return response.status_code == 200


def test_auth():
    """Test API key authentication."""
    print("\n🔐 Testing authentication...")
    
    # Without API key - should fail
    response = requests.post(
        f"{BASE_URL}/honeypot",
        json={"sessionId": "test", "message": {"sender": "scammer", "text": "test", "timestamp": "2026-01-28T10:00:00Z"}},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Without key: {response.status_code} (expected 401)")
    
    # With wrong API key - should fail
    response = requests.post(
        f"{BASE_URL}/honeypot",
        json={"sessionId": "test", "message": {"sender": "scammer", "text": "test", "timestamp": "2026-01-28T10:00:00Z"}},
        headers={"x-api-key": "wrong-key", "Content-Type": "application/json"}
    )
    print(f"   Wrong key: {response.status_code} (expected 401)")
    
    return True


def test_scam_detection():
    """Test scam detection with various messages."""
    print("\n🕵️ Testing scam detection...")
    
    test_cases = [
        {
            "name": "Bank Threat Scam",
            "message": "URGENT: Your SBI account will be blocked today. Click here to verify: http://sbi-verify.fake.com",
            "expected_scam": True
        },
        {
            "name": "UPI Request Scam",
            "message": "Share your UPI PIN to receive refund of Rs 5000 immediately",
            "expected_scam": True
        },
        {
            "name": "Lottery Scam",
            "message": "Congratulations! You won lottery of 50 lakhs. Send processing fee to account 1234567890",
            "expected_scam": True
        },
        {
            "name": "Normal Message",
            "message": "Hi, how are you doing today?",
            "expected_scam": False
        }
    ]
    
    for test in test_cases:
        payload = {
            "sessionId": f"test-{test['name'].lower().replace(' ', '-')}",
            "message": {
                "sender": "scammer",
                "text": test["message"],
                "timestamp": "2026-01-28T10:00:00Z"
            },
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/honeypot",
            json=payload,
            headers=HEADERS
        )
        
        result = response.json()
        status = "✅" if result.get("scamDetected") == test["expected_scam"] else "❌"
        print(f"   {status} {test['name']}: scamDetected={result.get('scamDetected')}")
        
        if result.get("scamDetected"):
            print(f"      Agent Response: {result.get('agentResponse', 'N/A')[:80]}...")
            if result.get("extractedIntelligence"):
                intel = result["extractedIntelligence"]
                if intel.get("upiIds"):
                    print(f"      UPI IDs: {intel['upiIds']}")
                if intel.get("phishingLinks"):
                    print(f"      Links: {intel['phishingLinks']}")
                if intel.get("bankAccounts"):
                    print(f"      Accounts: {intel['bankAccounts']}")


def test_multi_turn_conversation():
    """Test multi-turn conversation handling."""
    print("\n💬 Testing multi-turn conversation...")
    
    session_id = "multi-turn-test-123"
    
    # Turn 1: Initial scam message
    turn1_payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Your account will be blocked today. Call us immediately at 9876543210",
            "timestamp": "2026-01-28T10:00:00Z"
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
    }
    
    response1 = requests.post(f"{BASE_URL}/honeypot", json=turn1_payload, headers=HEADERS)
    result1 = response1.json()
    print(f"   Turn 1 - Scam Detected: {result1.get('scamDetected')}")
    print(f"   Turn 1 - Agent: {result1.get('agentResponse', 'N/A')}")
    
    # Turn 2: Scammer continues
    turn2_payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "To unblock, transfer Rs 500 to UPI ID verify@scambank",
            "timestamp": "2026-01-28T10:01:00Z"
        },
        "conversationHistory": [
            {"sender": "scammer", "text": turn1_payload["message"]["text"], "timestamp": turn1_payload["message"]["timestamp"]},
            {"sender": "user", "text": result1.get("agentResponse", ""), "timestamp": "2026-01-28T10:00:30Z"}
        ],
        "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
    }
    
    response2 = requests.post(f"{BASE_URL}/honeypot", json=turn2_payload, headers=HEADERS)
    result2 = response2.json()
    print(f"   Turn 2 - Messages Exchanged: {result2.get('engagementMetrics', {}).get('totalMessagesExchanged')}")
    print(f"   Turn 2 - Agent: {result2.get('agentResponse', 'N/A')}")
    print(f"   Turn 2 - UPI IDs Found: {result2.get('extractedIntelligence', {}).get('upiIds')}")
    print(f"   Turn 2 - Phone Numbers: {result2.get('extractedIntelligence', {}).get('phoneNumbers')}")


def main():
    print("=" * 60)
    print("🍯 HONEYPOT API LOCAL TEST")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Using API Key: {API_KEY[:10]}...")
    
    try:
        if not test_health():
            print("\n❌ Server is not running! Start it with: python -m app.main")
            return
        
        test_auth()
        test_scam_detection()
        test_multi_turn_conversation()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server!")
        print("   Make sure the server is running:")
        print("   python -m app.main")


if __name__ == "__main__":
    main()
