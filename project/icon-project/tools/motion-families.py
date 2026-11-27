"""Geometry choreography per metaphor; all actions return to their complete initial pose."""
def author(id,r,nodes,tag,group,add):
 b=id.split('-')[0]
 def joined(ns):return group(r,ns) if len(ns)>1 else ns[0] if ns else None
 def move(ns,k,a,x=12,y=12,start=0,end=1):
  n=joined(ns)
  if n is not None:add(n,k,a,x,y,start,end);return True
  return False
 def detail():return nodes[1:] if len(nodes)>1 else nodes
 def result(name,why):return name,why
 if b in ['book'] and 'open' in id and len(nodes)>1:
  add(nodes[0],'scale-x',-.075,12,12);return result('book-page-fold','Pages fold slightly around the stable spine and reopen')
 if b=='book' and len(nodes)>1:
  add(nodes[-1],'x',.6);return result('book-page-edge','Page edge shifts inside the stable binding')
 if b in ['sliders'] or (b=='settings' and any(x in id for x in ['03','04'])):
  for i,n in enumerate(nodes):
   add(n,'x',-.65 if i<len(nodes)/2 else .65,0,0,0 if i<len(nodes)/2 else .15,1)
  return result('slider-travel','Two slider assemblies travel in opposite directions and return')
 if b in ['bar','horizontal'] and 'chart' in id:
  for i,n in enumerate(detail() if len(nodes)>4 else nodes):add(n,'scale-y' if b=='bar' else 'scale-x',-.2,3,20.2,min(i*.04,.3),1)
  return result('chart-bar-wave','Bars contract around their common baseline in a staggered sequence')
 if b in ['pie']:
  move(detail(),'rotate',7);return result('pie-sector-turn','Chart sector pivots around the chart center and returns')
 if b=='flag' and len(nodes)>1:
  move(nodes[1:],'scale-x',-.13,8,3);return result('flag-fold','Fabric folds toward the fixed flagpole')
 if b=='lock' and len(nodes)>1:
  add(nodes[1],'y',-.5);return result('keyhole-feedback' if tag(nodes[0])=='g' else 'shackle-lift','Shackle makes a short lift and returns; no persistent state change')
 if b=='mail' and len(nodes)>1:
  move(nodes[1:],'scale-y',-.18,12,6.5);return result('envelope-flap','Flap folds toward its top hinge and returns')
 if b=='rocket':
  move(nodes,'y',-.65);return result('rocket-lift','Rocket travels upward in its own local coordinate system and returns')
 if b in ['heart','hearts']:
  move(detail() if any(w in id for w in ['circle','square','hexagon','octagon']) else nodes,'scale',-.09);return result('heart-beat','Heart contracts and returns; enclosing frame stays stable')
 if b in ['sun','sunrise','sunset','snowflake','asterisk','virus']:
  if b=='sun' and id=='sun-lined':move(nodes[:-1],'rotate',9)
  elif b in ['sunrise','sunset'] or 'setting' in id:move(nodes[:max(1,len(nodes)-2)],'y',.55 if 'set' in id else -.55)
  else:move(nodes,'rotate',6)
  return result('rays-turn','Rays or snowflake arms rotate as geometry; horizon remains an anchor where present')
 if b in ['star','stars','award','certificate','trophy']:
  move(detail() if b in ['award','certificate'] else nodes,'rotate',3)
  return result('award-rock','Star, award medallion or trophy rocks gently and returns')
 if b in ['volume','wifi','rss','signal','modem','podcast']:
  ns=nodes[:2] if b=='volume' else detail()
  for i,n in enumerate(ns):add(n,'scale',-.07,12,16,min(i*.08,.3),1)
  return result('signal-expansion','Signal arcs contract and expand with a phase delay; no opacity change')
 if b in ['search','zoom']:
  move(nodes,'rotate',-4,10.5,10.5);return result('search-scan','Magnifier turns around the lens center and returns')
 if b in ['user','users']:
  heads=[n for n in nodes if tag(n)=='circle']
  if heads:
   for i,n in enumerate(heads):add(n,'y',-.45,0,0,min(i*.13,.3),1)
   return result('person-nod','Heads lift in sequence while torso and status glyph remain stationary')
 if b in ['image','camera','webcam']:
  ns=[n for n in nodes if tag(n)=='circle']
  if ns:
   for n in ns:add(n,'scale',-.12,float(n.get('cx','12')),float(n.get('cy','12')))
   return result('lens-focus','Lens or light source contracts and returns inside a stable frame')
 if b in ['building','bank','home'] and len(nodes)>1:
  move(nodes[1:],'y',-.35);return result('interior-lift','Door, windows or columns lift slightly inside the fixed exterior')
 if b in ['file','clipboard','message','annotation','notification','terminal','text']:
  # Draw only the actual writing/confirmation strokes, not the entire object.
  if any(x in id for x in ['check','tick','code','question','x-']):return None
  if len(nodes)>1:
   move(nodes[1:],'y',-.5);return result('content-slide','Inner content slides inside its stationary document or message frame')
 if b in ['folder','archive','inbox','box','gift','package','shopping','briefcase','backpack','luggage','wallet']:
  if len(nodes)>1:
   if b in ['folder','archive','inbox','box']:move(nodes[1:],'scale-y',-.08,12,20)
   else:move(nodes[1:],'y',-.45)
   return result('container-detail','Lid, handle or interior detail moves while the main container remains stable')
 if b in ['monitor','laptop','tablet','phone','tv','printer','hard','server','simcard']:
  if len(nodes)>1:
   move(nodes[1:],'y',-.4);return result('device-detail','Screen content, tray or secondary device part shifts with a stable outer frame')
 if b=='spacing':
  groups=[n for n in nodes if tag(n)=='g']
  if groups:
   for n in groups:add(n,'scale-x' if 'width' in id else 'scale-y',-.1,12,12)
   return result('spacing-span','Arrowhead and stem change span together, guide rails remain fixed')
 if b in ['layout','grid','columns','rows','align','flex','distribute','spacing','menu','list','dotpoints','paragraph','reorder','table']:
  for i,n in enumerate(detail()[:12]):add(n,'x' if b not in ['columns','rows'] else 'y',.5 if i%2==0 else -.5,0,0,min(i*.035,.3),1)
  return result('layout-reflow','Independent layout elements move in a staggered alignment sequence')
 if b in ['music','headphones','speaker','microphone','recording','voicemail','radio']:
  move(detail(),'scale-y',-.12,12,16);return result('audio-vibration','Acoustic element or note compresses geometrically and returns')
 if b=='currency':
  move(nodes,'rotate',5);return result('currency-symbol-turn','All strokes of the currency symbol turn together; circular enclosure retains its shape')
 if b in ['atom','globe','glasses','orbit','disc','coins','currency','cryptocurrency','target','speedometer','power']:
  ns=detail()
  move(ns,'rotate',5);return result('inner-orbit','Inner ring, needle, lens or symbol turns within a stationary anchor')
 if b in ['scissors','tool','pen','pencil','edit','brush','paint','roller','dropper','ruler','eraser']:
  move(detail() if b in ['scissors','pen'] else nodes,'rotate',-3);return result('tool-pivot','Tool or cutting element pivots slightly and returns')
 if b in ['plane','car','truck','bus','train','tram','send']:
  move(nodes,'x',.5);return result('vehicle-travel','Vehicle travels a short distance and returns without changing shape')
 if b in ['map','route','marker','pin','navigation']:
  move(detail() if b in ['map','route'] else nodes,'y',-.5);return result('map-marker-lift','Marker or route endpoint lifts and returns')
 if b in ['key','anchor','hand','thumbs','feather','umbrella','scale','scales','telescope','microscope']:
  move(nodes,'rotate',-2.5);return result('object-pivot','Object pivots around its balance point and returns')
 if b in ['drop','droplets','cloud','moon','wind','waves','thermometer','lightbulb','battery']:
  ns=detail()
  for i,n in enumerate(ns[:10]):add(n,'y',.22 if id=='moon-star-lined' else -.4,0,0,min(i*.06,.3),1)
  return result('environment-flow','Weather, charge or light elements travel in a phased wave')
 return None
