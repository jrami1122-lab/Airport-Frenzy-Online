"""Release UI fixes, responsive Cabin Service, and native Ramp Runner tail contact."""
import base64,re

def once(s,a,b,why):
    if s.count(a)!=1:raise RuntimeError(f"release {why}: expected 1 source anchor, found {s.count(a)}")
    return s.replace(a,b,1)

def patch(html):
    # Responsive six-seat aircraft. Six seats always fit; belt labels are overlays
    # and never change grid sizing. Rules apply to both portrait and landscape.
    m=re.search(r"(const CABIN_SERVICE_HTML=')([A-Za-z0-9+/=]+)(')",html)
    if not m:raise RuntimeError("Cabin code missing")
    cabin=base64.b64decode(m.group(2)).decode('utf-8')
    css=r"""
<style id="af-cabin-six-seat-responsive">
:root{--afseatgap:clamp(1px,.7vw,4px)}
html,body{min-width:0!important;max-width:100%!important;overflow:hidden!important}
.app,.game-area,.cabin-shell,.cabin-viewport,.track,.seat-row{min-width:0!important;max-width:100%!important}
.seat-row{grid-template-columns:repeat(3,minmax(0,1fr)) minmax(12px,7%) repeat(3,minmax(0,1fr))!important;
 gap:var(--afseatgap)!important;padding:3px clamp(2px,1.4vw,8px)!important;
 width:100%!important;box-sizing:border-box!important}
.seat{min-width:0!important;width:100%!important;overflow:visible;isolation:isolate}
.gamepadSeat{position:absolute!important;top:2px!important;left:2px!important;
 padding:1px 2px!important;font-size:clamp(7px,1.5vw,10px)!important;line-height:1!important;
 z-index:2;max-width:calc(100% - 4px);pointer-events:none}
.passenger{max-width:100%;transform-origin:center bottom}
.seat-code{font-size:clamp(7px,1.35vw,10px)!important;z-index:2}
.aisle{min-width:0!important;width:100%}
.hud{min-width:0!important}.stats{min-width:0!important}.pill{min-width:0;overflow:hidden;text-overflow:ellipsis}
@media(max-width:760px){
 :root{--rowH:clamp(66px,12dvh,85px)}
 .game-area{display:grid!important;grid-template-columns:minmax(0,1fr)!important;
 grid-template-rows:minmax(0,1fr)!important;padding:4px!important;height:100%!important}
 .cabin-shell{width:100%!important;margin:0 auto!important;border-width:2px!important;
 border-radius:18px!important;overflow:hidden!important}
 .cabin-viewport{inset:5px clamp(6px,2.5vw,14px)!important}
 .seat-row{height:var(--rowH)!important}
 .seat{height:clamp(46px,8.2dvh,66px)!important;border-width:1px!important;border-radius:8px!important}
 .passenger{transform:scale(.64)!important}
 .seat-row:not(.current) .passenger{transform:scale(.58)!important}
 .gamepadSeat{font-size:8px!important}
 .bubble{z-index:5;max-width:100px;min-width:0!important;width:max-content!important;
 font-size:9px!important;white-space:normal!important;overflow-wrap:anywhere}
 .controls{position:relative!important;width:100%!important;right:auto!important;bottom:auto!important;
 padding:4px max(6px,env(safe-area-inset-right)) calc(4px + env(safe-area-inset-bottom))!important;
 background:#07131ee8!important}
 .controls button{min-height:43px!important}
 .hud{padding:4px 6px!important;max-height:none!important}
 .title{font-size:clamp(9px,2.6vw,12px)!important}
}
@media(orientation:landscape) and (max-height:600px){
 :root{--rowH:64px}
 .app{height:100dvh!important;grid-template-rows:auto minmax(0,1fr) auto!important}
 .game-area{height:100%!important;min-height:0!important;padding:3px!important;
 grid-template-columns:minmax(0,1fr)!important;grid-template-rows:minmax(0,1fr)!important}
 .cabin-shell{max-width:min(680px,94vw)!important;min-height:0!important;
 border-width:2px!important}
 .cabin-viewport{inset:3px clamp(5px,2vw,12px)!important}
 .seat-row{grid-template-columns:repeat(3,minmax(0,1fr)) minmax(11px,6%) repeat(3,minmax(0,1fr))!important;
 padding:2px 5px!important;gap:2px!important}
 .seat{height:49px!important}
 .passenger{transform:scale(.62)!important}
 .hud{max-height:58px!important;overflow:hidden!important;
 grid-template-columns:minmax(0,1fr) auto!important;gap:3px!important}
 .stats{display:flex!important;flex-wrap:nowrap!important}.pill{font-size:9px!important;padding:3px!important}
 .controls{position:relative!important;inset:auto!important;width:100%!important;
 min-height:47px!important;padding:3px 8px calc(3px + env(safe-area-inset-bottom))!important}
 .controls button{min-height:39px!important}
 .side-panel{display:none!important}
}
@media(max-width:360px){.passenger{transform:scale(.52)!important}.gamepadSeat{font-size:7px!important}}
</style>
"""
    cabin=once(cabin,"</head>",css+"</head>","cabin media CSS")
    cabin=once(cabin,"detail:{game:'cabin',reason:'complete'}",
      "detail:{game:'cabin',reason:'complete',player:window.frameElement?.id==='afLocalP2Frame'?2:1}",
      "who finished Cabin Service")

    html=html[:m.start(2)]+base64.b64encode(cabin.encode()).decode()+html[m.end(2):]
    html=once(html,"detail:{game:'marshal',reason:'wrong-signal'}",
       "detail:{game:'marshal',reason:'wrong-signal',player:window.frameElement?.id==='afLocalP2Frame'?2:1}",
       "who failed Air Marshalling")
    # Native opponent cart / tow-train collision, with sparks and real lost carts.
    src="function updatePlayer(p,dt){if(!p.alive)return;"
    collision="""function rivalTailContact(p){
 if(mode!=='versus'||!p.alive||p.immune>0)return;
 for(const other of players){
  if(other===p||!other.alive)continue;
  if(Math.hypot(p.x-other.x,p.y-other.y)<49){
   hit(p,'head-on');window.AF_AUDIO?.effect('crash',{gain:1,cooldown:650});
   burst((p.x+other.x)/2,(p.y+other.y)/2,'#ffca38');return;
  }
  for(let j=0;j<other.carts.length;j++){
   const cart=other.carts[j];
   if(Math.hypot(p.x-cart.x,p.y-cart.y)<48){
    hit(other,'opponent-tail',j);
    burst(cart.x,cart.y,'#ffae44');burst(p.x,p.y,'#ff4d51');
    window.AF_AUDIO?.effect('crash',{gain:1,cooldown:650});return;
   }
  }
 }
}
"""
    html=once(html,src,collision+src,"ramp rival tail physics")
    html=once(html,"collisionBody(p);",
      "collisionBody(p);rivalTailContact(p);",
      "ramp collision application")
    # Avoid overlaid mini-game panels on mobile in all orientations.
    polish="""<style id="af-release-overflow">
:root{--af-safe-bottom:env(safe-area-inset-bottom)}
html,body{max-width:100vw!important;overflow-x:hidden!important}
button,a,input,select{touch-action:manipulation}
#afRivals{max-height:26dvh!important;overflow:hidden!important}
@media(max-width:767px),((pointer:coarse) and (max-height:600px)){
 #afRivals,#afPadBadge{display:none!important}
 #afShiftClock.visible{right:max(4px,env(safe-area-inset-right))!important;
  bottom:calc(3px + env(safe-area-inset-bottom))!important;
  padding:2px 5px!important;min-width:0!important;max-width:105px!important;
  opacity:.84!important;pointer-events:none!important}
 #afShiftClock.visible #afShiftTime{font-size:14px!important}
 #afShiftClock #afShiftEnd{pointer-events:auto!important}
 #afRivals.visible{display:none!important}
 #afFront .afMainButtons{max-width:calc(100vw - 14px)!important}
 .cabinHost{overflow:hidden!important}
 .cabinHost iframe{width:100%;height:100dvh;max-width:100vw}
}
@media(orientation:landscape) and (max-height:510px){
 #afFront .afHome,#afFront .afPanel{max-height:100dvh!important}
 #afGames .arcadeGrid{max-height:calc(100dvh - 100px)!important;overflow-y:auto!important}
 .cabinHost .cabinMenu{top:2px!important;left:4px!important;padding:4px 7px!important;
 font-size:10px!important;max-width:100px!important;white-space:nowrap!important}
}
</style>"""
    html=html.replace("</head>",polish+"</head>",1)
    return html
