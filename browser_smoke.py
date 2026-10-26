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
                main_buttons=page.locator("#afFront .afMainButtons button")
                assert await main_buttons.count()==3, "Expected exactly 3 home modes"
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
                    print("DEBUG original marshal count:",await page.locator("#startMarshal").count(),flush=True)
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
            await host.locator("#afPlay").wait_for(timeout=15000)
            await guest.locator("#afPlay").wait_for(timeout=15000)
            await host.locator("#afPlay").click()
            await guest.locator("#afPlay").click()
            assert await host.locator("#afRivals .rival").count()==1,"No opponent PiP"
            assert await guest.locator("#afRivals .rival").count()==1,"Guest PiP missing"
            assert await host.locator("#startBagVersus").evaluate("(b)=>getComputedStyle(b).pointerEvents")=="none","Online split screen not disabled"
            await host.screenshot(path=str(OUT/"bag-desktop.png"))
            await guest.screenshot(path=str(OUT/"bag-mobile.png"))
            print("PASS: desktop/mobile/landscape menus, six games, online room, Casual Mode, Bag Stacker and opponent panel.")
            await host.close()
            await guest.close()
        finally:
            await browser.close()

if __name__=="__main__":
    asyncio.run(main())
