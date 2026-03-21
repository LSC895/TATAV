# ⚔️ Tatav 1 — AI Commander Battle
### Local Edition — No API Keys, No Rate Limits, Runs on Your NVIDIA GPU

---

## 🚀 Quick Start (5 minutes)

### Step 1 — Install Ollama (one time only)
1. Go to: **https://ollama.com/download**
2. Download for Windows → install it
3. Open Command Prompt and run:
   ```
   ollama pull mistral
   ```
   This downloads the Mistral AI model (~4GB). Takes a few minutes.

### Step 2 — Install Python (if not already)
1. Go to: **https://python.org/downloads**
2. Download Python 3.11+ → install it
3. ✅ Check "Add Python to PATH" during install

### Step 3 — Run Tatav 1
1. Extract this folder anywhere on your PC
2. Double-click **START.bat**
3. Browser opens automatically → **http://localhost:8000**
4. Press **Start Battle** — done!

---

## 🎮 How to Play

| Button | What it does |
|--------|-------------|
| ▶ Start Battle | Begins the battle — both AIs start thinking |
| 💰 Loot | Drops a treasure chest on the map — AIs react |
| ⚔️ Weapon | Drops a weapon cache — tempts AIs to FIGHT |
| ⛈ Storm | Triggers storm — damages BOTH armies each round |
| ☀️ Clear | Clears the storm — restores morale |
| 🕊 Peace | Sends a peace envoy — may trigger NEGOTIATE |
| 💣 BOMB | Manually bombs a random commander |

**Timer:** Each AI has **10 seconds** to think. If time runs out → 💣 BOMB drops automatically!

**Decisions:** AI can choose FIGHT ⚔️ / DEFEND 🛡️ / NEGOTIATE 🤝 / RETREAT 🏃

**Win condition:** Troops reach 0 OR after 20 rounds — highest troops+loot wins.

---

## ⚙️ Change the AI Model

Open `server.py` and change line 20:

```python
MODEL = "mistral"        # fast, ~4GB
# MODEL = "llama3"       # smarter, ~8GB
# MODEL = "phi3"         # smallest, ~2GB (good for low RAM)
# MODEL = "gemma2"       # good balance
```

Then run: `ollama pull <model_name>`

---

## 🔧 Troubleshooting

**"Ollama not running" warning:**
→ Open Command Prompt → run `ollama serve`

**Game is slow:**
→ Use `phi3` model (faster, smaller)
→ Make sure your NVIDIA GPU drivers are up to date

**Port already in use:**
→ Change `--port 8000` to `--port 8001` in START.bat

**Browser doesn't open:**
→ Manually go to http://localhost:8000

---

## 🏗️ Project Structure

```
tatav1/
├── server.py          ← FastAPI backend + AI logic
├── requirements.txt   ← Python packages
├── START.bat          ← Windows launcher
├── README.md          ← This file
└── static/
    └── index.html     ← Frontend (auto-served)
```

---

## 🌱 What to build next (Tatav 2)

- More commanders (4-way battle)
- Different AI personalities (coward, traitor, berserker)
- Memory — AIs remember previous rounds
- Map events (earthquakes, floods, reinforcements)
- Multiplayer — user controls one army, AI controls the other
- Voice narration for each decision

---

Built with ❤️ using FastAPI + Ollama + Mistral
**Tatav** (तत्त्व) — the essence of intelligence
