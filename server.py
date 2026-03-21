"""
Tatav 1 — AI Commander Battle
Local backend using Ollama (free, no API keys, runs on your NVIDIA GPU)
"""

import json
import asyncio
import random
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Tatav 1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# ── Ollama config ─────────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"       # fast & small — changes to llama3 or phi3 also work
THINK_TIMEOUT = 10      # seconds before bomb drops

# ── Game state (per connection) ───────────────────────────────
def fresh_state():
    return {
        "round": 0,
        "weather": "clear",
        "active": False,
        "pending_event": "",
        "red":  {"troops": 100, "morale": 80, "loot": 30},
        "blue": {"troops": 100, "morale": 80, "loot": 30},
        "grid": make_grid(),
    }

def make_grid():
    # 15 cols x 10 rows: 1=red, 2=blue, 0=neutral
    return [[1 if c < 5 else (2 if c > 9 else 0) for c in range(15)] for _ in range(10)]

# ── Ollama call ───────────────────────────────────────────────
async def ask_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.9,
            "num_predict": 120,
            "stop": ["\n\n", "```"]
        }
    }
    async with httpx.AsyncClient(timeout=12.0) as client:
        r = await client.post(OLLAMA_URL, json=payload)
        r.raise_for_status()
        return r.json().get("response", "")

def build_prompt(side: str, state: dict) -> str:
    enemy = "blue" if side == "red" else "red"
    s, e = state[side], state[enemy]
    name = "Commander Agni (Red, aggressive)" if side == "red" else "Commander Vayu (Blue, strategic)"
    ev = f"\nEVENT: {state['pending_event']}" if state['pending_event'] else ""
    return f"""You are {name} in a war game. Round {state['round']}.
My: Troops={s['troops']} Morale={s['morale']} Loot={s['loot']}
Enemy: Troops={e['troops']} Morale={e['morale']} Loot={e['loot']}
Weather:{state['weather']}{ev}

Reply ONLY valid JSON, no extra text:
{{"d":"FIGHT","r":"short reason max 10 words","tc":-5,"mc":3,"lg":8}}
d=FIGHT|DEFEND|NEGOTIATE|RETREAT tc=troops_change mc=morale_change lg=loot_gain"""

def parse_decision(raw: str) -> dict:
    try:
        clean = raw.strip()
        # Find JSON object in response
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start >= 0 and end > start:
            j = json.loads(clean[start:end])
            return {
                "decision": j.get("d", "DEFEND"),
                "reason": j.get("r", "Holding position."),
                "tc": int(j.get("tc", 0)),
                "mc": int(j.get("mc", 0)),
                "lg": int(j.get("lg", 0)),
            }
    except Exception:
        pass
    # Fallback — try to detect decision word in raw text
    for dec in ["FIGHT", "DEFEND", "NEGOTIATE", "RETREAT"]:
        if dec in raw.upper():
            return {"decision": dec, "reason": "Instinct.", "tc": 0, "mc": 0, "lg": 0}
    return {"decision": "DEFEND", "reason": "Playing it safe.", "tc": 0, "mc": 0, "lg": 0}

# ── Apply decision to state ───────────────────────────────────
def apply_decision(state: dict, side: str, dec: dict, enemy_dec: str | None):
    s = state[side]
    o = state["blue" if side == "red" else "red"]

    s["troops"] = clamp(s["troops"] + dec["tc"])
    s["morale"]  = clamp(s["morale"]  + dec["mc"])
    s["loot"]    = min(100, max(0, s["loot"] + dec["lg"]))

    if state["weather"] == "storm":
        s["troops"] = clamp(s["troops"] - 4)
        s["morale"]  = clamp(s["morale"]  - 7)

    combat_log = []
    if dec["decision"] == "FIGHT":
        dmg = random.randint(6, 16)
        o["troops"] = clamp(o["troops"] - dmg)
        o["morale"]  = clamp(o["morale"]  - 6)
        combat_log.append(f"💥 {'Agni' if side == 'red' else 'Vayu'} attacks! Enemy -{dmg} troops")

    if dec["decision"] == "RETREAT":
        s["troops"] = clamp(s["troops"] - 4)
        s["morale"]  = clamp(s["morale"]  - 12)

    if dec["decision"] == "NEGOTIATE" and enemy_dec == "NEGOTIATE":
        s["morale"] = min(100, s["morale"] + 15)
        combat_log.append("🤝 Both negotiating — morale +15 each")

    return combat_log

def bomb_side(state: dict, side: str, reason: str) -> str:
    s = state[side]
    s["troops"] = clamp(s["troops"] - 30)
    s["morale"]  = clamp(s["morale"]  - 25)
    s["loot"]    = max(0, s["loot"] - 20)
    name = "Agni" if side == "red" else "Vayu"
    return f"💣 BOOM! {name} BOMBED! -30 troops -25 morale -20 loot. ({reason})"

def push_front(grid, side: str):
    for r in range(10):
        if grid[r][7] == 0 and random.random() < 0.35:
            grid[r][7] = 1 if side == "red" else 2

def clear_items(grid):
    for r in range(10):
        for c in range(15):
            if grid[r][c] in (3, 4):
                grid[r][c] = 0

def clamp(v):
    return max(0, min(100, v))

def check_win(state: dict) -> str | None:
    if state["red"]["troops"] <= 0:
        return "blue"
    if state["blue"]["troops"] <= 0:
        return "red"
    if state["round"] >= 20:
        rs = state["red"]["troops"] + state["red"]["loot"]
        bs = state["blue"]["troops"] + state["blue"]["loot"]
        return "red" if rs > bs else "blue"
    return None

# ── WebSocket game loop ───────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    state = fresh_state()

    async def send(data: dict):
        await ws.send_json(data)

    async def send_log(msg: str, log_type: str = "system"):
        await send({"type": "log", "msg": msg, "log_type": log_type})

    async def send_state():
        await send({
            "type": "state",
            "round": state["round"],
            "weather": state["weather"],
            "red":  state["red"],
            "blue": state["blue"],
            "grid": state["grid"],
        })

    try:
        await send_log("🔌 Connected to Tatav 1 server! Ollama is ready. Press Start Battle.")

        while True:
            msg = await ws.receive_json()
            action = msg.get("action")

            # ── Start ──
            if action == "start":
                state["active"] = True
                await send_log("⚔️ BATTLE BEGINS! Commanders have 10 seconds to think — or face the 💣 BOMB!", "system")
                asyncio.create_task(run_battle_loop(ws, state, send, send_log, send_state))

            # ── Reset ──
            elif action == "reset":
                state.update(fresh_state())
                await send({"type": "reset"})
                await send_state()
                await send_log("↺ Game reset. Press Start Battle!", "system")

            # ── Drop loot ──
            elif action == "drop_loot":
                r = random.randint(1, 8)
                state["grid"][r][7] = 3
                state["red"]["loot"]  = min(100, state["red"]["loot"]  + 10)
                state["blue"]["loot"] = min(100, state["blue"]["loot"] + 10)
                state["pending_event"] = "A treasure chest appeared! Fight to claim it for +25 loot bonus."
                await send_state()
                await send_log("💰 Loot chest dropped on the battlefield!", "event")

            # ── Drop weapon ──
            elif action == "drop_weapon":
                r = random.randint(1, 8)
                state["grid"][r][7] = 4
                state["pending_event"] = "Weapon cache spotted! FIGHT this round for +20 attack power."
                await send_state()
                await send_log("⚔️ Weapon cache dropped! Both commanders notice...", "event")

            # ── Weather ──
            elif action == "weather_storm":
                state["weather"] = "storm"
                state["pending_event"] = "Brutal storm! -4 troops and -7 morale per round."
                await send_state()
                await send_log("⛈️ STORM unleashed! Both armies suffer each round.", "event")

            elif action == "weather_clear":
                state["weather"] = "clear"
                state["red"]["morale"]  = min(100, state["red"]["morale"]  + 10)
                state["blue"]["morale"] = min(100, state["blue"]["morale"] + 10)
                state["pending_event"] = "Storm cleared. Morale restored."
                await send_state()
                await send_log("☀️ Weather cleared! Both armies recover morale +10.", "event")

            # ── Peace ──
            elif action == "peace":
                state["pending_event"] = "Neutral envoy offers peace. NEGOTIATE gets +15 morale bonus."
                await send_log("🕊️ Peace offer sent! Will they take it?", "event")

            # ── Manual bomb ──
            elif action == "manual_bomb":
                side = random.choice(["red", "blue"])
                msg_txt = bomb_side(state, side, "Manual bomb by player!")
                await send_state()
                await send_log(msg_txt, "bomb")
                await send({"type": "bomb", "side": side})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await send_log(f"⚠️ Server error: {e}", "system")
        except Exception:
            pass


async def run_battle_loop(ws, state, send, send_log, send_state):
    """Main battle loop — runs each round with timeout protection."""
    while state.get("active"):
        state["round"] += 1
        await send({"type": "round_start", "round": state["round"]})
        await send_log(f"--- Round {state['round']} ---", "system")

        # Signal thinking start + start timers
        await send({"type": "thinking", "sides": ["red", "blue"]})

        # Race both AI calls against timeout
        red_dec, blue_dec = None, None
        red_bombed, blue_bombed = False, False

        red_task  = asyncio.create_task(ask_ollama(build_prompt("red",  state)))
        blue_task = asyncio.create_task(ask_ollama(build_prompt("blue", state)))

        # Wait with timeout
        done, pending = await asyncio.wait(
            [red_task, blue_task],
            timeout=THINK_TIMEOUT
        )

        # Cancel anything still running
        for t in pending:
            t.cancel()

        # Process red
        if red_task in done and not red_task.cancelled():
            try:
                raw = red_task.result()
                red_dec = parse_decision(raw)
            except Exception as e:
                msg = bomb_side(state, "red", f"AI error: {e}")
                red_bombed = True
                await send_log(msg, "bomb")
                await send({"type": "bomb", "side": "red"})
        else:
            msg = bomb_side(state, "red", "Timed out!")
            red_bombed = True
            await send_log(msg, "bomb")
            await send({"type": "bomb", "side": "red"})

        # Process blue
        if blue_task in done and not blue_task.cancelled():
            try:
                raw = blue_task.result()
                blue_dec = parse_decision(raw)
            except Exception as e:
                msg = bomb_side(state, "blue", f"AI error: {e}")
                blue_bombed = True
                await send_log(msg, "bomb")
                await send({"type": "bomb", "side": "blue"})
        else:
            msg = bomb_side(state, "blue", "Timed out!")
            blue_bombed = True
            await send_log(msg, "bomb")
            await send({"type": "bomb", "side": "blue"})

        # Clear pending event
        state["pending_event"] = ""

        # Apply decisions
        all_logs = []
        if red_dec and not red_bombed:
            logs = apply_decision(state, "red",  red_dec,  blue_dec["decision"] if blue_dec else None)
            all_logs += logs
        if blue_dec and not blue_bombed:
            logs = apply_decision(state, "blue", blue_dec, red_dec["decision"]  if red_dec  else None)
            all_logs += logs

        # Update map
        if red_dec and red_dec["decision"]  == "FIGHT": push_front(state["grid"], "red")
        if blue_dec and blue_dec["decision"] == "FIGHT": push_front(state["grid"], "blue")
        clear_items(state["grid"])

        # Send results
        await send({
            "type": "decisions",
            "red":  {"dec": red_dec,  "bombed": red_bombed},
            "blue": {"dec": blue_dec, "bombed": blue_bombed},
        })

        for log_msg in all_logs:
            await send_log(log_msg, "event")

        if red_dec:
            await send_log(f"Agni → {red_dec['decision']} — {red_dec['reason']}", "red")
        if blue_dec:
            await send_log(f"Vayu → {blue_dec['decision']} — {blue_dec['reason']}", "blue")

        await send_state()

        # Check win
        winner = check_win(state)
        if winner:
            state["active"] = False
            await send({"type": "winner", "side": winner, "round": state["round"]})
            return

        # Pause between rounds
        await asyncio.sleep(3.5)


# ── Health check ──────────────────────────────────────────────
@app.get("/health")
async def health():
    # Check if Ollama is running
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get("http://localhost:11434/api/tags")
            models = [m["name"] for m in r.json().get("models", [])]
            return {"status": "ok", "ollama": True, "models": models}
    except Exception:
        return {"status": "ok", "ollama": False, "models": []}
