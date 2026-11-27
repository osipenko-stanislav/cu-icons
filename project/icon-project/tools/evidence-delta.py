from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
r=Path('icon-project/review/contact-sheets');parts=[]
for b,y0,y1 in [('005',850,1440),('006',110,300),('007',450,680),('009',300,680),('021',110,490),('027',1200,1440),('028',300,680),('032',110,300)]:
 im=Image.open(r/f'v2-batch-{b}-review.png');c=im.crop((0,y0,im.width,min(im.height,y1)));parts.append((b,c))
out=Image.new('RGB',(1050,sum(im.height+25 for _,im in parts)),'#f8f8f4');d=ImageDraw.Draw(out);y=0
for b,im in parts:d.text((10,y),b,fill='#000');y+=25;out.paste(im,(0,y));y+=im.height
out.save(r/'v2-corrections-detail.png')
