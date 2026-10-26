# Airport Frenzy — Scoring, pacing and QA review

Updated: October 26, 2026. This review is for the six original browser minigames and online tournaments. Keep game visuals, local games, and shared-room controls intact.

## Shared tournament rules
- All participating devices receive the same server-authoritative countdown and matching minigame.
- A live round has a shared 150-second server limit. Player scores are current values, **not their historical peak** before penalties; banked gameplay progress remains banked.
- The leaderboard compares results **within each game**, awarding 3 / 2 / 1 / 0 tournament points by placement to positive scorers. Therefore fundamentally different raw score scales do not advantage one minigame over another.
- Six games rotate; a player still at zero tournament points after Game 4 is eliminated. Game 6 decides the highest cumulative tournament score, with a best-of-three tiebreaker for tied leaders. The server advances rounds automatically.

| Game | What the game rewards | Timing / fairness | Status |
| --- | --- | --- | --- |
| **Ramp Runner** | **150 points per deposited cart** with a +200 bonus for a 10-cart delivery; **65 provisional points** for each attached undeposited cart; +60 for repairs, modest lost-cart/life penalties. The deposited value persists after crashes. | **2:30 shift**; obvious marked **6–10 cart depot** and bilateral **service tunnels**. Top speed capped at tier 5. Avoid the old high-score wipeout after one collision. | Changes implemented and build-tested; complete actual tug navigation still needs hands-on review. |
| **Bag Stacker** | Actual placements, based on bag area / load and placement position. | Multiplayer uses solo control on each device; split-screen mode disabled while in an online crew. Score compared by round *rank*, not against other game scales. | Existing physics preserved. Two-browser launch, game canvas and live opponent PiP verified. |
| **Flight Attendant** | Correct passenger service plus request-response bonuses; missed customers incur a 500-point penalty per loss. | Reduced from **20 to 10 trips**. HUD now shows **net points after passenger losses**, including during a shared-room round. | Source and rules verified; full 10-trip visual test still needed. |
| **Terminal Assist** | Completing passenger transport, with higher scores for prompt delivery. | Original 120-second clock can earn extra time for successful assistance; online session ends on its own common 150-second clock. The shared tournament compares rank, avoiding scale bias. | Original movement / destination physics left intact; launch and scoring paths reviewed. |
| **Document Control** | +150 for verified evidence, +100 for correct decisions, +70 for correct but unverified resolutions; −30 for wrong decisions. | Single-player 'Endless Shift' ends at the first incorrect decision. Online room reports the actual nonnegative live score and uses the shared game time limit. | Existing case evidence and decision logic preserved; full evidence-variation test still needed. |
| **Air Marshalling** | 100 points per correct signal, +10 per round (up to 200); points remain earned if memory fails. | Every direction is geometrically distinct; a combined left-and-right readout spells out the recognized complete command. Invalid combinations don't cost an attempt. Double-tap timeout shows guidance instead of abruptly ending a turn. | Automated browser checks verify Cut Engine, both Stops, Set/Release Brakes, invalid positions and visible score. |

## Current known limits
- The online contest is **synchronized individual gameplay**: each device has its own local game simulation. Opponent previews are low-resolution game-only snapshots where the active canvas is available; this is not four-player shared-world physics.
- Browser smoke tests validate menu visibility, six game launches, Bag Stacker on two simultaneous browsers, and Marshalling command recognition. Real-person playthroughs of all six complete games, multiple mobile devices and gameplay balance under different player skill levels remain necessary.
- Scores are reported by client devices. An authoritative anti-cheat simulation for every minigame would be a separate undertaking.
