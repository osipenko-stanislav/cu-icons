// Track tuple: part index, property, magnitude, pivot x/y, start/end fractions.
function mountMotion(root, parts, scene, preset) {
  if (scene.trigger==='static') return ()=>{};
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let frame = 0, started = 0, activePreset, original;
  const animatedAttributes = scene.tracks.flatMap(([index, kind]) => {
    const names = kind==='draw' ? ['stroke-dasharray','stroke-dashoffset'] : ['transform'];
    return names.map(name => [parts[index],name]);
  });
  function stop() {
    cancelAnimationFrame(frame);
    frame = 0;
    root.querySelector('[id$="motion-idle"]')?.removeAttribute('visibility');
    root.querySelector('[id$="motion-active"]')?.setAttribute('visibility','hidden');
    if (!original) return;
    for (const [part,name,value] of original) {
      if (value===null) part.removeAttribute(name);
      else part.setAttribute(name,value);
    }
    original = null;
  }
  function paint(time) {
    const p = activePreset;
    const t = Math.min(1,(time-started)/(p.duration*scene.duration));
    for (const [index,kind,amount,x,y,from,to] of scene.tracks) {
      const part = parts[index];
      const local = Math.max(0,Math.min(1,(t-from)/(to-from)));
      if (kind==='draw') {
        const length = part.getTotalLength();
        part.setAttribute('stroke-dasharray',length+' '+(length+2));
        part.setAttribute('stroke-dashoffset', (length+1.1)*(1-local*local*(3-2*local)));
        continue;
      }
      if (kind==='blink') {
        const factor = 1 - amount*Math.sin(Math.PI*local)**2;
        part.setAttribute('transform',`translate(0 ${y*(1-factor)}) scale(1 ${factor})`);
        continue;
      }
      const wave = p.curve==='spring'
        ? Math.sin(local*15)*Math.exp(-4*local)*Math.sin(Math.PI*local)*3
        : Math.sin(Math.PI*local)**2;
      const value = wave*amount*p.amplitude;
      part.setAttribute('transform',kind==='rotate' ? `rotate(${value} ${x} ${y})`
        : kind==='x' ? `translate(${value} 0)` : `translate(0 ${value})`);
    }
    if (t<1) frame=requestAnimationFrame(paint);
    else stop();
  }
  function play() {
    if (frame || reduced.matches) return;
    root.querySelector('[id$="motion-idle"]')?.setAttribute('visibility','hidden');
    root.querySelector('[id$="motion-active"]')?.removeAttribute('visibility');
    activePreset=preset();
    original=animatedAttributes.map(([part,name])=>[part,name,part.getAttribute(name)]);
    started=performance.now();
    paint(started);
  }
  root.addEventListener('click',play);
  if (scene.trigger==='hover') root.addEventListener('pointerenter',play);
  reduced.addEventListener('change',stop);
  return play;
}
