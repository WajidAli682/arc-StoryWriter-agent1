from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import time
import re
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='')

# Config
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
AIML_API_KEY = os.getenv("AIML_API_KEY")

# Tera Wallet
CREATOR_ADDRESS = "0xc566bc1e529a71ece83145f98aac3c818d1311b3"

# Arc Testnet
w3 = Web3(Web3.HTTPProvider("https://rpc.testnet.arc.network"))

# USDC Contract
USDC_ADDRESS = "0x3600000000000000000000000000000000000000"
USDC_DECIMALS = 6

contract = w3.eth.contract(address=USDC_ADDRESS, abi=[
    {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
])

full_story = ""
user_wallet = None

print(f"🎭 AI Story Teller Server Started on Railway!")
print(f"💰 Creator receives USDC at: {CREATOR_ADDRESS}")

# AI & TTS Functions
def generate_story_with_ai(prompt):
    """Generate engaging 2-3 minute story with AI"""
    try:
        # Extract topic from any input format
        topic = extract_topic(prompt)
        
        headers = {"Authorization": f"Bearer {AIML_API_KEY}", "Content-Type": "application/json"}
        
        # Better system prompt for engaging stories
        system_prompt = """You are a master storyteller. Create engaging, magical stories that are 2-3 minutes long when read aloud. 
        Stories should have vivid descriptions, emotional depth, and be appropriate for all ages.
        Keep the story between 250-350 words."""
        
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a magical story about: {topic}"}
            ],
            "max_tokens": 600,
            "temperature": 0.8
        }
        
        response = requests.post("https://api.aimlapi.com/v1/chat/completions", 
                               json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            story = response.json()["choices"][0]["message"]["content"].strip()
            return clean_story_text(story)
        else:
            print(f"AI API Error: {response.status_code}")
            
    except Exception as e:
        print(f"AI Generation Error: {e}")
    
    # Fallback story
    return """In a hidden valley where moonlight danced on silver streams, lived a young fox named Ember. Unlike other foxes, Ember could understand the whispers of the wind and the secrets of the stars.

One evening, the Northern Star shared a prophecy about restoring the valley's fading magic. As darkness crept across the land, Ember embarked on a journey to the ancient Stone Circle.

With a gentle touch and pure heart, she reawakened the valley's magic, learning that true power lies in connection and compassion. The stars shone brighter than ever, and the streams sang songs of renewal."""

def extract_topic(prompt):
    """Extract story topic from any input format"""
    prompt = prompt.lower().strip()
    
    # Remove common prefixes
    prefixes = ['tell me a story about', 'story about', 'about', 'generate story about', 
                'create story about', 'tell story about', 'make story about']
    
    for prefix in prefixes:
        if prompt.startswith(prefix):
            prompt = prompt[len(prefix):].strip()
            break
    
    # If empty after processing, return default
    if not prompt or len(prompt) < 2:
        return "magical adventure"
    
    return prompt

def clean_story_text(story):
    """Clean and format story text"""
    # Remove extra whitespace
    story = re.sub(r'\s+', ' ', story).strip()
    
    # Ensure proper sentence endings
    if not story.endswith(('.', '!', '?')):
        story += '.'
    
    return story

def create_teaser(full_story):
    """Create teaser from full story (20-30 seconds of reading)"""
    sentences = full_story.split('. ')
    
    if len(sentences) <= 2:
        # If very short story, use first 120 characters
        teaser = full_story[:120] + '...' if len(full_story) > 120 else full_story
    else:
        # Use first 2 sentences for teaser
        teaser_sentences = sentences[:2]
        teaser = '. '.join(teaser_sentences) + '...'
    
    teaser += " 🎧 Tip $0.50 to unlock the full magical story!"
    return teaser

def text_to_speech(text, filename):
    """Convert text to speech using ElevenLabs"""
    if not ELEVENLABS_API_KEY:
        print("ElevenLabs API key not configured")
        return None
        
    try:
        url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8
            }
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=60)
        
        if response.status_code == 200:
            filepath = os.path.join("public", filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"✅ Audio generated: {filename}")
            return f"/{filename}?v={int(time.time())}"
        else:
            print(f"❌ TTS Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ TTS Exception: {e}")
    
    return None

# Payment Functions - ORIGINAL LOGIC
def build_tip_tx(user_address):
    """Build transaction for USDC tip - ORIGINAL WORKING CODE"""
    try:
        user_checksum = w3.to_checksum_address(user_address)
        amount_wei = int(0.5 * 10**USDC_DECIMALS)

        # Check USDC balance
        balance = contract.functions.balanceOf(user_checksum).call()
        if balance < amount_wei:
            return None, "Not enough USDC! Get test USDC from faucet.arc.network"

        # Check ETH balance for gas
        eth_balance = w3.eth.get_balance(user_checksum)
        min_eth_for_gas = w3.to_wei(0.001, 'ether')
        if eth_balance < min_eth_for_gas:
            return None, "Not enough ETH for gas fees! Get test ETH from faucet"

        nonce = w3.eth.get_transaction_count(user_checksum)
        current_gas_price = w3.eth.gas_price
        gas_price = max(current_gas_price, w3.to_wei(15, 'gwei'))

        transfer_func = "0xa9059cbb"
        to_address_padded = CREATOR_ADDRESS[2:].zfill(64)
        amount_padded = hex(amount_wei)[2:].zfill(64)
        data = transfer_func + to_address_padded + amount_padded

        tx = {
            'from': user_checksum,
            'to': USDC_ADDRESS,
            'value': '0x0',
            'data': data,
            'chainId': '0x4CFA2',
            'gas': '0x186A0',
            'gasPrice': hex(int(gas_price)),
            'nonce': hex(nonce)
        }

        print(f"💰 Tip TX built for {user_address}")
        return tx, "ready"

    except Exception as e:
        print(f"❌ TX build error: {e}")
        return None, str(e)

# Routes - ORIGINAL STRUCTURE
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('public', filename)

@app.route('/connect', methods=['POST'])
def connect():
    global user_wallet
    data = request.json
    user_wallet = data.get('wallet')
    if user_wallet and w3.is_address(user_wallet):
        print(f"🔗 Wallet connected: {user_wallet}")
        return jsonify({"status": "connected", "wallet": user_wallet})
    return jsonify({"status": "failed"}), 400

@app.route('/chat', methods=['POST'])
def chat():
    global full_story, user_wallet
    
    data = request.json
    user_message = data.get('message', '').strip().lower()
    
    if not user_message:
        return jsonify({"reply": "Please tell me what story you'd like to hear! Try: 'about cats', 'space adventure', or 'magical forest'"})
    
    if not user_wallet:
        return jsonify({"reply": "Please connect your wallet first to generate stories!"})
    
    print(f"📖 Story request: {user_message}")
    
    # Generate story for ANY input (not just 'story' or 'tell')
    if len(user_message) > 2:  # Any meaningful input
        full_story = generate_story_with_ai(user_message)
        teaser = create_teaser(full_story)
        audio = text_to_speech(teaser, "teaser.mp3")
        
        return jsonify({
            "reply": "✨ Your story teaser is ready!",
            "written": teaser,
            "audio": f"/teaser.mp3?v={int(time.time())}",
            "canTip": True
        })
    
    return jsonify({
        "reply": "Please enter a story topic! Examples: 'about dragons', 'space adventure', 'magical forest'"
    })

@app.route('/tip', methods=['POST'])
def tip():
    global full_story, user_wallet
    
    if not user_wallet:
        return jsonify({"reply": "Connect wallet first!"})
    
    tx, status = build_tip_tx(user_wallet)
    if tx:
        return jsonify({
            "reply": "Confirm in MetaMask to pay $0.50!",
            "tx": tx,
            "status": "sign_required"
        })
    else:
        return jsonify({"reply": f"Tip failed: {status}"})

# Confirm tx after user signs - ORIGINAL LOGIC
@app.route('/confirm_tx', methods=['POST'])
def confirm_tx():
    global full_story
    tx_hash = request.json.get('tx_hash')
    if not tx_hash:
        return jsonify({"error": "No tx hash"}), 400

    # Generate full story audio - ORIGINAL LOGIC
    audio = text_to_speech(full_story, "full.mp3")
    
    return jsonify({
        "reply": "Tip received! Full story unlocked!",
        "written": full_story,
        "audio": f"/full.mp3?v={int(time.time())}",
        "explorer": f"https://testnet.arcscan.app/tx/{tx_hash}"
    })

if __name__ == '__main__':
    # Create public directory if it doesn't exist
    if not os.path.exists('public'):
        os.makedirs('public')
    
    port = int(os.environ.get('PORT', 3000))
    print("🚀 Starting AI Story Teller Server on Railway...")
    print(f"📍 http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)