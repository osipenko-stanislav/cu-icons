from pathlib import Path
import json
P=Path('icon-project');D=P/'gallery/motion-review/reference-series';cfg=json.loads((D/'scenes.json').read_text());ids={'ref-shower','ref-steam','ref-kitchen','ref-bio','ref-bed','ref-brand-network'};scenes=[s for s in cfg['scenes'] if s['id'] in ids]
js=r'''
(async()=>{
 const result={checks:[],frames:[],errors:[]};let reduce=false,listeners=[];matchMedia=()=>({get matches(){return reduce},addEventListener(e,f){listeners.push(f)},removeEventListener(e,f){listeners=listeners.filter(fn=>fn!==f)}});
 function frame(root,id,t){const original=root.querySelector('.exact-renderer svg')||root.querySelector('svg'),svg=original.cloneNode(true);svg.setAttribute('width','48');svg.setAttribute('height','48');svg.style.width='48px';svg.style.height='48px';svg.style.color='#111';result.frames.push({id,t,svg:svg.outerHTML})}
 for(const scene of config.scenes.filter(s=>s.tracks[0][1]==='reference-lottie'))for(const [name,p] of Object.entries(config.presets)){
  const root=document.createElement('button');root.style.color='#111';root.innerHTML=scene.svg;document.body.append(root);
  try{const c=mountMotion(root,[],scene,()=>p);await c.ready;c.stop();
   for(const t of [0,.15,.33,.5,.67,.85,1]){c.seek(t);if(name==='Balanced')frame(root,scene.id,t)}
   c.stop();root.dispatchEvent(new Event('pointerenter'));const looping=scene.tracks[0][7].interaction==='hover-loop';result.checks.push({id:scene.id,preset:name,hoverPlays:!c.animation.isPaused,expectedLoop:c.animation.loop===looping});
   root.dispatchEvent(new Event('pointerleave'));result.checks.push({id:scene.id,preset:name,noLoopAfterLeave:c.animation.loop===false});c.animation.advanceTime(10000);result.checks.push({id:scene.id,preset:name,finishes:c.animation.isPaused,idleAfterLoop:!looping||c.animation.currentFrame<.01});
   c.stop();reduce=true;listeners.forEach(fn=>fn());root.dispatchEvent(new Event('pointerenter'));result.checks.push({id:scene.id,preset:name,reducedMotion:c.animation.isPaused&&root.querySelector('.exact-renderer').style.display==='none'});reduce=false;listeners.forEach(fn=>fn());c.destroy();
  }catch(e){result.errors.push({id:scene.id,error:String(e)})}root.remove();
 }
 let now=0,queue=[];requestAnimationFrame=fn=>{queue.push(fn);return queue.length};cancelAnimationFrame=()=>queue=[];Object.defineProperty(performance,'now',{value:()=>now});
 for(const scene of config.scenes.filter(s=>s.tracks[0][1]!=='reference-lottie'))for(const [name,p] of Object.entries(config.presets)){
  const root=document.createElement('button');root.style.color='#111';root.innerHTML=scene.svg;document.body.append(root);
  try{const c=mountMotion(root,[...root.querySelectorAll('[data-part]')],scene,()=>p),before=root.innerHTML;now=0;queue=[];c();let moved=false;
   for(const t of [0,.15,.33,.5,.67,.85,1]){now=t*scene.duration*p.duration;queue.shift()?.(now);if(t>0&&t<1&&root.innerHTML!==before)moved=true;if(name==='Balanced')frame(root,scene.id,t)}
   result.checks.push({id:scene.id,preset:name,moved,restored:root.innerHTML===before});reduce=true;queue=[];c();result.checks.push({id:scene.id,preset:name,reducedMotion:queue.length===0&&root.innerHTML===before});reduce=false;c.stop();
  }catch(e){result.errors.push({id:scene.id,error:String(e)})}root.remove();
 }
 document.getElementById('result').textContent=JSON.stringify(result);
})();
'''
(D/'refinements-check.html').write_text('<!doctype html><meta charset="utf-8"><pre id="result"></pre><script src="player.js"></script><script>const config='+json.dumps({**cfg,'scenes':scenes})+';'+js+'</script>');print('Prepared',len(scenes),'scenes')
