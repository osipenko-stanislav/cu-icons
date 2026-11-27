"""Detailed local motion for Bio, Bed and Brand Network, preserving idle artwork."""
from pathlib import Path
from importlib.machinery import SourceFileLoader
import copy,json,math,hashlib,bisect
P=Path('icon-project');O=P/'motion/reference-series';C=P/'result/curated';R=P/'review/motion/ref-details-2026-11-27';R.mkdir(exist_ok=True)
G=SourceFileLoader('detail_svg_motion',str(P/'tools/svg-to-lottie.py')).load_module();V=lambda v:{'a':0,'k':v};N=48
cfg=json.loads((O/'motion.json').read_text());targets={'ref-bio','ref-bed','ref-brand-network'};before={s['id']:s for s in cfg['scenes'] if s['id'] in targets}
if not (R/'before-scenes.json').exists():(R/'before-scenes.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n')
other={s['id']:hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest() for s in cfg['scenes'] if s['id'] not in targets}
def prop(values):return {'a':1,'k':[{'t':i,'s':v,'o':{'x':.333333,'y':.333333},'i':{'x':.666667,'y':.666667}} for i,v in enumerate(values)]}
def wave(t,start,width):
 u=(t-start)/width
 return math.sin(math.pi*u)**2 if 0<u<1 else 0

def warp(path,fn):
 out=copy.deepcopy(path)
 for i,v in enumerate(path['v']):
  q=fn(v);out['v'][i]=q
  for h in ['i','o']:
   p=fn([v[a]+path[h][i][a] for a in [0,1]]);out[h][i]=[p[a]-q[a] for a in [0,1]]
 for h in ['v','i','o']:out[h]=[[round(x,5) for x in p] for p in out[h]]
 return out

def group(entry,paths=None,tr=None):
 g=G.paint_group(entry)
 if paths:g['it'][0]['ks']=prop([[p] for p in paths])
 if tr:g['it'][-1].update(tr)
 return g

def animation(id,groups):
 return {'nm':id+' / detailed authored motion','v':'5.5.2','fr':30,'ip':0,'op':N,'w':24,'h':24,'ddd':0,'assets':[],'layers':[{'ddd':0,'ind':1,'ty':4,'sr':1,'ks':{'o':V(100),'r':V(0),'p':V([0,0,0]),'a':V([0,0,0]),'s':V([100,100,100])},'ao':0,'shapes':groups,'ip':0,'op':N,'st':0,'bm':0}]}
def center(path):return [(min(p[a] for p in path['v'])+max(p[a] for p in path['v']))/2 for a in [0,1]]
def samples(path):
 out=[];v=path['v'];count=len(v) if path['c'] else len(v)-1
 for i in range(count):
  j=(i+1)%len(v);a=v[i];b=[a[k]+path['o'][i][k] for k in [0,1]];d=v[j];c=[d[k]+path['i'][j][k] for k in [0,1]]
  for step in range(20):
   t=step/20;out.append([a[k]*(1-t)**3+3*b[k]*t*(1-t)**2+3*c[k]*t*t*(1-t)+d[k]*t**3 for k in [0,1]])
 out.append(v[0] if path['c'] else v[-1]);return out

def travel(path,u):
 ps=samples(path);length=[0]
 for a,b in zip(ps,ps[1:]):length.append(length[-1]+math.dist(a,b))
 distance=max(0,min(1,u))*length[-1];i=min(len(ps)-1,max(1,bisect.bisect_left(length,distance)));f=(distance-length[i-1])/max(.00001,length[i]-length[i-1]);return [ps[i-1][a]+f*(ps[i][a]-ps[i-1][a]) for a in [0,1]]
def filled_circle(x,y,r):return G.extract(f'<svg xmlns="http://www.w3.org/2000/svg"><circle cx="{x}" cy="{y}" r="{r}" fill="currentColor"/></svg>'.encode())[0]
report=[]
for scene in cfg['scenes']:
 id=scene['id']
 if id not in targets:continue
 entries=G.extract((O/'svg'/(id+'.svg')).read_bytes());groups=[]
 if id=='ref-bio':
  nodes=list(range(7,13));centers={i:center(entries[i]['path']) for i in nodes};order=sorted(nodes,key=lambda i:(math.atan2(centers[i][1]-12,centers[i][0]-12)+math.pi/2)%(2*math.pi));delay={i:order.index(i)*.075 for i in nodes}
  def displacement(i,t):
   c=centers[i];w=wave(t,delay[i],.42);length=math.dist(c,[12,12]);return [(c[a]-12)/length*.45*w for a in [0,1]],1+.17*w
  for i,e in enumerate(entries):
   if i in nodes:
    c=centers[i];paths=[]
    for f in range(N+1):
     delta,scale=displacement(i,f/N);paths.append(warp(e['path'],lambda p:[c[a]+delta[a]+(p[a]-c[a])*scale for a in [0,1]]))
    groups.append(group(e,paths))
   elif i<6:
    p=e['path'];outer=max(range(len(p['v'])),key=lambda j:math.dist(p['v'][j],[12,12]));node=min(nodes,key=lambda j:math.dist(p['v'][outer],centers[j]));paths=[]
    for f in range(N+1):
     d,_=displacement(node,f/N);q=copy.deepcopy(p);q['v'][outer]=[q['v'][outer][a]+d[a] for a in [0,1]];paths.append(q)
    groups.append(group(e,paths))
   else:groups.append(group(e))
  description='Clockwise pulse of six atoms; each bond endpoint follows its atom; nucleus remains anchored.'
 elif id=='ref-bed':
  keys=[(0,0),(.25,.85),(.5,-.15),(.7,.13),(.95,0),(1,0)]
  def amount(t):
   for (a,x),(b,y) in zip(keys,keys[1:]):
    if a<=t<=b:
     u=(t-a)/(b-a);u=u*u*(3-2*u);return x+(y-x)*u
   return 0
  for i,e in enumerate(entries):
   if i!=2:groups.append(group(e));continue
   paths=[]
   for f in range(N+1):
    depth=amount(f/N)
    def deform(p):
     x,y=p;base=17.5789;u=max(0,min(1,(x-3)/18));weight=math.sin(math.pi*u)**2*max(0,min(1,(base-y)/9))**.5;return [x,y+depth*weight]
    paths.append(warp(e['path'],deform))
   groups.append(group(e,paths))
  description='Mattress compresses and settles with a small rebound; posts and lower baseline remain fixed.'
 else:
  groups=[group(e) for e in entries]
  for node,start,width in [(1,.01,.25),(3,.43,.3),(4,.76,.24)]:
   c=center(entries[node]['path']);entry=filled_circle(c[0],c[1],1.18);opacity=prop([[100*wave(f/N,start,width)] for f in range(N+1)]);groups.append(group(entry,tr={'o':opacity}))
  for edge,start,end in [(0,.13,.55),(2,.55,.9)]:
   positions=[];opacities=[]
   for f in range(N+1):
    t=f/N;u=(t-start)/(end-start);positions.append(travel(entries[edge]['path'],u));opacities.append([100*wave(t,start,end-start)])
   groups.append(group(filled_circle(0,0,.48),tr={'p':prop(positions),'o':prop(opacities)}))
  description='Signal travels along existing branches, with sequential node highlights; original graph stays anchored.'
 data=animation(id,groups);scene['duration']=1600;scene['tracks']=[[0,'reference-lottie',1,0,0,0,1,{'version':1,'authored':True,'interaction':'hover-replay','animationData':data,'sourceId':'atom' if id=='ref-bio' else 'soft-settle' if id=='ref-bed' else 'network-signal','sourceUrl':'https://useanimations.com/icons/settings-v2' if id=='ref-bio' else 'https://useanimations.com/icons/inbox' if id=='ref-bed' else 'https://useanimations.com/icons/shuffle','overflow':False}]]
 for folder in [O,C]:(folder/'animation'/(id+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n')
 report.append({'id':id,'description':description,'idle_artwork_preserved':True})
assert all(hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest()==other[s['id']] for s in cfg['scenes'] if s['id'] not in targets)
(O/'motion.json').write_text(json.dumps(cfg,separators=(',',':'))+'\n');active={r['id'] for r in json.loads((C/'catalog.json').read_text())};(C/'motion.json').write_text(json.dumps({**{k:v for k,v in cfg.items() if k!='scenes'},'scenes':[s for s in cfg['scenes'] if s['id'] in active]},separators=(',',':'))+'\n');(R/'authoring.json').write_text(json.dumps({'scenes':report,'other_scene_hashes':other},indent=2)+'\n');print(report)
