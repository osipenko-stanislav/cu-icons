"""Apply verified supplemental aliases while retaining full source assets and motion."""
from pathlib import Path
import json,shutil,hashlib,collections,html
P=Path('icon-project');R=P/'review/motion/user-selection-2026-11-27';C=P/'result/curated';A=P/'archive/semantic-duplicates';O=P/'motion/reference-series'
checks=json.loads((R/'remaining-aliases.json').read_text());old=json.loads((A/'aliases.json').read_text());groups=json.loads((A/'groups.json').read_text());catalog=json.loads((P/'result/catalog.json').read_text());byid={r['id']:r for r in catalog};active={r['id'] for r in json.loads((C/'catalog.json').read_text())};notes={r['icon']:r for r in json.loads((P/'review/user-feedback/2026-11-26/feedback.json').read_text())['entries']}
backup=R/'before-additional-aliases.json'
if not backup.exists():backup.write_text(json.dumps({'aliases':old,'groups':groups,'active_ids':sorted(active)},ensure_ascii=False,indent=2)+'\n')
active=set(json.loads(backup.read_text())['active_ids'])
source=json.loads((P/'motion/reference-series/motion.json').read_text());scenes={s['id']:s for s in source['scenes']};before_hash=hashlib.sha256((O/'motion.json').read_bytes()).hexdigest()
# Retain reference examples explicitly picked by the user when available.
reference_anchors={'heart-lined','flash-lined','flash-off-lined','loading-01-lined','file-02-lined','phone-call-02-lined','wifi-lined','folder-lined'}
def rank(id):
 n=notes.get(id);quality=100 if n and n['review_status']=='positive' else 0 if not n else -30 if 'geometry' in n['tags'] else -10
 return (-quality,-int(id in reference_anchors),len(id),id)
new={};applied=[]
for g in checks['confirmed_groups']:
 ids=[i for i in g['members'] if i in active]
 if len(ids)<2:continue
 keep=min(ids,key=rank);members=[i for i in ids if i!=keep]
 for id in members:new[id]=keep
 applied.append({**g,'canonical':keep,'archived':members})
for id,keep in new.items():
 for sub,name in [('svg',byid[id]['file']),('geometry',id+'.svg'),('animation',id+'.json')]:
  a=C/sub/name;b=A/sub/name
  if a.exists():
   if b.exists():assert a.read_bytes()==b.read_bytes();a.unlink()
   else:shutil.move(str(a),str(b))
links={**old,**new}
def resolve(id):
 seen=set()
 while id in links:
  assert id not in seen;seen.add(id);id=links[id]
 return id
aliases={id:resolve(id) for id in links};remaining={r['id'] for r in catalog}-set(aliases)
# Merge connected groups so every archived ID resolves directly to an active ID.
merged=collections.defaultdict(list)
for id,keep in aliases.items():merged[keep].append(id)
final_groups=[{'meaning_key':keep.removesuffix('-lined'),'canonical':keep,'archived':sorted(ids),'basis':'Recorded semantic variants/synonyms. Supplemental groups also have equal alpha masks at 24 and 48px.','canonical_selection':'Prefer positive user feedback and selected reference examples; preserve all other versions in archive.'} for keep,ids in sorted(merged.items())]
for folder,ids in [(C,remaining),(A,set(aliases))]:
 items=[{**r,'canonical':aliases.get(r['id'],r['id'])} for r in catalog if r['id'] in ids]
 (folder/'catalog.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n')
 (folder/'motion.json').write_text(json.dumps({**{k:v for k,v in source.items() if k!='scenes'},'scenes':[scenes[r['id']] for r in items]},separators=(',',':'))+'\n')
 overrides=json.loads((O/'trigger-overrides.json').read_text());(folder/'trigger-overrides.json').write_text(json.dumps({k:v for k,v in overrides.items() if k in ids},indent=2)+'\n')
 rows=[{**r,'collection':'archive' if r['icon'] in aliases else 'active','canonical':aliases.get(r['icon'],r['icon'])} for r in notes.values() if r['icon'] in ids];(folder/'review-status.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(A/'aliases.json').write_text(json.dumps(aliases,indent=2)+'\n');(A/'groups.json').write_text(json.dumps(final_groups,ensure_ascii=False,indent=2)+'\n')
# Rebuild the archive comparison without rerunning initial archive selection.
script=(P/'tools/capture-review-and-archive.py').read_text();segment=script[script.index('# File-based browsing'):script.index("print(json.dumps(summary")]
archive=[r for r in catalog if r['id'] in aliases];groups=final_groups;active=[r for r in catalog if r['id'] in remaining];exec(segment)
assert before_hash==hashlib.sha256((O/'motion.json').read_bytes()).hexdigest()
report={'newly_archived':len(new),'new_groups':len(applied),'active':len(remaining),'archived_total':len(aliases),'semantic_groups_total':len(final_groups),'full_motion_unchanged':True,'applied':applied}
(R/'additional-archive.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in report.items() if k!='applied'})
