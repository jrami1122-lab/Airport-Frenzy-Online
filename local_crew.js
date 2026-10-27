/* Local Party/Casual UI, saved scores, timed rounds, controller joining. */
(()=>{'use strict';if(window.AF_LOCAL)return;
const $=s=>document.querySelector(s);
const games=[['ramp','Ramp Runner','🚜','#startSolo','#startVersus'],['bags','Bag Stacker','🧳','#startBagSolo','#startBagVersus'],['cabin','Flight Attendant','🛫','#startCabin'],['assist','Terminal Assist','♿','#startAssist','#startAssistVersus'],['docs','Document Control','🛂','#startDocsSolo'],['marshal','Air Marshalling','🦺','#startMarshal']];
const colors=['#53d5ff','#ffcf54','#ff7281','#ab91ff'],DURATION=120,STORE='af-local-statistics-v2';
let stats={};try{stats=JSON.parse(localStorage.getItem(STORE)||'{}')||{}}catch(e){}
let mode='party',humans=1,cpus=1,rounds=6,selection='ramp',session=null,single=null,clock=null,deadline=0,connectedPads=new Set();
const save=()=>{try{localStorage.setItem(STORE,JSON.stringify(stats))}catch(e){}};
const isMobile=()=>window.innerWidth<768;
const byId=id=>games.find(g=>g[0]===id);
const num=s=>Number.parseInt(String(s||'0').replace(/[^\d-]/g,''),10)||0;
function score(game,p=0){try{
 if(game[0]==='ramp')return num(p?$('#afRampP2Score')?.textContent:$('#score')?.textContent);
 if(game[0]==='bags')return +(window.__AF_BAG_SCORES?.()?.[p]??(p?0:window.__AF_BAG_SCORE?.()))||0;
 const id=game[0]==='assist'&&p?'assistFrame2':{cabin:'cabinFrame',assist:'assistFrame',docs:'docFrame',marshal:'airFrame'}[game[0]];
 return Math.max(0,num($('#'+id)?.contentDocument?.querySelector('#score')?.textContent));
 }catch(e){return 0}}
function record(game,name,val){
 const id=name+' / '+game[1];const x=stats[id]||{plays:0,total:0,best:0};
 x.plays++;x.total+=val;x.last=val;x.best=Math.max(x.best,val);x.date=new Date().toISOString();stats[id]=x;save();
}
function statsView(){
 const el=$('#afLocalStats');if(!el)return;
 const a=Object.entries(stats).filter(x=>x[1]?.plays).sort((a,b)=>(b[1].date||'').localeCompare(a[1].date||'')).slice(0,6);
 el.innerHTML=a.length?a.map(([n,p])=>'<div><b>'+n+'</b><small>BEST '+p.best+' · '+p.plays+' SHIFTS</small></div>').join(''):'<p>Play a shift to save your first result.</p>';
}
function timer(showLabel){
 const e=$('#afShiftClock');e.classList.add('visible');$('#afShiftLabel').textContent=showLabel;
 deadline=Date.now()+DURATION*1000;clearInterval(clock);clock=setInterval(()=>{
  const v=Math.max(0,Math.ceil((deadline-Date.now())/1000));
  $('#afShiftTime').textContent=Math.floor(v/60)+':'+String(v%60).padStart(2,'0');
  if(!v)endShift();
 },200);
}
function clearTimer(){clearInterval(clock);clock=null;$('#afShiftClock').classList.remove('visible')}
function leaveGame(){
 if($('#bagGame')&&!$('#bagGame').hidden)$('#bagMenu')?.click();
 else if($('#assistHost')&&!$('#assistHost').hidden)$('#assistMenu')?.click();
 else if($('#cabinHost')&&!$('#cabinHost').hidden)$('#cabinMenu')?.click();
 else if($('#docHost')&&!$('#docHost').hidden)$('#docMenu')?.click();
 else if($('#airHost')&&!$('#airHost').hidden){try{$('#airFrame').contentDocument.querySelector('#mainMenu')?.click()}catch(e){}}
 else $('#rampMain')?.click();
 $('#afFront')?.classList.remove('playing');
}
function launch(game,shared){
 const btn=$(shared&&game[4]?game[4]:game[3]);if(!btn)return false;
 $('#afFront')?.classList.add('playing');btn.click();
 if(game[0]==='assist'||game[0]==='marshal'){
  const f=$(game[0]==='assist'?'#assistFrame':'#airFrame');
  f?.addEventListener('load',()=>{try{f.contentDocument?.querySelector('#begin')?.click()}catch(e){}},{once:true});
 }
 return true;
}
function resultPage(markup){$('#afLocalResultsBody').innerHTML=markup;$('#afLocalResults').classList.add('open')}
function dismiss(){$('#afLocalResults').classList.remove('open')}
function runTurn(){
 const s=session;if(!s)return;
 const game=s.games[s.round],people=s.players.filter(p=>p.human);
 if(s.cursor>=people.length){completeRound();return}
 const shared=people.length===2&&s.cursor===0&&!!game[4]&&!isMobile();
 s.shared=shared;
 const player=people[s.cursor];
 if(!launch(game,shared))return resultPage('<h2>Game unavailable</h2>');
 timer((shared?'P1 + P2':player.name)+' · '+game[1]);
}
function endShift(){
 if(!clock)return;
 clearTimer();
 if(single){
  const g=single,val=score(g);
  record(g,'P1',val);single=null;leaveGame();statsView();
  resultPage('<h2>'+g[2]+' '+g[1]+' · SHIFT COMPLETE</h2><h1>🏅 '+val+'</h1><p>Score saved locally.</p><button id="afLocalNext">BACK TO GAME SELECT</button>');
  $('#afLocalNext').onclick=()=>{dismiss();$('#gameSelect')?.click()};
  return;
 }
 const s=session;if(!s)return;const g=s.games[s.round],p=s.players.filter(x=>x.human);
 if(s.shared){p[0].last=score(g,0);p[1].last=score(g,1);s.cursor=p.length}
 else{p[s.cursor].last=score(g);s.cursor++}
 leaveGame();
 if(s.cursor<p.length){
  resultPage('<h2>SHIFT COMPLETE</h2><p>'+p[s.cursor].name+' is up next.</p><button id="afLocalNext">START NEXT PLAYER</button>');
  $('#afLocalNext').onclick=()=>{dismiss();runTurn()};
 }else completeRound();
}
function completeRound(){
 const s=session,g=s.games[s.round];
 const humanAvg=s.players.filter(p=>p.human).reduce((sum,p)=>sum+(p.last||0),0)/Math.max(1,s.players.filter(p=>p.human).length);
 for(const p of s.players){
  if(!p.human)p.last=Math.round(Math.max(125,humanAvg*.88)*(1+.20*Math.sin((s.round+1)*16.3+p.slot*4.9)));
  record(g,p.name,p.last||0);
 }
 const ranks=[...s.players].sort((a,b)=>b.last-a.last);
 for(let i=0;i<ranks.length;i++){const p=ranks[i];p.points+=(p.last>0?[3,2,1,0][i]:0);if(!i&&p.last>0)p.wins++}
 const rows=ranks.map((p,i)=>'<div class="afLocalStanding" style="border-left-color:'+p.color+'"><span>'+(i+1)+'. '+p.name+(p.human?'':' <small>SIMULATED AI</small>')+'</span><b>'+p.last+' RAW · '+p.points+' PTS</b></div>').join('');
 s.round++;s.cursor=0;s.players.forEach(p=>p.last=0);
 if(s.round>=s.games.length){endTournament();return}
 resultPage('<h2>'+g[1]+' · ROUND RESULTS</h2>'+rows+'<p>Next: '+s.games[s.round][1]+'</p><button id="afLocalNext">NEXT GAME</button>');
 $('#afLocalNext').onclick=()=>{dismiss();runTurn()};
}
function endTournament(){
 const s=session;if(!s)return;session=null;
 const ranks=[...s.players].sort((a,b)=>b.points-a.points||b.wins-a.wins),win=ranks[0];
 stats.trophies=(stats.trophies||[]).slice(-19);
 stats.trophies.push({winner:win.name,points:win.points,at:new Date().toISOString()});save();statsView();
 resultPage('<h1 class="afLocalTrophy">🏆</h1><h2>EMPLOYEE OF THE MONTH</h2><h3>'+win.name+'</h3><p>'+win.points+' tournament points · '+win.wins+' game wins</p>'+
 ranks.map((p,i)=>'<div class="afLocalStanding" style="border-left-color:'+p.color+'"><b>'+(i+1)+'. '+p.name+'</b><strong>'+p.points+' PTS</strong></div>').join('')+
 '<button id="afLocalNext">BACK TO MAIN MENU</button>');
 $('#afLocalNext').onclick=()=>{dismiss();$('#afFront .afBack')?.click()};
}
function setup(){
 humans=Math.max(1,Math.min(isMobile()?1:4,humans));cpus=Math.max(0,Math.min(4-humans,cpus));
 $('#afHumanCount').textContent=humans;$('#afCpuCount').textContent=cpus;
 const names=Array.from({length:humans+cpus},(_,i)=>'<div style="border-color:'+colors[i]+'"><b>'+(i<humans?'🎮 P'+(i+1):'🤖 CPU '+(i-humans+1))+'</b><small>'+(i<humans?'HUMAN':'SIMULATED AI')+'</small></div>').join('');
 $('#afLocalRoster').innerHTML=names;
 $('#afLocalNote').textContent=isMobile()?'Mobile: solo against AI only; same-device multiplayer is disabled.':
 humans===2?'Native two-player layouts run together in Ramp Runner, Bag Stacker and Terminal Assist. Other games alternate turns.':
 'Human players take separate timed turns. CPU scores are simulated, not live-playing characters.';
 $('#afLocalRoundGroup').hidden=mode!=='party';$('#afLocalGameGroup').hidden=mode!=='casual';
 $('#afLocalHeading').textContent=mode==='party'?'🏆 PARTY MODE · TOURNAMENT':'👥 LOCAL MULTIPLAYER';
 for(let b of $('#afLocalRoundGroup').querySelectorAll('[data-count]'))b.classList.toggle('active',+b.dataset.count===rounds);
 $('#afLocalGameSelect').value=selection;
 $('#afLocalStart').disabled=(mode==='party'&&humans+cpus<2);
 $('#afLocalControllers').textContent='🎮 '+connectedPads.size+' CONTROLLER'+(connectedPads.size===1?'':'S')+' · PRESS START TO JOIN';
}
function open(type){
 mode=type;$('#afLocalHub').classList.add('open');if(type==='casual')cpus=0;setup();statsView();
}
function start(){
 if(single||session)return;
 const roster=Array.from({length:humans+cpus},(_,i)=>({name:i<humans?'P'+(i+1):'CPU '+(i-humans+1),human:i<humans,slot:i,color:colors[i],points:0,wins:0,last:0}));
 let order=mode==='party'?[...games].sort(()=>Math.random()-.5).slice(0,rounds):[byId(selection)];
 session={players:roster,games:order,round:0,cursor:0,shared:false};
 $('#afLocalHub').classList.remove('open');runTurn();
}
function install(){
 $('#afGameJump')?.remove();
 for(let btn of $('#afGameMount')?.querySelectorAll('.start.versus')||[])btn.hidden=true;
 const css=document.createElement('style');
 css.textContent='#afGameJump,#afGameMount .start.versus{display:none!important}#afGameMount .arcadeGrid{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}#afGameMount .gameChoice{min-width:0;padding:13px}'+
 '#afLocalPlay{margin-left:auto;background:#165c70;border:1px solid #60dfd2;color:#fff;border-radius:10px;padding:11px;font:700 12px system-ui;cursor:pointer}'+
 '#afLocalHub,#afLocalResults{display:none;position:fixed;z-index:3400;inset:0;background:#061a29ed;overflow-y:auto;justify-content:center;align-items:flex-start;padding:15px}#afLocalHub.open,#afLocalResults.open{display:flex}'+
 '.afLocalPanel{width:min(700px,100%);background:#0b2b40;color:#f4f7fc;border:1px solid #64b4c9;border-radius:16px;padding:20px;box-shadow:0 15px 40px #000a;font:14px/1.4 system-ui}'+
 '.afLocalPanel button,.afLocalPanel select{background:#19516b;color:#fff;border:1px solid #6cafc7;border-radius:8px;min-height:39px;padding:7px 10px;font-weight:800;cursor:pointer}'+
 '.afLocalPanel button.active{background:#775e27;border-color:#ffe69a}.afLocalPanel button:disabled{opacity:.45}'+
 '.afLocalTop{display:flex;justify-content:space-between;gap:15px}.afLocalCounts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:15px 0}.afLocalCounts>label{background:#102a3d;border:1px solid #35576a;border-radius:9px;padding:9px}'+
 '.afLocalCounts label div{display:flex;justify-content:space-between;align-items:center;margin-top:7px}.afLocalCounts strong{font-size:23px;color:#ffe093}'+
 '#afLocalRoster{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:12px 0}#afLocalRoster div{border-left:5px solid;background:#16384c;padding:9px;border-radius:7px}#afLocalRoster small{display:block;font-size:10px;color:#b3d5da}'+
 '#afLocalControllers{color:#8fdbf4;border:1px dashed #5e9caf;padding:10px;text-align:center;border-radius:7px;cursor:pointer}'+
 '#afLocalRoundGroup button{margin-right:7px}#afLocalStart{display:block;width:100%;background:#147d60;font-size:19px;margin-top:10px}#afLocalGameSelect{width:100%}'+
 '#afLocalStats{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:12px;font-size:11px}#afLocalStats>div{background:#0d2130;padding:6px;border-radius:5px}#afLocalStats small{display:block;color:#87c7d4}'+
 '.afLocalStanding{display:flex;justify-content:space-between;background:#15384b;border-left:5px solid #57c3e1;padding:9px;margin:5px 0}.afLocalStanding small{font-size:10px;opacity:.7}.afLocalTrophy{text-align:center;font-size:66px}'+
 '#afLocalResults button{display:block;margin:16px auto 0;background:#217861}'+
 '#afShiftClock{display:none;position:fixed;z-index:3200;bottom:10px;right:10px;left:auto;transform:none;pointer-events:none;background:#082b3df5;color:white;border:1px solid #70d5e9;border-radius:12px;padding:5px 12px;text-align:center;font:12px system-ui}#afShiftClock.visible{display:block}#afShiftClock b{font-size:22px;color:#ffe18e}#afShiftClock small{display:block}#afShiftClock button{font-size:10px;pointer-events:auto}'+
 '@media(max-width:767px){#afLocalPlay{display:none!important}#afGameMount .arcadeGrid{grid-template-columns:1fr}#afLocalRoster{grid-template-columns:repeat(2,1fr)}.afLocalPanel{padding:11px}}';
 document.head.append(css);
 const hdr=$('#afGames .afPanelHead');const link=document.createElement('button');link.id='afLocalPlay';link.textContent='👥 LOCAL MULTIPLAYER';hdr.append(link);link.onclick=()=>{if(!isMobile())open('casual')};
 const hub=document.createElement('div');hub.id='afLocalHub';
 hub.innerHTML='<div class="afLocalPanel"><div class="afLocalTop"><h2 id="afLocalHeading">PARTY MODE</h2><button id="afLocalBack">✕ CLOSE</button></div>'+
 '<p>Up to four players. Compete in timed airport shifts with saved results.</p>'+
 '<div class="afLocalCounts"><label>HUMAN PLAYERS<div><button data-edit="humans:-1">−</button><strong id="afHumanCount">1</strong><button data-edit="humans:1">+</button></div></label>'+
 '<label>AI COMPETITORS<div><button data-edit="cpus:-1">−</button><strong id="afCpuCount">1</strong><button data-edit="cpus:1">+</button></div></label></div>'+
 '<div id="afLocalControllers">🎮 PRESS START TO JOIN</div><div id="afLocalRoster"></div>'+
 '<div id="afLocalRoundGroup"><h3>RANDOM TOURNAMENT PLAYLIST</h3><button data-count="2">2 GAMES</button><button data-count="4">4 GAMES</button><button data-count="6">6 GAMES</button></div>'+
 '<div id="afLocalGameGroup"><h3>CHOOSE A GAME</h3><select id="afLocalGameSelect">'+games.map(g=>'<option value="'+g[0]+'">'+g[2]+' '+g[1]+'</option>').join('')+'</select></div>'+
 '<p id="afLocalNote"></p><button id="afLocalStart">START SHIFT</button><h3>LOCAL CAREER STATS</h3><div id="afLocalStats"></div></div>';
 document.body.append(hub);
 const results=document.createElement('div');results.id='afLocalResults';results.innerHTML='<div class="afLocalPanel" id="afLocalResultsBody"></div>';document.body.append(results);
 const clockUI=document.createElement('div');clockUI.id='afShiftClock';clockUI.innerHTML='<b>⏱ <span id="afShiftTime">2:00</span></b><small id="afShiftLabel">P1 · SHIFT TIMER</small><button id="afShiftEnd">END SHIFT</button>';document.body.append(clockUI);
 $('#afShiftEnd').onclick=endShift;$('#afLocalBack').onclick=()=>$('#afLocalHub').classList.remove('open');
 $('#afLocalStart').onclick=start;$('#afLocalGameSelect').onchange=e=>{selection=e.target.value;setup()};
 hub.querySelectorAll('[data-edit]').forEach(btn=>btn.onclick=()=>{
  const [n,d]=btn.dataset.edit.split(':');if(n==='humans')humans+=+d;else cpus+=+d;setup()});
 hub.querySelectorAll('[data-count]').forEach(btn=>btn.onclick=()=>{rounds=+btn.dataset.count;setup()});
 $('#afLocalControllers').onclick=()=>{if(!isMobile()){humans=Math.min(4,humans+1);cpus=Math.min(cpus,4-humans);setup()}};
 $('#partyPlay')?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();mode='party';humans=1;cpus=1;open('party')},true);
 document.addEventListener('click',e=>{
  if(session||single||$('#afOnlineRoom.open')||$('#afLocalHub.open')||$('#afLocalResults.open'))return;
  const b=e.target.closest('button'),g=b&&games.find(x=>x[3].slice(1)===b.id);
  if(g&&!$('#afFront')?.classList.contains('playing')){single=g;timer('P1 · '+g[1]);}
 },true);
 window.addEventListener('af-controller-start',e=>{
  if(isMobile())return;connectedPads.add(e.detail.index);
  if($('#afLocalHub.open')){humans=Math.max(humans,Math.min(4,connectedPads.size));setup()}
 });
 statsView();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
window.AF_LOCAL={open,start,status:()=>({humans,cpus,rounds,inParty:!!session,inCasual:!!single}),games,stats:()=>stats};
})();