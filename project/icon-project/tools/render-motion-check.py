from pathlib import Path
import re,html,json,sys,xml.etree.ElementTree as E
from PIL import Image,ImageDraw,ImageChops
sys.path.insert(0,str(Path('icon-project/tools').resolve()));from importlib.machinery import SourceFileLoader
renderer=SourceFileLoader('local_renderer','icon-project/tools/iconizer-local.py').load_module().Renderer()
raw=Path('/private/tmp/cu-motion-dom.html').read_text();data=json.loads(html.unescape(re.search(r'<pre id="result">(.*?)</pre>',raw,re.S)[1]))
failed=[c for c in data['checks'] if any(v is False for v in c.values())]
print('browser checks',len(data['checks']),'failures',failed)
P=Path('icon-project');folder=P/'review/motion';folder.mkdir(exist_ok=True)
static=[]
for s in json.loads((P/'motion/pilot/motion.json').read_text())['scenes']:
 for size in [16,24,32,64]:
  a=renderer.render((P/'motion/pilot/svg'/f"{s['id']}.svg").read_bytes(),size);b=renderer.render((P/'motion/pilot/geometry'/f"{s['id']}.svg").read_bytes(),size)
  diff=ImageChops.difference(a,b); extrema=diff.getextrema(); max_delta=max(v[1] for v in extrema); pixels=sum(1 for v in diff.getdata() if max(v)>0)
  static.append({'id':s['id'],'size':size,'identical':diff.getbbox() is None,'max_channel_delta':max_delta,'changed_pixels':pixels,'equivalent':max_delta<=24 and pixels<=size*size*.025})
sheet=Image.new('RGB',(1000,4*145),'#fafafa');draw=ImageDraw.Draw(sheet)
ids=list(dict.fromkeys(f['id'] for f in data['frames']))
for frame in data['frames']:
 if frame['preset']!='Balanced':continue
 row=ids.index(frame['id']);col=[0,.15,.33,.5,.67,.85,1].index(frame['t']);x=col*140+40;y=row*145+30
 im=renderer.render(frame['svg'].encode(),64);sheet.paste(im,(x,y),im);draw.text((x,y+68),str(frame['t']),fill='black')
 draw.text((10,row*145+8),frame['id'],fill='black')
sheet.save(folder/'balanced-frames.png')
report={'browser_checks':data['checks'],'static_equivalence':static,'sampled_frames':len(data['frames']),'status':'pass' if not failed and all(s['equivalent'] for s in static) else 'failed','limitations':['Chromium only; deterministic frame sampling, not real device timing.']}
(folder/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
(folder/'frames.json').write_text(json.dumps(data['frames'])+'\n')
print('static equivalence',all(s['equivalent'] for s in static));print(folder/'balanced-frames.png')
