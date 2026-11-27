from pathlib import Path
import json
P=Path('icon-project');cfg=json.loads((P/'motion/series/motion.json').read_text());scenes=[s for s in cfg['scenes'] if s['id'].startswith(('arrow-','arrows-','corner-','chevron-')) and not any(x in s['id'] for x in ['selector','triangle'])]
for s in scenes:s['svg']=(P/'motion/series/geometry'/f"{s['id']}.svg").read_text()
js='''
let now=0,queue=[];requestAnimationFrame=fn=>{queue.push(fn);return queue.length};cancelAnimationFrame=()=>queue=[];matchMedia=()=>({matches:false,addEventListener(){}});Object.defineProperty(performance,'now',{value:()=>now});const checks=[];
for(const scene of scenes){const host=document.createElement('button');host.innerHTML=scene.svg;document.body.append(host);const parts=[...host.querySelectorAll('[data-part]')];const play=mountMotion(host,parts,scene,()=>({duration:1,amplitude:1,curve:'cosine'}));now=0;queue=[];play();const part=parts[parts.length-1];const a=part.getCTM();now=scene.duration/2;queue.shift()(now);const b=part.getCTM();let dx=b.e-a.e,dy=b.f-a.f;const expectedX=scene.id.includes('left')?-1:scene.id.includes('right')?1:0,expectedY=scene.id.includes('up')?-1:scene.id.includes('down')?1:0;checks.push({id:scene.id,dx,dy,direction:(expectedX?dx*expectedX>0:Math.abs(dx)<.001)&&(expectedY?dy*expectedY>0:Math.abs(dy)<.001)});play.stop();host.remove()}
document.body.innerHTML='<pre id="result"></pre>';document.getElementById('result').textContent=JSON.stringify(checks);
'''
Path('/private/tmp/cu-arrow-direction.html').write_text('<!doctype html><body><script>'+(P/'motion/assets/motion/player.js').read_text()+'\nconst scenes='+json.dumps(scenes)+';'+js+'</script>')
