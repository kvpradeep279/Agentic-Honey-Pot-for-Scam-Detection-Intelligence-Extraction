"""Quick multi-turn test"""
import requests
import time

url = 'https://agentic-honey-pot-for-scam-detection.onrender.com/honeypot'
headers = {'Content-Type': 'application/json', 'X-API-Key': 'supersecret123'}
session_id = f'multi-turn-test-{int(time.time())}'
history = []

messages = [
    'URGENT: Your SBI account blocked! Update KYC immediately. Call 9876543210. UPI: scammer@ybl',
    'Send Rs.500 to verify your account',
    'Your account number is needed for KYC update sir'
]

print(f"Session: {session_id}")
print("-" * 60)

for i, msg in enumerate(messages):
    payload = {
        'sessionId': session_id,
        'callbackUrl': 'https://httpbin.org/post',
        'message': {'role': 'scammer', 'content': msg},
        'conversationHistory': history
    }
    
    start = time.time()
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    elapsed = time.time() - start
    
    data = r.json()
    
    resp_content = data.get('response', {}).get('content', '')[:100]
    scam_detected = data.get('scamDetected', False)
    intel = data.get('extractedIntelligence', {})
    
    print(f"\nTurn {i+1} ({elapsed:.2f}s):")
    print(f"  Scammer: {msg[:60]}...")
    print(f"  Agent: {resp_content}...")
    print(f"  scamDetected: {scam_detected}")
    
    # Update history
    history.append({'role': 'scammer', 'content': msg})
    history.append(data.get('response', {}))
    
    time.sleep(1)

print("\n" + "=" * 60)
print("Final Intelligence:", data.get('extractedIntelligence', {}))
