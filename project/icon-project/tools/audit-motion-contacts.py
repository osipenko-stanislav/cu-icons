from pathlib import Path
import json,sys
P=Path('icon-project');source=Path(sys.argv[1]) if len(sys.argv)>1 else P/'motion/series';config=json.loads((source/'motion.json').read_text())
for s in config['scenes']:s['svg']=(source/'geometry'/f"{s['id']}.svg").read_text()
js='''
let now=0,queue=[];requestAnimationFrame=fn=>{queue.push(fn);return queue.length};cancelAnimationFrame=()=>queue=[];matchMedia=()=>({matches:false,addEventListener(){}});Object.defineProperty(performance,'now',{value:()=>now});const findings=[],counts={icons:0,contacts:0,presetRuns:0};
function world(p,m){return {x:p.x*m.a+p.y*m.c+m.e,y:p.x*m.b+p.y*m.d+m.f}}
function distance(p,poly,m){let min=Infinity;for(let i=1;i<poly.length;i++){const a=world(poly[i-1],m),b=world(poly[i],m),dx=b.x-a.x,dy=b.y-a.y,den=dx*dx+dy*dy,t=den?Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/den)):0;min=Math.min(min,Math.hypot(p.x-a.x-t*dx,p.y-a.y-t*dy))}return min}
for(const scene of config.scenes){
 const host=document.createElement('button');host.innerHTML=scene.svg;document.body.append(host);const active=host.querySelector('[id$="motion-active"]'),nodes=[...active.querySelectorAll('path,circle,ellipse,line,polyline,polygon,rect')].filter(n=>!n.closest('defs,clipPath'));
 const geometry=nodes.map(n=>{const length=n.getTotalLength(),steps=Math.min(800,Math.max(8,Math.ceil(length/.18))),poly=Array.from({length:steps+1},(_,i)=>n.getPointAtLength(length*i/steps)),start=poly[0],end=poly[poly.length-1],closed=['circle','ellipse','rect','polygon'].includes(n.localName)||Math.hypot(start.x-end.x,start.y-end.y)<.00001;return {poly,anchors:closed?[]:[start,end]}});
 const matrices=nodes.map(n=>n.getCTM()),contacts=[];
 for(let i=0;i<nodes.length;i++)for(const [end,point] of geometry[i].anchors.entries())for(let j=0;j<nodes.length;j++)if(i!==j){const gap=distance(world(point,matrices[i]),geometry[j].poly,matrices[j]);if(gap<.025)contacts.push({i,j,end,baseline:gap,maxGap:gap,point})}
 counts.icons++;counts.contacts+=contacts.length;
 if(contacts.length&&scene.tracks.some(t=>!['draw','erase-redraw'].includes(t[1]))){
  for(const [preset,p] of Object.entries(config.presets)){
   const play=mountMotion(host,[...host.querySelectorAll('[data-part]')],scene,()=>p);now=0;queue=[];play();counts.presetRuns++;
   for(const t of [0,.1,.2,.35,.5,.65,.8,.9,1]){now=t*scene.duration*p.duration;queue.shift()?.(now);const matrices=nodes.map(n=>n.getCTM());if(scene.tracks.some(t=>t[1]==='page-turn'))for(let i=0;i<nodes.length;i++){const length=nodes[i].getTotalLength(),steps=Math.min(800,Math.max(8,Math.ceil(length/.18)));geometry[i].poly=Array.from({length:steps+1},(_,k)=>nodes[i].getPointAtLength(length*k/steps))}for(const c of contacts){const point=scene.tracks.some(t=>t[1]==='page-turn')?nodes[c.i].getPointAtLength(c.end?nodes[c.i].getTotalLength():0):c.point;const gap=distance(world(point,matrices[c.i]),geometry[c.j].poly,matrices[c.j]);if(gap>c.maxGap){c.maxGap=gap;c.preset=preset;c.time=t}}}
  }
 }
 const shapeKey=n=>JSON.stringify([n.localName,...['d','cx','cy','r','x','y','width','height','rx','ry','x1','x2','y1','y2','points'].map(k=>n.getAttribute(k))]);
 const broken=contacts.filter(c=>c.maxGap-c.baseline>.12).map(({point,...c})=>({...c,point:[point.x,point.y],sourcePath:nodes[c.i].getAttribute('d'),targetPath:nodes[c.j].getAttribute('d')}));if(broken.length)findings.push({id:scene.id,broken,contacts:contacts.map(c=>({source:shapeKey(nodes[c.i]),target:shapeKey(nodes[c.j]),point:[c.point.x,c.point.y],baseline:c.baseline}))});host.remove();
}
document.body.innerHTML='<pre id="result"></pre>';document.getElementById('result').textContent=JSON.stringify({counts,findings});
'''
Path('/private/tmp/cu-reference-contact-audit.html' if len(sys.argv)>1 else '/private/tmp/cu-motion-contact-audit.html').write_text('<!doctype html><body><script>'+(P/'motion/assets/motion/player.js').read_text()+'\nconst config='+json.dumps(config)+';'+js+'</script>')
print('Prepared geometry contact audit')
