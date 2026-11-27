from pathlib import Path
import json
P=Path('icon-project'); src=P/'motion/reference-pilot'; config=json.loads((src/'motion.json').read_text())
for s in config['scenes']:s['svg']=(src/'geometry'/f"{s['id']}.svg").read_text()
player=Path('icon-project/motion/assets/motion/player.js').read_text()
js='''
let now=0,queue=[],reduce=false;const frames=[],checks=[];
window.requestAnimationFrame=fn=>{queue.push(fn);return queue.length};window.cancelAnimationFrame=()=>{queue=[]};
window.matchMedia=()=>({get matches(){return reduce},addEventListener(){}});
Object.defineProperty(performance,'now',{value:()=>now});
for(const scene of config.scenes)for(const [preset,p] of Object.entries(config.presets)){
const host=document.createElement('button');host.innerHTML=scene.svg;document.body.append(host);
const parts=[...host.querySelectorAll('[data-part]')],before=host.innerHTML;
const play=mountMotion(host,parts,scene,()=>p);now=0;queue=[];play();
checks.push({id:scene.id,preset,startHasAllParts:scene.tracks.every(([i,k])=>k!=='erase-redraw'||!parts[i].hasAttribute('stroke-dasharray'))});
let moved=false;
for(const t of [0,.15,.33,.5,.67,.85,1]){now=t*scene.duration*p.duration;let fn=queue.shift();if(fn)fn(now);if(t>0&&t<1&&host.innerHTML!==before)moved=true;checks.push({id:scene.id,preset,t,noFade:parts.every(part=>!part.hasAttribute('stroke-opacity'))});frames.push({id:scene.id,preset,t,svg:host.innerHTML});}
checks.push({id:scene.id,preset,moved,restored:host.innerHTML===before});
queue=[];reduce=true;play();checks.push({id:scene.id,preset,reducedMotion:host.innerHTML===before&&queue.length===0});reduce=false;
now=0;host.dispatchEvent(new Event('pointerenter'));checks.push({id:scene.id,preset,hover:(queue.length>0)===['hover','hover-click'].includes(scene.trigger)});now=scene.duration*p.duration;queue.shift()?.(now);
now=0;host.click();checks.push({id:scene.id,preset,clickReplay:(queue.length>0)===['click-replay','hover-click'].includes(scene.trigger)});now=scene.duration*p.duration;queue.shift()?.(now);for(const [index,kind,amount,x,y,start,end] of scene.tracks)if(kind==='erase-redraw') {
 now=0;queue=[];play();now=(start+(end-start)/2)*scene.duration*p.duration;queue.shift()?.(now);
 const part=parts[index],span=part.getTotalLength()+1.1;
 checks.push({id:scene.id,preset,index,fullyErasedAtMidpoint:Math.abs(Number(part.getAttribute('stroke-dashoffset'))+span)<.00001,noFade:!part.hasAttribute('stroke-opacity')});
 now=scene.duration*p.duration;queue.shift()?.(now);
 checks.push({id:scene.id,preset,index,restoredAfterRedraw:host.innerHTML===before});
}
host.remove();
}
document.body.innerHTML='<pre id="result"></pre>';document.getElementById('result').textContent=JSON.stringify({checks,frames});
'''
Path('/private/tmp/cu-reference-motion-test.html').write_text('<!doctype html><body><script>'+player+'\nconst config='+json.dumps(config)+';'+js+'</script>')
print('Browser frame check prepared')
