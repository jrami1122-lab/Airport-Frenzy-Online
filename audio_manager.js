/* Airport Frenzy sound director. MP3 assets are served from /assets/audio/. */
(()=>{'use strict';if(window.AF_AUDIO)return;
const file={menu:'music_menu',arcade:'music_arcade',cabin:'music_cabin',calm:'music_calm',thump:'sfx_thump',
 bag:'sfx_bag_drop',crash:'sfx_crash',wrong:'sfx_wrong',ding:'sfx_ding',plane:'sfx_flyover',motor:'sfx_motor'};
const src=k=>'/assets/audio/'+file[k]+'.mp3';
const sets={ramp:['arcade','menu'],bags:['arcade','menu'],marshal:['arcade','calm'],cabin:['cabin','calm'],assist:['calm','menu'],docs:['calm','cabin'],menu:['menu','calm','arcade','cabin']};
let enabled=true,unlocked=false,mode='menu',current=null,engine=null,queue=0,playIndex=0,last={},volMusic=.24,volFx=.46;
const tryPlay=a=>{if(a)a.play().catch(()=>{});};
function effect(k,{gain=1,cooldown=180}={}){if(!unlocked||!enabled||document.hidden||!file[k])return;
 const now=performance.now();if(now-(last[k]||0)<cooldown)return;last[k]=now;
 const a=new Audio(src(k));a.volume=Math.min(1,volFx*gain);tryPlay(a);a.onended=()=>{a.src='';};return a;}
function nextTrack(){const tracks=sets[mode]||sets.menu;playIndex=(playIndex+1)%tracks.length;music(tracks[playIndex]);}
function music(k){if(!unlocked||!enabled||document.hidden||!file[k])return;
 const old=current;if(old?.dataset?.afTrack===k&&!old.paused)return;
 const a=new Audio(src(k));a.dataset.afTrack=k;a.volume=0;current=a;tryPlay(a);
 a.onended=()=>{if(current===a)nextTrack();};
 let x=0;clearInterval(queue);queue=setInterval(()=>{x=Math.min(1,x+.12);a.volume=x*volMusic;
 if(old){old.volume=Math.max(0,(1-x)*volMusic);if(x===1){old.pause();old.src='';}}
 if(x===1)clearInterval(queue);},55);}
function motor(on){if(!on){if(engine){engine.pause();engine.src='';engine=null;}return;}
 if(!unlocked||!enabled||engine)return;engine=new Audio(src('motor'));engine.loop=true;engine.volume=volFx*.22;tryPlay(engine);}
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
document.addEventListener('visibilitychange',()=>{if(document.hidden){current?.pause();engine?.pause()}
 else if(enabled&&unlocked){tryPlay(current);tryPlay(engine)}});
function setEnabled(v){enabled=!!v;if(!enabled){current?.pause();motor(false)}
 else if(unlocked)game(mode);const btn=document.querySelector('#afAudioToggle');if(btn)btn.textContent=enabled?'🔊':'🔇';}
function attach(){
 if(document.getElementById('afAudioToggle'))return;
 const tray=document.createElement('div');tray.id='afSoundTray';
 tray.style.cssText='position:fixed;left:8px;bottom:calc(7px + env(safe-area-inset-bottom));z-index:10500;display:flex;align-items:center;gap:4px;color:#dff3ff;background:#05253ae0;padding:3px;border-radius:8px;font:12px system-ui;';
 tray.innerHTML='<button type="button" id="afAudioToggle" aria-label="Toggle game audio" style="background:#123b53;color:white;border:1px solid #8ce7fb;border-radius:8px;padding:7px;min-height:34px;cursor:pointer">🔊</button><details style="padding:3px"><summary style="cursor:pointer">Audio</summary><label style="display:block">Music <input type="range" id="afMusicVolume" min="0" max="100" value="24"></label><label style="display:block">Effects <input type="range" id="afFxVolume" min="0" max="100" value="46"></label><button id="afNextMusic" type="button">Next song</button></details>';
 document.body.append(tray);tray.querySelector('#afAudioToggle').onclick=()=>setEnabled(!enabled);
 tray.querySelector('#afMusicVolume').oninput=e=>{volMusic=+e.target.value/100;if(current)current.volume=volMusic};
 tray.querySelector('#afFxVolume').oninput=e=>{volFx=+e.target.value/100;if(engine)engine.volume=volFx*.22};
 tray.querySelector('#afNextMusic').onclick=nextTrack;
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',attach,{once:true});else attach();
window.AF_AUDIO={effect,music,motor,game,unlock,setEnabled,tracks:file};
})();