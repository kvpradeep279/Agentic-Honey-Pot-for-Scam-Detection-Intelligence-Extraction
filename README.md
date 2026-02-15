# 🍯 Agentic Honey-Pot for Scam Detection & Intelligence Extraction

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![Gemini AI](https://img.shields.io/badge/Gemini-AI%20Powered-orange.svg)
![Accuracy](https://img.shields.io/badge/Accuracy-95.8%25-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**An AI-powered honeypot API that detects scam messages, engages scammers in believable conversations, and extracts actionable intelligence — all without revealing detection.**

[Live Demo](#deployment) • [API Docs](#9-api-documentation) • [Test Results](#12-test-results--metrics)

</div>

---

## 📋 Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [The Scam Crisis in India](#2-the-scam-crisis-in-india)
3. [Our Solution](#3-our-solution)
4. [System Architecture](#4-system-architecture)
5. [Project Structure](#5-project-structure)
6. [Scam Detection Engine](#6-scam-detection-engine)
7. [Intelligence Extraction](#7-intelligence-extraction)
8. [AI Agent Behavior](#8-ai-agent-behavior)
9. [API Documentation](#9-api-documentation)
10. [Callback Mechanism](#10-callback-mechanism)
11. [Scam Categories Covered](#11-scam-categories-covered)
12. [Test Results & Metrics](#12-test-results--metrics)
13. [Known Limitations](#13-known-limitations)
14. [Setup & Installation](#14-setup--installation)
15. [Deployment](#15-deployment)
16. [Usage Examples](#16-usage-examples)
17. [Security Considerations](#17-security-considerations)
18. [Future Improvements](#18-future-improvements)
19. [References](#19-references)

---

## 1. Problem Statement

### The Challenge

Online scams including **bank fraud**, **UPI fraud**, **phishing**, and **fake offers** are becoming increasingly adaptive. Scammers change their tactics based on user responses, making traditional detection systems ineffective.

### The Objective

Build an **Agentic Honey-Pot** — an AI-powered system that:

| Requirement | Description |
|-------------|-------------|
| **Detect** | Identify scam or fraudulent messages |
| **Engage** | Activate an autonomous AI Agent |
| **Maintain Persona** | Keep a believable human-like character |
| **Multi-turn** | Handle ongoing conversations |
| **Extract** | Gather scam-related intelligence |
| **Report** | Return structured results via API |

> 💡 **Key Insight**: Instead of simply blocking scammers, we **engage them** to waste their time and extract valuable intelligence that can help protect others.

---

## 2. The Scam Crisis in India

### 📊 Current Statistics (2024-2025)

```mermaid
pie showData
    title Types of Digital Scams in India (2024-25)
    "UPI/Payment Fraud" : 38
    "Bank KYC Scams" : 24
    "Lottery/Prize Scams" : 14
    "Job Offer Scams" : 11
    "Investment Scams" : 8
    "Others" : 5
```

### Key Facts

| Metric | Value | Source |
|--------|-------|--------|
| **Annual Fraud Cases** | 1.1+ Million reported | RBI Annual Report 2024 |
| **Financial Loss** | ₹14,000+ Crores annually | Cyber Crime Portal |
| **Most Targeted Age Group** | 35-55 years | NPCI Data |
| **SMS Scam Rate** | 47% of all scam attempts | TRAI Report |
| **Average Loss per Victim** | ₹1.2 Lakhs | Indian Cyber Crime Coordination Centre |
| **Reporting Rate** | Only 14% report scams | Survey Data |

### Why Scams Succeed

Scammers exploit fundamental human psychology to manipulate victims. Understanding these tactics helps in building better detection systems:

**Psychological Triggers Used by Scammers:**

- **Fear & Urgency** - Messages create panic ("Your account will be blocked in 24 hours!") forcing hasty decisions without verification
- **Authority Trust** - Impersonating banks, government agencies (RBI, Income Tax, CBI) to gain instant credibility
- **Greed & Reward** - Promises of lottery winnings, job offers, or investment returns too good to be true
- **Social Proof** - Claims like "1000s have already benefited" to create false legitimacy
- **Reciprocity** - Small favors followed by larger requests

**The Scam Progression:**

1. **Initial Contact** - Scam message creates emotional trigger
2. **Victim Engagement** - Fear, trust, or greed compels response
3. **Information Extraction** - OTP, bank details, or personal data requested
4. **Financial Loss** - ₹1.2 Lakhs average loss per victim in India

### Common Scam Channels

| Channel | Percentage | Trend |
|---------|------------|-------|
| **SMS** | 47% | ↑ Rising |
| **WhatsApp** | 28% | ↑ Rising |
| **Phone Calls** | 18% | → Stable |
| **Email** | 5% | ↓ Declining |
| **Other Apps** | 2% | → Stable |

---

## 3. Our Solution

### What We Built

An **AI-powered honeypot API** that turns the tables on scammers by:

1. **Detecting scam intent** using pattern matching and behavioral analysis
2. **Engaging scammers** with an AI agent that plays the role of a gullible victim
3. **Extracting intelligence** (bank accounts, UPI IDs, phone numbers, links)
4. **Reporting findings** to the evaluation endpoint for analysis

**How It Works (In Simple Terms):**

When a scammer sends a message like "Your account will be blocked, share OTP immediately!", our system:

1. **Analyzes** the message for 19 scam indicators (urgency, threats, data requests)
2. **Calculates** a confidence score (0.0 to 1.0) based on weighted pattern matches
3. **If scam detected**, activates an AI agent that pretends to be a busy, trusting professional
4. **Extracts** any bank accounts, UPI IDs, phone numbers, or phishing links
5. **Engages** the scammer in conversation, wasting their time
6. **Reports** all extracted intelligence to law enforcement/security teams

### Key Differentiators

| Feature | Traditional Systems | Our Honeypot |
|---------|---------------------|--------------|
| Response to scams | Block/Ignore | **Engage & Extract** |
| Intelligence gathering | None | **Automated extraction** |
| Scammer time wasted | 0 seconds | **Minutes of engagement** |
| Learning capability | Static rules | **AI-adaptive responses** |
| Language support | English only | **English + Hinglish + Regional** |

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Framework** | FastAPI | High-performance async API |
| **AI Engine (Primary)** | Google Gemini (2 keys) | Natural language generation with key rotation |
| **AI Engine (Fallback)** | Grok / xAI | Fallback AI when Gemini hits rate limits |
| **Language** | Python 3.11+ | Core implementation |
| **Deployment** | Render.com | Cloud hosting |

---

## 4. System Architecture

### High-Level Architecture

```mermaid
flowchart TB
    subgraph External
        SC[🦹 Scammer]
        GUVI[📊 GUVI Evaluation]
    end
    
    subgraph API["🍯 Honeypot API"]
        EP["/honeypot Endpoint"]
        AUTH[🔐 API Key Auth]
        SD[🔍 Scam Detector]
        AG[🤖 AI Agent]
        SM[📝 Session Manager]
        IE[🎯 Intel Extractor]
        CB[📤 Callback Handler]
    end
    
    SC -->|1. Send Message| EP
    EP -->|2. Verify| AUTH
    AUTH -->|3. Analyze| SD
    SD -->|4. If Scam| AG
    AG -->|5. Generate Reply| SM
    SM -->|6. Extract| IE
    IE -->|7. Store| SM
    AG -->|8. Return Reply| SC
    CB -->|9. Report| GUVI
    
    style SC fill:#ff6b6b,color:#fff
    style AG fill:#4ecdc4,color:#fff
    style GUVI fill:#45b7d1,color:#fff
```

### Request-Response Flow

```mermaid
sequenceDiagram
    participant S as 🦹 Scammer
    participant A as 🍯 API
    participant D as 🔍 Detector
    participant AI as 🤖 Agent
    participant G as 📊 GUVI

    S->>A: POST /honeypot
    A->>A: Validate API Key
    A->>D: Analyze Message
    D->>D: Pattern Matching & Keyword Scoring
    D-->>A: {is_scam, confidence, reasons}
    
    alt Is Scam
        A->>D: Extract Intelligence (from Input)
        A->>A: Update Session Data
        
        A->>AI: Generate Response
        AI->>AI: Maintain Persona
        AI-->>A: Human-like Reply
        
        opt Sufficient Engagement
            A->>G: POST Callback (Async)
            G-->>A: Acknowledged
        end
    end
    
    A-->>S: {status, reply}
```

---

## 5. Project Structure

```
📁 Agentic-Honey-Pot-for-Scam-Detection/
│
├── 📂 app/                          # Core application code
│   ├── 📄 __init__.py               # Package initializer
│   ├── 📄 main.py                   # FastAPI application entry point
│   ├── 📄 scam_detector.py          # Scam detection engine (700+ lines)
│   ├── 📄 agent.py                  # AI agent for engagement (multi-provider)
│   ├── 📄 session_manager.py        # Multi-turn session handling
│   ├── 📄 callback_handler.py       # GUVI callback integration
│   ├── 📄 models.py                 # Pydantic data models
│   └── 📄 config.py                 # Configuration & API key management
│
├── 📂 testing/                      # Test suite & demo scripts
│   ├── 📄 test_final_comprehensive.py  # 191-case comprehensive test suite
│   ├── 📄 demo_api_test.py             # API endpoint testing demo
│   └── 📄 demo_conversation.py         # Multi-turn conversation demo
│
├── 📂 Documents/                    # Problem statement docs (gitignored)
│
├── 📄 requirements.txt              # Python dependencies
├── 📄 Procfile                      # Deployment configuration
├── 📄 render.yaml                   # Render.com settings
├── 📄 .env.example                  # Environment template
├── 📄 .gitignore                    # Git ignore rules
└── 📄 README.md                     # This documentation
```

### File Descriptions

#### **app/main.py** — API Entry Point
| Responsibility | Description |
|----------------|-------------|
| Route handling | Defines `/honeypot` and `/health` endpoints |
| Authentication | Validates `x-api-key` header |
| Request processing | Orchestrates detection → engagement → extraction |
| Error handling | Returns appropriate HTTP status codes |

#### **app/scam_detector.py** — Detection Engine
| Responsibility | Description |
|----------------|-------------|
| Keyword matching | 100+ scam-related keywords across 10 categories |
| Pattern analysis | Regex for accounts, UPIs, phones, links |
| Confidence scoring | 0.0 to 1.0 scale with weighted factors |
| Obfuscation handling | Detects leetspeak and SMS abbreviations |

#### **app/agent.py** — AI Engagement
| Responsibility | Description |
|----------------|-------------|
| Multi-provider AI | Gemini (2 keys × 4 models) + Grok fallback |
| Key rotation | Round-robin across API keys to avoid rate limits |
| Persona maintenance | Middle-aged Indian professional character |
| Language mirroring | Hinglish/regional language support |
| Fallback responses | 50+ pre-built responses for API failures |

#### **app/session_manager.py** — State Management
| Responsibility | Description |
|----------------|-------------|
| Session tracking | Per-conversation state |
| Intelligence accumulation | Merges intel across messages |
| Message counting | Tracks engagement depth |
| Duplicate prevention | Ensures single callback per session |

#### **app/callback_handler.py** — GUVI Reporting
| Responsibility | Description |
|----------------|-------------|
| Callback timing | Triggers at optimal engagement depth |
| Payload construction | Formats data per specification |
| Async sending | Non-blocking callback dispatch |
| Error handling | Retries and logging |

#### **app/models.py** — Data Models
| Responsibility | Description |
|----------------|-------------|
| Request validation | Pydantic models for `Message`, `Metadata`, `HoneypotRequest` |
| Response schemas | `HoneypotResponse`, `ExtractedIntelligence` |
| Type safety | Automatic validation, JSON schema generation |
| Flexible parsing | Handles string/dict messages, int/float/string timestamps |

#### **app/config.py** — Configuration Management
| Responsibility | Description |
|----------------|-------------|
| Environment loading | Reads all keys from `.env` via `python-dotenv` |
| Multi-key support | Loads `GEMINI_API_KEY`, `GEMINI_API_KEY_2`, ..., `GEMINI_API_KEY_10` |
| Provider config | Manages Gemini, Grok, and OpenAI API keys |
| Operational params | Callback URL, thresholds, and system settings |

#### **testing/test_final_comprehensive.py** — Comprehensive Test Suite
| Responsibility | Description |
|----------------|-------------|
| 191 test cases | Covers all 18 scam categories + false positives + edge cases |
| Extraction validation | Verifies UPI, phone, bank account, and link extraction |
| Confidence checks | Ensures minimum confidence thresholds are met |
| Summary reporting | Prints pass/fail counts and failure details |

#### **testing/demo_api_test.py** — API Testing Demo
| Responsibility | Description |
|----------------|-------------|
| Live API testing | Sends scam messages to the running API endpoint |
| Response validation | Checks status codes, reply format, and content |
| Multi-turn testing | Simulates multi-message conversations |

#### **testing/demo_conversation.py** — Conversation Demo
| Responsibility | Description |
|----------------|-------------|
| 15-message simulation | Runs a realistic scam conversation through all components |
| Intelligence report | Shows cumulative extracted intelligence after engagement |
| Engagement summary | Displays conversation statistics and scam confidence |

---

## 6. Scam Detection Engine

The detection engine is the heart of our system. It uses a **multi-layered approach** combining keyword matching, pattern recognition, and context analysis to identify scam messages with high accuracy.

**Key Design Principles:**

- **High Recall** - Better to engage a non-scam than miss a real scam
- **Low False Positives** - Legitimate OTPs and bank notifications are excluded
- **Language Agnostic** - Works with English, Hindi, Hinglish, and regional languages
- **Obfuscation Resistant** - Handles leetspeak (4cc0unt) and SMS abbreviations (ur acc blkd)

### Detection Algorithm Overview

```mermaid
flowchart LR
    subgraph Input
        M[📩 Message]
    end
    
    subgraph Processing
        L[🛡️ Legitimate Guard]
        N[🔄 Normalize Text]
        K[📝 Keyword Scoring]
        P[🔍 Pattern Matching]
        C[📊 Context Analysis]
    end
    
    subgraph Output
        S[📈 Confidence Score]
        D[✅ Decision]
    end
    
    M --> L
    L -->|Not Legitimate| N
    L -->|Legitimate| D
    N --> K
    N --> P
    N --> C
    K --> S
    P --> S
    C --> S
    S --> D
```

> ⚠️ **Important**: The Legitimate Guard (Check 0) runs **first** — before any scam scoring. If the message matches a legitimate pattern (bank OTP, transaction alert, booking confirmation), it is immediately cleared with a score of 0.0 and all remaining scam checks are bypassed. This is why we achieve **0% false positives**.

### Detection Checks (19 Total)

| # | Check | Score Impact | Description |
|---|-------|--------------|-------------|
| 0 | **Legitimate Message Guard** | → 0.0 (bypass) | Real OTPs, transaction alerts, delivery/booking notifications — immediately cleared |
| 0b | **Credit Card Bill Guard** | → 0.0 (bypass) | Legitimate credit card bill reminders with "min due" — immediately cleared |
| 1 | **Urgency Keywords** | +0.15 | "urgent", "immediately", "jaldi", "abhi" |
| 2 | **Threat Keywords** | +0.20 | "blocked", "suspended", "legal action" |
| 3 | **Sensitive Data Requests** | +0.25 | "OTP", "PIN", "CVV", "Aadhaar" |
| 4 | **Financial Keywords** | +0.25 | "lottery", "prize", "refund", "KYC" |
| 4b | **Job Scam Keywords** | +0.15–0.40 | "selected", "work from home" + payment request |
| 5 | **Impersonation** | +0.15 | "RBI", "SBI", "customer care", "government" |
| 6 | **Suspicious Links** | +0.25 | HTTP/HTTPS links (legitimate domains filtered out) |
| 7 | **Mixed Language (Hinglish)** | +0.10–0.25 | Scam keywords in mixed Hindi-English (e.g. "jaldi bhejo") |
| 8 | **Over-Polite Formal Tone** | +0.15 | "Dear Sir/Madam" + financial request combos |
| 9 | **Benign Pretext Hooks** | +0.15 | "Refund pending", "security update", "chargeback" |
| 10 | **Channel Shift Request** | +0.20 | "Message me on WhatsApp", "Call this number" |
| 10b | **UPI/Transfer Request** | +0.15–0.30 | Direct payment demands ("pay", "transfer") with UPI IDs |
| 11 | **Obfuscation Detection** | +0.25 | Leetspeak, spaced text, SMS abbreviations |
| 12 | **Remote Access** | +0.35 | "AnyDesk", "TeamViewer", "screen share" |
| 13 | **Government Authority** | +0.25 | "CBI", "ED", "Income Tax", "arrest warrant" |
| 14 | **Charity/Donation Scams** | +0.20 | "donation", "temple", "orphanage" + UPI |
| 15 | **Insurance/Policy Scams** | +0.20 | "policy", "premium", "claim" + urgency |
| 16 | **Context from History** | +0.10 | Multi-turn escalation detection |

*Score varies based on context combination

### Keyword Categories

```python
URGENCY_KEYWORDS = [
    "urgent", "immediately", "right now", "today only",
    "last chance", "act now", "hurry", "jaldi", "abhi", "turant"
]

THREAT_KEYWORDS = [
    "blocked", "suspended", "terminated", "legal action",
    "police", "arrest", "penalty", "cbi", "ed", "raid"
]

SENSITIVE_DATA_KEYWORDS = [
    "otp", "pin", "password", "cvv", "account number",
    "upi", "aadhar", "pan", "credit card", "debit card"
]
```

### Confidence Scoring System

| Score Range | Classification | Action |
|-------------|----------------|--------|
| **0.00 - 0.29** | Not a scam | Normal response |
| **0.30 - 0.49** | Low confidence | Monitor, light engagement |
| **0.50 - 0.69** | Medium confidence | Full engagement |
| **0.70 - 0.89** | High confidence | Aggressive extraction |
| **0.90 - 1.00** | Definite scam | Maximum engagement |

### Obfuscation Detection

Scammers often disguise messages using:

| Technique | Example | Our Detection |
|-----------|---------|---------------|
| **Leetspeak** | `4cc0unt bl0ck3d` | Normalized to "account blocked" |
| **Spaced text** | `O T P` | Collapsed to "OTP" |
| **SMS abbreviations** | `ur acc blkd` | Expanded to "your account blocked" |
| **Zero substitution** | `0TP` | Converted to "OTP" |

```python
LEETSPEAK_MAP = {
    '0': 'o', '1': 'i', '3': 'e', '4': 'a',
    '5': 's', '7': 't', '@': 'a', '$': 's'
}

SMS_ABBREVIATIONS = {
    'ur': 'your', 'u': 'you', 'r': 'are',
    'plz': 'please', 'acc': 'account', 'blkd': 'blocked'
}
```

### False Positive Prevention (Check 0 — Legitimate Guard)

The **very first step** in our detection is a whitelist layer with **15+ regex patterns** that recognizes legitimate messages. If matched, the message is immediately cleared with score `0.0` — **all 19 scam checks are bypassed entirely**.

| Legitimate Pattern | Example | Regex Logic |
|--------------------|---------|-------------|
| Real OTP notifications | "Your OTP for SBI transaction is 123456. Do not share." | Matches `OTP.*do not share` format |
| Transaction alerts | "INR 5000.00 debited from A/c XX1234. Avl Bal: INR 45000" | Matches `debited.*Avl Bal` format |
| Payment confirmations | "Rs.500 paid to Swiggy via UPI. Ref: 123456789012" | Matches `paid to.*via UPI` format |
| Delivery updates | "Your Amazon order #XYZ has been shipped" | Matches `order.*shipped/delivered` |
| Booking confirmations | "Your flight 6E-123 is confirmed. PNR: ABC123" | Matches `booking/flight.*confirmed` |
| Appointment reminders | "Your appointment with Dr. Sharma at 10 AM" | Matches `appointment.*confirmed` |
| Movie/ticket bookings | "BookMyShow: Tickets confirmed for Avatar 2" | Matches `ticket.*confirmed/booked` |
| Credit card bills | "HDFC Card bill Rs.15000 due on 20-Feb. Min Due: Rs.1500" | Matches `card bill.*min.*due` |
| Genuine refund notifications | "Refund of ₹500 processed to your account" | Matches `refund.*processed/initiated` |

> 💡 **Why this matters**: Without this guard, legitimate OTPs containing "OTP" (+0.25) and bank names like "SBI" (+0.15) would incorrectly score 0.40 and be flagged as scams. Our Check 0 prevents this entirely.

---

## 7. Intelligence Extraction

### Extracted Data Types

Our system automatically extracts actionable intelligence from scam conversations. This data can be used by law enforcement and cybersecurity teams to track and prosecute scammers.

**Types of Intelligence Extracted:**

| Data Type | Format | Detection Method | Use Case |
|-----------|--------|------------------|----------|
| **Bank Accounts** | 9-18 digit numbers | Regex pattern matching | Report to banks for fraud alerts |
| **IFSC Codes** | 11 alphanumeric chars | Bank code validation | Identify scammer's bank branch |
| **UPI IDs** | name@provider | Pattern: `*@ybl`, `*@paytm` | Block fraudulent UPI handles |
| **Phone Numbers** | +91-XXXXXXXXXX | Indian mobile format | Trace scammer's identity |
| **Phishing Links** | HTTP/HTTPS URLs | Domain analysis | Takedown malicious websites |
| **Keywords** | Scam phrases | NLP extraction | Improve detection patterns |

**Why This Matters:**
- Each extracted bank account can prevent multiple future frauds
- UPI IDs can be reported to NPCI for immediate blocking
- Phone numbers help law enforcement trace scam networks
- Phishing URLs can be submitted to Google Safe Browsing

### Extraction Patterns

#### Bank Account Numbers
```python
# Pattern: 9-18 digit numbers
r'\b\d{9,18}\b'

# Examples detected:
# - 1234567890123456
# - 123456789012
# - Account: 9876543210
```

#### UPI IDs
```python
# Pattern: name@provider format
r'\b[\w.\-]+@[a-zA-Z]{2,}\b'

# Examples detected:
# - scammer@ybl
# - fraud.person@paytm
# - fake123@upi
```

#### Phone Numbers
```python
# Patterns: Indian mobile numbers
r'(?:\+91[\-\s]?)?[6-9]\d{9}'

# Examples detected:
# - +91-9876543210
# - 9876543210
# - +91 98765 43210
```

#### Phishing Links
```python
# Pattern: URLs with common domains
r'https?://[^\s]+'
r'[a-zA-Z0-9][-a-zA-Z0-9]*\.(?:com|in|co\.in|org|net)'

# Examples detected:
# - http://fake-sbi.com/kyc
# - sbi-verify.secure-bank.co.in
```

### Obfuscated Data Extraction

Scammers often disguise their contact information to bypass filters. Our extraction engine handles these obfuscated formats:

| Obfuscation Type | Raw Input | Extracted Output | Method |
|-----------------|-----------|-----------------|--------|
| **Spaced UPI** | `name @ bank` | `name@bank` | Regex + whitespace normalization |
| **Spaced Phone** | `98 765 432 10` | `9876543210` | Digit aggregation with validation |
| **Spaced Digits** | `1 2 3 4 5 6 7 8 9 0 1 2` | `123456789012` | Spaced chunk detection |
| **Masked Accounts** | `XXXX1234` | `XXXX1234` (preserved) | Masked account pattern |
| **Dashed Phone** | `98-765-432-10` | `9876543210` | Separator stripping |

### Smart Phone vs. Account Disambiguation

A critical challenge: long digit sequences could be either phone numbers or bank accounts. Our system disambiguates using:

| Rule | Logic |
|------|-------|
| **Length check** | 10 digits starting with 6-9 → Phone; 11-18 digits → Bank account |
| **Substring exclusion** | If a phone number is a substring of a bank account, skip it |
| **First digit rule** | Digits starting with 6-9 are Indian mobile numbers; others are account numbers |
| **Duplicate prevention** | Same number is never listed in both `phoneNumbers` and `bankAccounts` |

> 💡 This prevents a bank account `9876543210123456` from also being extracted as phone `9876543210`.

---

## 8. AI Agent Behavior

### Agent Persona

The AI agent plays the role of a **middle-aged Indian person (35-55 years)** who is:

| Trait | Behavior |
|-------|----------|
| **Moderate tech knowledge** | Not an expert but uses banking apps, still asks for clarification on complex terms |
| **Busy professional** | Working person with family responsibilities, makes hasty decisions under pressure |
| **Trusting of officials** | Respects authority figures like banks, government agencies |
| **Worried about security** | Concerned about account safety and savings |
| **Cooperative** | Willing to help if it seems legitimate, asks questions before acting |

### Response Generation Flow (Multi-Key + Multi-Provider)

The system uses a **3-tier AI resilience chain**: round-robin Gemini key rotation → Grok fallback → static responses.

```mermaid
flowchart TD
    A["📨 Scammer Message"] --> B{"AI Available?"}
    B -->|No| STATIC["📝 Static Fallback Response"]
    B -->|Yes| RR["🔑 Rotate to Next Gemini Key<br/>Round-Robin"]
    
    RR --> M1["Try gemini-flash-lite-latest"]
    M1 -->|"✅ Success"| H["✅ Return Response"]
    M1 -->|"❌ Fail"| M1R{"Rate Limited?"}
    M1R -->|"Yes & keys left"| SWAP1["🔑 Switch Key & Retry"]
    SWAP1 -->|✅| H
    SWAP1 -->|❌| M2
    M1R -->|"No / keys exhausted"| M2["Try gemini-2.5-flash-lite"]
    
    M2 -->|✅| H
    M2 -->|❌| M3["Try gemini-2.0-flash-lite"]
    M3 -->|✅| H
    M3 -->|❌| M4["Try gemini-2.5-flash"]
    M4 -->|✅| H
    M4 -->|❌| GROK
    
    GROK["🔄 Try Grok Cloud<br/>llama-3.3-70b-versatile"] -->|✅| H
    GROK -->|❌| STATIC
    STATIC --> H
    
    style H fill:#4ecdc4,color:#fff
    style GROK fill:#8b5cf6,color:#fff
    style STATIC fill:#ffa94d,color:#000
    style RR fill:#3b82f6,color:#fff
```

### AI Provider Chain

| Priority | Provider | Model | Purpose |
|----------|----------|-------|---------|
| 1 | Gemini (Key 1→2) | `gemini-flash-lite-latest` | Highest free tier quota, fastest |
| 2 | Gemini (Key 1→2) | `gemini-2.5-flash-lite` | Lite version of 2.5 |
| 3 | Gemini (Key 1→2) | `gemini-2.0-flash-lite` | Lite version of 2.0 |
| 4 | Gemini (Key 1→2) | `gemini-2.5-flash` | Full version (lower quota) |
| 5 | **Groq Cloud** | `llama-3.3-70b-versatile` | **Fallback Llama 3 model via Groq** |
| 6 | Static | Pre-built responses | Final safety net (50+ responses) |

> 🔑 **Key Rotation Strategy**: Each request rotates to the next Gemini API key (round-robin). On rate limit (429), the system also swaps to the other key before moving to the next model. This effectively gives **8 Gemini attempts** (4 models × 2 keys) before falling back to Groq.

### Language Mirroring

The agent **mirrors the scammer's language style**:

| Scammer Input | Agent Response Style |
|---------------|---------------------|
| Pure English | English with simple words |
| Hinglish | Mixed Hindi-English ("Acha, beta...") |
| Hindi-heavy | More Hindi words in response |
| Tamil indicators | Tamil acknowledgments ("Seri") |
| Telugu indicators | Telugu acknowledgments ("Sare") |

### Example Conversations

**English Scam:**
```
Scammer: "Your account will be blocked!"
Agent: "Oh no! Which account are you talking about? I have savings in SBI..."
```

**Hinglish Scam:**
```
Scammer: "Aapka account block ho jayega, OTP bhejo"
Agent: "Acha? But kyun beta? Kaun sa account? Mera paisa safe hai na?"
```

### Fallback Response System

When all AI providers fail (Gemini + Grok), the agent uses **50+ pre-built responses** across 10 categories:

| Category | Example Responses |
|----------|-------------------|
| **Confusion** | "I don't understand, can you explain again?" |
| **Banking** | "Which bank is this from? SBI or HDFC?" |
| **Verification** | "How do I know this is really from the bank?" |
| **Technical** | "UPI? I use it for payments but this seems different..." |
| **Stalling** | "Wait, I'm in a meeting right now, give me a moment..." |
| **Family** | "Let me check with my wife first, she handles our accounts" |
| **Compliance** | "Okay, what number should I send it to?" |
| **Concern** | "My savings are very important to me..." |
| **Hinglish** | "Acha ji? Kya karna padega?" |
| **Extracted** | Questions that prompt revealing more info |

### Exposure Risk Filter (Cover Protection)

A critical safety mechanism: every AI-generated response is scanned before being sent to the scammer.

```mermaid
flowchart LR
    A[🤖 AI Response] --> B{Contains risky words?}
    B -->|No| C[✅ Send to Scammer]
    B -->|Yes| D[❌ Discard & Use Fallback]
    
    style C fill:#4ecdc4,color:#fff
    style D fill:#ff6b6b,color:#fff
```

**Risky words checked**: `scam`, `fraud`, `fake`, `suspicious`, `report`, `police`, `cyber crime`, `phishing`, `malicious`, `don't trust`, `not legitimate`

> 🚨 **Why this matters**: Without this filter, a single Gemini slip-up saying "this seems suspicious" would blow the bot's cover instantly. The scammer would stop engaging and move to the next victim.

### Scammer Tactics Analyzer (Behavioral Intelligence)

Beyond extracting data, our system classifies the scammer's **psychological tactics** for each message:

| Detected Tactic | Trigger Keywords | Intelligence Value |
|----------------|-----------------|--------------------|
| "Creating urgency to bypass rational thinking" | `urgent`, `immediately`, `hurry` | Identifies manipulation strategy |
| "Using threats and fear tactics" | `blocked`, `suspended`, `legal` | Documents intimidation methods |
| "Impersonating authority/institution" | `bank`, `rbi`, `government` | Tracks impersonation patterns |
| "Attempting to steal credentials" | `otp`, `pin`, `password`, `cvv` | Records data theft attempts |
| "Using financial bait/rewards" | `prize`, `lottery`, `winner` | Identifies lure strategies |
| "Attempting to redirect to phishing site" | `link`, `click`, `download` | Flags phishing infrastructure |

These tactics are written into `agentNotes` in the callback payload, giving law enforcement a **behavioral profile** of the scammer — not just raw data.

---

## 9. API Documentation

The API is designed to be **simple to integrate** while providing comprehensive functionality. A single endpoint handles all scam detection, engagement, and intelligence extraction.

**Integration Highlights:**
- **Single endpoint** (`/honeypot`) handles everything
- **Session-based** conversations maintain context across multiple messages
- **Stateless design** allows horizontal scaling
- **JSON in/out** with clear request/response schemas
- **API key authentication** for security
- **Flexible message format** — accepts `text` or `content` field, string or dict messages, int/float/string timestamps

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/honeypot` | Main scam processing endpoint |
| `GET` | `/health` | Health check endpoint |
| `HEAD` | `/health` | Health check (no body) |
| `GET` | `/` | Root endpoint (redirects to health) |

### Authentication

All requests to `/honeypot` require the `x-api-key` header:

```http
x-api-key: YOUR_SECRET_API_KEY
Content-Type: application/json
```

### Request Format

#### First Message (Start of Conversation)
```json
{
  "sessionId": "unique-session-id-123",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

#### Follow-up Message (Multi-turn)
```json
{
  "sessionId": "unique-session-id-123",
  "message": {
    "sender": "scammer",
    "text": "Share your OTP to unblock account",
    "timestamp": 1770005529731
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately.",
      "timestamp": 1770005528731
    },
    {
      "sender": "agent",
      "text": "Oh no! Which bank is this from? My savings are important...",
      "timestamp": 1770005528800
    }
  ],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

### Response Format

#### Successful Response
```json
{
  "status": "success",
  "reply": "Oh dear! Which OTP are you asking about? I received many messages today..."
}
```

#### Error Responses

| Status Code | Response | Cause |
|-------------|----------|-------|
| `401` | `{"detail": "Missing x-api-key header"}` | No API key provided |
| `401` | `{"detail": "Invalid API key"}` | Wrong API key |
| `422` | `{"detail": "Validation error"}` | Invalid request format |
| `500` | `{"detail": "Internal server error"}` | Server-side error |

---

## 10. Callback Mechanism

The callback mechanism allows our honeypot to **report extracted intelligence** to an external evaluation system (in this case, GUVI's hackathon endpoint). This enables real-time monitoring of scam detection performance.

**Why Callbacks Matter:**
- **Real-time reporting** - Intelligence is shared as soon as sufficient data is collected
- **Non-blocking** - Callbacks are sent asynchronously, so API response is not delayed
- **Intelligent timing** - Waits for sufficient engagement before sending (maximizes intelligence)
- **Duplicate prevention** - Each session sends only ONE callback to avoid duplicate reports

### Conversation History Re-Extraction

On every API request, the system **re-extracts intelligence** from all previous scammer messages in the `conversationHistory`. This ensures:

- ✅ **Restart resilience** — If the server restarts mid-conversation, intelligence is recovered from the history the evaluator sends
- ✅ **Cumulative extraction** — Intelligence from earlier messages is not lost even if sessions are cleared
- ✅ **Message count recovery** — `message_count` is recalculated from `conversationHistory` length, not stored state

### When Callback is Triggered

The callback logic balances **collecting enough intelligence** vs **reporting quickly**. It uses a tiered approach:

```mermaid
flowchart TD
    Start["📩 New Message Processed"] --> Scam{"Is Scam?"}
    Scam -->|No| Stop["❌ No Callback"]
    Scam -->|Yes| Intel{"Check Intelligence"}
    
    Intel -->|"3+ Items & >10 msgs"| Send["📤 Send Callback"]
    Intel -->|"2 Items & >15 msgs"| Send
    Intel -->|"1 Item & >20 msgs"| Send
    Intel -->|"Keywords & >25 msgs"| Send
    Intel -->|"Max Turns (35)"| Send
    
    Intel -->|"Not Enough"| Wait["⏳ Continue Engagement"]
    
    Send --> Async["🚀 Async POST to GUVI"]
    Async --> Done["✅ Done (Mark Session Sent)"]
```

The system sends a callback to GUVI when:

1. ✅ **Scam is confirmed** (`scamDetected = true`)
2. ✅ **Sufficient engagement** (multiple messages exchanged)
3. ✅ **Intelligence extracted** (at least 2+ items found)
4. ✅ **Not already sent** (prevents duplicates)

### Callback Endpoint

```
POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult
Content-Type: application/json
```

### Callback Payload Structure

```json
{
  "sessionId": "unique-session-id-123",
  "scamDetected": true,
  "totalMessagesExchanged": 15,
  "extractedIntelligence": {
    "bankAccounts": ["1234567890123456"],
    "upiIds": ["scammer@ybl", "fraud@paytm"],
    "phishingLinks": ["http://fake-sbi.com/kyc"],
    "phoneNumbers": ["+91-9876543210"],
    "suspiciousKeywords": ["blocked", "urgent", "kyc", "otp", "verify"]
  },
  "agentNotes": "Bank fraud scam targeting SBI customers. Scammer impersonated bank employee and used urgency tactics. Requested OTP, account details, and payment via UPI."
}
```

### Callback Timing Strategy

| Condition | Trigger Point |
|-----------|---------------|
| Rich intel (3+ items) | After 10+ turns (~5 scammer msgs) |
| Multiple intel (2 items) | After 15+ turns (~8 scammer msgs) |
| Single real intel | After 20+ turns (~10 scammer msgs) |
| Keywords only | After 25+ turns (~13 scammer msgs) |
| Maximum engagement | After 35+ turns (force send) |

---

## 11. Scam Categories Covered

### 18 Detection Categories

Our detection system covers **18 comprehensive scam categories** based on real-world scam patterns observed in India. The test suite validates detection across all categories with weighted distribution based on prevalence.

**Category Distribution:**
- **High-frequency scams** (Bank Fraud, Government) get more test cases due to higher real-world occurrence
- **Emerging scams** (Crypto, Romance) are included to future-proof the system
- **False positive tests** ensure legitimate messages aren't incorrectly flagged

### Category Details

| # | Category | Tests | Examples |
|---|----------|-------|----------|
| 1 | **Bank Fraud** | 20 | KYC expiry, account blocked, card suspended |
| 2 | **Government Impersonation** | 15 | Income Tax, CBI, ED, RBI notices |
| 3 | **Lottery & Prize** | 12 | Amazon lucky draw, WhatsApp lottery |
| 4 | **Job Offer Scams** | 10 | Work from home, data entry, registration fee |
| 5 | **Delivery & Courier** | 10 | Package held, customs fee required |
| 6 | **Investment & Crypto** | 10 | Double your money, guaranteed returns |
| 7 | **Tech Support** | 8 | Virus detected, remote access needed |
| 8 | **Utility Bill Scams** | 8 | Electricity disconnection, gas bill |
| 9 | **Obfuscation** | 15 | Leetspeak, spaced text, SMS abbreviations |
| 10 | **False Positives** | 20 | Legitimate OTPs, delivery notifications |
| 11 | **Edge Cases** | 15 | Empty messages, special characters |
| 12 | **Social Engineering** | 10 | Trust building, authority exploitation |
| 13 | **Channel Shift** | 8 | Move to WhatsApp, Telegram, phone call |
| 14 | **Romance Scams** | 6 | Emotional manipulation, gift requests |
| 15 | **Insurance & Medical** | 6 | Policy maturity, claim processing |
| 16 | **Religious & Charity** | 5 | Temple donations, orphanage scams |
| 17 | **Regional Language** | 8 | Tamil, Telugu, Hindi variants |
| 18 | **SMS Abbreviations** | 5 | "ur acc blkd", "snd OTP asap" |

---

## 12. Test Results & Metrics

Our test suite validates the detection engine against **191 real-world test cases** spanning all 18 scam categories. The tests are designed to ensure both high detection accuracy AND low false positive rates.

**Testing Philosophy:**
- **Real scam samples** - Test messages based on actual scam patterns reported in India
- **False positive validation** - Legitimate messages (OTPs, notifications) must NOT be flagged
- **Obfuscation testing** - Leetspeak, spaced text, and SMS abbreviations are covered
- **Regional language support** - Hindi, Tamil, Telugu variants tested

### Overall Performance

```
================================================================================
📊 TEST RESULTS SUMMARY
================================================================================
✅ Passed: 183/191
❌ Failed: 8/191
📈 Pass Rate: 95.8%
================================================================================
```

**What the 8 Failures Mean:**
- Most failures are **edge cases** with borderline confidence scores
- NO false positives (all 20 legitimate messages correctly identified)
- System errs on the side of engagement (high recall preferred)

### Category-wise Results

| Category | Passed | Total | Rate |
|----------|--------|-------|------|
| Bank Fraud | 19 | 20 | 95% |
| Government Impersonation | 14 | 15 | 93% |
| Lottery & Prize | 12 | 12 | 100% |
| Job Offer Scams | 9 | 10 | 90% |
| Delivery & Courier | 9 | 10 | 90% |
| Investment & Crypto | 9 | 10 | 90% |
| Tech Support | 7 | 8 | 87.5% |
| Utility Bills | 8 | 8 | 100% |
| Obfuscation | 14 | 15 | 93% |
| **False Positives** | **20** | **20** | **100%** |
| Edge Cases | 14 | 15 | 93% |
| Social Engineering | 10 | 10 | 100% |
| Channel Shift | 8 | 8 | 100% |
| Romance Scams | 6 | 6 | 100% |
| Insurance & Medical | 6 | 6 | 100% |
| Religious & Charity | 5 | 5 | 100% |
| Regional Language | 8 | 8 | 100% |
| SMS Abbreviations | 5 | 5 | 100% |

### Key Metrics

| Metric | Value | Rating |
|--------|-------|--------|
| **Overall Accuracy** | 95.8% | ⭐ Outstanding |
| **False Positive Rate** | 0% | ⭐ Perfect |
| **True Positive Rate** | 94.7% | ⭐ Excellent |
| **Response Time** | <5 seconds | ⭐ Fast |
| **Multi-turn Support** | 15+ messages | ⭐ Robust |

---

## 13. Known Limitations

### Detection Limitations

| Limitation | Description | Impact |
|------------|-------------|--------|
| **No ML Model** | Pattern-based, not machine learning | May miss novel scam patterns |
| **No URL Verification** | Doesn't check if URLs are actually malicious | Relies on suspicious patterns |
| **Confidence Edge Cases** | Some low-intensity scams score below threshold | ~4% false negatives |
| **New Scam Types** | Requires manual keyword updates | Lag in detecting new tactics |

### Technical Limitations

| Limitation | Description | Mitigation |
|------------|-------------|------------|
| **Gemini API Quota** | Rate limits on free tier | Multi-key rotation (2 keys × 4 models) + Grok fallback |
| **Session Memory** | In-memory storage (no persistence) | Re-extraction from `conversationHistory` on each request recovers most data |
| **Server Restart** | Accumulated intelligence lost on restart | `message_count` recalculated from history; intel re-extracted from historical messages |
| **Single Instance** | No horizontal scaling | Render handles auto-scaling |
| **Regional Languages** | Limited to common phrases | Primarily English/Hinglish |

### Edge Cases That May Fail

| Scenario | Why It Fails |
|----------|--------------|
| Very subtle phishing | No urgent/threat keywords |
| Image-based scams | Text-only analysis |
| Voice call scams | API handles text only |
| Highly obfuscated text | Complex encoding not covered |
| New bank names | Not in impersonation list |

---

## 14. Setup & Installation

Getting the honeypot running locally takes **less than 5 minutes**. Follow these steps to set up your development environment.

> **Quick Start**: If you just want to test the API, use our [live demo endpoint](#15-deployment) instead.

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git
- Google Gemini API key (free)

### Local Development Setup

#### 1. Clone Repository
```bash
git clone https://github.com/kvpradeep279/Agentic-Honey-Pot-for-Scam-Detection-Intelligence-Extraction.git
cd Agentic-Honey-Pot-for-Scam-Detection-Intelligence-Extraction
```

#### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
```bash
# Copy example to actual .env
cp .env.example .env

# Edit .env with your values
HONEYPOT_API_KEY=your-secret-api-key
GEMINI_API_KEY=your-first-gemini-key
GEMINI_API_KEY_2=your-second-gemini-key     # Optional: enables key rotation
GrokAI_API_KEY=your-grok-xai-key            # Optional: fallback AI provider
```

#### 5. Get API Keys

**Gemini (Primary — Free tier):**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key" (create 2 keys for rotation)
4. Copy keys to `.env` as `GEMINI_API_KEY` and `GEMINI_API_KEY_2`

**Grok / xAI (Fallback — Optional):**
1. Visit [xAI Console](https://console.x.ai/)
2. Create an API key
3. Copy to `.env` as `GrokAI_API_KEY`

> 💡 **Multi-key rotation** distributes load across keys to avoid hitting free tier rate limits. Grok acts as a safety net when all Gemini keys are exhausted.

#### 6. Run Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 7. Verify Installation
```bash
# Health check
curl http://localhost:8000/health

# Expected response
{"status":"healthy","message":"Honeypot API is running"}
```

---

## 15. Deployment

### Render.com Deployment

#### render.yaml Configuration
```yaml
services:
  - type: web
    name: honeypot-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: HONEYPOT_API_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: GEMINI_API_KEY_2
        sync: false
      - key: GrokAI_API_KEY
        sync: false
```

#### Deployment Steps

1. **Connect GitHub** to Render.com
2. **Create New Web Service**
3. **Select Repository**
4. **Configure Environment Variables**:
   - `HONEYPOT_API_KEY`: Your API key for authentication
   - `GEMINI_API_KEY`: Primary Google Gemini key
   - `GEMINI_API_KEY_2`: Secondary Gemini key (for rotation)
   - `GrokAI_API_KEY`: Grok/xAI key (fallback provider)
5. **Deploy**

### Production URL
```
https://your-app-name.onrender.com
```

---

## 16. Usage Examples

### Python Example

```python
import requests

API_URL = "https://your-app-name.onrender.com/honeypot"
API_KEY = "your-api-key"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# First message
payload = {
    "sessionId": "test-session-001",
    "message": {
        "sender": "scammer",
        "text": "Your SBI account is blocked. Share OTP to unblock.",
        "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

response = requests.post(API_URL, headers=headers, json=payload)
print(response.json())
# Output: {"status": "success", "reply": "Oh no! SBI? Which account..."}
```

### cURL Example

```bash
curl -X POST "https://your-app-name.onrender.com/honeypot" \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "Urgent! Your account blocked. Pay Rs 500 to unblock.",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {"channel": "SMS"}
  }'
```

---

## 17. Security Considerations

### Data Handling

| Aspect | Implementation |
|--------|----------------|
| **API Authentication** | Mandatory `x-api-key` header |
| **Secrets Management** | Environment variables, never in code |
| **Data Storage** | In-memory only, no persistence |
| **Intelligence Data** | Only sent to GUVI endpoint |

### Ethical Guidelines

| ✅ We Do | ❌ We Don't |
|----------|-------------|
| Detect scam patterns | Impersonate real individuals |
| Extract scammer data | Store victim information |
| Waste scammer time | Harass or threaten anyone |
| Report to authorities | Send illegal instructions |

### Best Practices

1. **Never commit `.env`** to version control
2. **Rotate API keys** periodically
3. **Monitor callback failures** for issues
4. **Log responsibly** (no sensitive data)

---

## 18. Future Improvements

### Planned Enhancements

| Feature | Priority | Description |
|---------|----------|-------------|
| **ML-based Detection** | High | Train model on labeled scam data |
| **Real-time URL Check** | High | Verify URLs against threat databases |
| **Voice Call Support** | Medium | Extend to phone scam detection |
| **More Languages** | Medium | Better regional language support |
| **Persistent Sessions** | Low | Database-backed session storage |
| **Analytics Dashboard** | Low | Visualize scam patterns |

### Technical Debt

- [ ] Add comprehensive logging
- [ ] Implement rate limiting
- [ ] Add request validation middleware
- [ ] Create admin endpoints for monitoring

---

## 19. References

### Statistics Sources

- [RBI Annual Report 2024](https://www.rbi.org.in)
- [NPCI UPI Statistics](https://www.npci.org.in)
- [Indian Cyber Crime Coordination Centre](https://cybercrime.gov.in)
- [TRAI Reports](https://www.trai.gov.in)

### Technical Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Google Gemini API](https://ai.google.dev/docs)
- [Render.com Docs](https://docs.render.com)
- [Pydantic](https://docs.pydantic.dev)

### Problem Statement

- GUVI Hackathon 2026 - Problem Statement 2
- Agentic Honey-Pot for Scam Detection & Intelligence Extraction

---

<div align="center">

**Built with ❤️ for GUVI Hackathon 2026**

[⬆ Back to Top](#-agentic-honey-pot-for-scam-detection--intelligence-extraction)

</div>
