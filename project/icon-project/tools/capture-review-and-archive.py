"""Capture supplied feedback and create reversible semantic collections; retain source catalog."""
from pathlib import Path
import json,re,hashlib,shutil,collections,html
P=Path('icon-project');R=P/'review/user-feedback/2026-11-26';A=P/'archive/semantic-duplicates';C=P/'result/curated';O=P/'motion/reference-series'
if (P/'review/motion/user-selection-2026-11-27/additional-archive.json').exists():
 raise SystemExit('Initial archive is superseded. Do not overwrite the supplemental archive or later ref additions.')
SOURCE=Path('/Users/st.osipenko/.codex/attachments/c6a10184-d1b3-409c-b54d-b86b82d28e7e/Pasted text.txt')
if (R/'source-feedback.json').exists():SOURCE=R/'source-feedback.json'
raw=SOURCE.read_bytes();receipt=json.loads(raw);feedback=receipt['needsRevision'];catalog=json.loads((P/'result/catalog.json').read_text());byid={r['id']:r for r in catalog};notes={r['icon']:r for r in feedback}
assert len(notes)==len(feedback) and not set(notes)-set(byid)
positive={'ок','хорошо','супер','отлично','кайф','это отлично','это вообще кайф','хороший пример','норм'}
def classify(r):
 t=r['comment'].strip().lower();tags=[]
 if t in positive:return 'positive',[]
 if re.search('геометр|геомер',t):tags.append('geometry')
 if any(w in t for w in ['динамик','двигаться','двигай','разводить','анимируй','анимируем']):tags.append('object-or-part-motion')
 if 'маск' in t:tags.append('mask-and-stationary-frame')
 if any(w in t for w in ['строук','строуком']):tags.append('stroke-choice')
 if any(w in t for w in ['зацик','зацикл']):tags.append('loop')
 if any(w in t for w in ['старая','прошлая','верни','была лучше']):tags.append('previous-version')
 if any(w in t for w in ['не одновременно','по-разному']):tags.append('stagger')
 if not tags or any(w in t for w in ['анимац','плохо','брак','не подходит','не нравится']):tags.append('motion-review')
 return 'revision',tags
# Explicitly selected synonymous variant families. Numeric content, chart content,
# panel counts, document payloads and ambiguous metaphors are kept outside this rule.
allowed=set('''align-bottom align-horizontal-centre align-left align-right align-top align-vertical-center announcement asterisk attachment bell bell-off bell-ringing bold book-open briefcase calendar-check calendar-heart calendar-minus calendar-plus camera car check-done check-verified cloud cloud-blank code-circle code-square copy cpu-chip credit-card crop cursor cursor-click database diamond disc dotpoints download download-cloud edit file-attachment file-check file-code file-download file-heart file-lock file-minus file-plus file-question file-search file-shield file-x film filter-funnel fingerprint gaming-pad gift git-branch glasses globe-slated graduation-hat hash headphones hexagon horizontal-bar-chart hourglass inbox italic key keyboard laptop layers-three layers-two left-indent life-buoy lightning link link-broken link-external loading lock lock-unlocked log-in log-out luggage magic-wand mail maximize message-circle message-square message-text-circle message-text-square microphone microphone-off minimize modem monitor moon music-note navigation-pointer navigation-pointer-off pen-tool pencil percent phone phone-call phone-incoming phone-outgoing piggy-bank pilcrow pin power presentation-chart puzzle-piece qr-code right-indent rocket rss save scissors scissors-cut send shield shopping-bag shopping-cart shuffle snowflake speaker strikethrough tablet tag thermometer ticket tool translate trash trophy truck tv type type-strikethrough umbrella underline upload upload-cloud user user-check user-down user-left user-minus user-plus user-right user-up user-x wallet webcam'''.split())
def semantic_key(id):
 s=id.removesuffix('-lined');k=re.sub(r'-\d+(?=-|$)','',s)
 if k in allowed:return k
 # Narrow/plain arrow names express the same action; keep frame, direction,
 # double/single and filled/block distinctions outside this synonym rule.
 if re.fullmatch(r'arrow-(?:narrow-)?(?:up|down|left|right|up-left|up-right|down-left|down-right)',s):return s.replace('arrow-narrow-','arrow-')
 return None
potential=collections.defaultdict(list)
for r in catalog:
 k=semantic_key(r['id'])
 if k:potential[k].append(r['id'])
# Visual review separates text alignment from object alignment, a handset from
# a mobile device, open/closed mail, and single objects from collections.
for key in ['align-left','align-right']:
 potential[key]=[i for i in potential[key] if i!=key+'-lined']
potential['phone']=['phone-01-lined','phone-02-lined']
potential['mail-closed']=['mail-01-lined','mail-02-lined','mail-03-lined']
potential['mail-open']=['mail-04-lined','mail-05-lined']
potential.pop('mail',None)
for key,id in [('tag','tag-03-lined'),('film','film-03-lined'),('monitor','monitor-05-lined')]:
 potential[key]=[i for i in potential[key] if i!=id]
for key in ['disc','tool']:
 potential.pop(key,None)
# These are independently checked semantic aliases, rather than a generic
# removal of numbered suffixes across the catalog.
for key,ids in {'attachment':['attachment-01-lined','attachment-02-lined','paperclip-lined'],'colors':['colors-lined','colors-lined-1']}.items():
 potential[key]=[i for i in ids if i in byid]
# Keep directional variants and state opposites separate.
def rank(id):
 r=notes.get(id);state,tags=classify(r) if r else ('unreviewed',[])
 feedback_score=100 if state=='positive' else 0 if state=='unreviewed' else -30 if 'geometry' in tags else -10
 return (-feedback_score, -int(byid[id].get('status')=='User approved'),bool(re.search(r'-\d+(?:-|$)',id)),len(id),id)
groups=[];archived={}
for key,ids in sorted(potential.items()):
 if len(ids)<2:continue
 ids=sorted(set(ids),key=rank);canonical=ids[0];duplicates=ids[1:]
 groups.append({'meaning_key':key,'canonical':canonical,'archived':duplicates,'basis':'Same named action/metaphor and modifier; stylistic variants or explicit synonyms. Numeric content/count groups excluded.','canonical_selection':'Prefer a pure positive user review; then an unreviewed candidate over a reported defect; use existing approval/name only to break ties. This is a reversible working selection.'})
 for id in duplicates:
  assert id not in archived;archived[id]=canonical
active=[r for r in catalog if r['id'] not in archived];archive=[r for r in catalog if r['id'] in archived]
for folder in [R,A,C]:folder.mkdir(parents=True,exist_ok=True)
(R/'source-feedback.json').write_bytes(raw)
motion=json.loads((O/'motion.json').read_text());scenes={s['id']:s for s in motion['scenes']};manifest={r['id']:r for r in json.loads((O/'manifest.json').read_text())}
normalized=[]
for r in feedback:
 state,tags=classify(r);id=r['icon'];normalized.append({**r,'review_status':state,'tags':tags,'collection':'archive' if id in archived else 'active','canonical':archived.get(id,id),'current_static_sha256':byid[id]['sha256'],'current_scene_sha256':hashlib.sha256(json.dumps(scenes[id],sort_keys=True).encode()).hexdigest(),'hash_binding':'Captured at import for traceability; supplied receipt has no scene hashes.'})
(R/'feedback.json').write_text(json.dumps({'version':1,'project':receipt['project'],'source_sha256':hashlib.sha256(raw).hexdigest(),'entries':normalized},ensure_ascii=False,indent=2)+'\n')
(R/'reviewed-motion-snapshot.json').write_text(json.dumps({**{k:v for k,v in motion.items() if k!='scenes'},'scenes':[scenes[r['icon']] for r in feedback]},separators=(',',':'))+'\n')
for folder,items in [(C,active),(A,archive)]:
 for sub in ['svg','geometry','animation']:(folder/sub).mkdir(exist_ok=True)
 for r in items:
  id=r['id'];shutil.copy2(O/'svg'/(id+'.svg'),folder/'svg'/r['file']);shutil.copy2(O/'geometry'/(id+'.svg'),folder/'geometry'/(id+'.svg'))
  if (O/'animation'/(id+'.json')).exists():shutil.copy2(O/'animation'/(id+'.json'),folder/'animation'/(id+'.json'))
  assert hashlib.sha256((folder/'svg'/r['file']).read_bytes()).hexdigest()==r['sha256']
 (folder/'catalog.json').write_text(json.dumps([{**r,'canonical':archived.get(r['id'],r['id'])} for r in items],ensure_ascii=False,indent=2)+'\n')
 (folder/'motion.json').write_text(json.dumps({**{k:v for k,v in motion.items() if k!='scenes'},'scenes':[scenes[r['id']] for r in items]},separators=(',',':'))+'\n')
 (folder/'trigger-overrides.json').write_text(json.dumps({k:v for k,v in json.loads((O/'trigger-overrides.json').read_text()).items() if k in {r['id'] for r in items}},indent=2)+'\n')
 (folder/'review-status.json').write_text(json.dumps([n for n in normalized if n['icon'] in {r['id'] for r in items}],ensure_ascii=False,indent=2)+'\n')
 # The player is copied for preserving behavior, not regenerated.
 shutil.copy2(P/'motion/exact-reference/assets/player.js',folder/'player.js')
 for name,source in [('useAnimations-MIT.txt',P/'references/motion/useanimations/LICENSE.txt'),('lottie-web-MIT.md',P/'motion/exact-reference/vendor/LICENSE.lottie-web.md')]:
  (folder/'licenses').mkdir(exist_ok=True);shutil.copy2(source,folder/'licenses'/name)
(A/'groups.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2)+'\n');(A/'aliases.json').write_text(json.dumps(archived,indent=2)+'\n')
counts=collections.Counter(n['review_status'] for n in normalized);tags=collections.Counter(t for n in normalized for t in n['tags'])
summary={'source_entries':len(feedback),'positive':counts['positive'],'revision':counts['revision'],'unreviewed':len(catalog)-len(feedback),'semantic_groups':len(groups),'active':len(active),'archived':len(archive),'tag_counts':dict(tags),'source_receipt_sha256':hashlib.sha256(raw).hexdigest(),'original_full_catalog_preserved':True,'animation_revisions_implemented':False,'motion_classes_status':'Four-class proposal recorded; not yet approved or implemented.'}
(R/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
# A complete feedback register retains original wording, including positive records
# carried by the receipt's misleading needsRevision field.
lines=['# Все замечания пользователя','',f"Всего {len(normalized)} записей. Исходные формулировки сохранены; ключ needsRevision не определяет статус.",'','| Иконка | Оценка | Коллекция | Комментарий | Preset / скорость / обводка |','| --- | --- | --- | --- | --- |']
for n in normalized:
 comment=n['comment'].replace('|','\\|').replace('\n','<br>');lines.append(f"| `{n['icon']}` | {'Положительная' if n['review_status']=='positive' else 'Правка'} | {n['collection']} | {comment} | {n['preset']} / {n['speed']}× / {n['strokeWidth']} px |")
(R/'COMMENTS.md').write_text('\n'.join(lines)+'\n')
# Compact semantic rows for visual verification; SVG files remain editable assets.
from PIL import Image,ImageDraw,ImageFont
import resvg_py
from io import BytesIO
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',11)
for start in range(0,len(groups),35):
 batch=groups[start:start+35];im=Image.new('RGB',(1200,len(batch)*64),'white');draw=ImageDraw.Draw(im)
 for row,g in enumerate(batch):
  y=row*64;draw.text((8,y+5),g['meaning_key'],font=font,fill='#111')
  for col,id in enumerate([g['canonical']]+g['archived']):
   x=220+col*120;rawsvg=(O/'svg'/(id+'.svg')).read_text().replace('currentColor','#111');sprite=Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=rawsvg.replace('width="24"','width="32"').replace('height="24"','height="32"'),skip_system_fonts=True))).convert('RGBA');im.paste(sprite,(x,y+3),sprite);draw.text((x,y+39),id.removesuffix('-lined')[:22],font=font,fill='#167444' if col==0 else '#555')
  draw.line((0,y+63,1200,y+63),fill='#ddd')
 im.save(A/f'comparison-{start//35+1:02}.png')
# File-based browsing works without modifying the running project gallery.
markup=['<!doctype html><meta charset="utf-8"><title>Архив смысловых дублей</title><style>body{font:15px system-ui;margin:32px;max-width:1200px}section{border-top:1px solid #ddd;padding:16px 0}figure{display:inline-flex;flex-direction:column;align-items:center;width:190px;margin:8px;vertical-align:top}img{width:48px;height:48px}figcaption{overflow-wrap:anywhere;text-align:center;font-size:12px;margin-top:8px}.keep{color:#167444}input{font:inherit;padding:8px;width:350px}</style>',f'<h1>Архив смысловых дублей</h1><p>{len(groups)} групп · {len(archive)} альтернатив · {len(active)} иконок в сокращённом наборе. Зелёная подпись — оставленная версия. Выбор обратим; все пользовательские замечания сохранены.</p><input id="q" placeholder="Поиск по имени">']
for g in groups:
 markup.append('<section data-search="'+html.escape(' '.join([g['meaning_key'],g['canonical']]+g['archived']))+'"><h2>'+html.escape(g['meaning_key'])+'</h2>')
 for id in [g['canonical']]+g['archived']:
  r=byid[id];src='../../result/curated/svg/'+r['file'] if id==g['canonical'] else 'svg/'+r['file'];comment=notes.get(id,{}).get('comment','Без оценки');markup.append(f'<figure><img src="{html.escape(src,quote=True)}"><figcaption class="{"keep" if id==g["canonical"] else ""}">{html.escape(id)}<br>{html.escape(comment)}</figcaption></figure>')
 markup.append('</section>')
markup.append('<script>q.oninput=()=>document.querySelectorAll("section").forEach(s=>s.hidden=!s.dataset.search.includes(q.value.toLowerCase().trim()))</script>');(A/'index.html').write_text(''.join(markup))
print(json.dumps(summary,ensure_ascii=False,indent=2))
