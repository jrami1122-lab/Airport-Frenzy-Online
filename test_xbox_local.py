"""Desktop/phone-sized Chrome tests for Xbox controller UI and local tournament flow."""
import asyncio
from playwright.async_api import async_playwright

BASE="http://127.0.0.1:10000"
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
  try:
   page=await browser.new_page(viewport={"width":1366,"height":768})
   errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
   await page.goto(BASE,wait_until="domcontentloaded")
   await page.locator("#gameSelect").click()
   await page.locator("#afLocalPlay").wait_for(timeout=15000)
   await page.locator("#afPadBadge").wait_for(timeout=15000)
   assert await page.evaluate("!!window.AF_GAMEPAD&&!!window.AF_LOCAL")
   assert await page.locator("#afGameJump").count()==0,"Duplicate top game shortcuts still present"
   assert await page.locator("#afGameMount .gameChoice").count()==6,"Expected six clean game cards"
   assert await page.locator("#afLocalPlay").is_visible()
   assert await page.locator("#startVersus").evaluate("(el)=>getComputedStyle(el).display")=="none"
   assert await page.locator("#startBagVersus").evaluate("(el)=>getComputedStyle(el).display")=="none"
   await page.locator("#afGames .afBack").click()
   await page.locator("#partyPlay").click()
   assert await page.locator("#afLocalHub").evaluate("(el)=>el.classList.contains('open')")
   await page.locator('[data-edit="cpus:1"]').click()
   await page.locator('[data-edit="cpus:1"]').click()
   assert await page.locator("#afHumanCount").inner_text()=="1"
   assert await page.locator("#afCpuCount").inner_text()=="3"
   await page.locator('[data-count="2"]').click()
   await page.locator("#afLocalStart").click()
   await page.locator("#afShiftClock.visible").wait_for(timeout=15000)
   await page.locator("#afShiftEnd").click()
   await page.locator("#afLocalNext").click()
   await page.locator("#afShiftClock.visible").wait_for(timeout=15000)
   await page.locator("#afShiftEnd").click()
   assert "EMPLOYEE OF THE MONTH" in await page.locator("#afLocalResults").inner_text()
   assert await page.evaluate("Array.isArray(window.AF_LOCAL.stats().trophies)")
   await page.locator("#afLocalNext").click()
   await page.locator("#gameSelect").click()
   await page.locator("#startBagSolo").click()
   await page.locator("#afShiftClock.visible").wait_for(timeout=12000)
   await page.locator("#afShiftEnd").click()
   assert "SHIFT COMPLETE" in await page.locator("#afLocalResults").inner_text()
   await page.locator("#afLocalNext").click()
   await page.locator("#afLocalPlay").click()
   assert await page.locator("#afLocalHub").evaluate("(el)=>el.classList.contains('open')")
   await page.locator('[data-edit="humans:1"]').click()
   assert await page.locator("#afHumanCount").inner_text()=="2"
   await page.locator("#afLocalGameSelect").select_option("bags")
   await page.locator("#afLocalStart").click()
   await page.locator("#bagGame").wait_for(state="visible",timeout=15000)
   assert await page.evaluate("typeof window.__AF_BAG_SCORES==='function'"),"Native local bag scores unavailable"
   await page.locator("#afShiftEnd").click()
   await page.locator("#afLocalResults.open").wait_for()
   assert "P2" in await page.locator("#afLocalResults").inner_text(),"Missing player two result"
   await page.locator("#afLocalNext").click()
   assert not errors,"Browser JS errors: "+repr(errors[:4])
   print("PASS desktop: six clean cards, hidden blue Versus buttons, customizable 1P+3AI tournament, Employee of Month, casual stats and native local Bag P2.",flush=True)
   await page.close()
   phone=await browser.new_page(viewport={"width":390,"height":844},is_mobile=True,has_touch=True)
   await phone.goto(BASE,wait_until="domcontentloaded")
   await phone.locator("#afLocalPlay").wait_for(state="attached",timeout=15000)
   assert not await phone.locator("#afLocalPlay").is_visible(),"Mobile must hide shared-device local multiplayer"
   await phone.locator("#partyPlay").click()
   await phone.locator('[data-edit="humans:1"]').click()
   assert await phone.locator("#afHumanCount").inner_text()=="1","Mobile should be 1 human maximum"
   print("PASS mobile: no local split-screen option; solo-versus-AI Party Mode retained.",flush=True)
   await phone.close()
  finally: await browser.close()
asyncio.run(main())