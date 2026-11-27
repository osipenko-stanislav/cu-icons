from pathlib import Path
import json,sys
P=Path('icon-project');source=Path(sys.argv[1]) if len(sys.argv)>1 else P/'motion/series';config=json.loads((source/'motion.json').read_text())
for s in config['scenes']:s['svg']=(source/'geometry'/f"{s['id']}.svg").read_text()
js='''
let now=0,queue=[];requestAnimationFrame=fn=>{queue.push(fn);return queue.length};cancelAnimationFrame=()=>queue=[];matchMedia=()=>({matches:false,addEventListener(){}});Object.defineProperty(performance,'now',{value:()=>now});const findings=[],counts={icons:0,movingPairs:0};
function poly(node){let length=node.getTotalLength(),steps=Math.min(500,Math.max(8,Math.ceil(length/.2)));return Array.from({length:steps+1},(_,i)=>node.getPointAtLength(length*i/steps))}
function mapped(poly,m){return poly.map(p=>({x:p.x*m.a+p.y*m.c+m.e,y:p.x*m.b+p.y*m.d+m.f}))}
function bounds(poly){return [Math.min(...poly.map(p=>p.x)),Math.min(...poly.map(p=>p.y)),Math.max(...poly.map(p=>p.x)),Math.max(...poly.map(p=>p.y))]}
function cross(a,b,c){return (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)}
function intersects(a,b){const ab=bounds(a),bb=bounds(b);if(ab[0]>bb[2]||bb[0]>ab[2]||ab[1]>bb[3]||bb[1]>ab[3])return false;for(let i=1;i<a.length;i++)for(let j=1;j<b.length;j++){if(Math.max(a[i-1].x,a[i].x)<Math.min(b[j-1].x,b[j].x)||Math.max(b[j-1].x,b[j].x)<Math.min(a[i-1].x,a[i].x)||Math.max(a[i-1].y,a[i].y)<Math.min(b[j-1].y,b[j].y)||Math.max(b[j-1].y,b[j].y)<Math.min(a[i-1].y,a[i].y))continue;if(cross(a[i-1],a[i],b[j-1])*cross(a[i-1],a[i],b[j])<-.000001&&cross(b[j-1],b[j],a[i-1])*cross(b[j-1],b[j],a[i])<-.000001)return true}return false}
function delta(a,b){return Math.max(...['a','b','c','d','e','f'].map(k=>Math.abs(a[k]-b[k])))}
for(const scene of config.scenes){counts.icons++;if(!scene.tracks.some(t=>!['draw','erase-redraw'].includes(t[1])))continue;const host=document.createElement('button');host.innerHTML=scene.svg;document.body.append(host);const nodes=[...host.querySelector('[id$="motion-active"]').querySelectorAll('path,circle,ellipse,line,polyline,rect,polygon')].filter(n=>!n.closest('defs,clipPath')),polys=nodes.map(poly),initial=nodes.map(n=>n.getCTM()),world=polys.map((p,i)=>mapped(p,initial[i])),pairs=[];
for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++)if(!intersects(world[i],world[j]))pairs.push({i,j,relative:initial[j].inverse().multiply(initial[i])});
const found=new Map();for(const [preset,p] of Object.entries(config.presets)){const play=mountMotion(host,[...host.querySelectorAll('[data-part]')],scene,()=>p);now=0;queue=[];play();for(const t of [0,.15,.3,.5,.7,.85,1]){now=t*scene.duration*p.duration;queue.shift()?.(now);if(scene.tracks.some(t=>t[1]==='page-turn'))for(let i=0;i<nodes.length;i++)polys[i]=poly(nodes[i]);const matrices=nodes.map(n=>n.getCTM()),world=polys.map((p,i)=>mapped(p,matrices[i]));for(const pair of pairs){if(found.has(pair.i+':'+pair.j)||delta(pair.relative,matrices[pair.j].inverse().multiply(matrices[pair.i]))<.00001)continue;counts.movingPairs++;if(intersects(world[pair.i],world[pair.j]))found.set(pair.i+':'+pair.j,{i:pair.i,j:pair.j,preset,t,source:nodes[pair.i].getAttribute('d'),target:nodes[pair.j].getAttribute('d')})}}}
if(found.size)findings.push({id:scene.id,crossings:[...found.values()]});host.remove()}
document.body.innerHTML='<pre id="result"></pre>';document.getElementById('result').textContent=JSON.stringify({counts,findings});
'''
Path('/private/tmp/cu-reference-crossing-audit.html' if len(sys.argv)>1 else '/private/tmp/cu-motion-crossing-audit.html').write_text('<!doctype html><body><script>'+(P/'motion/assets/motion/player.js').read_text()+'\nconst config='+json.dumps(config)+';'+js+'</script>')
