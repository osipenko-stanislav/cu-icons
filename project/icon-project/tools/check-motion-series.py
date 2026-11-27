from pathlib import Path
import json
P=Path('icon-project');src=P/'motion/series';config=json.loads((src/'motion.json').read_text());catalog={r['id']:r for r in json.loads((src/'catalog.json').read_text())}
for s in config['scenes']:s['svg']=(src/'geometry'/f"{s['id']}.svg").read_text();s['pattern']=catalog[s['id']]['pattern']
player=(P/'motion/assets/motion/player.js').read_text()
js='''
let now=0,queue=[],reduce=false;const frames=[],checks=[];
window.requestAnimationFrame=fn=>{queue.push(fn);return queue.length};window.cancelAnimationFrame=()=>{queue=[]};
window.matchMedia=()=>({get matches(){return reduce},addEventListener(){}});
Object.defineProperty(performance,'now',{value:()=>now});
for(const scene of config.scenes)for(const [preset,p] of Object.entries(config.presets)){
const host=document.createElement('button');host.innerHTML=scene.svg;document.body.append(host);
const parts=[...host.querySelectorAll('[data-part]')],before=host.innerHTML;
const play=mountMotion(host,parts,scene,()=>p);now=0;queue=[];play();
const result={id:scene.id,preset,parts:parts.length,startsComplete:scene.tracks.every(([i,k])=>k!=='erase-redraw'||!parts[i].hasAttribute('stroke-dasharray')),noFade:true,moved:false,trimCycle:true};
for(const t of [0,.15,.33,.5,.67,.85,1]){
 now=t*scene.duration*p.duration;let fn=queue.shift();if(fn)fn(now);
 if(t>0&&t<1&&host.innerHTML!==before)result.moved=true;
 result.noFade &&= parts.every(part=>!part.hasAttribute('stroke-opacity'));
 if(preset==='Balanced'&&t===.5 || preset==='Expressive'&&scene.pattern!=='detail-path'&&t>0&&t<1)frames.push({id:scene.id,preset,t,svg:host.innerHTML});
}
result.restored=host.innerHTML===before;
queue=[];reduce=true;play();result.reducedMotion=host.innerHTML===before&&queue.length===0;reduce=false;
now=0;host.dispatchEvent(new Event('pointerenter'));result.hover=(queue.length>0)===['hover','hover-click'].includes(scene.trigger);now=scene.duration*p.duration;queue.shift()?.(now);
now=0;host.click();result.clickReplay=(queue.length>0)===['click-replay','hover-click'].includes(scene.trigger);now=scene.duration*p.duration;queue.shift()?.(now);
for(const [index,kind,amount,x,y,start,end] of scene.tracks)if(kind==='erase-redraw') {
 now=0;queue=[];play();now=(start+(end-start)/2)*scene.duration*p.duration;queue.shift()?.(now);
 const part=parts[index],span=part.getTotalLength()+1.1;
 result.trimCycle &&= Math.abs(Number(part.getAttribute('stroke-dashoffset'))+span)<.00001;
 now=scene.duration*p.duration;queue.shift()?.(now);result.trimCycle &&= host.innerHTML===before;
}
checks.push(result);host.remove();
}
document.body.innerHTML='<pre id="result"></pre>';document.getElementById('result').textContent=JSON.stringify({checks,frames});
'''
Path('/private/tmp/cu-motion-series-test.html').write_text('<!doctype html><body><script>'+player+'\nconst config='+json.dumps(config)+';'+js+'</script>')
print('Prepared browser QA for',len(config['scenes']),'scenes')
