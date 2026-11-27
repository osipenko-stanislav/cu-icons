#!/usr/bin/env python3
"""Source-preserving family adaptation into the approved CU reference profile.
Never writes approved SVGs or the style specification. Stages only Pending entries.
"""
from pathlib import Path
import re, json, math, copy, sys, importlib.util
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)
def el(tag,**attrs):return E.Element('{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
def path(d,cap='round',join='round'):return el('path',d=d,stroke_linecap=cap,stroke_linejoin=join)
def circle(x,y,r):return el('circle',cx=x,cy=y,r=r)
def fmt(n):return format(round(n,5),'.5f').rstrip('0').rstrip('.') if n else '0'
NUM=r'[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?'
COUNTS={'M':2,'L':2,'C':6,'Q':4,'S':4,'T':2,'H':1,'V':1,'A':7,'Z':0}

def segments(d):
 tok=re.findall('[A-Za-z]|'+NUM,d); out=[];i=0;cmd=None;p=(0.,0.);start=p
 while i<len(tok):
  if tok[i].isalpha():cmd=tok[i];i+=1
  if cmd.islower() and cmd!='z':raise ValueError('Relative path needs explicit handling')
  k=cmd.upper();n=COUNTS[k]
  if k=='Z':out.append([k,[],p,start]);p=start;cmd=None;continue
  a=list(map(float,tok[i:i+n]));i+=n
  if len(a)!=n:raise ValueError('Bad path')
  end=(a[-2],a[-1]) if k not in ['H','V'] else (a[0],p[1]) if k=='H' else (p[0],a[0])
  out.append([k,a,p,end]);p=end
  if k=='M':start=p;cmd='L'
 return out

def serialize(segs):return ''.join(k+(' '.join(fmt(x) for x in a)) for k,a,*_ in segs)
def subpaths(d):return re.findall(r'[Mm][^Mm]*',d)
def transform_d(d,sx=1,sy=1,tx=0,ty=0):
 out=[]
 for k,a,_,_ in segments(d):
  a=list(a)
  if k=='H':a[0]=a[0]*sx+tx
  elif k=='V':a[0]=a[0]*sy+ty
  elif k=='A':
   a[0]*=abs(sx);a[1]*=abs(sy);a[5]=a[5]*sx+tx;a[6]=a[6]*sy+ty
  else:
   for i in range(0,len(a),2):a[i]=a[i]*sx+tx;a[i+1]=a[i+1]*sy+ty
  out.append([k,a])
 return serialize(out)

def curve_corner(group):
 if len(group)!=3 or any(s[0]!='C' for s in group):return None
 a=group[0][2]; b=group[-1][3]; c1=group[0][1][:2]; c2=group[-1][1][2:4]
 eps=.002
 horizontal=abs(c1[1]-a[1])<eps and abs(c2[0]-b[0])<eps
 vertical=abs(c1[0]-a[0])<eps and abs(c2[1]-b[1])<eps
 dx=b[0]-a[0];dy=b[1]-a[1]
 if abs(dx)<.2 or abs(dy)<.2 or max(abs(dx),abs(dy))>6.5 or abs(abs(dx)-abs(dy))>.015:return None
 if not (horizontal or vertical):return None
 corner=(b[0],a[1]) if horizontal else (a[0],b[1])
 # All control points must stay in the monotone quarter-box.
 for s in group:
  for j in range(0,6,2):
   if not min(a[0],b[0])-eps<=s[1][j]<=max(a[0],b[0])+eps or not min(a[1],b[1])-eps<=s[1][j+1]<=max(a[1],b[1])+eps:return None
 if horizontal:label=('T' if dy>0 else 'B')+('R' if dx>0 else 'L')
 else:label=('B' if dy>0 else 'T')+('R' if dx<0 else 'L')
 return label,corner,a,b

def adapt_corners(d,keep):
 seg=segments(d);out=[];changed=0;i=0
 while i<len(seg):
  c=curve_corner(seg[i:i+3])
  if c:
   label,vertex,a,b=c
   # Only a family's designated curved corners survive. Smaller inner corners stay straight.
   r=min(3,abs(b[0]-a[0]),abs(b[1]-a[1]))
   if label not in keep or r<1.8:
    out.extend([['L',list(vertex)],['L',list(b)]])
   else:
    # Same entry/exit tangents, with a true radius <=3 rather than source easing splines.
    ux=(a[0]-vertex[0])/abs(a[0]-vertex[0]) if a[0]!=vertex[0] else 0
    uy=(a[1]-vertex[1])/abs(a[1]-vertex[1]) if a[1]!=vertex[1] else 0
    vx=(b[0]-vertex[0])/abs(b[0]-vertex[0]) if b[0]!=vertex[0] else 0
    vy=(b[1]-vertex[1])/abs(b[1]-vertex[1]) if b[1]!=vertex[1] else 0
    entry=(vertex[0]+ux*r,vertex[1]+uy*r);exit=(vertex[0]+vx*r,vertex[1]+vy*r)
    # Path direction determines the arc sweep via the incoming and outgoing vectors.
    inc=(-ux,-uy); leave=(vx,vy); sweep=int(inc[0]*leave[1]-inc[1]*leave[0]>0)
    out.extend([['L',list(entry)],['A',[r,r,0,0,sweep,*exit]],['L',list(b)]])
   changed+=1;i+=3
  else:out.append(seg[i]);i+=1
 return serialize(out),changed

# Approved pilot components are used unchanged where the source variant needs that component.
PILOT=ROOT/'staging/pilot'
def pilot_children(identifier):return [copy.deepcopy(n) for n in E.parse(PILOT/(identifier+'-lined.svg')).getroot()]
HOUSE=pilot_children('home-01')[0]; SHIELD=pilot_children('shield-tick')[0]

def normalize(root):
 for n in root.iter():
  for k in ['fill','stroke']:
   if n.get(k) and n.get(k) not in ['none','transparent'] and not n.get(k).startswith('url('):n.set(k,'currentColor')
  if n.get('stroke-width') is not None:n.set('stroke-width','1')
  if n.get('stroke-linecap')=='square':n.set('stroke-linecap','round')
 root.set('stroke-width','1');root.set('fill','none');root.set('viewBox','0 0 24 24');root.set('width','24');root.set('height','24')

def apply(root,sx=1,sy=1,tx=0,ty=0):
 for n in root.iter():
  if n.get('d'):n.set('d',transform_d(n.get('d'),sx,sy,tx,ty))
  for key in ['x','cx','x1','x2']:
   if n.get(key) is not None:n.set(key,fmt(float(n.get(key))*sx+tx))
  for key in ['y','cy','y1','y2']:
   if n.get(key) is not None:n.set(key,fmt(float(n.get(key))*sy+ty))
  for key,scale in [('r',min(sx,sy)),('rx',sx),('ry',sy)]:
   if n.get(key) is not None:n.set(key,fmt(float(n.get(key))*scale))
  if n is not root:
   for key,scale in [('width',sx),('height',sy)]:
    if n.get(key) is not None:n.set(key,fmt(float(n.get(key))*scale))

def adapt(identifier,raw):
 root=E.fromstring(raw);vb=list(map(float,root.get('viewBox').split()));base=identifier.removesuffix('-lined');notes=[];normalize(root)
 if vb[2:]==[16,16]:
  apply(root,1.5,1.5);notes.append('16-to-24 coordinate conversion; live stroke remains 1')
 if vb[2:]==[40,40]:
  apply(root,.6,.6)
  rect=next(n for n in root if n.tag.endswith('rect'));root.remove(rect)
  c=circle(12,12,11);c.set('stroke','currentColor');root.insert(0,c)
  notes.append('40-to-24; tonal circle container converted to live outline circle; document retained')
 # Exact pilot house silhouette, with meaningful source variants retained.
 if base.startswith('home-'):
  root=el('svg',xmlns=NS,width=24,height=24,viewBox='0 0 24 24',fill='none',stroke='currentColor',stroke_width=1)
  if base=='home-03':
   root.extend([path('M2 11 12 2 22 11','butt','miter'),path('M4 9.2V21H20V9.2M10 21V14H14V21','butt','miter')])
  elif base=='home-05':root.append(path('M4 11 12 3 20 11V21H14V14H10V21H4Z','butt','miter'))
  else:
   root.append(copy.deepcopy(HOUSE))
   if base=='home-02':root.append(path('M10 21V14H14V21','butt','miter'))
   if base=='home-04':root.append(circle(12,13,3))
   if base=='home-line':root.append(path('M8 17H16'))
   if base=='home-smile':root.append(path('M8 13.5A4.1 4.1 0 0 0 16 13.5'))
  notes.append('Approved pitched roof with source-specific door, circle, smile or eaves')
 if base.startswith('shield-') and base not in ['shield-02','shield-off']:
  for n in root.iter():
   if not n.get('d'):continue
   parts=subpaths(n.get('d'));new=[]
   for d in parts:
    if '7.217' in d and len(d)>500 and d.rstrip().endswith('Z'):
     new.append(SHIELD.get('d'));notes.append('Approved flat-top shield contour')
    else:new.append(d)
   n.set('d',''.join(new))
  if base=='shield-03':
   for n in root.iter():
    if n.get('d'):n.set('d',re.sub(r'M12 2\.50011V21\.5001','M12 3V21.5',n.get('d')))
 if base=='shield-off':
  root=el('svg',xmlns=NS,width=24,height=24,viewBox='0 0 24 24',fill='none',stroke='currentColor',stroke_width=1)
  root.extend([path('M8 3H20V13.5M18 17.5 12 21.5 6.2 17.65A5 5 0 0 1 4 13.5V6'),path('M3 3 21 21')]);notes.append('Flat-top shield with separated slash intersections')
 if base in ['arrow-up','arrow-down']:
  root.clear();root.attrib.update({'width':'24','height':'24','viewBox':'0 0 24 24','fill':'none','stroke':'currentColor','stroke-width':'1'})
  root.append(path('M12 22V2M2 12 12 2 22 12' if base=='arrow-up' else 'M12 2V22M2 12 12 22 22 12'));notes.append('20-unit arrows matching approved left/right pair')
 # Family-specific corner grammar, including partial modifier containers.
 family=base.split('-')[0];keep=None
 if family=='file':keep={'BL'}
 elif family=='calendar':keep={'TL','BR'}
 elif family=='folder':keep={'TR','BL'}
 elif family in ['monitor','tablet','laptop','browser','server','clipboard','copy','image','briefcase','wallet','presentation','notification','keyboard','printer'] or base.startswith(('cpu-chip','credit-card','book-closed')):keep={'TL'}
 elif family in ['message','annotation'] and 'circle' not in base:keep={'TR','BR'}
 changes=0
 if keep:
  for n in root.iter():
   if n.get('d'):
    d,count=adapt_corners(n.get('d'),keep);n.set('d',d);changes+=count
  if changes:notes.append(f'{changes} container corner groups adapted; curved '+','.join(sorted(keep)))
 # File fold uses a simple corner instead of the soft source fold.
 if family=='file' and vb[2]==24:
  fold=False
  for n in root.iter():
   if not n.get('d'):continue
   parts=subpaths(n.get('d'));new=[]
   for d in parts:
    if re.match(r'M14 2\.269',d) and 'H19.7305' in d:
     new.append('M14 2V8H20');fold=True
    elif len(d)>400 and ('12.0118' in d or 'M14 2H8.8' in d) and d.rstrip().endswith('Z'):
     new.append('M14 2H4V19A3 3 0 0 0 7 22H20V8Z');fold=True
    else:new.append(d)
   n.set('d',''.join(new))
  apply(root,.875,.9,2,1.2)
  if fold:notes.append('Crisp fold with one curved lower corner')
  notes.append('Document envelope aligned to reference proportions')
 if family=='calendar':
  for n in root.iter():
   if not n.get('d'):continue
   parts=[d for d in subpaths(n.get('d')) if d not in ['M16 2V6','M8 2V6']]
   n.set('d',''.join(parts))
  apply(root,17/18,17/18,2/3,-5/18)
  for n in root.iter():
   if n.get('d'):
    parts=subpaths(n.get('d'));n.set('d',''.join('M3.5 7.5H20.5' if re.match(r'M20\.5 9\.16667H3\.5',d) else d for d in parts))
  notes.append('Approved shallow header; plain/date/check variants retained')
 # Tight circular head proportions, preserving all body and badge distinctions.
 if family in ['user','users']:
  for n in root.iter():
   if not n.get('d'):continue
   new=[]
   for d in subpaths(n.get('d')):
    seg=segments(d)
    if len(seg)==6 and seg[0][0]=='M' and seg[-1][0]=='Z' and all(v[0]=='C' for v in seg[1:5]):
     points=[s[3] for s in seg[:-1]];xs=[p[0] for p in points];ys=[p[1] for p in points];x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
     if 6<=x1-x0<=9.1 and abs((x1-x0)-(y1-y0))<.02 and y1<=12.1:
      x=(x0+x1)/2;y=7.5;r=3.5
      new.append(f'M{fmt(x+r)} {y}A{r} {r} 0 1 1 {fmt(x-r)} {y}A{r} {r} 0 1 1 {fmt(x+r)} {y}Z');notes.append('Head radius 3.5 at y7.5, consistent with pilot');continue
    new.append(d)
   n.set('d',''.join(new))
 # Match rear-head arcs to the approved group icon, preserving edit overlap breaks.
 if family=='users':
  for n in root.iter():
   if not n.get('d'):continue
   new=[]
   for d in subpaths(n.get('d')):
    if len(d)<400 and re.match(r'M(?:15\.5 3\.29076|16 3\.46776)',d) and d.count('C') in [2,3]:
     new.append('M14.5 4.5A3.5 3.5 0 1 1 14.5 10.5')
    elif len(d)<400 and d.startswith('M16 11.5322') and d.count('C') in [2,3]:
     new.append('M14.5 10.5A3.5 3.5 0 1 0 14.5 4.5')
    elif d=='M15.5 3.29076C16.9659 3.88415 18 5.32131 18 7':
     new.append('M14.5 4.5A3.5 3.5 0 0 1 18.5 7.5')
    else:new.append(d)
   n.set('d',''.join(new))
 # Native rects in source containers obey the same selective-corner grammar.
 if keep:
  for parent in list(root.iter()):
   for n in list(parent):
    if n.tag.endswith('}rect') and (n.get('rx') or n.get('ry')):
     x=float(n.get('x','0'));y=float(n.get('y','0'));w=float(n.get('width'));h=float(n.get('height'));r=min(3,float(n.get('rx',n.get('ry','0'))),w/2,h/2)
     if w<3 or h<3:continue
     corners=[('TL',(x,y)),('TR',(x+w,y)),('BR',(x+w,y+h)),('BL',(x,y+h))]
     d=f'M{fmt(x+r if "TL" in keep else x)} {fmt(y)}'
     d+=f'H{fmt(x+w-r if "TR" in keep else x+w)}'+(f'A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x+w)} {fmt(y+r)}' if 'TR' in keep else '')
     d+=f'V{fmt(y+h-r if "BR" in keep else y+h)}'+(f'A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x+w-r)} {fmt(y+h)}' if 'BR' in keep else '')
     d+=f'H{fmt(x+r if "BL" in keep else x)}'+(f'A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x)} {fmt(y+h-r)}' if 'BL' in keep else '')
     d+=f'V{fmt(y+r if "TL" in keep else y)}'+(f'A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x+r)} {fmt(y)}' if 'TL' in keep else '')+'Z'
     attrs={k:v for k,v in n.attrib.items() if k not in ['x','y','width','height','rx','ry']};attrs['d']=d;p=el('path',**attrs);parent.insert(list(parent).index(n),p);parent.remove(n)
     notes.append('Native rounded rectangle adapted')
 if not notes:notes.append('Source geometry compatible; live stroke/palette/caps normalized')
 # Avoid duplicate xmlns attributes on authored roots.
 root.attrib.pop('xmlns',None)
 return E.tostring(root,encoding='utf-8')+b'\n',notes

def main():
 manifest=json.loads((ROOT/'manifest.json').read_text()); batches=[b for b in manifest['batches'] if b['id']!='pilot']
 wanted=sys.argv[1:] or [b['id'] for b in batches]; report={}
 for batch in batches:
  if batch['id'] not in wanted:continue
  stage=ROOT/'staging'/batch['id'];stage.mkdir(parents=True,exist_ok=True)
  for identifier in batch['ids']:
   if manifest['icons'][identifier]['status']!='Pending':continue
   src=manifest['sources'][manifest['icons'][identifier]['source']]
   raw,notes=adapt(identifier,(ROOT/src['path']).read_bytes());(stage/(identifier+'.svg')).write_bytes(raw);report[identifier]=notes
  print(batch['id'],len(list(stage.glob('*.svg'))))
 target=ROOT/'review/reports/series-authoring.json'
 if target.exists():report={**json.loads(target.read_text()),**report}
 target.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
