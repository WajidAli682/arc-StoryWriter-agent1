from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Simple in-memory storage
user_sessions = {}

print("✅ AI Story Teller Server Started!")

@app.route('/connect', methods=['POST'])
def connect():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "failed", "error": "No data"}), 400
            
        user_wallet = data.get('wallet', '').strip()
        
        # Basic wallet validation
        if user_wallet and len(user_wallet) > 10:
            user_sessions[user_wallet] = {"full_story": ""}
            return jsonify({
                "status": "connected", 
                "wallet": user_wallet,
                "message": "Wallet connected successfully!"
            })
        else:
            return jsonify({"status": "failed", "error": "Invalid wallet"}), 400
            
    except Exception as e:
        error_msg = f"Connect error: {str(e)}"
        print(error_msg)
        return jsonify({"status": "failed", "error": error_msg}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"reply": "No data received"}), 400
            
        user_message = data.get('message', '').strip()
        user_wallet = data.get('wallet', '')
        
        print(f"📖 Chat request: {user_message}")
        
        if not user_message:
            return jsonify({"reply": "Please enter a story topic!"})
        
        if not user_wallet:
            return jsonify({"reply": "Please connect wallet first!"})
        
        # Generate simple story
        story = f"✨ Once upon a time, there was a magical {user_message}. This story was created just for you! The full AI-powered version with audio will be available soon."
        teaser = story[:100] + "... 🎧 Tip $0.50 to unlock full story!"
        
        # Store story
        user_sessions[user_wallet] = {"full_story": story}
        
        return jsonify({
            "reply": "Story generated successfully!",
            "written": teaser,
            "canTip": True
        })
        
    except Exception as e:
        error_msg = f"Chat error: {str(e)}"
        print(error_msg)
        return jsonify({"reply": "Server error. Please try again."}), 500

@app.route('/tip', methods=['POST'])
def tip():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"reply": "No data"}), 400
            
        user_wallet = data.get('wallet', '')
        
        if not user_wallet:
            return jsonify({"reply": "Connect wallet first!"})
        
        # Test transaction data
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
            "reply": "Confirm transaction in MetaMask!",
            "tx": test_tx,
            "status": "sign_required"
        })
            
    except Exception as e:
        error_msg = f"Tip error: {str(e)}"
        print(error_msg)
        return jsonify({"reply": "Tip failed. Try again."}), 500

@app.route('/confirm_tx', methods=['POST'])
def confirm_tx():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400
            
        tx_hash = data.get('tx_hash', '')
        user_wallet = data.get('wallet', '')
        
        # Get stored story or create default
        story_data = user_sessions.get(user_wallet, {})
        full_story = story_data.get("full_story", "Thank you for your support! Here's your full magical adventure story.")
        
        return jsonify({
            "reply": "🎉 Payment confirmed! Full story unlocked!",
            "written": full_story,
            "explorer": f"https://testnet.arcscan.app/tx/{tx_hash}"
        })
        
    except Exception as e:
        error_msg = f"Confirm error: {str(e)}"
        print(error_msg)
        return jsonify({"error": "Confirmation failed"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Server is working!"})

# Vercel serverless handler - SIMPLE VERSION
def handler(request, context):
    try:
        # Convert Vercel request to Flask response
        with app.test_request_context(
            path=request['path'],
            method=request['method'],
            headers=request['headers'],
            json=request.get('body')
        ):
            response = app.full_dispatch_request()
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
    except Exception as e:
        print(f"Handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }

# Local development
if __name__ == '__main__':
    app.run(debug=True)