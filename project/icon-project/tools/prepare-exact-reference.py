"""Retarget licensed reference timelines to project-owned SVG geometry."""
from pathlib import Path
from importlib.machinery import SourceFileLoader
import copy,json,math,hashlib,xml.etree.ElementTree as E
P=Path('icon-project');O=P/'motion/exact-reference';R=P/'references/motion/useanimations';G=SourceFileLoader('svg_lottie',str(P/'tools/svg-to-lottie.py')).load_module();E.register_namespace('','http://www.w3.org/2000/svg')
catalog={r['id']:r for r in json.loads((P/'result/catalog.json').read_text())};reference={r['id']:r for r in json.loads((R/'catalog.json').read_text())['icons']};manifest=[];scenes=[]
def source(id):return json.loads((R/'json'/f'{id}.json').read_text())
def value(v):return {'a':0,'k':v}
def shift(prop,dx,dy):
 if prop.get('a'):
  for k in prop['k']:
   for field in ['s','e']:
    if field in k:k[field][0]+=dx;k[field][1]+=dy
 else:prop['k'][0]+=dx;prop['k'][1]+=dy

def clear_shapes(data):
 def strip(items):
  out=[]
  for n in items:
   if n['ty'] in ['sh','rc','el','sr','st','fl','gf','gs']:continue
   n=copy.deepcopy(n)
   if n['ty']=='gr':n['it']=strip(n['it'])
   out.append(n)
  return out
 for layer in data['layers']:layer['shapes']=strip(layer.get('shapes',[]))

def group(data,layer,index):return data['layers'][layer]['shapes'][index]
def group_transform(g):return next(n for n in g['it'] if n['ty']=='tr')
def placement(data,layer,index,at_end=False):
 layerM=G.initial_matrix(data['layers'][layer]['ks']);tr=copy.deepcopy(group_transform(group(data,layer,index)))
 if at_end:
  for prop in tr.values():
   if isinstance(prop,dict) and prop.get('a'):prop['k']=prop['k'][-1].get('s',prop['k'][-2].get('e'));prop['a']=0
 return G.multiply(layerM,G.initial_matrix(tr))

def inject(data,layer,index,entries,force=None,at_end=False):
 m=G.inverse(placement(data,layer,index,at_end));g=group(data,layer,index);g['it']=[G.paint_group(e,G.transform_path(e['path'],m),force) for e in entries]+g['it']

def prepare(id,ref,author):
 item=catalog[id];raw=(P/'result/svg'/item['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==item['sha256'];entries=G.extract(raw);original=source(ref);data=copy.deepcopy(original)
 if data.get('assets') or any(l.get('ty')!=4 or l.get('parent') is not None for l in data['layers']):raise ValueError(ref+' needs explicit precomp mapping')
 dx=(24-data['w'])/2;dy=(24-data['h'])/2
 for layer in data['layers']:shift(layer['ks']['p'],dx,dy)
 data['w']=data['h']=24;clear_shapes(data);author(data,original,entries)
 data['nm']=id+' — retargeted from '+ref;data['meta']={'reference':reference.get(ref,{}).get('page','https://useanimations.com/icons/'+ref),'sourceMotionSha256':hashlib.sha256((R/'json'/f'{ref}.json').read_bytes()).hexdigest(),'ownSvgSha256':item['sha256'],'artwork':'All visible shapes are derived from the project SVG. Reference timing and easing retained.'}
 (O/'animation'/f'{id}.json').write_text(json.dumps(data,separators=(',',':'))+'\n');(O/'svg'/f'{id}.svg').write_bytes(raw)
 root=E.fromstring(raw);carrier=E.Element('{http://www.w3.org/2000/svg}g',{'data-part':'0'})
 for n in list(root):root.remove(n);carrier.append(n)
 root.append(carrier);(O/'geometry'/f'{id}.svg').write_bytes(E.tostring(root))
 behavior=reference.get(ref,{}).get('interaction') or {'menu-v2':'click-toggle','toggle':'click-toggle','loading-v3':'loop'}[ref]
 payload={'version':1,'interaction':behavior,'animationData':data,'sourceId':ref,'sourceUrl':'https://useanimations.com/icons/'+ref,'overflow':ref not in ['arrow-right','arrow-left']}
 scene={'id':id,'label':id.removesuffix('-lined').replace('-',' ').title(),'trigger':'reference','duration':(data['op']-data.get('ip',0))/data['fr']*1000,'tracks':[[0,'reference-lottie',1,0,0,0,1,payload]]};scenes.append(scene)
 manifest.append({'id':id,'reference':ref,'interaction':behavior,'duration':scene['duration'],'static_svg_sha256':item['sha256'],'motion_source_sha256':data['meta']['sourceMotionSha256'],'mapping':'Explicit visual-part correspondence; upstream artwork removed','status':'pilot-pending-review'})

def whole(d,o,e):inject(d,0,0,e)
def gear(d,o,e):inject(d,0,0,e[:1]);inject(d,0,1,e[1:])
def globe(d,o,e):inject(d,0,0,e[-2:]);inject(d,1,0,e[:-2])
def bars(d,o,e):
 order=sorted(e,key=lambda p:p['path']['v'][0][0])
 for layer,entry in enumerate(order):
  original=next(n for n in o['layers'][layer]['shapes'][0]['it'] if n['ty']=='sh')['ks'];keys=[];path0=original['k'][0]['s'][0];baseline=path0['v'][0][1];height=baseline-path0['v'][1][1];own=entry['path'];ownBase=own['v'][0][1];ownHeight=ownBase-own['v'][1][1]
  for k in original['k']:
   k=copy.deepcopy(k)
   for field in ['s','e']:
    if field not in k:continue
    y=k[field][0]['v'][1][1];shape=copy.deepcopy(own);shape['v'][1][1]=round(ownBase-ownHeight*(baseline-y)/height,5);k[field]=[shape]
   keys.append(k)
  g=G.paint_group(entry);g['it'][0]['ks']={'a':1,'k':keys};target=group(d,layer,0);target['it']=[g]+target['it']

def like(d,o,e):inject(d,0,0,e);inject(d,1,0,e,force='fill',at_end=True)
def wifi(d,o,e):
 for layer in d['layers']:
  layer['ks']['p']=value([12,19.25,0]);layer['ks']['a']=value([12,19.25,0])
 inject(d,0,0,e[-1:]);inject(d,1,0,e[2:3]);inject(d,2,0,e[1:2]);inject(d,3,0,e[0:1])

def trash(d,o,e):inject(d,0,0,e[:2]);inject(d,0,1,e[2:])
def menu(d,o,e):
 for i,entry in enumerate(e):inject(d,0,i,[entry])
def toggle(d,o,e):inject(d,0,0,e[1:]);inject(d,0,1,e[:1])
def loader(d,o,e):
 # A single intact open arc rotates continuously. Splitting it into independently
 # trimmed quarters caused four disappearing flecks and a discontinuity at its gap.
 d['fr']=30;d['ip']=0;d['op']=60;d['assets']=[]
 tr=copy.deepcopy(G.IDENTITY_TRANSFORM);tr['a']=value([12,12]);tr['p']=value([12,12]);tr['r']={'a':1,'k':[{'t':0,'s':[0],'e':[360],'o':{'x':[0],'y':[0]},'i':{'x':[1],'y':[1]}},{'t':60,'s':[360]}]}
 layer=copy.deepcopy(o['layers'][0]);layer.update(ip=0,op=60,st=0,ks={'o':value(100),'r':value(0),'p':value([0,0,0]),'a':value([0,0,0]),'s':value([100,100,100])},shapes=[{'ty':'gr','it':[G.paint_group(entry) for entry in e]+[tr]}]);d['layers']=[layer]

for id,ref,fn in [('settings-01-lined','settings',gear),('file-02-lined','file',whole),('globe-01-lined','globe',globe),('bar-chart-01-lined','bar-chart',bars),('heart-lined','heart',like),('star-01-lined','star',like),('wifi-lined','wifi',wifi),('trash-01-lined','trash',trash),('arrow-right-lined','arrow-right',whole),('arrow-left-lined','arrow-left',whole),('menu-01-lined','menu-v2',menu),('toggle-03-left-lined','toggle',toggle),('loading-01-lined','loading-v3',loader)]:prepare(id,ref,fn)
config=json.loads((P/'motion/series/motion.json').read_text());config['scenes']=scenes;config['defaultPreset']='Balanced';(O/'motion.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n');(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
policy={'source':'User explicitly requested full useAnimations motion and authorized reference state changes and loops','geometry':'Use current restyled result/svg; never substitute reference drawings','book_exception':'Restore and retain original light compression; no added or turning pages','reference_behavior':'Copy state changes, loops, timing and easing; manual per-icon trigger overrides remain available','full_mapping':{'direct_name_matches':395,'source_animations':184,'part_mapping':'requires visual verification; naming matches are not production-ready'}};(P/'specification/useanimations-transfer-policy.json').write_text(json.dumps(policy,ensure_ascii=False,indent=2)+'\n')
print('Retargeted',len(scenes),'scenes; all visible geometry comes from current project SVGs')
