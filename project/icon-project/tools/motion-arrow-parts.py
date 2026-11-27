"""Keep straight arrowheads and the stems touching their tips in one rigid part."""
import re,math
NUMBER=r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?'
def points(node):
 if not node.tag.endswith('path'):return None
 d=node.get('d','')
 if re.search(r'[CcSsQqTtAaZz]',d):return None
 tokens=re.findall(r'[MmLlHhVv]|'+NUMBER,d);out=[];i=0;cmd=None;x=y=0
 try:
  while i<len(tokens):
   if tokens[i].isalpha():cmd=tokens[i];i+=1
   if cmd in ['M','L','m','l']:
    a,b=float(tokens[i]),float(tokens[i+1]);i+=2
    if cmd.islower():a+=x;b+=y
    x,y=a,b
   elif cmd in ['H','h']:
    a=float(tokens[i]);i+=1;x=a+x if cmd=='h' else a
   elif cmd in ['V','v']:
    a=float(tokens[i]);i+=1;y=a+y if cmd=='v' else a
   else:return None
   out.append((x,y))
  return out
 except (ValueError,IndexError):return None

def combine(root,nodes,parent_of,group):
 paths={n:points(n) for n in nodes};links=[]
 for head,pts in paths.items():
  if pts is None or len(pts)!=3:continue
  a,tip,b=pts;u=(a[0]-tip[0],a[1]-tip[1]);v=(b[0]-tip[0],b[1]-tip[1]);lu=math.hypot(*u);lv=math.hypot(*v)
  if not lu or not lv or abs(lu-lv)>max(lu,lv)*.15:continue
  cosine=(u[0]*v[0]+u[1]*v[1])/(lu*lv)
  if not -.7<cosine<.7:continue
  bisector=(u[0]/lu+v[0]/lv,u[1]/lu+v[1]/lv);length=math.hypot(*bisector)
  if not length:continue
  direction=(-bisector[0]/length,-bisector[1]/length)
  for stem,line in paths.items():
   if line is None or len(line)!=2 or parent_of(root,stem) is not parent_of(root,head):continue
   for endpoint,other in [(line[0],line[1]),(line[1],line[0])]:
    if math.dist(endpoint,tip)>.015:continue
    delta=(other[0]-tip[0],other[1]-tip[1]);distance=math.hypot(*delta)
    if distance<min(lu,lv)*.6:continue
    if -(delta[0]*direction[0]+delta[1]*direction[1])/distance<.98:continue
    links.append((head,stem,direction));break
 components=[]
 for head,stem,direction in links:
  matches=[c for c in components if head in c['nodes'] or stem in c['nodes']]
  c={'nodes':{head,stem},'directions':[direction]}
  for previous in matches:c['nodes']|=previous['nodes'];c['directions']+=previous['directions'];components.remove(previous)
  components.append(c)
 replacement={};rigid={}
 for c in components:
  chosen=[n for n in nodes if n in c['nodes']];g=group(root,chosen)
  if g is None:continue
  rigid[g]=c['directions']
  for n in chosen:replacement[n]=g
 atomic=[]
 for n in nodes:
  n=replacement.get(n,n)
  if n not in atomic:atomic.append(n)
 return atomic,rigid,replacement
