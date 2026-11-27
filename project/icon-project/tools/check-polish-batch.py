from pathlib import Path
import json
P=Path('icon-project');D=P/'gallery/motion-review/reference-series';ids=[r['id'] for r in json.loads((P/'review/motion/polish-2026-11-27/authored-batch.json').read_text())]
js=r'''
(async()=>{
 const ids=IDS,config=await(await fetch('scenes.json')).json(),range=new URLSearchParams(location.search),start=Number(range.get('start')||0),end=Number(range.get('end')||ids.length),selected=new Set(ids.slice(start,end));const scenes=config.scenes.filter(s=>selected.has(s.id)),out={checks:[],frames:[],errors:[]};let reduced=false,listeners=[];
 matchMedia=()=>({get matches(){return reduced},addEventListener(e,f){listeners.push(f)},removeEventListener(e,f){listeners=listeners.filter(fn=>fn!==f)}});
 function snapshot(root,id,t){const original=root.querySelector('.exact-renderer svg')||root.querySelector('svg'),svg=original.cloneNode(true);svg.setAttribute('width','48');svg.setAttribute('height','48');svg.style.width='48px';svg.style.height='48px';svg.style.color='#111';out.frames.push({id,t,svg:svg.outerHTML})}
 for(const scene of scenes.filter(s=>s.tracks[0][1]==='reference-lottie'))for(const [name,p] of Object.entries(config.presets)){
  const root=document.createElement('button');root.style.color='#111';root.innerHTML=scene.svg;document.body.append(root);
  try{const c=mountMotion(root,[],scene,()=>p);await c.ready;c.stop();let changed=false,first;
   for(const t of [0,.15,.33,.5,.67,.85,1]){c.seek(t);const svg=root.querySelector('.exact-renderer svg'),signature=svg.innerHTML;if(t===0)first=signature;else if(signature!==first)changed=true;
    if(name==='Balanced')snapshot(root,scene.id,t);
    const invalid=[...svg.querySelectorAll('path')].some(n=>/NaN|undefined|Infinity/.test(n.getAttribute('d')||''));out.checks.push({id:scene.id,preset:name,t,finitePaths:!invalid});
   }
   out.checks.push({id:scene.id,preset:name,moved:changed});c.stop();const kind=scene.tracks[0][7].interaction,looping=['loop','hover-loop'].includes(kind),state=['hover','click-toggle'].includes(kind),event=scene.trigger==='reference'?(kind.startsWith('click')?'click':'pointerenter'):scene.trigger==='click-replay'?'click':'pointerenter';root.dispatchEvent(new Event(event));out.checks.push({id:scene.id,preset:name,inputStarts:!c.animation.isPaused,loopMode:c.animation.loop===looping});
   if(looping){root.dispatchEvent(new Event(event==='click'?'click':'pointerleave'));c.animation.advanceTime(20000);out.checks.push({id:scene.id,preset:name,loopFinishes:c.animation.isPaused&&c.animation.currentFrame<.01})}
   else{c.animation.advanceTime(20000);out.checks.push({id:scene.id,preset:name,finishes:c.animation.isPaused});if(state){root.dispatchEvent(new Event(event==='click'?'click':'pointerleave'));c.animation.advanceTime(20000);out.checks.push({id:scene.id,preset:name,reverseRestores:c.animation.isPaused&&c.animation.currentFrame<.01})}}
   c.stop();reduced=true;listeners.forEach(f=>f());root.dispatchEvent(new Event(event));out.checks.push({id:scene.id,preset:name,reducedMotion:c.animation.isPaused});reduced=false;listeners.forEach(f=>f());c.destroy();
  }catch(e){out.errors.push({id:scene.id,preset:name,error:String(e)})}root.remove();
 }
 let now=0,queue=[];requestAnimationFrame=fn=>{queue.push(fn);return queue.length};cancelAnimationFrame=()=>queue=[];Object.defineProperty(performance,'now',{value:()=>now});
 for(const scene of scenes.filter(s=>s.tracks[0][1]!=='reference-lottie'))for(const [name,p] of Object.entries(config.presets)){
  const root=document.createElement('button');root.style.color='#111';root.innerHTML=scene.svg;document.body.append(root);
  try{const c=mountMotion(root,[...root.querySelectorAll('[data-part]')],scene,()=>p),before=root.innerHTML;now=0;queue=[];c();let moved=false;
   for(const t of [0,.15,.33,.5,.67,.85,1]){now=t*scene.duration*p.duration;queue.shift()?.(now);if(t>0&&t<1&&root.innerHTML!==before)moved=true;if(name==='Balanced')snapshot(root,scene.id,t)}
   out.checks.push({id:scene.id,preset:name,moved,restored:root.innerHTML===before});reduced=true;queue=[];c();out.checks.push({id:scene.id,preset:name,reducedMotion:queue.length===0&&root.innerHTML===before});reduced=false;c.stop();const trigger=scene.trigger;scene.trigger='reference';queue=[];root.dispatchEvent(new Event('pointerenter'));out.checks.push({id:scene.id,preset:name,nativeDefaultWorks:queue.length>0});c.stop();scene.trigger=trigger;
  }catch(e){out.errors.push({id:scene.id,preset:name,error:String(e)})}root.remove();
 }
 document.getElementById('result').textContent=JSON.stringify(out);
})();
'''.replace('IDS',json.dumps(ids))
(D/'polish-check.html').write_text('<!doctype html><meta charset="utf-8"><pre id="result"></pre><script src="player.js"></script><script>'+js+'</script>');print('Prepared checks for',len(ids),'scenes')
