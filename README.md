# 🎙️ AI Story Teller — Pay-to-Unlock Magical Stories (Arc USDC Tip)

## 🌟 Overview
**AI Story Teller** is a smart web app that allows users to generate short, emotional stories using artificial intelligence.  
It combines **AI creativity** with **decentralized payments**, enabling users to unlock full stories and realistic audio by tipping **$0.50 in USDC** directly on the **Arc Testnet**.

This project was built for the **lablab.ai Hackathon** with **Arc + USDC Integration**.

---

## 🚀 Live Demo
🔗 **Live App:** [https://arc-storywriter-agent1-production.up.railway.app/](https://arc-storywriter-agent1-production.up.railway.app/)  
💻 **GitHub Repo:** [https://github.com/WajidAli682/arc-StoryWriter-agent1](https://github.com/WajidAli682/arc-StoryWriter-agent1)

> For best experience:  
> Use **desktop browser with MetaMask** connected to **Arc Testnet**.

---

## 💡 Features
- ✨ Generate emotional stories from simple text prompts  
- 🎧 Listen to free teaser audio (powered by **ElevenLabs**)  
- 💰 Unlock full story + audio by tipping **$0.50 USDC**  
- 🔗 Blockchain integration using **Web3.py** and **Web3.js**  
- 🧠 AI-generated stories via **AIML API**  
- 🌐 Flask + Python backend hosted on **Railway**  

---

## ⚙️ How It Works
1. The frontend connects to **MetaMask** for wallet authentication and tipping.  
2. The backend (Flask) uses **Web3.py** to handle blockchain transactions on Arc.  
3. Once payment is confirmed, the app:
   - Calls **AIML API** for story generation  
   - Uses **ElevenLabs API** for realistic text-to-speech  
   - Returns the full story and audio to the user instantly  

---

## 🧩 Technologies Used
| Category | Tools |
|-----------|--------|
| **Frontend** | HTML, JavaScript, Web3.js |
| **Backend** | Flask, Python, Web3.py |
| **AI & Speech** | AIML API, ElevenLabs |
| **Blockchain** | Arc Testnet (USDC tip system) |
| **Hosting** | Railway |
| **Version Control** | GitHub |

---

## 🧠 Business Model & Future Plans
AI Story Teller demonstrates a **sustainable business model** for small creators.  
Users can **pay micro-tips** to unlock content — allowing creators to **earn directly** from AI stories.

### Future Features
- 🌍 Multi-language story support  
- 🧑‍💻 Author dashboards  
- 🎙️ Premium AI voices  
- 🔗 Arc Mainnet integration  

---

## 🛠️ Installation (For Local Testing)
```bash
# Clone the repository
git clone https://github.com/WajidAli682/arc-StoryWriter-agent1

# Navigate to project directory
cd arc-StoryWriter-agent1

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py


The app will run locally at http://127.0.0.1:5000/ may be other host on your case


🔒 Environment Variables

Create a .env file in your root directory with:

ELEVENLABS_API_KEY=your_api_key_here
AIML_API_KEY=your_api_key_here
