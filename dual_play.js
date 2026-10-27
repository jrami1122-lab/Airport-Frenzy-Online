/* True dual-frame local play for minigames with a self-contained HTML game.
   Each device/controller operates its own live simulation and score. */
(()=>{'use strict';if(window.AF_DUAL)return;
const $=q=>document.querySelector(q);
const hosts={cabin:['#cabinHost','#cabinFrame'],docs:['#docHost','#docFrame'],marshal:['#airHost','#airFrame']};
let active=null,second=null,first=null,host=null;
function cleanup(){
 if(host)host.classList.remove('afTwoPlayer');
 second?.remove();second=null;first=null;host=null;active=null;
}
function mount(id){
 cleanup();const pair=hosts[id];if(!pair)return false;
 host=$(pair[0]);first=$(pair[1]);
 if(!host||!first||host.hidden)return false;
 second=document.createElement('iframe');second.id='afLocalP2Frame';
 second.title='Airport Frenzy · Player 2 · '+id;
 second.setAttribute('allow','fullscreen');
 second.srcdoc=first.srcdoc;
 host.append(second);
 host.classList.add('afTwoPlayer');
 active=id;
 return true;
}
function doc(player){if(!active)return null;const frame=player===1?second:first;
 try{return frame?.contentDocument||null}catch(e){return null}}
function score(player){const d=doc(player);if(!d)return 0;
 const str=d.querySelector('#score')?.textContent||'0';
 return Math.max(0,parseInt(str.replace(/[^\d-]/g,''),10)||0)}
function setup(){
 const style=document.createElement('style');style.id='afDualPlayCSS';
 style.textContent='.cabinHost.afTwoPlayer{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;grid-template-rows:minmax(0,1fr)!important;align-items:stretch!important;gap:3px!important;padding:40px 4px 5px!important;overflow:hidden!important}.cabinHost.afTwoPlayer iframe{display:block!important;min-width:0!important;width:100%!important;height:100%!important;border:2px solid #5ebcdb!important;border-radius:8px!important;box-sizing:border-box!important}.cabinHost.afTwoPlayer iframe#afLocalP2Frame{border-color:#ffd576!important}.cabinHost.afTwoPlayer .cabinMenu{position:absolute!important;left:10px!important;top:4px!important;z-index:80!important;min-height:32px!important;padding:5px 12px!important}.cabinHost.afTwoPlayer:before{content:"P1";position:absolute;top:10px;left:43%;z-index:70;color:#73dfff;font:900 13px system-ui}.cabinHost.afTwoPlayer:after{content:"P2";position:absolute;top:10px;right:19%;z-index:70;color:#ffda7b;font:900 13px system-ui}@media(max-width:767px){.cabinHost.afTwoPlayer{display:block!important}.cabinHost.afTwoPlayer #afLocalP2Frame{display:none!important}}';
 document.head.append(style);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();
window.AF_DUAL={mount,cleanup,doc,score,isActive:()=>!!active,game:()=>active};
})();