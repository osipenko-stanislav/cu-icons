from pathlib import Path
import json
P=Path('icon-project');D=P/'gallery/motion-review/reference-series';config=json.loads((D/'scenes.json').read_text());scenes=[s for s in config['scenes'] if s['id'] in ['ref-shower','ref-steam']]
js=r'''
(async()=>{
 const result={checks:[],frames:[],errors:[]};let reduce=false,listeners=[];matchMedia=()=>({get matches(){return reduce},addEventListener(e,fn){listeners.push(fn)},removeEventListener(e,fn){listeners=listeners.filter(f=>f!==fn)}});
 for(const scene of config.scenes)for(const [name,preset] of Object.entries(config.presets)){
  const root=document.createElement('button');root.style.cssText='width:48px;height:48px;color:#111';root.innerHTML=scene.svg;document.body.append(root);
  try{const c=mountMotion(root,[],scene,()=>preset);await c.ready;c.stop();
   for(const t of [0,.15,.33,.5,.67,.85,1]){c.seek(t);if(name==='Balanced'){const svg=root.querySelector('.exact-renderer svg').cloneNode(true);svg.setAttribute('width','48');svg.setAttribute('height','48');svg.style.width='48px';svg.style.height='48px';svg.style.color='#111';result.frames.push({id:scene.id,t,svg:svg.outerHTML})}}
   c.stop();root.dispatchEvent(new Event('pointerenter'));result.checks.push({id:scene.id,preset:name,hoverLoops:!c.animation.isPaused&&c.animation.loop===true});root.dispatchEvent(new Event('pointerleave'));result.checks.push({id:scene.id,preset:name,leaveFinishesCycle:c.animation.loop===false});
   c.animation.goToAndPlay(c.animation.totalFrames-2,true);await new Promise(resolve=>setTimeout(resolve,250));c.animation.advanceTime(250);result.checks.push({id:scene.id,preset:name,returnedToIdle:c.animation.isPaused&&c.animation.currentFrame<.01});
   c.stop();reduce=true;listeners.forEach(fn=>fn());root.dispatchEvent(new Event('pointerenter'));result.checks.push({id:scene.id,preset:name,reducedMotion:c.animation.isPaused&&root.querySelector('.exact-renderer').style.display==='none'});reduce=false;listeners.forEach(fn=>fn());c.destroy();
  }catch(e){result.errors.push({id:scene.id,error:String(e)})}root.remove();
 }
 document.getElementById('result').textContent=JSON.stringify(result);
})();
'''
(D/'weather-check.html').write_text('<!doctype html><meta charset="utf-8"><pre id="result"></pre><script src="player.js"></script><script>const config='+json.dumps({**config,'scenes':scenes})+';'+js+'</script>');print('Prepared weather checks for',len(scenes),'scenes')
