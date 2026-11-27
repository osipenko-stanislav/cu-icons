from pathlib import Path
import importlib.util, json, hashlib, xml.etree.ElementTree as E
sp=importlib.util.spec_from_file_location('adapter',Path(__file__).with_name('iconizer-local.py')); m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
r=m.Renderer(); results={}
for p in sorted(Path('icon-project/staging/pilot').glob('*.svg')):
 node=E.fromstring(p.read_bytes());node.set('viewBox','-4 -4 32 32');ink=r.render(E.tostring(node),1024)
 box=ink.getchannel('A').getbbox(); bounds=[-4+v/32 for v in box]
 results[p.stem]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'expanded_viewbox_bounds':bounds,'within_canvas': min(bounds[:2])>=0 and max(bounds[2:])<=24}
report={'method':'resvg alpha bounds on enlarged -4 -4 32 32 viewBox at 1024px; bound quantization 0.03125 units','icons':results}
Path('icon-project/review/reports/clipping-check.json').write_text(json.dumps(report,indent=2)+'\n')
print('Passed',sum(x['within_canvas'] for x in results.values()),'/',len(results))
for i,x in results.items():
 if not x['within_canvas'] or i=='rocket-01-lined':print(i,x)
