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
