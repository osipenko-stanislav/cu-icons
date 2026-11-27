from pathlib import Path
import json,re,base64,xml.etree.ElementTree as E
from io import BytesIO
import importlib.util
sp=importlib.util.spec_from_file_location('adapter',Path(__file__).with_name('iconizer-local.py'));adapter=importlib.util.module_from_spec(sp);sp.loader.exec_module(adapter)
root=Path('icon-project');text=(root/'gallery/index.html').read_text()
pattern=r'(<script id="data" type="application/json">)(.*?)(</script>)'
match=re.search(pattern,text,re.S); data=json.loads(match[2]);ids=json.loads((root/'pilot-ids.json').read_text()); data['icons']=[i for i in data['icons'] if i['id'] in ids]
anchors=['arrow-right','arrow-left','heart','brand-home-lined','brand-doc-lined','brand-doc-lined','calendar','calendar','brand-device-desktop-lined','brand-chip-lined','profile','brand-users2-lined','users-plus','message','message','brand-shield-lined','brand-rocket-lined','book','bell','trash','case','brand-doc-lined','brand-chip-lined','steam']
def paint_preview(uri):
 if not uri or not uri.startswith('data:image/svg+xml'):return uri
 node=E.fromstring(base64.b64decode(uri.split(',')[1]))
 for e in node.iter():
  for k in ['stroke','fill']:
   if e.get(k) in ['white','black','#141414','#D9D9D9']:e.set(k,'currentColor')
 return 'data:image/svg+xml;base64,'+base64.b64encode(E.tostring(node)).decode()
# Render masked references as PNG evidence rather than injecting SVG outside the skill profile.
for name in dict.fromkeys(anchors):
 if data['references'].get(name):continue
 node=E.parse(Path('ref')/(name+'.svg')).getroot()
 def recolor(el,definition=False):
  definition=definition or el.tag.split('}')[-1] in ['mask','clipPath','defs']
  if not definition:
   for key in ['stroke','fill']:
    if el.get(key) in ['white','black','#141414','#D9D9D9']:el.set(key,'#171717')
  for ch in el:recolor(ch,definition)
 recolor(node);image=adapter.Renderer().render(E.tostring(node),128);buf=BytesIO();image.save(buf,format='PNG')
 image.save(root/'review/contact-sheets'/('reference-'+name+'.png'))
 data['references'][name]='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()
for i in data['icons']:
 n=anchors[ids.index(i['id'])];i['referencePreview']=paint_preview(data['references'][n]); i['original']=paint_preview(i['original'])
data['references']={k:paint_preview(data['references'][k]) for k in dict.fromkeys(anchors)}
payload=json.dumps(data,ensure_ascii=False,separators=(',',':'))
text=text[:match.start(2)]+payload+text[match.end(2):]
text=text.replace('</style>','.dark img[src^="data:image/png"]{filter:invert(1)}</style>')
text=text.replace('<title>Icon library review</title>','<title>CU · пилот 24 иконки</title>').replace('<h1>Icon library review</h1>','<h1>Пилот · 24 из 1189 иконок</h1><p>Исходник → результат по стилю ref. Откройте карточку для сравнения с ближайшим эталоном. Для сравнения цвета эталонов и исходников приведены к общему цвету только в предпросмотре.</p><p>Проверьте 16 и 24 px; 64 px позволяет рассмотреть геометрию. Замечания и утверждение можно написать в чате. Вся библиотека ожидает утверждения этого пилота.</p>')
text=text.replace("[['Original',icon.original],['Current',icon.uri]]","[['Ближайший эталон',icon.referencePreview],['Исходник',icon.original],['Результат',icon.uri]]")
(root/'gallery/pilot.html').write_text(text)
print(root/'gallery/pilot.html')
