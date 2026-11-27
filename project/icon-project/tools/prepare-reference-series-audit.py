from pathlib import Path
D=Path('icon-project/gallery/motion-review/reference-series')
js=r'''
(async()=>{
 const result={rows:[],errors:[]},config=await(await fetch('scenes.json')).json();window.addEventListener('error',e=>result.errors.push({error:e.message}));
 const range=new URLSearchParams(location.search),start=Number(range.get('start')||0),end=Number(range.get('end')||config.scenes.length),ids=range.get('ids')?.split(',');
 const host=document.getElementById('host');
 function exportFrame(root){const svg=root.querySelector('.exact-renderer svg');if(!svg)return null;const inverse=svg.getScreenCTM().inverse(),paths=[];
 for(const path of svg.querySelectorAll('path')){if(path.closest('defs'))continue;const style=getComputedStyle(path),matrix=inverse.multiply(path.getScreenCTM());let opacity=1;for(let n=path;n&&n!==svg.parentNode;n=n.parentNode)opacity*=Number(getComputedStyle(n).opacity||1);const length=path.getTotalLength(),steps=Math.min(180,Math.max(8,Math.ceil(length/.4)));const poly=length>0?Array.from({length:steps+1},(_,i)=>{const p=path.getPointAtLength(i*length/steps);return [p.x*matrix.a+p.y*matrix.c+matrix.e,p.x*matrix.b+p.y*matrix.d+matrix.f]}):[];
 paths.push({d:path.getAttribute('d'),m:[matrix.a,matrix.b,matrix.c,matrix.d,matrix.e,matrix.f],stroke:style.stroke,fill:style.fill,fillOpacity:Number(style.fillOpacity),strokeOpacity:Number(style.strokeOpacity),opacity,length,poly});}
 return paths;}
 function gap(p,line){let best=Infinity;for(let k=1;k<line.length;k++){const a=line[k-1],b=line[k],dx=b[0]-a[0],dy=b[1]-a[1],den=dx*dx+dy*dy,t=den?Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)):0;best=Math.min(best,Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy))}return best}
 function trim(data){if(!data||typeof data!=='object')return false;if(data.ty==='tm')return true;return Object.values(data).some(v=>v&&typeof v==='object'&&trim(v))}
 for(const scene of config.scenes.slice(start,end).filter(s=>!ids||ids.includes(s.id))){
  if(scene.tracks[0][1]!=='reference-lottie'){result.rows.push({id:scene.id,unchanged:true});continue}
  try{
   host.innerHTML=scene.svg;const controller=mountMotion(host,[],scene,()=>config.presets.Balanced);await controller.ready;controller.stop();const frames=[];
   for(const t of [0,.15,.33,.5,.67,.85,1]){controller.seek(t);frames.push({t,paths:exportFrame(host)})}
   const baseline=frames[0].paths,contacts=[],tears=[];
   if(!trim(scene.tracks[0][7].animationData))for(let i=0;i<baseline.length;i++){const a=baseline[i];if(a.poly.length<2||a.opacity<.95||Math.hypot(a.poly[0][0]-a.poly.at(-1)[0],a.poly[0][1]-a.poly.at(-1)[1])<.001)continue;
    for(const end of [0,-1])for(let j=0;j<baseline.length;j++){const b=baseline[j];if(i===j||b.opacity<.95||b.poly.length<2)continue;const p=a.poly.at(end),base=gap(p,b.poly);if(base>.035)continue;let max=base,time=0;for(const frame of frames){const x=frame.paths[i],y=frame.paths[j];if(x.opacity<.95||y.opacity<.95||x.poly.length<2||y.poly.length<2)continue;const d=gap(x.poly.at(end),y.poly);if(d>max){max=d;time=frame.t}}contacts.push({i,j,end,base,max,time});if(max-base>.18)tears.push({i,j,end,base,max,time})}
   }
   const empty=frames.every(f=>f.paths.every(p=>!p.d||p.opacity<.005||p.length<.001));
   const signatures=frames.map(f=>JSON.stringify(f.paths.map(p=>[p.d,p.m,p.opacity])));const staticMotion=new Set(signatures).size===1;
   for(const f of frames)for(const p of f.paths)delete p.poly;
   result.rows.push({id:scene.id,frames,contacts,tears,empty,staticMotion});controller.destroy();host.innerHTML='';
  }catch(e){result.errors.push({id:scene.id,error:e.stack});host.innerHTML=''}
 }
 const out=document.createElement('pre');out.id='audit-result';out.textContent=JSON.stringify(result);document.body.append(out);document.body.dataset.complete='true';
})();
'''
(D/'audit.html').write_text('<!doctype html><meta charset="utf-8"><style>#host{width:48px;height:48px;color:black}#host svg{width:48px;height:48px}#host svg path{vector-effect:non-scaling-stroke;stroke-width:1px}</style><div id="host"></div><script src="player.js"></script><script>'+js+'</script>')
print('Prepared browser audit')
