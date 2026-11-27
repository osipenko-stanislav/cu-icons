from pathlib import Path
import sys,json,hashlib,importlib.util,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];sp=importlib.util.spec_from_file_location('adapter',Path(__file__).with_name('iconizer-local.py'));a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a);r=a.Renderer()
sys.path.insert(0,'/Users/st.osipenko/.codex/skills/cu-iconizer/scripts');from svg import inspect;from project import rules_for
m=json.loads((ROOT/'manifest.json').read_text());style=json.loads((ROOT/'specification/icon-style.json').read_text());result={};errors=[];clipped=[];memo={}
for p in sorted((ROOT/'staging/reference-series').glob('*.svg')):
 i=p.stem
 if m['icons'][i]['status']=='Approved':continue
 raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();facts,issues=inspect(raw,i,rules_for(style,m['icons'][i]))
 if sha in memo:bounds=memo[sha]
 else:
  n=E.fromstring(raw);n.set('viewBox','-4 -4 32 32');box=r.render(E.tostring(n),768,ROOT/'review/cache').getchannel('A').getbbox();bounds=[-4+v/24 for v in box] if box else None;memo[sha]=bounds
 within=bool(bounds and min(bounds[:2])>=0 and max(bounds[2:])<=24)
 result[i]={'sha256':sha,'issues':issues,'bounds':bounds,'within_canvas':within}
 if any(x['level']=='Error' for x in issues):errors.append(i)
 if not within:clipped.append(i)
(ROOT/'review/reports/v2-preflight.json').write_text(json.dumps({'count':len(result),'errors':errors,'clipped':clipped,'icons':result},indent=2)+'\n')
print('Candidates',len(result),'technical errors',errors,'clipped',clipped,flush=True)
for i in errors+clipped:print(i,result[i],flush=True)
