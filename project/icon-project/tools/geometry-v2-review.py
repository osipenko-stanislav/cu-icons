from pathlib import Path
import json,base64,html,importlib.util,hashlib,xml.etree.ElementTree as E
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];sp=importlib.util.spec_from_file_location('runner',Path(__file__).with_name('run-series.py'));s=importlib.util.module_from_spec(sp);sp.loader.exec_module(s)
m=json.loads((ROOT/'manifest.json').read_text());samples=json.loads((ROOT/'review/reports/geometry-v2-samples.json').read_text())['samples'];font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',13)
columns=['work / original','ref / geometry anchor','v1 / rejected approach','v2 / reference form']
rows=[]
for i in samples:
 src=m['sources'][m['icons'][i['id']]['source']]
 files=[ROOT/src['path'],ROOT/m['references'][i['reference']]['path'],ROOT/i['previous_path'],ROOT/'staging/geometry-v2'/(i['id']+'.svg')]
 images=[s.painted(p.read_bytes(),'#171717') for p in files];rows.append((i,images))
for start in range(0,len(rows),12):
 group=rows[start:start+12];im=Image.new('RGB',(980,70+len(group)*125),'#f8f8f4');d=ImageDraw.Draw(im)
 d.text((15,10),'GEOMETRY REVISION / compare 48 px and actual 24 px / v1 and v2 share 1-unit stroke',font=font,fill='#171717')
 for k,label in enumerate(columns):d.text((230+k*184,40),label,font=font,fill='#444444')
 for j,(rec,images) in enumerate(group):
  y=70+j*125;d.text((12,y+12),rec['id'].removesuffix('-lined'),font=font,fill='#171717');d.text((12,y+37),rec['reference'][:27],font=font,fill='#666666')
  for k,raw in enumerate(images):
   for size,dy in [(48,0),(24,65)]:
    ink=s.r.render(raw,size,ROOT/'review/cache');im.paste(ink,(265+k*184+(48-size)//2,y+dy),ink)
 p=ROOT/'review/contact-sheets'/f'geometry-v2-{start//12+1}.png';im.save(p)
 p.with_suffix('.json').write_text(json.dumps({'png_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'icons':{rec['id']:hashlib.sha256((ROOT/'staging/geometry-v2'/(rec['id']+'.svg')).read_bytes()).hexdigest() for rec,_ in group},'sizes':[24,48],'comparison':columns},indent=2)+'\n')
 print(p)
def uri(raw):return 'data:image/svg+xml;base64,'+base64.b64encode(raw).decode()
body=[]
for rec,images in rows:
 pictures=''.join('<figure><img alt="'+html.escape(label)+'" src="'+uri(raw)+'"><figcaption>'+html.escape(label)+'</figcaption></figure>' for label,raw in zip(['Исходник work','Основа геометрии ref','Первая серия · v1','Перерисовано · v2'],images))
 body.append('<article><h2>'+html.escape(rec['id'])+'</h2><p class="anchor">ref: '+html.escape(rec['reference'])+'</p><div class="comparison">'+pictures+'</div><p>'+html.escape(rec['reason'])+'</p></article>')
text='''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Геометрия · исправление серии</title><style>
*{box-sizing:border-box}body{margin:0 auto;padding:32px;max-width:1100px;background:#f8f8f4;color:#171717;font:15px/1.5 system-ui}h1{font-size:28px;line-height:1.2}h2{font-size:16px;margin:0}.lead{max-width:830px}.toolbar{position:sticky;top:0;background:#f8f8f4;padding:16px 0;display:flex;gap:24px;border-bottom:1px solid #ccc}button,select{font:inherit;padding:4px 8px}article{padding:24px 0;border-bottom:1px solid #ccc}.anchor{font-size:13px;color:#666;margin:4px 0 20px}.comparison{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}figure{margin:0;min-height:105px;text-align:center;padding:14px 0;background:#efefea}img{width:48px;height:48px;display:block;margin:0 auto 14px}figcaption{font-size:13px}.dark{background:#202428;color:#f1f3ef}.dark .toolbar{background:#202428}.dark figure{background:#303438}.dark img{filter:invert(1)}.dark .anchor{color:#aaa}@media(max-width:600px){body{padding:16px}.comparison{gap:4px}figcaption{font-size:10px}}
</style><h1>Исправление геометрии · 23 примера</h1><p class="lead">После вашего замечания: <b>форма ref приоритетна, смысл work сохраняется</b>. У v1 и v2 одинаковая толщина линии — 1 px на сетке 24×24. Сравниваем именно контуры, пропорции и детали. Эталоны и исходники сохранены; цвет приведён к общему только в превью.</p><p class="lead">Пилот из 24 иконок остаётся утверждённым. Первая массовая серия требует пересмотра; эти 23 примера показывают исправленный способ построения.</p><div class="toolbar"><label>Размер <select id="size"><option>16</option><option>24</option><option>32</option><option selected>48</option><option>64</option></select> px</label><label><input id="theme" type="checkbox"> Тёмный фон</label></div>'''+''.join(body)+'''<script>document.getElementById('size').onchange=e=>{for(const i of document.images){i.style.width=i.style.height=e.target.value+'px'}};document.getElementById('theme').onchange=e=>document.body.classList.toggle('dark',e.target.checked);</script></html>'''
(ROOT/'gallery/geometry-v2.html').write_text(text)
