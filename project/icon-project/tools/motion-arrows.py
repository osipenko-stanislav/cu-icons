"""World-coordinate arrow motion, independent of the source SVG's nested transforms."""
import xml.etree.ElementTree as E
NS='{http://www.w3.org/2000/svg}'
def author(id,r,nodes,parent_of,add):
 base=id.split('-')[0]
 if base not in ['arrow','arrows','chevron','corner']:return None
 def world_target(chosen):
  target=E.Element(NS+'g');r.append(target)
  for n in chosen:
   chain=[];p=parent_of(r,n)
   while p is not r:chain.append(p);p=parent_of(r,p)
   parent=parent_of(r,n);parent.remove(n);dest=target
   for ancestor in reversed(chain):
    clone=E.SubElement(dest,ancestor.tag,{k:v for k,v in ancestor.attrib.items() if k!='id'});dest=clone
   dest.append(n)
  return target
 if id=='arrows-triangle-lined':
  add(world_target(nodes),'rotate',8,12,12)
  return 'cycle-return','Cycle rotates around its own center and returns'
 if 'selector' in id and len(nodes)>=2:
  axis='y' if 'vertical' in id else 'x'
  add(world_target(nodes[:len(nodes)//2]),axis,-.45)
  add(world_target(nodes[len(nodes)//2:]),axis,.45)
  return 'selector-spread','Opposing chevrons move apart in canvas coordinates and return'
 framed=any(w in id for w in ['circle','square'])
 chosen=nodes[1:] if framed and len(nodes)>1 else nodes
 target=world_target(chosen)
 # Normalize the vector so diagonals have the same travel distance as axial arrows.
 dx=-1 if 'left' in id else 1 if 'right' in id else 0
 dy=-1 if 'up' in id else 1 if 'down' in id else 0
 if not dx and not dy:return None
 distance=.75 if framed else .65
 length=(dx*dx+dy*dy)**.5
 if dx and dy:
  inner=E.SubElement(target,NS+'g')
  for n in list(target):
   if n is not inner:target.remove(n);inner.append(n)
  add(target,'x',distance*dx/length);add(inner,'y',distance*dy/length)
 elif dx:add(target,'x',distance*dx)
 else:add(target,'y',distance*dy)
 return 'arrow-vector-return','Arrow travels along its semantic direction in canvas coordinates; frame stays stationary'
