"""Browser smoke: real Chromium on desktop/mobile, original game and online rooms."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
BASE="http://127.0.0.1:10000"
OUT=Path("/tmp/airport-smoke")
OUT.mkdir(exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
        try:
            for width,height in ((1366,768),(390,844),(667,375)):
                page=await browser.new_page(viewport={"width":width,"height":height})
                errors=[]
                page.on("pageerror",lambda e:errors.append(str(e)))
                await page.goto(BASE,wait_until="domcontentloaded",timeout=60000)
                await page.locator("#afLobbyLaunch").wait_for(state="attached",timeout=60000)
                await page.locator("#afOptions #afSoundTray").wait_for(state="attached",timeout=12000)
                assert await page.locator("#afAudioToggle").count()==0,"Floating audio button must not be on the home screen"
                assert not await page.locator("#afSoundTray").is_visible(),"Options audio settings leaked onto home screen"
                assert await page.evaluate("!!window.AF_AUDIO && typeof AF_AUDIO.effect==='function' && typeof AF_AUDIO.music==='function'"),"Audio director not loaded"
                assert await page.locator("#afMusicVolume").count()==1,"Music volume missing"
                assert await page.locator("#afFxVolume").count()==1,"Effects volume missing"
                main_buttons=page.locator("#afFront .afMainButtons button")
                assert await main_buttons.count()==4, "Expected 3 play modes plus Install App"
                for sel,txt in (("#partyPlay","PARTY MODE"),("#gameSelect","CASUAL MODE"),("#afLobbyLaunch","START A LOBBY")):
                    el=page.locator(sel)
                    assert txt in (await el.inner_text()),sel
                    assert await el.is_visible(),f"{sel} hidden on {width}x{height}"
                    box=await el.bounding_box()
                    assert box and box["x"]>=-1 and box["x"]+box["width"]<=width+1 and box["y"]>=-1 and box["y"]+box["height"]<=height+1, f"{sel} off-screen: {box} on {width}x{height}"
                await page.locator("#gameSelect").click()
                game_count=await page.locator("#afGames .gameChoice").count()
                if game_count<6:
                    print("DEBUG game_count:",game_count,flush=True)
                    print("DEBUG game headings:",await page.locator(".gameChoice h2").all_inner_texts(),flush=True)
                    print("DEBUG page errors:",errors[:12],flush=True)
                    script_diagnostic=await page.evaluate("""() => {let e=document.querySelector('#af-online-v12'),s=e?.textContent||'';let pos=s.indexOf('#afGameJump');return {len:s.length,preview:s.slice(Math.max(0,pos-120),pos+210),begin:s.slice(0,150),end:s.slice(-150),hasApi:!!window.__AF_ONLINE};}""")
                    print("DEBUG online inline script:",script_diagnostic,flush=True)
                    print("DEBUG original marshal count:",await page.locator("#startMarshal").count(),flush=True)
                    print("DEBUG external script links:",await page.locator("script[src]").evaluate_all("(x)=>x.map(e=>e.src)"),flush=True)
                    r=await page.request.get(BASE+"/online_party.js?v=13")
                    payload=await r.text()
                    print("DEBUG party fetch:",r.status,len(payload),repr(payload[-100:]),flush=True)
                    print("DEBUG front DOM:",await page.locator("#afFront .afMainButtons").inner_html(),flush=True)
                    print("DEBUG game mount:",(await page.locator("#afGameMount").inner_html())[:1200],flush=True)
                assert game_count>=6, "Lost one of six games: "+str(game_count)
                assert await page.locator("#startMarshal").count()==1,"Missing Air Marshalling"
                await page.screenshot(path=str(OUT/f"menu-{width}.png"))
                await page.close()
            host=await browser.new_page(viewport={"width":1366,"height":768})
            guest=await browser.new_page(viewport={"width":390,"height":844})
            await host.goto(BASE,wait_until="domcontentloaded",timeout=60000)
            await guest.goto(BASE,wait_until="domcontentloaded",timeout=60000)
            await host.locator("#afLobbyLaunch").click()
            await host.locator("#afName").fill("Captain")
            await host.locator("#afCreate").click()
            await host.locator("#afOnlineRoom .roomcode").wait_for(timeout=15000)
            code=(await host.locator("#afOnlineRoom .roomcode").inner_text()).strip()
            assert len(code)==6,code
            await guest.locator("#afLobbyLaunch").click()
            await guest.locator("#afName").fill("Ramp Agent")
            await guest.locator("#afCodeInput").fill(code)
            await guest.locator("#afJoin").click()
            await guest.locator("#afOnlineRoom .roomcode").wait_for(timeout=15000)
            await host.wait_for_function("document.querySelectorAll('#afOnlineRoom .member').length>=2",timeout=15000)
            await host.locator("#afSingle").click()
            await host.locator("#afGameSelect").select_option("bags")
            await host.locator("#afStart").click()
            await host.locator("#afSyncCountdown").wait_for(timeout=15000)
            await guest.locator("#afSyncCountdown").wait_for(timeout=15000)
            # Neither player clicks Play; server launches the same game automatically.
            await host.wait_for_function("window.__AF_ONLINE?.getState().playing===true",timeout=15000)
            await guest.wait_for_function("window.__AF_ONLINE?.getState().playing===true",timeout=15000)
            host_info=await host.evaluate("window.__AF_ONLINE.getState()")
            guest_info=await guest.evaluate("window.__AF_ONLINE.getState()")
            assert host_info["room"]["startAt"]==guest_info["room"]["startAt"],"Devices used different clocks"
            assert host_info["room"]["roundId"]==guest_info["room"]["roundId"],"Devices joined different games"
            assert host_info["room"]["game"]==guest_info["room"]["game"]=="bags"
            await host.locator("#afRivals .rival").first.wait_for(timeout=6000)
            await guest.locator("#afRivals .rival").first.wait_for(state="attached",timeout=6000)
            assert await host.locator("#afRivals .rival").count()==1,"No opponent PiP"
            assert await guest.locator("#afRivals .rival").count()==1,"Guest PiP missing"
            assert await host.locator("#bagGame").is_visible(),"Host game canvas isn't visible"
            assert await guest.locator("#bagGame").is_visible(),"Guest game canvas isn't visible"
            await host.locator("#afRivals .rival img").first.wait_for(timeout=12000)
            await guest.locator("#afRivals .rival img").first.wait_for(state="attached",timeout=12000)
            assert await host.locator("#afRivals .rival img").count()==1, "Host has no real opponent frame"
            assert await guest.locator("#afRivals .rival img").count()==1, "Guest has no real opponent frame"
            assert await host.locator("#startBagVersus").evaluate("(b)=>getComputedStyle(b).pointerEvents")=="none","Online split screen not disabled"
            await host.screenshot(path=str(OUT/"bag-desktop.png"))
            await guest.screenshot(path=str(OUT/"bag-mobile.png"))
            print("PASS: synchronized Bag Stacker and desktop opponent preview; mobile preview kept unobtrusively hidden.")
            await host.close()
            await guest.close()
        finally:
            await browser.close()

if __name__=="__main__":
    asyncio.run(main())
