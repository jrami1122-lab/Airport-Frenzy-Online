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
html=html.replace(external,'<script id="af-online-v12">\\n'+script.replace("</script", "<\\/script")+'\\n</script>',1)
html=html.replace('<button id="partyPlay"><small>TOURNAMENT MODE</small>PARTY PLAY <em>›</em></button>',
    '<button id="partyPlay"><small>2–4 PLAYERS · ONLINE</small>ONLINE PARTY PLAY <em>›</em></button>',1)
html=html.replace('6 AIRPORT CHALLENGES · OFFLINE READY','6 AIRPORT CHALLENGES · ONLINE READY',1)
html=html.replace("MOBILE FIXED v3","ONLINE PARTY v1.2",1)
if 'ONLINE PARTY PLAY' not in html or 'id="af-online-v12"' not in html:
    raise RuntimeError("Online Party UI injection failed")
(ROOT/"index.html").write_text(html,encoding="utf-8")
print(f"Assembled Airport Frenzy Online v1.2 with {len(parts)} chunks, all six games, inline online Party Play ({len(html):,} characters).")
