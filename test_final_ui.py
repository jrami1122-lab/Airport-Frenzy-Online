"""Regression: no unwanted controller scrollbar, Options-only music and real Bag end."""
import asyncio
from playwright.async_api import async_playwright
BASE='http://127.0.0.1:10000'

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  try:
   home=await browser.new_page(viewport={'width':850,'height':450})
   errors=[];home.on('pageerror',lambda e:errors.append(str(e)))
   await home.goto(BASE,wait_until='domcontentloaded')
   await home.locator('#afSoundTray').wait_for(state='attached',timeout=20000)
   assert not await home.locator('#afSoundTray').is_visible(), 'Audio panel visible on home screen'
   assert await home.locator('#afOptions #afMusicVolume').count()==1,'Music slider not inside Options'
   assert await home.locator('#afOptions #afFxVolume').count()==1,'Effects slider not inside Options'
   assert await home.locator('#afAudioToggle').count()==0,'Old floating Audio toggle returned'
   assert await home.locator('#afFront .afMainButtons button').count()==3
   await home.evaluate("""()=>{
    const g={index:0,connected:true,axes:[0,0,0,0],
      buttons:Array.from({length:17},()=>({pressed:false,value:0}))};
    for(let i=0;i<5;i++){g.axes[1]=.92;window.AF_GAMEPAD.tick([g]);g.axes[1]=0;window.AF_GAMEPAD.tick([g]);}
   }""")
   positions=await home.evaluate("""()=>({
    bodyX:document.scrollingElement.scrollLeft,bodyY:document.scrollingElement.scrollTop,
    homeX:document.getElementById('afHome').scrollLeft,homeY:document.getElementById('afHome').scrollTop,
    overflow:getComputedStyle(document.getElementById('afHome')).overflowY
   })""")
   assert positions['bodyX']==0 and positions['homeX']==0 and positions['homeY']==0,'Controller moved menu scroll position: '+str(positions)
   await home.locator('#afMusic').click()
   assert await home.locator('#afOptions').is_visible()
   assert await home.locator('#afSoundTray').is_visible()
   await home.locator('#optionMusic').click()
   assert await home.locator('#optionMusic').inner_text()=='OFF','Options music toggle disconnected'
   await home.locator('#optionMusic').click()
   await home.locator('#optionSfx').click()
   assert await home.locator('#optionSfx').inner_text()=='OFF','Options effects toggle disconnected'
   await home.locator('#optionSfx').click()
   await home.locator('#optionsDone').click()
   assert not await home.locator('#afSoundTray').is_visible()
   assert not errors,'Home JS errors '+str(errors[:3])
   print('PASS menu: gamepad focus does not expose scrollbars; music/SFX live exclusively in Options.',flush=True)
   await home.close()

   bag=await browser.new_page(viewport={'width':1366,'height':768})
   bag_errors=[];bag.on('pageerror',lambda e:bag_errors.append(str(e)))
   await bag.goto(BASE,wait_until='domcontentloaded')
   await bag.locator('#gameSelect').click()
   await bag.locator('#startBagSolo').click()
   await bag.locator('#afShiftClock.visible').wait_for(timeout=10000)
   state=await bag.evaluate("window.__AF_BAG_STATE?.()")
   assert state and len(state['boards'])==1 and state['boards'][0]['gameOver'] is False,state
   assert await bag.evaluate("typeof window.__AF_TEST_BAG_END")== 'function'
   await bag.evaluate("window.__AF_TEST_BAG_END(0)")
   await bag.locator('#afLocalResults.open').wait_for(timeout=2400)
   assert 'SHIFT COMPLETE' in await bag.locator('#afLocalResults').inner_text()
   assert not await bag.locator('#afShiftClock').is_visible()
   saved=await bag.evaluate("window.AF_LOCAL.stats()['P1 / Bag Stacker']")
   assert saved and saved['plays']>=1,'Bag score not saved at game-over'
   assert not bag_errors,'Bag JS errors '+str(bag_errors[:3])
   print('PASS Bag Stacker: real board gameOver immediately ends match and saves final score (no timer wait).',flush=True)
   await bag.close()

   docs=await browser.new_page(viewport={'width':1366,'height':768})
   await docs.goto(BASE,wait_until='domcontentloaded')
   await docs.locator('#gameSelect').click()
   await docs.locator('#startDocsSolo').click()
   frame=docs.frame_locator('#docFrame')
   await frame.locator('body').wait_for(timeout=10000)
   await frame.locator('body').evaluate("""body=>{
     const region=document.createElement('div');
     region.id='testDocumentsScroller';region.className='caseScroll';
     region.style.cssText='position:absolute;top:8px;left:8px;height:70px;width:210px;overflow-y:auto';
     region.innerHTML='<div style="height:700px">Case files</div>';
     body.appendChild(region);
   }""")
   await docs.evaluate("""()=>{
    const gp={index:0,connected:true,axes:[0,.9,0,0],
     buttons:Array.from({length:17},(_,i)=>({pressed:i===4,value:i===4?1:0}))};
    window.AF_GAMEPAD.tick([gp]);window.AF_GAMEPAD.tick([gp]);
   }""")
   moved=await frame.locator('#testDocumentsScroller').evaluate('(el)=>el.scrollTop')
   assert moved>0,'LB + stick did not scroll Document Control: '+str(moved)
   print('PASS Document Control: LB + stick scrolls records instead of shifting selection.',flush=True)
   await docs.close()
  finally:await browser.close()

asyncio.run(main())
