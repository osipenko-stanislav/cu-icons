from pathlib import Path
import re,html,json,collections,xml.etree.ElementTree as E
from PIL import Image,ImageChops,ImageDraw
from io import BytesIO
import resvg_py
P=Path('icon-project');R=P/'review/motion/materials-audit-2026-11-27';out={'items':[],'errors':[]}
for n in [0,301,602]:
 raw=Path(f'/private/tmp/cu-materials-{n}.html').read_text();m=re.search(r'<pre id="result">(.*?)</pre>',raw,re.S)
 d=json.loads(html.unescape(m.group(1)))
 for k in out:out[k]+=d[k]
(R/'browser-capture.json').write_text(json.dumps(out))
print('Captured',len(out['items']),'errors',out['errors'][:10]);print('Color failures',[(r['id'],len(r['paintFailures']),r['paintFailures'][:1]) for r in out['items'] if r['paintFailures']][:30])
def render(raw,size):
 root=E.fromstring(raw);root.set('width',str(size));root.set('height',str(size));root.set('style','color:#111')
 for n in root.iter():
  if n.tag.split('}')[-1] in ['path','rect','circle','ellipse','line','polygon','polyline'] and n.get('stroke')!='none':n.set('stroke-width',str(24/size))
 return Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=E.tostring(root).decode(),skip_system_fonts=True))).convert('RGBA')
results=[]
for row in out['items']:
 r={k:v for k,v in row.items() if k!='frames'};r['sizes']={}
 for size in [16,24,32,48]:
  ims=[render(f['svg'],size).getchannel('A') for f in row['frames']];initial=ims[0];ds=[sum(ImageChops.difference(initial,x).getdata())/255 for x in ims[1:]];r['sizes'][str(size)]={'max_changed_pixel_equivalents':round(max(ds),3),'max_alpha_mass':round(max(sum(x.getdata())/255 for x in ims),3)}
 results.append(r)
(R/'findings.json').write_text(json.dumps({'sample_frames':[0,.13,.25,.37,.5,.61,.75,.83,1],'note':'Raster screening is diagnostic only; no perceptual pass/fail implied. Color checks exclude masks and definitions.','items':results,'errors':out['errors']},ensure_ascii=False,indent=2))
print('No raster difference at48',[(r['id'],r.get('interaction')) for r in results if r['sizes']['48']['max_changed_pixel_equivalents']<.01]);print('Weak16<=2',[(r['id'],r['sizes']['16']['max_changed_pixel_equivalents']) for r in results if 0<r['sizes']['16']['max_changed_pixel_equivalents']<=2][:55])
ids=['ref-kitchen','ref-bed','ref-bio','ref-brand-network','cloud-sun-01-lined','camera-01-lined','credit-card-check-lined','home-01-lined','settings-04-lined','placeholder-lined','flag-01-lined','zoom-in-lined']
im=Image.new('RGB',(840,len(ids)*78),'white');draw=ImageDraw.Draw(im)
for i,id in enumerate(ids):
 row=next((r for r in out['items'] if r['id']==id),None)
 if not row:continue
 y=i*78;draw.text((5,y+5),id,fill='black')
 for k,size in enumerate([16,24,32]):
  draw.text((230+k*200,y+3),str(size)+'px',fill='black')
  for j,f in enumerate([row['frames'][j] for j in [0,1,3,5,8]]):
   sprite=render(f['svg'],size);im.paste(sprite,(230+k*200+j*36,y+30),sprite)
im.save(R/'small-sizes.png')
