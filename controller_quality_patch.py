"""Controller polish, six-seat flight attendant and event-driven game end states."""
import base64,re

def one(s,a,b,name):
    n=s.count(a)
    if n!=1:
        raise RuntimeError(f"Controller polish {name}: expected one anchor, found {n}")
    return s.replace(a,b,1)

def patch(html):
    start=html.index("/* Soft, generated airport-lounge music.")
    end=html.index("/* Common navigation controls for every embedded game. */",start)
    html=html[:start]+"/* Background music comes only from the uploaded audio director. */\n"+html[end:]
    html=one(html,"hud.innerHTML='<b>HOLD FULL</b> · '+a.count+' bags'",
       "window.dispatchEvent(new CustomEvent('af-game-finished',{detail:{game:'bags',reason:'hold-full'}}));hud.innerHTML='<b>HOLD FULL</b> · '+a.count+' bags'",
       "solo Bag Stacker completion")
    html=one(html,"hud.innerHTML='<b>'+winner+'</b> · P1 '+at+' total'",
       "window.dispatchEvent(new CustomEvent('af-game-finished',{detail:{game:'bags',reason:'versus-finished'}}));hud.innerHTML='<b>'+winner+'</b> · P1 '+at+' total'",
       "two-player Bag Stacker completion")
    m=re.search(r"(const CABIN_SERVICE_HTML=')([A-Za-z0-9+/=]+)(')",html)
    if not m:raise RuntimeError("Cabin HTML not found")
    cabin=base64.b64decode(m.group(2)).decode("utf-8")
    cabin=one(cabin,"SEATS=['A','B','C','D']","SEATS=['A','B','C','D','E','F']","six passenger seat slots")
    cabin=one(cabin,"grid-template-columns:1fr 1fr 48px 1fr 1fr",
              "grid-template-columns:repeat(3,minmax(0,1fr)) 34px repeat(3,minmax(0,1fr))",
              "six seat columns")
    cabin=one(cabin,"j===2?'<div class=\"aisle\"></div>'",
              "j===3?'<div class=\"aisle\"></div>'","aisle after third seat")
    cabin=one(cabin,"<span class=\"seat-code\">$"+"{row}$"+"{letter}</span>",
              "<span class=\"seat-code\">$"+"{row}$"+"{letter}</span><small class=\"gamepadSeat\">$"+"{['LT','X','Y','A','B','RT'][j]}</small>",
              "integrated seat labels")
    cabin=one(cabin,".seat{height:79px;position:relative;",
             ".gamepadSeat{position:absolute;top:1px;left:4px;background:#093a55da;color:#fff9b8;border-radius:4px;font:900 10px system-ui;padding:1px 3px;pointer-events:none}.seat{height:79px;min-width:0;position:relative;",
             "discrete seat hints")
    cabin=one(cabin,"$('#upBtn').onclick=()=>move(-1);",
      """document.addEventListener('af-cabin-seat',ev=>{
 const letter=String(ev.detail?.seat||'');
 if(!SEATS.includes(letter))return;
 const p=passengers.find(p=>p.row===position&&p.letter===letter);
 if(!p||!p.request||p.lost){showToast('NO ACTIVE ORDER AT SEAT '+letter);return}
 deliver(p);
});
$('#upBtn').onclick=()=>move(-1);""",
      "flight attendant controller seat events")
    cabin=one(cabin,"function finishGame(){const penalty=",
      """function finishGame(){
 try{parent.dispatchEvent(new parent.CustomEvent('af-game-finished',{detail:{game:'cabin',reason:'complete'}}))}catch(e){}
 const penalty=""",
      "flight attendant completion event")
    html=html[:m.start(2)]+base64.b64encode(cabin.encode("utf-8")).decode("ascii")+html[m.end(2):]
    html=one(html,"running=false;parent.AF_AUDIO?.effect('wrong'",
      "running=false;try{parent.dispatchEvent(new parent.CustomEvent('af-game-finished',{detail:{game:'marshal',reason:'wrong-signal'}}))}catch(e){}parent.AF_AUDIO?.effect('wrong'",
      "Air Marshalling loss event")
    return html
