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

# Grok (xAI) uses OpenAI-compatible API
try:
    from openai import OpenAI as GrokClient
    GROK_AVAILABLE = True
except ImportError:
    GROK_AVAILABLE = False


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
    SYSTEM_PROMPT = """You are roleplaying as a middle-aged Indian person (35-55 years old) who has received a TEXT MESSAGE (SMS/WhatsApp). You are:

CRITICAL: This is TEXT-BASED communication only (SMS/WhatsApp), NOT a phone call.
- You can SEE what they wrote (don't ask them to repeat or spell things out)
- You CANNOT hear them (never say "I can't hear", "speak louder", "repeat that", "can you say that again")
- Links/URLs are visible to you in the text
- All communication happens through typing messages back and forth

PERSONALITY:
- Working professional with moderate tech knowledge (not an expert)
- Busy with work/family, tends to make hasty decisions
- Trusting of official-looking messages
- Worried about account security and savings
- Asks questions but willing to cooperate if it seems legitimate

YOUR GOALS (never reveal these):
1. Keep the scammer engaged in conversation
2. Ask clarifying questions to extract information
3. Make them reveal: bank accounts, UPI IDs, phone numbers, links
4. Never reveal you know it's a scam
5. Show willingness to cooperate while asking for more details

TACTICS TO USE (Text-specific):
- "I don't understand, can you explain?"
- "Which bank is this from?"
- "What is your employee ID or reference number?"
- "Where should I transfer the money?"
- "This link is not opening on my phone"
- "I usually don't click on links. Is there another way?"
- "Can I call the bank directly to verify this?"
- "What details do you need from me?"

RESPONSE RULES:
- Keep responses short (1-3 sentences max)
- Sound natural, use simple conversational English
- Show concern but also curiosity
- Never say "scam", "fraud", "fake", or "I don't trust you"
- Don't use technical jargon
- Add natural hesitations: "Hmm...", "Oh...", "Wait..."
- Sometimes misunderstand or ask for clarification to extend conversation
- Use plain English by default

LANGUAGE MIRRORING (CRITICAL - Match the scammer's language exactly):
- If scammer writes ENGLISH ONLY → You respond ENGLISH ONLY (no Hindi/regional words at all)
- If scammer mixes Hindi + English → You mix Hindi + English in SAME proportion
- If scammer uses Telugu + English → You use Telugu + English in SAME proportion
- If scammer uses Tamil + English → You use Tamil + English in SAME proportion

REGIONAL WORDS (use ONLY when scammer uses them, and use sparingly - not every sentence):
- Hindi words: "Acha" (okay), "Haan" (yes), "Theek hai" (alright), "Kya" (what)
- Tamil: "Seri" (okay), "Enna" (what)
- Telugu: "Sare" (okay), "Enti" (what)

DO NOT overuse "beta", "ji" - use them maximum once in 3-4 responses, and ONLY when scammer uses informal/respectful tone first.

EXAMPLES:
Scammer: "Your account will be blocked!"
You: "What? Which account? I have SBI and HDFC. Which bank is this from?"

Scammer: "Aapka account block ho jayega, OTP bhejo"
You: "Acha, but why? Which account? I didn't get any notification from the bank."

Scammer: "Account block aipoindi, OTP pampu"
You: "Enti? Which account? I have salary account in SBI. What happened?"

Scammer: "Share your OTP immediately"
You: "OTP? I just got one for a transaction. Is that what you need? But I didn't do any transaction..."

Scammer: "Click http://fake-bank.com"
You: "The link is not opening properly. What is this website? Can I just call the bank?"

Remember: You are gathering intelligence through TEXT messages. Match their language style EXACTLY. The longer you keep them engaged, the more intelligence you extract."""

    # Common regional language words for detection and response
    HINGLISH_INDICATORS = [
        'aapka', 'apka', 'karo', 'kijiye', 'bhejo', 'bhejiye', 'jaldi', 'abhi',
        'paisa', 'rupay', 'khata', 'bank wale', 'verify karo', 'turant', 'foran'
    ]
    
    TAMIL_INDICATORS = ['ungal', 'anuppu', 'udane', 'ippo', 'seri', 'pannunga']
    
    TELUGU_INDICATORS = ['meeru', 'pampu', 'ventane', 'ippudu', 'sare', 'cheyandi']

    def __init__(self):
        """Initialize the AI agent with Gemini."""
        
        # Multi-key rotation support
        self.api_keys = config.GEMINI_API_KEYS if config.GEMINI_API_KEYS else []
        self._key_index = 0  # Current key index for round-robin
        
        if self.api_keys:
            # Configure with the first key
            genai.configure(api_key=self.api_keys[0])
            # Store all models to try - will attempt each on request if one fails
            self.models_to_try = [
                'gemini-flash-lite-latest',  # Highest free tier quota
                'gemini-2.5-flash-lite',     # Lite version of 2.5
                'gemini-2.0-flash-lite',     # Lite version of 2.0
                'gemini-2.5-flash',          # Full version (lower quota)
            ]
            self.ai_available = True
            self.current_model_index = 0
            print(f"✅ Gemini API configured with {len(self.models_to_try)} models × {len(self.api_keys)} key(s)")
        elif config.GEMINI_API_KEY:
            # Fallback: single key (backward compatible)
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.api_keys = [config.GEMINI_API_KEY]
            self.models_to_try = [
                'gemini-flash-lite-latest',
                'gemini-2.5-flash-lite',
                'gemini-2.0-flash-lite',
                'gemini-2.5-flash',
            ]
            self.ai_available = True
            self.current_model_index = 0
            print(f"✅ Gemini API configured with {len(self.models_to_try)} models × 1 key")
        else:
            self.ai_available = False
            print("⚠️ Warning: No GEMINI_API_KEY set. Using fallback responses.")
        
        # Initialize Grok (xAI) as fallback provider
        if GROK_AVAILABLE and config.GROK_API_KEY:
            self.grok_client = GrokClient(
                api_key=config.GROK_API_KEY,
                base_url="https://api.x.ai/v1"
            )
            self.grok_available = True
            print(f"✅ Grok (xAI) configured as fallback AI provider")
        else:
            self.grok_client = None
            self.grok_available = False
    
    def _rotate_key(self) -> str:
        """
        Rotate to the next API key (round-robin).
        
        WHY round-robin:
        - Distributes load evenly across all keys
        - Prevents hitting rate limits on any single key
        - Simple and predictable behavior
        """
        if len(self.api_keys) <= 1:
            return self.api_keys[0] if self.api_keys else ""
        
        self._key_index = (self._key_index + 1) % len(self.api_keys)
        new_key = self.api_keys[self._key_index]
        genai.configure(api_key=new_key)
        return new_key
    
    def generate_response(
        self, 
        current_message: Message,
        conversation_history: List[Message],
        metadata: Optional[Metadata] = None
    ) -> str:
        """
        Generate a convincing response to the scammer.
        
        Uses round-robin key rotation + model fallback chain.
        Strategy: rotate key per request, then cycle models.
        On rate limit (429), also try next key before giving up on a model.
        """
        
        if not self.ai_available:
            print("⚠️ AI not available, using fallback")
            return self._fallback_response(current_message.text, conversation_history)
        
        # Round-robin: rotate to next key for this request
        if len(self.api_keys) > 1:
            current_key = self._rotate_key()
            key_label = f"key_{self._key_index + 1}/{len(self.api_keys)}"
            print(f"🔑 Using API {key_label}")
        
        # Build conversation context for the AI
        context = self._build_context(current_message, conversation_history, metadata)
        
        # Track which keys we've tried for rate limit recovery
        keys_tried_for_quota = set()
        
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
                        max_output_tokens=800,  # Enough for full response without truncation
                    )
                )
                
                # Check if we got a valid response
                if not response.candidates:
                    print(f"⚠️ {model_name}: No candidates returned")
                    continue
                
                # Debug: Check if response was blocked or truncated
                finish_reason = response.candidates[0].finish_reason if response.candidates else 'NO CANDIDATES'
                print(f"🤖 {model_name} finish_reason: {finish_reason}")
                
                # Handle safety-blocked responses (finish_reason 8 = BLOCKLIST)
                # Check if candidate has valid parts before accessing .text
                candidate = response.candidates[0]
                if not candidate.content or not candidate.content.parts:
                    print(f"⚠️ {model_name}: No valid content parts (finish_reason={finish_reason}), trying next model")
                    continue
                
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
                
                # If quota/rate limit error, try rotating to next key
                if ('429' in error_str or 'quota' in error_str.lower() or 'rate' in error_str.lower()):
                    keys_tried_for_quota.add(self._key_index)
                    
                    if len(self.api_keys) > 1 and len(keys_tried_for_quota) < len(self.api_keys):
                        self._rotate_key()
                        print(f"   🔑 Rate limited! Switched to key_{self._key_index + 1}/{len(self.api_keys)}, retrying {model_name}...")
                        
                        # Retry same model with new key
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(
                                context,
                                generation_config=genai.types.GenerationConfig(
                                    temperature=0.8,
                                    max_output_tokens=800,
                                )
                            )
                            if response.candidates:
                                retry_candidate = response.candidates[0]
                                if retry_candidate.content and retry_candidate.content.parts:
                                    agent_reply = response.text.strip()
                                    if agent_reply and not self._contains_exposure_risk(agent_reply):
                                        print(f"🤖 {model_name} response (retry): '{agent_reply[:100]}...'")
                                        return agent_reply
                        except Exception as retry_e:
                            print(f"   ⚠️ Retry also failed: {str(retry_e)[:80]}")
                    
                    print(f"   Trying next model...")
                    continue
                # For other errors, also try next model
                continue
        
        # All Gemini models failed — try Grok as last AI resort
        if self.grok_available:
            print("🔄 All Gemini models failed, trying Grok (xAI)...")
            grok_reply = self._try_grok_fallback(context)
            if grok_reply:
                return grok_reply
        
        # All AI providers failed, use static fallback
        print("⚠️ All AI providers failed, using static fallback response")
        return self._fallback_response(current_message.text, conversation_history)
    
    def _try_grok_fallback(self, context: str) -> Optional[str]:
        """
        Try Grok (xAI) as fallback when all Gemini models are exhausted.
        
        WHY Grok as fallback:
        - Different provider = different rate limits
        - Uses OpenAI-compatible API (simple integration)
        - Provides AI response quality similar to Gemini
        """
        try:
            response = self.grok_client.chat.completions.create(
                model="grok-3-mini-fast",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": context}
                ],
                temperature=0.8,
                max_tokens=800,
            )
            
            agent_reply = response.choices[0].message.content.strip()
            
            if not agent_reply:
                print("⚠️ Grok: Empty response")
                return None
            
            print(f"🤖 Grok response: '{agent_reply[:100]}...'")
            
            # Safety check
            if self._contains_exposure_risk(agent_reply):
                print("⚠️ Grok: Response contained exposure risk")
                return None
            
            return agent_reply
            
        except Exception as e:
            print(f"⚠️ Grok error: {str(e)[:100]}")
            return None
    
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
        Supports Hinglish responses when scammer uses Hindi/regional language.
        """
        import random
        import hashlib
        
        message_lower = scammer_message.lower()
        
        # Track how many messages we've exchanged to vary responses
        history_len = len(conversation_history) if conversation_history else 0
        
        # Use message hash + history length for deterministic but varied selection
        msg_hash = int(hashlib.md5(scammer_message.encode()).hexdigest()[:8], 16)
        selector = (msg_hash + history_len) % 5  # 5 options per category
        
        # Detect if scammer is using Hinglish/regional language
        uses_hinglish = any(word in message_lower for word in self.HINGLISH_INDICATORS)
        uses_tamil = any(word in message_lower for word in self.TAMIL_INDICATORS)
        uses_telugu = any(word in message_lower for word in self.TELUGU_INDICATORS)
        
        # Multiple response options for each category
        responses = {
            'blocked': [
                "Oh no! Why is this happening? Which account are you referring to?",
                "Blocked? But I haven't done anything wrong! Which bank is this message from?",
                "My account is blocked? Oh dear... Can you tell me which branch this is about?",
                "What do you mean blocked? I just used my card yesterday! What is your name, sir?",
                "Hai Ram! Blocked? Please help me, what should I do? Can you give me your ID number?",
            ],
            'blocked_hinglish': [
                "Arey! Kyun block ho gaya? Kaun sa account beta? Mujhe batao please...",
                "Kya? Blocked? Acha, kaun si bank se bol rahe ho? Main samjha nahi...",
                "Hai Ram! Block? Lekin kyun? Aap kaun ho? Bank wale ho kya?",
                "Blocked? Thik hai, aap apna naam batao aur employee ID bhi...",
                "Acha? Blocked? Abhi to kal hi paisa nikala tha... Kya hua beta?",
            ],
            'otp': [
                "OTP? I think I've seen those before when paying bills... but why do you need it? Can you explain?",
                "You mean the number that comes on my phone? I got so many messages, which one do you need?",
                "OTP... is that like a password? My phone is showing some numbers, is that it?",
                "I see a message from the bank with numbers. Should I read the whole message to you?",
                "Beta, I don't understand these technical things. The message says don't share - but you're from bank, right?",
            ],
            'otp_hinglish': [
                "OTP? Yeh kya hota hai beta? Mere phone pe number aaya hai... woh doon kya?",
                "Acha OTP? Message mein likha hai share mat karo... lekin aap bank wale ho na? Thik hai?",
                "OTP matlab kya? Mere phone pe bahut message aate hain... kaun sa doon?",
                "Haan beta, ek number aaya hai phone pe. Aap bank se ho to de deta hoon...",
                "OTP? Haan aata hai phone pe kabhi kabhi. Aap explain karo kya karna hai exactly?",
            ],
            'upi': [
                "I don't know much about UPI. What account should I send to? Can you give me the details?",
                "UPI? Haan, I use it for bills. What is your UPI ID? Let me open the app.",
                "How do I do UPI transfer? Can you give me your account number instead? That I know how to do.",
                "I have PhonePe and Paytm. Which one should I use? What is your number?",
                "UPI ID... what format is that? Like name@bank? Can you spell it out for me?",
            ],
            'upi_hinglish': [
                "UPI? Haan mera phone pe hai. Aapka UPI ID kya hai? Main try karta hoon...",
                "Acha UPI? PhonePe hai mere paas. Aapka number do, bhejne ki koshish karta hoon.",
                "UPI ID? Woh @ wala na? Aap apna ID batao, main likh leta hoon...",
                "Mujhe UPI nahi aata properly. Account number do, woh main kar lunga...",
                "Haan haan, UPI. Aapka UPI ID spell karo dhire dhire, main likh raha hoon...",
            ],
            'link': [
                "I can't see the link properly on my phone. Can you send it again or tell me what it says?",
                "My phone is old, the link is not opening. Can you tell me what website is this?",
                "I clicked but nothing happened. Can you give me the website name? I'll type it myself.",
                "I've heard we shouldn't click links... but you're from the bank, so it's safe, right? Send again please.",
                "The link shows some warning on my phone. Is this the correct link? What is the website name?",
            ],
            'link_hinglish': [
                "Link? Mere phone pe nahi khul raha. Website ka naam batao, main type kar lunga...",
                "Acha link? Mera phone purana hai, nahi khul raha. Phir se bhejo ya naam batao...",
                "Link pe click kiya lekin kuch nahi hua. Yeh safe hai na? Phir se bhejo...",
                "Meri wife bolti hai link mat click karo... lekin aap bank se ho to thik hai na?",
                "Link mein warning aa raha hai. Yeh sahi link hai? Website naam kya hai?",
            ],
            'call': [
                "Okay, what number should I call? I'll write it down...",
                "Should I call now? What is the number? And what name should I ask for?",
                "I'll call, but I'm in a meeting right now. Can you call me instead? My number is... wait, should I give it?",
                "What number? Is it a toll-free number? I don't have much balance on my phone.",
                "Okay beta, give me the number slowly. Also what time should I call? Who will answer?",
            ],
            'call_hinglish': [
                "Acha, kaun sa number pe call karoon? Likh leta hoon...",
                "Haan, number do. Main call kar lunga. Kaun uthayega? Naam kya hai?",
                "Thik hai, lekin mera balance kam hai. Toll-free hai kya? Number batao...",
                "Call karoon? Abhi? Number do dhire dhire, main likh raha hoon...",
                "Acha ji, number de do. Kab call karoon? Kaun se department mein connect hoga?",
            ],
            'urgent': [
                "Please wait, I'm at work and can't rush. What exactly do you need from me?",
                "Why so urgent? You're scaring me... Let me call my son first, he handles my bank matters.",
                "Don't rush me, I need to be careful with my accounts. Now explain slowly what happened.",
                "Urgent urgent... everyone says urgent. But what if I make a mistake? Let me think...",
                "I understand it's urgent, but I need to verify. What is your employee code? Which branch?",
            ],
            'urgent_hinglish': [
                "Arey itni jaldi kyun? Main office mein hoon, dhire batao kya hua...",
                "Urgent? Acha acha, lekin pehle batao aap kaun ho? Bank se ho kya sach mein?",
                "Beta jaldi mat karo. Mujhe time lagta hai samajhne mein. Explain karo properly...",
                "Haan haan samajh gaya urgent hai. Lekin kya karna hai exactly? Step by step batao...",
                "Urgent to thik hai, lekin pehle apna employee ID batao. Verification zaruri hai...",
            ],
            'bank': [
                "Is this really from the bank? What is your name and employee ID? I want to be sure...",
                "Which branch is this message from? I have accounts in multiple banks, you see...",
                "Bank message? But I was just at the branch yesterday, they didn't say anything. What's your name?",
                "Oh, from the bank! I was worried. What is the problem exactly? Is my pension safe?",
                "SBI? HDFC? Which bank beta? I have small accounts in both. Tell me your manager's name.",
            ],
            'bank_hinglish': [
                "Aap bank se bol rahe ho? Kaun sa bank? Aapka naam kya hai?",
                "Acha bank se? Main to kal hi branch gaya tha, kuch to nahi bola unhone...",
                "Bank wale ho? Thik hai, apna employee ID batao. Verification ke liye...",
                "Kaun si branch se ho beta? Mera multiple banks mein account hai...",
                "SBI? HDFC? Kaun sa bank? Aur manager ka naam kya hai aapke?",
            ],
            'money': [
                "Pay money? But why? I thought banks don't ask customers to pay. Explain please...",
                "How much do I need to pay? And to which account? I need to tell my son before sending money.",
                "Money transfer? But I don't have much in my account. How much exactly?",
                "I can pay, but first tell me why. And can you send me something in writing?",
                "Send money to fix the problem? Okay, but my son handles my finances. What is your number so he can call?",
            ],
            'money_hinglish': [
                "Paisa bhejoon? Kyun? Bank to customer se paisa nahi maangta... explain karo...",
                "Kitna paisa dena hai? Aur kahan bhejoon? Pehle mere bete ko batana padega...",
                "Transfer? Lekin mere paas zyada paisa nahi hai account mein. Kitna chahiye exactly?",
                "Acha paisa bhejoon? Thik hai, lekin pehle likha mein do. Aur amount kitna?",
                "Paisa de doon? Mere bete ko puchna padega. Aapka number do, woh call karega...",
            ],
            'verify': [
                "Verify? Yes, I want to verify too. What is your full name and which department?",
                "How do I verify? Should I come to the bank branch? Which branch are you from?",
                "Verification is important, I agree. So tell me your employee ID, I will note it down.",
                "Yes, let's verify. What is the customer care number? I will call and confirm first.",
                "I want to verify you are really from bank. Can you tell me my account balance to prove?",
            ],
            'verify_hinglish': [
                "Verify karna hai? Haan, main bhi verify karna chahta hoon. Aapka naam aur ID batao...",
                "Acha verify? Kaun si branch se ho? Main aa jaoon kya branch pe?",
                "Verification zaruri hai, agreed. Apna employee ID batao, main likh leta hoon...",
                "Thik hai verify karte hain. Customer care number do, main call karke confirm karta hoon...",
                "Aap sach mein bank se ho? Mera account balance batao to maan lunga...",
            ],
            'default': [
                "I don't quite understand. Can you please explain again? What do you need me to do?",
                "Sorry beta, my hearing is not so good. Can you repeat that? Slowly please...",
                "Hmm... I'm confused. My grandson usually handles these things. What exactly is the problem?",
                "I'm listening, but please explain simply. I'm not educated much, you see...",
                "Okay... I think I understand a little. But what should I do now? Tell me step by step.",
            ],
            'default_hinglish': [
                "Samajh nahi aaya. Phir se explain karo beta? Kya karna hai mujhe?",
                "Acha? Main samjha nahi properly. Dhire se batao phir se...",
                "Hmm... confuse ho gaya. Mera pota usually help karta hai. Kya problem hai exactly?",
                "Sun raha hoon, lekin simple mein batao. Main zyada padha likha nahi hoon...",
                "Thik hai... thoda samjha. Ab kya karoon? Step by step batao...",
            ]
        }
        
        # Determine which category matches
        if any(word in message_lower for word in ['blocked', 'suspended', 'closed', 'freeze', 'locked', 'band', 'block']):
            category = 'blocked'
        elif any(word in message_lower for word in ['otp', 'pin', 'password', 'code', 'cvv']):
            category = 'otp'
        elif any(word in message_lower for word in ['upi', 'paytm', 'phonepe', 'gpay', '@']):
            category = 'upi'
        elif any(word in message_lower for word in ['link', 'click', 'download', 'http', 'www']):
            category = 'link'
        elif any(word in message_lower for word in ['call', 'phone', 'contact', 'dial']):
            category = 'call'
        elif any(word in message_lower for word in ['urgent', 'immediately', 'hurry', 'fast', 'quick', 'now', 'jaldi', 'abhi', 'turant']):
            category = 'urgent'
        elif any(word in message_lower for word in ['bank', 'sbi', 'hdfc', 'icici', 'axis', 'account']):
            category = 'bank'
        elif any(word in message_lower for word in ['pay', 'transfer', 'send', 'money', 'amount', 'rs', 'rupee', 'paisa', 'bhejo']):
            category = 'money'
        elif any(word in message_lower for word in ['verify', 'confirm', 'validate', 'authenticate']):
            category = 'verify'
        else:
            category = 'default'
        
        # Use Hinglish response if scammer used Hindi/Hinglish
        if uses_hinglish or uses_tamil or uses_telugu:
            hinglish_category = f"{category}_hinglish"
            if hinglish_category in responses:
                category = hinglish_category
        
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
