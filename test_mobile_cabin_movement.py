"""Mobile Cabin Service: touch UP and DOWN must visually move the aisle in portrait and landscape."""
import asyncio,math
from playwright.async_api import async_playwright

BASE="http://127.0.0.1:10000"

async def scene(browser,width,height):
    page=await browser.new_page(viewport={"width":width,"height":height},is_mobile=True,has_touch=True)
    errors=[];page.on("pageerror",lambda error:errors.append(str(error)))
    await page.goto(BASE,wait_until="domcontentloaded",timeout=30000)
    await page.locator("#gameSelect").click()
    await page.locator("#startCabin").click()
    frame=page.frame_locator("#cabinFrame")
    await frame.locator("#startGame").tap(timeout=10000)
    await frame.locator("#upBtn").wait_for(state="visible")
    assert await frame.locator("#upBtn").is_enabled(), "UP must start enabled"
    async def measure():
      return await frame.locator("#track").evaluate("""node=>{
        const height=document.querySelector('.seat-row').getBoundingClientRect().height;
        const value=node.style.transform, matrix=getComputedStyle(node).transform;
        const x=matrix==='none'?0:parseFloat(matrix.match(/matrix(?:3d)?\\((.*)\\)/)?.[1].split(',')[5]||'NaN');
        return {height,transform:value,matrix,x,
          row:document.querySelector('#positionText').textContent,
          upEnabled:!document.querySelector('#upBtn').disabled,
          downEnabled:!document.querySelector('#downBtn').disabled};
      }""")
    start=await measure()
    assert start["row"]=="ROW 15" and start["height"]>40 and math.isfinite(start["x"]), start
    assert "NaN" not in start["transform"], start
    for row in [14,13]:
      await frame.locator("#upBtn").tap(timeout=6000)
      await page.wait_for_timeout(465)
      state=await measure()
      assert state["row"]==f"ROW {row}", (width,height,state)
      assert state["x"]>start["x"]+30, (width,height,start,state)
      assert "NaN" not in state["transform"], state
      start=state
    print(f"PASS {width}x{height}: mobile touch UP visibly advances aisle to row 13.",flush=True)

    # Finish the walk to the galley and test the complete reverse movement.
    for _ in range(13):
      await frame.locator("#upBtn").tap(timeout=6000)
      await page.wait_for_timeout(425)
    await frame.locator("#leaveGalley").wait_for(state="visible",timeout=10000)
    await frame.locator("#leaveGalley").tap()
    await frame.locator("#downBtn").wait_for(state="visible",timeout=10000)
    assert await frame.locator("#downBtn").is_enabled()
    galley=await measure()
    assert galley["row"]=="GALLEY",galley
    await frame.locator("#downBtn").tap(timeout=6000)
    await page.wait_for_timeout(480)
    result=await measure()
    assert result["row"]=="ROW 1",(width,height,result)
    assert result["x"] < galley["x"]-30, (width,height,galley,result)
    assert "NaN" not in result["transform"],result
    assert not errors,(width,height,errors[:3])
    print(f"PASS {width}x{height}: Galley return DOWN visibly advances to row 1.",flush=True)
    await page.close()

async def main():
 async with async_playwright() as playwright:
  browser=await playwright.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
  try:
   for dimensions in [(390,844),(844,390)]:
    await scene(browser,*dimensions)
  finally:
   await browser.close()
asyncio.run(main())
