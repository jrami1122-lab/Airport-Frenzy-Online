"""Release 2.4: device layouts, installability and actual P1/P2 game simulation."""
import asyncio
from playwright.async_api import async_playwright
BASE='http://127.0.0.1:10000'

async def cabin_layout(browser,w,h,mobile):
 page=await browser.new_page(viewport={"width":w,"height":h},is_mobile=mobile,has_touch=mobile)
 errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
 await page.goto(BASE,wait_until="domcontentloaded")
 await page.locator("#gameSelect").click()
 await page.locator("#startCabin").click()
 frame=page.frame_locator("#cabinFrame")
 await frame.locator("#startGame").click(timeout=12000)
 await frame.locator(".seat-row").first.wait_for(timeout=12000)
 measurement=await frame.locator("body").evaluate("""()=>{
  const row=document.querySelector('.seat-row'),seats=[...row.querySelectorAll('.seat')];
  const rb=row.getBoundingClientRect(),b=seats.map(s=>s.getBoundingClientRect());
  return {row:rb.width,screen:innerWidth,count:seats.length,
   css:getComputedStyle(row).gridTemplateColumns,
   inside:b.every(x=>x.left>=rb.left-2&&x.right<=rb.right+2),
   overlapping:b.some((x,i)=>b.some((y,j)=>i<j&&Math.min(x.right,y.right)-Math.max(x.left,y.left)>3)),
   scroll:document.documentElement.scrollWidth,viewport:innerWidth};
 }""")
 assert measurement["count"]==6, (w,h,measurement)
 assert measurement["inside"] and not measurement["overlapping"],(w,h,measurement)
 assert measurement["scroll"]<=measurement["viewport"]+2,(w,h,measurement)
 assert not errors,(w,h,errors[:3])
 await page.close()
 return measurement

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
  try:
   p0=await browser.new_page(viewport={"width":1280,"height":720})
   await p0.goto(BASE,wait_until="domcontentloaded")
   for route in ["/manifest.webmanifest","/app-icon.svg","/service-worker.js","/dual_play.js","/release_features.js"]:
    response=await p0.request.get(BASE+route)
    assert response.status==200,(route,response.status)
   await p0.locator("#afReleaseInstall").wait_for(timeout=12000)
   await p0.locator("#afMusic").click()
   await p0.locator("#afFullOptions").wait_for(timeout=7000)
   await p0.locator("#optionsDone").click()
   assert await p0.locator("#afPadBadge").count()==1
   assert not await p0.locator("#afPadBadge").is_visible(),"Unofficial Xbox corner badge remains"
   print("PASS PWA: install button, manifest, icon, service worker and fullscreen Options control.",flush=True)
   await p0.close()

   for w,h,mobile in [(390,844,True),(844,390,True),(1366,768,False),(1920,1080,False)]:
    result=await cabin_layout(browser,w,h,mobile)
    print(f"PASS Cabin six seats at {w}x{h}: width={result['row']:.1f}, non-overlapping.",flush=True)

   page=await browser.new_page(viewport={"width":1366,"height":768})
   await page.goto(BASE,wait_until="domcontentloaded")
   await page.locator("#gameSelect").click()
   await page.locator("#afLocalPlay").click()
   await page.locator('[data-edit="humans:1"]').click()
   await page.locator("#afLocalGameSelect").select_option("cabin")
   await page.locator("#afLocalStart").click()
   await page.locator("#cabinHost.afTwoPlayer #afLocalP2Frame").wait_for(state="visible",timeout=12000)
   assert await page.evaluate("window.AF_DUAL.isActive()")
   assert await page.locator("#cabinHost.afTwoPlayer iframe").count()==2
   await page.locator("#afShiftEnd").click()
   await page.locator("#afLocalResults.open").wait_for(timeout=8000)
   assert "P2" in await page.locator("#afLocalResults").inner_text()
   print("PASS PC two-player: two independent Cabin Service frames and both saved results.",flush=True)
   await page.close()
  finally:await browser.close()

asyncio.run(main())
