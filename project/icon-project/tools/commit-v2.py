from pathlib import Path
import json,hashlib,sys,subprocess,importlib.util,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];tool=Path(__file__).with_name('iconizer-local.py')
sp=importlib.util.spec_from_file_location('runner',Path(__file__).with_name('run-series.py'));runner=importlib.util.module_from_spec(sp);sp.loader.exec_module(runner);runner.PREFIX='v2-'
m=json.loads((ROOT/'manifest.json').read_text());style=json.loads((ROOT/'specification/icon-style.json').read_text());sys.path.insert(0,'/Users/st.osipenko/.codex/skills/cu-iconizer/scripts');from svg import inspect;from project import rules_for
pre=json.loads((ROOT/'review/reports/v2-preflight.json').read_text());tested=0
for i,v in m['icons'].items():
 if v['status']=='Approved':continue
 p=ROOT/'staging/reference-series'/(i+'.svg');raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
 if pre['icons'].get(i,{}).get('sha256')==sha:continue
 _,issues=inspect(raw,i,rules_for(style,v));node=E.fromstring(raw);node.set('viewBox','-4 -4 32 32');box=runner.r.render(E.tostring(node),768,ROOT/'review/cache').getchannel('A').getbbox();bounds=[-4+x/24 for x in box];pre['icons'][i]={'sha256':sha,'issues':issues,'bounds':bounds,'within_canvas':min(bounds[:2])>=0 and max(bounds[2:])<=24};tested+=1
pre['errors']=[i for i,v in pre['icons'].items() if any(z['level']=='Error' for z in v['issues'])];pre['clipped']=[i for i,v in pre['icons'].items() if not v['within_canvas']];(ROOT/'review/reports/v2-preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
print('Incremental preflight',tested,'errors',pre['errors'],'clipped',pre['clipped'],flush=True)
if pre['errors'] or pre['clipped']:raise RuntimeError('Fix candidates before submission')
# Refresh only sheets whose exact current revisions changed; retain existing proof of all other renders.
for b in m['batches'][1:]:
 virtual=json.loads(json.dumps(m))
 for i in b['ids']:
  v=virtual['icons'][i];p=ROOT/'staging/reference-series'/(i+'.svg')
  if v['status']!='Approved' and p.exists():v['path']=str(p.relative_to(ROOT));v['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 side=ROOT/'review/contact-sheets'/('v2-'+b['id']+'-review.json');stored=json.loads(side.read_text()) if side.exists() else {'icons':{}}
 if any(stored['icons'].get(i)!=virtual['icons'][i]['sha256'] for i in b['ids']):
  old_png=side.with_suffix('.png').read_bytes() if side.with_suffix('.png').exists() else None
  runner.sheet(b,virtual);new_png=side.with_suffix('.png').read_bytes();print('Refreshed sheet',b['id'],'pixels unchanged',old_png==new_png,flush=True)
# Submit through the installed skill CLI in its planned batches. Preserve every approved artifact.
for b in m['batches'][1:]:
 staging=ROOT/'staging/v2-batches'/b['id'];staging.mkdir(parents=True,exist_ok=True)
 for i in b['ids']:
  if m['icons'][i]['status']=='Approved':continue
  (staging/(i+'.svg')).write_bytes((ROOT/'staging/reference-series'/(i+'.svg')).read_bytes())
 proc=subprocess.run([sys.executable,str(tool),'--project',str(ROOT),'submit-batch',b['id'],str(staging)],capture_output=True,text=True)
 if proc.returncode:raise RuntimeError(proc.stdout+proc.stderr)
 print('Submitted',b['id'],flush=True)
