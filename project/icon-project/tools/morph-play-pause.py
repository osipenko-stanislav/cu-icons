"""Explicit play/pause correspondence on existing curves; no crossfade."""
from pathlib import Path
from importlib.machinery import SourceFileLoader
import copy,json,hashlib
P=Path('icon-project');O=P/'motion/reference-series';C=P/'result/curated';R=P/'review/motion/stability-2026-11-27';G=SourceFileLoader('pair_svg',str(P/'tools/svg-to-lottie.py')).load_module();V=lambda x:{'a':0,'k':x};N=48
ids={'play-lined','play-circle-lined','play-square-lined','pause-circle-lined','pause-square-lined'};cfg=json.loads((O/'motion.json').read_text());report=[]
def bounds(e):return [min(v[0] for v in e['path']['v']),min(v[1] for v in e['path']['v']),max(v[0] for v in e['path']['v']),max(v[1] for v in e['path']['v'])]
def entries(id):return G.extract((O/'svg'/(id+'.svg')).read_bytes())
for s in cfg['scenes']:
 id=s['id']
 if id not in ids:continue
 p=R/'before'/(id+'.json')
 if not p.exists():p.write_text(json.dumps(s,separators=(',',':'))+'\n')
 es=entries(id);plain=id in ['play-lined','pause-lined'];fixed=[] if plain else [e for e in es if max(bounds(e)[2]-bounds(e)[0],bounds(e)[3]-bounds(e)[1])>15];glyph=[e for e in es if e not in fixed];play_id=id.replace('pause','play');pause_id=id.replace('play','pause');plays=entries(play_id);play=next(e for e in plays if e['path']['c'] and (plain or max(bounds(e)[2]-bounds(e)[0],bounds(e)[3]-bounds(e)[1])<13));bars=sorted([e for e in entries(pause_id) if not e['path']['c']],key=lambda e:bounds(e)[0]);assert len(bars)==2
 path=play['path'];assert len(path['v'])==12;lx,top,_,bottom=bounds(bars[0]);rx,rt,_,rb=bounds(bars[1]);mid=(rt+rb)/2;targets=[((lx,top),(lx,bottom)),((rx,rb),(rx,mid)),((rx,mid),(rx,rt))];groups=[G.paint_group(e) for e in fixed]
 for indices,(a,b) in zip([[8,9,10,11,0],[0,1,2,3,4],[4,5,6,7,8]],targets):
  src={'c':False,**{k:[copy.deepcopy(path[k][j]) for j in indices] for k in ['v','i','o']}};src['i'][0]=[0,0];src['o'][-1]=[0,0];dst={'c':False,'v':[[a[k]+(b[k]-a[k])*j/4 for k in [0,1]] for j in range(5)],'i':[[0,0] for _ in range(5)],'o':[[0,0] for _ in range(5)]};first,last=(src,dst) if id.startswith('play') else (dst,src);paint=copy.deepcopy(play);paint['path']=first;g=G.paint_group(paint);keys=[]
  for f in range(N+1):
   t=f/N;u=t*t*(3-2*t);shape={'c':False,**{k:[[first[k][j][a]+(last[k][j][a]-first[k][j][a])*u for a in [0,1]] for j in range(5)] for k in ['v','i','o']}};keys.append({'t':f,'s':[shape],'o':{'x':.333333,'y':.333333},'i':{'x':.666667,'y':.666667}})
  g['it'][0]['ks']={'a':1,'k':keys};groups.append(g)
 data={'nm':id+' / explicit play pause morph','v':'5.5.2','fr':192,'ip':0,'op':48,'w':24,'h':24,'ddd':0,'assets':[],'layers':[{'ddd':0,'ind':1,'ty':4,'sr':1,'ks':{'o':V(100),'r':V(0),'p':V([0,0,0]),'a':V([0,0,0]),'s':V([100,100,100])},'ao':0,'shapes':groups,'ip':0,'op':48,'st':0,'bm':0}]};s['duration']=250;s['tracks']=[[0,'reference-lottie',1,0,0,0,1,{'version':1,'authored':True,'interaction':'click-toggle','animationData':data,'sourceId':'explicit-play-pause','sourceUrl':'','overflow':False}]]
 for folder in [O,C]:(folder/'animation'/(id+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n')
 report.append({'id':id,'target':pause_id if id.startswith('play') else play_id,'description':'Three continuous curve chains map to two pause bars. Fixed frame; original rounded play outline retained; no opacity tracks.','status':'needs-visual-review'})
(O/'motion.json').write_text(json.dumps(cfg,separators=(',',':'))+'\n');active={r['id'] for r in json.loads((C/'catalog.json').read_text())};(C/'motion.json').write_text(json.dumps({**cfg,'scenes':[s for s in cfg['scenes'] if s['id'] in active]},separators=(',',':'))+'\n');(R/'state-pairs.json').write_text(json.dumps(report,indent=2)+'\n');print('Authored',len(report),'explicit state pairs')
