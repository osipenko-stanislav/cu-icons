from pathlib import Path
from importlib.machinery import SourceFileLoader
import json,xml.etree.ElementTree as E,math
P=Path('icon-project');points=SourceFileLoader('arrow_parts',str(P/'tools/motion-arrow-parts.py')).load_module().points
config=json.loads((P/'motion/series/motion.json').read_text());catalog={r['id']:r for r in json.loads((P/'motion/series/catalog.json').read_text())};scenes=[]
for scene in config['scenes']:
 if not catalog[scene['id']].get('rigid_arrow_parts'):continue
 raw=(P/'motion/series/geometry'/f"{scene['id']}.svg").read_text();r=E.fromstring(raw);active=next(n for n in r.iter() if n.get('id','').endswith('motion-active'));paths=[n for n in active.iter() if n.tag.endswith('path')];parents={n:p for p in active.iter() for n in p};joints=[]
 for i,head in enumerate(paths):
  pts=points(head)
  if pts is None or len(pts)!=3:continue
  a,tip,b=pts;u=(a[0]-tip[0],a[1]-tip[1]);v=(b[0]-tip[0],b[1]-tip[1]);lu=math.hypot(*u);lv=math.hypot(*v)
  if not lu or not lv or abs(lu-lv)>max(lu,lv)*.15:continue
  if not -.7<(u[0]*v[0]+u[1]*v[1])/(lu*lv)<.7:continue
  bisector=(u[0]/lu+v[0]/lv,u[1]/lu+v[1]/lv);bl=math.hypot(*bisector)
  for j,stem in enumerate(paths):
   line=points(stem)
   if line is None or len(line)!=2 or parents[head] is not parents[stem]:continue
   for endpoint,other in [(line[0],line[1]),(line[1],line[0])]:
    if math.dist(tip,endpoint)>.015:continue
    delta=(other[0]-tip[0],other[1]-tip[1]);length=math.hypot(*delta)
    if length<min(lu,lv)*.6 or (delta[0]*bisector[0]+delta[1]*bisector[1])/(length*bl)<.98:continue
    joints.append([i,j,tip,endpoint]);break
 scene={**scene,'svg':raw,'joints':joints};scenes.append(scene)
js='''
let now=0,queue=[];requestAnimationFrame=fn=>{queue.push(fn);return queue.length};cancelAnimationFrame=()=>queue=[];matchMedia=()=>({matches:false,addEventListener(){}});Object.defineProperty(performance,'now',{value:()=>now});const checks=[];
for(const scene of scenes)for(const [preset,p] of Object.entries(presets)){
 const host=document.createElement('button');host.innerHTML=scene.svg;document.body.append(host);const parts=[...host.querySelectorAll('[data-part]')],paths=[...host.querySelector('[id$="motion-active"]').querySelectorAll('path')];const play=mountMotion(host,parts,scene,()=>p);now=0;queue=[];play();let maximum=0;
 for(let step=0;step<=20;step++){now=scene.duration*p.duration*step/20;queue.shift()?.(now);for(const [a,b,tip,end] of scene.joints){const x=new DOMPoint(...tip).matrixTransform(paths[a].getCTM()),y=new DOMPoint(...end).matrixTransform(paths[b].getCTM());maximum=Math.max(maximum,Math.hypot(x.x-y.x,x.y-y.y))}}
 checks.push({id:scene.id,preset,joints:scene.joints.length,maxJointGap:maximum,connected:maximum<.016});host.remove();
}
document.body.innerHTML='<pre id="result"></pre>';document.getElementById('result').textContent=JSON.stringify(checks);
'''
Path('/private/tmp/cu-arrow-joints.html').write_text('<!doctype html><body><script>'+(P/'motion/assets/motion/player.js').read_text()+'\nconst scenes='+json.dumps(scenes)+';const presets='+json.dumps(config['presets'])+';'+js+'</script>');print('Junction check:',len(scenes),'icons,',sum(len(s['joints']) for s in scenes),'head/stem joints')
