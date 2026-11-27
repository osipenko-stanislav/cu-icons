"""Targeted polish of diagnosed groups; preserve successful unrelated scenes."""
from pathlib import Path
from importlib.machinery import SourceFileLoader
import json,copy,math,re,hashlib
P=Path('icon-project');O=P/'motion/reference-series';C=P/'result/curated';R=P/'review/motion/polish-2026-11-27';H=R/'motion-history';H.mkdir(exist_ok=True)
X=SourceFileLoader('polish_extra','icon-project/tools/polish_extra.py').load_module()
M=SourceFileLoader('polish_source','icon-project/tools/retarget-motion-library.py').load_module();G=M.G;V=lambda x:{'a':0,'k':x};N=48
queue=json.loads((R/'queue.json').read_text());wanted={r['icon']:r for r in queue['items']};cfg=json.loads((O/'motion.json').read_text());old={s['id']:copy.deepcopy(s) for s in cfg['scenes']};catalog={r['id']:r for r in json.loads((P/'result/catalog.json').read_text())};report=[]
def prop(fn):return {'a':1,'k':[{'t':f,'s':fn(f/N),'o':{'x':.333333,'y':.333333},'i':{'x':.666667,'y':.666667}} for f in range(N+1)]}
def wave(t,start=0,end=1):
 u=(t-start)/(end-start);return math.sin(math.pi*u)**2 if 0<u<1 else 0

def group(es,move=None,rotate=None,scale=None,pivot=(12,12),opacity=None):
 tr=copy.deepcopy(G.IDENTITY_TRANSFORM)
 if rotate is not None or scale is not None:tr.update(p=V(list(pivot)),a=V(list(pivot)))
 if move:tr['p']=prop(lambda t:list(move(t)))
 if rotate:tr['r']=prop(lambda t:[rotate(t)])
 if scale:tr['s']=prop(lambda t:[100*v for v in scale(t)])
 if opacity:tr['o']=prop(lambda t:[opacity(t)])
 return {'ty':'gr','it':[G.paint_group(e) for e in es]+[tr]}
def layer(groups,mask=None):
 out={'ddd':0,'ind':1,'ty':4,'sr':1,'ks':{'o':V(100),'r':V(0),'p':V([0,0,0]),'a':V([0,0,0]),'s':V([100,100,100])},'ao':0,'shapes':groups,'ip':0,'op':N,'st':0,'bm':0}
 if mask:out.update(hasMask=True,masksProperties=[{'inv':False,'mode':'a','pt':V(mask),'o':V(100),'x':V(0),'nm':'Own stationary frame window'}])
 return out

def box(e):return M.bounds(e['path'])
def ctr(e):
 b=box(e);return [(b[0]+b[2])/2,(b[1]+b[3])/2]
def partition(es,predicate):return [e for e in es if predicate(e)],[e for e in es if not predicate(e)]
def glyph_parts(es):
 fixed=[];moving=[]
 for e in es:
  b=box(e)
  (fixed if b[2]-b[0]>=12 or b[3]-b[1]>=12 else moving).append(e)
 return fixed,moving

def morph_state(entries,targets):
 # Independent paint layers preserve each state on the project's own curves.
 # Overlapping opacity ramps avoid an empty intermediate control.
 return [layer([group(entries,opacity=lambda t:100*(1-min(1,max(0,(t-.2)/.4)))),group(targets,opacity=lambda t:100*min(1,max(0,(t-.3)/.4)))])]
def recipe(id,es):
 family=id.split('-')[0];behavior='hover-replay';description='';layers=None
 if family in ['bookmark','camera','eye']:return X.author(globals(),id,es)
 if id.startswith('arrow-') and ('circle' in id or 'square' in id):
  fixed,moving=partition(es,lambda e:max(box(e)[2]-box(e)[0],box(e)[3]-box(e)[1])>15)
  assert fixed and moving,id
  if 'circle' in id:mask=G.extract(b'<svg xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="9.5"/></svg>')[0]['path']
  else:
   mask=next((copy.deepcopy(e['path']) for e in fixed if e['path']['c']),None)
   if mask:mask=G.transform_path(mask,[.97,0,0,.97,.36,.36])
   else:mask=G.bezier_paths('M2.5 2.5H21.5V21.5H2.5Z')[0]
  dx=-1 if 'left' in id else 1 if 'right' in id else 0;dy=-1 if 'up' in id else 1 if 'down' in id else 0
  def distance(t):
   if t<.12:return 0
   if t<.32:return (t-.12)/.2*25
   if t<.345:return -25
   if t<.58:return -25+(t-.345)/.235*25
   return 0
  move=lambda t:[dx*distance(t),dy*distance(t)];alpha=lambda t:0 if .305<t<.365 else 100
  layers=[layer([group(fixed)]),layer([group(moving,move=move,opacity=alpha)],mask)];description='Only the arrow moves in its direction; own frame is fixed and masks the passage.'
 elif family=='arrow':
  dx=-1 if 'left' in id else 1 if 'right' in id else 0;dy=-1 if 'up' in id else 1 if 'down' in id else 0;layers=[layer([group(es,move=lambda t:[dx*1.25*wave(t),dy*1.25*wave(t)])])];description='Short directional gesture; all arrow segments remain joined.'
 elif family=='arrows' and 'triangle' not in id:
  horizontal=any(x in id for x in ['left','right']);axis=1 if horizontal else 0;mid=12;parts=[[e for e in es if ctr(e)[axis]<mid],[e for e in es if ctr(e)[axis]>=mid]];sign=-1 if any(x in id for x in ['left','up']) else 1;groups=[]
  for i,part in enumerate(parts):groups.append(group(part,move=lambda t,i=i:[sign*(1+i*.35)*wave(t,i*.16,.85+i*.15) if horizontal else 0,sign*(1+i*.35)*wave(t,i*.16,.85+i*.15) if not horizontal else 0]))
  layers=[layer(groups)];description='Related arrows move in their indicated direction with distinct phases.'
 elif family=='chevron':
  if 'selector' in id:
   horizontal='horizontal' in id;axis=0 if horizontal else 1;groups=[]
   for sign in [-1,1]:
    part=[e for e in es if (ctr(e)[axis]-12)*sign>0];groups.append(group(part,move=lambda t,sign=sign:[sign*.9*wave(t) if horizontal else 0,sign*.9*wave(t) if not horizontal else 0]))
   layers=[layer(groups)]
  else:
   sign=-1 if 'left' in id else 1;layers=[layer([group(es,move=lambda t:[sign*.9*wave(t),0])])]
  description='Single legible directional gesture; selector halves separate along their axis.'
 elif family=='credit':
  moving=[e for e in es if ctr(e)[0]>12 and ctr(e)[1]>10 and max(box(e)[2]-box(e)[0],box(e)[3]-box(e)[1])<10];fixed=[e for e in es if e not in moving];assert moving,id
  ps=[p for e in moving for p in e['path']['v']];pivot=[sum(p[a] for p in ps)/len(ps) for a in [0,1]]
  if 'refresh' in id:dynamic=group(moving,rotate=lambda t:60*wave(t),pivot=pivot)
  elif any(x in id for x in ['down','download','up','upload']):
   sign=-1 if any(x in id for x in ['up','upload']) else 1;dynamic=group(moving,move=lambda t:[0,sign*.7*wave(t)])
  else:dynamic=group(moving,scale=lambda t:[1+.12*wave(t)]*2,pivot=pivot)
  layers=[layer([group(fixed),dynamic])];description='Card stays fixed; only its explanatory badge reacts.'
 elif family=='clipboard':
  fixed,moving=glyph_parts(es)
  # Header clip is also fixed; small content lives below its y=6 boundary.
  fixed+=[e for e in moving if box(e)[3]<=7];moving=[e for e in moving if box(e)[3]>7]
  if moving:layers=[layer([group(fixed),group(moving,move=lambda t:[0,-.55*wave(t)])])]
  else:layers=[layer([group(es,scale=lambda t:[1+.025*wave(t)]*2,pivot=(12,21.5))])]
  description='Clip/body seam repaired; content gives a small coherent reaction without bending the board.'
 elif family=='cursor' and 'box' in id:
  fixed,moving=glyph_parts(es);layers=[layer([group(fixed),group(moving,move=lambda t:[.7*wave(t),-.7*wave(t)])])];description='Only the cursor moves; its box remains fixed.'
 elif family=='alarm':
  if 'off' in id:
   slash=[e for e in es if len(e['path']['v'])==2 and abs(e['path']['v'][0][0]-e['path']['v'][1][0])>14 and abs(e['path']['v'][0][1]-e['path']['v'][1][1])>14];fixed=[e for e in es if e not in slash];layers=[layer([group(fixed),group(slash,opacity=lambda t:100-35*wave(t))])]
  else:
   moving=[e for e in es if 8<=box(e)[0] and box(e)[2]<=16 and 8<=box(e)[1] and box(e)[3]<=17 and not e['path']['c']];fixed=[e for e in es if e not in moving];assert moving,id;layers=[layer([group(fixed),group(moving,scale=lambda t:[1+.12*wave(t)]*2,pivot=(12,13))])]
  description='Alarm body remains legible; only the status sign is accented.'
 elif family=='clock' or family=='watch':
  circles=[e for e in es if e['path']['c'] and abs((box(e)[2]-box(e)[0])-(box(e)[3]-box(e)[1]))<.2 and box(e)[2]-box(e)[0]>10];center=tuple(ctr(max(circles,key=lambda e:box(e)[2]-box(e)[0]))) if circles else (12,12);hands=[e for e in es if not e['path']['c'] and len(e['path']['v'])<=4 and min(math.dist(p,center) for p in e['path']['v'])<1.1 and max(math.dist(p,center) for p in e['path']['v'])>2];fixed=[e for e in es if e not in hands];assert hands,id
  angle=-80 if 'rewind' in id else 120 if 'fast-forward' in id else 360 if 'refresh' in id else 50 if 'stopwatch' in id else 12
  fn=(lambda t:angle*(t*t*(3-2*t))) if 'refresh' in id else (lambda t:angle*wave(t));layers=[layer([group(fixed),group(hands,rotate=fn,pivot=center)])];description='Hands rotate around their dial center; dial, straps and status modifiers stay fixed.'
 elif family=='bell' and 'off' in id:
  on=G.extract((O/'svg/bell-01-lined.svg').read_bytes());layers=morph_state(es,on);behavior='click-toggle';description='Bell off/on is an explicit reversible state transition on the existing bell artwork.'
 elif family=='bell':
  # One coherent physical assembly prevents independently retargeted seams.
  badge=[e for e in es if len(e['path']['v'])<=4 and (box(e)[0]>=16 or ('off' in id and max(box(e)[2]-box(e)[0],box(e)[3]-box(e)[1])>20))];body=[e for e in es if e not in badge]
  layers=[layer([group(body,rotate=lambda t:7*math.sin(t*math.pi*4)*math.sin(math.pi*t)**2,pivot=(12,4)),group(badge)])];description='Bell and clapper form one coherent swinging assembly; modifiers remain separate and readable.'
 elif family in ['bookmark','brackets','code','file','image','info','italic','grid']:
  fixed,moving=glyph_parts(es)
  if family=='grid' and id=='grid-03-lined':fixed=[e for e in es if math.dist(ctr(e),[12,12])<3];moving=[e for e in es if e not in fixed]
  if family=='file':
   fixed+=[e for e in moving if box(e)[1]<8];moving=[e for e in moving if box(e)[1]>=8]
  if moving and fixed:layers=[layer([group(fixed),group(moving,scale=lambda t:[1+.065*wave(t)]*2)])]
  else:layers=[layer([group(es,scale=lambda t:[1+.035*wave(t)]*2)])]
  description='Frame/main object remains anchored where present; meaningful interior detail receives one restrained accent.'
 elif family in ['atom','hand','home','snowflake','virus','recording','search','cloud','coins','line','flag','camera']:
  if family=='recording':
   groups=[]
   for i,e in enumerate(es):
    b=box(e);pivot=ctr(e);groups.append(group([e],scale=lambda t,i=i:[1,1+.12*wave(t,(i%4)*.08,.7+(i%4)*.08)],pivot=pivot))
   layers=[layer(groups)];description='Waveform bars pulse in offset phases while retaining the original bar count.'
  elif family=='line':
   fixed=[e for e in es if len(e['path']['v'])<=3 and box(e)[0]<=4 and box(e)[3]>=20];moving=[e for e in es if e not in fixed];layers=[layer([group(fixed),group(moving,move=lambda t:[0,(-.6 if 'up' in id else .6)*wave(t)])])];description='Restore chart axes; the trend line reacts without losing its graph context.'
  elif family=='flag':
   fixed=[e for e in es if box(e)[2]-box(e)[0]<.05 and box(e)[3]-box(e)[1]>12];moving=[e for e in es if e not in fixed]
   # Continuous x warp is zero on the pole, so cloth connections cannot tear.
   groups=[group(fixed)]
   for e in moving:
    g=G.paint_group(e);paths=[]
    pole=min(p[0] for p in e['path']['v'])
    for f in range(N+1):
     tr=copy.deepcopy(e['path']);w=wave(f/N)
     for j,p in enumerate(tr['v']):tr['v'][j]=[p[0],p[1]+.45*w*max(0,min(1,(p[0]-pole)/12))]
     paths.append(tr)
    g['it'][0]['ks']=prop(lambda t,paths=paths:[paths[min(N,round(t*N))]]);groups.append(g)
   layers=[layer(groups)];description='Pole stays fixed; cloth reacts continuously with its attachment edge anchored.'
  elif family=='search':
   layers=[layer([group(es,scale=lambda t:[1+.035*wave(t)]*2,pivot=(10.5,10.5))])];description='Lens and handle react as one connected assembly; restore the intended large lens geometry.'
  elif family=='hand':layers=[layer([group(es,rotate=lambda t:7*math.sin(t*math.pi*2)*math.sin(math.pi*t)**2,pivot=(12,20))])];description='Coherent greeting around the wrist; fingers never morph independently.'
  elif family=='cloud':layers=[layer([group(es,move=lambda t:[.55*wave(t),0])])];description='Keep restored weather details connected in a short cloud-drift response.'
  else:layers=[layer([group(es,scale=lambda t:[1+.035*wave(t)]*2)])];description='Coherent response on the preserved source assembly; remove fragment-wise distortion.'
 else:return X.author(globals(),id,es)
 return layers,behavior,description

for scene in cfg['scenes']:
 id=scene['id']
 if id not in wanted:continue
 if id in ['reorder-lined','compass-lined']:
  original=json.loads((P/'motion/series/motion.json').read_text());original=next(t for t in original['scenes'] if t['id']==id);scene.update(copy.deepcopy(original))
  for folder in [O,C]:(folder/'geometry'/(id+'.svg')).write_bytes((P/'motion/series/geometry'/(id+'.svg')).read_bytes())
  report.append({'id':id,'description':'Restored the actual earlier scene and motion geometry requested by the user.','user_comment':wanted[id]['comment'],'status':'needs-browser-and-visual-review'});continue
 if id in ['file-06-lined','cloud-lightning-lined']:
  candidates=list(H.glob(id+'-*.json'))+list((P/'review/motion/reference-series/history').glob(id+'-*.json'));previous=next(json.loads(p.read_text()) for p in candidates if not json.loads(p.read_text())['tracks'][0][7].get('authored'))
  ref=previous['tracks'][0][7]['sourceId'];data,details=M.retarget(id,ref,G.extract((O/'svg'/(id+'.svg')).read_bytes()));scene.update(previous);scene['tracks'][0][7]['animationData']=data;scene['duration']=(data['op']-data.get('ip',0))/data['fr']*1000
  for folder in [O,C]:(folder/'animation'/(id+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n')
  report.append({'id':id,'description':'Keep the positively reviewed motion, rebuilt on the repaired geometry.','user_comment':wanted[id]['comment'],'status':'needs-browser-and-visual-review'});continue
 es=G.extract((O/'svg'/(id+'.svg')).read_bytes());result=recipe(id,es)
 if result is None:continue
 layers,behavior,description=result
 for i,l in enumerate(layers):l['ind']=i+1
 digest=hashlib.sha256(json.dumps(old[id],sort_keys=True).encode()).hexdigest();path=H/(id+'-'+digest+'.json')
 if not path.exists():path.write_text(json.dumps(old[id],separators=(',',':'))+'\n')
 duration=400 if behavior in ['click-toggle','hover'] else 1600 if behavior in ['loop','hover-loop'] else 800
 data={'nm':id+' / targeted polish','v':'5.5.2','fr':N*1000/duration,'ip':0,'op':N,'w':24,'h':24,'ddd':0,'assets':[],'layers':layers};scene['duration']=duration;scene['tracks']=[[0,'reference-lottie',1,0,0,0,1,{'version':1,'authored':True,'interaction':behavior,'animationData':data,'sourceId':'targeted-polish','sourceUrl':'','overflow':False}]]
 for folder in [O,C]:(folder/'animation'/(id+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n')
 report.append({'id':id,'description':description,'user_comment':wanted[id]['comment'],'status':'needs-browser-and-visual-review'})
(O/'motion.json').write_text(json.dumps(cfg,separators=(',',':'))+'\n');active={r['id'] for r in json.loads((C/'catalog.json').read_text())};(C/'motion.json').write_text(json.dumps({**{k:v for k,v in cfg.items() if k!='scenes'},'scenes':[s for s in cfg['scenes'] if s['id'] in active]},separators=(',',':'))+'\n');(R/'authored-batch.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Authored',len(report),'targeted scenes; remaining',len(wanted)-len(report))
