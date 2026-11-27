const motionProfiles={"direction":[[0,0],[0.12,-0.08],[0.42,1],[0.58,1],[0.92,0],[1,0]],"hinge":[[0,0],[0.3,1],[0.55,1],[0.86,0],[1,0]],"mechanism":[[0,0],[0.16,-0.04],[0.48,1],[0.66,0.92],[0.9,0],[1,0]],"heartbeat":[[0,0],[0.18,0.82],[0.32,0.12],[0.49,1],[0.7,0],[1,0]],"fold":[[0,0],[0.3,1],[0.52,0.85],[0.86,0],[1,0]],"flutter":[[0,0],[0.21,1],[0.43,0.18],[0.62,0.62],[0.8,0.08],[1,0]],"ripple":[[0,0],[0.28,1],[0.53,0.2],[0.7,0.45],[1,0]],"chart":[[0,0],[0.2,0.15],[0.43,1],[0.6,0.94],[1,0]]};
function sampleMotionProfile(name,t){const keys=motionProfiles[name];for(let i=1;i<keys.length;i++){const [end,b]=keys[i],[start,a]=keys[i-1];if(t<=end){let u=Math.max(0,Math.min(1,(t-start)/(end-start)));u=u*u*(3-2*u);return a+(b-a)*u}}return 0}
// Track tuple: part index, property, magnitude, pivot x/y, start/end fractions.
function mountMotion(root, parts, scene, preset) {
  if (scene.trigger==='static') return ()=>{};
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let frame = 0, started = 0, activePreset, original;
  const animatedAttributes = scene.tracks.flatMap(([index, kind]) => {
    const names = (kind==='draw'||kind==='erase-redraw') ? ['stroke-dasharray','stroke-dashoffset'] : kind==='page-turn' ? ['d','transform','visibility'] : ['transform'];
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
  function strokeMetrics(part) {
    const style=getComputedStyle(part), width=parseFloat(style.strokeWidth)||1;
    let length=part.getTotalLength();
    if(style.vectorEffect==='non-scaling-stroke') {
      const matrix=part.getCTM();
      if(matrix) length*=Math.hypot(matrix.a,matrix.b);
    }
    return {length,padding:Math.max(1,width)+.1};
  }
  function paint(time) {
    const p = activePreset;
    const t = Math.min(1,(time-started)/(p.duration*scene.duration));
    for (const [index,kind,amount,x,y,from,to,profile] of scene.tracks) {
      const part = parts[index];
      const local = Math.max(0,Math.min(1,(t-from)/(to-from)));
      if (kind==='erase-redraw') {
        if (local===0 || local===1) {
          for (const [node,name,value] of original) if(node===part) {
            if(value===null) part.removeAttribute(name); else part.setAttribute(name,value);
          }
        } else {
          // One dash and one gap travel along the full path: full -> empty -> full.
          // Padding clears round caps at the middle of the gap.
          const metrics=strokeMetrics(part);
          const span = metrics.length+metrics.padding;
          const progress = local*local*(3-2*local);
          part.setAttribute('stroke-dasharray',span+' '+span);
          part.setAttribute('stroke-dashoffset',-2*span*progress);
        }
        continue;
      }
      if (kind==='draw') {
        const {length,padding}=strokeMetrics(part);
        part.setAttribute('stroke-dasharray',length+' '+(length+padding*2));
        part.setAttribute('stroke-dashoffset', (length+padding)*(1-local*local*(3-2*local)));
        continue;
      }
      if (kind==='page-turn') {
        if(local<=.1||local>=.9) {
          part.setAttribute('visibility','hidden');
        } else {
          // A page starts fully laid on the right, passes edge-on through the
          // spine and lands fully on the left. It never grows out of the spine.
          const progress=(local-.1)/.8;
          const eased=progress*progress*(3-2*progress);
          const span=Math.cos(Math.PI*eased), width=Math.abs(span);
          if(width<.018) part.setAttribute('visibility','hidden');
          else {
            const side=span>0?1:0, reverse=side?0:1;
            const n=value=>Number(value.toFixed(5));
            const X=offset=>n(x+offset*span);
            // Lift the top edge inside the cover curve as the page narrows.
            // The spine anchors (x,6) and (x,21) remain fixed throughout.
            const top=n(6-2.5*width);
            const d=`M${x} 6A${n(5*width)} ${n(5*width)} 0 0 ${side} ${X(4.5)} ${top}H${X(10)}V16.5A${n(2.5*width)} 2.5 0 0 ${side} ${X(7.5)} 19H${X(4)}A${n(4*width)} 4 0 0 ${reverse} ${X(1.5)} 19.9L${x} 21`;
            part.setAttribute('d',d);
            part.removeAttribute('transform');
            part.setAttribute('visibility','visible');
          }
        }
        continue;
      }
      if (kind==='blink') {
        const factor = 1 - amount*Math.sin(Math.PI*local)**2;
        part.setAttribute('transform',`translate(0 ${y*(1-factor)}) scale(1 ${factor})`);
        continue;
      }
      const wave = profile && motionProfiles[profile] ? sampleMotionProfile(profile,local) : p.curve==='spring'
        ? Math.sin(local*15)*Math.exp(-4*local)*Math.sin(Math.PI*local)*3
        : Math.sin(Math.PI*local)**2;
      if (kind==='scale'||kind==='scale-x'||kind==='scale-y') {
        const factor=1+Math.max(0,wave)*amount*p.amplitude;
        const sx=kind==='scale-y'?1:factor,sy=kind==='scale-x'?1:factor;
        part.setAttribute('transform',`translate(${x} ${y}) scale(${sx} ${sy}) translate(${-x} ${-y})`);
        continue;
      }
      const safeWave = (scene.id.startsWith('graduation-hat-')||scene.id.startsWith('rocket-')||scene.id.startsWith('trash-')||scene.id==='moon-star-lined'||/^(arrow|arrows|chevron|corner)-/.test(scene.id)) ? Math.max(0,wave) : wave;
      const value = safeWave*amount*p.amplitude;
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
  root.addEventListener('click',()=>{if(['click-replay','hover-click'].includes(scene.trigger))play()});
  root.addEventListener('pointerenter',()=>{if(['hover','hover-click','reference'].includes(scene.trigger))play()});
  play.stop=stop;
  reduced.addEventListener('change',stop);
  return play;
}
