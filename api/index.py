from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Simple storage
stories = {}

@app.route('/connect', methods=['POST'])
def connect():
    try:
        data = request.get_json()
        wallet = data.get('wallet', '').strip()
        
        if wallet and len(wallet) > 10:
            stories[wallet] = {"story": ""}
            return jsonify({
                "status": "connected", 
                "wallet": wallet
            })
        return jsonify({"status": "failed"}), 400
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        wallet = data.get('wallet', '')
        
        if not message:
            return jsonify({"reply": "Please enter a story topic!"})
        
        if not wallet:
            return jsonify({"reply": "Please connect wallet first!"})
        
        # Create simple story
        story = f"✨ Once upon a time, there was a magical {message}. This is your AI-generated story teaser. The full story with audio narration will be available after tipping!"
        teaser = story[:120] + "... 🎧 Tip $0.50 to unlock full story!"
        
        stories[wallet] = {"story": story}
        
        return jsonify({
            "reply": "Story teaser ready!",
            "written": teaser,
            "canTip": True
        })
        
    except Exception as e:
        return jsonify({"reply": "Server error"}), 500

@app.route('/tip', methods=['POST'])
def tip():
    try:
        data = request.get_json()
        wallet = data.get('wallet', '')
        
        if not wallet:
            return jsonify({"reply": "Connect wallet first!"})
        
        # Test transaction
        tx_data = {
            "from": wallet,
            "to": "0x2de592b3951807dfb72931596d11fe93b753881e",
            "value": "0x0",
            "data": "0x",
            "chainId": "0x4CFA2",
            "gas": "0x186A0",
            "gasPrice": "0x0",
            "nonce": "0x0"
        }
        
        return jsonify({
            "reply": "Confirm in MetaMask!",
            "tx": tx_data,
            "status": "sign_required"
        })
            
    except Exception as e:
        return jsonify({"reply": "Tip error"}), 500

@app.route('/confirm_tx', methods=['POST'])
def confirm_tx():
    try:
        data = request.get_json()
        tx_hash = data.get('tx_hash', '')
        wallet = data.get('wallet', '')
        
        story = stories.get(wallet, {}).get("story", "Full magical story unlocked! Thank you for your support.")
        
        return jsonify({
            "reply": "Payment confirmed!",
            "written": story,
            "explorer": f"https://testnet.arcscan.app/tx/{tx_hash}"
        })
        
    except Exception as e:
        return jsonify({"error": "Confirmation failed"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

# Vercel handler
def handler(event, context):
    try:
        from flask import Request, Response
        import json as json_module
        
        # Convert Vercel event to Flask request
        with app.request_context(
            path=event['path'],
            method=event['httpMethod'],
            headers=event.get('headers', {}),
            json=event.get('body') if event.get('body') else None
        ):
            response = app.full_dispatch_request()
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Server error'})
        }

if __name__ == '__main__':
    app.run()