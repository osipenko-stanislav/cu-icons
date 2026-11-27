from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
from io import BytesIO
import json,xml.etree.ElementTree as E,resvg_py
P=Path('icon-project');R=P/'review/motion/polish-2026-11-27';d=json.loads((R/'browser-checks.json').read_text());ids=[r['id'] for r in json.loads((R/'authored-batch.json').read_text())];frames={id:[f for f in d['frames'] if f['id']==id] for id in ids};font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',11)
def render(raw,size=40):
 root=E.fromstring(raw);root.set('width',str(size));root.set('height',str(size));root.set('style','color:#111')
 for n in root.iter():
  if n.tag.split('}')[-1] in ['path','circle','ellipse','line','rect','polyline','polygon']:n.set('stroke-width',str(24/size))
 return Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=E.tostring(root).decode(),skip_system_fonts=True))).convert('RGBA')
for start in range(0,len(ids),32):
 batch=ids[start:start+32];im=Image.new('RGB',(1100,((len(batch)+1)//2)*95),'white');draw=ImageDraw.Draw(im)
 for i,id in enumerate(batch):
  x=i%2*550;y=i//2*95;draw.text((x+7,y+5),id,font=font,fill='#111')
  for j,f in enumerate(frames[id]):
   sprite=render(f['svg']);im.paste(sprite,(x+15+j*74,y+24),sprite);draw.text((x+26+j*74,y+69),str(round(f['t']*100)),font=font,fill='#888')
  draw.line((x,y+94,x+550,y+94),fill='#ddd')
 im.save(R/f'frames-{start//32+1:02}.png')
# Compare the first rendered pose to current native source; keep quantified
# differences for masks and state assemblies that need visual interpretation.
rest=[]
for id in ids:
 raw=(P/'motion/reference-series/svg'/(id+'.svg')).read_text();first=next(f for f in frames[id] if f['t']==0)
 a=render(raw,48);b=render(first['svg'],48);diff=ImageChops.difference(a.getchannel('A'),b.getchannel('A'));rest.append({'id':id,'mean_alpha_difference':sum(diff.getdata())/(48*48*255),'max_alpha_difference':diff.getextrema()[1]})
(R/'rest-differences.json').write_text(json.dumps(rest,indent=2)+'\n');print('Rendered',len(ids),'scenes in eight sheets');print('Rest differences requiring visual review',[(r['id'],round(r['mean_alpha_difference'],4)) for r in rest if r['mean_alpha_difference']>.008])
