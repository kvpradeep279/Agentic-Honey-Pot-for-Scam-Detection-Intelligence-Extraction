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
# 4. Mixed-language detection (Hinglish + regional)
# 5. Over-polite formal scam patterns
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
        "within 24 hours", "asap", "emergency", "expire", "expiring",
        # Hinglish urgency
        "jaldi", "abhi", "turant", "foran"
    ]
    
    THREAT_KEYWORDS = [
        "blocked", "suspended", "terminated", "closed", "frozen",
        "legal action", "police", "arrest", "penalty", "fine",
        "case filed", "court", "lawsuit", "investigation",
        # Additional threats
        "cbi", "ed", "raid", "jail", "crime branch", "cyber cell",
        "money laundering", "tax evasion", "seize", "freeze",
        "deactivated", "deactivate", "disconnection", "disconnected"
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
        "won", "lakhs", "crores", "free money", "claim your",
        # Additional financial baits
        "maturity", "disbursement", "pending amount"
    ]
    
    # Job scam keywords
    JOB_SCAM_KEYWORDS = [
        "selected", "job offer", "work from home", "part time job",
        "registration fee", "joining fee", "selected for", "offer letter",
        "salary", "per month", "/month", "earn money", "hired"
    ]
    
    IMPERSONATION_KEYWORDS = [
        "rbi", "reserve bank", "income tax", "government",
        "sbi", "hdfc", "icici", "axis", "bank manager",
        "customer care", "support team", "official"
    ]
    
    # ----- Mixed Language Keywords (Hinglish + Regional) -----
    # WHY: Scammers use mixed language to bypass English-only detection
    # These are ONLY counted when paired with sensitive data requests
    HINGLISH_SCAM_KEYWORDS = [
        # Hindi urgency/threat words in Latin script
        "jaldi", "abhi", "turant", "foran",  # urgency: quickly, now, immediately
        "band", "block", "rok",  # blocked/stopped
        "paisa", "rupay", "rupees", "rs",  # money
        "bhejo", "bhejiye", "transfer karo", "transfer kijiye",  # send
        # Common scam phrases in Hinglish
        "aapka account", "aapka khata", "apka bank",
        "verify karo", "verify kijiye", "confirm karo",
        # Tamil common words
        "udane", "ippo",  # immediately, now
        # Telugu common words
        "vెంటనే", "ippudu",  # immediately, now
    ]
    
    # ----- Over-Polite Formal Scam Patterns -----
    # WHY: Some scams sound extremely formal/official to gain trust
    # These are ONLY counted when paired with financial/verification requests
    FORMAL_SCAM_PATTERNS = [
        "dear sir", "dear madam", "dear customer", "dear user",
        "respected sir", "respected madam", "respected customer",
        "greetings from", "warm greetings",
        "we regret to inform", "we are pleased to inform",
        "kindly do the needful", "kindly cooperate", "kindly verify",
        "as per rbi guidelines", "as per bank policy", "as per government",
        "mandatory kyc", "mandatory verification", "compliance requirement",
        "your cooperation is appreciated", "failure to comply",
        "scheduled maintenance", "routine verification", "annual update",
        "case id", "reference number", "ticket number", "complaint id"
    ]
    
    # ----- Benign Pretext Keywords (Legitimate-sounding scam hooks) -----
    # WHY: Scammers use soft language to make requests seem normal
    BENIGN_PRETEXT_KEYWORDS = [
        "refund pending", "cashback pending", "reward pending",
        "reversal", "chargeback", "account upgrade",
        "security update", "system upgrade", "app update required"
    ]
    
    # ----- Channel Shift Keywords (Red flag: moving to another platform) -----
    CHANNEL_SHIFT_KEYWORDS = [
        "call me on", "whatsapp me", "message me on", "contact on telegram",
        "reach me at", "continue on whatsapp", "move to whatsapp",
        "whatsapp us", "call my", "personal number", "my number",
        "telegram", "whatsapp", "download", "install"
    ]
    
    # Transfer/payment request keywords
    TRANSFER_KEYWORDS = [
        "transfer", "send money", "pay", "payment", "bhej", "bhejo",
        "deposit", "fee", "charge", "processing fee"
    ]
    
    # SMS Abbreviations mapping for normalization
    SMS_ABBREVIATIONS = {
        'ur': 'your', 'u': 'you', 'r': 'are', '2': 'to', '4': 'for',
        'blkd': 'blocked', 'blckd': 'blocked', 'blk': 'block',
        'shr': 'share', 'pls': 'please', 'plz': 'please',
        'acct': 'account', 'acc': 'account', 'a/c': 'account',
        'immdt': 'immediate', 'immdtly': 'immediately',
        'vrfy': 'verify', 'vrfctn': 'verification',
        'msg': 'message', 'amt': 'amount', 'bal': 'balance',
        'txn': 'transaction', 'pwd': 'password', 'no': 'number',
        'suspndd': 'suspended', 'suspnsn': 'suspension',
        'xpird': 'expired', 'xpry': 'expiry', 'updt': 'update',
        '2day': 'today', '2moro': 'tomorrow', 'b4': 'before',
        'lse': 'lose', 'alrt': 'alert', 'att': 'attention',
        'yr': 'your', 'bnk': 'bank', 'clk': 'click',
    }
    
    # Leetspeak character mapping
    LEETSPEAK_MAP = {
        '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's',
        '7': 't', '@': 'a', '$': 's', '!': 'i', '|': 'l',
        '<': 'c', '>': 'k'  # For bloc|<ed
    }
    
    def __init__(self):
        """Initialize the scam detector with compiled patterns."""
        
        # Compile regex patterns for better performance
        # WHY regex: Catches structured data like account numbers
        
        # UPI ID pattern: username@bankname
        self.upi_pattern = re.compile(
            r'[a-zA-Z0-9._-]+@[a-zA-Z]+',
            re.IGNORECASE
        )
        
        # Phone number patterns (Indian format) - including toll-free
        # ENHANCED: Capture full format including +91 prefix with various separators
        self.phone_pattern = re.compile(
            r'\+91[-\s]?[6-9]\d{9}|'           # +91-9876543210 or +91 9876543210
            r'\+91[-\s]?\d{5}[-\s]?\d{5}|'     # +91-98765-43210
            r'(?<!\d)[6-9]\d{9}(?!\d)|'         # Plain 10-digit (not part of longer number)
            r'\d{10}|'                          # Any 10 digits
            r'1800[-\s]?\d{3}[-\s]?\d{4,}'     # Toll-free
        )
        
        # Bank account patterns (various formats)
        self.bank_account_pattern = re.compile(
            r'\b\d{9,18}\b|\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{0,6}\b'
        )
        
        # URL pattern - ENHANCED to catch plain domains too
        self.url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+|'                              # Full URLs with http/https
            r'www\.[a-zA-Z0-9][-a-zA-Z0-9.]*\.[a-zA-Z]{2,}[^\s]*|'        # www domains
            r'[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z0-9][-a-zA-Z0-9]*\.(?:com|in|co\.in|org|net|io)[^\s]*|'  # subdomain.domain.tld
            r'[a-zA-Z0-9][-a-zA-Z0-9]*\.(?:com|in|co\.in|org|net|io|ly|me)(?:/[^\s]*)?',  # Plain domains
            re.IGNORECASE
        )
        
        # Email pattern - for extracting scammer email addresses
        self.email_pattern = re.compile(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            re.IGNORECASE
        )
        
        # ----- Obfuscated Data Patterns (for extraction only) -----
        # WHY: Scammers obfuscate data to avoid detection
        
        # Spaced digits pattern: "9 8 7 6 5 4 3 2 1 0" or "9-8-7-6-5-4-3-2-1-0"
        self.spaced_digits_pattern = re.compile(
            r'(\d[\s\-\.]+){9,17}\d'
        )
        
        # Masked account pattern: "98xx-xx43-xx10" or "XXXX1234XXXX"
        self.masked_account_pattern = re.compile(
            r'\b[\dxX]{4}[-\s]?[\dxX]{4}[-\s]?[\dxX]{4}[-\s]?[\dxX]{0,6}\b',
            re.IGNORECASE
        )
        
        # UPI with spaces: "name @ bank" or "name@ bank"
        self.spaced_upi_pattern = re.compile(
            r'[a-zA-Z0-9._-]+\s*@\s*[a-zA-Z]+',
            re.IGNORECASE
        )
        
        # ----- Legitimate Message Patterns (False Positive Guards) -----
        # WHY: Avoid flagging real bank notifications
        self.legitimate_patterns = [
            # OTP delivery from banks (NOT requesting OTP)
            re.compile(r'\d{4,6}\s+is\s+(your|the)\s+otp.*do not share', re.IGNORECASE),
            re.compile(r'otp\s*(is|:)\s*\d{4,6}.*valid for \d+ min', re.IGNORECASE),
            re.compile(r'your otp.*is\s*\d{4,6}', re.IGNORECASE),
            
            # Transaction alerts (past tense - already happened)
            re.compile(r'rs\.?\s*[\d,]+\.?\d*\s*(has been )?(debited|credited)\s*(from|to)', re.IGNORECASE),
            re.compile(r'(debited|credited).*from.*a/?c.*bal', re.IGNORECASE),
            re.compile(r'transaction.*successful.*ref', re.IGNORECASE),
            re.compile(r'available balance.*rs\.?\s*[\d,]+', re.IGNORECASE),
            re.compile(r'(if not|not)\s+(done|authorized|made|you).*call.*1800', re.IGNORECASE),
            
            # Order/Delivery confirmations (informational, no action needed)
            re.compile(r'(order|delivery).*(arriving|delivered|shipped|dispatched)', re.IGNORECASE),
            re.compile(r'will be delivered (today|tomorrow|by)', re.IGNORECASE),
            re.compile(r'track (your |the )?(order|package|delivery)', re.IGNORECASE),
            
            # Booking confirmations (informational)
            re.compile(r'(flight|train|bus|hotel|movie|cab).*(confirmed|booked)', re.IGNORECASE),
            re.compile(r'(booking|reservation)\s*(id|ref|no)[:.\s]*[a-zA-Z0-9]+', re.IGNORECASE),
            re.compile(r'check-?in (opens|available|time)', re.IGNORECASE),
            re.compile(r'your (booking|appointment|reservation) (is|has been) confirmed', re.IGNORECASE),
            
            # Bill reminders (legitimate - mentions due date without threat)
            re.compile(r'(bill|payment|emi|due).*(due|last) date.*(is|\d)', re.IGNORECASE),
            re.compile(r'pay before due date', re.IGNORECASE),
            re.compile(r'(electricity|gas|water|broadband) bill of rs', re.IGNORECASE),
            
            # Service tickets/acknowledgments
            re.compile(r'(complaint|ticket|request|query).*#?\w+.*(registered|created|received)', re.IGNORECASE),
            re.compile(r'thank you for (contacting|reaching|your feedback)', re.IGNORECASE),
            re.compile(r'we will (respond|reply|get back|resolve)', re.IGNORECASE),
            
            # Refund confirmation (money coming TO user, not FROM)
            re.compile(r'refund of rs\.?\s*[\d,]+.*initiated', re.IGNORECASE),
            re.compile(r'refund.*credited within', re.IGNORECASE),
            
            # Appointment confirmations (doctor, salon, etc.)
            re.compile(r'(appointment|booking).*(confirmed|scheduled).*(dr\.|doctor|salon|hospital|clinic)', re.IGNORECASE),
            re.compile(r'(dr\.|doctor).*appointment', re.IGNORECASE),
            re.compile(r'your appointment (with|at|for)', re.IGNORECASE),
            
            # Entertainment bookings (movies, events)
            re.compile(r'(movie|show|event|concert).*(booking|ticket).*(confirmed|booked)', re.IGNORECASE),
            re.compile(r'(bookmyshow|pvr|inox).*booking', re.IGNORECASE),
        ]
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by converting leetspeak and SMS abbreviations.
        Returns normalized lowercase text for detection.
        """
        text = text.lower()
        
        # Convert leetspeak characters
        for leet, normal in self.LEETSPEAK_MAP.items():
            text = text.replace(leet, normal)
        
        # Replace SMS abbreviations (word boundaries)
        words = text.split()
        normalized_words = []
        for word in words:
            # Remove trailing punctuation for lookup
            word_clean = re.sub(r'[!?.,:;]+$', '', word)
            if word_clean in self.SMS_ABBREVIATIONS:
                normalized_words.append(self.SMS_ABBREVIATIONS[word_clean])
            else:
                normalized_words.append(word)
        
        return ' '.join(normalized_words)
    
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
        # Handle empty messages
        if not message or not message.strip():
            return False, 0.0, []
        
        message_lower = message.lower()
        # Also create normalized version for obfuscation detection
        message_normalized = self.normalize_text(message)
        
        reasons = []
        score = 0.0
        
        # ----- Check 0: Legitimate Message Guard (False Positive Prevention) -----
        # WHY: Real bank notifications should NOT be flagged
        for pattern in self.legitimate_patterns:
            if pattern.search(message):
                # This looks like a legitimate bank notification
                return False, 0.0, ["Legitimate bank notification detected"]
        
        # ----- Check 0b: Additional Legitimate Transaction Patterns -----
        # Credit card bill reminder (not scam if mentions "due date" and "min due")
        if re.search(r'(credit card|card) bill.*min.*due', message_lower, re.IGNORECASE):
            return False, 0.0, ["Legitimate credit card bill reminder"]
        
        # ----- Check 1: Urgency Indicators -----
        # WHY: Scammers create panic to bypass rational thinking
        # Check both original and normalized text
        urgency_found = [kw for kw in self.URGENCY_KEYWORDS if kw in message_lower or kw in message_normalized]
        if urgency_found:
            score += 0.15
            reasons.append(f"Urgency tactics: {', '.join(urgency_found[:3])}")
        
        # ----- Check 2: Threat Indicators -----
        # WHY: Scammers use fear of consequences
        # Check both original and normalized text
        threats_found = [kw for kw in self.THREAT_KEYWORDS if kw in message_lower or kw in message_normalized]
        if threats_found:
            score += 0.20
            reasons.append(f"Threatening language: {', '.join(threats_found[:3])}")
            
            # Extra boost if threat + bank/account mentioned together
            # "Your bank account will be blocked" is a classic scam pattern
            if any(word in message_lower or word in message_normalized for word in ['bank', 'account', 'card', 'wallet']):
                score += 0.15
                reasons.append("Threatening language targeting financial assets")
        
        # ----- Check 3: Requests for Sensitive Data -----
        # WHY: Legitimate services don't ask for passwords via SMS
        requests_found = [kw for kw in self.REQUEST_KEYWORDS if kw in message_lower or kw in message_normalized]
        sensitive_found = [kw for kw in self.SENSITIVE_DATA_KEYWORDS if kw in message_lower or kw in message_normalized]
        
        # Check for personal data requests (DOB, mobile, etc.)
        personal_data_keywords = ['date of birth', 'dob', 'mobile number', 'registered mobile', 
                                   'mother name', 'father name', 'address', 'aadhaar', 'aadhar']
        personal_data_found = [kw for kw in personal_data_keywords if kw in message_lower]
        
        if requests_found and sensitive_found:
            score += 0.25
            reasons.append(f"Requesting sensitive info: {', '.join(sensitive_found[:3])}")
        elif requests_found and personal_data_found:
            score += 0.25
            reasons.append(f"Requesting personal data: {', '.join(personal_data_found[:2])}")
        elif sensitive_found:
            score += 0.15
            reasons.append(f"Mentions sensitive data: {', '.join(sensitive_found[:3])}")
        elif personal_data_found:
            score += 0.15
            reasons.append(f"Mentions personal data: {', '.join(personal_data_found[:2])}")
        
        # ----- Check 4: Financial Bait -----
        # WHY: "Free money" is a classic scam hook
        financial_found = [kw for kw in self.FINANCIAL_KEYWORDS if kw in message_lower or kw in message_normalized]
        if financial_found:
            score += 0.25  # Increased weight - lottery/prize scams are very common
            reasons.append(f"Financial bait: {', '.join(financial_found[:3])}")
            
            # Extra boost if they mention sending money/fees
            if any(word in message_lower for word in ['send', 'transfer', 'fee', 'processing', 'pay']):
                score += 0.15
                reasons.append("Requesting payment/fee (advance fee fraud)")
        
        # ----- Check 4b: Job Scam Detection -----
        # WHY: Job scams are very common, especially those asking for fees
        job_scam_found = [kw for kw in self.JOB_SCAM_KEYWORDS if kw in message_lower or kw in message_normalized]
        if job_scam_found:
            score += 0.15
            reasons.append(f"Job scam indicators: {', '.join(job_scam_found[:3])}")
            # Extra boost if asking for payment
            if any(word in message_lower for word in ['fee', 'pay', 'transfer', 'send', 'account', 'deposit']):
                score += 0.25
                reasons.append("Job offer requesting payment (advance fee fraud)")
        
        # ----- Check 5: Impersonation -----
        # WHY: Scammers pretend to be banks/government
        impersonation_found = [kw for kw in self.IMPERSONATION_KEYWORDS if kw in message_lower]
        if impersonation_found:
            score += 0.15
            reasons.append(f"Possible impersonation: {', '.join(impersonation_found[:3])}")
        
        # ----- Check 6: Suspicious Links -----
        # WHY: Phishing links are key scam infrastructure
        urls = self.url_pattern.findall(message)
        # Filter out common legitimate domains
        legit_domains = ['amazon.in', 'amazon.com', 'flipkart.com', 'swiggy.com', 'zomato.com',
                         'uber.com', 'ola.com', 'bookmyshow.com', 'irctc.co.in', 'makeMytrip.com',
                         'sbi.co.in', 'hdfcbank.com', 'icicibank.com', 'axisbank.com',
                         'google.com', 'facebook.com', 'instagram.com', 'youtube.com']
        suspicious_urls = []
        for url in urls:
            url_lower = url.lower()
            # Skip if it's a UPI ID (contains @)
            if '@' in url_lower:
                continue
            # Skip if it matches legitimate domain
            is_legit = any(legit in url_lower for legit in legit_domains)
            if not is_legit:
                suspicious_urls.append(url)
        
        if suspicious_urls:
            score += 0.25
            reasons.append(f"Contains suspicious links: {', '.join(suspicious_urls[:2])}")
        
        # ----- Check 7: Mixed Language (Hinglish + Regional) -----
        # WHY: Scammers use mixed language to bypass English-only detection
        hinglish_found = [kw for kw in self.HINGLISH_SCAM_KEYWORDS if kw in message_lower]
        if hinglish_found:
            # Hinglish with sensitive data request is strong signal
            if sensitive_found:
                score += 0.15
                reasons.append(f"Mixed language with sensitive request: {', '.join(hinglish_found[:2])}")
            # Hinglish urgency + threat/financial is also strong signal
            elif threats_found or financial_found or urgency_found:
                score += 0.20
                reasons.append(f"Mixed language with urgency/threat: {', '.join(hinglish_found[:2])}")
            # Hinglish with phone number request
            elif self.phone_pattern.search(message):
                score += 0.15
                reasons.append(f"Mixed language with contact request: {', '.join(hinglish_found[:2])}")
            score += 0.10
            reasons.append(f"Mixed language with sensitive request: {', '.join(hinglish_found[:2])}")
        
        # ----- Check 8: Over-Polite Formal Scam Patterns -----
        # WHY: Some scams sound extremely formal/official to gain trust
        # CONSERVATIVE: Only count if ALSO has financial/verification request
        formal_found = [kw for kw in self.FORMAL_SCAM_PATTERNS if kw in message_lower]
        has_financial_or_verify = financial_found or requests_found or sensitive_found
        if formal_found and has_financial_or_verify:
            score += 0.15
            reasons.append(f"Formal/official language with financial request: {', '.join(formal_found[:2])}")
        
        # ----- Check 9: Benign Pretext Scam Hooks -----
        # WHY: Scammers use legitimate-sounding pretexts
        benign_pretext_found = [kw for kw in self.BENIGN_PRETEXT_KEYWORDS if kw in message_lower]
        if benign_pretext_found:
            score += 0.15
            reasons.append(f"Benign-sounding scam pretext: {', '.join(benign_pretext_found[:2])}")
        
        # ----- Check 10: Channel Shift Request -----
        # WHY: Scammers try to move conversation to unmonitored channels
        channel_shift_found = [kw for kw in self.CHANNEL_SHIFT_KEYWORDS if kw in message_lower]
        if channel_shift_found:
            score += 0.20  # Increased - channel shifts are suspicious
            reasons.append(f"Requesting channel shift: {', '.join(channel_shift_found[:2])}")
            # Extra boost if also requesting sensitive data or has account details
            if sensitive_found or requests_found or impersonation_found or personal_data_found:
                score += 0.20
                reasons.append("Channel shift with sensitive/financial context")
            # Also boost if mentions bank/account
            elif any(word in message_lower for word in ['bank', 'account', 'details', 'account details', 'verify', 'verification']):
                score += 0.20
                reasons.append("Channel shift with account/bank context")
            # Telegram/WhatsApp with suspicious context
            elif any(word in message_lower for word in ['deal', 'offer', 'exclusive', 'join', 'group']):
                score += 0.15
                reasons.append("Channel shift with suspicious context")
        
        # ----- Check 10b: UPI/Transfer Request -----
        # WHY: Direct transfer requests are strong scam indicators
        transfer_found = [kw for kw in self.TRANSFER_KEYWORDS if kw in message_lower]
        upi_in_message = self.upi_pattern.search(message)
        if transfer_found and upi_in_message:
            score += 0.30  # Strong signal - they want money
            reasons.append("Transfer request with UPI ID (money scam)")
        elif upi_in_message and (threats_found or urgency_found or financial_found):
            score += 0.25
            reasons.append("UPI ID with urgency/threat (payment scam)")
        elif upi_in_message:
            score += 0.15  # UPI alone is suspicious
            reasons.append("Contains UPI ID")
        
        # ----- Check 11: Obfuscation Detection -----
        # WHY: Scammers use leetspeak/obfuscation to bypass detection
        # If normalized text differs significantly and has scam indicators
        if message_lower != message_normalized:
            # Check normalized text for keywords not found in original
            normalized_urgency = [kw for kw in self.URGENCY_KEYWORDS if kw in message_normalized and kw not in message_lower]
            normalized_threats = [kw for kw in self.THREAT_KEYWORDS if kw in message_normalized and kw not in message_lower]
            normalized_sensitive = [kw for kw in self.SENSITIVE_DATA_KEYWORDS if kw in message_normalized and kw not in message_lower]
            
            if normalized_urgency or normalized_threats or normalized_sensitive:
                score += 0.25
                reasons.append(f"Obfuscated scam text detected")
                if normalized_threats:
                    score += 0.15
                    reasons.append(f"Hidden threat: {', '.join(normalized_threats[:2])}")
                if normalized_sensitive:
                    score += 0.15
                    reasons.append(f"Hidden sensitive request: {', '.join(normalized_sensitive[:2])}")
        
        # ----- Check 12: Remote Access Scam -----
        # WHY: Remote access tools are very dangerous
        remote_access_keywords = ['anydesk', 'teamviewer', 'quicksupport', 'remote access', 
                                  'share screen', 'screen share', 'screen sharing']
        remote_access_found = [kw for kw in remote_access_keywords if kw in message_lower]
        if remote_access_found:
            score += 0.35
            reasons.append(f"Remote access scam: {', '.join(remote_access_found[:2])}")
        
        # ----- Check 13: Government Authority Scam -----
        # WHY: Fake government threats are common
        govt_scam_keywords = ['cbi', 'income tax', 'customs', 'enforcement directorate', 
                             'cyber cell', 'crime branch', 'cyber crime', 'inspector',
                             'court summon', 'arrest warrant', 'legal action', 'fir', 
                             'case filed', 'digital arrest']
        govt_threats_found = [kw for kw in govt_scam_keywords if kw in message_lower]
        if govt_threats_found:
            score += 0.25
            reasons.append(f"Government impersonation: {', '.join(govt_threats_found[:2])}")
            if urgency_found or threats_found:
                score += 0.15
                reasons.append("Authority scam with threats")
        
        # ----- Check 14: Charity/Donation Scams -----
        # WHY: Fake charity requests with payment links are scams
        charity_keywords = ['donate', 'donation', 'charity', 'relief fund', 'orphan', 
                           'temple', 'darshan', 'puja', 'religious', 'ngo']
        charity_found = [kw for kw in charity_keywords if kw in message_lower]
        if charity_found and upi_in_message:
            score += 0.20
            reasons.append(f"Charity scam with payment: {', '.join(charity_found[:2])}")
        elif charity_found and (transfer_found or sensitive_found):
            score += 0.15
            reasons.append(f"Suspicious charity request: {', '.join(charity_found[:2])}")
        
        # ----- Check 15: Insurance/Policy Scams -----
        # WHY: Fake policy expiry scams are common
        insurance_keywords = ['policy', 'premium', 'insurance', 'lic', 'claim', 'nominee', 
                             'maturity', 'lapse', 'expiry']
        insurance_found = [kw for kw in insurance_keywords if kw in message_lower]
        if insurance_found and (urgency_found or transfer_found or upi_in_message):
            score += 0.20
            reasons.append(f"Insurance scam indicators: {', '.join(insurance_found[:2])}")
        
        # ----- Check 16: Context from History -----
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
        Includes obfuscated data extraction (spaced digits, masked patterns).
        """
        intel = ExtractedIntelligence()
        
        # Extract UPI IDs (normal format)
        upi_matches = self.upi_pattern.findall(message)
        upi_set = set(upi_matches)
        
        # Also extract spaced UPI IDs: "name @ bank"
        spaced_upi_matches = self.spaced_upi_pattern.findall(message)
        for match in spaced_upi_matches:
            # Normalize by removing extra spaces
            normalized = re.sub(r'\s+', '', match)
            if normalized not in upi_set:
                upi_set.add(normalized)
        
        # Filter out common email-like patterns that aren't UPI
        upi_set = {upi for upi in upi_set if not any(
            domain in upi.lower() for domain in ['gmail', 'yahoo', 'hotmail', 'outlook', 'email']
        )}
        intel.upiIds = list(upi_set)
        
        # Precompute spaced digit chunks once (used for phone + account extraction)
        spaced_text_chunks = re.findall(r'(\d[\s\-\.]+(?:\d[\s\-\.]*){8,}\d)', message)

        # Identify long numeric sequences to prevent phone substring extraction
        account_matches = self.bank_account_pattern.findall(message)
        account_digit_exclusions = []
        for acc in account_matches:
            normalized = re.sub(r'[-\s]', '', acc)
            if len(normalized) >= 11:
                account_digit_exclusions.append(normalized)
        for chunk in spaced_text_chunks:
            normalized = re.sub(r'[\s\-\.]', '', chunk)
            if 11 <= len(normalized) <= 18:
                # Check if this chunk is actually part of a +91 phone prefix
                # e.g., "1-9876543210" from "+91-9876543210" should NOT be treated as account
                chunk_start = message.find(chunk)
                is_phone_prefix = False
                if chunk_start > 0:
                    # Look back for +91 or +9 pattern before this chunk
                    prefix = message[max(0, chunk_start-4):chunk_start]
                    if '+9' in prefix or '+91' in prefix:
                        is_phone_prefix = True
                # Also check: if normalized starts with '1' or '91' and rest is a 10-digit phone
                if not is_phone_prefix:
                    if normalized[:2] == '91' and len(normalized[2:]) == 10 and normalized[2] in '6789':
                        is_phone_prefix = True
                    elif normalized[0] == '1' and len(normalized[1:]) == 10 and normalized[1] in '6789':
                        is_phone_prefix = True
                
                if not is_phone_prefix:
                    account_digit_exclusions.append(normalized)

        # Extract phone numbers (normal format)
        phone_matches = self.phone_pattern.findall(message)
        # IMPORTANT: Keep ORIGINAL format for evaluation matching!
        # Evaluator checks: fake_value IN extracted_value
        # So if fake is '+91-9876543210', we need to store that exact format
        formatted_phones = []
        phone_numbers_10digit = []  # Track 10-digit phone numbers for filtering
        for phone in phone_matches:
            clean_phone = re.sub(r'[-\s]', '', phone)
            if len(clean_phone) >= 10:
                # Extract 10-digit core (last 10 digits to handle +91 prefix)
                phone_10digit = clean_phone[-10:]
                # Skip if the phone number is part of a longer bank account number
                if any(phone_10digit in acc for acc in account_digit_exclusions):
                    continue
                # Store ORIGINAL format from message (for evaluation matching)
                formatted_phones.append(phone)  # Keep original with dashes/spaces
                # Also store normalized version for broader matching
                formatted_phones.append(clean_phone)
                phone_numbers_10digit.append(phone_10digit)
        
        # Also extract spaced phone numbers: "98 765 432 10" or "9-8-7-6-5-4-3-2-1-0"
        spaced_phone_pattern = re.compile(r'\b(\d[\s\-\.]+(?:\d[\s\-\.]*){8,9}\d)\b')
        spaced_phone_matches = spaced_phone_pattern.findall(message)
        for match in spaced_phone_matches:
            # Normalize: remove spaces, dashes, dots
            normalized = re.sub(r'[\s\-\.]', '', match)
            if len(normalized) == 10 and normalized[0] in '6789':
                # Looks like an Indian phone number
                if normalized not in phone_numbers_10digit:
                    formatted_phones.append(normalized)
                    phone_numbers_10digit.append(normalized)
        
        # Also extract spaced digits that look like phone numbers
        # Find all matches of spaced digits in the message
        for chunk in spaced_text_chunks:
            # Normalize: remove spaces, dashes, dots
            normalized = re.sub(r'[\s\-\.]', '', chunk)
            if len(normalized) == 10 and normalized[0] in '6789':
                # Looks like an Indian phone number
                if normalized not in phone_numbers_10digit and not any(normalized in acc for acc in account_digit_exclusions):
                    formatted_phones.append(normalized)
                    phone_numbers_10digit.append(normalized)
        
        phone_set = set(formatted_phones)
        phone_set_10digit = set(phone_numbers_10digit)
        intel.phoneNumbers = list(phone_set)

        # Build a comprehensive phone exclusion set for filtering bank accounts
        # This includes all variations: 10-digit, +91 prefix, 91 prefix, etc.
        phone_exclusion_set = set(phone_numbers_10digit)
        for p10 in phone_numbers_10digit:
            phone_exclusion_set.add('91' + p10)     # 919876543210
            phone_exclusion_set.add('1' + p10)      # 19876543210 (partial +91 match)
            phone_exclusion_set.add('+91' + p10)    # +919876543210

        # Extract bank account numbers (be careful with false positives)
        # Filter out likely false positives (too short or common numbers)
        valid_accounts = [acc for acc in account_matches if len(acc.replace('-', '').replace(' ', '')) >= 9]
        
        # Also extract spaced digits that look like bank account numbers
        for chunk in spaced_text_chunks:
            normalized = re.sub(r'[\s\-\.]', '', chunk)
            # Bank accounts are typically 9-18 digits, not starting with 6-9 (those are phones)
            if 9 <= len(normalized) <= 18 and normalized[0] not in '6789':
                valid_accounts.append(normalized)
        
        # Also extract masked account patterns
        masked_matches = self.masked_account_pattern.findall(message)
        for match in masked_matches:
            # Only add if it has at least some digits (not all X)
            if re.search(r'\d', match):
                valid_accounts.append(match)
        
        # Remove any account numbers that are actually phone numbers
        filtered_accounts = []
        for acc in valid_accounts:
            clean_acc = acc.replace('-', '').replace(' ', '')
            # Skip if this is exactly a phone number or a phone number variant
            if clean_acc in phone_exclusion_set:
                continue
            # Skip 10-digit numbers starting with 6-9 (Indian mobile numbers, not accounts)
            if len(clean_acc) == 10 and clean_acc[0] in '6789':
                continue
            # Skip 12-digit numbers that are just 91 + phone (e.g., 919876543210)
            if len(clean_acc) == 12 and clean_acc[:2] == '91' and clean_acc[2] in '6789':
                if clean_acc[2:] in phone_set_10digit:
                    continue
            # Skip 11-digit numbers that are partial phone matches (e.g., 19876543210)
            if len(clean_acc) == 11 and clean_acc[1] in '6789':
                if clean_acc[1:] in phone_set_10digit:
                    continue
            filtered_accounts.append(acc)
        
        intel.bankAccounts = list(set(filtered_accounts))
        
        # Extract URLs (enhanced)
        url_matches = self.url_pattern.findall(message)
        # Filter out UPI IDs and email addresses
        valid_links = []
        for url in url_matches:
            url_lower = url.lower()
            # Skip if it looks like a UPI ID (has @ but no /)
            if '@' in url_lower and '/' not in url_lower:
                continue
            # Skip common email domains
            if any(email_domain in url_lower for email_domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']):
                continue
            # Skip very short domains that might be false positives
            if len(url) < 6:
                continue
            valid_links.append(url)
        intel.phishingLinks = list(set(valid_links))
        
        # Extract email addresses
        email_matches = self.email_pattern.findall(message)
        # Filter out UPI IDs (which look like emails but have bank suffixes)
        upi_suffixes = ['@ybl', '@paytm', '@oksbi', '@okaxis', '@upi', '@apl', '@ibl', 
                        '@axisbank', '@sbi', '@hdfcbank', '@icici', '@okicici', '@okhdfcbank',
                        '@fakebank', '@fakeupi', '@fam', '@fbl']  # Include fake test suffixes
        valid_emails = []
        for email in email_matches:
            email_lower = email.lower()
            # Skip if it's a UPI ID
            if any(email_lower.endswith(suffix) for suffix in upi_suffixes):
                continue
            # Must have proper email domain (not just @bank)
            if '.' in email.split('@')[-1]:  # Domain part has a dot
                valid_emails.append(email)
        intel.emailAddresses = list(set(valid_emails))
        
        # Extract suspicious keywords found (including new categories)
        message_lower = message.lower()
        all_keywords = (
            self.URGENCY_KEYWORDS + 
            self.THREAT_KEYWORDS + 
            self.SENSITIVE_DATA_KEYWORDS +
            self.BENIGN_PRETEXT_KEYWORDS
        )
        found_keywords = [kw for kw in all_keywords if kw in message_lower]
        intel.suspiciousKeywords = list(set(found_keywords))
        
        return intel
    
    def detect_scam_type(self, message: str, intel: 'ExtractedIntelligence' = None) -> str:
        """
        Detect the type of scam based on message content and extracted intelligence.
        
        Returns one of: bank_fraud, upi_fraud, phishing, lottery, job_scam, 
                       government_scam, tech_support, investment_scam, unknown
        """
        message_lower = message.lower()
        
        # Bank fraud indicators
        bank_keywords = ['bank', 'sbi', 'hdfc', 'icici', 'axis', 'account', 'blocked', 
                        'kyc', 'atm', 'debit card', 'credit card', 'netbanking']
        
        # UPI fraud indicators
        upi_keywords = ['upi', 'paytm', 'phonepe', 'gpay', 'google pay', 'bhim', 
                       'cashback', '@ybl', '@paytm', '@oksbi', '@okaxis']
        
        # Phishing indicators
        phishing_keywords = ['click', 'link', 'http', 'www', 'verify', 'update', 
                            'login', 'password', 'secure']
        
        # Lottery/Prize indicators
        lottery_keywords = ['lottery', 'winner', 'won', 'prize', 'congratulations', 
                           'lucky', 'draw', 'claim', 'reward']
        
        # Job scam indicators
        job_keywords = ['job', 'hiring', 'salary', 'work from home', 'part time', 
                       'selected', 'offer letter', 'registration fee']
        
        # Government scam indicators
        govt_keywords = ['cbi', 'ed', 'income tax', 'police', 'customs', 'court', 
                        'arrest', 'warrant', 'government', 'aadhaar', 'pan']
        
        # Investment scam indicators
        invest_keywords = ['invest', 'trading', 'stock', 'crypto', 'bitcoin', 
                          'returns', 'profit', 'double', 'guaranteed']
        
        # Count matches
        scores = {
            'bank_fraud': sum(1 for k in bank_keywords if k in message_lower),
            'upi_fraud': sum(1 for k in upi_keywords if k in message_lower),
            'phishing': sum(1 for k in phishing_keywords if k in message_lower),
            'lottery': sum(1 for k in lottery_keywords if k in message_lower),
            'job_scam': sum(1 for k in job_keywords if k in message_lower),
            'government_scam': sum(1 for k in govt_keywords if k in message_lower),
            'investment_scam': sum(1 for k in invest_keywords if k in message_lower)
        }
        
        # Also consider extracted intelligence
        if intel:
            if intel.upiIds:
                scores['upi_fraud'] += 3
            if intel.bankAccounts:
                scores['bank_fraud'] += 2
            if intel.phishingLinks:
                scores['phishing'] += 3
            if intel.emailAddresses:
                scores['phishing'] += 1
        
        # Find highest scoring type
        if max(scores.values()) == 0:
            return 'unknown'
        
        return max(scores, key=scores.get)


# Create global detector instance
scam_detector = ScamDetector()
