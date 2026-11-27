"""One shared animation per icon: targeted readability repairs, no size branches."""
from pathlib import Path
from importlib.machinery import SourceFileLoader
import json,copy,math,hashlib
P=Path('icon-project');O=P/'motion/reference-series';C=P/'result/curated';R=P/'review/motion/stability-2026-11-27';H=R/'before';G=SourceFileLoader('strong_svg',str(P/'tools/svg-to-lottie.py')).load_module();N=48;V=lambda x:{'a':0,'k':x}
ids=set('alarm-clock-minus-lined alert-triangle-lined announcement-01-lined cloud-raining-04-lined cloud-snowing-01-lined indeterminate-lined indeterminate-small-lined info-circle-lined info-hexagon-lined lightbulb-01-lined ref-laundry ref-microwave ref-kitchen ref-bed ref-brand-network'.split());cfg=json.loads((O/'motion.json').read_text());report=[]
def prop(fn):return {'a':1,'k':[{'t':f,'s':fn(f/N),'o':{'x':.333333,'y':.333333},'i':{'x':.666667,'y':.666667}} for f in range(N+1)]}
def wave(t):return math.sin(math.pi*t)**2

def group(es,move=None,scale=None,rotate=None,pivot=(12,12),opacity=None):
 tr=copy.deepcopy(G.IDENTITY_TRANSFORM)
 if scale or rotate:tr.update(p=V(list(pivot)),a=V(list(pivot)))
 if move:tr['p']=prop(lambda t:list(move(t)))
 if scale:tr['s']=prop(lambda t:[x*100 for x in scale(t)])
 if rotate:tr['r']=prop(lambda t:[rotate(t)])
 if opacity:tr['o']=prop(lambda t:[opacity(t)])
 return {'ty':'gr','it':[G.paint_group(e) for e in es]+[tr]}
def bounds(e):return [min(p[0] for p in e['path']['v']),min(p[1] for p in e['path']['v']),max(p[0] for p in e['path']['v']),max(p[1] for p in e['path']['v'])]
def lerp(t,keys):
 for (a,x),(b,y) in zip(keys,keys[1:]):
  if a<=t<=b:
   u=(t-a)/(b-a);u=u*u*(3-2*u);return x+(y-x)*u
 return keys[-1][1]
for scene in cfg['scenes']:
 id=scene['id']
 if id not in ids:continue
 path=H/(id+'.json')
 if not path.exists():path.write_text(json.dumps(scene,separators=(',',':'))+'\n')
 # Always derive from immutable pre-repair scene, so reruns do not amplify again.
 before=json.loads(path.read_text());scene.clear();scene.update(copy.deepcopy(before));es=G.extract((O/'svg'/(id+'.svg')).read_bytes());description='';groups=[]
 if id=='ref-kitchen':
  for tr in scene['tracks']:tr[2]=1.5 if tr[2]>0 else -1.2
  description='Fork descends 1.5 units, spoon rises 1.2; joined parts share displacement.'
 elif id in ['ref-bed','ref-brand-network']:
  data=scene['tracks'][0][7]['animationData'];shapes=data['layers'][0]['shapes']
  if id=='ref-bed':
   g=shapes[2];original=es[2]['path']
   for k in g['it'][0]['ks']['k']:
    p=k['s'][0]
    for key in ['v','i','o']:
     for i,xy in enumerate(p[key]):p[key][i]=[original[key][i][a]+2*(xy[a]-original[key][i][a]) for a in [0,1]]
   description='Double the existing continuous mattress compression; preserve fixed attachment points and posts.'
  else:
   # Enlarge only authored signal accents, keeping the graph and phases intact.
   for i,g in enumerate(shapes[5:],5):
    p=g['it'][0]['ks']['k'];factor=1.38 if i<8 else 1.67
    cx=(min(v[0] for v in p['v'])+max(v[0] for v in p['v']))/2;cy=(min(v[1] for v in p['v'])+max(v[1] for v in p['v']))/2
    for j,v in enumerate(p['v']):p['v'][j]=[cx+(v[0]-cx)*factor,cy+(v[1]-cy)*factor]
    for key in ['i','o']:p[key]=[[x*factor for x in xy] for xy in p[key]]
   description='Larger moving signal and node fills within the original rings; graph geometry and phases unchanged.'
 else:
  if id.startswith('indeterminate'):
   groups=[group(es,scale=lambda t:[1+.22*wave(t),1])];description='One clear horizontal expansion and return, preserving the minus symbol.'
  elif id.startswith('info-') or id=='alert-triangle-lined':
   fixed=[e for e in es if max(bounds(e)[2]-bounds(e)[0],bounds(e)[3]-bounds(e)[1])>12];moving=[e for e in es if e not in fixed];assert fixed and moving
   groups=[group(fixed),group(moving,move=lambda t:[0,-1.5*wave(t)])];description='Stable enclosing shape; explanatory glyph rises and returns as one assembly.'
  elif id=='alarm-clock-minus-lined':
   moving=[e for e in es if bounds(e)[1]==bounds(e)[3] and 5<bounds(e)[2]-bounds(e)[0]<8];fixed=[e for e in es if e not in moving];assert moving
   groups=[group(fixed),group(moving,scale=lambda t:[1+.38*wave(t),1],pivot=(12,13))];description='Readable minus-sign emphasis within the stationary clock.'
  elif id=='announcement-01-lined':
   moving=[e for e in es if bounds(e)[0]>21];fixed=[e for e in es if e not in moving];assert moving
   groups=[group(fixed),group(moving,move=lambda t:[1.3*wave(t),0],opacity=lambda t:100-25*wave(t))];description='Sound mark travels outward; loudspeaker remains stable.'
  elif id.startswith('cloud-'):
   moving=[e for e in es if bounds(e)[1]>=17];fixed=[e for e in es if e not in moving];groups=[group(fixed)];assert moving
   for i,e in enumerate(moving):
    def phase(t,i=i):return max(0,min(1,(t-i*.04)/(1-i*.04)))
    groups.append(group([e],move=lambda t,i=i:[0,lerp(phase(t,i),[(0,0),(.1,0),(.6,1.9),(.72,1.9),(.73,0),(1,0)])],opacity=lambda t,i=i:lerp(phase(t,i),[(0,100),(.4,100),(.7,0),(.8,0),(1,100)])))
   description='Independent falling precipitation beneath a stationary cloud; reset only while invisible.'
  elif id=='lightbulb-01-lined':
   groups=[group(es,rotate=lambda t:8*wave(t),pivot=(12,22))];description='Connected bulb assembly leans and returns around its base; no detached small details.'
  elif id=='ref-laundry':
   moving=[e for e in es if e['path']['c'] and 11<bounds(e)[2]-bounds(e)[0]<13];fixed=[e for e in es if e not in moving];assert len(moving)==1
   groups=[group(fixed),group(moving,scale=lambda t:[1-.52*wave(t),1],pivot=(6,13))];description='Door opens around its left hinge and closes; washing-machine case stays fixed.'
  elif id=='ref-microwave':
   window=next(e for e in es if e['path']['c'] and 10<bounds(e)[2]-bounds(e)[0]<13);g=G.paint_group(window,force='fill');g['it'][-1]['o']=prop(lambda t:[26*wave(t)]);groups=[{'ty':'gr','it':[g,copy.deepcopy(G.IDENTITY_TRANSFORM)]},group(es)];description='Heating chamber lights up and dims inside its existing window; case and controls remain stable.'
  data={'nm':id+' / readable shared motion','v':'5.5.2','fr':60,'ip':0,'op':N,'w':24,'h':24,'ddd':0,'assets':[],'layers':[{'ddd':0,'ind':1,'ty':4,'sr':1,'ks':{'o':V(100),'r':V(0),'p':V([0,0,0]),'a':V([0,0,0]),'s':V([100,100,100])},'ao':0,'shapes':groups,'ip':0,'op':N,'st':0,'bm':0}]};scene['duration']=800;scene['tracks']=[[0,'reference-lottie',1,0,0,0,1,{'version':1,'authored':True,'interaction':'hover-replay','animationData':data,'sourceId':'readability-polish','sourceUrl':'','overflow':False}]]
 if scene['tracks'][0][1]=='reference-lottie':
  for folder in [O,C]:(folder/'animation'/(id+'.json')).write_text(json.dumps(scene['tracks'][0][7]['animationData'],separators=(',',':'))+'\n')
 report.append({'id':id,'description':description,'one_animation_for_all_sizes':True,'status':'needs-visual-review','before_sha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),'after_sha256':hashlib.sha256(json.dumps(scene,sort_keys=True).encode()).hexdigest()})
(O/'motion.json').write_text(json.dumps(cfg,separators=(',',':'))+'\n');active={r['id'] for r in json.loads((C/'catalog.json').read_text())};(C/'motion.json').write_text(json.dumps({**cfg,'scenes':[s for s in cfg['scenes'] if s['id'] in active]},separators=(',',':'))+'\n');(R/'motion-repairs.json').write_text(json.dumps(report,indent=2)+'\n');print('Strengthened',len(report),'scenes')
