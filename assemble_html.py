"""Restore the exact original Airport Frenzy HTML from ordered GitHub source parts."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
parts=sorted((ROOT/"game_source").glob("*.htmlpart"))
if len(parts)!=45:
    raise RuntimeError(f"Expected 45 artwork/gameplay chunks; got {len(parts)}")
html="".join(p.read_text(encoding="utf-8") for p in parts)
external='<script src="/online_party.js"></script>'
if external not in html or "<!doctype html>" not in html.lower():
    raise RuntimeError("Game reconstruction failed integrity checks")
if 'id="partyPlay"' not in html or 'id="startMarshal"' not in html:
    raise RuntimeError("Original home menu or Air Marshalling game is missing")
# Inline online UI at the end of the page: it cannot be skipped by a cached/missing
# /online_party.js request, while preserving all 45 original game source chunks.
script=(ROOT/"online_party.js").read_text(encoding="utf-8")
if not script.strip().startswith("(()=>") or 'window.__AF_ONLINE=' not in script:
    raise RuntimeError("Online Party UI did not pass its build guard")
# The massive original page has some later script tags swallowed by browser parsing.
# Install the lobby loader *inside the proven working front-menu bootstrap* instead.
front_anchor="document.body.append(front);q('#afGameMount').append(gameGrid);"
if html.count(front_anchor)!=1:
    raise RuntimeError("Original menu bootstrap missing")
boot=front_anchor+"""
const originalMarshal=document.querySelector('#startMarshal')?.closest('.gameChoice');
if(originalMarshal && !document.querySelector('#afGameMount #startMarshal')){
  document.querySelector('#afGameMount .arcadeGrid')?.append(originalMarshal);
}
const lobbyScript=document.createElement('script');
lobbyScript.src='/online_party.js?v=14';
lobbyScript.async=false;
document.body.append(lobbyScript);
"""
html=html.replace(front_anchor,boot,1)
html=html.replace(external,'<!-- online menu dynamically loaded by front bootstrap -->',1)
html=html.replace('<button id="partyPlay"><small>TOURNAMENT MODE</small>PARTY PLAY <em>›</em></button>',
    '<button id="partyPlay"><small>TOURNAMENT · GAME ROTATION</small>🏆 PARTY MODE <em>›</em></button>',1)
html=html.replace('<button id="gameSelect"><small>CHOOSE YOUR SHIFT</small>GAME SELECT <em>›</em></button>',
    '<button id="gameSelect"><small>CHOOSE ANY CHALLENGE</small>🎮 CASUAL MODE <em>›</em></button>'
    '<button id="afLobbyLaunch"><small>2–4 PEOPLE · INVITE WITH CODE OR LINK</small>🌐 START A LOBBY <em>›</em></button>',1)
html=html.replace('6 AIRPORT CHALLENGES · OFFLINE READY','6 GAMES · ONLINE ROOMS OR LOCAL PLAY',1)
html=html.replace("MOBILE FIXED v3","ONLINE CREWS v1.3",1)
required=['id="partyPlay"','id="gameSelect"','id="afLobbyLaunch"','id="startMarshal"',"lobbyScript.src='/online_party.js?v=14'"]
if any(needle not in html for needle in required):
    raise RuntimeError("Home mode / online game menu injection failed")
(ROOT/"index.html").write_text(html,encoding="utf-8")
print(f"Assembled Airport Frenzy Online v1.4 with {len(parts)} chunks, all six games, standalone online Party Play ({len(html):,} characters).")
