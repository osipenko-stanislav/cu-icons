from pathlib import Path
import json,re,html,collections,xml.etree.ElementTree as E
from PIL import Image,ImageChops,ImageDraw,ImageFont
from io import BytesIO
import resvg_py
P=Path('icon-project');R=P/'review/motion/stability-2026-11-27';out={'items':[],'checks':[],'errors':[]}
out=json.loads((R/'browser-capture.json').read_text())
(R/'browser-capture.json').write_text(json.dumps(out));bad=[r for r in out['checks'] if any(v is False for v in r.values())];colors=[r['id'] for r in out['items'] if r['paintFailures']];print('scenes',len(out['items']),'checks',len(out['checks']),'errors',out['errors'][:5],'failed',bad[:8],'color failures',colors)
summary={'scene_count':len(out['items']),'checks':len(out['checks']),'failures':bad,'errors':out['errors'],'color_failures':colors,'themes':['dark ink','light ink','accent blue'],'phases':[0,.13,.25,.37,.5,.61,.75,.83,1],'presets':['Smooth','Balanced','Expressive'],'one_animation_for_all_sizes':True};(R/'checks.json').write_text(json.dumps(summary,indent=2)+'\n')
before={r['id']:r for r in json.loads((P/'review/motion/materials-audit-2026-11-27/browser-capture.json').read_text())['items']};after={r['id']:r for r in out['items']};ids=[r['id'] for r in json.loads((R/'motion-repairs.json').read_text())]+[r['id'] for r in json.loads((R/'state-pairs.json').read_text())];font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',11)
def render(raw,size):
 root=E.fromstring(raw);root.set('width',str(size));root.set('height',str(size));root.set('style','color:#111')
 for n in root.iter():
  if n.tag.split('}')[-1] in ['path','rect','circle','ellipse','line','polygon','polyline'] and n.get('stroke')!='none':n.set('stroke-width',str(24/size))
 return Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=E.tostring(root).decode(),skip_system_fonts=True))).convert('RGBA')
metrics=[]
for start in range(0,len(ids),8):
 selected=ids[start:start+8];im=Image.new('RGB',(1040,len(selected)*104),'white');draw=ImageDraw.Draw(im)
 for i,id in enumerate(selected):
  y=i*104;draw.text((5,y+5),id,font=font,fill='black')
  for k,(size,which) in enumerate([(16,'before'),(16,'after'),(32,'before'),(32,'after')]):
   row=(before if which=='before' else after)[id];draw.text((230+k*200,y+5),f'{which} {size}px',font=font,fill='black');sprites=[]
   for j,fi in enumerate([0,1,3,5,8]):
    sprite=render(row['frames'][fi]['svg'],size);im.paste(sprite,(230+k*200+j*37,y+40),sprite);sprites.append(sprite.getchannel('A'))
   maxdiff=max(sum(ImageChops.difference(sprites[0],x).getdata())/255 for x in sprites[1:]);metrics.append({'id':id,'size':size,'revision':which,'max_changed_pixel_equivalents':round(maxdiff,3)})
  draw.line((0,y+103,1040,y+103),fill='#ddd')
 im.save(R/f'before-after-{start//8+1:02}.png')
(R/'raster-screening.json').write_text(json.dumps(metrics,indent=2)+'\n')
