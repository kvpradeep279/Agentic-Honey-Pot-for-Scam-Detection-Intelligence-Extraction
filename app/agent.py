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
            # Store all models to try - will attempt each on request if one fails
            self.models_to_try = [
                'gemini-flash-lite-latest',  # Highest free tier quota
                'gemini-2.5-flash-lite',     # Lite version of 2.5
                'gemini-2.0-flash-lite',     # Lite version of 2.0
                'gemini-2.5-flash',          # Full version (lower quota)
            ]
            self.ai_available = True  # Assume available, will fallback per-request if needed
            self.current_model_index = 0
            print(f"✅ Gemini API configured with {len(self.models_to_try)} model options")
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
            print("⚠️ AI not available, using fallback")
            return self._fallback_response(current_message.text, conversation_history)
        
        # Build conversation context for the AI
        context = self._build_context(current_message, conversation_history, metadata)
        
        # Try each model until one works
        for model_name in self.models_to_try:
            try:
                print(f"🤖 Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                # Generate response using Gemini
                response = model.generate_content(
                    context,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.8,  # Slightly creative for natural responses
                        max_output_tokens=300,  # Enough for 1-3 sentences
                    )
                )
                
                # Check if we got a valid response
                if not response.candidates:
                    print(f"⚠️ {model_name}: No candidates returned")
                    continue
                
                # Debug: Check if response was blocked or truncated
                finish_reason = response.candidates[0].finish_reason if response.candidates else 'NO CANDIDATES'
                print(f"🤖 {model_name} finish_reason: {finish_reason}")
                
                # Extract and clean the response
                agent_reply = response.text.strip()
                
                if not agent_reply:
                    print(f"⚠️ {model_name}: Empty response")
                    continue
                
                # Debug: Print response
                print(f"🤖 {model_name} response: '{agent_reply[:100]}...'")
                
                # Safety check: Make sure we don't expose detection
                if self._contains_exposure_risk(agent_reply):
                    print(f"⚠️ {model_name}: Response contained exposure risk, using fallback")
                    return self._fallback_response(current_message.text, conversation_history)
                
                return agent_reply
                
            except Exception as e:
                error_str = str(e)
                print(f"⚠️ {model_name} error: {error_str[:100]}")
                # If quota error, try next model
                if '429' in error_str or 'quota' in error_str.lower():
                    print(f"   Quota exceeded, trying next model...")
                    continue
                # For other errors, also try next model
                continue
        
        # All models failed, use fallback
        print("⚠️ All AI models failed, using fallback response")
        return self._fallback_response(current_message.text, conversation_history)
    
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
    
    def _fallback_response(self, scammer_message: str, conversation_history: List[Message] = None) -> str:
        """
        Generate a varied response without AI when API is unavailable.
        
        WHY fallback:
        - API might be down
        - Rate limits might be hit
        - Better to respond than fail silently
        
        Uses multiple response options and tracks used responses to avoid repetition.
        """
        import random
        import hashlib
        
        message_lower = scammer_message.lower()
        
        # Track how many messages we've exchanged to vary responses
        history_len = len(conversation_history) if conversation_history else 0
        
        # Use message hash + history length for deterministic but varied selection
        msg_hash = int(hashlib.md5(scammer_message.encode()).hexdigest()[:8], 16)
        selector = (msg_hash + history_len) % 5  # 5 options per category
        
        # Multiple response options for each category
        responses = {
            'blocked': [
                "Oh no! Why is this happening? Which account are you referring to?",
                "Blocked? But I haven't done anything wrong! Which bank are you calling from?",
                "My account is blocked? Oh dear... Can you tell me which branch this is about?",
                "What do you mean blocked? I just used my card yesterday! What is your name, sir?",
                "Hai Ram! Blocked? Please help me, what should I do? Can you give me your ID number?",
            ],
            'otp': [
                "OTP? I'm not sure what that is... My grandson usually helps me with these things. Can you explain?",
                "You mean the number that comes on my phone? I got so many messages, which one do you need?",
                "OTP... is that like a password? My phone is showing some numbers, is that it?",
                "I see a message from the bank with numbers. Should I read the whole message to you?",
                "Beta, I don't understand these technical things. The message says don't share - but you're from bank, right?",
            ],
            'upi': [
                "I don't know much about UPI. What account should I send to? Can you give me the details?",
                "UPI? My grandson set that up for me. What is your UPI ID? I'll ask him to help me send.",
                "How do I do UPI transfer? Can you give me your account number instead? That I know how to do.",
                "I have PhonePe and Paytm. Which one should I use? What is your number?",
                "UPI ID... is that like scammer.help@bank? Can you spell it out slowly for me?",
            ],
            'link': [
                "I can't see the link properly on my phone. Can you send it again or tell me what it says?",
                "My phone is old, the link is not opening. Can you tell me what website is this?",
                "I clicked but nothing happened. Can you give me the website name? I'll type it myself.",
                "My grandson says don't click links... but you're from bank, so it's safe, right? Send again please.",
                "The link shows some warning on my phone. Is this the correct link? What is the website name?",
            ],
            'call': [
                "Okay, what number should I call? I'll write it down...",
                "Should I call now? What is the number? And what name should I ask for?",
                "I will call, but my hearing is not good. Can you call me instead? My number is... wait, should I give it?",
                "What number? Is it a toll-free number? I don't have much balance on my phone.",
                "Okay beta, give me the number slowly. Also what time should I call? Who will answer?",
            ],
            'urgent': [
                "Please wait, I'm an old person and need time to understand. What exactly do you need from me?",
                "Why so urgent? You're scaring me... Let me call my son first, he handles my bank matters.",
                "Beta, don't rush me. At my age, I need to be careful. Now explain slowly what happened.",
                "Urgent urgent... everyone says urgent. But what if I make a mistake? Let me think...",
                "I understand it's urgent, but I need to verify. What is your employee code? Which branch?",
            ],
            'bank': [
                "Is this really from the bank? What is your name and employee ID? I want to be sure...",
                "Which branch are you calling from? I have accounts in multiple banks, you see...",
                "Bank calling? But I was just at the branch yesterday, they didn't say anything. What's your name?",
                "Oh, from the bank! I was worried. What is the problem exactly? Is my pension safe?",
                "SBI? HDFC? Which bank beta? I have small accounts in both. Tell me your manager's name.",
            ],
            'money': [
                "Pay money? But why? I thought banks don't ask customers to pay. Explain please...",
                "How much do I need to pay? And to which account? I need to tell my son before sending money.",
                "Money transfer? But I don't have much in my account. How much exactly?",
                "I can pay, but first tell me why. And can you send me something in writing?",
                "Send money to fix the problem? Okay, but my son handles my finances. What is your number so he can call?",
            ],
            'verify': [
                "Verify? Yes, I want to verify too. What is your full name and which department?",
                "How do I verify? Should I come to the bank branch? Which branch are you from?",
                "Verification is important, I agree. So tell me your employee ID, I will note it down.",
                "Yes, let's verify. What is the customer care number? I will call and confirm first.",
                "I want to verify you are really from bank. Can you tell me my account balance to prove?",
            ],
            'default': [
                "I don't quite understand. Can you please explain again? What do you need me to do?",
                "Sorry beta, my hearing is not so good. Can you repeat that? Slowly please...",
                "Hmm... I'm confused. My grandson usually handles these things. What exactly is the problem?",
                "I'm listening, but please explain simply. I'm not educated much, you see...",
                "Okay... I think I understand a little. But what should I do now? Tell me step by step.",
            ]
        }
        
        # Determine which category matches
        if any(word in message_lower for word in ['blocked', 'suspended', 'closed', 'freeze', 'locked']):
            category = 'blocked'
        elif any(word in message_lower for word in ['otp', 'pin', 'password', 'code', 'cvv']):
            category = 'otp'
        elif any(word in message_lower for word in ['upi', 'paytm', 'phonepe', 'gpay', '@']):
            category = 'upi'
        elif any(word in message_lower for word in ['link', 'click', 'download', 'http', 'www']):
            category = 'link'
        elif any(word in message_lower for word in ['call', 'phone', 'contact', 'dial']):
            category = 'call'
        elif any(word in message_lower for word in ['urgent', 'immediately', 'hurry', 'fast', 'quick', 'now']):
            category = 'urgent'
        elif any(word in message_lower for word in ['bank', 'sbi', 'hdfc', 'icici', 'axis', 'account']):
            category = 'bank'
        elif any(word in message_lower for word in ['pay', 'transfer', 'send', 'money', 'amount', 'rs', 'rupee']):
            category = 'money'
        elif any(word in message_lower for word in ['verify', 'confirm', 'validate', 'authenticate']):
            category = 'verify'
        else:
            category = 'default'
        
        # Select response based on hash to ensure variety but consistency for same message
        return responses[category][selector % len(responses[category])]
    
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
