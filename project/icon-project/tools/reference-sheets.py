from pathlib import Path
import sys, xml.etree.ElementTree as E
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent))
import importlib.util
sp=importlib.util.spec_from_file_location('adapter',Path(__file__).with_name('iconizer-local.py')); m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
r=m.Renderer(); files=sorted(Path('ref').glob('*.svg')); font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',12)
for start in range(0,len(files),30):
 im=Image.new('RGB',(1000,140+((min(30,len(files)-start)+5)//6)*125),'#f6f5f2'); dr=ImageDraw.Draw(im)
 dr.text((20,18),'REF / original geometry, preview paint normalized to black / 24 and 64 px',font=font,fill='#111111')
 for i,p in enumerate(files[start:start+30]):
  node=E.fromstring(p.read_bytes())
  for e in node.iter():
   for k in ['fill','stroke']:
    if e.get(k) in ['white','black','#141414','#D9D9D9']:e.set(k,'#171717')
  raw=E.tostring(node); x=15+(i%6)*165;y=70+(i//6)*125
  for sz,dx in [(24,12),(64,55)]:
   ink=r.render(raw,sz); im.paste(ink,(x+dx,y),ink)
  dr.text((x,y+75),p.stem,font=font,fill='#111111')
 out=Path('icon-project/review/contact-sheets')/f'references-normalized-{start//30+1}.png';out.parent.mkdir(parents=True,exist_ok=True);im.save(out); print(out)
