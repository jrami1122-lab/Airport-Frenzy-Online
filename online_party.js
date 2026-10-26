(()=>{'use strict';
const $=s=>document.querySelector(s),GAMES=[['ramp','Ramp Runner','🚜','#startSolo'],['bags','Bag Stacker','🧳','#startBagSolo'],['cabin','Flight Attendant','🛫','#startCabin'],['assist','Terminal Assist','♿','#startAssist'],['docs','Document Control','🛂','#startDocsSolo'],['marshal','Air Marshalling','🦺','#startMarshal']];
const game=k=>GAMES.find(g=>g[0]===k)||GAMES[0],safe=s=>String(s??'').replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
const css=document.createElement('style');css.textContent=[
'#afOnlineRoomOpen{display:block;width:100%;min-height:59px;margin:8px 0;padding:12px;border:2px solid #55cddd;border-radius:14px;background:#134255;color:#e9fbff;font:bold 19px system-ui;cursor:pointer}',
'#afOnlineRoomOpen small{display:block;font-size:10px;color:#b6e3ee;letter-spacing:.1em}',
'#afOnlineRoom{display:none;position:fixed;z-index:510;inset:0;justify-content:center;align-items:center;overflow:auto;padding:10px;background:#04111aed;backdrop-filter:blur(8px);touch-action:pan-y}',
'#afOnlineRoom.open{display:flex}',
'#afOnlineRoom .card{box-sizing:border-box;width:min(680px,100%);max-height:calc(100dvh - 20px);overflow-y:auto;touch-action:pan-y;padding:clamp(12px,3vw,22px);border:2px solid #7095a4;border-radius:17px;background:linear-gradient(145deg,#162c3b,#071723);color:#effaff;box-shadow:0 12px 50px #000e}',
'#afOnlineRoom h2{font:bold clamp(19px,4vw,27px) system-ui;color:#ffe4a3;margin:0}',
'#afOnlineRoom h3{font:bold 16px system-ui;color:#c9e9ee;margin:15px 0 9px}',
'#afOnlineRoom p{font:14px/1.45 system-ui;color:#c6d9df}',
'#afOnlineRoom button,#afOnlineRoom input,#afOnlineRoom select{box-sizing:border-box;min-height:42px;border:1px solid #678c99;border-radius:9px;padding:9px;font:600 15px system-ui}',
'#afOnlineRoom button{background:#205067;color:#f1ffff;cursor:pointer}',
'#afOnlineRoom button.primary{background:#ffd16c;color:#102230;font-weight:800}',
'#afOnlineRoom button:disabled{opacity:.4}',
'#afOnlineRoom input,#afOnlineRoom select{background:#081927;color:#fff;width:100%;min-width:0}',
'#afOnlineRoom .row{display:flex;flex-wrap:wrap;gap:8px;margin:11px 0;align-items:center}',
'#afOnlineRoom .row>*{flex:1 1 130px}',
'#afOnlineRoom .top{display:flex;align-items:center;justify-content:space-between;gap:8px}',
'#afOnlineRoom .top button{flex:0 0 auto}',
'#afOnlineRoom .roomcode{font:bold 25px ui-monospace,monospace;letter-spacing:.15em;color:#ffe0a3}',
'#afOnlineRoom .member{--pcolor:#4cd3ff;display:flex;align-items:center;justify-content:space-between;gap:6px;padding:9px;margin:8px 0;background:#071722;border-left:6px solid var(--pcolor);border-radius:9px}',
'#afOnlineRoom .member b{font:700 14px system-ui}',
'#afOnlineRoom .member small{display:block;color:#9dc1cd;font:12px system-ui}',
'#afOnlineRoom .dot{width:14px;height:14px;background:var(--pcolor);border-radius:50%;display:inline-block;margin-right:6px}',
'#afOnlineRoom .score{font:bold 13px ui-monospace,monospace;color:#ffdf96;white-space:nowrap}',
'#afOnlineRoom .note{padding:10px;border:1px solid #345967;border-radius:8px;background:#133344;font:13px/1.5 system-ui;color:#e1eefa}',
'#afOnlineRoomErr{font:12px system-ui;color:#ffc3b3;min-height:17px}',
'#afCrewDock{display:none;position:fixed;z-index:430;right:8px;top:max(56px,calc(env(safe-area-inset-top) + 55px));max-width:min(270px,75vw);border:2px solid var(--pcolor,#4cd3ff);border-radius:12px;background:#041928ed;color:#fff;padding:9px;box-shadow:0 8px 22px #000b;font:700 12px system-ui}',
'#afCrewDock.visible{display:block}#afCrewDock button{padding:7px 13px;margin:7px 4px 0 0;background:#174e62;color:#fff;border:1px solid #75aab6;border-radius:7px;font:700 12px system-ui}#afCrewDock .finish{background:#d9a94e;color:#12202a}',
'@media(max-width:400px){#afOnlineRoom{padding:4px}#afOnlineRoom .card{padding:10px;max-height:99dvh}#afOnlineRoom .roomcode{font-size:19px}}'
].join('\n');css.textContent+=`
/* Dedicated game selector: all six titles visible before any scrolling. */
#afGameJump{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;padding:8px 5px 11px;position:sticky;top:0;z-index:20;background:#092235f0;border-bottom:1px solid #43869d;box-shadow:0 6px 17px #0008;}
#afGameJump button{min-height:49px;min-width:0;padding:5px 3px;border:1px solid #49788d;border-radius:9px;background:#143449;color:#f5e8c5;font:700 12px/1.2 system-ui;overflow-wrap:anywhere;cursor:pointer;}
#afGameJump button span{display:block;font-size:11px;margin-top:3px;color:#d3edfa;}
#afGameJump button:focus-visible{outline:3px solid #f6d46d;outline-offset:2px;}
#afGameMount .afGameSpotlight{outline:3px solid #ffd34e;outline-offset:-4px;}
@media(max-width:370px){#afGameJump{gap:4px}#afGameJump button span{font-size:10px}}
`;document.head.appendChild(css);
const pane=document.createElement('div');pane.id='afOnlineRoom';pane.innerHTML='<div class="card"><div class="top"><h2>✈️ AIRPORT FRENZY ONLINE</h2><button id="afOnlineRoomClose">✕</button></div><div id="afOnlineRoomBody"></div><div id="afOnlineRoomErr"></div></div>';document.body.appendChild(pane);
const dock=document.createElement('div');dock.id='afCrewDock';document.body.appendChild(dock);
// Reuse the existing prominent Party Play button: adding a third large
// button made the new online mode invisible on short/mobile screens.
const launch=$('#partyPlay')||document.createElement('button');
const openLocalParty=launch.onclick;
launch.id='afOnlineRoomOpen';
launch.innerHTML='<small>2–4 PLAYERS · ONLINE ROOM</small>✈️ ONLINE PARTY PLAY <em>›</em>';
if(!launch.isConnected)($('#afFront .afMainButtons')||$('#afFront .afHome')||$('#afFront')||document.body).prepend(launch);
// Keep the original offline tournament reachable from the Online panel.
function localParty(){hide();if(typeof openLocalParty==='function'){openLocalParty.call(launch)}else{$('#afGames')?.classList.add('active');}}
// Every game must be discoverable immediately, even in a short mobile viewport.
const mount=$('#afGameMount');
if(mount&&!$('#afGameJump')){
 const jump=document.createElement('nav');jump.id='afGameJump';
 jump.setAttribute('aria-label','Choose one of six airport games');
 jump.innerHTML=GAMES.map(g=>'<button type="button" data-af-jump="'+g[0]+'" aria-label="Go to '+g[1]+'">'+g[2]+' <span>'+g[1]+'</span></button>').join('');
 mount.prepend(jump);
 jump.querySelectorAll('button').forEach(btn=>btn.onclick=()=>{
  const label=game(btn.dataset.afJump)[1];
  const card=[...mount.querySelectorAll('.gameChoice')].find(el=>el.querySelector('h2')?.textContent.includes(label));
  if(card){card.scrollIntoView({behavior:'smooth',block:'center'});card.classList.add('afGameSpotlight');setTimeout(()=>card.classList.remove('afGameSpotlight'),1100)}
 });
}
let socket=null,room=null,identity=null,token=null,playing=false,localFinished=false,startAt=0,reconnect=null;
let name=localStorage.getItem('afPlayerName')||'Player',lastCode='';
const mine=()=>room?.players?.find(x=>x.id===identity),host=()=>room?.host===identity,remaining=()=>Math.max(0,Math.ceil((room?.deadline||0)-Date.now()/1000));
function error(msg){$('#afOnlineRoomErr').textContent=msg}
function open(){pane.classList.add('open');render()}
function hide(){pane.classList.remove('open')}
function emit(o){if(socket?.readyState===WebSocket.OPEN)socket.send(JSON.stringify(o));else error('Connection unavailable')}
function connect(type,code='',reconnecting=false){
 if(!reconnecting){identity=null;token=null;room=null;sessionStorage.removeItem('afOnlineSession')}
 if(socket){socket.onclose=null;socket.close()}
 lastCode=code;
 const url=(location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/ws';const ws=new WebSocket(url);socket=ws;
 error('Connecting…');
 ws.onopen=()=>emit({type,code,name,token:reconnecting?token:null});
 ws.onmessage=e=>{let d;try{d=JSON.parse(e.data)}catch{return}
   if(d.type==='identity'){identity=d.id;token=d.token}
   if(d.type==='room'){
     const old=room;room=d;lastCode=d.code;sessionStorage.setItem('afOnlineSession',JSON.stringify({id:identity,token,code:d.code,name}));
     if(playing&&(old?.stage==='round'&&d.stage!=='round'||old?.game&&old.game!==d.game))stopGame();
     if(old?.index!==d.index)localFinished=false;
     error('');render();dockView();
   }else if(d.type==='error')error(d.message);
 };
 ws.onerror=()=>error('Unable to connect to party server.');
 ws.onclose=()=>{if(socket!==ws)return;if(room){error('Reconnecting…');clearTimeout(reconnect);reconnect=setTimeout(()=>connect('join',room.code,true),2500)}};
}
const player=p=>'<div class="member" style="--pcolor:'+safe(p.color)+'"><div><span class="dot"></span><b>'+safe(p.name)+(p.id===room.host?' 👑':'')+(p.id===identity?' (you)':'')+'</b><small>'+(p.online?'Connected':'Offline')+(p.eliminated?' · Eliminated':'')+(p.finished?' · Finished':'')+'</small></div><div class="score">'+p.pts+' PTS</div></div>';
function render(){
 if(!pane.classList.contains('open'))return;
 const body=$('#afOnlineRoomBody');if(!room){
 const param=new URL(location.href).searchParams.get('room')||lastCode;
 body.innerHTML='<p>Create a private crew room or join a friend. Each player uses a separate device.</p><label>YOUR NAME<input id="afName" maxlength="20" value="'+safe(name)+'"></label><div class="row"><button class="primary" id="afCreate">CREATE ROOM</button></div><div class="row"><input id="afCodeInput" placeholder="Six-character code" maxlength="6" value="'+safe(param)+'"><button id="afJoin">JOIN ROOM</button></div><p class="note">Live scoring · 2–4 players · unique crew colors · six original arcade games</p><div class="row"><button id="afOfflineParty">LOCAL PARTY PLAY (SAME DEVICE)</button></div>';
 $('#afCreate').onclick=()=>{name=$('#afName').value||'Player';localStorage.setItem('afPlayerName',name);connect('create')};
 $('#afJoin').onclick=()=>{name=$('#afName').value||'Player';localStorage.setItem('afPlayerName',name);const code=$('#afCodeInput').value.trim().toUpperCase();if(code.length!==6){error('Enter all six characters.');return}connect('join',code)};
 $('#afOfflineParty').onclick=localParty;
 return;
 }
 const players=room.players.slice().sort((a,b)=>b.pts-a.pts);
 let section='';
 if(room.stage==='lobby'){
 section='<h3>CREW LOBBY · '+players.length+'/4</h3>'+players.map(player).join('')+'<div class="row"><button id="afTournament" '+(!host()?'disabled':'')+' class="'+(room.mode==='tournament'?'primary':'')+'">🏆 TOURNAMENT</button><button id="afSingle" '+(!host()?'disabled':'')+' class="'+(room.mode==='single'?'primary':'')+'">🎮 SINGLE GAME</button></div>';
 if(room.mode==='single')section+='<label>GAME<select id="afGameSelect" '+(!host()?'disabled':'')+'>'+GAMES.map(g=>'<option value="'+g[0]+'" '+(room.preferredGame===g[0]?'selected':'')+'>'+g[2]+' '+g[1]+'</option>').join('')+'</select></label>';
 section+='<p class="note">Six-game rotation: after Game 4, anyone still on zero points is eliminated. Top score after Game 6 wins. A tie triggers a best-of-three playoff.</p>';
 section+=host()?'<button id="afStart" class="primary" '+(players.length<2?'disabled':'')+'>START '+(room.mode==='single'?'GAME':'TOURNAMENT')+'</button>':'<p>Waiting for host to start…</p>';
 }else if(room.stage==='round'){
 const info=game(room.game),active=!mine()?.eliminated&&(!room.tiebreak||room.tiebreakPlayers.includes(identity));
 section='<h3>'+(room.tiebreak?'PLAYOFF '+room.tiebreakRound:room.mode==='single'?'SINGLE GAME':'GAME '+(room.index+1)+'/6')+' · '+info[2]+' '+info[1]+'</h3><p>⏱ <b id="afTime">'+remaining()+'</b> seconds left. All players compete on their own devices.</p>'+players.map(p=>player(p).replace(p.pts+' PTS',p.score+' SCORE')).join('');
 section+=active&&!mine()?.finished?'<button class="primary" id="afPlay">'+(playing?'RETURN TO GAME':'PLAY THIS GAME')+'</button><p>Finish your attempt from the crew panel inside the game.</p>':'<p class="note">Waiting for active crew members to finish.</p>';
 }else if(room.stage==='results'){
 section='<h3>GAME '+(room.index+1)+' RESULTS</h3>'+(room.results||[]).map(r=>{const p=players.find(x=>x.id===r.id);return p?player(p).replace(p.pts+' PTS',r.score+' · +'+(room.tiebreak?0:r.earned)+' PTS'):''}).join('')+'<h3>OVERALL</h3>'+players.map(player).join('');
 if(room.mode==='tournament'&&room.index===3)section+='<p class="note">Game 4 elimination: players remaining at zero total points are out.</p>';
 section+=host()?'<button class="primary" id="afNext">NEXT GAME</button>':'<p>Waiting for host…</p>';
 }else if(room.stage==='tiebreak_ready'){
 section='<h3>BEST-OF-THREE PLAYOFF</h3><p>Tied leaders play up to three tiebreakers. First to two wins takes the trophy; unresolved ties continue in sudden death.</p>'+players.filter(p=>room.tiebreakPlayers.includes(p.id)).map(player).join('')+(host()?'<button class="primary" id="afNext">START PLAYOFF</button>':'<p>Waiting for host…</p>');
 }else if(room.stage==='finished'){
 section='<h3>🏆 CHAMPION: '+safe(players.find(p=>p.id===room.winner)?.name||'Crew')+'</h3>'+players.map(player).join('')+(host()?'<button id="afRematch" class="primary">PLAY ANOTHER MATCH</button>':'');
 }
 body.innerHTML='<div class="row"><span class="roomcode">'+safe(room.code)+'</span><button id="afInvite">COPY INVITE LINK</button></div>'+section+'<div class="row"><button id="afLeave">LEAVE ROOM</button></div>';
 $('#afInvite').onclick=()=>{const u=location.origin+'/?room='+room.code;navigator.clipboard?.writeText(u).then(()=>error('Invite link copied.'),()=>error(u))||error(u)};
 $('#afTournament')?.addEventListener('click',()=>emit({type:'configure',mode:'tournament',game:'ramp'}));
 $('#afSingle')?.addEventListener('click',()=>emit({type:'configure',mode:'single',game:'ramp'}));
 $('#afGameSelect')?.addEventListener('change',e=>emit({type:'configure',mode:'single',game:e.target.value}));
 $('#afStart')?.addEventListener('click',()=>emit({type:'start'}));
 $('#afPlay')?.addEventListener('click',()=>playing?hide():playGame());
 $('#afNext')?.addEventListener('click',()=>emit({type:'next'}));
 $('#afRematch')?.addEventListener('click',()=>emit({type:'rematch'}));
 $('#afLeave').onclick=leave;
}
function num(v){const x=parseInt(String(v??'0').replace(/[^\d]/g,''),10);return Number.isFinite(x)?Math.min(10000000,Math.max(0,x)):0}
function measured(){
 try{
 const g=room?.game;if(!g)return 0;
 if(g==='ramp')return num($('#score')?.textContent);
 if(g==='bags')return num(window.__AF_BAG_SCORE?.());
 const frame={cabin:'#cabinFrame',assist:'#assistFrame',docs:'#docFrame',marshal:'#airFrame'}[g],doc=$(frame)?.contentDocument;
 if(!doc)return 0;
 return g==='marshal'?Math.max(0,num(doc.querySelector('#round')?.textContent)-1):num(doc.querySelector('#score')?.textContent);
 }catch(e){console.warn(e);return 0}
}
function playGame(){
 if(room?.stage!=='round'||mine()?.eliminated||mine()?.finished)return;
 const info=game(room.game),b=$(info[3]);if(!b){error('This game could not be launched.');return}
 playing=true;localFinished=false;startAt=Date.now();hide();$('#afFront')?.classList.add('playing');b.click();dockView();
}
function stopGame(){
 if(!playing)return;playing=false;
 try{
 const button={ramp:'#rampMain',bags:'#bagMenu',cabin:'#cabinMenu',assist:'#assistMenu',docs:'#docMenu'}[room?.game];
 if(button)$(button)?.click();
 if(room?.game==='marshal')$('#airFrame')?.contentDocument?.querySelector('#mainMenu')?.click();
 }catch(e){console.warn(e)}
 $('#intro')?.classList.remove('hide');$('#afFront')?.classList.remove('playing');dockView();
}
function finish(){
 if(!playing||localFinished||room?.stage!=='round')return;
 if(Date.now()-startAt<3000){error('Play for at least three seconds.');open();return}
 const score=measured();localFinished=true;emit({type:'finish',score});stopGame();open();
}
function dockView(){
 const on=!!room&&room.stage==='round'&&playing&&!localFinished;dock.classList.toggle('visible',on);if(!on)return;
 dock.style.setProperty('--pcolor',mine()?.color||'#4cd3ff');
 dock.innerHTML='<div>● '+safe(mine()?.name)+' · '+(room.tiebreak?'PLAYOFF':'GAME '+(room.index+1))+'</div><div>⏱ '+remaining()+'s · SCORE '+measured()+'</div><button id="afDockRoom">ROOM</button><button id="afDockFinish" class="finish">FINISH</button>';
 $('#afDockRoom').onclick=open;$('#afDockFinish').onclick=finish;
}
function leave(){
 emit({type:'leave'});stopGame();room=null;identity=null;token=null;lastCode='';clearTimeout(reconnect);sessionStorage.removeItem('afOnlineSession');
 if(socket){socket.onclose=null;socket.close();socket=null}
 const u=new URL(location.href);u.searchParams.delete('room');history.replaceState(null,'',u);hide();dockView();
}
$('#afOnlineRoomClose').onclick=hide;launch.onclick=open;
setInterval(()=>{if(room?.stage==='round'){if(playing&&!localFinished){emit({type:'score',score:measured()});dockView()}if($('#afTime'))$('#afTime').textContent=remaining();}},1000);
window.__AF_ONLINE={open,getState:()=>({room,identity,playing,score:measured()})};
const query=new URL(location.href).searchParams.get('room');if(query){open();try{const data=JSON.parse(sessionStorage.getItem('afOnlineSession')||'{}');if(data.code===query&&data.token){token=data.token;identity=data.id;name=data.name||name;connect('join',query,true)}}catch(e){}}
})();