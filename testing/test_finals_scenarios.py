"""
Finals Test Script - Tests Exact Sample Scenarios from Evaluation Docs
=======================================================================
This tests the 3 sample scenarios to verify our extraction works correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scam_detector import scam_detector
from app.models import ExtractedIntelligence

def print_separator():
    print("=" * 70)

def test_extraction(name: str, message: str, expected: dict):
    """Test intelligence extraction against expected values"""
    print(f"\n🧪 TEST: {name}")
    print("-" * 70)
    print(f"Message: {message[:80]}...")
    
    # Detect scam
    is_scam, confidence, reasons = scam_detector.detect(message)
    print(f"Scam Detected: {is_scam} (confidence: {confidence:.2f})")
    
    # Extract intelligence
    intel = scam_detector.extract_intelligence(message)
    
    # Check each expected item
    passed = True
    results = []
    
    for data_type, fake_values in expected.items():
        if not fake_values:
            continue
            
        # Get extracted values for this type
        extracted = getattr(intel, data_type, [])
        
        for fake_value in fake_values:
            # Evaluation logic: any(fake_value in str(v) for v in extracted_values)
            found = any(fake_value in str(v) for v in extracted)
            if not found:
                # Also check reverse: extracted value in fake
                found = any(str(v) in fake_value for v in extracted)
            
            status = "✅" if found else "❌"
            results.append(f"  {status} {data_type}: '{fake_value}' -> Found: {found}")
            if not found:
                passed = False
                results.append(f"     Extracted {data_type}: {extracted}")
    
    for r in results:
        print(r)
    
    print(f"\nResult: {'✅ PASSED' if passed else '❌ FAILED'}")
    return passed

def main():
    print_separator()
    print("🏆 FINALS SAMPLE SCENARIOS - EXTRACTION TEST")
    print_separator()
    
    passed = 0
    failed = 0
    
    # SCENARIO 1: Bank Fraud
    if test_extraction(
        "Bank Fraud Detection",
        "URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity. Call +91-9876543210 or send to scammer.fraud@fakebank. Account: 1234567890123456",
        {
            "bankAccounts": ["1234567890123456"],
            "upiIds": ["scammer.fraud@fakebank"],
            "phoneNumbers": ["+91-9876543210"]
        }
    ):
        passed += 1
    else:
        failed += 1
    
    # SCENARIO 2: UPI Fraud
    if test_extraction(
        "UPI Fraud Multi-turn",
        "Congratulations! You have won a cashback of Rs. 5000 from Paytm. To claim your reward, please verify your UPI details at cashback.scam@fakeupi. Contact: +91-8765432109",
        {
            "upiIds": ["cashback.scam@fakeupi"],
            "phoneNumbers": ["+91-8765432109"]
        }
    ):
        passed += 1
    else:
        failed += 1
    
    # SCENARIO 3: Phishing
    if test_extraction(
        "Phishing Link Detection",
        "You have been selected for iPhone 15 Pro at just Rs. 999! Click here to claim: http://amaz0n-deals.fake-site.com/claim?id=12345. Contact: offers@fake-amazon-deals.com",
        {
            "phishingLinks": ["http://amaz0n-deals.fake-site.com/claim?id=12345"],
            "emailAddresses": ["offers@fake-amazon-deals.com"]
        }
    ):
        passed += 1
    else:
        failed += 1
    
    # Summary
    print_separator()
    print(f"📊 RESULTS: {passed}/{passed + failed} scenarios passed")
    print_separator()
    
    if failed == 0:
        print("🎉 ALL SCENARIOS PASSED! Ready for finals!")
    else:
        print(f"⚠️ {failed} scenarios need attention!")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
