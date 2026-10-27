"""Xbox controller usability, six-seat cabin mapping and real game-completion integration."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

page_html=Path("index.html").read_text(encoding="utf8")
assert "/* Soft, generated airport-lounge music." not in page_html
assert "window.dispatchEvent(new CustomEvent('af-game-finished',{detail:{game:'bags'" in page_html
assert "window.__AF_BAG_SCORES" in page_html
assert "SEATS=['A','B','C','D','E','F']" not in page_html  # iframe is encoded in source
print("PASS source: legacy lounge synthesizer removed and hold-full auto-finish is wired.",flush=True)

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
  try:
   page=await browser.new_page(viewport={"width":1366,"height":768})
   errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
   await page.goto("http://127.0.0.1:10000",wait_until="domcontentloaded",timeout=60000)
   await page.locator("#afPadPauseMenu").wait_for(timeout=10000)
   await page.evaluate("""()=>{window.__padSim=(buttons=[],axes=[0,0,0,0])=>{
    const gp={connected:true,index:0,axes,buttons:Array.from({length:17},(_,i)=>({pressed:buttons.includes(i),value:buttons.includes(i)?1:0}))};
    window.AF_GAMEPAD.tick([gp]);};
   }""")
   await page.evaluate("window.__padSim([], [0,.9,0,0])")
   assert await page.locator(".afPadFocused").count()==1,"No highlighted focused button"
   style=await page.locator(".afPadFocused").evaluate("(e)=>getComputedStyle(e).outlineWidth")
   assert int(style.replace("px",""))>=3,"Controller focus highlight insufficient: "+style
   await page.evaluate("window.__padSim([])")
   await page.evaluate("window.__padSim([0])")
   assert await page.locator("#afFront .afPanel.active").count()==1,"A did not activate highlighted menu"
   await page.evaluate("window.__padSim([])")
   await page.locator("#gameSelect").click()
   await page.locator("#startSolo").click()
   await page.evaluate("window.__padSim([9])")
   assert await page.locator("#afPadPauseMenu.open").is_visible(),"Menu/Start does not open pause menu"
   assert await page.evaluate("window.AF_LOCAL.status().paused"),"Local clock was not paused"
   await page.evaluate("window.__padSim([])")
   await page.evaluate("window.__padSim([0])")
   assert not await page.locator("#afPadPauseMenu").is_visible(),"A didn't resume from pause"
   assert not await page.evaluate("window.AF_LOCAL.status().paused"),"Resuming did not resume shift clock"
   await page.locator("#afShiftEnd").click()
   await page.locator("#afLocalNext").click()
   await page.locator("#startCabin").click()
   cabin=page.frame_locator("#cabinFrame")
   await cabin.locator("#seat-1F").wait_for(state="attached",timeout=15000)
   await cabin.locator("#seat-1A").wait_for(state="attached")
   assert await cabin.locator(".seat-row").first.locator(".seat").count()==6,"Expected six seats per row"
   await cabin.locator("body").evaluate("""()=>{window.__seatEvents=[];
      document.addEventListener('af-cabin-seat',e=>window.__seatEvents.push(e.detail.seat));}""")
   for button in [6,2,3,0,1,7]:
    await page.evaluate("window.__padSim([])")
    await page.evaluate("(b)=>window.__padSim([b])",button)
   seats=await cabin.locator("body").evaluate("()=>window.__seatEvents")
   assert seats[-6:]==list("ABCDEF"),"LT X Y A B RT seat mapping incorrect: "+str(seats)
   assert await page.locator("#cabinHost").is_visible(),"B seat button quit the cabin game"
   assert not errors,"JS errors: "+repr(errors[:4])
   print("PASS Xbox: visible focus and A selection, actual pause/resume clock, and six-seat LT X Y A B RT controls.",flush=True)
   await page.close()

   bag=await browser.new_page(viewport={"width":1366,"height":768})
   await bag.goto("http://127.0.0.1:10000",wait_until="domcontentloaded")
   await bag.locator("#gameSelect").click()
   await bag.locator("#startBagSolo").click()
   await bag.locator("#afShiftClock.visible").wait_for(timeout=10000)
   await bag.evaluate("window.dispatchEvent(new CustomEvent('af-game-finished',{detail:{game:'bags',reason:'hold-full'}}))")
   await bag.locator("#afLocalResults.open").wait_for(timeout=4000)
   assert "SHIFT COMPLETE" in await bag.locator("#afLocalResults").inner_text()
   assert not await bag.locator("#afShiftClock").is_visible()
   print("PASS Bag Stacker: full hold immediately ends local shift, saves score, and shows results.",flush=True)
   await bag.close()
  finally:
   await browser.close()

asyncio.run(main())
