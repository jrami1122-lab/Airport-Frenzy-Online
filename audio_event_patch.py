"""Inject audio only at actual gameplay events after balance patching, keeping physics intact."""
def once(source, old, new, label):
    found=source.count(old)
    if found != 1:
        raise RuntimeError(f"Audio event '{label}' missing ({found}); abort game build instead of silently desyncing")
    return source.replace(old,new,1)

def patch(html):
    html=once(html,"flyoverSound(dir);nextFly=rnd(15,60);flyClock=0",
        "window.AF_AUDIO?.effect('plane',{gain:.88,cooldown:4000});nextFly=rnd(15,60);flyClock=0",
        "real aircraft flyover")
    html=once(html,
        "function hit(p,source,cutIndex=null){if(!p.alive||p.immune>0)return;",
        "function hit(p,source,cutIndex=null){if(!p.alive||p.immune>0)return;window.AF_AUDIO?.effect('crash',{gain:.95,cooldown:400});",
        "tug collision")
    html=once(html,"function collect(p,c){loose.splice(loose.indexOf(c),1);",
        "function collect(p,c){window.AF_AUDIO?.effect('thump',{gain:.4,cooldown:240});loose.splice(loose.indexOf(c),1);",
        "cart connection")
    html=once(html,"function repair(p,r){repairs.splice(repairs.indexOf(r),1);",
        "function repair(p,r){window.AF_AUDIO?.effect('ding',{gain:.7});repairs.splice(repairs.indexOf(r),1);",
        "ramp repairs")
    html=once(html,
        "p.carts.splice(-n);p.banked+=points;p.delivered+=n;p.bankCooldown=1.7;",
        "p.carts.splice(-n);p.banked+=points;p.delivered+=n;p.bankCooldown=1.7;window.AF_AUDIO?.effect('ding',{gain:1,cooldown:200});",
        "depot banking")
    html=once(html,
        "function finishRampShift(){\n if(!playing||paused)return;",
        "function finishRampShift(){\n if(!playing||paused)return;window.AF_AUDIO?.effect('ding',{gain:1});window.AF_AUDIO?.motor(false);",
        "ramp shift completion")
    # Marshalling now triggers correct/wrong audio directly in its
    # Simon Says submission handler, without exposing the target.
    return html
