/* Airport Frenzy: Xbox One/Series standard-gamepad input. Existing touch/keyboard remain. */
(()=>{'use strict';if(window.AF_GAMEPAD)return;
const $=s=>document.querySelector(s);
const info={
 menu:'D-PAD navigate · A select · B back · START join · RS cursor · RT click',
 ramp:'LS drive/steer · RT gas · LT reverse · MENU pause · B exit',
 bags:'LS move chute · X rotate bag · RT fast belt · MENU pause · B exit',
 assist:'LS wheelchair · RT forward · LT reverse · MENU pause · B exit',
 cabin:'D-PAD aisle · RS pointer · A/RT click · LB/RB next options',
 docs:'D-PAD/LS navigate · A/RT click · RS pointer · LB/RB tabs',
 marshal:'LS left wand · RS right wand · LB/RB forward wands · Y circle · A signal (twice for DOUBLE)'};
const state=new Map();let connected=0,badge=null,help=null,focused=null,cursor=null,lastMode='',lastJoined=[];
const DEAD=.32;
function click(e){if(e&&!e.disabled&&e.getClientRects().length){e.click();return true}return false}
function mode(){
 if($('#afOnlineRoom.open')||$('#afLocalHub.open')||$('#afLocalResults.open'))return {id:'menu',doc:document};
 const lookup=[['marshal','airHost','airFrame'],['docs','docHost','docFrame'],['assist','assistHost','assistFrame'],['cabin','cabinHost','cabinFrame']];
 for(let [id,host,frame] of lookup)if($('#'+host)&&!$('#'+host).hidden){const iframe=$('#'+frame);
 try{if(iframe?.contentDocument?.body)return {id,doc:iframe.contentDocument}}catch(e){}
 return{id,doc:document}}
 if($('#bagGame')&&!$('#bagGame').hidden)return{id:'bags',doc:document};
 if($('#intro')?.classList.contains('hide')||($('#afFront')?.classList.contains('playing')))return{id:'ramp',doc:document};
 return {id:'menu',doc:document};
}
function k(doc,key,down){try{
 const w=doc.defaultView||window;
 w.dispatchEvent(new w.KeyboardEvent(down?'keydown':'keyup',{key,bubbles:true,cancelable:true}));
}catch(e){}}
function diffKeys(st,doc,next){const keys=new Set(next);
 for(const key of st.keys)if(!keys.has(key)||st.doc!==doc)k(st.doc||doc,key,false);
 for(const key of keys)if(!st.keys.has(key)||st.doc!==doc)k(doc,key,true);
 st.doc=doc;st.keys=keys;
}
function release(st){diffKeys(st,st.doc||document,[])}
function stFor(i){if(!state.has(i))state.set(i,{keys:new Set(),doc:document,buttons:[],nav:0,cur:null,last:0,context:''});return state.get(i)}
function pressed(g,i){return !!(g?.buttons?.[i]?.pressed||g?.buttons?.[i]?.value>.6)}
function axis(g,i){const n=g?.axes?.[i]||0;return Math.abs(n)>DEAD?n:0}
function once(st,g,i,fn){if(pressed(g,i)&&!st.buttons[i])fn()}
function tap(doc,key){k(doc,key,true);k(doc,key,false)}
function controls(g){return {
 left:pressed(g,14)||axis(g,0)<-.45,right:pressed(g,15)||axis(g,0)>.45,
 up:pressed(g,12)||axis(g,1)<-.45,down:pressed(g,13)||axis(g,1)>.45,
 gas:pressed(g,7)||axis(g,5)>.55,brake:pressed(g,6)||axis(g,2)<-.8}};
function buttons(doc){
 let root=doc.body;
 if(doc===document)root=$('#afLocalHub.open')||$('#afOnlineRoom.open')||$('#afLocalResults.open')||$('#afOptions:not([hidden])')||$('#afFront .afPanel.active')||$('#afFront')||doc.body;
 return [...root.querySelectorAll('button,a[href],select,[role="button"],input:not([type=hidden])')].filter(e=>e.getClientRects().length&&!e.disabled&&getComputedStyle(e).visibility!=='hidden'&&!e.closest('#afPadHelp,#afPadBadge,#afRivals'));
}
function focusNav(st,doc,dir){
 const all=buttons(doc);if(!all.length)return;
 const i=all.indexOf(focused);
 focused=all[(i<0?0:(i+dir+all.length)%all.length)];
 focused.focus({preventScroll:true});focused.scrollIntoView({block:'nearest',inline:'nearest'});
}
function cursorAt(st,doc,x,y,fire){
 if(!st.cur||st.cur.ownerDocument!==doc||!st.cur.isConnected){
  st.cur=doc.createElement('div');st.cur.id='afPadCursor';
  st.cur.style.cssText='position:fixed;z-index:2147480000;width:15px;height:15px;background:#53baf577;border:2px solid #ffffad;border-radius:50%;box-shadow:0 0 7px #049bff;pointer-events:none;transform:translate(-50%,-50%)';
  doc.body.append(st.cur);st.px=doc.defaultView.innerWidth/2;st.py=doc.defaultView.innerHeight/2;
 }
 st.px=Math.max(6,Math.min(doc.defaultView.innerWidth-6,st.px+x*18));
 st.py=Math.max(6,Math.min(doc.defaultView.innerHeight-6,st.py+y*18));
 st.cur.style.left=st.px+'px';st.cur.style.top=st.py+'px';
 if(fire){
  st.cur.style.display='none';
  const target=doc.elementFromPoint(st.px,st.py);
  st.cur.style.display='';
  if(target){const btn=target.closest('button,a,[role="button"],input');if(btn)click(btn);
  else target.dispatchEvent(new doc.defaultView.MouseEvent('click',{bubbles:true,cancelable:true,clientX:st.px,clientY:st.py}));}
 }
}
function back(m,doc){
 const picks={menu:['#afLocalBack','#afOnlineRoomClose','.afBack','#afBack'],
  ramp:['#rampMain','#modeSelect'],bags:['#bagMenu'],assist:['#assistMenu'],docs:['#docMenu'],
  cabin:['#cabinMenu'],marshal:['#mainMenu','#overMain']};
 for(let query of picks[m]||[])if(click((m==='marshal'?doc:document).querySelector(query)))return;
 if(m==='menu')click($('#afHome .afBack'));
}
function pause(m,doc){
 const look={ramp:'#pause',bags:'#bagPause',assist:'#pause',docs:'#pause',cabin:'#pause',marshal:'#pause'};
 if(click(doc.querySelector(look[m])))return;
 let host={assist:'assistHost',cabin:'cabinHost',docs:'docHost',marshal:'airHost'}[m];click($('#'+host+' .uPause'));
}
function gameplay(st,g,index,ctx){
 const doc=ctx.doc,m=ctx.id,c=controls(g);const l=axis(g,0),y=axis(g,1),rx=axis(g,2),ry=axis(g,3);
 let keys=[];
 if(m==='ramp'||m==='bags'||m==='assist'){
  if(c.left)keys.push(index===0?'a':'ArrowLeft');
  if(c.right)keys.push(index===0?'d':'ArrowRight');
  if(m==='bags'){
   if(c.up||pressed(g,2))keys.push(index===0?'w':'ArrowUp');
   if(c.gas||pressed(g,0)||c.down)keys.push(index===0?'s':'ArrowDown');
  }else{
   if(c.up||c.gas)keys.push(index===0?'w':'ArrowUp');
   if(c.down||c.brake)keys.push(index===0?'s':'ArrowDown');
  }
  if(m==='assist')keys=keys.map(k=>k.startsWith('Arrow')?k:({a:'ArrowLeft',d:'ArrowRight',w:'ArrowUp',s:'ArrowDown'}[k]));
 }else if(m==='marshal'){
  if(index!==0){release(st);return}
  if(y<-.48)keys.push('w');else if(y>.48)keys.push('s');
  if(l<-.48)keys.push('a');else if(l>.48)keys.push('d');
  if(pressed(g,4))keys.push('q');
  if(ry<-.48)keys.push('ArrowUp');else if(ry>.48)keys.push('ArrowDown');
  if(rx<-.48)keys.push('ArrowLeft');else if(rx>.48)keys.push('ArrowRight');
  if(pressed(g,5))keys.push('Enter');
 }else if(m==='cabin'){
  if(c.up)keys.push('ArrowUp');if(c.down)keys.push('ArrowDown');
 }
 if(m==='assist'&&index===1&&$('#assistFrame2')&&!$('#assistFrame2').hidden){
  try{const d=$('#assistFrame2').contentDocument;if(d)diffKeys(st,d,keys)}catch(e){}
 }else diffKeys(st,doc,keys);
 if(m==='marshal'){
  once(st,g,3,()=>tap(doc,'/'));
  once(st,g,0,()=>tap(doc,' '));
 }
 if(m==='bags'){once(st,g,2,()=>tap(doc,index===0?'w':'ArrowUp'))}
 if(m==='cabin'||m==='docs'){
  if(m==='docs'&&Math.abs(y)>.48&&Date.now()-st.nav>180){focusNav(st,doc,y>0?1:-1);st.nav=Date.now()}
  if(m==='docs'){
   once(st,g,2,()=>click(doc.querySelector('[data-decision="inquire"]')));
   once(st,g,3,()=>click(doc.querySelector('[data-decision="report"]')));
  }
  if(Math.abs(rx)>.12||Math.abs(ry)>.12)cursorAt(st,doc,rx,ry,false);
  once(st,g,0,()=>{if(!click(doc.activeElement))cursorAt(st,doc,0,0,true)});
  once(st,g,7,()=>cursorAt(st,doc,0,0,true));
  once(st,g,4,()=>{const tabs=[...doc.querySelectorAll('.tab:not(.locked)')],cur=tabs.indexOf(doc.querySelector('.tab.active'));click(tabs[Math.max(0,cur-1)])});
  once(st,g,5,()=>{const tabs=[...doc.querySelectorAll('.tab:not(.locked)')],cur=tabs.indexOf(doc.querySelector('.tab.active'));click(tabs[Math.min(tabs.length-1,cur+1)])});
 }
 once(st,g,9,()=>pause(m,doc));once(st,g,1,()=>back(m,doc));
}
function menu(st,g,index,doc){
 release(st);
 const cy=axis(g,1),cx=axis(g,0);
 if((pressed(g,13)||cy>.55)&&Date.now()-st.nav>200){focusNav(st,doc,1);st.nav=Date.now()}
 if((pressed(g,12)||cy<-.55)&&Date.now()-st.nav>200){focusNav(st,doc,-1);st.nav=Date.now()}
 if((pressed(g,14)||cx<-.55)&&Date.now()-st.nav>200){focusNav(st,doc,-1);st.nav=Date.now()}
 if((pressed(g,15)||cx>.55)&&Date.now()-st.nav>200){focusNav(st,doc,1);st.nav=Date.now()}
 if(Math.abs(axis(g,2))>.2||Math.abs(axis(g,3))>.2)cursorAt(st,doc,axis(g,2),axis(g,3),false);
 once(st,g,0,()=>{if(!click(doc.activeElement))cursorAt(st,doc,0,0,true)});
 once(st,g,7,()=>cursorAt(st,doc,0,0,true));
 once(st,g,1,()=>back('menu',doc));
 once(st,g,9,()=>window.dispatchEvent(new CustomEvent('af-controller-start',{detail:{index}})));
}
function tick(gps){
 const pads=Array.from(gps||[]).filter(g=>g?.connected!==false&&g?.buttons);
 connected=pads.length;
 const ctx=mode();
 for(let i=0;i<Math.min(4,pads.length);i++){
  const gp=pads[i],index=Number.isInteger(gp.index)?gp.index:i,st=stFor(index);
  if(ctx.id==='menu')menu(st,gp,index,ctx.doc);else gameplay(st,gp,index,ctx);
  st.buttons=gp.buttons.map(b=>!!(b?.pressed||b?.value>.6));
 }
 for(const [idx,st] of state)if(!pads.some(p=>(Number.isInteger(p.index)?p.index:0)===idx))release(st);
 if(lastMode!==ctx.id){lastMode=ctx.id;if(help)help.querySelector('#afPadGuide').textContent=info[ctx.id]}
 if(badge)badge.textContent=connected?'🎮 '+connected+' connected':'🎮 Connect Xbox controller';
 return{connected,mode:ctx.id};
}
function loop(){try{tick(navigator.getGamepads?.()||[])}catch(e){console.warn('Gamepad input:',e)}
 requestAnimationFrame(loop)}
function setup(){
 if(badge)return;
 badge=document.createElement('button');badge.id='afPadBadge';badge.type='button';
 badge.textContent='🎮 Connect Xbox controller';badge.setAttribute('aria-label','Xbox controller instructions');
 badge.style.cssText='position:fixed;top:6px;right:8px;z-index:4400;background:#0a3446e8;color:white;border:1px solid #8bdaf0;border-radius:7px;padding:5px 8px;font:700 11px system-ui;cursor:pointer';
 document.body.append(badge);
 help=document.createElement('div');help.id='afPadHelp';
 help.style.cssText='display:none;position:fixed;right:7px;top:42px;z-index:5000;width:min(315px,87vw);padding:12px;background:#052238f5;border:1px solid #67c8e9;border-radius:10px;color:white;box-shadow:0 9px 32px #000b;font:13px/1.4 system-ui';
 help.innerHTML='<b>🎮 XBOX CONTROLLER</b><button id="afPadClose" type="button" style="float:right;color:white;background:transparent;border:0">✕</button><p id="afPadGuide"></p><small>Works in Chrome/Edge over HTTPS via USB or Bluetooth. Press any gamepad button to activate.</small>';
 document.body.append(help);badge.onclick=()=>{help.style.display=help.style.display==='none'?'block':'none';help.querySelector('#afPadGuide').textContent=info[mode().id]};
 help.querySelector('#afPadClose').onclick=()=>help.style.display='none';
 const style=document.createElement('style');
 style.textContent='.afPadFocused{outline:3px solid #ffd45d!important;outline-offset:2px!important} @media(max-width:650px){#afPadBadge{top:auto!important;bottom:4px!important;right:4px!important;font-size:9px!important;opacity:.8}}';
 document.head.append(style);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();
window.AF_GAMEPAD={tick,status:()=>({connected,mode:lastMode}),maps:info};
requestAnimationFrame(loop);
})();