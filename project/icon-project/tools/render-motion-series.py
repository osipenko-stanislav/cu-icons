from pathlib import Path
import json,re,html,sys,xml.etree.ElementTree as E
from importlib.machinery import SourceFileLoader
from PIL import Image,ImageDraw,ImageChops
renderer=SourceFileLoader('local_renderer','icon-project/tools/iconizer-local.py').load_module().Renderer()
P=Path('icon-project');out=P/'review/motion/series';out.mkdir(exist_ok=True)
raw=Path('/private/tmp/cu-motion-series-dom.html').read_text();match=re.search(r'<pre id="result">(.*?)</pre>',raw,re.S)
if not match:raise SystemExit('Browser result is absent')
data=json.loads(html.unescape(match[1]));failures=[c for c in data['checks'] if any(v is False for v in c.values())]
(out/'frames.json').write_text(json.dumps(data['frames'])+'\n')
(out/'browser-checks.json').write_text(json.dumps(data['checks'],indent=2)+'\n')
catalog=json.loads((P/'motion/series/catalog.json').read_text());by={r['id']:r for r in catalog};static=[];clipped=[]
for r in catalog:
 for size in [16,24,32]:
  a=renderer.render((P/'motion/series/svg'/f"{r['id']}.svg").read_bytes(),size);b=renderer.render((P/'motion/series/geometry'/f"{r['id']}.svg").read_bytes(),size)
  if ImageChops.difference(a,b).getchannel('A').getbbox():static.append({'id':r['id'],'size':size})
for f in data['frames']:
 root=E.fromstring(f['svg']);root.set('viewBox','-2 -2 28 28');im=renderer.render(E.tostring(root),112);bbox=im.getchannel('A').getbbox()
 if bbox and (bbox[0]<8 or bbox[1]<8 or bbox[2]>104 or bbox[3]>104):clipped.append({'id':f['id'],'preset':f['preset'],'t':f['t'],'bbox':bbox})
mid={f['id']:f['svg'].encode() for f in data['frames'] if f['preset']=='Balanced'}
for page in range((len(catalog)+69)//70):
 sheet=Image.new('RGB',(1400,1000),'#fafafa');draw=ImageDraw.Draw(sheet)
 for i,r in enumerate(catalog[page*70:(page+1)*70]):
  x=(i%7)*200;y=(i//7)*100;id=r['id'];draw.text((x+5,y+3),id[:31],fill='black')
  for j,(raw,dark) in enumerate([((P/'motion/series/svg'/f'{id}.svg').read_bytes(),False),(mid[id],False),(mid[id],True)]):
   im=renderer.render(raw,24);bg=Image.new('RGBA',(24,24),'#202124' if dark else '#fafafa')
   if dark:im=Image.merge('RGBA',(Image.new('L',im.size,255),)*3+(im.getchannel('A'),))
   bg.alpha_composite(im);sheet.paste(bg.resize((48,48),Image.Resampling.NEAREST).convert('RGB'),(x+8+j*61,y+24))
  draw.text((x+5,y+79),r['pattern'][:30],fill='#555555')
 sheet.save(out/f'sheet-{page+1:02}.png')
report={'scenes':len(catalog),'preset_runs':len(data['checks']),'browser_failures':failures,'static_mismatches':static,'clipped_frames':clipped,'sampled_raster_frames':len(data['frames']),'visual_review':'pending sequential sheet inspection','limitations':['Chromium only','No product state transitions or continuous loops implied']}
(out/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='limitations'},indent=2))
