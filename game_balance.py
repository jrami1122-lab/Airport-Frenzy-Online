"""Build-time improvements to the original minigames, kept separate from online room code."""
import re,base64

def replace_one(s,a,b,why):
    n=s.count(a)
    if n!=1:raise RuntimeError(f"{why}: expected one match, found {n}")
    return s.replace(a,b,1)

def patch_ramp(s):
    R=lambda a,b,why:replace_one(s,a,b,why)
    s=R("let players=[],loose=[],repairs=[],particles=[];",
"""let players=[],loose=[],repairs=[],particles=[],shiftClock=0;
const DEPOT={x:270,y:750,r:145},SHIFT_SECONDS=150;
function bankCarts(p){
 if(!p.alive||p.carts.length<6||p.bankCooldown>0||distance(p,DEPOT)>DEPOT.r)return;
 const n=Math.min(10,p.carts.length),points=n*150+(n===10?200:0);
 p.carts.splice(-n);p.banked+=points;p.delivered+=n;p.bankCooldown=1.7;
 message(p.id+' DEPOSITED '+n+' CARTS · +'+points+' BANKED!');
 burst(DEPOT.x,DEPOT.y,p.color);beep(940,.18,'sine');updateHud();
}
function finishRampShift(){
 if(!playing||paused)return;paused=true;playing=false;stopEngines();
 $('#modeSelect').hidden=false;
 const winner=[...players].sort((a,b)=>scoreOf(b)-scoreOf(a))[0];
 message('SHIFT COMPLETE · '+winner.id+' '+scoreOf(winner)+' POINTS');
 updateHud();
}
""","ramp banking")
    s=replace_one(s,"immune:0}}","immune:0,banked:0,delivered:0,bankCooldown:0}}","ramp player bank values")
    s=replace_one(s,"spawnClock=0;repairClock=0;flyover=null;flyClock=0;nextFly=rnd(15,60);players=","spawnClock=0;repairClock=0;shiftClock=0;flyover=null;flyClock=0;nextFly=rnd(15,60);players=","ramp timer reset")
    s=replace_one(s,"function scoreOf(p){return p.carts.length*1000+p.bonuses*100-p.lostCarts*500-p.livesLost*100-(p.eliminated?5000:0)}",
    "function scoreOf(p){return Math.max(0,p.banked+p.carts.length*65+p.bonuses*60-p.lostCarts*15-p.livesLost*35)}","bank-safe ramp score")
    s=replace_one(s,"function scoreBreakdown(p){return p.id+' '+scoreOf(p)+' ('+p.carts.length+' carts, '+p.bonuses+' bonuses, '+p.lostCarts+' lost)'}",
    "function scoreBreakdown(p){return p.id+' '+scoreOf(p)+' ('+p.delivered+' banked carts, '+p.carts.length+' on tug, '+p.lostCarts+' lost)'}","ramp breakdown")
    s=replace_one(s,"p.tier++;message(p.id+' SPEED TIER '","p.tier=Math.min(5,p.tier+1);message(p.id+' SPEED TIER '","ramp speed ceiling")
    s=replace_one(s,"if(p.x<35||p.x>world.w-35||p.y<35||p.y>world.h-35){p.x=clamp(p.x,35,world.w-35);p.y=clamp(p.y,35,world.h-35);hit(p,'boundary')}",
"""if((p.x<35||p.x>world.w-35)&&Math.abs(p.y-750)<135){
 const dx=p.x<35?world.w-115:-(world.w-115);p.x+=dx;
 for(const c of p.carts)c.x+=dx;
 p.immune=Math.max(.65,p.immune);
 message(p.id+' USED SIDE-SERVICE TUNNEL');
}else if(p.x<35||p.x>world.w-35||p.y<35||p.y>world.h-35){
 p.x=clamp(p.x,35,world.w-35);p.y=clamp(p.y,35,world.h-35);hit(p,'boundary')
}""","two-way tunnel")
    s=replace_one(s,"for(const c of [...loose])if(distance(c,p)<58){collect(p,c);break}",
    "p.bankCooldown=Math.max(0,p.bankCooldown-dt);bankCarts(p);for(const c of [...loose])if(distance(c,p)<58){collect(p,c);break}","deposit trigger")
    s=replace_one(s,"players.forEach(p=>updatePlayer(p,dt));for(const c of loose)",
    "shiftClock+=dt;players.forEach(p=>updatePlayer(p,dt));if(shiftClock>=SHIFT_SECONDS){finishRampShift();return}for(const c of loose)","2:30 shift")
    s=replace_one(s,"ctx.fillText('GATE 12',185,135);ctx.fillText('SERVICE ROAD',1660,1390);",
"""ctx.fillText('GATE 12',185,135);ctx.fillText('SERVICE ROAD',1660,1390);
 ctx.save();ctx.fillStyle='#194b38dd';ctx.strokeStyle='#89f2ac';ctx.lineWidth=9;
 ctx.fillRect(DEPOT.x-125,DEPOT.y-120,250,240);
 ctx.strokeRect(DEPOT.x-125,DEPOT.y-120,250,240);
 ctx.fillStyle='#dcffe5';ctx.textAlign='center';ctx.font='bold 30px Arial';
 ctx.fillText('CART DEPOT',DEPOT.x,DEPOT.y-30);
 ctx.font='bold 24px Arial';ctx.fillText('BANK 6–10 CARTS',DEPOT.x,DEPOT.y+20);
 ctx.restore();
 for(const x of [0,world.w-78]){
 ctx.fillStyle='#132e48';ctx.fillRect(x,615,78,270);
 ctx.strokeStyle='#82dcff';ctx.lineWidth=7;ctx.strokeRect(x,615,78,270);
 }""","visible depot and tunnel")
    s=replace_one(s,"ui.mode.textContent=mode==='versus'?'Versus: P1 WASD · P2 Arrows':'Solo: Arrow keys or touch';",
    "ui.mode.textContent='2:30 SHIFT · GREEN DEPOT: BANK 6–10 CARTS · BLUE SIDE TUNNELS';","ramp directions")
    s=replace_one(s,"function updateHud(){if(mode==='solo')",
    "function updateHud(){ui.mode.textContent='SHIFT '+Math.floor(Math.max(0,SHIFT_SECONDS-shiftClock)/60)+':'+String(Math.floor(Math.max(0,SHIFT_SECONDS-shiftClock)%60)).padStart(2,'0')+' · BANK 6–10 CARTS';if(mode==='solo')","timer HUD")
    return s

def patch_cabin(s):
    pattern=r"(const CABIN_SERVICE_HTML=')([A-Za-z0-9+/=]+)(')"
    m=re.search(pattern,s)
    if not m:raise RuntimeError("Cabin base64 missing")
    code=base64.b64decode(m.group(2)).decode("utf-8")
    code=replace_one(code,"CAPACITY=12,MAX_ROUNDS=20","CAPACITY=12,MAX_ROUNDS=10","10-trip cabin")
    code=replace_one(code,"START 20-TRIP SHIFT","START 10-TRIP SHIFT","cabin button")
    # Show true net service points during the shift rather than deferring customer
    # penalties until the last trip; this is the score the online room observes.
    code=replace_one(code, "$('#score').textContent=score;",
      "$('#score').textContent=Math.max(0,score-lost*500);", "live net cabin score")
    code=replace_one(code,"const penalty=lost*500,final=score-penalty",
      "const penalty=lost*500,final=Math.max(0,score-penalty)","nonnegative final cabin score")
    return s[:m.start(2)]+base64.b64encode(code.encode()).decode()+s[m.end(2):]

def patch_marshalling(s):
    s=replace_one(s,"const poses={out:{l:-165,r:-15},inner:{l:-25,r:-155},up:{l:-58,r:-122},down:{l:75,r:105},front:{l:-52,r:-128}};",
    "const poses={out:{l:-160,r:-20},inner:{l:-35,r:-145},up:{l:-90,r:-90},down:{l:85,r:95},front:{l:20,r:160}};","distinct wand directions")
    s=replace_one(s,
    "let sequence=[],playerIndex=0,round=1,running=false,paused=false,demoing=false,expected=null,tapCount=0,tapTimer=0,circleReady={l:false,r:false},best=+(localStorage.airMarshallBest||0),audio=null;",
    """let sequence=[],playerIndex=0,round=1,running=false,paused=false,demoing=false,expected=null,tapCount=0,tapTimer=0,circleReady={l:false,r:false},best=+(localStorage.airMarshallBest||0),audio=null,points=0;
const scorePill=document.createElement('div');
scorePill.className='pill';scorePill.innerHTML='SCORE <b id="score">0</b>';game.querySelector('.hud')?.append(scorePill);
// A neutral control hint is always present; no combined pose or correctness badge.
const submitHelp=document.createElement('small');submitHelp.id='submitHelp';
submitHelp.textContent='(double tap for double signal)';
submitHelp.style.cssText='position:absolute;z-index:15;left:50%;bottom:max(3px,env(safe-area-inset-bottom));transform:translateX(-50%);font:600 10px/1.25 system-ui;color:#f1f7fb;text-align:center;white-space:nowrap;text-shadow:0 2px 4px #001;pointer-events:none';
game.append(submitHelp);
submit.style.bottom='max(27px,calc(env(safe-area-inset-bottom) + 24px))';
const signalStyle=document.createElement('style');
signalStyle.textContent='.game #submit{bottom:max(27px,calc(env(safe-area-inset-bottom) + 24px))!important}.game #submitHelp{display:block}.game .armCheck.ready{background:#071f30e8!important;color:#fff!important;border-color:#8bdfff70!important;box-shadow:0 6px 18px #0018!important}';
document.head.append(signalStyle);""","marshalling scoring and hint")
    s=replace_one(s,"armChecks[side].classList.remove('ready')}",
    "armChecks[side].classList.remove('ready')}","wand status stays neutral")
    s=replace_one(s,"function matches(c){return zones.l===c.l&&zones.r===c.r&&(!c.circle||circleReady[c.circle])}",
    """function matches(c){return zones.l===c.l&&zones.r===c.r&&(!c.circle||circleReady[c.circle])}
// Individual arm panels display ALL possible commands for THAT arm position only.
// They must never filter by the opposite wand or by the instructor's target.
function armOptions(side){
 return commands.filter(c=>c[side]===zones[side]).map(c=>
 c.name+(c.taps===2?' (DOUBLE)':'')+(c.circle?' (CIRCLE '+c.circle.toUpperCase()+')':''));
}
function armLabel(side){return (side==='l'?'LEFT':'RIGHT')+' — '+armOptions(side).join(' · ')}
let pendingSignalTimer=null,pendingSignature=null;
function signalSignature(){return zones.l+'|'+zones.r+'|'+!!circleReady.r+'|'+!!circleReady.l}
function resolveSubmission(taps){
 clearTimeout(pendingSignalTimer);pendingSignalTimer=null;pendingSignature=null;tapCount=0;
 if(!running||paused||demoing)return;
 const expected=sequence[playerIndex];
 const actual=commands.find(c=>matches(c)&&(c.taps===2?2:1)===taps);
 if(!actual||!expected||actual.id!==expected.id){fail(expected);return}
 points+=100+Math.min(100,(round-1)*10);
 scorePill.querySelector('#score').textContent=points;
 parent.AF_AUDIO?.effect('ding',{gain:.85});
 sfx('good');message.textContent='CORRECT SIGNAL';game.classList.add('flash');
 setTimeout(()=>game.classList.remove('flash'),220);playerIndex++;resetPose();
 if(playerIndex===sequence.length){
  round++;best=Math.max(best,sequence.length);
  localStorage.airMarshallBest=best;bestEl.textContent='BEST '+best;
  step.textContent='SEQUENCE CLEAR';setTimeout(nextRound,850)
 }else step.textContent='YOUR TURN · '+(playerIndex+1)+'/'+sequence.length;
}""","no combined signal readout and Simon submission evaluation")
    # Generate each guide directly from the authoritative commands: no stale
    # hand-maintained list and no cross-arm matching indicator.
    start=s.find("function armFeedback(side){")
    end=s.find("function setPose(side,",start)
    if start<0 or end<0:raise RuntimeError("original arm feedback missing")
    s=s[:start]+"""function armFeedback(side){
 armChecks[side].textContent=armLabel(side);
 armChecks[side].classList.remove('ready');
}
"""+s[end:]
    s=replace_one(s,
      "function fail(c){if(!running)return;running=false;sfx('bad');",
      "function fail(c){if(!running)return;clearTimeout(pendingSignalTimer);pendingSignalTimer=null;pendingSignature=null;running=false;parent.AF_AUDIO?.effect('wrong',{gain:.8});sfx('bad');",
      "wrong submission should fail")
    s=replace_one(s,
      "'</b> full rounds.<br>The expected signal was <b>'+c.name+'</b>.';",
      "'</b> full rounds.<br>Incorrect signal. Try again to repeat the sequence.';",
      "no correct-answer spoiler after fail")
    s=replace_one(s,
      "function begin(){sequence=[];round=1;playerIndex=0;running=true;",
      "function begin(){clearTimeout(pendingSignalTimer);pendingSignalTimer=null;pendingSignature=null;sequence=[];round=1;playerIndex=0;running=true;",
      "clear pending submit on restart")
    s=replace_one(s,
      "function resetPose(){lastReady.l=lastReady.r=false;",
      "function resetPose(){clearTimeout(pendingSignalTimer);pendingSignalTimer=null;pendingSignature=null;lastReady.l=lastReady.r=false;",
      "reset submitted gesture")
    s=replace_one(s,"pendingSignature=null;sequence=[];round=1;playerIndex=0;running=true;",
    "pendingSignature=null;sequence=[];round=1;playerIndex=0;points=0;scorePill.querySelector('#score').textContent=0;running=true;","marshalling score reset")
    # Replace the ENTIRE legacy submit handler: leaving its former tail would
    # create a syntax error and accidentally retain its target-based grading.
    start=s.find("function submitSignal(){")
    end=s.find("function fail(c)",start)
    if start<0 or end<0:raise RuntimeError("original marshalling submit handler missing")
    s=s[:start]+"""function submitSignal(){
 if(!running||paused||demoing)return;
 const expected=sequence[playerIndex];
 if(pendingSignalTimer){
  if(pendingSignature!==signalSignature()){clearTimeout(pendingSignalTimer);pendingSignalTimer=null;pendingSignature=null;fail(expected);return}
  resolveSubmission(2);return;
 }
 // Judge what the player actually submitted, never the requested command first.
 const possibilities=commands.filter(c=>matches(c));
 if(!possibilities.length){fail(expected);return}
 if(possibilities.some(c=>c.taps===2)){
  pendingSignature=signalSignature();
  pendingSignalTimer=setTimeout(()=>resolveSubmission(1),900);
  message.textContent='SIGNAL RECEIVED';return;
 }
 resolveSubmission(1);
}
"""+s[end:]
    # The new submit handler resolves only the gesture actually performed
    # (including double-press timing); wrong answers fail at submission.
    start=s.find("function zoneFrom(side,x,y){")
    end=s.find("function drag(side,e)",start)
    if start<0 or end<0:raise RuntimeError("marshalling drag classifier missing")
    s=s[:start]+"""function zoneFrom(side,x,y){
 const p=person.getBoundingClientRect(),sx=p.left+(side==='l'?90:168),sy=p.top+104;
 const dx=x-sx,dy=y-sy;if(Math.hypot(dx,dy)<22)return zones[side];
 const angle=Math.atan2(dy,dx);
 let result='down',best=Infinity;
 for(const [name,pair] of Object.entries(poses)){
  const delta=angle-pair[side]*Math.PI/180;
  const diff=Math.abs(Math.atan2(Math.sin(delta),Math.cos(delta)));
  if(diff<best){best=diff;result=name}
 }
 return result;
}
"""+s[end:]
    # Original pointerup closure referenced sx/sy defined only inside pointermove.
    # Recompute shoulder coordinates on release so circular and ordinary drags
    # cannot throw ReferenceError and skip the actual signal recognition.
    s=replace_one(s,
        "h.onpointerup=h.onpointercancel=v=>{move(v);",
        "h.onpointerup=h.onpointercancel=v=>{const box=person.getBoundingClientRect(),sx=box.left+(side==='l'?90:168),sy=box.top+104;move(v);",
        "fix Air Marshalling undefined pointerup shoulder coordinates")
    s=replace_one(s,"addEventListener('resize',resetPose);resetPose();",
    "addEventListener('resize',resetPose);resetPose();","no center hint initialization")
    return s

def patch(html):
    return patch_marshalling(patch_cabin(patch_ramp(html)))
