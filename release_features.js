/* Installable, fullscreen-capable Airport Frenzy and safe keyboard input. */
(()=>{'use strict';if(window.AF_RELEASE)return;
const $=s=>document.querySelector(s);let installPrompt=null;
const editing=el=>!!el?.closest?.('input:not([type=range]),textarea,[contenteditable="true"],[role="textbox"],select');
function toast(msg){let e=$('#afReleaseToast');if(!e){e=document.createElement('div');e.id='afReleaseToast';
e.style.cssText='position:fixed;left:50%;bottom:12px;transform:translateX(-50%);max-width:90vw;background:#082e45f2;color:white;padding:9px 14px;border:1px solid #74dcf1;border-radius:12px;z-index:30002;font:12px system-ui;pointer-events:none;text-align:center';document.body.append(e)}
e.textContent=msg;clearTimeout(e.timer);e.timer=setTimeout(()=>e.remove(),3300)}
async function fullscreen(){try{if(document.fullscreenElement)await document.exitFullscreen();else if(document.documentElement.requestFullscreen)await document.documentElement.requestFullscreen();else toast('On iOS, install to Home Screen for fullscreen play.')}catch(e){toast('Fullscreen is unavailable in this browser.')}}
function fullButtons(){
for(const [parent,id] of [[$('#afOptions .optionsCard'),'afFullOptions'],[$('#afPadPauseMenu .padCard'),'afFullPause']]){
if(!parent||$('#'+id))continue;const b=document.createElement('button');b.id=id;b.type='button';b.textContent='ENTER FULL SCREEN';
b.style.cssText='display:block;width:calc(100% - 12px);min-height:40px;background:#174967;color:white;border:1px solid #6fbdde;border-radius:10px;margin:7px;padding:7px 12px;cursor:pointer;font:bold 12px system-ui';
b.onclick=fullscreen;parent.insertBefore(b,$(id==='afFullPause'?'#afPauseFinish':'#optionsDone'))}}
async function install(){
if(matchMedia('(display-mode:standalone)').matches||navigator.standalone){toast('Airport Frenzy is already installed.');return}
if(installPrompt){installPrompt.prompt();try{const c=await installPrompt.userChoice;if(c?.outcome==='accepted')installPrompt=null}catch(e){}return}
toast(/iPhone|iPad|iPod/.test(navigator.userAgent)?'Safari Share → Add to Home Screen → Add':'Browser menu → Install app / Add to Home Screen')}
function setup(){
const css=document.createElement('style');
css.textContent='#afPadBadge{display:none!important}#afReleaseInstall{background:#19586a!important;border:1px solid #71cce4!important;color:white!important;min-height:39px!important;padding:8px 12px!important;border-radius:12px!important;font-size:clamp(12px,2.2vw,15px)!important}#afFront .afHome{max-width:100vw!important}@media(max-height:480px) and (orientation:landscape){#afReleaseInstall{min-height:28px!important;padding:4px!important}#afFront .afMainButtons{max-height:calc(100dvh - 80px)!important;overflow-y:auto!important}}';
document.head.append(css);
const holder=$('#afHome .afMainButtons')||$('#afHome')||$('#afFront');
if(holder&&!$('#afReleaseInstall')){const b=document.createElement('button');b.id='afReleaseInstall';b.type='button';b.innerHTML='<small>ADD TO YOUR DEVICE</small>📲 INSTALL APP';holder.appendChild(b);b.onclick=install}
fullButtons();const options=$('#afOptions'),pause=$('#afPadPauseMenu');
const watcher=new MutationObserver(fullButtons);
if(options)watcher.observe(options,{childList:true,subtree:true});
if(pause)watcher.observe(pause,{childList:true,subtree:true});
document.addEventListener('fullscreenchange',()=>{for(const id of ['afFullOptions','afFullPause']){const b=$('#'+id);if(b)b.textContent=document.fullscreenElement?'EXIT FULL SCREEN':'ENTER FULL SCREEN'}});
window.addEventListener('keydown',e=>{if(editing(e.target))e.stopImmediatePropagation()},true);
window.addEventListener('keyup',e=>{if(editing(e.target))e.stopImmediatePropagation()},true);
if('serviceWorker' in navigator)navigator.serviceWorker.register('/service-worker.js').catch(()=>{});
}
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();installPrompt=e});
window.AF_RELEASE={install,toggleFullscreen:fullscreen,toast};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();
})();