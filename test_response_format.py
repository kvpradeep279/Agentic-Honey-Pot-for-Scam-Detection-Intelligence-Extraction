"""
Simple test to verify API response format matches spec from Documents/doc.txt

Expected Response Format (Section 8):
{
  "status": "success",
  "reply": "Agent response here"
}

Callback Format (Section 12):
{
  "sessionId": "session-id",
  "scamDetected": true,
  "totalMessagesExchanged": 1,
  "extractedIntelligence": {...},
  "agentNotes": "..."
}
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:8005/honeypot"
API_KEY = "hp-kv-scam-detect-2026-x7k9m2p4"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

# Test 1: Simple bank scam message
print_section("TEST 1: Simple Bank Scam Message")

payload = {
    "sessionId": "test-format-001",
    "message": {
        "sender": "scammer",
        "text": "Your SBI bank account will be blocked today. Click here to verify: http://fake-sbi.com",
        "timestamp": int(time.time() * 1000)
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

print("\n📨 REQUEST PAYLOAD:")
print(json.dumps(payload, indent=2))

response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)

print(f"\n✅ STATUS CODE: {response.status_code}")
print("\n📩 RESPONSE:")
print(json.dumps(response.json(), indent=2))

# Verify response format
resp_json = response.json()
required_fields = ["status", "reply"]
print("\n🔍 FORMAT VALIDATION:")

all_valid = True
for field in required_fields:
    if field in resp_json:
        print(f"  ✅ '{field}' present: {resp_json[field]}")
    else:
        print(f"  ❌ '{field}' MISSING")
        all_valid = False

if all_valid:
    print("\n✅ RESPONSE FORMAT MATCHES SPEC! (status + reply)")
else:
    print("\n❌ RESPONSE FORMAT DOES NOT MATCH SPEC")

# Test 2: Follow-up message (multi-turn)
print_section("TEST 2: Multi-Turn Conversation (Follow-up)")

payload2 = {
    "sessionId": "test-format-001",
    "message": {
        "sender": "scammer",
        "text": "Send Rs 5000 to our UPI: bank.verify@ybl to unlock your account",
        "timestamp": int(time.time() * 1000) + 1000
    },
    "conversationHistory": [
        {
            "sender": "scammer",
            "text": "Your SBI bank account will be blocked today. Click here to verify: http://fake-sbi.com",
            "timestamp": int(time.time() * 1000)
        },
        {
            "sender": "agent",
            "text": "Oh no! My account is blocked? But I just used it yesterday. What should I do?",
            "timestamp": int(time.time() * 1000) + 500
        }
    ],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

print("\n📨 REQUEST PAYLOAD (with conversation history):")
print(json.dumps(payload2, indent=2)[:400] + "... [truncated]")

response2 = requests.post(API_URL, headers=HEADERS, json=payload2, timeout=30)

print(f"\n✅ STATUS CODE: {response2.status_code}")
print("\n📩 RESPONSE:")
resp2_json = response2.json()
print(json.dumps(resp2_json, indent=2))

print("\n🔍 FORMAT VALIDATION (Multi-turn):")
all_valid2 = True
for field in required_fields:
    if field in resp2_json:
        print(f"  ✅ '{field}' present")
    else:
        print(f"  ❌ '{field}' MISSING")
        all_valid2 = False

if all_valid2:
    print("\n✅ MULTI-TURN RESPONSE FORMAT MATCHES SPEC!")
else:
    print("\n❌ MULTI-TURN FORMAT DOES NOT MATCH SPEC")

# Summary
print_section("SUMMARY")
print(f"\n✅ Single Message Test: {'PASS' if all_valid else 'FAIL'}")
print(f"✅ Multi-Turn Test: {'PASS' if all_valid2 else 'FAIL'}")

if all_valid and all_valid2:
    print("\n🎉 ALL FORMAT TESTS PASSED!")
    print("   Response format matches Documents/doc.txt specification")
else:
    print("\n⚠️  SOME FORMAT VALIDATION FAILED")
    print("   Check the response structure against spec")

print("\n" + "="*70)
