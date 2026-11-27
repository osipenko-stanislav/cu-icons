from pathlib import Path
import sys,json,subprocess,importlib.util,hashlib,base64,copy
import xml.etree.ElementTree as E
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]; TOOL=Path(__file__).with_name('iconizer-local.py'); PY=sys.executable
spec=importlib.util.spec_from_file_location('adapter',TOOL);adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
r=adapter.Renderer();FONT=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',11)
def cmd(*args):
 result=subprocess.run([PY,str(TOOL),'--project',str(ROOT),*map(str,args)],capture_output=True,text=True)
 if result.returncode:raise RuntimeError(result.stdout[-1600:]+result.stderr[-1600:])
 return result.stdout

def painted(raw,color):
 n=E.fromstring(raw)
 def walk(n,definition=False):
  definition=definition or n.tag.split('}')[-1] in ['mask','clipPath','defs']
  if not definition:
   for k in ['fill','stroke']:
    if n.get(k) and n.get(k) not in ['none','transparent'] and not n.get(k).startswith('url('):n.set(k,color)
  for ch in n:walk(ch,definition)
 walk(n);n.set('color',color)
 return E.tostring(n)

def sheet(batch,m):
 ids=[i for i in batch['ids'] if m['icons'][i]['path']];w=1050;cellw=210;cellh=190;top=110
 im=Image.new('RGB',(w,top+((len(ids)+4)//5)*cellh),'#f8f8f4');dr=ImageDraw.Draw(im)
 dr.text((12,8),globals().get('PREFIX','')+batch['id']+' | source / result light / result dark | 16, 24, 48 px',font=FONT,fill='#171717')
 # Shared original anchors, with preview-only paint normalization.
 anchors=['brand-doc-lined','calendar','brand-device-desktop-lined','brand-chip-lined','profile','brand-users2-lined','message','brand-shield-lined','heart','arrow-right','brand-home-lined']
 for j,a in enumerate(anchors):
  raw=(ROOT/m['references'][a]['path']).read_bytes();ink=r.render(painted(raw,'#171717'),32,ROOT/'review/cache');x=15+j*93;im.paste(ink,(x,30),ink);dr.text((x,68),a.replace('brand-','')[:15],font=FONT,fill='#555555')
 evidence={}
 for j,i in enumerate(ids):
  rec=m['icons'][i];raw=(ROOT/rec['path']).read_bytes();evidence[i]=hashlib.sha256(raw).hexdigest();src=m['sources'][rec['source']];old=(ROOT/src['path']).read_bytes()
  x=(j%5)*cellw;y=top+(j//5)*cellh
  dr.text((x+8,y+4),i.removesuffix('-lined')[:29],font=FONT,fill='#9c1f28' if rec['status']=='Validation failed' else '#171717')
  for row,(data,color,bg) in enumerate([(old,'#171717','#f8f8f4'),(raw,'#171717','#f8f8f4'),(raw,'#f1f3ef','#202428')]):
   yy=y+22+row*54
   if row==2:dr.rectangle((x+3,yy-1,x+cellw-4,yy+50),fill=bg)
   for size,dx in [(16,13),(24,62),(48,120)]:
    ink=r.render(painted(data,color),size,ROOT/'review/cache');im.paste(ink,(x+dx,yy+(48-size)//2),ink)
 path=ROOT/'review/contact-sheets'/(globals().get('PREFIX','')+batch['id']+'-review.png');im.save(path)
 path.with_suffix('.json').write_text(json.dumps({'png_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'icons':evidence,'references':anchors,'sizes':[16,24,48],'themes':['light','dark'],'source_comparison':True},indent=2)+'\n')
 return path

def main():
 m=json.loads((ROOT/'manifest.json').read_text());wanted=sys.argv[1:] or [b['id'] for b in m['batches'][1:]]
 for b in m['batches'][1:]:
  if b['id'] not in wanted:continue
  if any(m['icons'][i]['status']=='Pending' for i in b['ids']):cmd('submit-batch',b['id'],ROOT/'staging'/b['id'])
  m=json.loads((ROOT/'manifest.json').read_text());p=sheet(b,m)
  failed=[i for i in b['ids'] if m['icons'][i]['status']=='Validation failed']
  print(b['id'],len(b['ids']),'staged; technical failures:',','.join(failed) or 'none','sheet',p.name,flush=True)
if __name__=='__main__':main()
