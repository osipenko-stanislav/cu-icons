from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
import json,xml.etree.ElementTree as E,resvg_py
P=Path('icon-project');R=P/'review/motion/polish-2026-11-27';rows=[r for r in json.loads((R/'queue.json').read_text())['items'] if 'geometry' in r['tags']];catalog={r['id']:r for r in json.loads((P/'result/catalog.json').read_text())};font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',11)
def render(path):
 root=E.fromstring(path.read_bytes());root.set('width','48');root.set('height','48');root.set('color','#111')
 for n in root.iter():
  for k in ['stroke','fill']:
   if n.get(k) in ['black','white']:n.set(k,'#111')
  if 'stroke-width' in n.attrib:n.set('stroke-width','1')
 return Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=E.tostring(root).decode(),skip_system_fonts=True))).convert('RGBA')
for start in range(0,len(rows),24):
 batch=rows[start:start+24];im=Image.new('RGB',(1200,((len(batch)+3)//4)*120),'white');draw=ImageDraw.Draw(im)
 for i,row in enumerate(batch):
  id=row['icon'];x=i%4*300;y=i//4*120;draw.text((x+5,y+5),id,font=font,fill='#111')
  for p,dx,label in [(Path('work')/catalog[id]['file'],40,'work'),(P/'result/svg'/catalog[id]['file'],160,'current')]:
   sprite=render(p);im.paste(sprite,(x+dx,y+30),sprite);draw.text((x+dx,y+85),label,font=font,fill='#777')
  draw.line((x,y+119,x+300,y+119),fill='#ddd')
 im.save(R/f'geometry-before-{start//24+1:02}.png')
print('Rendered',len(rows),'geometry findings')
