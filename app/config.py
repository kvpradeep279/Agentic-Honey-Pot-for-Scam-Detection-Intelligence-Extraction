# ===========================================
# Configuration File
# ===========================================
# WHY: Centralizes all configuration in one place
# This makes it easy to change settings without modifying code
# ===========================================

import os
from dotenv import load_dotenv

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
    
    # OpenAI API key (alternative if you have credits)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # GUVI Callback URL - where we send final results
    GUVI_CALLBACK_URL: str = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    # Agent settings
    MAX_CONVERSATION_TURNS: int = 10  # Maximum messages before ending engagement
    MIN_TURNS_BEFORE_CALLBACK: int = 3  # Minimum turns before sending callback
    
    # Scam detection threshold (0.0 to 1.0)
    SCAM_THRESHOLD: float = 0.6


# Create a global config instance
config = Config()
