"""Four-device room test: joins, colors, host mode, gameplay and live views."""
import asyncio
import server
server.COUNTDOWN=3
from aiohttp.test_utils import TestServer, TestClient

async def until(ws, typ, limit=5):
    for _ in range(12):
        message=await asyncio.wait_for(ws.receive_json(),limit)
        if message.get("type")==typ:
            return message
    raise AssertionError(f"Missing {typ}")

async def main():
    async with TestServer(server.app) as test_server:
        async with TestClient(test_server) as client:
            sockets=[]
            try:
                for i in range(4):
                    ws=await client.ws_connect("/ws")
                    sockets.append(ws)
                    await until(ws,"welcome")
                    await ws.send_json({"type":"create" if i==0 else "join",
                                        "code":room_code if i else None,
                                        "name":f"Crew {i+1}"})
                    ident=await until(ws,"identity")
                    assert ident["id"] and ident["token"]
                    room=await until(ws,"room")
                    if i==0:room_code=room["code"]
                    assert len(room["players"])==i+1
                    assert len(set(p["color"] for p in room["players"]))==i+1
                extra=await client.ws_connect("/ws")
                await until(extra,"welcome")
                await extra.send_json({"type":"join","code":room_code,"name":"Fifth"})
                error=await until(extra,"error")
                assert "full" in error["message"].lower()
                await extra.close()
                # Drain stale lobby broadcasts from earlier joins.
                await sockets[0].send_json({"type":"configure","mode":"single","game":"bags"})
                configured=await until(sockets[3],"room")
                while configured["mode"]!="single":
                    configured=await until(sockets[3],"room")
                await sockets[0].send_json({"type":"start"})
                started=await until(sockets[3],"room")
                assert started["stage"]=="countdown" and started["game"]=="bags"
                assert 0<started["startAt"]<started["deadline"]
                for k in range(3):
                    notice=await until(sockets[k],"room")
                    while notice["stage"]!="countdown":notice=await until(sockets[k],"room")
                    assert notice["startAt"]==started["startAt"] and notice["roundId"]==started["roundId"]
                # Score sent before kickoff is ignored: no early advantage.
                await sockets[0].send_json({"type":"score","score":500})
                live=await until(sockets[3],"room")
                assert live["stage"]=="round" and live["startAt"]==started["startAt"]
                await sockets[0].send_json({"type":"score","score":220})
                await sockets[0].send_json({"type":"preview","image":"data:image/jpeg;base64,AAAA"})
                frame=await until(sockets[3],"preview")
                assert frame["id"]==started["host"] and frame["image"].startswith("data:image/jpeg")
                print("PASS: four unique colors, shared countdown for four clients, early-score lockout, live Bag Stacker scoring and streamed preview.")
            finally:
                for ws in sockets:
                    await ws.close()
if __name__=="__main__":
    asyncio.run(main())
