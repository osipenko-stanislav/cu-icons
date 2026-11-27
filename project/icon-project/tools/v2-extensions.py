from pathlib import Path
import copy,math,re,xml.etree.ElementTree as E

def install(v):
 global g,p,c,svg,ref,resize,children,glyph,frame
 g,p,c,svg,ref,resize,children,glyph,frame=(getattr(v,k) for k in ['g','p','c','svg','ref','resize','children','glyph','frame'])

def rotate(r,angle):
 if not angle:return r
 group=g.el('g',transform=f'rotate({angle} 12 12)');group.extend(children(r));return svg(group)
def mirror(r):
 group=g.el('g',transform='matrix(-1 0 0 1 24 0)');group.extend(children(r));return svg(group)
def direct(base,old):
 f=base.split('-')[0];tokens=base.split('-')
 if f=='arrow':
  dirs=[t for t in tokens if t in ['up','down','left','right']];direction='-'.join(dirs)
  if len(dirs)==2:
   r=ref('arrow-link');angle={'up-right':0,'down-right':90,'down-left':180,'up-left':270}[direction]
  else:
   r=ref('arrow-left');angle={'right':0,'down':90,'left':180,'up':270}[direction]
  if 'circle' in base or 'square' in base:
   rr=resize(r,.56)
   outline=p('M20.66 7A10 10 0 1 0 20.66 17') if 'broken' in base else c(12,12,10) if 'circle' in base else frame(curve='TLBR')
   r=svg(outline,*children(rr))
  elif 'block' in base:
   r=svg(p('M2 8H13V3L22 12 13 21V16H2Z'));angle={'right':0,'down':90,'left':180,'up':270}[direction]
  elif 'narrow' in base and len(dirs)==1:r=svg(p('M2 12H22M16 6 22 12 16 18'))
  return rotate(r,angle),'arrow-left / arrow-link'
 if f=='chevron':
  dirs=[t for t in tokens if t in ['up','down','left','right']]
  if 'selector' in base:
   r=svg(p('M6 9 12 3 18 9M6 15 12 21 18 15'))
   return rotate(r,90 if 'horizontal' in base else 0),'chervon-up / chervon-down'
  r=ref('chervon-down');angle={'down':0,'left':90,'up':180,'right':270}[dirs[0]]
  if 'double' in base:r=svg(p('M6 6 12 12 18 6M6 12 12 18 18 12'))
  return rotate(r,angle),'chervon-down'
 if f=='corner':
  paths={
   'up-right':'M3 21V13A4 4 0 0 1 7 9H21M15 3 21 9 15 15',
   'up-left':'M21 21V13A4 4 0 0 0 17 9H3M9 3 3 9 9 15',
   'down-right':'M3 3V11A4 4 0 0 0 7 15H21M15 9 21 15 15 21',
   'down-left':'M21 3V11A4 4 0 0 1 17 15H3M9 9 3 15 9 21',
   'right-up':'M3 21H11A4 4 0 0 0 15 17V3M9 9 15 3 21 9',
   'right-down':'M3 3H11A4 4 0 0 1 15 7V21M9 15 15 21 21 15',
   'left-up':'M21 21H13A4 4 0 0 1 9 17V3M3 9 9 3 15 9',
   'left-down':'M21 3H13A4 4 0 0 0 9 7V21M3 15 9 21 15 15'}
  return svg(p(paths[base.removeprefix('corner-')])),'brand-network-lined / arrow-left'
 if f in ['refresh','repeat','reverse','flip','switch','arrows']:
  if f in ['reverse','flip']:
   r=svg(p('M3 8H14A6 6 0 0 1 14 20H7M9 2 3 8 9 14'))
   return mirror(r) if base.endswith(('right','forward')) else r,'brand-network-lined / arrow-left'
  if f=='arrows' and 'triangle' in base:
   r=ref('arrow-link');return None,None
  if f=='arrows':
   r=svg(p('M2 7H21M16 2 21 7 16 12M2 17H21M16 12 21 17 16 22'))
   r=rotate(r,{'right':0,'down':90,'left':180,'up':270}[next(t for t in tokens if t in ['up','down','left','right'])])
   return r,'arrow-left / arrow-right (parallel directions preserved)'
  if f in ['switch','repeat']:
   r=svg(p('M2 7H22M16 1 22 7 16 13M22 17H2M8 11 2 17 8 23'))
   if 'vertical' in base or 'up' in tokens or 'down' in tokens:r=rotate(r,90)
   if base.endswith('02') or 'left' in tokens:r=mirror(r)
   return r,'arrow-left / arrow-right'
  num=int(base[-2:]) if base[-2:].isdigit() else 1
  if num==1:r=svg(p('M20 8A9 9 0 1 0 20 16M20 3V8H15'))
  else:r=svg(p('M3 10A9 9 0 0 1 18 5L21 8M21 14A9 9 0 0 1 6 19L3 16M16 8H21V3M8 16H3V21'))
  if num in [3,4]:r=rotate(r,90)
  if 'ccw' in base:r=mirror(r)
  return r,'loading / arrow-left'
 if base.startswith('marker-pin'):
  if base.endswith(('01','02','03')):return ref('marker-pin-01'),'marker-pin-01'
  if base.endswith('04'):return ref('marker-pin-04'),'marker-pin-04'
  if base.endswith('06'):return ref('pin'),'pin'
  r=svg(p('M12 2V16M12 2 20 5.5 12 9M8 13C4 13.75 2 15.2 2 17C2 19.5 6.5 21.5 12 21.5S22 19.5 22 17C22 15.2 20 13.75 16 13'))
  return r,'flag / pin'
 if f=='lock':
  if 'keyhole' in base:
   r=svg(c(12,12,10) if 'circle' in base else frame(),p('M10 13A3 3 0 1 1 14 13L15 18H9Z'));return r,'brand-question-lined / brand-doc-lined'
  if base.endswith(('03','04')):
   r=svg(c(12,15,6),p('M12 14V17'))
  else:r=svg(frame(5,10,14,11,'BL',3),p('M12 14.5V17'))
  r.append(p('M8.5 10V6A3.5 3.5 0 0 1 15.5 6V8' if 'unlocked' in base else 'M8.5 10V6A3.5 3.5 0 0 1 15.5 6V10'))
  return r,'brand-doc-lined / brand-briefcase-lined'
 if f=='clipboard':
  r=svg(frame(5,4.5,14,17,'BL',3),p('M8.5 2.5H15.5V6H8.5Z'))
  kind=next((t for t in tokens if t in ['check','plus','minus','x','download','attachment']),None)
  if kind:r.extend(glyph(kind,12,14,.9))
  elif base=='clipboard':r.append(p('M8 12H16M8 16H13'))
  return r,'doc / brand-doc-lined'
 if f=='credit':
  # Card shell is derived from the approved lock card, with a reference-selected opposite corner.
  kind=next((t for t in tokens if t in ['check','plus','minus','x','download','upload','shield','refresh','search','edit','down','up']),None)
  if kind:
   r=svg(p('M21.5 11V5H5.5A3 3 0 0 0 2.5 8V18.5H11M2.5 9.5H21.5'),*glyph(kind,18.5,17.5,.95))
  else:r=svg(frame(2.5,5,19,13.5,'TLBR',3),p('M2.5 9.5H21.5'))
  if base=='credit-card-02':r.append(p('M6 14.5H10'))
  return r,'pilot/credit-card-lock / brand-briefcase-lined'
 if f=='wallet':
  if base.endswith('05'):return None,None
  r=svg(frame(3.5,6,17,14,'TLBR',3),p('M3.5 10.5H20.5'))
  if base.endswith('02'):r.append(p('M6 6 16 2.5 18 6'))
  if base.endswith(('03','04')):r.append(p('M20.5 12.5H17A2 2 0 0 0 17 16.5H20.5'))
  return r,'brand-briefcase-lined'
 if f=='shopping':
  if 'cart' in base:
   return svg(p('M2.5 3.5H5L7 16.5H19.5L22 6.5H5.5'),c(8.5,21,.65),c(18.5,21,.65)),'trash / brand-briefcase-lined'
  r=svg(frame(4,7,16,14,'TLBR',3),p('M8.5 7V5A3.5 3.5 0 0 1 15.5 5V7'))
  if base.endswith('03'):r.append(p('M8.5 11A3.5 3.5 0 0 0 15.5 11'))
  return r,'brand-briefcase-lined'
 if f=='lightbulb':
  r=svg(p('M9.5 18H14.5C14.5 15 17 13 17 10.75A5 5 0 0 0 7 10.75C7 13 9.5 15 9.5 18ZM10 20H14M11 22H13'))
  if base.endswith(('02','05')):r.append(p('M12 2V4M2.5 11.5H4.5M19.5 11.5H21.5M5 5 6.5 6.5M17.5 6.5 19 5'))
  if base.endswith(('04','05')):r.append(p('M10.5 10.5H13.5M12 10.5V16'))
  return r,'coworking (live-stroke reconstruction)'
 if f=='cloud' or ('cloud' in base and f in ['upload','download']):
  # The lobe rhythm is drawn from the steam reference; the closed cloud base retains weather meaning.
  r=svg(p('M5.5 15.5H18.5A3.5 3.5 0 0 0 18.5 8.5H17A5.5 5.5 0 0 0 6 8.5H5.5A3.5 3.5 0 0 0 5.5 15.5Z'))
  if 'raining' in base:
   r.append(p('M8 18V22M12 17V21M16 18V22' if base.endswith('02') else 'M8 18V19M12 20V21M16 18V19' if base.endswith('04') else 'M9 18 7 21M13 18 11 21M17 18 15 21' if base.endswith(('03','05')) else 'M8 18V19M8 21V22M12 17V18M12 20V21M16 18V19M16 21V22'))
   if base.endswith('06'):r=svg(*children(r)[:1],p('M5 18.5H19M7 21.5H17'))
  if 'snowing' in base:
   for x,y in [(8,18),(12,21),(16,18)]:r.append(c(x,y,.25))
  if 'lightning' in base:r.extend(glyph('zap',12,19,.65))
  if 'off' in base:r.append(p('M3 3 21 21'))
  if 'sun' in base:
   # Rays remain visible outside the cloud and use the exact reference sun spacing.
   sun=svg(p('M2.5 6A2.5 2.5 0 0 1 6.5 4M5 1.5V2.5M1.5 5.5H2M2 2.5 2.7 3.2M8.5 2 7.8 2.7'));r=svg(*children(sun),*children(r))
  if 'moon' in base:
   moon=svg(p('M3 7A4 4 0 0 1 8 2A4 4 0 0 0 6.5 6'));r=svg(*children(moon),*children(r))
  if f in ['upload','download']:r.extend(glyph('up' if f=='upload' else 'down',12,12,.7))
  return r,'steam / sun-lined / moon-02-lined'
 if f=='star':
  if base.endswith(('04','05','06')):
   r=ref('brand-shine-lined')
   if not base.endswith('06'):
    for n in r:
     if n.get('d'):n.set('d',g.subpaths(n.get('d'))[0])
    r=resize(r,1.18,.1,-3)
   return r,'brand-shine-lined'
  n=5 if base.endswith('01') else 6 if base.endswith('02') else 8;pts=[]
  for j in range(n*2):
   a=-math.pi/2+j*math.pi/n;rad=10 if j%2==0 else 4.5 if n==5 else 6
   pts.append((12+rad*math.cos(a),12+rad*math.sin(a)))
  return svg(p('M'+'L'.join(f'{x:.4f} {y:.4f}' for x,y in pts)+'Z')),'brand-shine-lined / brand-award1-lined (point and gap grammar)'
 if f=='stars':return ref('brand-shine-lined'),'brand-shine-lined'
 return None,None

# Recognize rectilinear container subpaths and replace the complete contour, including existing A arcs.
def reconstruct_rectangles(root):
 changed=0
 for n in root.iter():
  if not n.get('d'):continue
  result=[]
  for d in g.subpaths(n.get('d')):
   seg=g.segments(d)
   if not d.rstrip().endswith('Z'):result.append(d);continue
   axis=0;bad=False;points=[]
   for k,a,start,end in seg:
    points.extend([end] if k=='M' else [start,end])
    if k in ['L','H','V']:
     if abs(start[0]-end[0])>.001 and abs(start[1]-end[1])>.001:bad=True
     elif math.dist(start,end)>.25:axis+=1
    if k=='C':points.extend([(a[j],a[j+1]) for j in range(0,6,2)])
    if k not in ['M','L','H','V','A','C','Z']:bad=True
   xs=[x for x,y in points];ys=[y for x,y in points];x,y,w,h=min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)
   if not bad and axis>=3 and min(w,h)>=4 and w*h>=35 and max(w,h)<=22:
    result.append(frame(x,y,w,h,'TLBR',min(3,w/4,h/4)).get('d'));changed+=1
   else:result.append(d)
  n.set('d',''.join(result))
 return changed

original_direct=direct

def direct(base,old):
 f=base.split('-')[0];tokens=base.split('-');mod=next((t for t in tokens if t in ['check','plus','minus','x','up','down','left','right','edit']),None)
 if f=='image':
  if 'indent' in base:
   r=svg(frame(2,7,7,7,'TLBR',1.5),p('M12 7H22M12 11H22M12 15H19M2 19H22'))
   return mirror(r) if 'right' in tokens else r,'brand-device-desktop-lined / menu'
  if mod:r=svg(p('M14.5 3.5H5.5A3 3 0 0 0 2.5 6.5V20.5H18.5A3 3 0 0 0 21.5 17.5V10.5'),*glyph(mod,19.5,5.5,.7))
  elif base.endswith('02'):r=svg(c(12,12,9.5))
  elif base.endswith('05'):r=svg()
  else:r=svg(frame(2.5,3.5,19,17,'TLBR',3))
  if 'user' in base:
   profile=svg(p('M4.5 19A6 6 0 0 1 10.5 13H13.5A6 6 0 0 1 19.5 19V20.5H4.5Z'),c(12,7.5,3.5));profile=resize(profile,.7,3.6,3.6);r.extend(children(profile))
  else:
   r.append(c(8,8.5,1.5));r.append(p('M4 16 10 10 19 18' if base.endswith('02') else 'M3 19 9.5 12 18 20.5M14 16 17 12.5 21.5 17'))
  return r,'brand-device-desktop-lined / profile / brand-chart-lined'
 if f=='copy':return ref('copy'),'copy'
 if f in ['check','x','plus','minus','info','alert','help']:
  if f=='help':inner=svg(*glyph('question',12,12,1.05))
  elif f=='info':inner=svg(p('M12 10V16'),c(12,7.5,.25))
  elif f=='alert':inner=svg(p('M12 7.5V13.5'),c(12,16,.25))
  elif f=='check':inner=ref('check')
  elif f=='x':inner=ref('x-close')
  elif f=='minus':inner=ref('minus')
  else:inner=svg(p('M12 4V20M4 12H20'))
  r=inner
  if 'verified' in base:
   outline=ref('brand-award1-lined')
   for n in outline.iter():
    if n.get('d'):n.set('d',g.subpaths(n.get('d'))[0])
   r=svg(*children(outline),*children(resize(inner,.55)))
  elif 'circle' in base:r=svg(c(12,12,11 if f in ['plus','minus'] else 9.5),*children(resize(inner,1 if f in ['info','alert','help'] else .625 if f in ['plus','minus'] else .65)))
  elif 'square' in base:r=svg(frame(),*children(resize(inner,.625 if f in ['plus','minus'] else .65)))
  elif 'hexagon' in base or 'octagon' in base or 'triangle' in base:
   n=3 if 'triangle' in base else 6 if 'hexagon' in base else 8;pts=[]
   for j in range(n):
    a=-math.pi/2+2*math.pi*j/n;pts.append(f'{12+10*math.cos(a):.4f} {12+10*math.sin(a):.4f}')
   r=svg(p('M'+'L'.join(pts)+'Z'),*children(resize(inner,.65)))
  elif f in ['info','alert','help']:r=svg(c(12,12,9.5),*children(inner))
  elif 'small' in base:r=resize(inner,.6)
  elif 'done' in base:r=svg(frame(7,7,15,15,'TLBR',2.5),p('M3 16V3H16'),*children(resize(inner,.5,8,8)))
  elif 'heart' in base:r=svg(*children(ref('heart')),*children(resize(inner,.45)))
  return r,'check / info / error / success / brand-award1-lined'
 if f in ['bar','horizontal','align','flex','spacing','distribute','grid']:
  # Reflow diagrams to the CU half-unit keylines and broader spacing; retain data/order semantics.
  r=E.fromstring(old);g.apply(r,1.05,1.025,-.6,-.3)
  count=reconstruct_rectangles(r)
  return r,'brand-chart-lined / calendar / brand-device-desktop-lined (diagram keylines)'
 if f=='menu':
  if base.endswith('05'):return ref('menu'),'menu'
  if base.endswith('01'):return svg(p('M3 6H21M3 12H21M3 18H21')),'menu'
  rr=E.fromstring(old);g.apply(rr,1,.9,0,1.2);return rr,'menu'
 if f in ['brackets','variable']:
  rr=ref('math') if f=='brackets' else ref('brand-math-lined')
  if f=='brackets':
   kind=next((t for t in tokens if t in ['check','plus','minus','slash','x','ellipses']),None)
   if kind:rr.extend(glyph('slash' if kind=='slash' else 'dots' if kind=='ellipses' else kind,12,12,.9))
  return rr,'math / brand-math-lined'
 if f=='heart':
  rr=ref('heart')
  if 'circle' in base:rr=svg(c(12,12,10),*children(resize(rr,.62)))
  elif 'square' in base:rr=svg(frame(),*children(resize(rr,.62)))
  elif 'hexagon' in base or 'octagon' in base:
   n=6 if 'hexagon' in base else 8;pts=[]
   for j in range(n):
    a=-math.pi/2+j*2*math.pi/n;pts.append(f'{12+10*math.cos(a):.4f} {12+10*math.sin(a):.4f}')
   rr=svg(p('M'+'L'.join(pts)+'Z'),*children(resize(rr,.62)))
  elif 'hand' in base:return None,None
  return rr,'heart'
 if f=='coins':
  if 'stacked' in base:
   cylinder=ref('data')
   if base.endswith('04'):return cylinder,'data'
   left=resize(cylinder,.57,.3,7);right=resize(cylinder,.57,10,7 if base.endswith('02') else 10)
   return svg(*children(left),*children(right)),'data'
  if 'hand' in base:return None,None
  rr=svg(c(8.5,15,6.5),p('M9 8A6 6 0 1 1 15 14'))
  if base.endswith(('02','04')):rr.append(p('M8 12 9 11V18M7.5 18H10.5'))
  if 'swap' in base:rr.append(p('M2 7A5 5 0 0 1 8 2M4 2H8V6M22 17A5 5 0 0 1 16 22M20 22H16V18'))
  return rr,'clock / data (coin circle and overlap grammar)'
 return original_direct(base,old)

second_direct=direct

def direct(base,old):
 f=base.split('-')[0];tokens=base.split('-')
 if f=='git':
  r=ref('brand-network-lined')
  if 'merge' in base:r=mirror(r)
  elif 'commit' in base:r=svg(p('M2 12H8.5M15.5 12H22'),c(12,12,3.5))
  elif 'pull' in base:r=svg(p('M6 7V17M18 17V10A4 4 0 0 0 14 6H12M15 3 12 6 15 9'),c(6,4.5,2.18),c(6,19.5,2.18),c(18,19.5,2.18))
  return r,'brand-network-lined'
 if f in ['filter','sliders']:
  if f=='filter' and 'lines' in base:
   r=svg(p('M3 7H21M6.5 12H17.5M10 17H14'))
   if 'up' in base:r=rotate(r,180)
  else:
   r=ref('filter')
   if f=='sliders' and base.endswith(('01','02')):r=rotate(r,90)
  return r,'filter'
 if f=='loading':return ref('loading'),'loading'
 if f=='share':
  if base.endswith('07'):return svg(p('M7 10.5 16 6M7 13.5 16 18'),c(5,12,2.18),c(18,5,2.18),c(18,19,2.18)),'brand-network-lined'
  if base.endswith(('01','02')):
   r=ref('download');list(r)[0].set('d','M7 8L12 3L17 8M12 3V15');return r,'download / arrow-left'
  if base.endswith(('03','04')):return svg(frame(),*children(resize(ref('arrow-link'),.7))),'arrow-link / brand-device-desktop-lined'
  return svg(p('M3 20C3 12 8 9 14 9V4L22 12 14 20V15C9 15 5 16 3 20Z')),'arrow-left / brand-network-lined'
 if f=='microphone':
  r=svg(p('M8.5 5.5A3.5 3.5 0 0 1 15.5 5.5V11A3.5 3.5 0 0 1 8.5 11Z'),p('M5 10V11A7 7 0 0 0 19 11V10M12 18V22M8 22H16'))
  if base.endswith('02'):r.remove(list(r)[-1]);r.append(p('M5 10V11A7 7 0 0 0 19 11V10'))
  if 'off' in base:r.append(p('M3 3 21 21'))
  return r,'brand-rocket-lined (capsule) / trophy (stand)'
 if f=='phone' and base not in ['phone-01','phone-02']:
  # Narrower, diagonal handset: the arc/bridge proportions follow reference glasses rather than stock soft corners.
  r=svg(p('M5 3 2.5 5.5C2.5 13.5 10.5 21.5 18.5 21.5L21 19 16.5 14.5 14 17C10.5 15.5 8.5 13.5 7 10L9.5 7.5Z'))
  if 'incoming' in base:r.extend(glyph('down',18,6,.65))
  if 'outgoing' in base:r.extend(glyph('up',18,6,.65))
  if 'call' in base:r.append(p('M16 3A5 5 0 0 1 21 8M16 6A2 2 0 0 1 18 8'))
  if 'plus' in base:r.extend(glyph('plus',18,6,.65))
  if 'x' in base:r.extend(glyph('x',18,6,.65))
  if 'pause' in base:r.append(p('M17 3V9M21 3V9'))
  if 'hang' in base:r=rotate(r,135)
  return r,'brand-glasses-lined / arrow-left'
 if f=='log':
  r=ref('log-out-03')
  if 'in' in tokens:
   body=g.subpaths(list(r)[0].get('d'))[-1];r=svg(p(body),p('M21 12H9M14 7 9 12 14 17'))
  if base.endswith('04'):
   r=svg(p('M12 22A10 10 0 1 1 12 2'),*glyph('left' if 'in' in tokens else 'right',14,12,1.25))
  return r,'log-out-03'
 if f=='bookmark':
  r=svg(p('M5 3H16A3 3 0 0 1 19 6V22L12 18.5 5 22Z'))
  kind=next((t for t in tokens if t in ['add','check','minus','x']),None)
  if kind:r.extend(glyph('plus' if kind=='add' else kind,12,11,.85))
  return r,'brand-doc-lined / reward'
 if f=='sale':
  r=ref('sale')
  if base.endswith(('02','03','04')):
   seal=ref('brand-award1-lined')
   for n in seal.iter():
    if n.get('d'):n.set('d',g.subpaths(n.get('d'))[0])
   r=svg(*children(seal),p('M8 16 16 8'),c(8.5,8.5,.4),c(15.5,15.5,.4))
  return r,'sale / brand-award1-lined'
 if f in ['arrow','chevron','corner','refresh','repeat','reverse','flip','switch','arrows','marker','lock','clipboard','credit','wallet','shopping','lightbulb','cloud','star','stars','image','copy','check','x','plus','minus','info','alert','help','bar','horizontal','align','flex','spacing','distribute','grid','menu','brackets','variable','heart','coins']:
  return second_direct(base,old)
 return None,None

def sharpen_geometric_corners(root):
 changed=0
 for n in root.iter():
  if not n.get('d'):continue
  seg=g.segments(n.get('d'));out=[];i=0
  while i<len(seg):
   group=seg[i:i+3]
   if len(group)==3 and all(z[0]=='C' for z in group):
    start=group[0][2];end=group[-1][3];c1=group[0][1][:2];c2=group[-1][1][2:4]
    a=(c1[0]-start[0],c1[1]-start[1]);b=(end[0]-c2[0],end[1]-c2[1]);cross=a[0]*b[1]-a[1]*b[0];dist=math.dist(start,end)
    if .01<dist<4 and abs(cross)>1e-8:
     delta=(end[0]-start[0],end[1]-start[1]);t=(delta[0]*b[1]-delta[1]*b[0])/cross
     vertex=(start[0]+t*a[0],start[1]+t*a[1])
     if math.dist(vertex,start)<=4 and math.dist(vertex,end)<=4 and t>0:
      out.extend([['L',list(vertex)],['L',list(end)]]);i+=3;changed+=1;continue
   out.append(seg[i]);i+=1
  n.set('d',g.serialize(out))
 return changed

third_direct=direct

def direct(base,old):
 if base.startswith('eye'):
  if 'off' in base:return ref('hide'),'hide'
  r=ref('show');ns='http://www.w3.org/2000/svg'
  for n in list(r):
   if n.tag.endswith('}mask'):
    n.tag='{'+ns+'}clipPath';keep={'id':n.get('id')};n.attrib.clear();n.attrib.update(keep)
   if n.get('mask'):
    n.set('clip-path',n.get('mask'));del n.attrib['mask']
  return r,'show (native clipPath replacing authoring mask)'
 return third_direct(base,old)
