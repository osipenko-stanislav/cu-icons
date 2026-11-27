from pathlib import Path
import json,hashlib,importlib.util,sys,collections,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('adapter',Path(__file__).with_name('iconizer-local.py'));a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);r=a.Renderer()
m=json.loads((ROOT/'manifest.json').read_text());results={};fail=[]
for i,icon in m['icons'].items():
 raw=(ROOT/icon['path']).read_bytes();node=E.fromstring(raw);node.set('viewBox','-4 -4 32 32');im=r.render(E.tostring(node),1024,ROOT/'review/cache');box=im.getchannel('A').getbbox();bounds=[-4+v/32 for v in box] if box else None
 good=bool(bounds and min(bounds[:2])>=0 and max(bounds[2:])<=24)
 results[i]={'sha256':icon['sha256'],'bounds':bounds,'within_canvas':good}
 if not good:fail.append(i)
(ROOT/'review/reports/series-clipping.json').write_text(json.dumps({'method':'Expanded viewBox -4 -4 32 32 at 1024 px; quantization 0.03125 units','count':len(results),'failed':fail,'icons':results},indent=2)+'\n')
issues={i:x['validation']['issues'] for i,x in m['icons'].items() if x['validation'] and x['validation']['issues']}
(ROOT/'review/reports/series-validation-issues.json').write_text(json.dumps(issues,indent=2)+'\n')
print('All icons:',len(results),'clipping failures:',fail);print('Issues:',{i:v for i,v in issues.items() if any(x['level']=='Error' for x in v)})
print('Warnings:',collections.Counter(y['code'] for v in issues.values() for y in v))
# Check originals against their immutable imports, preserving case in source names.
for folder,key in [('ref','references'),('work','sources')]:
 original={hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.parent.joinpath(folder).glob('*.svg')}
 imported={v['sha256'] for v in m[key].values()}
 print(folder,'original hashes unchanged:',original==imported,'files:',len(list(ROOT.parent.joinpath(folder).glob('*.svg'))))
print('Approved pilot hashes intact:',all(m['icons'][i]['sha256']==h for i,h in m['pilot_approval']['icons'].items()))
