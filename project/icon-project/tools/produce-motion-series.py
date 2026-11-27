"""Family motion authoring. Immutable static assets; review candidates, not automatic approvals."""
from pathlib import Path
import xml.etree.ElementTree as E
import json,re,copy,hashlib,collections
P=Path('icon-project');O=P/'motion/series';O.mkdir(exist_ok=True)
for d in ['svg','geometry']:(O/d).mkdir(exist_ok=True)
NS='{http://www.w3.org/2000/svg}';E.register_namespace('',NS[1:-1])
from importlib.machinery import SourceFileLoader
assembly_author=SourceFileLoader('motion_assemblies',str(P/'tools/motion-assemblies.py')).load_module().combine
structural_contacts=json.loads((P/'specification/motion-structural-contacts.json').read_text())['items']
arrow_parts=SourceFileLoader('motion_arrow_parts',str(P/'tools/motion-arrow-parts.py')).load_module().combine
arrow_author=SourceFileLoader('motion_arrows',str(P/'tools/motion-arrows.py')).load_module().author
family_author=SourceFileLoader('motion_families',str(P/'tools/motion-families.py')).load_module().author
catalog=json.loads((P/'result/catalog.json').read_text());pilot=json.loads((P/'motion/pilot/motion.json').read_text());pilot_by={s['id']:s for s in pilot['scenes']}
scenes=[];records=[]
override_path=O/'trigger-overrides.json'
trigger_overrides=json.loads(override_path.read_text()) if override_path.exists() else {}
def suggested_trigger(id):
 base=id.split('-')[0]
 if base in ['trash','delete','download','upload','save','copy','log','edit','pencil','pen','send','share','print','printer','play','pause','stop','recording','skip','fast','refresh','repeat','shuffle','undo','redo','check','x','maximize','minimize','expand','crop','scissors','eraser','bookmark','power']:
  return 'click-replay'
 if base in ['arrow','arrows','chevron','corner','search','zoom','settings','sliders','filter','menu','dots','plus','minus','toggle','switch','navigation','link','cursor','help','info','eye']:
  return 'hover-click'
 return 'hover'
def tag(n):return n.tag.split('}')[-1]
def shapes(root):
 out=[]
 def visit(n,style,hidden=False):
  style={**style,**{k:v for k,v in n.attrib.items() if k in ['fill','stroke','visibility']}}
  hidden=hidden or tag(n) in ['defs','clipPath'] or style.get('visibility')=='hidden'
  if not hidden and tag(n) in ['path','circle','ellipse','rect','line','polyline','polygon']:out.append((n,style))
  for c in n:visit(c,style,hidden)
 visit(root,{'fill':'black','stroke':'none'});return out

def split(root):
 for parent in list(root.iter()):
  if tag(parent) in ['defs','clipPath']:continue
  for node in list(parent):
   if tag(node)!='path' or node.get('id') or 'm' in node.get('d',''):continue
   paths=re.findall(r'M[^M]*',node.get('d',''))
   if len(paths)>1:
    at=list(parent).index(node);parent.remove(node)
    for i,d in enumerate(paths):
     n=copy.deepcopy(node);n.set('d',d);parent.insert(at+i,n)

def parent_of(root,node):return next(p for p in root.iter() if node in list(p))
def group(root,nodes):
 parent=parent_of(root,nodes[0])
 if not all(parent_of(root,n) is parent for n in nodes):return None
 g=E.Element(NS+'g');at=list(parent).index(nodes[0]);parent.insert(at,g)
 for n in nodes:parent.remove(n);g.append(n)
 return g

def produce(item):
 id=item['id'];raw=(P/'result/svg'/item['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==item['sha256']
 (O/'svg'/f'{id}.svg').write_bytes(raw)
 if id in pilot_by:
  derived=(P/'motion/pilot/geometry'/f'{id}.svg').read_bytes();s=copy.deepcopy(pilot_by[id]);pattern='approved-pilot';idea='Exact user-approved pilot choreography'
 else:
  r=E.fromstring(raw);split(r);visible=shapes(r);filled={n:st.get('fill') not in ['none','transparent'] for n,st in visible};nodes=[n for n,st in visible];stroke=[n for n,st in visible if st.get('stroke') not in ['none','transparent']];base=id.split('-')[0];motions=[];pattern='detail-path';idea='Stable anchor; erase and redraw detail contours in sequence'
  nodes,assemblies,structural_replaced=assembly_author(r,nodes,structural_contacts.get(id,[]),parent_of,group)
  stroke=list(dict.fromkeys(structural_replaced.get(n,n) for n in stroke))
  nodes,rigid_arrows,replaced=arrow_parts(r,nodes,parent_of,group)
  stroke=list(dict.fromkeys(replaced.get(n,n) for n in stroke))
  def add(n,k,a,x=0,y=0,start=0,end=1):motions.append([n,k,a,x,y,start,end])
  def allgroup():return group(r,nodes)
  def allworld():return group(r,[n for n in list(r) if tag(n) not in ['defs','clipPath']])
  family=None
  if id in ['certificate-01-lined','server-04-lined','target-02-lined','target-03-lined']:
   whole=allworld()
   if whole is not None:
    if id=='server-04-lined':add(whole,'scale-y',-.035,12,21);family=('server-assembly','Server levels move as one chassis, preserving shared cylindrical edges')
    else:add(whole,'rotate',1.5 if id.startswith('certificate') else 5,12,12);family=('connected-symbol-turn','Certificate or reticle moves as one connected symbol')
  if not motions:family=arrow_author(id,r,nodes,parent_of,add)
  if not motions:family=family_author(id,r,nodes,tag,group,add)
  if family and motions:pattern,idea=family
  # Short directional replay, fixed endpoints and a complete return to the same pose.
  if motions:pass
  elif base in ['arrow','arrows','chevron','corner','trend','log','download','upload','send','navigation'] and not any(w in id for w in ['circle','square','block']):
   g=allworld()
   if g is not None:
    direction='y' if any(w in id for w in ['down','up','download','upload']) else 'x'
    amount=(-.55 if any(w in id for w in ['up','upload']) else .55) if direction=='y' else (-.55 if 'left' in id or id.startswith('log-in-') else .55)
    add(g,direction,amount)
    if direction=='y' and any(w in id for w in ['left','right']):
     inner=E.Element(NS+'g')
     for child in list(g):g.remove(child);inner.append(child)
     g.append(inner);add(inner,'x',-.55 if 'left' in id else .55)
    pattern='directional-return';idea='Small directional travel and return; no state change'
  elif id=='compass-lined':
   add(nodes[-2],'rotate',-4,10.7448,8.66169);add(nodes[-1],'rotate',4,13.2552,8.66169);pattern='drafting-compass-hinge';idea='Legs close slightly around their hinges; crown stays fixed'
  elif base in ['settings','refresh','repeat','compass','hurricane','fan']:
   target=nodes[0] if base=='settings' else nodes[-1] if base=='compass' else allgroup()
   if target is not None:add(target,'rotate',-12 if 'ccw' in id else 12,12,12);pattern='rotation-return';idea='Mechanism turns and returns to its original angle'
  elif base in ['clock','watch'] and len(nodes)>1:
   add(nodes[2] if base=='watch' else nodes[1],'rotate',22,12,12);pattern='hand-sweep';idea='Hands move inside a stable dial and return'
  elif base=='trash' and len(nodes)>2:
   g=group(r,nodes[:2])
   if g is not None:add(g,'rotate',-9,5,6);pattern='lid-hinge';idea='Handle and lid move together around their hinge'
  elif base=='bell':
   g=allgroup()
   if g is not None:add(g,'rotate',7,12,6);pattern='bell-swing';idea='Bell swings around its upper attachment'
  elif base=='eye' and 'off' not in id:
   g=allgroup()
   if g is not None:add(g,'blink',.5,0,12);pattern='eye-blink';idea='Visible eye closes partly and reopens without fading'
  elif base=='face':
   eyes=[n for n in nodes if tag(n)=='circle' and float(n.get('r','10'))<1]
   for n in eyes:add(n,'blink',.65,0,float(n.get('cy','12')))
   if eyes:pattern='face-blink';idea='Eyes blink inside a stable facial outline'
  elif base=='cloud' and 'raining' in id and len(nodes)>1:
   for i,n in enumerate(nodes[1:]):add(n,'y',.5,0,0,min(i*.05,.3),1)
   pattern='rainfall-return';idea='Rain drops travel downward and return, cloud stays still'
  if not motions and assemblies:
   g=allgroup()
   if g is not None:add(g,'rotate',2,12,12);pattern='assembled-object-pivot';idea='Connected structural contours pivot together without opening seams'
  if not motions:
   # Never trim filled-only marks. Keep their fill role and use a small geometric pulse.
   if not stroke:
    g=allgroup()
    if g is not None:add(g,'blink',.16,0,12);pattern='filled-geometric-pulse';idea='Filled mark compresses slightly and returns, no opacity animation'
   else:
    candidates=stroke[1:] if len(stroke)>1 else stroke
    # Modifiers come last in the family compositions. Keep structural frames untouched.
    if base in ['file','folder','shield','calendar','clipboard','user','users','message','annotation','credit','package','bookmark','alarm','lock','phone','image','monitor'] and len(candidates)>3:candidates=candidates[-3:]
    candidates=candidates[:10];count=len(candidates)
    for i,n in enumerate(candidates):
     start=0 if count==1 else .42*i/(count-1)
     if n in assemblies:add(n,'rotate',2,12,12)
     elif n in rigid_arrows:add(n,'x',.5)
     elif filled.get(n):add(n,'blink',.22,0,float(n.get('cy','12')),0,1)
     else:add(n,'erase-redraw',1,0,0,start,min(1,start+.58))
  # A family may animate neighboring details independently, but never split an arrow.
  coherent=[]
  for n,k,a,x,y,start,end in motions:
   if n not in rigid_arrows:coherent.append([n,k,a,x,y,start,end]);continue
   directions=rigid_arrows[n];dx,dy=directions[0]
   if any(dx*other[0]+dy*other[1]<-.9 for other in directions):
    coherent.append([n,'scale-x' if abs(dx)>abs(dy) else 'scale-y',-.08,12,12,start,end])
   elif abs(dx)<.001:coherent.append([n,'y',dy*.55,0,0,start,end])
   elif abs(dy)<.001:coherent.append([n,'x',dx*.55,0,0,start,end])
   else:
    inner=E.Element(NS+'g')
    for child in list(n):n.remove(child);inner.append(child)
    n.append(inner);coherent.extend([[n,'x',dx*.55,0,0,start,end],[inner,'y',dy*.55,0,0,start,end]])
  motions=coherent
  if not motions:raise ValueError(id+': no motion parts')
  # Put pre-existing transforms outside animated nodes. Never overwrite their pose.
  for n,k,*_ in motions:
   if n.get('transform'):
    parent=parent_of(r,n);at=list(parent).index(n);wrapper=E.Element(NS+'g',{'transform':n.attrib.pop('transform')});parent.remove(n);parent.insert(at,wrapper);wrapper.append(n)
  order={n:i for i,n in enumerate(r.iter())};motions.sort(key=lambda m:order[m[0]])
  tracks=[]
  for i,(n,*values) in enumerate(motions):n.set('data-part',str(i));tracks.append([i,*values])
  active=E.Element(NS+'g',{'id':'motion-active','visibility':'hidden'})
  for n in list(r):r.remove(n);active.append(n)
  idle=E.Element(NS+'g',{'id':'motion-idle'})
  for n in E.fromstring(raw):idle.append(copy.deepcopy(n))
  # Clip/gradient IDs are isolated between idle and active, then per scene by the builder.
  for g,prefix in [(idle,'idle--'),(active,'active--')]:
   ids={n.get('id'):prefix+n.get('id') for n in g.iter() if n.get('id')}
   for n in g.iter():
    for k,v in list(n.attrib.items()):
     if k=='id':n.set(k,ids[v])
     else:
      for old,new in ids.items():v=v.replace('url(#'+old+')','url(#'+new+')')
      n.set(k,v)
  r.append(idle);r.append(active);derived=E.tostring(r,encoding='utf-8')
  duration=1100 if pattern not in ['detail-path'] else min(2000,1200+max(0,len(motions)-1)*70)
  s=dict(id=id,label=id.removesuffix('-lined').replace('-',' ').title(),trigger='hover',duration=duration,tracks=tracks)
 s['trigger']=trigger_overrides.get(id,suggested_trigger(id))
 (O/'geometry'/f'{id}.svg').write_bytes(derived);scenes.append(s)
 records.append(dict(id=id,filename=item['file'],family=id.split('-')[0],pattern=pattern,rationale=idea,static_sha256=item['sha256'],geometry_sha256=hashlib.sha256(derived).hexdigest(),scene_sha256=hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest(),static_review_status=item['status'],trigger=s['trigger'],suggested_trigger=suggested_trigger(id),trigger_source='user' if id in trigger_overrides else 'inferred',rigid_arrow_parts=0 if id in pilot_by else len(rigid_arrows),structural_assemblies=0 if id in pilot_by else len(assemblies),motion_review_status='pending-agent-check',user_motion_approval='pilot-only' if id in pilot_by else 'pending'))
for item in catalog:produce(item)
config={**pilot,'scenes':scenes};(O/'motion.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n');(O/'catalog.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
receipt={'user_message':'Ок, давай все иконки','scope':'Approve concrete four-scene motion pilot v3 and authorize animation production for all 1189 current catalog SVGs. Existing static review statuses remain unchanged.','pilot_config_sha256':hashlib.sha256((P/'motion/pilot/motion.json').read_bytes()).hexdigest(),'player_sha256':hashlib.sha256((P/'motion/assets/motion/player.js').read_bytes()).hexdigest(),'source_catalog_sha256':hashlib.sha256((P/'result/catalog.json').read_bytes()).hexdigest(),'scenes':pilot['scenes']}
receipt_path=P/'review/reports/motion-pilot-user-approval.json'
if not receipt_path.exists():receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'scenes':len(scenes),'patterns':dict(collections.Counter(r['pattern'] for r in records))},indent=2))
