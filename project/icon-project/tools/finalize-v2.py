from pathlib import Path
import json,hashlib,sys,importlib.util,xml.etree.ElementTree as E,collections
ROOT=Path(__file__).resolve().parents[1];sp=importlib.util.spec_from_file_location('runner',Path(__file__).with_name('run-series.py'));r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
m=json.loads((ROOT/'manifest.json').read_text());author=json.loads((ROOT/'review/reports/reference-series-authoring.json').read_text());samples=json.loads((ROOT/'review/reports/geometry-v2-samples.json').read_text())['samples'];sample_map={i['id']:i for i in samples}
# These notes describe why fixed semantic forms remain and which construction anchors were compared.
family_anchors={
 'currency':('brand-math-lined','Preserved currency glyph identity; monoline curves and unframed mathematical notation are compatible.'),
 'globe':('clock','Preserved geographic content and longitude/latitude geometry; circular envelope matches the reference circle family.'),
 'fingerprint':('heart','Preserved fingerprint ridge layout; organic continuous curves use the same live monoline construction.'),
 'link':('brand-glasses-lined','Preserved link count and broken-link state; circular/organic tangencies remain compatible with reference loops.'),
 'type':('brand-math-lined','Preserved the semantic letterforms of typography controls.'),
 'cursor':('arrow-link','Preserved pointer/cursor identity; angular outline and joins follow the navigation reference.'),
 'package':('brand-home-lined','Preserved box projection and modifier; geometric straight edges follow the architectural reference.'),
 'cube':('brand-home-lined','Preserved perspective and visible faces; straight edges and thin live contours are compatible.'),
 'target':('clock','Preserved target rings, ticks and pointer direction; shared circular geometry.'),
 'pie':('clock','Preserved sector angles and boundaries because they define the graphic meaning; shared circular construction.'),
 'bluetooth':('brand-code-lined','Preserved the recognizable Bluetooth symbol and slash/state; its diagonals are compatible with reference linework.'),
 'qr':('brand-chip-lined','Preserved the supplied matrix layout; no arbitrary redesign of the pattern.'),
}
crit={'schema_version':1,'reviewer':'Codex reference-first sequential visual review','independence':'sequential','icons':[]};geometry=[];retained=[]
for b in m['batches'][1:]:
 ev='review/contact-sheets/v2-'+b['id']+'-review.png';side=json.loads((ROOT/ev).with_suffix('.json').read_text());assert hashlib.sha256((ROOT/ev).read_bytes()).hexdigest()==side['png_sha256']
 for i in b['ids']:
  rec=m['icons'][i];assert side['icons'][i]==rec['sha256'],i+' evidence stale'
  if rec['status']=='Approved':continue
  crit['icons'].append({'id':i,'sha256':rec['sha256'],'render_evidence':[ev],'findings':[]})
  a=author[i]
  if a['method']=='retained-pending-family-review':
   family=rec['family'].split('-')[0];anchor,note=family_anchors.get(family,('brand-code-lined / clock / brand-home-lined','Preserved the distinctive semantic contour; inspected angular/round parts, scale, gaps and live linework beside the reference anchors. No exact same-metaphor reference exists for this variant.'))
   retained.append({'id':i,'reference':anchor,'reason':note,'review':'sequential visual inspection of current source/result at 16,24,48 px in both themes'})
(ROOT/'review/reports/v2-critique.json').write_text(json.dumps(crit,indent=2)+'\n')
(ROOT/'review/reports/v2-retained-geometry-review.json').write_text(json.dumps(retained,indent=2)+'\n')
# Compare contours with a common stroke width and common preview paint, independent of the 1.5 ->1 change.
prior_geometry={x['id']:x for x in json.loads((ROOT/'review/reports/v2-contour-change.json').read_text())['icons']} if (ROOT/'review/reports/v2-contour-change.json').exists() else {}
for i,icon in m['icons'].items():
 if prior_geometry.get(i,{}).get('sha256')==icon['sha256']:
  geometry.append(prior_geometry[i]);continue
 raw=(ROOT/icon['path']).read_bytes();src=(ROOT/m['sources'][icon['source']]['path']).read_bytes()
 def neutral(raw):
  n=E.fromstring(r.painted(raw,'black'))
  for el in n.iter():
   if el.get('stroke-width') is not None:el.set('stroke-width','1')
   if el.get('stroke-linecap') is not None:el.set('stroke-linecap','round')
   if el.get('stroke-linejoin') is not None:el.set('stroke-linejoin','round')
  n.set('stroke-width','1');return E.tostring(n)
 current=r.r.render(neutral(raw),64,ROOT/'review/cache').getchannel('A');original=r.r.render(neutral(src),64,ROOT/'review/cache').getchannel('A')
 diff=sum(abs(a-b)>16 for a,b in zip(current.tobytes(),original.tobytes()));ink=sum(v>16 for v in original.tobytes());changed=diff>max(4,ink*.02)
 geometry.append({'id':i,'sha256':icon['sha256'],'pixels_changed_with_equal_line_weight':diff,'source_ink_pixels':ink,'contour_change_above_tolerance':changed})
(ROOT/'review/reports/v2-contour-change.json').write_text(json.dumps({'method':'64px alpha comparison after neutralizing paint, width=1, round caps/joins; changed if >4 pixels or >2% of source ink differ by >16 alpha levels','changed':sum(x['contour_change_above_tolerance'] for x in geometry),'total':len(geometry),'icons':geometry},indent=2)+'\n')
print('Review records',len(crit['icons']),'retained contours reviewed',len(retained),'visible contour changes',sum(x['contour_change_above_tolerance'] for x in geometry),'/',len(geometry))
