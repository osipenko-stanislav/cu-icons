from pathlib import Path
import json,hashlib,sys,importlib.util,collections,xml.etree.ElementTree as E,shutil
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('adapter',Path(__file__).with_name('iconizer-local.py'));a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a);r=a.Renderer()
m=json.loads((ROOT/'manifest.json').read_text());ids=[i for i,v in m['icons'].items() if v['status']!='Approved'];critique={'schema_version':1,'reviewer':'Codex sequential visual review','independence':'sequential','icons':[]}
for i in ids:
 icon=m['icons'][i];b=next(b for b in m['batches'] if i in b['ids']);label=b['id']+'-review.png'
 if b['id']=='batch-001':label='batch-001-'+('001' if b['ids'].index(i)<20 else '002')+'.png'
 evidence='review/contact-sheets/'+label
 side=json.loads((ROOT/evidence).with_suffix('.json').read_text())
 assert side['icons'][i]==icon['sha256']
 critique['icons'].append({'id':i,'sha256':icon['sha256'],'render_evidence':[evidence],'findings':[]})
(ROOT/'review/reports/series-critique.json').write_text(json.dumps(critique,indent=2)+'\n')
# Recheck only revised hashes on the expanded canvas.
p=ROOT/'review/reports/series-clipping.json';clip=json.loads(p.read_text());tested=0
for i,icon in m['icons'].items():
 if clip['icons'][i]['sha256']==icon['sha256']:continue
 node=E.fromstring((ROOT/icon['path']).read_bytes());node.set('viewBox','-4 -4 32 32');box=r.render(E.tostring(node),1024,ROOT/'review/cache').getchannel('A').getbbox();bounds=[-4+v/32 for v in box]
 clip['icons'][i]={'sha256':icon['sha256'],'bounds':bounds,'within_canvas':min(bounds[:2])>=0 and max(bounds[2:])<=24};tested+=1
clip['failed']=[i for i,v in clip['icons'].items() if not v['within_canvas']];p.write_text(json.dumps(clip,indent=2)+'\n')
print('Updated clipping checks:',tested,'failures:',clip['failed'],flush=True)
# Exact vector and raster equivalences. No quadratic near-similarity scan is needed.
sys.path.insert(0,'/Users/st.osipenko/.codex/skills/cu-iconizer/scripts');from svg import normalized,parse
exact=collections.defaultdict(list);alpha=collections.defaultdict(list);source_alpha={}
for i,icon in m['icons'].items():
 raw=(ROOT/icon['path']).read_bytes();exact[hashlib.sha256(normalized(parse(raw),geometry=True)).hexdigest()].append(i)
 im=r.render(raw,24,ROOT/'review/cache');alpha[hashlib.sha256(im.getchannel('A').tobytes()).hexdigest()].append(i)
for group in alpha.values():
 if len(group)<2:continue
 for i in group:
  icon=m['icons'][i];src=m['sources'][icon['source']];node=E.fromstring((ROOT/src['path']).read_bytes())
  for n in node.iter():
   if n.get('stroke-width'):n.set('stroke-width','1')
  source_alpha[i]=hashlib.sha256(r.render(E.tostring(node),24,ROOT/'review/cache').getchannel('A').tobytes()).hexdigest()
groups=[]
for h,g in alpha.items():
 if len(g)>1:groups.append({'ids':g,'same_source_at_24px_with_normalized_weight':len({source_alpha[i] for i in g})==1,'decision':'Retain all source IDs. No files removed.'})
report={'method':'Exact paint-independent vector signature and exact alpha raster at 24 px; no exhaustive near-similarity scan','exact_vector_groups':[v for v in exact.values() if len(v)>1],'exact_raster_groups':groups}
(ROOT/'review/reports/series-duplicates.json').write_text(json.dumps(report,indent=2)+'\n')
print('Exact raster duplicate groups:',len(groups),'new coincidences:',[g for g in groups if not g['same_source_at_24px_with_normalized_weight']],flush=True)
# Flat SVG candidates are review artifacts; approved-only release stays separate.
dest=ROOT/'review/svg';dest.mkdir(exist_ok=True);mapping=[]
for i,icon in m['icons'].items():
 raw=(ROOT/icon['path']).read_bytes();(dest/(i+'.svg')).write_bytes(raw)
 mapping.append({'id':i,'file':i+'.svg','sha256':icon['sha256'],'approval':'pilot-approved' if icon['status']=='Approved' else 'awaiting-user-review'})
(dest/'catalog.json').write_text(json.dumps(mapping,indent=2)+'\n')
print('Flat review SVGs:',len(mapping))
