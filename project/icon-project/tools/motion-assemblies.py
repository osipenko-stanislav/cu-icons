"""Keep structurally connected artwork together in scenes with confirmed joint tears."""
import json,xml.etree.ElementTree as E
ATTRS=['d','cx','cy','r','x','y','width','height','rx','ry','x1','x2','y1','y2','points']
def key(n):return json.dumps([n.tag.split('}')[-1],*[n.get(a) for a in ATTRS]],ensure_ascii=False,separators=(',',':'))
def combine(root,nodes,contacts,parent_of,group):
 lookup={}
 for n in nodes:lookup.setdefault(key(n),[]).append(n)
 components=[]
 for c in contacts:
  for a in lookup.get(c['source'],[]):
   for b in lookup.get(c['target'],[]):
    if a is b:continue
    matches=[s for s in components if a in s or b in s];merged={a,b}
    for s in matches:merged|=s;components.remove(s)
    components.append(merged)
 replaced={};assemblies=[]
 for component in components:
  chosen=[n for n in nodes if n in component];g=group(root,chosen)
  if g is None:
   g=E.Element('{http://www.w3.org/2000/svg}g');root.append(g)
   for n in chosen:
    chain=[];p=parent_of(root,n)
    while p is not root:chain.append(p);p=parent_of(root,p)
    p=parent_of(root,n);p.remove(n);dest=g
    for ancestor in reversed(chain):dest=E.SubElement(dest,ancestor.tag,{k:v for k,v in ancestor.attrib.items() if k!='id'})
    dest.append(n)
  assemblies.append(g)
  for n in chosen:replaced[n]=g
 result=[]
 for n in nodes:
  n=replaced.get(n,n)
  if n not in result:result.append(n)
 return result,assemblies,replaced
