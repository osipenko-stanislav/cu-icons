from pathlib import Path
import json,hashlib,importlib.util,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];sp=importlib.util.spec_from_file_location('adapter',Path(__file__).with_name('iconizer-local.py'));a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a);r=a.Renderer();m=json.loads((ROOT/'manifest.json').read_text());pre=json.loads((ROOT/'review/reports/v2-preflight.json').read_text());old=json.loads((ROOT/'review/reports/series-clipping.json').read_text())['icons'];tested=0;checks={}
for i,v in m['icons'].items():
 previous=pre['icons'].get(i) or old.get(i)
 if previous and previous['sha256']==v['sha256']:checks[i]=previous;continue
 raw=(ROOT/v['path']).read_bytes();n=E.fromstring(raw);n.set('viewBox','-4 -4 32 32');box=r.render(E.tostring(n),768,ROOT/'review/cache').getchannel('A').getbbox();bounds=[-4+x/24 for x in box];checks[i]={'sha256':v['sha256'],'bounds':bounds,'within_canvas':min(bounds[:2])>=0 and max(bounds[2:])<=24};tested+=1
bad=[i for i,v in checks.items() if not v['within_canvas']];errors=[i for i,v in m['icons'].items() if any(x['level']=='Error' for x in v['validation']['issues'])];warnings={i:v['validation']['issues'] for i,v in m['icons'].items() if v['validation']['issues']}
report={'count':len(checks),'incremental_new_checks':tested,'clipped':bad,'technical_errors':errors,'advisories':warnings,'icons':checks};(ROOT/'review/reports/final-integrity.json').write_text(json.dumps(report,indent=2)+'\n');print('Final current revisions:',len(checks),'retested:',tested,'clipped:',bad,'errors:',errors,'advisories:',list(warnings))
assert len(checks)==1189 and not bad and not errors
