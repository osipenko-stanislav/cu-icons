"""Convert only project-owned SVG paths to editable Lottie Beziers."""
import math,re,xml.etree.ElementTree as E
from svg.path import parse_path,Move,Line,Close,CubicBezier,QuadraticBezier,Arc
IDENTITY=[1,0,0,1,0,0]
def multiply(a,b):return [a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5]]
def inverse(a):
 det=a[0]*a[3]-a[1]*a[2]
 return [a[3]/det,-a[1]/det,-a[2]/det,a[0]/det,(a[2]*a[5]-a[3]*a[4])/det,(a[1]*a[4]-a[0]*a[5])/det]
def translate(x,y):return [1,0,0,1,x,y]
def rotate(r):
 a=math.radians(r);return [math.cos(a),math.sin(a),-math.sin(a),math.cos(a),0,0]
def transform(a,p):return complex(a[0]*p.real+a[2]*p.imag+a[4],a[1]*p.real+a[3]*p.imag+a[5])
def svg_matrix(value):
 result=IDENTITY
 for name,args in re.findall(r'([A-Za-z]+)\s*\(([^)]*)\)',value or ''):
  n=[float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',args)]
  if name=='matrix':m=n
  elif name=='translate':m=translate(n[0],n[1] if len(n)>1 else 0)
  elif name=='scale':m=[n[0],0,0,n[1] if len(n)>1 else n[0],0,0]
  elif name=='rotate':m=rotate(n[0]);m=multiply(multiply(translate(n[1],n[2]),m),translate(-n[1],-n[2])) if len(n)>1 else m
  elif name=='skewX':m=[1,0,math.tan(math.radians(n[0])),1,0,0]
  elif name=='skewY':m=[1,math.tan(math.radians(n[0])),0,1,0,0]
  else:raise ValueError('Unsupported SVG transform '+name)
  result=multiply(result,m)
 return result

def cubic_segments(segment):
 if isinstance(segment,Close) and segment.start==segment.end:return []
 if isinstance(segment,CubicBezier):return [(segment.start,segment.control1,segment.control2,segment.end)]
 if isinstance(segment,QuadraticBezier):return [(segment.start,segment.start+(segment.control-segment.start)*2/3,segment.end+(segment.control-segment.end)*2/3,segment.end)]
 if isinstance(segment,Arc):
  if segment.start==segment.end:return []
  rx=segment.radius.real*segment.radius_scale;ry=segment.radius.imag*segment.radius_scale;phi=math.radians(segment.rotation);rotation=complex(math.cos(phi),math.sin(phi));a=math.radians(segment.theta);delta=math.radians(segment.delta);count=max(1,math.ceil(abs(delta)/(math.pi/2)));out=[]
  def point(t):return segment.center+complex(rx*math.cos(t),ry*math.sin(t))*rotation
  def derivative(t):return complex(-rx*math.sin(t),ry*math.cos(t))*rotation
  for i in range(count):
   start=a+delta*i/count;end=a+delta*(i+1)/count;k=4/3*math.tan((end-start)/4);p0=segment.start if i==0 else point(start);p3=segment.end if i==count-1 else point(end);out.append((p0,p0+k*derivative(start),p3-k*derivative(end),p3))
  return out
 return [(segment.start,segment.start,segment.end,segment.end)]

def bezier_paths(d,m=IDENTITY):
 paths=[];segments=[];closed=False
 def flush():
  if not segments:return
  vertices=[segments[0][0]];incoming=[0j];outgoing=[0j]
  for a,b,c,end in segments:
   outgoing[-1]=b-a
   if closed and abs(end-vertices[0])<1e-6 and (a,b,c,end)==segments[-1]:incoming[0]=c-end
   else:vertices.append(end);incoming.append(c-end);outgoing.append(0j)
  def pair(z):return [round(z.real,5),round(z.imag,5)]
  paths.append({'c':closed,'v':[pair(transform(m,v)) for v in vertices],'i':[pair(transform(m,v+z)-transform(m,v)) for v,z in zip(vertices,incoming)],'o':[pair(transform(m,v+z)-transform(m,v)) for v,z in zip(vertices,outgoing)]})
 for s in parse_path(d):
  if isinstance(s,Move):flush();segments=[];closed=False
  else:
   if isinstance(s,Close):closed=True
   segments.extend(cubic_segments(s))
 flush();return paths

def extract(raw):
 root=E.fromstring(raw);entries=[]
 def walk(n,m,style,hidden=False):
  kind=n.tag.split('}')[-1];m=multiply(m,svg_matrix(n.get('transform')));style={**style,**{k:v for k,v in n.attrib.items() if k in ['stroke','fill','stroke-linecap','stroke-linejoin','stroke-width','opacity','fill-rule']}};hidden=hidden or kind in ['defs','clipPath'] or n.get('visibility')=='hidden'
  if not hidden:
   d=n.get('d')
   if kind in ['circle','ellipse']:
    cx=float(n.get('cx','0'));cy=float(n.get('cy','0'));rx=float(n.get('r',n.get('rx','0')));ry=float(n.get('r',n.get('ry','0')));d=f'M{cx+rx} {cy}A{rx} {ry} 0 0 1 {cx} {cy+ry}A{rx} {ry} 0 0 1 {cx-rx} {cy}A{rx} {ry} 0 0 1 {cx} {cy-ry}A{rx} {ry} 0 0 1 {cx+rx} {cy}Z'
   elif kind=='line':d=f'M{n.get("x1","0")} {n.get("y1","0")}L{n.get("x2","0")} {n.get("y2","0")}'
   elif kind=='rect':
    x=float(n.get('x','0'));y=float(n.get('y','0'));w=float(n.get('width'));h=float(n.get('height'));rx=float(n.get('rx','0'));ry=float(n.get('ry',str(rx)))
    d=f'M{x+rx} {y}H{x+w-rx}A{rx} {ry} 0 0 1 {x+w} {y+ry}V{y+h-ry}A{rx} {ry} 0 0 1 {x+w-rx} {y+h}H{x+rx}A{rx} {ry} 0 0 1 {x} {y+h-ry}V{y+ry}A{rx} {ry} 0 0 1 {x+rx} {y}Z' if rx else f'M{x} {y}H{x+w}V{y+h}H{x}Z'
   if d:
    for path in bezier_paths(d,m):entries.append({'path':path,'style':style.copy(),'source_d':d})
  for c in n:walk(c,m,style,hidden)
 walk(root,IDENTITY,{'fill':'black','stroke':'none','stroke-linecap':'butt','stroke-linejoin':'miter','stroke-width':'1'});return entries

def transform_path(path,m):
 def p(v):return complex(*v)
 def xy(z):return [round(z.real,5),round(z.imag,5)]
 vertices=[p(v) for v in path['v']]
 return {'c':path['c'],'v':[xy(transform(m,v)) for v in vertices],'i':[xy(transform(m,v+p(z))-transform(m,v)) for v,z in zip(vertices,path['i'])],'o':[xy(transform(m,v+p(z))-transform(m,v)) for v,z in zip(vertices,path['o'])]}

def initial_value(prop,default):
 if not prop:return default
 if not prop.get('a'):return prop.get('k',default)
 return prop['k'][0].get('s',default)
def initial_matrix(tr):
 p=initial_value(tr.get('p'),[0,0]);a=initial_value(tr.get('a'),[0,0]);s=initial_value(tr.get('s'),[100,100]);r=initial_value(tr.get('r'),0);r=r[0] if isinstance(r,list) else r
 return multiply(multiply(multiply(translate(p[0],p[1]),rotate(r)),[s[0]/100,0,0,s[1]/100,0,0]),translate(-a[0],-a[1]))
IDENTITY_TRANSFORM={'ty':'tr','p':{'a':0,'k':[0,0]},'a':{'a':0,'k':[0,0]},'s':{'a':0,'k':[100,100]},'r':{'a':0,'k':0},'o':{'a':0,'k':100},'sk':{'a':0,'k':0},'sa':{'a':0,'k':0}}
def paint_group(entry,path=None,force=None):
 import copy
 style=entry['style'];path=path or entry['path'];it=[{'ty':'sh','ks':{'a':0,'k':path}}]
 stroke=style.get('stroke') not in ['none','transparent'];fill=style.get('fill') not in ['none','transparent']
 if force=='fill':stroke=False;fill=True
 if fill:it.append({'ty':'fl','c':{'a':0,'k':[0,0,0,1]},'o':{'a':0,'k':100},'r':2 if style.get('fill-rule')=='evenodd' else 1})
 if stroke:it.append({'ty':'st','c':{'a':0,'k':[0,0,0,1]},'o':{'a':0,'k':100},'w':{'a':0,'k':1},'lc':{'butt':1,'round':2,'square':3}.get(style.get('stroke-linecap'),1),'lj':{'miter':1,'round':2,'bevel':3}.get(style.get('stroke-linejoin'),1),'ml':4,'bm':0})
 it.append(copy.deepcopy(IDENTITY_TRANSFORM));return {'ty':'gr','it':it,'nm':'Project SVG geometry'}
