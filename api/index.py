from flask import Flask, request, jsonify
import os
import requests
import json

app = Flask(__name__)

# Config - Vercel environment variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
AIML_API_KEY = os.getenv("AIML_API_KEY", "")

# In-memory storage
user_sessions = {}

print("🎭 AI Story Teller Server Started!")

# AI Functions
def generate_story_with_ai(prompt):
    """Generate engaging story"""
    try:
        # Simple story generation for testing
        story = f"Once upon a time, in a land far away, there was a magical {prompt}. This story was created just for you. The full version with AI and audio will be available soon!"
        return story
    except Exception as e:
        return f"A wonderful story about {prompt} awaits you!"

def create_teaser(full_story):
    """Create teaser from full story"""
    teaser = full_story[:120] + "..."
    teaser += " 🎧 Tip $0.50 to unlock the full magical story!"
    return teaser

# Routes
@app.route('/connect', methods=['POST'])
def connect():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "failed", "error": "No data"}), 400
            
        user_wallet = data.get('wallet', '').strip()
        
        if user_wallet and len(user_wallet) > 10:  # Basic validation
            user_sessions[user_wallet] = {"full_story": ""}
            return jsonify({
                "status": "connected", 
                "wallet": user_wallet,
                "message": "Wallet connected successfully!"
            })
        else:
            return jsonify({"status": "failed", "error": "Invalid wallet address"}), 400
            
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"reply": "No data received"}), 400
            
        user_message = data.get('message', '').strip().lower()
        user_wallet = data.get('wallet', '')
        
        print(f"📖 Received: {user_message} from {user_wallet}")
        
        if not user_message:
            return jsonify({"reply": "Please enter a story topic!"})
        
        if not user_wallet:
            return jsonify({"reply": "Please connect your wallet first!"})
        
        # Generate story
        full_story = generate_story_with_ai(user_message)
        teaser = create_teaser(full_story)
        
        # Store in session
        user_sessions[user_wallet] = {"full_story": full_story}
        
        return jsonify({
            "reply": "✨ Your story teaser is ready!",
            "written": teaser,
            "canTip": True
        })
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return jsonify({"reply": "Server error occurred. Please try again."}), 500

@app.route('/tip', methods=['POST'])
def tip():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"reply": "No data received"}), 400
            
        user_wallet = data.get('wallet', '')
        
        if not user_wallet:
            return jsonify({"reply": "Connect wallet first!"})
        
        # Simple test transaction
        test_tx = {
            "from": user_wallet,
            "to": "0x2de592b3951807dfb72931596d11fe93b753881e",
            "value": "0x0",
            "data": "0x",
            "chainId": "0x4CFA2",
            "gas": "0x186A0",
            "gasPrice": "0x0",
            "nonce": "0x0"
        }
        
        return jsonify({
            "reply": "Confirm in MetaMask to pay $0.50!",
            "tx": test_tx,
            "status": "sign_required"
        })
            
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

@app.route('/confirm_tx', methods=['POST'])
def confirm_tx():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400
            
        tx_hash = data.get('tx_hash', '')
        user_wallet = data.get('wallet', '')
        
        if not tx_hash or not user_wallet:
            return jsonify({"error": "Missing tx_hash or wallet"}), 400

        full_story = user_sessions.get(user_wallet, {}).get("full_story", "")
        
        if not full_story:
            full_story = "Thank you for your tip! Here's your full magical story about adventure and wonder in distant lands."

        return jsonify({
            "reply": "🎉 Tip received! Full story unlocked!",
            "written": full_story,
            "explorer": f"https://testnet.arcscan.app/tx/{tx_hash}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({"message": "AI Story Teller API is running!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "Server is working!"})

# Vercel serverless handler
def handler(request, context):
    try:
        with app.app_context():
            return app(request, context)
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e), 'message': 'Server error'})
        }

# For local development
if __name__ == '__main__':
    app.run(debug=True)