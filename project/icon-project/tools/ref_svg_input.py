"""Read imported native ref SVGs with strictly local alpha masks preserved."""
import re
from motion_gallery import parse,inspect,xml
from production import isolate_ids

def svg_input_ref(path,identifier):
 raw=path.read_bytes();tree=parse(raw);parts={};ids={n.get('id') for n in tree.iter() if n.get('id')}
 for n in tree.iter():
  kind=n.tag.split('}')[-1]
  if 'data-part' in n.attrib:
   value=n.attrib.pop('data-part');assert re.fullmatch(r'0|[1-9][0-9]*',value) and int(value) not in parts;parts[int(value)]=(n,value)
  if 'mask' in n.attrib:
   match=re.fullmatch(r'url\(#([A-Za-z0-9_.:-]+)\)',n.get('mask'));assert match and match[1] in ids,'Mask must resolve inside the same SVG'
  if kind=='mask':
   assert n.get('maskUnits','userSpaceOnUse') in ['userSpaceOnUse','objectBoundingBox']
   assert n.get('style','') in ['', 'mask-type:alpha','mask-type: alpha']
 assert list(parts)==list(range(len(parts)))
 # Validate the ordinary SVG profile on a copy with mask-only extensions
 # removed. Separately checked local definitions remain in the published tree.
 import copy
 checked=copy.deepcopy(tree)
 for parent in checked.iter():
  for child in list(parent):
   if child.tag.split('}')[-1]=='mask':parent.remove(child)
  parent.attrib.pop('mask',None)
 for issue in inspect(xml(checked),identifier)[1]:
  if issue['level']=='Error':raise ValueError(f'{path.name}: {issue["message"]}')
 # Mask children themselves contain only the same validated vector subset.
 for mask in tree.iter():
  if mask.tag.split('}')[-1]!='mask':continue
  wrapper=parse(b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"/>')
  for child in mask:wrapper.append(copy.deepcopy(child))
  for issue in inspect(xml(wrapper),identifier)[1]:
   if issue['level']=='Error':raise ValueError(f'{path.name}: mask content: {issue["message"]}')
 isolate_ids(tree,identifier+'--')
 for node,value in parts.values():node.set('data-part',value)
 return raw,xml(tree).decode(),parts
