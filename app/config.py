# ===========================================
# Configuration File
# ===========================================
# WHY: Centralizes all configuration in one place
# This makes it easy to change settings without modifying code
# ===========================================

import os
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class that holds all our settings.
    
    WHY we use environment variables:
    1. Security - API keys should never be in code
    2. Flexibility - Easy to change between environments (dev/prod)
    3. Best Practice - Follows 12-factor app methodology
    """
    
    # Your API key that clients must send to access your honeypot
    # This is what you'll submit to GUVI
    HONEYPOT_API_KEY: str = os.getenv("HONEYPOT_API_KEY", "your-secret-api-key-here")
    
    # Google Gemini API key (we'll use Gemini because it has a free tier!)
    # Get your free API key at: https://makersuite.google.com/app/apikey
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Multi-key rotation: Load all available Gemini API keys
    # Supports GEMINI_API_KEY, GEMINI_API_KEY_2, GEMINI_API_KEY_3, ...
    # WHY: Free tier has rate limits; rotating keys distributes load
    @staticmethod
    def _load_gemini_keys() -> List[str]:
        keys = []
        # Primary key
        primary = os.getenv("GEMINI_API_KEY", "")
        if primary:
            keys.append(primary)
        # Additional keys (GEMINI_API_KEY_2, _3, _4, ...)
        for i in range(2, 11):  # Support up to 10 keys
            key = os.getenv(f"GEMINI_API_KEY_{i}", "")
            if key:
                keys.append(key)
        return keys
    
    GEMINI_API_KEYS: List[str] = []
    
    # OpenAI API key (alternative if you have credits)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Grok (xAI) API key — uses OpenAI-compatible endpoint as fallback
    GROK_API_KEY: str = os.getenv("GrokAI_API_KEY", "")
    
    # GUVI Callback URL - where we send final results
    GUVI_CALLBACK_URL: str = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    # Agent settings
    # Doc example shows 18 messages (~36 total with agent replies)
    # We want to wait for enough intel before sending callback
    MAX_CONVERSATION_TURNS: int = 35  # Force callback after this many messages
    MIN_TURNS_BEFORE_CALLBACK: int = 10  # Minimum for rich intel
    
    # Scam detection threshold (0.0 to 1.0)
    SCAM_THRESHOLD: float = 0.6


# Create a global config instance
config = Config()
# Load multi-key list after instance creation
config.GEMINI_API_KEYS = Config._load_gemini_keys()
print(f"🔑 Loaded {len(config.GEMINI_API_KEYS)} Gemini API key(s)")
