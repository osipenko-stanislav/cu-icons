"""Rebuild named unapproved scenes without changing the approved pilot or static SVGs."""
import sys,json,hashlib,copy
from pathlib import Path
from importlib.machinery import SourceFileLoader
P=Path('icon-project');O=P/'motion/reference-series'
M=SourceFileLoader('retarget_revision',str(P/'tools/retarget-motion-library.py')).load_module()
config=json.loads((O/'motion.json').read_text());manifest=json.loads((O/'manifest.json').read_text());byid={r['id']:r for r in manifest}
approved={s['id'] for s in json.loads((P/'motion/exact-reference/motion.json').read_text())['scenes']}
for id in sys.argv[1:]:
 if id in approved:raise ValueError('Approved pilot requires explicit reopening: '+id)
 scene=next(s for s in config['scenes'] if s['id']==id);before=copy.deepcopy(scene)
 history=P/'review/motion/reference-series/history';history.mkdir(parents=True,exist_ok=True)
 digest=hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest()
 saved=history/(id+'-'+digest+'.json')
 if not saved.exists():saved.write_text(json.dumps(before,separators=(',',':'))+'\n')
 ref=scene['tracks'][0][7]['sourceId'];d,details=M.retarget(id,ref,M.G.extract((O/'svg'/(id+'.svg')).read_bytes()))
 scene['tracks'][0][7]['animationData']=d;scene['duration']=(d['op']-d.get('ip',0))/d['fr']*1000
 byid[id]['details']=details;byid[id]['status']='needs-visual-review'
 (O/'animation'/(id+'.json')).write_text(json.dumps(d,separators=(',',':'))+'\n')
 print('Revised',id)
(O/'motion.json').write_text(json.dumps(config,separators=(',',':'))+'\n');(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
