# ===========================================
# Scam Detection Module
# ===========================================
# WHY: We need to identify if an incoming message is a scam
# before activating our AI agent.
#
# Detection Strategy:
# 1. Keyword matching (fast, catches obvious scams)
# 2. Pattern analysis (regex for account numbers, links)
# 3. Behavioral indicators (urgency, threats, requests)
# ===========================================

import re
from typing import Tuple, List
from app.models import Message, ExtractedIntelligence


class ScamDetector:
    """
    Detects scam intent in messages using multiple techniques.
    
    WHY multiple techniques:
    - No single method catches everything
    - Layered approach = higher accuracy
    - Different scams use different tactics
    """
    
    # ----- Scam Indicator Keywords -----
    # WHY these categories: Based on real-world scam patterns
    
    URGENCY_KEYWORDS = [
        "urgent", "immediately", "right now", "today only", "expires",
        "last chance", "act now", "hurry", "limited time", "deadline",
        "within 24 hours", "asap", "emergency"
    ]
    
    THREAT_KEYWORDS = [
        "blocked", "suspended", "terminated", "closed", "frozen",
        "legal action", "police", "arrest", "penalty", "fine",
        "case filed", "court", "lawsuit", "investigation"
    ]
    
    REQUEST_KEYWORDS = [
        "verify", "confirm", "update", "share", "send",
        "provide", "enter", "submit", "click", "download"
    ]
    
    SENSITIVE_DATA_KEYWORDS = [
        "otp", "pin", "password", "cvv", "account number",
        "upi", "bank details", "card number", "aadhar", "pan",
        "credit card", "debit card", "netbanking"
    ]
    
    FINANCIAL_KEYWORDS = [
        "lottery", "prize", "winner", "cashback", "refund",
        "loan", "insurance", "kyc", "investment", "returns",
        "profit", "guaranteed", "double your money", "congratulations",
        "won", "lakhs", "crores", "free money", "claim your"
    ]
    
    IMPERSONATION_KEYWORDS = [
        "rbi", "reserve bank", "income tax", "government",
        "sbi", "hdfc", "icici", "axis", "bank manager",
        "customer care", "support team", "official"
    ]
    
    def __init__(self):
        """Initialize the scam detector with compiled patterns."""
        
        # Compile regex patterns for better performance
        # WHY regex: Catches structured data like account numbers
        
        # UPI ID pattern: username@bankname
        self.upi_pattern = re.compile(
            r'[a-zA-Z0-9._-]+@[a-zA-Z]+',
            re.IGNORECASE
        )
        
        # Phone number patterns (Indian format)
        self.phone_pattern = re.compile(
            r'(?:\+91[-\s]?)?[6-9]\d{9}|\d{10}'
        )
        
        # Bank account patterns (various formats)
        self.bank_account_pattern = re.compile(
            r'\b\d{9,18}\b|\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{0,6}\b'
        )
        
        # URL pattern
        self.url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+'
        )
    
    def detect(self, message: str, conversation_history: List[Message] = None) -> Tuple[bool, float, List[str]]:
        """
        Analyze message for scam intent.
        
        Args:
            message: The message text to analyze
            conversation_history: Previous messages for context
        
        Returns:
            Tuple of (is_scam, confidence_score, reasons)
        
        WHY return confidence + reasons:
        - Confidence: Threshold-based decisions
        - Reasons: Agent notes for final report
        """
        message_lower = message.lower()
        reasons = []
        score = 0.0
        
        # ----- Check 1: Urgency Indicators -----
        # WHY: Scammers create panic to bypass rational thinking
        urgency_found = [kw for kw in self.URGENCY_KEYWORDS if kw in message_lower]
        if urgency_found:
            score += 0.15
            reasons.append(f"Urgency tactics: {', '.join(urgency_found[:3])}")
        
        # ----- Check 2: Threat Indicators -----
        # WHY: Scammers use fear of consequences
        threats_found = [kw for kw in self.THREAT_KEYWORDS if kw in message_lower]
        if threats_found:
            score += 0.20
            reasons.append(f"Threatening language: {', '.join(threats_found[:3])}")
        
        # ----- Check 3: Requests for Sensitive Data -----
        # WHY: Legitimate services don't ask for passwords via SMS
        requests_found = [kw for kw in self.REQUEST_KEYWORDS if kw in message_lower]
        sensitive_found = [kw for kw in self.SENSITIVE_DATA_KEYWORDS if kw in message_lower]
        
        if requests_found and sensitive_found:
            score += 0.25
            reasons.append(f"Requesting sensitive info: {', '.join(sensitive_found[:3])}")
        elif sensitive_found:
            score += 0.15
            reasons.append(f"Mentions sensitive data: {', '.join(sensitive_found[:3])}")
        
        # ----- Check 4: Financial Bait -----
        # WHY: "Free money" is a classic scam hook
        financial_found = [kw for kw in self.FINANCIAL_KEYWORDS if kw in message_lower]
        if financial_found:
            score += 0.25  # Increased weight - lottery/prize scams are very common
            reasons.append(f"Financial bait: {', '.join(financial_found[:3])}")
            
            # Extra boost if they mention sending money/fees
            if any(word in message_lower for word in ['send', 'transfer', 'fee', 'processing', 'pay']):
                score += 0.15
                reasons.append("Requesting payment/fee (advance fee fraud)")
        
        # ----- Check 5: Impersonation -----
        # WHY: Scammers pretend to be banks/government
        impersonation_found = [kw for kw in self.IMPERSONATION_KEYWORDS if kw in message_lower]
        if impersonation_found:
            score += 0.15
            reasons.append(f"Possible impersonation: {', '.join(impersonation_found[:3])}")
        
        # ----- Check 6: Suspicious Links -----
        # WHY: Phishing links are key scam infrastructure
        urls = self.url_pattern.findall(message)
        if urls:
            # Check if URLs look suspicious
            suspicious_url = False
            for url in urls:
                url_lower = url.lower()
                # Legitimate banks use their official domains
                if not any(legit in url_lower for legit in ['sbi.co.in', 'hdfcbank.com', 'icicibank.com', 'axisbank.com']):
                    suspicious_url = True
                    break
            
            if suspicious_url:
                score += 0.20
                reasons.append("Contains suspicious links")
        
        # ----- Check 7: Context from History -----
        # WHY: Multi-turn scams reveal intent over time
        if conversation_history:
            history_text = " ".join([m.text.lower() for m in conversation_history])
            
            # If history shows escalating requests, increase score
            if any(kw in history_text for kw in self.SENSITIVE_DATA_KEYWORDS):
                score += 0.10
                reasons.append("Previous messages requested sensitive data")
        
        # Cap the score at 1.0
        score = min(score, 1.0)
        
        # Determine if it's a scam based on threshold
        is_scam = score >= 0.3  # Lower threshold - better to engage than miss
        
        return is_scam, score, reasons
    
    def extract_intelligence(self, message: str) -> ExtractedIntelligence:
        """
        Extract actionable intelligence from message.
        
        WHY separate from detection:
        - Detection = Is it a scam?
        - Extraction = What data did we find?
        
        We extract from EVERY message to accumulate intel.
        """
        intel = ExtractedIntelligence()
        
        # Extract UPI IDs
        upi_matches = self.upi_pattern.findall(message)
        intel.upiIds = list(set(upi_matches))
        
        # Extract phone numbers
        phone_matches = self.phone_pattern.findall(message)
        # Format phone numbers consistently
        formatted_phones = []
        for phone in phone_matches:
            clean_phone = re.sub(r'[-\s]', '', phone)
            if len(clean_phone) >= 10:
                formatted_phones.append(clean_phone)
        intel.phoneNumbers = list(set(formatted_phones))
        
        # Extract bank account numbers (be careful with false positives)
        account_matches = self.bank_account_pattern.findall(message)
        # Filter out likely false positives (too short or common numbers)
        valid_accounts = [acc for acc in account_matches if len(acc.replace('-', '').replace(' ', '')) >= 9]
        intel.bankAccounts = list(set(valid_accounts))
        
        # Extract URLs
        url_matches = self.url_pattern.findall(message)
        intel.phishingLinks = list(set(url_matches))
        
        # Extract suspicious keywords found
        message_lower = message.lower()
        all_keywords = (
            self.URGENCY_KEYWORDS + 
            self.THREAT_KEYWORDS + 
            self.SENSITIVE_DATA_KEYWORDS
        )
        found_keywords = [kw for kw in all_keywords if kw in message_lower]
        intel.suspiciousKeywords = list(set(found_keywords))
        
        return intel


# Create global detector instance
scam_detector = ScamDetector()
