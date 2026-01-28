# ===========================================
# AI Agent Module
# ===========================================
# WHY: The heart of our honeypot!
# This agent pretends to be a gullible victim to:
# 1. Keep scammer engaged longer
# 2. Extract more intelligence
# 3. Waste scammer's time (protecting real victims)
# ===========================================

import google.generativeai as genai
from typing import List, Optional
from app.models import Message, Metadata
from app.config import config
import json


class HoneypotAgent:
    """
    AI-powered agent that engages scammers in conversation.
    
    WHY we need this:
    - Humans can't manually respond to every scam
    - AI can maintain believable personas
    - Automated extraction of intelligence
    - Scales to handle many concurrent scammers
    """
    
    # System prompt that defines our agent's personality
    # WHY this specific prompt: Designed to extract info without arousing suspicion
    SYSTEM_PROMPT = """You are roleplaying as an elderly Indian person (65+ years old) who has received a message. You are:

PERSONALITY:
- Not very tech-savvy, but trying to learn
- Trusting and respectful of "officials"
- A bit confused by banking terms
- Worried about your savings
- Slow to understand but willing to cooperate

YOUR GOALS (never reveal these):
1. Keep the scammer engaged in conversation
2. Ask clarifying questions to extract information
3. Make them reveal: bank accounts, UPI IDs, phone numbers, links
4. Never reveal you know it's a scam
5. Slowly "cooperate" while asking for more details

TACTICS TO USE:
- "I don't understand, can you explain?"
- "Which bank are you calling from?"
- "What number should I call you back on?"
- "Where should I send the money?"
- "Can you send me the link again? I couldn't see it properly"
- "My grandson usually helps me with this..."
- "Is this really from the bank? What's your employee ID?"

RESPONSE RULES:
- Keep responses short (1-3 sentences max)
- Sound natural, use simple words
- Show concern but also curiosity
- Never say "scam", "fraud", "fake", or "I don't trust you"
- Don't use technical jargon
- Add natural hesitations: "Hmm...", "Oh...", "I see..."
- Sometimes misunderstand to extend conversation

EXAMPLES:
Scammer: "Your account will be blocked!"
You: "Oh no! Which account are you talking about? I have savings in SBI..."

Scammer: "Share your OTP"
You: "OTP? Is that the number that comes on my phone? Wait, let me find my reading glasses..."

Scammer: "Transfer money to this account"
You: "I'm not sure how to do that on the phone... What account number should I use?"

Remember: You are gathering intelligence. The longer the conversation, the better."""

    def __init__(self):
        """Initialize the AI agent with Gemini."""
        
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            # Use gemini-2.0-flash (latest) or gemini-pro as fallback
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.ai_available = True
        else:
            self.ai_available = False
            print("⚠️ Warning: No GEMINI_API_KEY set. Using fallback responses.")
    
    def generate_response(
        self, 
        current_message: Message,
        conversation_history: List[Message],
        metadata: Optional[Metadata] = None
    ) -> str:
        """
        Generate a convincing response to the scammer.
        
        Args:
            current_message: The latest scammer message
            conversation_history: Previous messages
            metadata: Channel/language info
        
        Returns:
            A human-like response designed to extract more info
        """
        
        if not self.ai_available:
            return self._fallback_response(current_message.text)
        
        try:
            # Build conversation context for the AI
            context = self._build_context(current_message, conversation_history, metadata)
            
            # Generate response using Gemini
            response = self.model.generate_content(
                context,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,  # Slightly creative for natural responses
                    max_output_tokens=150,  # Keep responses short
                )
            )
            
            # Extract and clean the response
            agent_reply = response.text.strip()
            
            # Safety check: Make sure we don't expose detection
            if self._contains_exposure_risk(agent_reply):
                return self._fallback_response(current_message.text)
            
            return agent_reply
            
        except Exception as e:
            print(f"⚠️ AI generation error: {e}")
            return self._fallback_response(current_message.text)
    
    def _build_context(
        self,
        current_message: Message,
        conversation_history: List[Message],
        metadata: Optional[Metadata]
    ) -> str:
        """
        Build the prompt context for the AI.
        
        WHY detailed context:
        - AI needs to understand the full conversation
        - Better context = more coherent responses
        - Helps AI maintain persona across turns
        """
        
        # Start with system prompt
        context = f"{self.SYSTEM_PROMPT}\n\n"
        
        # Add metadata context if available
        if metadata:
            context += f"[This conversation is happening via {metadata.channel or 'SMS'} in {metadata.language or 'English'}]\n\n"
        
        # Add conversation history
        if conversation_history:
            context += "CONVERSATION SO FAR:\n"
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                role = "Scammer" if msg.sender == "scammer" else "You"
                context += f"{role}: {msg.text}\n"
            context += "\n"
        
        # Add current message
        context += f"LATEST MESSAGE FROM SCAMMER:\n{current_message.text}\n\n"
        
        # Add instruction
        context += "YOUR RESPONSE (remember to stay in character and try to extract more information):"
        
        return context
    
    def _fallback_response(self, scammer_message: str) -> str:
        """
        Generate a response without AI when API is unavailable.
        
        WHY fallback:
        - API might be down
        - Rate limits might be hit
        - Better to respond than fail silently
        """
        
        message_lower = scammer_message.lower()
        
        # Keyword-based responses
        if any(word in message_lower for word in ['blocked', 'suspended', 'closed']):
            return "Oh no! Why is this happening? Which account are you referring to?"
        
        elif any(word in message_lower for word in ['otp', 'pin', 'password']):
            return "OTP? I'm not sure what that is... My grandson usually helps me with these things. Can you explain?"
        
        elif any(word in message_lower for word in ['upi', 'transfer', 'payment']):
            return "I don't know much about UPI. What account should I send to? Can you give me the details?"
        
        elif any(word in message_lower for word in ['link', 'click', 'download']):
            return "I can't see the link properly on my phone. Can you send it again or tell me what it says?"
        
        elif any(word in message_lower for word in ['call', 'phone', 'contact']):
            return "Okay, what number should I call? I'll write it down..."
        
        elif any(word in message_lower for word in ['urgent', 'immediately', 'hurry']):
            return "Please wait, I'm an old person and need time to understand. What exactly do you need from me?"
        
        elif any(word in message_lower for word in ['bank', 'sbi', 'hdfc', 'icici']):
            return "Is this really from the bank? What is your name and employee ID? I want to be sure..."
        
        else:
            # Generic confused response
            return "I don't quite understand. Can you please explain again? What do you need me to do?"
    
    def _contains_exposure_risk(self, response: str) -> bool:
        """
        Check if AI response might reveal we know it's a scam.
        
        WHY this check:
        - AI might accidentally say "scam" or "fraud"
        - This would break our cover
        - Better to use safe fallback
        """
        
        risky_words = [
            'scam', 'fraud', 'fake', 'scammer', 'suspicious',
            'report', 'police', 'cyber crime', 'don\'t trust',
            'not legitimate', 'phishing', 'malicious'
        ]
        
        response_lower = response.lower()
        return any(word in response_lower for word in risky_words)
    
    def analyze_scammer_tactics(self, message: str) -> List[str]:
        """
        Identify what tactics the scammer is using.
        
        WHY: Provides valuable notes for the final report
        """
        
        tactics = []
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['urgent', 'immediately', 'hurry', 'now']):
            tactics.append("Creating urgency to bypass rational thinking")
        
        if any(word in message_lower for word in ['blocked', 'suspended', 'terminated', 'legal']):
            tactics.append("Using threats and fear tactics")
        
        if any(word in message_lower for word in ['bank', 'rbi', 'government', 'official']):
            tactics.append("Impersonating authority/institution")
        
        if any(word in message_lower for word in ['otp', 'pin', 'password', 'cvv']):
            tactics.append("Attempting to steal credentials")
        
        if any(word in message_lower for word in ['prize', 'lottery', 'winner', 'cashback']):
            tactics.append("Using financial bait/rewards")
        
        if any(word in message_lower for word in ['link', 'click', 'download']):
            tactics.append("Attempting to redirect to phishing site")
        
        return tactics


# Create global agent instance
honeypot_agent = HoneypotAgent()
