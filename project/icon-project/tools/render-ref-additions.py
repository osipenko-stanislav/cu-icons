from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
from io import BytesIO
import json,resvg_py,xml.etree.ElementTree as E,hashlib
P=Path('icon-project');R=P/'review/motion/ref-additions-2026-11-27';data=json.loads((R/'browser-checks.json').read_text());ids=list(dict.fromkeys(f['id'] for f in data['frames']));font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',12)
for start in range(0,len(ids),7):
 batch=ids[start:start+7];im=Image.new('RGB',(1000,len(batch)*95),'white');draw=ImageDraw.Draw(im)
 for row,id in enumerate(batch):
  y=row*95;draw.text((8,y+5),id,font=font,fill='#111')
  for col,f in enumerate(f for f in data['frames'] if f['id']==id):
   sprite=Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=f['svg'],skip_system_fonts=True))).convert('RGBA');im.paste(sprite,(150+col*116,y+12),sprite);draw.text((160+col*116,y+65),str(round(f['t']*100))+'%',font=font,fill='#777')
  draw.line((0,y+94,1000,y+94),fill='#ddd')
 im.save(R/f'frames-{start//7+1:02}.png')
# Visible rest geometry must equal the imported currentColor SVG at all target sizes.
checks=[]
for id in ids:
 first=next(f for f in data['frames'] if f['id']==id and f['t']==0)
 for size in [16,24,48]:
  def render(raw):
   root=E.fromstring(raw);root.set('width',str(size));root.set('height',str(size));root.attrib.pop('style',None);root.set('color','#111');return Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=E.tostring(root).decode(),skip_system_fonts=True))).convert('RGBA')
  a=render(first['svg']);b=render((P/'motion/reference-series/svg'/(id+'.svg')).read_text());same=a.tobytes()==b.tobytes();checks.append({'id':id,'size':size,'rest_geometry_equal':same})
assert all(c['rest_geometry_equal'] for c in checks),[c for c in checks if not c['rest_geometry_equal']]
(R/'rest-equivalence.json').write_text(json.dumps(checks,indent=2)+'\n');print('Rendered',len(ids),'icons; rest geometry matches at 16/24/48px')
