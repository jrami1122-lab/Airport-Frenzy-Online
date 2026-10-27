"""Emulated Xbox standard gamepads to verify actual keyboard-compat mappings in Chromium."""
import asyncio
from playwright.async_api import async_playwright
BASE="http://127.0.0.1:10000"
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
  try:
   page=await browser.new_page(viewport={"width":1366,"height":768})
   await page.goto(BASE,wait_until="domcontentloaded")
   await page.locator("#afPadBadge").wait_for(timeout=12000)
   menu=await page.evaluate("""()=>{
     let joins=0;window.addEventListener('af-controller-start',()=>joins++);
     const gp={connected:true,index:0,axes:[0,0,0,0],buttons:Array.from({length:17},()=>({pressed:false,value:0}))};
     gp.buttons[9].pressed=true;window.AF_GAMEPAD.tick([gp]);window.AF_GAMEPAD.tick([gp]);
     return {joins,connected:window.AF_GAMEPAD.status().connected};
   }""")
   assert menu["joins"]==1,"Xbox Menu/Start should join once per press"
   assert menu["connected"]==1,"Controller detection failed"
   await page.locator("#gameSelect").click()
   await page.locator("#startSolo").click()
   routed=await page.evaluate("""()=>{
      const inputs=[];
      window.addEventListener('keydown',e=>inputs.push(e.key),true);
      const gp={connected:true,index:0,axes:[-.8,-.8,0,0],buttons:Array.from({length:17},()=>({pressed:false,value:0}))};
      window.AF_GAMEPAD.tick([gp]);window.AF_GAMEPAD.tick([]);
      return {inputs,mode:window.AF_GAMEPAD.status().mode};
   }""")
   assert 'a' in routed["inputs"] and 'w' in routed["inputs"],"Left stick not mapped to Ramp Runner WASD: "+str(routed)
   assert routed["mode"]=='ramp',"Wrong controller context: "+str(routed)
   await page.locator("#afShiftEnd").click()
   await page.locator("#afLocalNext").click()
   await page.locator("#afGames.active").wait_for(timeout=5000)
   await page.locator("#startMarshal").click()
   frame=page.frame_locator("#airFrame")
   await frame.locator("#leftCheck").wait_for(timeout=10000)
   await frame.locator("body").evaluate("(el)=>window.__AF_MARSHAL_TEST.setup('cutengine')")
   routed=await frame.locator("body").evaluate("""()=>{
     window.__xboxKeys=[];
     window.addEventListener('keydown',e=>window.__xboxKeys.push(e.key),true);
     return window.__xboxKeys;
   }""")
   result=await page.evaluate("""()=>{
     const gp={connected:true,index:0,axes:[.6,-.8,0,-.9],buttons:Array.from({length:17},()=>({pressed:false,value:0}))};
     gp.buttons[0].pressed=true;
     window.AF_GAMEPAD.tick([gp]);window.AF_GAMEPAD.tick([]);
     const doc=document.querySelector('#airFrame').contentDocument;
     return {keys:doc.defaultView.__xboxKeys,left:doc.querySelector('#leftA').style.transform,right:doc.querySelector('#rightA').style.transform};
   }""")
   assert ' ' in result["keys"],"Xbox A must submit signal: "+str(result)
   assert "rotate(-53" in result["left"],"Left wand snapped rather than following analog angle: "+str(result)
   assert "rotate(-90" in result["right"],"Right wand not tracking its own stick: "+str(result)
   print("PASS Xbox: Start joins, Ramp LS moves, marshalling wands rotate at actual analog angles and A submits.",flush=True)
  finally:await browser.close()
asyncio.run(main())