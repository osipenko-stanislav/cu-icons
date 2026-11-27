from pathlib import Path
import json
P=Path('icon-project');config=json.loads((P/'motion/series/motion.json').read_text());scene=config['scenes'][0];scene['svg']=(P/'motion/series/geometry'/f"{scene['id']}.svg").read_text();player=(P/'motion/assets/motion/player.js').read_text()
js='''
let now=0,queue=[];requestAnimationFrame=fn=>{queue.push(fn);return queue.length};cancelAnimationFrame=()=>queue=[];matchMedia=()=>({matches:false,addEventListener(){}});Object.defineProperty(performance,'now',{value:()=>now});
const host=document.createElement('button');host.innerHTML=scene.svg;document.body.append(host);const before=host.innerHTML;const play=mountMotion(host,[...host.querySelectorAll('[data-part]')],scene,()=>({duration:1,amplitude:1,curve:'cosine'}));const checks=[];
for(const trigger of ['hover','click-replay','hover-click']){
 scene.trigger=trigger;
 for(const event of ['pointerenter','click']){
  now=0;queue=[];host.dispatchEvent(new Event(event));const expected=event==='click'?trigger!=='hover':trigger!=='click-replay';checks.push({trigger,event,pass:(queue.length>0)===expected});
  if(queue.length){now=500;queue.shift()(now);play.stop();checks.push({trigger,event,stopRestores:host.innerHTML===before})}
 }
}
document.body.innerHTML='<pre id="result"></pre>';document.getElementById('result').textContent=JSON.stringify(checks);
'''
Path('/private/tmp/cu-trigger-modes.html').write_text('<!doctype html><body><script>'+player+'\nconst scene='+json.dumps(scene)+';'+js+'</script>')
