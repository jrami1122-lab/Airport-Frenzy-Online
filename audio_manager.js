/* Airport Frenzy sound director. MP3 assets are served from /assets/audio/. */
(()=>{'use strict';if(window.AF_AUDIO)return;
const file={menu:'music_menu',arcade:'music_arcade',cabin:'music_cabin',calm:'music_calm',thump:'sfx_thump',
 bag:'sfx_bag_drop',crash:'sfx_crash',wrong:'sfx_wrong',ding:'sfx_ding',plane:'sfx_flyover',motor:'sfx_motor'};
const src=k=>'/assets/audio/'+file[k]+'.mp3';
const sets={ramp:['arcade','menu'],bags:['arcade','menu'],marshal:['arcade','calm'],cabin:['cabin','calm'],assist:['calm','menu'],docs:['calm','cabin'],menu:['menu','calm','arcade','cabin']};
let enabled=true,musicEnabled=true,fxEnabled=true,unlocked=false,mode='menu',current=null,engine=null,queue=0,playIndex=0,last={},volMusic=.24,volFx=.46;
const tryPlay=a=>{if(a)a.play().catch(()=>{});};
function effect(k,{gain=1,cooldown=180}={}){if(!unlocked||!enabled||!fxEnabled||document.hidden||!file[k])return;
 const now=performance.now();if(now-(last[k]||0)<cooldown)return;last[k]=now;
 const a=new Audio(src(k));a.volume=Math.min(1,volFx*gain);tryPlay(a);a.onended=()=>{a.src='';};return a;}
function nextTrack(){const tracks=sets[mode]||sets.menu;playIndex=(playIndex+1)%tracks.length;music(tracks[playIndex]);}
function music(k){if(!unlocked||!enabled||!musicEnabled||document.hidden||!file[k])return;
 const old=current;if(old?.dataset?.afTrack===k&&!old.paused)return;
 const a=new Audio(src(k));a.dataset.afTrack=k;a.volume=0;current=a;tryPlay(a);
 a.onended=()=>{if(current===a)nextTrack();};
 let x=0;clearInterval(queue);queue=setInterval(()=>{x=Math.min(1,x+.12);a.volume=x*volMusic;
 if(old){old.volume=Math.max(0,(1-x)*volMusic);if(x===1){old.pause();old.src='';}}
 if(x===1)clearInterval(queue);},55);}
function motor(on){if(!on){if(engine){engine.pause();engine.src='';engine=null;}return;}
 if(!unlocked||!enabled||!fxEnabled||engine)return;engine=new Audio(src('motor'));engine.loop=true;engine.volume=volFx*.22;tryPlay(engine);}
function game(g){mode=sets[g]?g:'menu';playIndex=0;motor(['ramp','bags','assist'].includes(mode));
 music((sets[mode]||sets.menu)[0]);}
function unlock(){if(unlocked)return;unlocked=true;game(mode);
 document.removeEventListener('pointerdown',unlock,true);document.removeEventListener('keydown',unlock,true);}
document.addEventListener('pointerdown',unlock,true);document.addEventListener('keydown',unlock,true);
const starts={startSolo:'ramp',startVersus:'ramp',startBagSolo:'bags',startBagVersus:'bags',startCabin:'cabin',
 startAssist:'assist',startDocsSolo:'docs',startMarshal:'marshal'};
document.addEventListener('click',e=>{const b=e.target.closest?.('button');if(!b)return;
 if(starts[b.id]){game(starts[b.id]);effect('ding',{gain:.35,cooldown:300});}
 else if(['rampMain','bagMenu','cabinMenu','assistMenu','docMenu','afLeave','mainMenu'].includes(b.id))game('menu');
},true);
// Bag Stacker: physical baggage placement deserves a short soft thunk.
document.addEventListener('pointerup',e=>{
 if(mode==='bags'&&e.target.closest?.('#bagCanvas,#bagGame canvas'))effect('bag',{gain:.5,cooldown:250});
},true);
// Track genuine positive/negative score changes in the embedded airport jobs.
// Sound comes from changes to game state, not every tap on the UI.
const watched=new WeakSet(),scoreHistory=new WeakMap();
function monitorScore(doc,g){
 if(!doc||watched.has(doc))return;watched.add(doc);
 const score=doc.getElementById('score');
 if(!score)return;
 let lastNumber=null;
 const scan=()=>{
  if(mode!==g)return;
  const n=Number((score.textContent||'').replace(/[^0-9.-]/g,''));
  if(!Number.isFinite(n))return;
  if(lastNumber!==null&&n!==lastNumber){
   if(n>lastNumber)effect('ding',{gain:.45,cooldown:600});
   else if(n<lastNumber)effect('wrong',{gain:.35,cooldown:750});
  }lastNumber=n;
 };
 const watcher=new MutationObserver(scan);watcher.observe(score,{subtree:true,characterData:true,childList:true});scan();
}
const frames={cabin:'cabinFrame',assist:'assistFrame',docs:'docFrame',marshal:'airFrame'};
function watchFrames(){
 for(const [g,id] of Object.entries(frames)){
  const frame=document.getElementById(id);if(!frame)continue;
  try{monitorScore(frame.contentDocument,g)}catch(e){}
  if(!frame.dataset.afSoundWatch){frame.dataset.afSoundWatch='1';frame.addEventListener('load',()=>{try{monitorScore(frame.contentDocument,g)}catch(e){}})}
 }
}
setInterval(watchFrames,1300);
document.addEventListener('visibilitychange',()=>{if(document.hidden){current?.pause();engine?.pause()}
 else if(enabled&&unlocked){tryPlay(current);tryPlay(engine)}});
function setEnabled(v){enabled=!!v;setMusicEnabled(enabled);setEffectsEnabled(enabled)}
function setMusicEnabled(v){
 musicEnabled=!!v;if(!musicEnabled)current?.pause();
 else if(unlocked)music((sets[mode]||sets.menu)[playIndex]||'menu');
 const btn=document.getElementById('optionMusic');
 if(btn){btn.textContent=musicEnabled?'ON':'OFF';btn.setAttribute('aria-pressed',String(musicEnabled))}
}
function setEffectsEnabled(v){
 fxEnabled=!!v;if(!fxEnabled)motor(false);
 else if(unlocked&&['ramp','bags','assist'].includes(mode))motor(true);
 const btn=document.getElementById('optionSfx');
 if(btn){btn.textContent=fxEnabled?'ON':'OFF';btn.setAttribute('aria-pressed',String(fxEnabled))}
}
function attach(){
 if(document.getElementById('afSoundTray'))return;
 const options=document.getElementById('afOptions'),card=options?.querySelector('.optionsCard');
 if(!card)return;
 const tray=document.createElement('section');tray.id='afSoundTray';
 tray.style.cssText='position:static;border:1px solid #497e99;border-radius:10px;background:#081e30;color:#d5edf9;padding:10px;margin:10px 0;font:12px system-ui;display:grid;gap:7px';
 tray.innerHTML='<strong style="font-size:13px">🎵 SOUNDTRACK SETTINGS</strong>'+
 '<label style="display:grid;gap:3px">Music volume <input aria-label="Music volume" id="afMusicVolume" type="range" min="0" max="100" value="24"></label>'+
 '<label style="display:grid;gap:3px">Effects volume <input aria-label="Effects volume" id="afFxVolume" type="range" min="0" max="100" value="46"></label>'+
 '<button id="afNextMusic" type="button" style="background:#23526b;color:white;border:1px solid #6aafce;border-radius:7px;padding:8px">NEXT TRACK</button>';
 card.insertBefore(tray,card.querySelector('#optionsDone'));
 const optionsMusic=options.querySelector('#optionMusic');
 const optionsSfx=options.querySelector('#optionSfx');
 if(optionsMusic){optionsMusic.onclick=()=>setMusicEnabled(!musicEnabled);
 const t=optionsMusic.closest('.optionRow')?.querySelector('small');if(t)t.textContent='Uploaded airport music playlist'}
 if(optionsSfx){optionsSfx.onclick=()=>setEffectsEnabled(!fxEnabled);
 const t=optionsSfx.closest('.optionRow')?.querySelector('small');if(t)t.textContent='Game cues, engines and notifications'}
 tray.querySelector('#afMusicVolume').oninput=e=>{volMusic=+e.target.value/100;if(current)current.volume=volMusic};
 tray.querySelector('#afFxVolume').oninput=e=>{volFx=+e.target.value/100;if(engine)engine.volume=volFx*.22};
 tray.querySelector('#afNextMusic').onclick=nextTrack;
 setMusicEnabled(musicEnabled);setEffectsEnabled(fxEnabled);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',attach,{once:true});else attach();
window.AF_AUDIO={effect,music,motor,game,unlock,setEnabled,setMusicEnabled,setEffectsEnabled,tracks:file};
})();