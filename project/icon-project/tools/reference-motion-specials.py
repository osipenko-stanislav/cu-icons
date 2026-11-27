"""Explicit connected-geometry choreography for charts, toggles, dials and state symbols."""
import copy,math,re

def author(M,id,ref,d,entries):
 G=M.G;V=M.V;I=M.I
 def empty(fr=None,op=None):
  d['assets']=[];d['layers']=[]
  if fr:d['fr']=fr
  if op:d['op']=op
 def layer(groups,ks=None,mask=None):
  n={'ddd':0,'ind':len(d['layers'])+1,'ty':4,'sr':1,'ks':ks or {'o':V(100),'r':V(0),'p':V([0,0,0]),'a':V([0,0,0]),'s':V([100,100,100])},'ao':0,'shapes':groups,'ip':0,'op':d['op'],'st':0,'bm':0}
  if mask:n['hasMask']=True;n['masksProperties']=[mask]
  d['layers'].append(n);return n
 def tr():return copy.deepcopy(G.IDENTITY_TRANSFORM)
 def group(es,transform=None):return {'ty':'gr','it':[G.paint_group(e) for e in es]+[transform or tr()]}
 def apply_fn(path,fn):
  p=copy.deepcopy(path)
  for i,v in enumerate(path['v']):
   n=fn(v);p['v'][i]=n
   for h in ['i','o']:
    q=fn([v[0]+path[h][i][0],v[1]+path[h][i][1]]);p[h][i]=[q[0]-n[0],q[1]-n[1]]
  for h in ['v','i','o']:p[h]=[[round(x,5) for x in q] for q in p[h]]
  return p
 def baked(es,fn):
  for entry in es:
   g=G.paint_group(entry);g['it'][0]['ks']={'a':1,'k':[{'t':f,'s':[apply_fn(entry['path'],lambda p:fn(p,f))],'o':{'x':0,'y':0},'i':{'x':1,'y':1}} for f in range(int(d['op'])+1)]};yield g
 def enclosing(i):
  a=M.bounds(entries[i]['path']);return entries[i]['path']['c'] and any(j!=i and a[0]<M.bounds(e['path'])[0]-.1 and a[1]<M.bounds(e['path'])[1]-.1 and a[2]>M.bounds(e['path'])[2]+.1 and a[3]>M.bounds(e['path'])[3]+.1 for j,e in enumerate(entries))
 if id in ['globe-04-lined','globe-05-lined','globe-06-lined','globe-slated-02-lined']:
  src=M.json.loads((M.R/'json/globe.json').read_text());keys=src['layers'][0]['ks']['s']
  moving_indices={'globe-04-lined':{0,1},'globe-05-lined':{1,2,3,4},'globe-06-lined':{0},'globe-slated-02-lined':{4}}[id]
  moving=[e for i,e in enumerate(entries) if i in moving_indices];fixed=[e for i,e in enumerate(entries) if i not in moving_indices]
  center=11.5 if id=='globe-slated-02-lined' else 12
  def warp(p,f):return [center+(p[0]-center)*M.evaluate(keys,f)[0]/100,p[1]]
  empty(src['fr'],src['op']);layer([group(fixed)]);layer(list(baked(moving,warp)))
  return {'special':'reference globe scale timeline on geographic interior; globe outline, pointer and stand stay anchored'}
 if ref in ['heart','star']:
  original=copy.deepcopy(d);c=M.enumerate_shapes(d);outline=c[0];filled=c[1];end=copy.deepcopy(d)
  def endscale(n):
   if isinstance(n,dict):
    if n.get('ty')=='tr' and n.get('s',{}).get('a'):n['s']=V(n['s']['k'][-1]['s'])
    if 'ks' in n and isinstance(n['ks'],dict) and n['ks'].get('s',{}).get('a'):n['ks']['s']=V(n['ks']['s']['k'][-1]['s'])
    for v in n.values():endscale(v)
   elif isinstance(n,list):
    for v in n:endscale(v)
  endscale(end);fillMatrix=M.enumerate_shapes(end)[1]['matrix'];M.strip_geometry(d)
  fixed=[];moving=[]
  for i,e in enumerate(entries):
   if enclosing(i) or (id.startswith('heart-hand') and sum(q[1] for q in e['path']['v'])/len(e['path']['v'])>14):fixed.append(e)
   else:moving.append(e)
  for e in moving:
   outline['items'].insert(0,G.paint_group(e,G.transform_path(e['path'],G.inverse(outline['matrix']))))
   if e['path']['c']:filled['items'].insert(0,G.paint_group(e,G.transform_path(e['path'],G.inverse(fillMatrix)),force='fill'))
  if fixed:layer([group(fixed)])
  return {'special':'state fill on own silhouette; enclosing frame anchored'}
 if id.startswith('toggle-'):
  original=copy.deepcopy(d);source_tr=next(n for n in original['layers'][0]['shapes'][0]['it'] if n['ty']=='tr');keys=copy.deepcopy(source_tr['p']);variant=id.split('-')[1];right='right' in id;center=17 if right else 7;radius=5;top=7;height=10
  if variant=='02':top=8;height=8
  if variant=='03':top=6;height=12;center=16 if right else 8;radius=2.5
  target=24-center;delta=target-center
  for k in keys['k']:
   for field in ['s','e']:
    if field in k:k[field]=[(k[field][0]-8)/8*delta,0]
   k.pop('to',None);k.pop('ti',None)
  style={'fill':'none','stroke':'currentColor','stroke-linecap':'round','stroke-linejoin':'round'}
  knob={'path':G.extract(f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor"><circle cx="{center}" cy="12" r="{radius}"/></svg>'.encode())[0]['path'],'style':style}
  track=G.extract(f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor"><rect x="2" y="{top}" width="20" height="{height}" rx="{height/2}"/></svg>'.encode())[0];track['style']=style
  empty();motion=tr();motion['p']=keys;layer([group([knob],motion)])
  maskKeys=copy.deepcopy(keys)
  for k in maskKeys['k']:
   for field in ['s','e']:
    if field in k:
     x=k[field][0];k[field]=[apply_fn(knob['path'],lambda p:[p[0]+x,p[1]])]
  layer([group([track])],mask={'inv':False,'mode':'s','pt':maskKeys,'o':V(100),'x':V(0),'nm':'Own knob occludes own track'})
  return {'special':'knob moves coherently; track occlusion follows knob; left/right endpoints respected'}
 if id.startswith(('presentation-chart','bar-chart-square')):
  src=M.json.loads((M.R/'json/bar-chart.json').read_text())
  sourcepaths=[next(n for n in l['shapes'][0]['it'] if n['ty']=='sh')['ks'] for l in src['layers']]
  bars=[];fixed=[]
  for e in entries:
   b=M.bounds(e['path'])
   if not e['path']['c'] and b[2]-b[0]<.01 and 5<=b[0]<=19 and 5<=b[1]<b[3]<=18:bars.append(e)
   else:fixed.append(e)
  if bars:
   empty(src['fr'],src['op']);layer([group(fixed)])
   for i,e in enumerate(sorted(bars,key=lambda e:M.bounds(e['path'])[0])):
    prop=sourcepaths[min(i,len(sourcepaths)-1)];rest=prop['k'][0]['s'][0];height=rest['v'][0][1]-rest['v'][1][1];base=M.bounds(e['path'])[3]
    def warp(p,f,prop=prop,height=height,base=base):
     q=M.evaluate(prop,f)[0];ratio=(q['v'][0][1]-q['v'][1][1])/height
     return [p[0],base+(p[1]-base)*ratio]
    layer(list(baked([e],warp)))
   return {'special':'only chart bars change height; presentation frame and stand remain anchored'}
 if ref=='bar-chart' or id.startswith('horizontal-bar-chart'):
  src=M.json.loads((M.R/'json/bar-chart.json').read_text());sourcepaths=[next(n for n in l['shapes'][0]['it'] if n['ty']=='sh')['ks'] for l in src['layers']];horizontal=id.startswith('horizontal-');axis=0 if horizontal else 1;cross=1-axis
  fixed=[e for i,e in enumerate(entries) if enclosing(i)];moving=[e for i,e in enumerate(entries) if not enclosing(i)]
  ps=[p for e in moving for p in M.points(e['path'])];lo=[min(p[a] for p in ps) for a in [0,1]];hi=[max(p[a] for p in ps) for a in [0,1]];base=lo[axis] if horizontal else hi[axis];centers=[lo[cross]+(hi[cross]-lo[cross])*(i+.5)/3 for i in range(3)]
  def ratio(i,f):
   p=M.evaluate(sourcepaths[i],f)[0];rest=sourcepaths[i]['k'][0]['s'][0];height=rest['v'][0][1]-rest['v'][1][1];return (p['v'][0][1]-p['v'][1][1])/height
  def warp(p,f):
   x=p[cross];r=[ratio(i,f) for i in range(3)]
   if x<=centers[0]:s=r[0]
   elif x>=centers[2]:s=r[2]
   else:
    i=0 if x<centers[1] else 1;u=(x-centers[i])/(centers[i+1]-centers[i]);s=r[i]*(1-u)+r[i+1]*u
   q=p[:];q[axis]=base+(p[axis]-base)*s;return q
  empty(src['fr'],src['op']);groups=list(baked(moving,warp));layer(groups+[group(fixed)] if fixed else groups)
  return {'special':'shared continuous chart deformation; connected column edges and baseline preserved'}
 if id.startswith(('speedometer','watch-','alarm-clock','clock-')) and not id.startswith('clock-lined'):
  src=M.json.loads((M.R/'json/clock.json').read_text());rotations=[l['ks']['r'] for l in src['layers'] if l['ks'].get('r',{}).get('a')];needle=[];fixed=[]
  for entry in entries:
   ps=entry['path']['v'];r=[M.dist(p,[12,12]) for p in ps]
   if not entry['path']['c'] and ((min(r)<3 and max(r)>3.2) or (min(r)<.15 and max(r)>2)) and len(ps)<=4:needle.append(entry)
   else:fixed.append(entry)
  if not needle:
   # For an undivided hourglass or dial use the reference whole-object turn.
   return None
  empty(src['fr'],src['op']);layer([group(fixed)])
  for i,e in enumerate(needle):
   t=tr();t['p']=V([12,12]);t['a']=V([12,12]);t['r']=copy.deepcopy(rotations[i%len(rotations)]);layer([group([e],t)])
  return {'special':'hands pivot at dial center; scale and hour marks stay anchored'}
 if id.startswith(('layout-','columns-','rows-','spacing-','expand-','maximize-','scale-','transform-')):
  src=M.json.loads((M.R/'json/layout.json').read_text());xkeys=src['layers'][1]['ks']['p'];ykeys=src['layers'][0]['ks']['p'];ps=[p for e in entries for p in M.points(e['path'])];lo=[min(p[a] for p in ps) for a in [0,1]];hi=[max(p[a] for p in ps) for a in [0,1]];fixed=[e for i,e in enumerate(entries) if enclosing(i)];moving=[e for i,e in enumerate(entries) if not enclosing(i)]
  def warp(p,f):
   dx=(M.evaluate(xkeys,f)[0]-16)/18;dy=(M.evaluate(ykeys,f)[1]-16)/18;q=[]
   for a,delta in enumerate([dx,dy]):
    width=hi[a]-lo[a];u=(p[a]-lo[a])/max(width,.01);weight=max(0,1-abs(u-.5)*2);q.append(p[a]+delta*width*weight)
   return q
  empty(src['fr'],src['op']);layer(list(baked(moving,warp))+([group(fixed)] if fixed else []));return {'special':'continuous panel reflow with anchored bounds and shared junctions'}
 if id=='scales-01-lined':
  src=M.json.loads((M.R/'json/columns.json').read_text());keys=src['layers'][0]['ks']['p']
  def warp(p,f):
   delta=(M.evaluate(keys,f)[0]-16)*.4
   return [p[0],p[1]+delta*max(-1,min(1,(p[0]-12)/2))]
  empty(src['fr'],src['op']);layer(list(baked(entries,warp)))
  return {'special':'reference column timing drives opposing scale pans; shared continuous deformation preserves all joins'}
 return None
