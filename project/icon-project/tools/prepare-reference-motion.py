from pathlib import Path
import json,copy,xml.etree.ElementTree as E,hashlib
E.register_namespace('','http://www.w3.org/2000/svg')
P=Path('icon-project');O=P/'motion/reference-pilot';O.mkdir(exist_ok=True)
for name in ['svg','geometry']:(O/name).mkdir(exist_ok=True)
config=json.loads((P/'motion/series/motion.json').read_text());by={s['id']:s for s in config['scenes']};scenes=[];notes=[]
choices=[('arrow-right-lined','direction',1250,'Arrow nudge: a short preparation, clear travel, pause and return','https://useanimations.com/icons/arrow-right'),('book-open-01-lined','original-book',1100,'Light compression of the original book spread about its fixed spine; user requested no added or turning pages','https://useanimations.com/icons/book-open'),('settings-01-lined','mechanism',1300,'Gear takes up movement, turns and settles back','https://useanimations.com/icons/settings'),('trash-01-lined','hinge',1450,'Lid opens around its left hinge, pauses, then closes; bin remains still','https://useanimations.com/icons/trash'),('folder-lined','fold',1400,'Connected folder shell folds slightly toward its bottom edge and reopens','https://useanimations.com/icons/folder'),('heart-lined','heartbeat',1200,'Two contractions of different strength followed by a long rest','https://useanimations.com/icons/heart'),('wifi-lined','ripple',1500,'Geometric signal wave travels from the emitter toward the outer arc, with no fading','https://useanimations.com/icons/wifi'),('bar-chart-01-lined','chart',1450,'Bars move from their common baseline, left to right, then recover','https://useanimations.com/icons/bar-chart'),('flag-01-lined','flutter',1450,'Fabric makes two decaying folds around the fixed flagpole','https://useanimations.com/icons/flag')]
for id,profile,duration,idea,url in choices:
 s=copy.deepcopy(by[id]);s['duration']=duration;root=E.fromstring((P/'motion/series/geometry'/f'{id}.svg').read_bytes());active=next(n for n in root.iter() if n.get('id','').endswith('motion-active'))
 if profile=='original-book':
  s=copy.deepcopy(by[id])
 elif profile=='page':
  for n in root.iter():n.attrib.pop('data-part',None)
  page=E.SubElement(active,'{http://www.w3.org/2000/svg}path',{'d':'M12 6A5 5 0 0 1 16.5 3.5H22V16.5A2.5 2.5 0 0 1 19.5 19H16A4 4 0 0 0 13.5 19.9L12 21','stroke':'currentColor','fill':'none','stroke-linecap':'butt','stroke-linejoin':'miter','visibility':'hidden','data-part':'0'})
  s['tracks']=[[0,'page-turn',1,12,12,0,1]]
 elif profile=='ripple':
  for n in root.iter():n.attrib.pop('data-part',None)
  arcs=[n for n in active.iter() if n.tag.endswith('path')]
  assert len(arcs)==3
  s['tracks']=[]
  for i,n in enumerate(arcs):n.set('data-part',str(i));s['tracks'].append([i,'scale',-.12,12,19.25,(2-i)*.12,1,profile])
 else:
  for t in s['tracks']:
   if profile=='direction':t[2]=1.05
   elif profile=='mechanism':t[2]=16
   elif profile=='hinge':t[2]=-10.5
   elif profile=='fold':t[1:5]=['scale-y',-.08,12,20.5]
   elif profile=='flutter':t[2]=-.17
   elif profile=='chart':t[2]=-.35
   t.append(profile)
  if profile=='chart':
   parts=[n for n in root.iter() if n.get('data-part') is not None]
   # Bars were drawn right-to-left; phase the three bars left-to-right instead.
   for i,t in enumerate(s['tracks']):t[5]=(2-i)*.12;t[6]=1
 (O/'svg'/f'{id}.svg').write_bytes((P/'motion/series/svg'/f'{id}.svg').read_bytes());raw=E.tostring(root,encoding='utf-8');(O/'geometry'/f'{id}.svg').write_bytes(raw);scenes.append(s);notes.append({'id':id,'idea':idea,'reference':url,'geometry_sha256':hashlib.sha256(raw).hexdigest(),'motion_approval':'pending-new-direction'})
(O/'motion.json').write_text(json.dumps({**config,'scenes':scenes},ensure_ascii=False,indent=2)+'\n');(O/'direction.json').write_text(json.dumps({'status':'pilot-for-user-review','principles':'Original choreography informed by observed gesture phases; existing transformed static artwork retained; start/end full; no fade; per-icon trigger policy retained','references_observed':['trash','book-open','settings','arrow-right','folder','wifi','bar-chart','menu-v2','globe'],'scenes':notes},ensure_ascii=False,indent=2)+'\n');print('Prepared',len(scenes),'original motion proposals')
