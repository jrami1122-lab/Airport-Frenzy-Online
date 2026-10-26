"""Browser regression tests for true Simon Says Air Marshalling, plus original games."""
import asyncio, base64, re, math
from pathlib import Path
from playwright.async_api import async_playwright

PAGE=Path("index.html").read_text(encoding="utf-8")
assert "function bankCarts(p)" in PAGE
assert "p.carts.length<6" in PAGE
assert "SHIFT_SECONDS=150" in PAGE
assert "p.banked+p.carts.length*65" in PAGE
cab=re.search(r"const CABIN_SERVICE_HTML='([A-Za-z0-9+/=]+)'",PAGE)
assert cab and "MAX_ROUNDS=10" in base64.b64decode(cab.group(1)).decode("utf8")
assert "function armOptions(side)" in PAGE
assert "function resolveSubmission(taps)" in PAGE
assert "double tap for double signal" in PAGE
assert "CURRENT SIGNAL:" not in PAGE
assert "NO VALID SIGNAL · ADJUST BOTH WANDS" not in PAGE
print("PASS: Ramp Runner deposits/timer and ten-trip Cabin game retained; no automatic full-signal hint.",flush=True)

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
  try:
   page=await browser.new_page(viewport={"width":1366,"height":768})
   errs=[]
   page.on("pageerror",lambda e:errs.append(str(e)))
   await page.goto("http://127.0.0.1:10000",wait_until="domcontentloaded")
   await page.locator("#gameSelect").click()
   for btn in ("#startSolo","#startBagSolo","#startCabin","#startAssist","#startDocsSolo","#startMarshal"):
    assert await page.locator(btn).count()==1, "Missing minigame "+btn
   await page.locator("#startMarshal").click()
   frame=page.frame_locator("#airFrame")
   await page.wait_for_timeout(500)
   print("MARSHAL DEBUG",{"errors":errs,"iframe":(await frame.locator("body").inner_text())[:260],"hints":await frame.locator("#leftCheck").count(),"submithelp":await frame.locator("#submitHelp").count()},flush=True)
   await frame.locator("#leftCheck").wait_for(timeout=12000)
   assert await frame.locator("#signalHint").count()==0,"Old combined-position answer bubble remains"
   assert "(double tap for double signal)" == (await frame.locator("#submitHelp").inner_text()).strip()
   assert await frame.locator("#submit").is_visible()
   assert await frame.locator("#score").count()==1
   # Stage known prompts on localhost only; production keeps them hidden.
   async def setup(cmd):
    await frame.locator("body").evaluate("(el,id)=>window.__AF_MARSHAL_TEST.setup(id)",cmd)
    # Route keyboard events into the game iframe rather than the parent arcade.
    await frame.locator("#submit").focus()
   async def keys(*args):
    for key in args:await page.keyboard.press(key)
   async def submit():
    await frame.locator("#submit").click()
   async def lost():
    assert await frame.locator("#over").is_visible(),"Incorrect answer was not failed"
    assert "Incorrect signal" in await frame.locator("#summary").inner_text()
    assert "expected signal" not in (await frame.locator("#summary").inner_text()).lower()
   async def passed():
    assert await frame.locator("#step").inner_text()=="SEQUENCE CLEAR","Correct signal not accepted"

   await setup("cutengine")
   await keys("s","ArrowLeft")
   assert "CUT ENGINE" in await frame.locator("#leftCheck").inner_text()
   assert "CUT ENGINE" in await frame.locator("#rightCheck").inner_text()
   assert not await frame.locator("#over").is_visible()
   assert (await frame.locator("#message").inner_text())=="READY","UI revealed a correct match before submission"
   await submit(); await passed()
   assert "100" in await frame.locator("#score").inner_text()

   # Test every wand-position guide against the authoritative command list.
   actual=await frame.locator("body").evaluate("(el)=>window.__AF_MARSHAL_TEST.armMap()")
   for detail in actual.values():
    for name in detail["names"]:assert name in detail["label"],"Missing signal "+name+": "+detail["label"]
    for name in detail["doubles"]:assert name+" (DOUBLE)" in detail["label"],"Missing double mark: "+detail["label"]

   # Wrong submitted poses fail immediately (even if the current arms correspond
   # to another valid command).
   await setup("forward")
   await keys("s","ArrowLeft")
   await submit();await lost()
   await setup("forward")
   await keys("a","ArrowDown")
   await submit();await lost()
   print("PASS: every wand guide lists all possible commands without target confirmation; wrong poses fail.",flush=True)

   # A single STOP and a double EMERGENCY STOP share identical arm positions,
   # so the evaluation MUST use a timeout for single, two clicks for double.
   await setup("stop")
   await keys("w","ArrowUp")
   assert "NORMAL STOP" in await frame.locator("#leftCheck").inner_text()
   assert "EMERGENCY STOP (DOUBLE)" in await frame.locator("#leftCheck").inner_text()
   await submit()
   assert not await frame.locator("#over").is_visible()
   await page.wait_for_timeout(1010)
   await passed()
   await setup("estop")
   await keys("w","ArrowUp")
   await submit();await submit();await passed()
   await setup("estop")
   await keys("w","ArrowUp")
   await submit();await page.wait_for_timeout(1010);await lost()
   await setup("stop")
   await keys("w","ArrowUp")
   await submit();await submit();await lost()

   await setup("setbrakes")
   await keys("q","Enter")
   assert "SET BRAKES (DOUBLE)" in await frame.locator("#leftCheck").inner_text()
   assert "RELEASE BRAKES" in await frame.locator("#leftCheck").inner_text()
   await submit();await submit();await passed()
   await setup("releasebrakes")
   await keys("q","Enter")
   await submit();await page.wait_for_timeout(1010);await passed()
   await setup("startengine")
   await keys("s","ArrowUp","/")
   await submit();await passed()

   # Actual mouse dragging must still register Cut Engine; only the UI
   # correctness bubble was removed, not wand positioning or the tap target.
   await setup("cutengine")
   person=await frame.locator("#person").bounding_box()
   for side,angle,offset in (("l",85,90),("r",-145,168)):
    handle=frame.locator("#leftHandle" if side=="l" else "#rightHandle")
    box=await handle.bounding_box()
    assert box
    sx,sy=box["x"]+box["width"]/2,box["y"]+box["height"]/2
    tx=person["x"]+offset+112*math.cos(math.radians(angle))
    ty=person["y"]+104+112*math.sin(math.radians(angle))
    await page.mouse.move(sx,sy);await page.mouse.down()
    await page.mouse.move(tx,ty,steps=13);await page.mouse.up()
   assert not errs, "Browser errors: "+str(errs)
   await submit();await passed()
   print("PASS: correct/incorrect Simon Says, single/double stop & brakes, circular engine, real mouse drags.",flush=True)
  finally:
   await browser.close()

asyncio.run(main())
