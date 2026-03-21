⚔️ Tatav 1 — AI Commander Battle

#तत्त्व (Tatav) — the essence of intelligence

A real-time multi-agent AI battle game where two AI commanders think, react, and make strategic decisions — running fully local, no API keys, no rate limits. 

I build this in one day with Ollma! 

🎮 Live Demo
https://github.com/user-attachments/assets/YOUR_SCREEN_RECORDING_HERE

Two AI commanders (Agni 🔴 and Vayu 🔵) fight on a live battle map.
You control the weather, drop loot, send peace offers, or just drop a bomb.
Each AI has 10 seconds to think — or face the 💣 BOMB.

🧠 What This Is
Tatav 1 is the demo prototype of a larger vision:

Building an AI that can perceive a game environment, reason about it, and act —
similar to Google DeepMind's SIMA, but built from scratch by a solo indie AI engineer.

This version uses Mistral via Ollama as the reasoning brain.
The next version (Tatav Brain) will use a custom-trained PyTorch model — no borrowed AI.

🏗️ Architecture
User Browser (HTML/JS)
      ↕ WebSocket
FastAPI Server (Python)
      ↕ HTTP
Ollama (Mistral 7B) — runs on your local GPU
Frontend — Pure HTML/CSS/JS, no framework
Backend — FastAPI + WebSocket for real-time communication
AI Brain — Mistral 7B via Ollama (local, free, unlimited)
Game Logic — Custom Python engine (state, combat, map, timer)

⚡ Quick Start
Requirements

Windows PC with NVIDIA GPU
Python 3.11+
Ollama

Setup
# 1. Pull the AI model (one time, ~4GB)
ollama pull mistral

# 2. Clone this repo
git clone https://github.com/YOUR_USERNAME/tatav1
cd tatav1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload

Then open http://localhost:8000 and press Start Battle.
Or just double-click START.bat on Windows.

🎮 Controls (button with effect on AI)
#1 💰 Drop Loot - Tempts both AIs — aggressive ones will FIGHT for it
#2 ⚔️ Drop Weapon - Boosts attack — changes risk calculation
#3 ⛈️ Storm - Damages both armies every round — forces defensive play
#4 ☀️ Clear Weather - Restores morale — may trigger aggression
#5 🕊️ Peace Offer - May trigger NEGOTIATE if morale is low
#6 💣 BOMB - Manual chaos — drop a bomb on a random commander

📊 AI Decision System
Each round, both AI commanders receive a prompt containing:

Their current stats (troops, morale, loot)
Enemy stats
Weather conditions
Active events (loot drops, peace offers)

They must respond with one of:
FIGHT ⚔️ / DEFEND 🛡️ / NEGOTIATE 🤝 / RETREAT 🏃
They have 10 seconds to decide. Miss the timer → 💣 automatic bomb.

#Challenge faces nd limitation 
#1 AI brian is Mistral (borrowed) - not our own 
#2 MIstral Intall isn Tuff
#3 2d grid map not a real 3d game environment 
#4 no presistent memory across rounds 
#5 Decisions are text based - no visual preception yet 
