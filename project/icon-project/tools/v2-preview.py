from pathlib import Path
import json,importlib.util,sys,hashlib
ROOT=Path(__file__).resolve().parents[1];sp=importlib.util.spec_from_file_location('runner',Path(__file__).with_name('run-series.py'));a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a);a.PREFIX='v2-'
m=json.loads((ROOT/'manifest.json').read_text());ids=sys.argv[1:] or [b['id'] for b in m['batches'][1:]]
for i,v in m['icons'].items():
 p=ROOT/'staging/reference-series'/(i+'.svg')
 if p.exists() and v['status']!='Approved':v['path']=str(p.relative_to(ROOT));v['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
for b in m['batches'][1:]:
 if b['id'] in ids:print(a.sheet(b,m),flush=True)
