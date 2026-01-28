# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

An AI-powered honeypot API that detects scam messages, engages scammers in multi-turn conversations, and extracts intelligence.

## Features

- 🕵️ **Scam Detection**: Identifies fraudulent messages using keyword analysis and pattern matching
- 🤖 **AI Agent**: Uses Google Gemini to generate believable human-like responses
- 📊 **Intelligence Extraction**: Extracts bank accounts, UPI IDs, phone numbers, and phishing links
- 🔄 **Multi-turn Conversations**: Maintains conversation state across multiple messages
- 📡 **Callback Reporting**: Automatically reports findings to evaluation endpoint

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file:
```
HONEYPOT_API_KEY=your-secret-api-key
GEMINI_API_KEY=your-gemini-api-key
```

### 3. Run Locally
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Test
```bash
python test_local.py
```

## API Endpoints

### POST /honeypot
Main endpoint for receiving scam messages.

**Headers:**
- `x-api-key`: Your API key
- `Content-Type`: application/json

**Request Body:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your account will be blocked!",
    "timestamp": "2026-01-28T10:00:00Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

## Deployment

### Render.com
1. Push code to GitHub
2. Connect repo to Render
3. Set environment variables
4. Deploy!

## License
MIT
