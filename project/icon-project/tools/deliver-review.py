from pathlib import Path
import json,hashlib,base64,re,html,importlib.util,xml.etree.ElementTree as E,collections
from io import BytesIO
ROOT=Path(__file__).resolve().parents[1];sp=importlib.util.spec_from_file_location('runner',Path(__file__).with_name('run-series.py'));r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
m=json.loads((ROOT/'manifest.json').read_text());author=json.loads((ROOT/'review/reports/reference-series-authoring.json').read_text());retained={v['id']:v for v in json.loads((ROOT/'review/reports/v2-retained-geometry-review.json').read_text())};samples={v['id']:v for v in json.loads((ROOT/'review/reports/geometry-v2-samples.json').read_text())['samples']};baseline=json.loads((ROOT/'specification/v2-source-baseline.json').read_text())
# Confirm approved revisions and immutable inputs before assembling the review delivery.
for name in ['pilot-user-approval','geometry-v2-user-approval']:
 for a in json.loads((ROOT/'review/reports'/(name+'.json')).read_text())['decisions']:
  assert m['icons'][a['id']]['sha256']==a['sha256'] and m['icons'][a['id']]['status']=='Approved'
originals={re.sub(r'[^a-z0-9]+','-',p.stem.lower()).strip('-'):p for p in ROOT.parent.joinpath('work').glob('*.svg')};out=ROOT/'result/svg';out.mkdir(parents=True,exist_ok=True);catalog=[];raster=collections.defaultdict(list)
for i,icon in m['icons'].items():
 raw=(ROOT/icon['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==icon['sha256'];name=originals[i].name; (out/name).write_bytes(raw)
 catalog.append({'id':i,'file':name,'sha256':icon['sha256'],'status':icon['status'],'viewBox':'0 0 24 24'})
 raster[hashlib.sha256(r.r.render(raw,24,ROOT/'review/cache').getchannel('A').tobytes()).hexdigest()].append(i)
assert len(catalog)==len(originals)==1189
assert {p.name for p in out.glob('*.svg')}=={p.name for p in originals.values()}
for folder,key in [('ref','references'),('work','sources')]:
 assert {hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.parent.joinpath(folder).glob('*.svg')}=={v['sha256'] for v in m[key].values()}
(ROOT/'result/catalog.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n')
dup={'method':'Exact alpha-mask equality at 24px; source IDs and names preserved; no exhaustive near-similarity scan','groups':[ids for ids in raster.values() if len(ids)>1],'policy':'Under the user-approved reference-first construction policy, source alternatives can become visual aliases. Keep every source filename; do not deduplicate automatically.'}
(ROOT/'review/reports/v2-duplicates.json').write_text(json.dumps(dup,indent=2)+'\n')
summary={'total':len(catalog),'user_approved':sum(i['status']=='Approved' for i in catalog),'agent_reviewed':sum(i['status']=='AI reviewed' for i in catalog),'unprocessed':sum(i['status'] not in ['Approved','AI reviewed'] for i in catalog),'geometry_changes_with_neutral_stroke':json.loads((ROOT/'review/reports/v2-contour-change.json').read_text())['changed'],'exact_alias_groups_at_24px':len(dup['groups']),'original_filenames_preserved':True,'originals_unchanged':True,'canvas':[24,24],'visual_review':'Sequential, all batches at 16/24/48px in light/dark; revised details rechecked. No independent critic.','approval_scope':'47 concrete shown SVGs approved by the user; 1142 series SVGs ready for final user review.','release_status':'complete-review-set; final user approval remains separate'}
(ROOT/'result/status.json').write_text(json.dumps(summary,indent=2)+'\n')
# Build a complete reference/source/v1/current review page from the native skill gallery.
text=(ROOT/'gallery/index.html').read_text().replace('<p><a href="review.html">Открыть полный набор с четырьмя вариантами сравнения</a></p>','');match=re.search(r'(<script id="data" type="application/json">)(.*?)(</script>)',text,re.S);data=json.loads(match[2])
def uri(raw):return 'data:image/svg+xml;base64,'+base64.b64encode(raw).decode()
def preview(ustr):
 if not ustr or not ustr.startswith('data:image/svg+xml'):return ustr
 return uri(r.painted(base64.b64decode(ustr.split(',')[1]),'currentColor'))
def reference(name):
 item=m['references'].get(name)
 if not item:return None
 u=data['references'].get(name)
 if u:return preview(u)
 raw=r.painted((ROOT/item['path']).read_bytes(),'#171717');ink=r.r.render(raw,128,ROOT/'review/cache');buf=BytesIO();ink.save(buf,format='PNG');return 'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()
# Existing-pilot anchors are known from the original approved construction.
pilot_refs={'arrow-left-lined':'arrow-right','arrow-right-lined':'arrow-left','heart-lined':'heart','home-01-lined':'brand-home-lined','file-02-lined':'brand-doc-lined','file-plus-02-lined':'brand-doc-lined','calendar-lined':'calendar','calendar-check-01-lined':'calendar','monitor-01-lined':'brand-device-desktop-lined','cpu-chip-01-lined':'brand-chip-lined','user-01-lined':'profile','users-01-lined':'brand-users2-lined','users-plus-lined':'users-plus','message-square-01-lined':'message','message-text-square-01-lined':'message','shield-tick-lined':'brand-shield-lined','rocket-01-lined':'brand-rocket-lined','book-open-01-lined':'book','bell-01-lined':'bell','trash-01-lined':'trash','credit-card-lock-lined':'brand-briefcase-lined','folder-question-lined':'brand-doc-lined','settings-01-lined':'brand-chip-lined','cloud-raining-01-lined':'steam'}
chosen=[]
for icon in data['icons']:
 i=icon['id'];a=author.get(i,{})
 anchor=samples[i]['reference'] if i in samples else pilot_refs.get(i) or retained.get(i,{}).get('reference') or a.get('reference','brand-code-lined')
 anchor=anchor.split(' / ')[0].split(' (')[0]
 if anchor not in m['references']:anchor='brand-doc-lined' if icon['family'] in ['folder','file'] else 'brand-code-lined'
 icon['referencePreview']=reference(anchor);icon['referenceName']=anchor;icon['original']=preview(icon.get('original'));icon['outputName']=originals[i].name
 previous=baseline.get(i,{}).get('path') or samples.get(i,{}).get('previous_path') or m['icons'][i]['path']
 icon['previousPreview']=uri((ROOT/previous).read_bytes())
 icon['meaning']='Основа геометрии: '+anchor
 chosen.append(anchor)
refs=list(dict.fromkeys(['brand-home-lined','brand-doc-lined','brand-users2-lined','brand-device-desktop-lined','brand-chip-lined','brand-shield-lined','brand-rocket-lined','brand-briefcase-lined','brand-code-lined','brand-chart-lined','flag','trophy','reward','brand-glasses-lined','calendar','profile','clock','heart','message','filter','download','data','sun-lined','brand-smile-lined']))
data['references']={name:reference(name) for name in refs}
payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c');text=text[:match.start(2)]+payload+text[match.end(2):]
text=text.replace('<title>Icon library review</title>','<title>CU · полный набор 1189 иконок</title>')
text=text.replace('<h1>Icon library review</h1>','<h1>Полный набор · 1189 иконок</h1><p>Форма ref приоритетна; смысл work сохраняется. Все имена файлов сохранены. В карточке: эталон, исходник, первая серия и текущая геометрия.</p><p>47 показанных SVG утверждены вами; 1142 иконки серии прошли техническую и последовательную визуальную проверку и доступны для финального просмотра. Размер 16/24 px — рабочий, 48/64 px — детали.</p>')
text=text.replace("[['Original',icon.original],['Current',icon.uri]]", "[['Стилевой ориентир ref',icon.referencePreview],['Исходник work',icon.original],['Первая серия v1',icon.previousPreview],['Текущий SVG',icon.uri]]")
text=text.replace('<button id="copy">Copy SVG</button>','<button id="copy">Copy SVG</button><button id="downloadOne">Скачать SVG для проверки</button>')
text=text.replace("$('facts').textContent=", "$('downloadOne').disabled=!icon.uri?.startsWith('data:image/svg+xml');\n  $('facts').textContent=")
text=text.replace("$('saveComment').onclick=", "$('downloadOne').onclick=()=>{if(current?.uri?.startsWith('data:image/svg+xml'))download(dec(current.uri),current.outputName||current.id+'.svg','image/svg+xml');};\n$('saveComment').onclick=")
text=text.replace('[icon.id,icon.name,icon.meaning,icon.metaphor]','[icon.id,icon.name,icon.meaning,icon.metaphor,icon.outputName]')
text=text.replace('</style>', '.dark img[src^="data:image/png"]{filter:invert(1)}</style>')
text=text.replace('<details open><summary>Reference icons</summary>','<details><summary>Reference icons</summary>')
(ROOT/'gallery/review.html').write_text(text)
(ROOT/'result/README.md').write_text('''# CU · полный набор для финального просмотра

1189 редактируемых SVG в `svg/`. Исходные имена файлов, включая регистр, сохранены. Исходные папки ref/work не изменены.

Основа: форма ref приоритетна, смысл work сохраняется. Общая сетка 24×24, живая линия 1, монохромный currentColor. Три нестандартных исходных холста 16×16/40×40 приведены к 24×24. Некоторые варианты стали визуальными алиасами вслед за унификацией под ref; все ID и имена оставлены.

Просмотр: http://127.0.0.1:8765/review.html (если локальный сервер работает) или `../gallery/review.html` как автономный HTML. Карточка показывает ref/work/v1/текущий SVG. Есть поиск, фильтры, размеры и тема.

Проверка: все SVG технически валидны; силуэты просмотрены на 16/24/48 px в двух темах, без независимого критика. Отдельно проверены границы холста. Отчёты и хеши — в `../review/reports/` и `catalog.json`.

Статусы: 47 конкретных показанных SVG утверждены пользователем. Остальные 1142 прошли проверку агента и доступны для финального пользовательского просмотра. Этот каталог — полный набор результатов для ревью; статус окончательного утверждения отделён от технической готовности.
''')
print(json.dumps(summary,ensure_ascii=False),flush=True)
