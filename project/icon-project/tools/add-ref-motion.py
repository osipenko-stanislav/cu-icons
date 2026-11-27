"""Add unique supplied ref artwork without replacing existing library geometry."""
from pathlib import Path
import json,hashlib,copy,xml.etree.ElementTree as E
P=Path('icon-project');O=P/'motion/reference-series';C=P/'result/curated';R=P/'review/motion/ref-additions-2026-11-27';R.mkdir(exist_ok=True)
E.register_namespace('','http://www.w3.org/2000/svg');ns='{http://www.w3.org/2000/svg}'
new_names='bed bio chair closet cross-brand cross-brand-2 fridge iron kitchen laundry math microwave museum plates shower steam teacher walk brand-network-lined'.split()
# Household/subject/brand concepts absent from the retained collection. Branded
# variants of an existing metaphor are recorded as aliases, never substituted.
explicit={
'arrow-link':'link-external-01-lined','award':'award-01-lined','bell':'bell-01-lined','book':'book-open-01-lined','brand-academic-lined':'graduation-hat-01-lined','brand-award1-lined':'award-01-lined','brand-biotech-lined':'beaker-01-lined','brand-briefcase-lined':'briefcase-01-lined','brand-chart-lined':'bar-chart-01-lined','brand-chip-lined':'cpu-chip-01-lined','brand-code-lined':'code-01-lined','brand-device-desktop-lined':'monitor-01-lined','brand-doc-lined':'file-02-lined','brand-glasses-lined':'glasses-01-lined','brand-home-lined':'home-01-lined','brand-math-lined':'ref-math','brand-message-lined':'message-circle-01-lined','brand-molecule-lined':'ref-bio','brand-question-lined':'help-circle-lined','brand-rocket-lined':'rocket-01-lined','brand-shield-lined':'shield-01-lined','brand-shine-lined':'stars-01-lined','brand-smile-lined':'face-happy-lined','brand-users2-lined':'users-03-lined','brand-way-lined':'route-lined','cap-academic':'graduation-hat-01-lined','case':'briefcase-01-lined','chat':'message-chat-circle-lined','check':'check-lined','chervon-down':'chevron-down-lined','chervon-up':'chevron-up-lined','chip':'cpu-chip-01-lined','clock':'clock-lined','code':'code-01-lined','copy':'copy-01-lined','coworking':'lightbulb-01-lined','data':'database-01-lined','desktop':'monitor-01-lined','doc':'file-02-lined','dot':'dot-single-lined','dots':'dots-horizontal-lined','download':'download-01-lined','edit-01':'edit-01-lined','edit-02':'edit-01-lined','error':'x-circle-lined','file':'file-01-lined','filter':'filter-funnel-01-lined','flag':'flag-01-lined','glasses':'glasses-01-lined','grow':'trend-up-01-lined','heart':'heart-lined','hide':'eye-off-lined','home':'home-01-lined','info':'info-circle-lined','loading':'loading-01-lined','log-out-03':'log-out-01-lined','marker-pin-01':'marker-pin-01-lined','marker-pin-04':'marker-pin-04-lined','marketeq_wallet-money':'wallet-01-lined','medical':'medical-cross-lined','menu':'menu-01-lined','message':'message-circle-01-lined','mode':'contrast-02-lined','moon-02-lined':'moon-01-lined','pin':'pin-01-lined','play-circle':'play-circle-lined','play-square-lined':'play-square-lined','profile':'user-01-lined','reward':'award-01-lined','rocket':'rocket-01-lined','sale':'sale-01-lined','search':'search-md-lined','shield':'shield-01-lined','shine':'stars-01-lined','show':'eye-lined','success':'check-circle-lined','sun-lined':'sun-lined','trash':'trash-01-lined','trophy':'trophy-01-lined','users-plus':'users-plus-lined','users':'users-03-lined','way':'route-lined','wifi':'wifi-lined','x-close':'x-close-lined','minus-round':'minus-circle-lined','minus':'minus-lined'}
aliases=json.loads((P/'archive/semantic-duplicates/aliases.json').read_text());catalog=json.loads((P/'result/catalog.json').read_text());curated=json.loads((C/'catalog.json').read_text());active={r['id'] for r in curated}
ids={n:'ref-'+n.removesuffix('-lined') for n in new_names}
if (R/'import.json').exists() and set(ids.values())<=active:
 print('Reference additions already imported; keeping the original import evidence.');raise SystemExit(0)
def resolve(id):
 while id in aliases:id=aliases[id]
 return id
inventory=[]
for p in sorted(Path('ref').glob('*.svg')):
 name=p.stem
 if name in ids:inventory.append({'source':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'action':'add','id':ids[name]})
 else:
  target=resolve(explicit.get(name,name if name.endswith('-lined') else name+'-lined'))
  assert target in active or target in ids.values(),(name,target)
  inventory.append({'source':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'action':'skip-semantic-duplicate','canonical':target,'basis':'Same supplied metaphor/action; branded/style variant or existing equivalent.'})
config=json.loads((O/'motion.json').read_text());manifest=json.loads((O/'manifest.json').read_text());old_scene_hashes={s['id']:hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest() for s in config['scenes']};created=[]
for name,id in ids.items():
 if id in active:continue
 raw=(Path('ref')/(name+'.svg')).read_bytes();root=E.fromstring(raw);root.set('stroke-width',root.get('stroke-width','1'));root.set('color','currentColor')
 def normalize(n,definition=False):
  definition=definition or n.tag.split('}')[-1] in ['defs','mask','clipPath']
  if not definition:
   for k in ['stroke','fill']:
    if n.get(k) in ['white','black','#141414','#D9D9D9','#000','#000000','#fff','#ffffff']:n.set(k,'currentColor')
  for c in n:normalize(c,definition)
 normalize(root)
 if name=='kitchen':
  # The source's inward-clipped double stroke does not follow the shared
  # non-scaling width control. Keep its ellipse geometry as a live stroke.
  ellipse=next(n for n in root.iter() if n.tag.split('}')[-1]=='ellipse')
  ellipse.attrib.pop('mask',None);ellipse.attrib.pop('stroke-width',None)
  for parent in root.iter():
   for child in list(parent):
    if child.tag.split('}')[-1]=='mask':parent.remove(child)
 static=E.tostring(root);geo=copy.deepcopy(root);carrier=E.Element(ns+'g',{'data-part':'0'});geo.append(carrier)
 for n in list(geo):
  if n is not carrier and n.tag.split('}')[-1]!='defs':geo.remove(n);carrier.append(n)
 leaves=[]
 def parts(n,definition=False):
  definition=definition or n.tag.split('}')[-1] in ['defs','mask','clipPath']
  if not definition and n.tag.split('}')[-1] in ['path','circle','ellipse','line','rect','polygon','polyline']:
   assert not n.get('transform');leaves.append(n);n.set('data-part',str(len(leaves)))
  for c in n:parts(c,definition)
 parts(carrier)
 def track(part,kind,amount,x=12,y=12,start=0,end=1,profile='mechanism'):return [part,kind,amount,x,y,start,end,profile]
 duration=850;trigger='hover';cls='object-gesture';description='';tracks=[]
 if name=='bed':tracks=[track(0,'scale-y',-.025,12,20.58)];description='Soft compression returns to rest; complete bed remains connected.'
 elif name=='bio':tracks=[track(0,'rotate',6)];description='Connected molecular structure gives a short rotational response.'
 elif name=='chair':tracks=[track(0,'rotate',-3,12,21)];description='Chair tilts around its base, all components together.'
 elif name=='closet':tracks=[track(3,'erase-redraw',1,start=.05,end=.8),track(4,'erase-redraw',1,start=.2,end=.95)];cls='signal-propagation';description='Sequential handle glints; cabinet and doors stay fixed.'
 elif name.startswith('cross-brand'):tracks=[track(0,'scale',.07)];description='Single restrained brand accent; identity and orientation stay intact.'
 elif name=='fridge':tracks=[track(4,'erase-redraw',1,start=.1,end=.9)];cls='signal-propagation';description='Handle glint; no invented door opening or cabinet deformation.'
 elif name=='iron':tracks=[track(0,'x',.85,profile='direction')];description='Short coherent ironing stroke along the sole direction.'
 elif name=='kitchen':tracks=[track(i,'y',-.4,profile='hinge') for i in [1,4]]+[track(i,'y',.55,profile='hinge') for i in [2,3]];description='Fork moves slightly down; spoon moves slightly up; joined parts share the same motion.'
 elif name=='laundry':tracks=[track(4,'scale',.6,15.5,5,start=.05,end=.7),track(5,'scale',.6,17.5,5,start=.25,end=.95)];cls='signal-propagation';description='Panel indicators respond in sequence; body and drum remain still.'
 elif name=='math':tracks=[track(i,'x',-.7 if i<=2 else .7,profile='direction') for i in range(1,5)];description='Brace pairs expand together, preserving both joined halves.'
 elif name=='microwave':tracks=[track(2,'scale',.4,19.0001,16,start=.05,end=.7),track(3,'scale',.4,19.0001,13,start=.25,end=.95)];cls='signal-propagation';description='Short phased panel-indicator response; screen and cabinet stay fixed.'
 elif name=='museum':
  cols=[i for i,n in enumerate(leaves,1) if n.tag.split('}')[-1]=='path' and 'V21' in n.get('d','')];tracks=[track(i,'erase-redraw',1,start=.05+j*.1,end=.65+j*.1) for j,i in enumerate(cols)];cls='signal-propagation';description='Column accents travel in sequence inside the original clip; capital stays anchored.'
 elif name=='plates':tracks=[track(2,'erase-redraw',1,start=.1,end=.9)];cls='signal-propagation';description='Inner plate-ring highlight; original foreground occlusion and clip are retained.'
 elif name=='shower':tracks=[track(3,'erase-redraw',1,start=.1,end=.95)];cls='signal-propagation';description='Water marks redraw below the fixed shower head.'
 elif name=='steam':tracks=[track(i,'y',-.6,start=.05+(i-3)*.12,end=.7+(i-3)*.12,profile='ripple') for i in [3,4,5]];cls='signal-propagation';description='Phased rising steam accents; remaining silhouette stays fixed.'
 elif name=='teacher':tracks=[track(i,'rotate',-2.5,12,21) for i in [2,3]];description='Teacher leans coherently; board stays fixed.'
 elif name=='walk':tracks=[track(0,'rotate',-4,5,18,profile='direction')];description='Shoe lifts around the heel; sole, laces and upper stay connected.'
 elif name=='brand-network-lined':tracks=[track(0,'scale',.04)];description='Connected graph response preserves all branches and nodes.'
 assert tracks,name
 for t in tracks:
  assert t[0]<=len(leaves)
  if t[1]=='erase-redraw':assert leaves[t[0]-1].get('stroke') not in [None,'none'],name
 scene={'id':id,'label':'Ref · '+name.replace('-lined','').replace('-',' ').title(),'trigger':trigger,'duration':duration,'tracks':tracks}
 geometry=E.tostring(geo);row={'id':id,'file':id+'.svg','sha256':hashlib.sha256(static).hexdigest(),'status':'User-provided reference; animation pending review','viewBox':root.get('viewBox'),'origin':str(Path('ref')/(name+'.svg')),'original_filename':name+'.svg','origin_sha256':hashlib.sha256(raw).hexdigest()}
 for folder in [P/'result',C,O]:
  (folder/'svg').mkdir(exist_ok=True);(folder/'svg'/row['file']).write_bytes(static)
 for folder in [C,O]:(folder/'geometry'/(id+'.svg')).write_bytes(geometry)
 catalog.append(row);curated.append({**row,'canonical':id});config['scenes'].append(scene);manifest.append({'id':id,'reference':'user ref/'+name+'.svg','method':'user-authorized-ref-extension-native-svg','static_sha256':row['sha256'],'status':'needs-visual-review','details':{'motion_class':cls,'description':description,'original_masks_and_clip_paths_preserved':True}});created.append({'id':id,'source':row['origin'],'motion_class':cls,'description':description,'parts':len(leaves)+1})
(P/'result/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n');(C/'catalog.json').write_text(json.dumps(curated,ensure_ascii=False,indent=2)+'\n');(O/'motion.json').write_text(json.dumps(config,separators=(',',':'))+'\n');(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
active={r['id'] for r in curated};(C/'motion.json').write_text(json.dumps({**{k:v for k,v in config.items() if k!='scenes'},'scenes':[s for s in config['scenes'] if s['id'] in active]},separators=(',',':'))+'\n')
report={'ref_files':len(inventory),'added':created,'skipped':sum(r['action']=='skip-semantic-duplicate' for r in inventory),'inventory':inventory,'full_series':len(config['scenes']),'active':len(active),'existing_scene_hashes':old_scene_hashes,'original_ref_unchanged':all(hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256'] for r in inventory)}
(R/'import.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Added',len(created),'Skipped',report['skipped'],'Active',len(active))
