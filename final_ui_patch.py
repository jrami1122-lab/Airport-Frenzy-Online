"""Polish Xbox analog marshalling and guarantee Bag Stacker finish signals."""
def replace_one(s,a,b,why):
 n=s.count(a)
 if n!=1:raise RuntimeError(f"Controller polish {why}: expected 1 anchor, found {n}")
 return s.replace(a,b,1)

def patch(html):
 # Expose only match state for reliable end-of-game polling; physics stays unchanged.
 html=replace_one(html,"function checkEnd(){for(const b of boards)",
 """window.__AF_BAG_STATE=()=>({running,paused,versus,boards:boards.map(b=>({gameOver:!!b.gameOver,score:b.score,count:b.count}))});
 function checkEnd(){for(const b of boards)""","bag state accessor")
 # Count completion once even when the stack hits the line repeatedly.
 html=replace_one(html,"function checkEnd(){for(const b of boards)",
 """function checkEnd(){if(window.__afBagEndNotified&&(!versus||boards.every(b=>b.gameOver)))return;
 if(!versus||boards.every(b=>b.gameOver))window.__afBagEndNotified=true;
 for(const b of boards)""","bag one-shot end")
 html=replace_one(html,"function reset(v=false){versus=v;",
   "function reset(v=false){window.__afBagEndNotified=false;versus=v;","reset bag end guard")
 # Local-only deterministic QA can simulate a full hold without modifying
 # real game rules or exposing cheats to production users.
 html=replace_one(html,"window.__AF_BAG_STATE=()=>",
  """if(location.hostname==='127.0.0.1'||location.hostname==='localhost')
 window.__AF_TEST_BAG_END=(i=0)=>{if(boards[i]){boards[i].gameOver=true;checkEnd();}};
 window.__AF_BAG_STATE=()=>""","QA full hold hook")
 # Keep home menu contained; no browser-native scrollbar when focused with Xbox.
 style="""<style id="afNoHomeScroll">
 html,body{overflow-x:hidden!important;overscroll-behavior:none!important}
 #afFront,#afHome,#afHome .afMainButtons{scrollbar-width:none!important;overscroll-behavior:contain!important}
 #afFront::-webkit-scrollbar,#afHome::-webkit-scrollbar,#afHome .afMainButtons::-webkit-scrollbar{display:none!important}
 #afHome{overflow:hidden!important}
 #afHome .afMainButtons{overflow:visible!important}
 #afHome .afMainButtons button{max-width:100%;min-width:0!important}
 @media(max-height:600px) and (min-width:721px){
 #afFront .afHome{bottom:9px!important;max-height:calc(100dvh - 28px)!important}
 #afFront .afKicker{margin:0 0 7px!important;font-size:clamp(10px,2.6vh,13px)!important}
 #afFront .afMainButtons{gap:6px!important}
 #afFront .afMainButtons button{min-height:60px!important;padding:8px 50px 8px 14px!important;
 font-size:clamp(20px,5vh,30px)!important}
 #afFront .afMainButtons button small{font-size:9px!important}
 #afFront .afOnline{margin:6px 0 0!important}
 }
 </style>"""
 html=html.replace("</head>",style+"</head>",1) # Only the main HTML head; nested game HTML has its own head.
 # The original handler also needs the complete 360-degree stick positions
 # to move freely. Snap recognition is still based on nearest canonical
 # direction, so visually placing a wand remains intuitive.
 anchor="drag('l');drag('r');"
 if html.count(anchor)!=1:raise RuntimeError("marshalling analog insertion anchor")
 analog="""const analogTrack={l:{last:null,turn:0,at:0},r:{last:null,turn:0,at:0}};
 document.addEventListener('af-marshal-analog',event=>{
  if(!running||paused||demoing)return;
  const values=event.detail||{},now=performance.now();
  for(const side of ['l','r']){
   const stick=values[side];
   if(!stick||Math.hypot(stick.x,stick.y)<.42)continue;
   const radians=Math.atan2(stick.y,stick.x),deg=radians*180/Math.PI;
   const arm=arms[side];if(!arm)continue;
   arm.style.transform='rotate('+deg+'deg)';
   placeHandle(side,deg);
   const prev=analogTrack[side];
   if(prev.last!==null&&now-prev.at<300){
    const delta=Math.atan2(Math.sin(radians-prev.last),Math.cos(radians-prev.last));
    prev.turn+=delta;
   }else prev.turn=0;
   if(Math.abs(prev.turn)>4.7){
     circleReady[side]=true;prev.turn=0;
     message.textContent=(side==='l'?'LEFT':'RIGHT')+' CIRCLE READY';
   }
   prev.last=radians;prev.at=now;
   let nearest=null,error=Infinity;
   for(const [name,pair] of Object.entries(poses)){
    const a=pair[side]*Math.PI/180;
    const diff=Math.abs(Math.atan2(Math.sin(radians-a),Math.cos(radians-a)));
    if(diff<error){nearest=name;error=diff}
   }
   if(nearest&&zones[side]!==nearest){zones[side]=nearest;armFeedback(side)}
  }
 });
 """
 html=replace_one(html,anchor,analog+anchor,"continuous marshalling stick angles")
 return html
