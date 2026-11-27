// Reference timeline playback on retargeted, project-owned SVG geometry.
function mountExactReference(root,scene,preset) {
  const spec=scene.tracks[0][7], behavior=spec.interaction;
  const stage=root.querySelector('[data-motion-target]')||root;
  const fallback=stage.querySelector('svg'), holder=document.createElement('span');holder.className='exact-renderer';
  holder.style.cssText='display:inline-block;vertical-align:middle;width:'+(stage===root?'var(--icon-size,56px)':'100%')+';height:'+(stage===root?'var(--icon-size,56px)':'100%');
  stage.insertBefore(holder,fallback||null);
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const animation=lottie.loadAnimation({container:holder,renderer:'svg',autoplay:false,loop:false,animationData:JSON.parse(JSON.stringify(spec.animationData)),rendererSettings:{progressiveLoad:false,preserveAspectRatio:'xMidYMid meet'}});
  let loaded=false,active=false,hovered=false,clickedLoop=false,destroyed=false;
  const ready=new Promise((resolve,reject)=>{animation.addEventListener('DOMLoaded',()=>{loaded=true;styleSvg();show();autoplay();resolve(animation)});animation.addEventListener('data_failed',()=>reject(Error('Motion data failed')))});
  function styleSvg(){const svg=holder.querySelector('svg');if(!svg)return;svg.style.overflow=spec.overflow?'visible':'hidden';if(spec.overflow){for(const rect of svg.querySelectorAll('defs clipPath rect')){rect.setAttribute('x','-12');rect.setAttribute('y','-12');rect.setAttribute('width','48');rect.setAttribute('height','48')}}for(const node of svg.querySelectorAll('path,rect,circle,ellipse,line,polygon,polyline')){if(node.closest('defs,mask,clipPath'))continue;if(node.getAttribute('stroke')&&node.getAttribute('stroke')!=='none')node.setAttribute('stroke','currentColor');if(node.getAttribute('fill')&&node.getAttribute('fill')!=='none')node.setAttribute('fill','currentColor')}}
  function show(){const useFallback=reduced.matches&&behavior!=='click-toggle';holder.style.display=useFallback?'none':'inline-block';if(fallback)fallback.style.display=useFallback?'':'none'}
  function allowed(event){if(scene.trigger==='reference')return event==='hover'?behavior.startsWith('hover'):behavior.startsWith('click');return event==='hover'?['hover','hover-click'].includes(scene.trigger):['click-replay','hover-click'].includes(scene.trigger)}
  function isLoop(){return behavior==='loop'||behavior==='hover-loop'}
  function loopWanted(){return (scene.trigger==='reference'&&behavior==='loop')||(hovered&&allowed('hover'))||clickedLoop}
  function speed(){animation.setSpeed(1/(preset().duration||1))}
  function autoplay(){if(loaded&&!reduced.matches&&scene.trigger==='reference'&&behavior==='loop'){animation.loop=true;speed();animation.setDirection(1);animation.play()}}
  function target(next){if(!loaded)return;active=next;show();if(reduced.matches){if(behavior==='click-toggle')animation.goToAndStop(next?Math.max(0,animation.totalFrames-.001):0,true);return}animation.loop=false;speed();animation.setDirection(next?1:-1);animation.play()}
  function replay(force=true){if(!loaded||reduced.matches||(!force&&!animation.isPaused))return;show();animation.loop=false;speed();animation.setDirection(1);animation.goToAndPlay(0,true)}
  function loop(){if(!loaded||reduced.matches)return;show();animation.loop=loopWanted();speed();animation.setDirection(1);animation.play()}
  const enter=()=>{hovered=true;if(!allowed('hover'))return;if(isLoop())loop();else if(behavior==='hover'||behavior==='click-toggle')target(true);else replay(false)};
  const leave=()=>{hovered=false;if(!allowed('hover'))return;if(isLoop())animation.loop=loopWanted();else if(behavior==='hover'||behavior==='click-toggle')target(false)};
  const click=()=>{if(!allowed('click'))return;if(isLoop()){clickedLoop=!clickedLoop;if(clickedLoop)loop();else animation.loop=loopWanted()}else if(behavior==='hover'||behavior==='click-toggle')target(!active);else replay(true)};
  root.addEventListener('pointerenter',enter);root.addEventListener('pointerleave',leave);root.addEventListener('click',click);
  animation.addEventListener('complete',()=>{if(isLoop()&&!loopWanted())animation.goToAndStop(0,true)});
  const motionChanged=()=>{animation.pause();show();if(reduced.matches){if(behavior==='click-toggle')animation.goToAndStop(active?Math.max(0,animation.totalFrames-.001):0,true)}else autoplay()};reduced.addEventListener('change',motionChanged);
  function stop(){if(!loaded)return;animation.pause();animation.loop=false;animation.setDirection(1);animation.goToAndStop(0,true);active=false;hovered=false;clickedLoop=false;show()}
  function controller(){if(isLoop())loop();else replay(true)}
  controller.ready=ready;controller.animation=animation;controller.stop=stop;
  controller.seek=value=>{if(!loaded)return;animation.pause();active=value>=.5;animation.goToAndStop(Math.min(animation.totalFrames-.001,Math.max(0,value)*animation.totalFrames),true);show()};
  controller.setActive=target;controller.refresh=()=>{stop();autoplay()};controller.setTrigger=value=>{scene.trigger=value;controller.refresh()};controller.updateSpeed=speed;
  controller.destroy=()=>{destroyed=true;animation.destroy();holder.remove();if(fallback)fallback.style.display='';root.removeEventListener('pointerenter',enter);root.removeEventListener('pointerleave',leave);root.removeEventListener('click',click);reduced.removeEventListener('change',motionChanged)};
  return controller;
}
function mountMotion(root,parts,scene,preset){return scene.tracks[0]?.[1]==='reference-lottie'?mountExactReference(root,scene,preset):mountLegacyMotion(root,parts,scene,preset)}
