"""Game-specific validation with a real Chromium iframe and all six launch buttons."""
import asyncio,base64,re,math
from pathlib import Path
from playwright.async_api import async_playwright

PAGE=Path("index.html").read_text(encoding="utf-8")
assert "function bankCarts(p)" in PAGE
assert "p.carts.length<6" in PAGE
assert "Math.min(10,p.carts.length)" in PAGE
assert "const DEPOT={x:270,y:750,r:145},SHIFT_SECONDS=150" in PAGE
assert "p.banked+p.carts.length*65" in PAGE
assert "SERVICE TUNNEL" in PAGE or "SIDE-SERVICE TUNNEL" in PAGE
assert "function finishRampShift()" in PAGE
m=re.search(r"const CABIN_SERVICE_HTML='([A-Za-z0-9+/=]+)'", PAGE)
assert m, "Original encoded cabin game missing"
cabin=base64.b64decode(m.group(1)).decode("utf8")
assert "CAPACITY=12,MAX_ROUNDS=10" in cabin
assert "START 10-TRIP SHIFT" in cabin
assert "MAX_ROUNDS=20" not in cabin
assert "const poses={out:{l:-160,r:-20},inner:{l:-35,r:-145},up:{l:-90,r:-90},down:{l:85,r:95},front:{l:20,r:160}}" in PAGE
assert "function updateSignalHint()" in PAGE
assert "function availableSignals()" in PAGE
assert "NO VALID SIGNAL" in PAGE
print("PASS: shift timer, persistent cart banking, service tunnel, 10 cabin trips, and distinct marshal angles.", flush=True)

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
  try:
   page=await browser.new_page(viewport={"width":1366,"height":768})
   errs=[]
   page.on("pageerror",lambda e:errs.append(str(e)))
   await page.goto("http://127.0.0.1:10000",wait_until="domcontentloaded")
   await page.locator("#gameSelect").click()
   for button in ("#startSolo","#startBagSolo","#startCabin","#startAssist","#startDocsSolo","#startMarshal"):
    assert await page.locator(button).count()==1,"Missing game launch "+button
   await page.locator("#startMarshal").click()
   frame=page.frame_locator("#airFrame")
   await frame.locator("#signalHint").wait_for(timeout=12000)
   assert "CURRENT SIGNAL:" in await frame.locator("#signalHint").inner_text()
   # Keyboard poses should exactly match full two-wand action, not overlap.
   await frame.locator("#begin").click()
   await page.keyboard.press("s")
   await page.keyboard.press("ArrowLeft")
   hint=await frame.locator("#signalHint").inner_text()
   assert "CUT ENGINE" in hint, "Down+inward must register CUT ENGINE: "+hint
   # Drag the visible handles to the actual arm angles; test mouse gameplay,
   # not just keyboard shortcuts.
   person_box=await frame.locator("#person").bounding_box()
   assert person_box,"Marshal worker not visible"
   for side,angle,offset in (("l",85,90),("r",-145,168)):
    handle=frame.locator("#leftHandle" if side=="l" else "#rightHandle")
    handle_box=await handle.bounding_box()
    assert handle_box,"Missing mouse/touch handle "+side
    sx=handle_box["x"]+handle_box["width"]/2
    sy=handle_box["y"]+handle_box["height"]/2
    tx=person_box["x"]+offset+112*math.cos(math.radians(angle))
    ty=person_box["y"]+104+112*math.sin(math.radians(angle))
    await page.mouse.move(sx,sy)
    await page.mouse.down()
    await page.mouse.move(tx,ty,steps=13)
    await page.mouse.up()
   drag_hint=await frame.locator("#signalHint").inner_text()
   assert "CUT ENGINE" in drag_hint,"Mouse-dragged cut-engine pose is unrecognized: "+drag_hint

   await page.keyboard.press("w")
   await page.keyboard.press("ArrowUp")
   hint=await frame.locator("#signalHint").inner_text()
   assert "NORMAL STOP" in hint and "EMERGENCY STOP" in hint, "Overhead poses are mislabeled: "+hint
   await page.keyboard.press("q")
   await page.keyboard.press("Enter")
   hint=await frame.locator("#signalHint").inner_text()
   assert "SET BRAKES" in hint and "RELEASE BRAKES" in hint, "Forward poses are indistinguishable: "+hint
   await page.keyboard.press("a")
   await page.keyboard.press("ArrowDown")
   hint=await frame.locator("#signalHint").inner_text()
   assert "NO VALID SIGNAL" in hint, "Invalid pose was incorrectly recognized as a valid signal: "+hint
   assert await frame.locator("#score").count()==1
   assert not errs, "Page errors: "+str(errs[:3])
   print("PASS: Air Marshalling recognizes cut engine, stops, brakes, invalid combos; visible points HUD, no JS errors.",flush=True)
   await page.close()
  finally:await browser.close()

asyncio.run(main())
