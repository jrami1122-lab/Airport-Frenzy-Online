"""Airport Frenzy Online: websocket party-room and tournament server."""
import asyncio
import json
import os
import random
import re
import secrets
import time
from pathlib import Path
from aiohttp import web, WSMsgType

ROOT = Path(__file__).resolve().parent
GAMES = ("ramp", "bags", "cabin", "assist", "docs", "marshal")
COLORS = ("#4CD3FF", "#FFCF4A", "#FF6B72", "#A78BFA")
ROOMS = {}
SECONDS = max(30, int(os.environ.get("ROUND_SECONDS", "150")))


def safe_name(value):
    return (re.sub(r"[^\w -]", "", str(value or "Player"))[:20].strip() or "Player")


def view_player(p):
    return {key: p[key] for key in ("id", "name", "color", "pts", "wins", "score", "finished", "eliminated", "online", "tiebreakWins")}


def view_room(r):
    i = r["index"]
    games = r["games"]
    return {"type": "room", "code": r["code"], "host": r["host"], "stage": r["stage"], "mode": r["mode"],
            "game": games[i] if 0 <= i < len(games) else None, "games": games, "index": i,
            "players": [view_player(p) for p in r["players"]], "deadline": r["deadline"],
            "results": r["results"], "winner": r["winner"], "tiebreak": r["tiebreak"],
            "tiebreakRound": r["tiebreakRound"], "tiebreakPlayers": r["tiebreakPlayers"],
            "preferredGame": r["preferredGame"]}


async def send(ws, data):
    if ws is not None and not ws.closed:
        try:
            await ws.send_json(data)
        except (ConnectionError, RuntimeError):
            pass


async def broadcast(r):
    data = view_room(r)
    await asyncio.gather(*(send(p.get("ws"), data) for p in r["players"]))


def new_room():
    for _ in range(30):
        code = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(6))
        if code not in ROOMS:
            r = {"code": code, "host": None, "stage": "lobby", "players": [], "mode": "tournament",
                 "preferredGame": "ramp", "games": [], "index": -1, "deadline": 0, "timer": None,
                 "results": [], "winner": None, "tiebreak": False, "tiebreakRound": 0,
                 "tiebreakPlayers": [], "created": time.monotonic()}
            ROOMS[code] = r
            return r
    raise RuntimeError("No available room codes")


def eligible(r):
    return [p for p in r["players"] if not p["eliminated"] and (not r["tiebreak"] or p["id"] in r["tiebreakPlayers"])]


def cancel_timer(r):
    t = r.get("timer")
    if t and t is not asyncio.current_task():
        t.cancel()
    r["timer"] = None


async def round_timeout(r, index, deadline):
    try:
        await asyncio.sleep(max(0, deadline - time.time()))
        if r["stage"] == "round" and r["index"] == index and r["deadline"] == deadline:
            await finish_round(r)
    except asyncio.CancelledError:
        pass


async def begin_round(r, playoff=False):
    cancel_timer(r)
    if playoff:
        r["tiebreakRound"] += 1
        r["games"] = [random.choice(GAMES)]
        r["index"] = 0
    else:
        r["index"] += 1
    r["results"] = []
    r["stage"] = "round"
    r["deadline"] = time.time() + SECONDS
    for p in r["players"]:
        p["score"] = 0
        p["finished"] = False
    r["timer"] = asyncio.create_task(round_timeout(r, r["index"], r["deadline"]))
    await broadcast(r)


async def finish_round(r):
    if r["stage"] != "round":
        return
    cancel_timer(r)
    order = sorted(eligible(r), key=lambda p: (-p["score"], p["id"]))
    results = []
    for p in order:
        rank = 1 + sum(x["score"] > p["score"] for x in order)
        earned = max(0, 4-rank) if p["score"] > 0 else 0
        if not r["tiebreak"]:
            p["pts"] += earned
            if rank == 1 and p["score"] > 0:
                p["wins"] += 1
        results.append({"id": p["id"], "name": p["name"], "score": p["score"], "earned": earned, "rank": rank})
    r["results"] = results
    r["stage"] = "results"
    if r["tiebreak"]:
        if order and order[0]["score"] > 0 and (len(order) == 1 or order[0]["score"] > order[1]["score"]):
            order[0]["tiebreakWins"] += 1
        best = max((p["tiebreakWins"] for p in eligible(r)), default=0)
        leaders = [p for p in eligible(r) if p["tiebreakWins"] == best]
        if (best >= 2 and len(leaders) == 1) or (r["tiebreakRound"] >= 3 and len(leaders) == 1):
            r["stage"] = "finished"
            r["winner"] = leaders[0]["id"]
    else:
        if r["mode"] == "tournament" and r["index"] == 3:
            survivors = [p for p in eligible(r) if p["pts"] > 0]
            if survivors:
                for p in eligible(r):
                    if p["pts"] == 0:
                        p["eliminated"] = True
        if r["index"] + 1 >= len(r["games"]) or len(eligible(r)) == 1:
            players = sorted(eligible(r), key=lambda p: -p["pts"])
            if players:
                leaders = [p for p in players if p["pts"] == players[0]["pts"]]
                if len(leaders) == 1:
                    r["stage"] = "finished"
                    r["winner"] = leaders[0]["id"]
                else:
                    r["tiebreak"] = True
                    r["tiebreakPlayers"] = [p["id"] for p in leaders]
                    r["tiebreakRound"] = 0
                    r["stage"] = "tiebreak_ready"
    await broadcast(r)


async def dispatch(r, p, data):
    action = data.get("type")
    host = p["id"] == r["host"]
    if action == "configure" and host and r["stage"] == "lobby":
        mode = data.get("mode")
        game = data.get("game") or "ramp"
        if mode in ("single", "tournament") and game in GAMES:
            r["mode"] = mode
            r["preferredGame"] = game
    elif action == "start" and host and r["stage"] == "lobby" and len(r["players"]) >= 2:
        r["games"] = random.sample(GAMES, 6) if r["mode"] == "tournament" else [r["preferredGame"]]
        r["index"] = -1
        await begin_round(r)
        return
    elif action in ("score", "finish") and r["stage"] == "round" and p in eligible(r) and not p["finished"]:
        try:
            points = int(float(data.get("score", 0)))
        except (ValueError, TypeError, OverflowError):
            return
        if points < 0 or points > 10000000:
            return
        p["score"] = max(p["score"], points)
        if action == "finish":
            p["finished"] = True
            if all(x["finished"] or not x["online"] for x in eligible(r)):
                await finish_round(r)
                return
    elif action == "next" and host and r["stage"] in ("results", "tiebreak_ready"):
        await begin_round(r, playoff=r["tiebreak"])
        return
    elif action == "rematch" and host and r["stage"] == "finished":
        r.update(stage="lobby", games=[], index=-1, deadline=0, results=[], winner=None, tiebreak=False,
                 tiebreakRound=0, tiebreakPlayers=[])
        for x in r["players"]:
            x.update(pts=0, wins=0, score=0, finished=False, eliminated=False, tiebreakWins=0)
    elif action == "leave":
        if p in r["players"]:
            r["players"].remove(p)
        if r["host"] == p["id"] and r["players"]:
            r["host"] = r["players"][0]["id"]
        if not r["players"]:
            cancel_timer(r)
            ROOMS.pop(r["code"], None)
        else:
            await broadcast(r)
        return
    else:
        return
    await broadcast(r)


async def websocket(request):
    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=8192)
    await ws.prepare(request)
    room = me = None
    await send(ws, {"type": "welcome", "version": 1})
    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue
            try:
                data = json.loads(msg.data)
                if not isinstance(data, dict):
                    continue
            except (ValueError, TypeError):
                continue
            action = data.get("type")
            if action in ("create", "join") and me is None:
                if action == "create":
                    if len(ROOMS) >= 200:
                        await send(ws, {"type": "error", "message": "Too many active rooms"})
                        continue
                    room = new_room()
                else:
                    code = str(data.get("code", "")).strip().upper()
                    room = ROOMS.get(code)
                    if room is None:
                        await send(ws, {"type": "error", "message": "Room code not found"})
                        continue
                token = str(data.get("token") or "")
                existing = next((x for x in room["players"] if token and x["token"] == token), None)
                if existing:
                    old = existing.get("ws")
                    if old and not old.closed:
                        await old.close()
                    me = existing
                else:
                    if room["stage"] != "lobby" or len(room["players"]) >= 4:
                        await send(ws, {"type": "error", "message": "Room full or already started"})
                        continue
                    used = {x["color"] for x in room["players"]}
                    color = next(c for c in COLORS if c not in used)
                    me = {"id": secrets.token_hex(8), "token": secrets.token_urlsafe(32),
                          "name": safe_name(data.get("name") or f"Player {len(room['players'])+1}"),
                          "color": color, "pts": 0, "wins": 0, "score": 0, "finished": False,
                          "eliminated": False, "online": True, "tiebreakWins": 0, "ws": None}
                    room["players"].append(me)
                    if room["host"] is None:
                        room["host"] = me["id"]
                me["online"] = True
                me["ws"] = ws
                await send(ws, {"type": "identity", "id": me["id"], "token": me["token"]})
                await broadcast(room)
            elif me is not None and room is not None:
                await dispatch(room, me, data)
            else:
                await send(ws, {"type": "error", "message": "Create or join first"})
    finally:
        if me is not None and room is not None and me.get("ws") is ws:
            me["online"] = False
            me["ws"] = None
            if room["host"] == me["id"]:
                others = [x for x in room["players"] if x["online"]]
                if others:
                    room["host"] = others[0]["id"]
            await broadcast(room)
    return ws


async def health(request):
    return web.json_response({"ok": True, "rooms": len(ROOMS), "games": list(GAMES)})


async def index(request):
    return web.FileResponse(ROOT / "index.html", headers={"Cache-Control": "no-store"})


async def party_js(request):
    return web.FileResponse(ROOT / "online_party.js", headers={"Cache-Control": "no-store"})


async def reap(app):
    while True:
        await asyncio.sleep(600)
        for code, r in list(ROOMS.items()):
            if not any(x["online"] for x in r["players"]) and time.monotonic() - r["created"] > 3600:
                cancel_timer(r)
                del ROOMS[code]


async def on_start(app):
    app["reaper"] = asyncio.create_task(reap(app))


async def on_stop(app):
    app["reaper"].cancel()
    try:
        await app["reaper"]
    except asyncio.CancelledError:
        pass


app = web.Application(client_max_size=8192)
app.router.add_get("/", index)
app.router.add_get("/health", health)
app.router.add_get("/online_party.js", party_js)
app.router.add_get("/ws", websocket)
app.on_startup.append(on_start)
app.on_cleanup.append(on_stop)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
