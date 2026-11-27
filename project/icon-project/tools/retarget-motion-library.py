"""Retarget semantic reference motion to editable project curves, retaining native timelines."""
from pathlib import Path
from importlib.machinery import SourceFileLoader
import copy,json,math,re,hashlib,collections
P=Path('icon-project');R=P/'references/motion/useanimations';O=P/'motion/reference-series'
G=SourceFileLoader('svg_lottie_full',str(P/'tools/svg-to-lottie.py')).load_module()
I=G.IDENTITY;V=lambda x:{'a':0,'k':x}
CAT=json.loads((R/'catalog.json').read_text())['icons'];REF={r['id']:r for r in CAT};DIRECT=json.loads((P/'specification/useanimations-direct-mapping.json').read_text())['matched']
ALIASES={}
def alias(keys,ref):
 for key in keys.split():ALIASES[key]=ref
alias('alert','alert-circle');alias('airpods','headphones');alias('alarm clock watch hourglass old','clock');alias('annotation message notification','message-square');alias('announcement bell','notification-v4');alias('asterisk stars magic','star');alias('atom virus hurricane snowflake','settings-v2');alias('attachment','paperclip');alias('backpack luggage container','briefcase');alias('bank coins cryptocurrency currency piggy wallet safe','dollar-sign');alias('bar horizontal presentation chart line','bar-chart');alias('battery','battery');alias('beaker drop droplets','droplet');alias('bezier perspective skew feather','pen-tool');alias('bluetooth','bluetooth');alias('book passport','book');alias('brackets','code');alias('browser laptop','monitor');alias('brush pencil eraser roller paint','edit-3');alias('building home','home');alias('bus car plane rocket train tram','truck');alias('calculator equal indeterminate','divide');alias('certificate trophy graduation','award');alias('check mark','check');alias('chevron','chevron-down');alias('chrome','cast');alias('clapperboard','film');alias('cloud','cloud');alias('colors palette contrast','aperture');alias('compass navigation mouse cursor','mouse-pointer');alias('cpu data simcard usb','cpu');alias('dataflow route','git-branch');alias('cube','box');alias('diamond pentagon','hexagon');alias('dice grid qr','grid');alias('distribute flex align reorder','align-center');alias('divider slash','slash');alias('dot dots dotpoints','more-horizontal');alias('dropper','edit-2');alias('eagle hand','thumb-up');alias('expand maximize minimize transform scale','maximize-minimize');alias('eye','visibility');alias('face','smile');alias('fast reverse','rewind');alias('filter sliders','filter');alias('fingerprint scan face-id','crosshair');alias('flash lightning','zap');alias('flip reflect','rotate-cw');alias('gaming keyboard','table');alias('glasses webcam microscope telescope','camera');alias('globe','globe');alias('google','chrome');alias('heading letter paragraph pilcrow strikethrough subscript text translate variable','type');alias('hearts heart','heart');alias('help','help');alias('info','info');alias('intersect layer layers','layers');alias('layout rows spacing','layout');alias('left','align-left');alias('right','align-right');alias('lightbulb','sun');alias('link','link');alias('list','list');alias('loading','loading-v4');alias('lock passcode','lock');alias('marker pin','map-pin');alias('medical plus','plus-to-x');alias('microphone','microphone-v2');alias('modem signal','wifi');alias('moon','moon');alias('music','music');alias('package','package');alias('pause play','play-pause');alias('pen','pen-tool');alias('phone','phone');alias('placeholder','square');alias('podcast','radio');alias('puzzle','box');alias('receipt ticket','file-text');alias('recording','radio-button');alias('refresh','refresh-ccw');alias('ruler','align-justify');alias('sale','percent');alias('scales','columns');alias('scissors','scissors');alias('search','search-to-x');alias('shield','shield');alias('stand','monitor');alias('sticker','bookmark');alias('stop','stop-circle');alias('sun','sunset');alias('switch arrows','shuffle');alias('terminal','terminal');alias('thermometer','thermometer');alias('thumbs','thumb-up');alias('toggle','toggle');alias('trend','trending-up');alias('type','type');alias('underline','underline');alias('user','user');alias('users','users');alias('video','video-v2');alias('volume','volume');alias('waves','wind');alias('x','x-square');alias('zap','zap')

def choose(id):
 slug=re.sub(r'-\d+(?=-|$)','',id.removesuffix('-lined'));base=id.split('-')[0]
 if id in DIRECT:return DIRECT[id],'direct-name'
 if base=='building':return 'box','building-assembly'
 if base=='chart' or id.startswith('bar-line'):return 'trending-up','connected-chart'
 if slug in REF:return slug,'direct-normalized'
 if base=='arrow':
  direction=next((s for s in ['down-left','down-right','up-left','up-right','left','right','up','down'] if s in slug),'right');return 'arrow-'+direction,'directional-family'
 if base=='chevron':
  direction=next((s for s in ['left','right','up','down'] if s in slug),'down');return ('chevrons-' if 'double' in slug else 'chevron-')+direction,'directional-family'
 if base=='corner':return next((r for r in REF if r.startswith('corner-') and all(w in r for w in slug.split('-')[1:])),'corner-down-right'),'directional-family'
 if base=='cloud' and 'rain' in slug:return 'cloud-rain','weather-family'
 if base=='cloud' and 'snow' in slug:return 'cloud-snow','weather-family'
 if base in ['heart','star'] and not any(w in slug for w in ['hand','hearts']):return base,'symbol-state'
 if base=='file':return ('file-plus' if 'plus' in slug else 'file-minus' if 'minus' in slug else 'file-text' if 'text' in slug else 'file'),'document-family'
 if base=='folder':return ('folder-plus' if 'plus' in slug else 'folder-minus' if 'minus' in slug else 'folder'),'folder-family'
 if base=='message' or base=='annotation':return 'message-circle' if 'circle' in slug else 'message-square','message-family'
 if base=='face':return ('frown' if any(w in slug for w in ['sad','frown']) else 'meh' if 'neutral' in slug else 'smile'),'expression-family'
 if base=='hourglass':return 'rotate-cw','hourglass-turn'
 if base=='loading':return 'loading-v4','loader-family'
 if base=='line' or base=='trend':return 'trending-down' if 'down' in slug else 'trending-up','chart-family'
 if base=='credit':return 'credit-card','payment-family'
 if base=='eye':return 'visibility-v2' if 'off' in slug else 'visibility','visibility-family'
 if base=='book':return 'book','book-exception'
 if base in ALIASES:return ALIASES[base],'semantic-family'
 if base in REF:return base,'metaphor-family'
 if base=='speedometer':return 'clock','dial-family'
 raise ValueError('Missing semantic motion for '+id)

def interpolate(a,b,u):
 if isinstance(a,bool):return a
 if isinstance(a,(int,float)):return a+(b-a)*u
 if isinstance(a,list):return [interpolate(x,y,u) for x,y in zip(a,b)]
 if isinstance(a,dict):return {k:interpolate(v,b[k],u) if k in b and k!='c' else v for k,v in a.items()}
 return a

def evaluate(prop,time):
 if not prop.get('a'):return prop['k']
 keys=prop['k'];index=max((i for i,k in enumerate(keys) if k['t']<=time),default=0);a=keys[index]
 if index==len(keys)-1 or a.get('h'):return a.get('s',keys[max(0,index-1)].get('e'))
 b=keys[index+1];start=a.get('s',keys[max(0,index-1)].get('e'));end=a.get('e',b.get('s',start));u=max(0,min(1,(time-a['t'])/(b['t']-a['t'])))
 def v(side,axis,default):
  value=a.get(side,{}).get(axis,default);return value[0] if isinstance(value,list) else value
 x1,y1,x2,y2=v('o','x',0),v('o','y',0),v('i','x',1),v('i','y',1);lo=0;hi=1
 for _ in range(22):
  t=(lo+hi)/2;x=3*(1-t)**2*t*x1+3*(1-t)*t*t*x2+t**3
  if x<u:lo=t
  else:hi=t
 t=(lo+hi)/2;return interpolate(start,end,3*(1-t)**2*t*y1+3*(1-t)*t*t*y2+t**3)

def motion_signature(transforms,registration,op):
 reg=G.inverse(registration);result=[]
 for t in [0,op*.2,op*.5,op*.8,op]:
  m=I
  for tr in transforms:
   sampled={k:V(evaluate(v,t)) for k,v in tr.items() if k in ['p','a','s','r'] and isinstance(v,dict)};m=G.multiply(m,G.initial_matrix(sampled))
  result.append([round(v,4) for v in G.multiply(m,reg)])
 return json.dumps(result)

def reference_value(p,default):
 if not p:return default
 if not p.get('a'):return p.get('k',default)
 frames=p.get('k',[])
 # Register visible rest geometry even when an entrance begins at zero scale.
 values=[k.get('s') for k in frames if 's' in k]
 return next((v for v in values if not isinstance(v,list) or any(abs(x)>1e-8 for x in v if isinstance(x,(int,float)))),default)

def matrix(tr):
 tr=copy.deepcopy(tr)
 for k,default in [('p',[0,0]),('a',[0,0]),('s',[100,100]),('r',0)]:tr[k]=V(reference_value(tr.get(k),default) if k=='s' else G.initial_value(tr.get(k),default))
 return G.initial_matrix(tr)

def shift(p,dx,dy):
 if not p:return
 if p.get('s'):
  shift(p['x'],dx,0);shift(p['y'],dy,0);return
 if p.get('a'):
  for key in p['k']:
   for field in ['s','e']:
    if field in key:key[field][0]+=dx;key[field][1]+=dy
 else:p['k'][0]+=dx;p['k'][1]+=dy

def points(path,steps=5):
 out=[];n=len(path['v']);count=n if path['c'] else n-1
 for i in range(count):
  j=(i+1)%n;a=complex(*path['v'][i]);b=a+complex(*path['o'][i]);d=complex(*path['v'][j]);c=d+complex(*path['i'][j])
  for k in range(steps):
   t=k/steps;z=a*(1-t)**3+3*b*t*(1-t)**2+3*c*t*t*(1-t)+d*t**3;out.append([z.real,z.imag])
 if n:out.append(path['v'][0 if path['c'] else -1])
 return out

def bounds(path):
 ps=points(path);xs=[p[0] for p in ps];ys=[p[1] for p in ps];return [min(xs),min(ys),max(xs),max(ys)]
def dist(a,b):return math.hypot(a[0]-b[0],a[1]-b[1])
def score(own,src):
 a=bounds(own);b=bounds(src);aw=a[2]-a[0];ah=a[3]-a[1];bw=b[2]-b[0];bh=b[3]-b[1]
 center=math.hypot((a[0]+a[2]-b[0]-b[2])/2,(a[1]+a[3]-b[1]-b[3])/2)
 scale=abs(aw-bw)+abs(ah-bh);topology=1.1 if own['c']!=src['c'] else 0
 pa=points(own,3)[::2];pb=points(src,3)[::2]
 shape=sum(min(dist(p,q) for q in pb) for p in pa)/len(pa)+sum(min(dist(p,q) for q in pa) for p in pb)/len(pb)
 return center+.4*scale+topology+shape*.8

def enumerate_shapes(data):
 assets={a['id']:a for a in data.get('assets',[])};found=[]
 def groups(items,parent,layer,chain,transforms):
  tr=next((n for n in items if n.get('ty')=='tr'),None);local=G.multiply(parent,matrix(tr)) if tr else parent;transforms=transforms+([tr] if tr else [])
  for i,n in enumerate(items):
   if n['ty']=='gr':groups(n['it'],local,layer,chain+[(items,i)],transforms)
   elif n['ty']=='sh':
    ks=n['ks'];path=copy.deepcopy(ks['k'][0]['s'][0] if ks.get('a') else ks['k'])
    if not path.get('v'):continue
    found.append({'items':items,'shape':n,'path':path,'world':G.transform_path(path,local),'matrix':local,'layer':layer,'chain':chain,'delta_signature':motion_signature(transforms,local,data['op']),'paint':next((p for p in items if p['ty'] in ['st','fl']),None)})
 def layers(ls,parent,transforms):
  for layer in ls:
   local=G.multiply(parent,matrix(layer['ks']))
   if layer['ty']==4:groups(layer['shapes'],local,layer,[],transforms+[layer['ks']])
   elif layer['ty']==0:layers(assets[layer['refId']]['layers'],local,transforms+[layer['ks']])
   else:raise ValueError('Non-shape reference layer')
 layers(data['layers'],I,[]);return found

def strip_geometry(data):
 def strip(items):
  result=[]
  for n in items:
   if n['ty'] in ['sh','st','fl','gf','gs','mm']:continue
   if n['ty']=='gr':strip(n['it'])
   result.append(n)
  items[:]=result
 for l in data['layers']:
  l.pop('masksProperties',None);l['hasMask']=False
  if l['ty']==4:strip(l['shapes'])
 for a in data.get('assets',[]):
  for l in a.get('layers',[]):
   l.pop('masksProperties',None);l['hasMask']=False
   if l['ty']==4:strip(l['shapes'])

def morph_transfer(own,source,shared_bounds=None):
 keys=source['shape']['ks'];rest=source['path'];samples=points(rest,5);box=shared_bounds or bounds(own);refbox=bounds(rest);sx=(refbox[2]-refbox[0])/max(box[2]-box[0],.01);sy=(refbox[3]-refbox[1])/max(box[3]-box[1],.01)
 def correspondence(p):
  mapped=[refbox[0]+(p[0]-box[0])*sx,refbox[1]+(p[1]-box[1])*sy];nearest=sorted(range(len(samples)),key=lambda i:dist(mapped,samples[i]))[:3];weights=[1/max(dist(mapped,samples[i]),.025)**3 for i in nearest];den=sum(weights);return nearest,[w/den for w in weights]
 bindings={}
 for i,v in enumerate(own['v']):
  for handle in ['v','i','o']:
   p=v if handle=='v' else [v[0]+own[handle][i][0],v[1]+own[handle][i][1]];bindings[(i,handle)]=correspondence(p)
 def deform(path):
  target=points(path,5)
  if len(target)!=len(samples):return copy.deepcopy(own)
  warped={}
  for key,(indices,weights) in bindings.items():
   i,h=key;v=own['v'][i];p=v if h=='v' else [v[0]+own[h][i][0],v[1]+own[h][i][1]];delta=[sum((target[j][axis]-samples[j][axis])*w for j,w in zip(indices,weights)) for axis in [0,1]]
   # A flat target axis still transfers displacement at natural project scale.
   warped[key]=[p[0]+delta[0]/(sx if abs(sx)>.01 else 1),p[1]+delta[1]/(sy if abs(sy)>.01 else 1)]
  result=copy.deepcopy(own)
  for i in range(len(own['v'])):
   result['v'][i]=[round(x,5) for x in warped[(i,'v')]]
   for h in ['i','o']:result[h][i]=[round(warped[(i,h)][a]-warped[(i,'v')][a],5) for a in [0,1]]
  return result
 result=copy.deepcopy(keys)
 for k in result['k']:
  for field in ['s','e']:
   if field in k:k[field]=[deform(k[field][0])]
 return result

def has_transform_motion(src):
 ls=[src['layer']['ks']]+[next((n for n in items[i]['it'] if n['ty']=='tr'),{}) for items,i in src['chain']]
 return any(any(v.get('a') for k,v in tr.items() if k in ['p','a','s','r'] and isinstance(v,dict)) for tr in ls)

def signature(src):
 morph=src['shape']['ks']
 return src['delta_signature']+(json.dumps(morph,sort_keys=True) if morph.get('a') else '')

def connected(a,b):
 if a['c'] and b['c']:return False
 ps=points(b,20)
 for p in ([] if a['c'] else [a['v'][0],a['v'][-1]]):
  for x,y in zip(ps,ps[1:]):
   dx=y[0]-x[0];dy=y[1]-x[1];den=dx*dx+dy*dy;t=max(0,min(1,((p[0]-x[0])*dx+(p[1]-x[1])*dy)/den)) if den else 0
   if dist(p,[x[0]+t*dx,x[1]+t*dy])<.035:return True
 return False

def retarget(id,ref,entries):
 original=json.loads((R/'json'/(ref+'.json')).read_text());d=copy.deepcopy(original)
 for l in d['layers']:shift(l['ks'].get('p'),(24-d['w'])/2,(24-d['h'])/2)
 d['w']=d['h']=24
 special=SourceFileLoader('reference_specials',str(P/'tools/reference-motion-specials.py')).load_module().author(__import__(__name__),id,ref,d,entries)
 if special:return d,special
 candidates=enumerate_shapes(d)
 candidates=[c for c in candidates if not(c['paint'] and c['paint'].get('c',{}).get('k')==[1,1,1,1])] 
 if not candidates:raise ValueError('No reference parts: '+ref)
 if ref in ['visibility','microphone','video','microphone-v2','video-v2','cloud-off','shield-off','zap-off','camera-off','notification']:
  slashes=[c for c in candidates if len(c['path']['v'])==2 and abs(c['world']['v'][0][0]-c['world']['v'][1][0])>8 and abs(c['world']['v'][0][1]-c['world']['v'][1][1])>8]
  if slashes and not any(len(e['path']['v'])==2 and abs(e['path']['v'][0][0]-e['path']['v'][1][0])>8 and abs(e['path']['v'][0][1]-e['path']['v'][1][1])>8 for e in entries):
   entries=entries+[{'path':G.bezier_paths('M2 2L22 22')[0],'style':{'stroke':'currentColor','fill':'none','stroke-linecap':'round','stroke-linejoin':'round'},'constructed_state':'mute slash in project keylines'}]
 chosen=[min(range(len(candidates)),key=lambda i:score(e['path'],candidates[i]['world'])) for e in entries]
 # Keep mechanically joined artwork on the same transform. Morphs may articulate
 # internally when their registration does not introduce independent transforms.
 joints=[]
 for i in range(len(entries)):
  for j in range(i):
   if connected(entries[i]['path'],entries[j]['path']) or connected(entries[j]['path'],entries[i]['path']):joints.append((i,j))
 parents=list(range(len(entries)))
 def find(i):
  while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
  return i
 for i,j in joints:parents[find(i)]=find(j)
 components=collections.defaultdict(list)
 for i in range(len(entries)):components[find(i)].append(i)
 merged=0
 for component in components.values():
  if len({signature(candidates[chosen[i]]) for i in component})>1:
   options={chosen[i] for i in component};pick=min(options,key=lambda k:sum(score(entries[i]['path'],candidates[k]['world']) for i in component))
   for i in component:chosen[i]=pick
   merged+=1
 active=lambda c:has_transform_motion(c) or c['shape']['ks'].get('a') or any(n.get('ty')=='tm' and any(isinstance(v,dict) and v.get('a') for v in n.values()) for items,i in c['chain'] for n in items[i]['it'])
 if not any(active(candidates[k]) for k in chosen):
  moving=[k for k,c in enumerate(candidates) if active(c)]
  if moving:
   index=min(range(len(entries)),key=lambda i:min(score(entries[i]['path'],candidates[k]['world']) for k in moving));pick=min(moving,key=lambda k:score(entries[index]['path'],candidates[k]['world']));component={index}
   for _ in entries:
    for i,j in joints:
     if i in component or j in component:component.update([i,j])
   for i in component:chosen[i]=pick
 strip_geometry(d)
 # A common correspondence box gives shared vertices the same deformation.
 # Normalizing each fragment separately tears connected contours apart.
 shared_boxes={}
 for index in set(chosen):
  target=candidates[index]
  boxes=[bounds(G.transform_path(e['path'],G.inverse(target['matrix']))) for e,k in zip(entries,chosen) if k==index]
  shared_boxes[index]=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]
 morphed=0;assignments=[]
 for entry,index in zip(entries,chosen):
  target=candidates[index];local=G.transform_path(entry['path'],G.inverse(target['matrix']));g=G.paint_group(entry,local)
  if target['shape']['ks'].get('a'):
   g['it'][0]['ks']=morph_transfer(local,target,shared_boxes[index]);morphed+=1
  paint=target['paint']
  if paint and paint.get('o',{}).get('a'):
   for part in g['it']:
    if part['ty'] in ['st','fl']:part['o']=copy.deepcopy(paint['o'])
  # Original path order is retained inside each reference motion assembly.
  items=target['items'];at=next((i for i,n in enumerate(items) if n['ty'] in ['tr','tm']),len(items));items.insert(at,g)
  assignments.append({'reference_part':index,'morph':bool(target['shape']['ks'].get('a'))})
 d['nm']=id+' / '+ref;d['meta']={'artwork':'Project-owned SVG paths only','reference':REF[ref]['page'],'retarget':'semantic/part correspondence','sourceSha256':hashlib.sha256((R/'json'/(ref+'.json')).read_bytes()).hexdigest()}
 return d,{'parts':len(entries),'source_parts':len(candidates),'morphed_parts':morphed,'joined_components':merged,'assignments':assignments}

if __name__=='__main__':
 import xml.etree.ElementTree as E
 E.register_namespace('','http://www.w3.org/2000/svg')
 for folder in ['svg','geometry','animation']:(O/folder).mkdir(parents=True,exist_ok=True)
 approved=json.loads((P/'motion/exact-reference/motion.json').read_text());pilots={s['id']:s for s in approved['scenes']};main=json.loads((P/'motion/series/motion.json').read_text());old={s['id']:s for s in main['scenes']};out=[];manifest=[];errors=[]
 catalog=json.loads((P/'result/catalog.json').read_text())
 for count,item in enumerate(catalog):
  id=item['id'];raw=(P/'result/svg'/item['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==item['sha256']
  try:
   ref,method=choose(id)
   if id in pilots:
    scene=copy.deepcopy(pilots[id]);d=scene['tracks'][0][7]['animationData'];details={'approved_pilot':True};geometry=(P/'motion/exact-reference/geometry'/(id+'.svg')).read_bytes();ref=scene['tracks'][0][7]['sourceId'];method='approved-pilot-loader-revised' if id.startswith('loading') else 'approved-pilot'
   elif id.startswith('book-'):
    scene=copy.deepcopy(old[id]);geometry=(P/'motion/series/geometry'/(id+'.svg')).read_bytes();d=None;details={'book_original_preserved':True};method='explicit-book-exception'
   else:
    entries=G.extract(raw)
    if not entries:raise ValueError('No SVG paths extracted')
    d,details=retarget(id,ref,entries);scene={'id':id,'label':old[id]['label'],'trigger':'reference','duration':(d['op']-d.get('ip',0))/d['fr']*1000,'tracks':[[0,'reference-lottie',1,0,0,0,1,{'version':1,'interaction':REF[ref]['interaction'],'animationData':d,'sourceId':ref,'sourceUrl':REF[ref]['page'],'overflow':not ref.startswith(('arrow','chevron','corner'))}]]}
    root=E.fromstring(raw);carrier=E.Element('{http://www.w3.org/2000/svg}g',{'data-part':'0'})
    for n in list(root):root.remove(n);carrier.append(n)
    root.append(carrier);geometry=E.tostring(root)
   (O/'svg'/(id+'.svg')).write_bytes(raw);(O/'geometry'/(id+'.svg')).write_bytes(geometry)
   if d:(O/'animation'/(id+'.json')).write_text(json.dumps(d,separators=(',',':'))+'\n')
   out.append(scene);manifest.append({'id':id,'reference':ref,'method':method,'interaction':scene['tracks'][0][7]['interaction'] if d else scene['trigger'],'static_sha256':item['sha256'],'status':'needs-visual-review','details':details})
  except Exception as e:errors.append({'id':id,'error':str(e)})
  if (count+1)%100==0:print('Prepared',count+1,'/',len(catalog),'errors',len(errors),flush=True)
 config={k:v for k,v in main.items() if k!='scenes'};config['scenes']=out;(O/'motion.json').write_text(json.dumps(config,separators=(',',':'))+'\n');(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(O/'errors.json').write_text(json.dumps(errors,indent=2)+'\n');print('Prepared',len(out),'errors',errors,flush=True)
