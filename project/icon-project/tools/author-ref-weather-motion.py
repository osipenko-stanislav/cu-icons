"""Weather flow on the two supplied ref icons; keep all other scenes unchanged."""
from pathlib import Path
from importlib.machinery import SourceFileLoader
import json,copy,hashlib
P=Path('icon-project');O=P/'motion/reference-series';C=P/'result/curated';R=P/'review/motion/ref-weather-2026-11-27';R.mkdir(exist_ok=True)
G=SourceFileLoader('weather_svg',str(P/'tools/svg-to-lottie.py')).load_module();V=lambda x:{'a':0,'k':x}
config=json.loads((O/'motion.json').read_text());targets={'ref-shower','ref-steam'};before={s['id']:copy.deepcopy(s) for s in config['scenes'] if s['id'] in targets}
if not (R/'before-scenes.json').exists():(R/'before-scenes.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n')
others={s['id']:hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest() for s in config['scenes'] if s['id'] not in targets}
def keys(samples,fr=60):
 return {'a':1,'k':[{'t':round(t*fr,4),'s':v,'o':{'x':.333333,'y':.333333},'i':{'x':.666667,'y':.666667}} for t,v in samples]}
def layer(entries,ind,transform=None,mask=None):
 groups=[]
 for entry in entries:
  g=G.paint_group(entry)
  if transform:g['it'][-1].update(copy.deepcopy(transform))
  groups.append(g)
 out={'ddd':0,'ind':ind,'ty':4,'sr':1,'ks':{'o':V(100),'r':V(0),'p':V([0,0,0]),'a':V([0,0,0]),'s':V([100,100,100])},'ao':0,'shapes':groups,'ip':0,'op':60,'st':0,'bm':0}
 if mask:out.update(hasMask=True,masksProperties=[{'inv':False,'mode':'a','pt':V(mask),'o':V(100),'x':V(0),'nm':'Fixed water window below shower head'}])
 return out
window=G.bezier_paths('M7 15H23V24H7Z')[0];report=[]
for scene in config['scenes']:
 id=scene['id']
 if id not in targets:continue
 entries=G.extract((O/'svg'/(id+'.svg')).read_bytes());shower=id=='ref-shower'
 # extract() splits the disconnected water strokes into independent parts.
 if shower:
  moving=[e for e in entries if min(p[1] for p in e['path']['v'])>=16];fixed=[e for e in entries if e not in moving]
 else:moving=entries;fixed=[]
 layers=[layer(fixed,1)] if fixed else []
 for i,e in enumerate(moving):
  delay=(i%5)*.045;distance=2.2 if shower else 1.6 if i==0 else 2.0 if i==1 else 1.2;direction=1 if shower else -1
  peak=delay+.40;reset=delay+.445;finish=.91+delay*.4
  position=keys([(0,[0,0]),(delay+.035,[0,0]),(peak,[0,direction*distance]),(reset,[0,-direction*distance*.6]),(finish,[0,0]),(1,[0,0])])
  opacity=keys([(0,[100]),(delay+.12,[100]),(peak,[0]),(reset+.025,[0]),(delay+.73,[100]),(1,[100])])
  layers.append(layer([e],len(layers)+1,{'p':position,'o':opacity},window if shower else None))
 data={'nm':id+' / authored weather flow','v':'5.5.2','fr':30,'ip':0,'op':60,'w':24,'h':24,'ddd':0,'assets':[],'layers':layers,'meta':{'artwork':'Current user ref SVG paths, no replacement reference drawings','motion':'Unidirectional visible flow; positional reset only while fully transparent','source_inspiration':'https://useanimations.com/icons/cloud-rain' if shower else 'https://useanimations.com/icons/coffee'}}
 source='cloud-rain' if shower else 'coffee';scene['duration']=2000
 scene['tracks']=[[0,'reference-lottie',1,0,0,0,1,{'version':1,'authored':True,'interaction':'hover-loop','animationData':data,'sourceId':source,'sourceUrl':data['meta']['source_inspiration'],'overflow':False}]]
 (O/'animation'/(id+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n');(C/'animation'/(id+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n');report.append({'id':id,'fixed_parts':len(fixed),'moving_parts':len(moving),'direction':'down' if shower else 'up','behavior':'Loop while hovered, finish on leave, static with reduced motion.','geometry':'Preserved source curves; rain strokes split into independent timing parts.'})
assert all(hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest()==others[s['id']] for s in config['scenes'] if s['id'] not in targets)
(O/'motion.json').write_text(json.dumps(config,separators=(',',':'))+'\n');active={r['id'] for r in json.loads((C/'catalog.json').read_text())};(C/'motion.json').write_text(json.dumps({**{k:v for k,v in config.items() if k!='scenes'},'scenes':[s for s in config['scenes'] if s['id'] in active]},separators=(',',':'))+'\n')
p=O/'manifest.json';manifest=json.loads(p.read_text())
for row in manifest:
 if row['id'] in targets:row['status']='needs-visual-review';row['details']['weather_flow']=next(r for r in report if r['id']==row['id'])
p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(R/'authoring.json').write_text(json.dumps({'scope':sorted(targets),'scenes':report,'other_scene_hashes':others},indent=2)+'\n');print(report)
