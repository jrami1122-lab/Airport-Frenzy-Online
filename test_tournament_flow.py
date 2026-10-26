"""Full six-game tournament and two-round playoff use the server clock, not host Next."""
import asyncio
import server

server.SECONDS=0.50
server.COUNTDOWN=0.045
server.INTERMISSION=0.045

def new_player(i):
    return {"id": f"crew{i}", "token": f"token{i}", "name": f"Crew {i}",
            "color": server.COLORS[i], "pts":0, "wins":0, "score":0,
            "finished":False, "eliminated":False, "online":True,
            "tiebreakWins":0, "ws":None}

async def await_stage(room, stage, min_round=None):
    for i in range(400):
        if room["stage"]==stage and (min_round is None or room["roundId"]>min_round):
            return
        await asyncio.sleep(.005)
    raise AssertionError(f"Never entered stage {stage}; actual {room['stage']}, round {room['roundId']}")

async def play_tournament(tied=False):
    room=server.new_room()
    room["players"]=[new_player(i) for i in range(4)]
    room["host"]="crew0"
    try:
        await server.dispatch(room,room["players"][0],{"type":"start"})
        assert room["stage"]=="countdown" and room["index"]==0
        for game_num in range(6):
            await await_stage(room,"round")
            assert room["index"]==game_num
            assert len(room["games"])==6 and room["mode"]=="tournament"
            for i,p in enumerate(room["players"]):
                p["score"]=([120,120,60,10] if tied else [120,80,40,10])[i]
            await server.finish_round(room)
            if game_num==3: assert room["players"][3]["eliminated"],"Zero-point Crew 4 not eliminated after Game 4"
            if game_num<5:
                assert room["stage"]=="results",room["stage"]
                previous=room["roundId"]
                await await_stage(room,"countdown",previous)
                assert room["index"]==game_num+1,"Host had to trigger Next Game manually"
        if not tied:
            assert room["stage"]=="finished"
            assert room["winner"]=="crew0"
            print("PASS: six automatic tournament games, cumulative rankings, Game 4 elimination and Game 6 champion.")
        else:
            assert room["stage"]=="tiebreak_ready"
            for playoff_round in range(2):
                prior=room["roundId"]
                await await_stage(room,"countdown",prior)
                await await_stage(room,"round")
                assert room["tiebreakRound"]==playoff_round+1
                room["players"][0]["score"]=150
                room["players"][1]["score"]=70
                await server.finish_round(room)
            assert room["stage"]=="finished" and room["winner"]=="crew0"
            assert room["players"][0]["tiebreakWins"]==2
            print("PASS: automatically scheduled best-of-three tiebreaker resolves after two wins.")
    finally:
        server.cancel_timer(room)
        server.ROOMS.pop(room["code"],None)

async def main():
    await play_tournament(False)
    await play_tournament(True)

if __name__=="__main__":
    asyncio.run(main())
