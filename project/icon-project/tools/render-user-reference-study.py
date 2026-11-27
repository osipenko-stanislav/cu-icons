from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
import json,resvg_py
R=Path('icon-project/review/motion/user-selection-2026-11-27');rows=json.loads((R/'frames.json').read_text())['rows'];font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',12)
for start in range(0,len(rows),8):
 batch=rows[start:start+8];im=Image.new('RGB',(1000,len(batch)*130),'white');draw=ImageDraw.Draw(im)
 for i,row in enumerate(batch):
  y=i*130;draw.text((8,y+4),row['reference']+' / '+(row['project_id'] or 'no current icon'),font=font,fill='#111')
  for side,dy,label in [('source',24,'reference'),('project',76,'current')]:
   draw.text((8,y+dy+12),label,font=font,fill='#666')
   for j,f in enumerate(row[side] or []):
    sprite=Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=f['svg'],skip_system_fonts=True))).convert('RGBA');im.paste(sprite,(110+j*123,y+dy),sprite)
    if side=='source':draw.text((162+j*123,y+dy+16),str(round(f['t']*100))+'%',font=font,fill='#888')
  draw.line((0,y+129,1000,y+129),fill='#ddd')
 im.save(R/f'comparison-{start//8+1:02}.png')
print('Rendered four sheets')
