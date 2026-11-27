from pathlib import Path
P=Path('icon-project');page=(P/'gallery/motion-review/index.html').read_text()
js='''<script>
function waitReady(){if(!document.querySelector('select.trigger'))return setTimeout(waitReady,50);run().catch(e=>{document.body.dataset.error=e.stack})}
async function raster(svg,size){const clone=svg.cloneNode(true);clone.setAttribute('width',size);clone.setAttribute('height',size);clone.style.width=size+'px';clone.style.height=size+'px';const source=[...svg.querySelectorAll('path,circle,ellipse,rect,line,polyline,polygon')],targets=[...clone.querySelectorAll('path,circle,ellipse,rect,line,polyline,polygon')];targets.forEach((n,i)=>{const s=getComputedStyle(source[i]);for(const [attr,value] of [['stroke',s.stroke],['fill',s.fill],['stroke-width',s.strokeWidth],['vector-effect',s.vectorEffect]])n.setAttribute(attr,value)});const img=new Image();await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=reject;img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(new XMLSerializer().serializeToString(clone))});const canvas=document.createElement('canvas');canvas.width=canvas.height=size;const context=canvas.getContext('2d');context.drawImage(img,0,0,size,size);return {data:context.getImageData(0,0,size,size).data,canvas}}
async function run(){
 const checks=[],cards=[...document.querySelectorAll('article')],card=cards.find(c=>c.querySelector('h2').textContent==='Arrow Right'),svg=card.querySelector('.preview svg');
 for(const stroke of [1,2.5])for(const size of [16,24,32,48]){
  document.getElementById('stroke-width').value=stroke;document.getElementById('stroke-width').dispatchEvent(new Event('input'));
  document.getElementById('icon-size').value=size;document.getElementById('icon-size').dispatchEvent(new Event('change'));
  const {data}=await raster(svg,size);let thickness=0;const x=Math.floor(size*4/24);for(let y=0;y<size;y++)thickness+=data[(y*size+x)*4+3]/255;
  checks.push({stroke,size,measuredThickness:thickness,constantWidth:Math.abs(thickness-stroke)<.04});
 }
 let now=0,queue=[];window.requestAnimationFrame=fn=>{queue.push(fn);return queue.length};window.cancelAnimationFrame=()=>queue=[];Object.defineProperty(performance,'now',{value:()=>now});
 for(const stroke of [1,2.5])for(const size of [16,24,32,48]){
  const host=document.createElement('button');host.className='preview';host.innerHTML='<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'" viewBox="0 0 24 24" fill="none" stroke="black"><path data-part="0" d="M2 12H22" stroke-linecap="round"/></svg>';document.body.append(host);host.querySelector('svg').style.width=host.querySelector('svg').style.height=size+'px';document.body.style.setProperty('--icon-stroke',stroke+'px');
  const part=host.querySelector('path'),scene={id:'stroke-test',trigger:'hover-click',duration:1000,tracks:[[0,'erase-redraw',1,0,0,0,1]]};
  const play=mountMotion(host,[part],scene,()=>({duration:1,amplitude:1,curve:'cosine'}));now=0;queue=[];const before=host.innerHTML;play();const first=await raster(host.querySelector('svg'),size);now=500;queue.shift()(now);const mid=await raster(host.querySelector('svg'),size);let visible=0;for(let i=3;i<mid.data.length;i+=4)visible+=mid.data[i];now=1000;queue.shift()(now);checks.push({stroke,size,midpointFullyErased:visible===0,restored:host.innerHTML===before});host.remove();
 }
 document.getElementById('stroke-width').value='1';document.getElementById('stroke-width').dispatchEvent(new Event('input'));document.getElementById('icon-size').value='48';document.getElementById('icon-size').dispatchEvent(new Event('change'));
 const el=document.createElement('pre');el.id='stroke-result';el.textContent=JSON.stringify(checks);document.body.append(el);
}
setTimeout(waitReady,50);
</script>'''
(P/'gallery/motion-review/_stroke-check.html').write_text(page.replace('</body>',js+'</body>'))
print('Raster check prepared')
