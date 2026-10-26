"""Restore the exact original Airport Frenzy HTML from ordered GitHub source parts."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
parts=sorted((ROOT/"game_source").glob("*.htmlpart"))
if len(parts)!=45:
    raise RuntimeError(f"Expected 45 artwork/gameplay chunks; got {len(parts)}")
html="".join(p.read_text(encoding="utf-8") for p in parts)
if '<script src="/online_party.js"></script>' not in html or "<!doctype html>" not in html.lower():
    raise RuntimeError("Game reconstruction failed integrity checks")
(ROOT/"index.html").write_text(html,encoding="utf-8")
print(f"Assembled Airport Frenzy with {len(parts)} source chunks and {len(html):,} characters.")
