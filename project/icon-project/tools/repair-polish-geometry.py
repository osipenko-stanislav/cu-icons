"""Repair diagnosed static geometry without changing reference/source files."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,copy
P=Path('icon-project');O=P/'motion/reference-series';C=P/'result/curated';R=P/'review/motion/polish-2026-11-27';H=R/'geometry-history';H.mkdir(exist_ok=True);E.register_namespace('','http://www.w3.org/2000/svg');NS='{http://www.w3.org/2000/svg}'
if (R/'authored-batch.json').exists():raise SystemExit('Initial repair already superseded by reviewed polish; use targeted updates.')
work_ids=set('alarm-clock-off camera-off clock-fast-forward clock-refresh clock-rewind clock-snooze clock-stopwatch cloud-lightning cloud-moon cloud-sun-01 coins-swap-01 coins-swap-02 credit-card-refresh eye-off file-06 flag-04 flag-06 line-chart-down-02 line-chart-up-02 recording-01 recording-02 search-lg'.split());work_ids={s+'-lined' for s in work_ids}
clipboard={r['id'] for r in json.loads((C/'catalog.json').read_text()) if r['id'].startswith('clipboard-') or r['id']=='clipboard-lined'}
catalog=json.loads((P/'result/catalog.json').read_text());rows={r['id']:r for r in catalog};targets=work_ids|clipboard|{'eye-lined'};report=[]
for id in sorted(targets):
 row=rows[id];p=P/'result/svg'/row['file'];before=p.read_bytes();saved=H/(id+'-'+hashlib.sha256(before).hexdigest()+'.svg')
 if not saved.exists():saved.write_bytes(before)
 if id in work_ids:
  root=E.fromstring((Path('work')/row['file']).read_bytes());root.set('stroke-width','1')
  for n in root.iter():
   if 'stroke-width' in n.attrib:n.set('stroke-width','1')
   for k in ['stroke','fill']:
    if n.get(k) in ['black','white','#000','#000000','#fff','#ffffff']:n.set(k,'currentColor')
  reason='Restore source centerlines and semantic detail; normalize only paint and stroke width to the established style.'
 else:
  root=E.fromstring(before)
  if id in clipboard:
   body=next(n for n in root if n.tag.split('}')[-1]=='path');body.set('d','M8.5 4.5H5V18.5A3 3 0 0 0 8 21.5H19V4.5H15.5')
   if id=='clipboard-lined':
    for n in list(root):
     if n.tag.split('}')[-1]=='path' and n.get('d','').startswith('M8.5 12'):root.remove(n)
   reason='Remove body line crossing the clip; preserve clip/modifier and asymmetric corner. Plain clipboard stays a plain clipboard.'
  else:
   pupil=next(n for n in root.iter() if n.tag.split('}')[-1]=='circle');pupil.set('cx','12');pupil.set('cy','12');pupil.set('r','2.5');reason='Center the pupil inside the eye; keep the reference eyelid silhouette.'
 raw=E.tostring(root);sha=hashlib.sha256(raw).hexdigest();row['sha256']=sha;row['status']='User-requested geometry revision; review pending'
 for folder in [P/'result',C,O]:(folder/'svg'/row['file']).write_bytes(raw)
 geom=copy.deepcopy(root);carrier=E.Element(NS+'g',{'data-part':'0'});geom.append(carrier)
 for n in list(geom):
  if n is not carrier and n.tag.split('}')[-1]!='defs':geom.remove(n);carrier.append(n)
 for folder in [O,C]:(folder/'geometry'/(id+'.svg')).write_bytes(E.tostring(geom))
 report.append({'id':id,'reason':reason,'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':sha})
(P/'result/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n');p=C/'catalog.json';curated=json.loads(p.read_text())
for row in curated:
 if row['id'] in targets:row.update(sha256=rows[row['id']]['sha256'],status=rows[row['id']]['status'])
p.write_text(json.dumps(curated,ensure_ascii=False,indent=2)+'\n');p=O/'manifest.json';manifest=json.loads(p.read_text())
for row in manifest:
 if row['id'] in targets:row['static_sha256']=rows[row['id']]['sha256'];row['status']='user-revision-in-progress';row['geometry_revision']=next(r for r in report if r['id']==row['id'])
p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(R/'geometry-repairs.json').write_text(json.dumps(report,indent=2)+'\n');print('Repaired',len(report),'static icons; motion must be rebuilt before publishing')
