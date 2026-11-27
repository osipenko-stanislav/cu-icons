from pathlib import Path
import json
P=Path('icon-project');scene=next(s for s in json.loads((P/'motion/reference-pilot/motion.json').read_text())['scenes'] if s['id']=='book-open-01-lined');scene['svg']=(P/'motion/reference-pilot/geometry/book-open-01-lined.svg').read_text();presets=json.loads((P/'motion/reference-pilot/motion.json').read_text())['presets']
js='''
let now=0,queue=[];requestAnimationFrame=fn=>{queue.push(fn);return queue.length};cancelAnimationFrame=()=>queue=[];matchMedia=()=>({matches:false,addEventListener(){}});Object.defineProperty(performance,'now',{value:()=>now});const checks=[];
for(const [preset,p] of Object.entries(presets)){
 const host=document.createElement('button');host.innerHTML=scene.svg;document.body.append(host);const page=host.querySelector('[data-part]'),cover=host.querySelector('[id$="motion-active"] path'),coverPath=new Path2D(cover.getAttribute('d')),ctx=document.createElement('canvas').getContext('2d'),before=host.innerHTML;const play=mountMotion(host,[page],scene,()=>p);now=0;queue=[];play();let maxAnchorError=0,outside=0,visibleFrames=0,previousEdge=Infinity,monotonic=true;
 for(let step=0;step<=60;step++){now=step/60*scene.duration*p.duration;queue.shift()?.(now);if(page.getAttribute('visibility')==='hidden')continue;visibleFrames++;const length=page.getTotalLength(),a=page.getPointAtLength(0),b=page.getPointAtLength(length);maxAnchorError=Math.max(maxAnchorError,Math.hypot(a.x-12,a.y-6),Math.hypot(b.x-12,b.y-21));const box=page.getBBox(),edge=2*(box.x+box.width/2)-12;if(edge>previousEdge+.001)monotonic=false;previousEdge=edge;
 for(let i=1;i<100;i++){const point=page.getPointAtLength(length*i/100);if(ctx.isPointInPath(coverPath,point.x,point.y))continue;let distance=Infinity,coverLength=cover.getTotalLength();for(let k=0;k<=600;k++){const q=cover.getPointAtLength(coverLength*k/600);distance=Math.min(distance,Math.hypot(point.x-q.x,point.y-q.y))}if(distance>.025)outside++}
 }
 now=0;queue=[];play();now=scene.duration*p.duration*.4;queue.shift()?.(now);play.stop();const stopRestores=host.innerHTML===before;
 checks.push({preset,stopRestores,visibleFrames,maxAnchorError,anchorsFixed:maxAnchorError<.0001,pageInsideCover:outside===0,outsideSamples:outside,rightToLeftOnly:monotonic,restored:host.innerHTML===before});host.remove()
}
document.body.innerHTML='<pre id="book-result"></pre>';document.getElementById('book-result').textContent=JSON.stringify(checks);
'''
Path('/private/tmp/cu-book-turn-check.html').write_text('<!doctype html><body><script>'+(P/'motion/assets/motion/player.js').read_text()+'\nconst scene='+json.dumps(scene)+';const presets='+json.dumps(presets)+';'+js+'</script>')
