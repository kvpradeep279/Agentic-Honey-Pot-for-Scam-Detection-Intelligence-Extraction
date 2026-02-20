"""
═══════════════════════════════════════════════════════════════════════════════
15 SCENARIO MEGA TEST - FINALS VALIDATION
═══════════════════════════════════════════════════════════════════════════════
Tests all 15 core scam types against deployed API + local detection.

From Finals Documents:
1. Bank Fraud / KYC
2. UPI Fraud
3. Phishing Links
4. Government Impersonation
5. Lottery / Prize
6. Job Scam
7. Investment / Crypto
8. Delivery / Customs
9. Tech Support
10. Electricity / Utility Bill
11. Insurance
12. Loan Approval
13. Refund Scam
14. Income Tax
15. Digital Arrest / CBI
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Import local modules for unit testing
from app.scam_detector import scam_detector
from app.models import Message

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════
API_URL = os.getenv("API_BASE_URL", "https://agentic-honey-pot-for-scam-detection.onrender.com/honeypot")
API_KEY = os.getenv("API_KEY", "supersecret123")
CALLBACK_URL = "https://httpbin.org/post"  # Dummy for testing

# ═══════════════════════════════════════════════════════════════════════════
# 15 CORE SCENARIOS - Based on Finals Documentation
# ═══════════════════════════════════════════════════════════════════════════
FIFTEEN_SCENARIOS = [
    {
        "id": 1,
        "name": "Bank Fraud / KYC",
        "message": "URGENT: Your SBI account 1234567890123456 is blocked! Update KYC immediately. Call +91-9876543210. Send to verify@ybl",
        "fakeData": {
            "bankAccounts": ["1234567890123456"],
            "phoneNumbers": ["+91-9876543210", "9876543210"],
            "upiIds": ["verify@ybl"]
        }
    },
    {
        "id": 2,
        "name": "UPI Fraud",
        "message": "Congratulations! You won Rs.5000 Paytm cashback! To claim, send Rs.99 to cashback.claim@okicici. Contact: 8765432109",
        "fakeData": {
            "upiIds": ["cashback.claim@okicici"],
            "phoneNumbers": ["8765432109"]
        }
    },
    {
        "id": 3,
        "name": "Phishing Link",
        "message": "Your Amazon account locked! Verify at http://amaz0n-secure.fakesite.com/verify. Contact: support@fake-amazon.in",
        "fakeData": {
            "phishingLinks": ["http://amaz0n-secure.fakesite.com/verify"],
            "emailAddresses": ["support@fake-amazon.in"]
        }
    },
    {
        "id": 4,
        "name": "Government Impersonation",
        "message": "CBI NOTICE: Case filed against your Aadhaar. Pay fine Rs.50000 to cbi.fine@oksbi or face arrest! Call: 7654321098",
        "fakeData": {
            "upiIds": ["cbi.fine@oksbi"],
            "phoneNumbers": ["7654321098"]
        }
    },
    {
        "id": 5,
        "name": "Lottery / Prize Scam",
        "message": "WINNER! You won Rs.50 LAKH in KBC lottery! Pay Rs.10000 processing fee to kbc.winner@ybl. Call: 9999888877",
        "fakeData": {
            "upiIds": ["kbc.winner@ybl"],
            "phoneNumbers": ["9999888877"]
        }
    },
    {
        "id": 6,
        "name": "Job Scam",
        "message": "Selected for Rs.60000/month work from home job! Pay Rs.2000 registration to hr.jobs@paytm. Email: hr@fake-hiring.com",
        "fakeData": {
            "upiIds": ["hr.jobs@paytm"],
            "emailAddresses": ["hr@fake-hiring.com"]
        }
    },
    {
        "id": 7,
        "name": "Investment / Crypto Scam",
        "message": "GUARANTEED 200% returns on crypto! Invest Rs.50000 to account 9876543210987654. UPI: crypto.invest@ybl. Limited slots!",
        "fakeData": {
            "bankAccounts": ["9876543210987654"],
            "upiIds": ["crypto.invest@ybl"]
        }
    },
    {
        "id": 8,
        "name": "Delivery / Customs Scam",
        "message": "FedEx: Your parcel held at customs. Illegal items detected. Pay Rs.25000 to release@fedex.ybl or arrest! Call: 9876501234",
        "fakeData": {
            "upiIds": ["release@fedex.ybl"],
            "phoneNumbers": ["9876501234"]
        }
    },
    {
        "id": 9,
        "name": "Tech Support Scam",
        "message": "Microsoft Alert: Virus detected on your PC! Install TeamViewer for remote fix. Call immediately: 1800-234-5678",
        "fakeData": {
            "phoneNumbers": ["1800-234-5678", "18002345678"]
        }
    },
    {
        "id": 10,
        "name": "Electricity / Utility Bill Scam",
        "message": "BESCOM: Your electricity disconnecting in 2 hours! Pay Rs.3500 to bescom.bill@ybl immediately. Contact: 9988776655",
        "fakeData": {
            "upiIds": ["bescom.bill@ybl"],
            "phoneNumbers": ["9988776655"]
        }
    },
    {
        "id": 11,
        "name": "Insurance Scam",
        "message": "LIC Policy LAPSING TODAY! Pay premium Rs.15000 to lic.premium@okaxis immediately or lose nominee benefits!",
        "fakeData": {
            "upiIds": ["lic.premium@okaxis"]
        }
    },
    {
        "id": 12,
        "name": "Loan Approval Scam",
        "message": "Pre-approved Rs.10 Lakh personal loan! Pay Rs.5000 processing fee to loan.sanction@ybl. Limited time offer!",
        "fakeData": {
            "upiIds": ["loan.sanction@ybl"]
        }
    },
    {
        "id": 13,
        "name": "Refund Scam",
        "message": "Amazon Refund Rs.2500 pending! Pay Rs.50 verification fee to refund.claim@paytm for instant credit. Call: 8877665544",
        "fakeData": {
            "upiIds": ["refund.claim@paytm"],
            "phoneNumbers": ["8877665544"]
        }
    },
    {
        "id": 14,
        "name": "Income Tax Scam",
        "message": "IT Department: Rs.25000 refund pending. Click http://incometax-refund.fakegovt.in and provide PAN. Email: refund@fake-it.gov.in",
        "fakeData": {
            "phishingLinks": ["http://incometax-refund.fakegovt.in"],
            "emailAddresses": ["refund@fake-it.gov.in"]
        }
    },
    {
        "id": 15,
        "name": "Digital Arrest / CBI Scam",
        "message": "URGENT: Digital arrest warrant issued! Your Aadhaar linked to money laundering. Transfer Rs.100000 to account 1111222233334444 or face 7 years jail! Call CBI: 9123456789",
        "fakeData": {
            "bankAccounts": ["1111222233334444"],
            "phoneNumbers": ["9123456789"]
        }
    }
]

# ═══════════════════════════════════════════════════════════════════════════
# TEST FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def test_local_detection(scenario):
    """Test local ScamDetector for detection + extraction"""
    results = {
        "scenario": scenario["name"],
        "detection": False,
        "confidence": 0.0,
        "extraction": {},
        "extraction_score": 0,
        "extraction_max": 0
    }
    
    # Detection
    is_scam, conf, reasons = scam_detector.detect(scenario["message"])
    results["detection"] = is_scam
    results["confidence"] = conf
    
    # Extraction
    if is_scam:
        intel = scam_detector.extract_intelligence(scenario["message"])
        
        for data_type, fake_values in scenario["fakeData"].items():
            results["extraction_max"] += len(fake_values)
            extracted_list = getattr(intel, data_type, [])
            
            found_count = 0
            for fake_val in fake_values:
                # Check if extracted contains expected
                found = any(fake_val in str(v) or str(v) in fake_val for v in extracted_list)
                if found:
                    found_count += 1
            
            results["extraction"][data_type] = {
                "expected": fake_values,
                "extracted": extracted_list,
                "found": found_count
            }
            results["extraction_score"] += found_count
    
    return results


def test_api_single(scenario):
    """Test single scenario against deployed API"""
    session_id = f"test-15-scenario-{scenario['id']}-{int(time.time())}"
    
    payload = {
        "sessionId": session_id,
        "callbackUrl": CALLBACK_URL,
        "message": {
            "role": "scammer",
            "content": scenario["message"]
        },
        "conversationHistory": []
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    start = time.time()
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            return {
                "scenario": scenario["name"],
                "success": True,
                "scamDetected": data.get("scamDetected", False),
                "confidence": data.get("confidenceLevel", 0),
                "response": data.get("response", {}).get("content", "")[:100],
                "intelligence": data.get("extractedIntelligence", {}),
                "elapsed": elapsed,
                "error": None
            }
        else:
            return {
                "scenario": scenario["name"],
                "success": False,
                "error": f"HTTP {resp.status_code}: {resp.text[:100]}"
            }
    except Exception as e:
        return {
            "scenario": scenario["name"],
            "success": False,
            "error": str(e)
        }


def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def main():
    print_header("15 SCENARIO MEGA TEST - FINALS VALIDATION")
    print(f"Testing: {len(FIFTEEN_SCENARIOS)} scenarios")
    print(f"API URL: {API_URL}")
    print(f"Callback: {CALLBACK_URL}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # PART 1: LOCAL UNIT TESTS (Fast)
    # ═══════════════════════════════════════════════════════════════════════
    print_header("PART 1: LOCAL DETECTION & EXTRACTION (Unit Tests)")
    
    local_results = []
    local_detected = 0
    local_extracted = 0
    local_max_extract = 0
    
    for scenario in FIFTEEN_SCENARIOS:
        result = test_local_detection(scenario)
        local_results.append(result)
        
        status = "✅" if result["detection"] else "❌"
        print(f"{status} [{scenario['id']:2d}] {scenario['name']:<30} conf={result['confidence']:.2f}")
        
        if result["detection"]:
            local_detected += 1
            local_extracted += result["extraction_score"]
            local_max_extract += result["extraction_max"]
            
            # Show extraction details
            for dtype, info in result.get("extraction", {}).items():
                found = info["found"]
                total = len(info["expected"])
                if found < total:
                    print(f"      ⚠️ {dtype}: {found}/{total} - Expected: {info['expected']}, Got: {info['extracted']}")
    
    local_detect_pct = (local_detected / len(FIFTEEN_SCENARIOS)) * 100
    local_extract_pct = (local_extracted / local_max_extract * 100) if local_max_extract > 0 else 0
    
    print(f"\n📊 LOCAL RESULTS:")
    print(f"   Detection: {local_detected}/15 ({local_detect_pct:.0f}%)")
    print(f"   Extraction: {local_extracted}/{local_max_extract} ({local_extract_pct:.0f}%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # PART 2: API INTEGRATION TESTS (Concurrent)
    # ═══════════════════════════════════════════════════════════════════════
    print_header("PART 2: API INTEGRATION TESTS (Deployed)")
    
    # First check if API is up
    try:
        health = requests.get(API_URL.replace("/honeypot", "/health"), timeout=10)
        if health.status_code == 200:
            print("✅ API is healthy")
        else:
            print(f"⚠️ API health check returned: {health.status_code}")
    except Exception as e:
        print(f"⚠️ API health check failed: {e}")
    
    print("\nTesting scenarios concurrently...")
    
    api_results = []
    api_detected = 0
    
    # Run 3 at a time to avoid rate limits
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(test_api_single, s): s for s in FIFTEEN_SCENARIOS}
        
        for future in as_completed(futures):
            result = future.result()
            api_results.append(result)
            
            if result.get("success"):
                status = "✅" if result.get("scamDetected") else "⚠️"
                if result.get("scamDetected"):
                    api_detected += 1
                print(f"{status} {result['scenario']:<30} scam={result['scamDetected']} time={result['elapsed']:.2f}s")
            else:
                print(f"❌ {result['scenario']:<30} ERROR: {result.get('error', 'Unknown')[:50]}")
            
            time.sleep(0.3)  # Small delay between results
    
    api_pct = (api_detected / len(FIFTEEN_SCENARIOS)) * 100
    
    print(f"\n📊 API RESULTS:")
    print(f"   Detected: {api_detected}/15 ({api_pct:.0f}%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # FINAL SCORE PROJECTION
    # ═══════════════════════════════════════════════════════════════════════
    print_header("FINAL SCORE PROJECTION")
    
    # Based on Feb 19 scoring:
    # - Scam Detection: 20 pts
    # - Intelligence Extraction: 30 pts
    # - Conversation Quality: 30 pts
    # - Engagement: 10 pts
    # - Response Structure: 10 pts
    
    detect_score = 20 if local_detect_pct >= 90 else int(20 * local_detect_pct / 100)
    intel_score = 30 if local_extract_pct >= 90 else int(30 * local_extract_pct / 100)
    
    # Conservative estimates for conversation/engagement (need multi-turn to test)
    convo_score = 25  # Assuming good performance
    engage_score = 8
    struct_score = 9  # scamDetected + confidenceLevel + scamType
    
    projected = detect_score + intel_score + convo_score + engage_score + struct_score
    
    print(f"📈 Projected Score Breakdown:")
    print(f"   Scam Detection:      {detect_score}/20")
    print(f"   Intelligence:        {intel_score}/30")
    print(f"   Conversation:        {convo_score}/30 (estimate)")
    print(f"   Engagement:          {engage_score}/10 (estimate)")
    print(f"   Response Structure:  {struct_score}/10")
    print(f"   ───────────────────────────────")
    print(f"   PROJECTED TOTAL:     {projected}/100")
    
    if local_detect_pct == 100 and local_extract_pct >= 90:
        print("\n🏆 EXCELLENT! Ready for Finals!")
    elif local_detect_pct >= 90:
        print("\n✅ GOOD! Minor extraction improvements needed.")
    else:
        print("\n⚠️ NEEDS WORK! Fix detection gaps.")
    
    # Return success if >= 90% detection
    return local_detect_pct >= 90


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
