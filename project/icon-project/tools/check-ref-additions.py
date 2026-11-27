from pathlib import Path
import json
P=Path('icon-project');D=P/'gallery/motion-review/reference-series';config=json.loads((D/'scenes.json').read_text());scenes=[s for s in config['scenes'] if s['id'].startswith('ref-')]
js=r'''
(async()=>{
 let now=0,queue=[],reduce=false;requestAnimationFrame=fn=>{queue.push(fn);return queue.length};cancelAnimationFrame=()=>queue=[];
 matchMedia=()=>({get matches(){return reduce},addEventListener(){},removeEventListener(){}});Object.defineProperty(performance,'now',{value:()=>now});
 const out={checks:[],frames:[],errors:[]};
 for(const scene of config.scenes)for(const [name,preset] of Object.entries(config.presets)){
  const root=document.createElement('button');root.style.color='#111';root.innerHTML=scene.svg;document.body.append(root);const parts=[...root.querySelectorAll('[data-part]')],before=root.innerHTML;
  try{
   const play=mountMotion(root,parts,scene,()=>preset);now=0;queue=[];play();let moved=false;
   for(const t of [0,.15,.33,.5,.67,.85,1]){now=t*scene.duration*preset.duration;queue.shift()?.(now);if(t>0&&t<1&&root.innerHTML!==before)moved=true;
    if(name==='Balanced'){const svg=root.querySelector('svg').cloneNode(true);svg.setAttribute('width','48');svg.setAttribute('height','48');svg.style.color='#111';out.frames.push({id:scene.id,t,svg:svg.outerHTML})}
   }
   out.checks.push({id:scene.id,preset:name,parts:parts.length,moved,restored:root.innerHTML===before});
   reduce=true;queue=[];play();out.checks.push({id:scene.id,preset:name,reducedMotion:queue.length===0&&root.innerHTML===before});reduce=false;
   queue=[];root.dispatchEvent(new Event('pointerenter'));out.checks.push({id:scene.id,preset:name,hover:queue.length>0});play.stop();queue=[];root.click();out.checks.push({id:scene.id,preset:name,clickIgnored:queue.length===0});
   const localIds=new Set([...root.querySelectorAll('[id]')].map(n=>n.id));for(const n of root.querySelectorAll('*'))for(const attr of ['mask','clip-path']){const v=n.getAttribute(attr);if(v){const match=/^url\(#(.+)\)$/.exec(v);out.checks.push({id:scene.id,localReference:!!match&&localIds.has(match[1])})}}
  }catch(e){out.errors.push({id:scene.id,error:String(e)})}root.remove();
 }
 document.getElementById('result').textContent=JSON.stringify(out);
})();
'''
(D/'ref-check.html').write_text('<!doctype html><meta charset="utf-8"><pre id="result"></pre><script src="player.js"></script><script>const config='+json.dumps({**config,'scenes':scenes})+';'+js+'</script>');print('Prepared',len(scenes),'native reference scenes')
