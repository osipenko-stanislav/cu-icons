#!/usr/bin/env python3
"""Reference-first reconstruction authorized by the user after reviewing v2 comparisons.
Approved SVGs stay locked. Source/reference bytes remain immutable.
"""
from pathlib import Path
import json,re,copy,math,importlib.util,sys,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)
sp=importlib.util.spec_from_file_location('geo',Path(__file__).with_name('produce-series.py'));g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
p=g.path;c=g.circle

def svg(*nodes):
 r=g.el('svg',width=24,height=24,viewBox='0 0 24 24',fill='none',stroke='currentColor',stroke_width=1);r.extend(nodes);return r

def ref(name):
 r=E.parse(ROOT.parent/'ref'/(name+'.svg')).getroot();g.normalize(r);r.set('stroke','currentColor');return r

def pilot(name):return E.parse(ROOT/'staging/pilot'/(name+'-lined.svg')).getroot()
def children(r):return [copy.deepcopy(x) for x in r]
def resize(r,f,tx=None,ty=None):
 r=copy.deepcopy(r);g.apply(r,f,f,12*(1-f) if tx is None else tx,12*(1-f) if ty is None else ty);return r

def glyph(kind,x=12,y=14,f=1):
 paths={
 'plus':'M9 14H15M12 11V17','minus':'M9 14H15','check':'M8.5 14 11 16.5 15.5 11.5','x':'M9 11 15 17M15 11 9 17',
 'up':'M12 17V11M9 14 12 11 15 14','down':'M12 11V17M9 14 12 17 15 14','left':'M15 14H9M12 11 9 14 12 17','right':'M9 14H15M12 11 15 14 12 17',
 'info':'M12 11V16M12 9H12.01',
 'question':'M10 12A2 2 0 0 1 14 12C14 13.25 12 13.5 12 14.5V15M12 17H12.01',
 'lock':'M9 14H15V18H9ZM10.5 14V12A1.5 1.5 0 0 1 13.5 12V14',
 'search':'M14 16 16.5 18.5M14.5 13.5A2.5 2.5 0 1 1 9.5 13.5A2.5 2.5 0 1 1 14.5 13.5Z',
 'slash':'M10 17 14 11',
 'code':'M9.5 11 7.5 14 9.5 17M14.5 11 16.5 14 14.5 17M13 10 11 18',
 'download':'M12 10V17M9 14 12 17 15 14','upload':'M12 18V11M9 14 12 11 15 14',
 'edit':'M8.5 17.5 9.2 14.2 14 9.5 16.5 12 11.7 16.8ZM12.8 10.7 15.3 13.2',
 'refresh':'M9 14A3 3 0 0 1 14 11.5L15 12M15 14A3 3 0 0 1 10 16.5L9 16M12.5 12H15V9.5M11.5 16H9V18.5',
 'attachment':'M10 12V16A2 2 0 0 0 14 16V11A1 1 0 0 0 12 11V16',
 'dollar':'M14.5 11.5C14 10 10 10 10 12C10 14 14 13.5 14 15.5C14 17.5 10 17.5 9.5 16M12 9V19',
 'zap':'M12.5 9 8.5 15H12L11.5 19 16 12.5H12.5Z',
 }
 if kind=='heart':r=resize(ref('heart'),.38,12-12*.38,14-12*.38)
 elif kind=='shield':r=resize(pilot('shield-tick'),.43,12-12*.43,14-12*.43);r.remove(list(r)[-1])
 elif kind=='smile':r=svg(p('M8.5 13A3.5 3.5 0 0 0 15.5 13'),c(9,10.5,.2),c(15,10.5,.2))
 elif kind=='dots':r=svg(c(8.5,14,.25),c(12,14,.25),c(15.5,14,.25))
 elif kind=='bar':r=svg(p('M9 18V14M12 18V10M15 18V12'))
 else:r=svg(p(paths.get(kind,paths['plus'])))
 g.apply(r,f,f,x-12*f,y-14*f);return children(r)

def modifier(base):
 for v in ['info','question','attachment','download','upload','shield','refresh','heart','search','minus','check','plus','lock','edit','dollar','zap','dots','smile','code','down','left','right','up','x']:
  if v in base.split('-')[1:]:return v
 return None

def frame(x=3,y=3,w=18,h=18,curve='TLBR',r=3):
 k=set(re.findall('TL|TR|BR|BL',curve));r=min(r,w/2,h/2)
 d=f'M{x+r if "TL" in k else x} {y}H{x+w-r if "TR" in k else x+w}'
 if 'TR' in k:d+=f'A{r} {r} 0 0 1 {x+w} {y+r}'
 d+=f'V{y+h-r if "BR" in k else y+h}'
 if 'BR' in k:d+=f'A{r} {r} 0 0 1 {x+w-r} {y+h}'
 d+=f'H{x+r if "BL" in k else x}'
 if 'BL' in k:d+=f'A{r} {r} 0 0 1 {x} {y+h-r}'
 d+=f'V{y+r if "TL" in k else y}'
 if 'TL' in k:d+=f'A{r} {r} 0 0 1 {x+r} {y}'
 return p(d+'Z')

def message_base(notification=False):
 if notification:return svg(p('M15 4H3V13.5A3 3 0 0 0 6 16.5H14.5A4.5 4.5 0 0 1 18 18L20 20V8.5'),c(19.5,4.5,2))
 return svg(p('M3 4H17A3 3 0 0 1 20 7V20L18 18A4.5 4.5 0 0 0 14.5 16.5H6A3 3 0 0 1 3 13.5Z'))

def direct(base,old):
 # Exact examples reviewed by the user are the stable anchors for the full reconstruction.
 sample=ROOT/'staging/geometry-v2'/(base+'-lined.svg')
 if sample.exists():return E.parse(sample).getroot(),'reviewed-v2-sample'
 family=base.split('-')[0];mod=modifier(base)
 if family=='file':
  r=svg(p('M15 3H5.5V18A3 3 0 0 0 8.5 21H19.5V8ZM15 3V8H19.5'))
  if mod:r.extend(glyph(mod,12.5,14.5,.9))
  elif base in ['file-03','file-07']:r.extend(glyph('bar',12.5,14.5,.9))
  else:r.append(p('M9.5 13H15.5M9.5 16H13.5'))
  if base=='file-circle':r=svg(c(12,12,11),*children(resize(r,.66)))
  elif base in ['file-06','file-attachment-04','file-attachment-05']:
   small=resize(r,.86,1,1);r=svg(p('M8 2H18L22 6.5V19'),*children(small))
  return r,'brand-doc-lined'
 if family=='folder':
  r=svg(copy.deepcopy(list(pilot('folder-question'))[0]))
  if mod:r.extend(glyph(mod,12,13.5,.9))
  elif base=='folder-closed':r.extend([c(12,13.5,3),p('M10 11.5 14 15.5')])
  return r,'pilot/folder-question (reference container grammar)'
 if family=='calendar':
  r=svg(*children(pilot('calendar')))
  if mod:r.extend(glyph(mod,12,14,.95))
  elif base=='calendar-date':r.append(p('M10.5 12 12.5 10.5V17M10.5 17H14.5'))
  return r,'calendar'
 if family in ['message','annotation']:
  if 'chat' in base:return ref('brand-message-lined'),'brand-message-lined'
  r=message_base('notification' in base)
  if mod and mod!='notification':r.extend(glyph(mod,11.5,10.3,.8))
  elif 'text' in base:r.append(p('M6 8.5H16M6 11.5H14'))
  elif 'alert' in base:r.append(p('M11.5 7V11M11.5 13H11.51'))
  return r,'message (live-stroke reconstruction)'
 if family=='user':
  r=copy.deepcopy(pilot('user-01'))
  if mod:
   r=svg(c(8.5,7.5,3.5),p('M2 20.5V19A6 6 0 0 1 8 13H10.5'),*glyph(mod,18.5,18,.95))
  elif 'circle' in base:r=svg(c(12,12,10),*children(resize(r,.7,12-12*.7,11-12*.7)))
  elif 'square' in base:r=svg(frame(),*children(resize(r,.7,12-12*.7,11-12*.7)))
  return r,'profile'
 if family=='users':
  if mod:
   r=svg(c(8.5,7.5,3.5),p('M14 4.5A3.5 3.5 0 1 1 14 10.5M2 20.5V19A6 6 0 0 1 8 13H10.5'),*glyph(mod,19,18.5,.95))
  else:r=copy.deepcopy(pilot('users-01'))
  return r,'brand-users2-lined / approved live arcs'
 if family=='shield':
  if mod=='off' or base=='shield-off':return E.parse(ROOT/'staging/batch-028/shield-off-lined.svg').getroot(),'brand-shield-lined with contour breaks'
  r=svg(copy.deepcopy(list(pilot('shield-tick'))[0]))
  if mod:r.extend(glyph(mod,12,11.7,.95))
  elif base=='shield-03':r.append(p('M12 3V21.5'))
  return r,'brand-shield-lined'
 if family=='home':
  # Keep source's meaningful window/smile variant; replace its outer shell with the reference house.
  rr=ref('brand-home-lined');parts=g.subpaths(list(rr)[0].get('d'));r=svg(p(parts[-1],'butt','miter'))
  if base=='home-04':r.append(c(12,13,3))
  elif base=='home-smile':r.append(p('M8 13.5A4.1 4.1 0 0 0 16 13.5'))
  elif base=='home-line':r.append(p('M8 17H16'))
  else:r.append(p(parts[0],'butt','miter'))
  return r,'brand-home-lined'
 if family=='monitor':
  if base=='monitor-05':
   r=svg(frame(2,4,12,11,'TLBR',2),p('M5 19H11M8 15V19'),frame(16,3,6,18,'TL',2),p('M18.5 7H19.5M18.5 10H19.5'))
  else:
   r=ref('brand-device-desktop-lined')
   if base=='monitor-03':r.append(p('M3 12.5H21'))
   if base=='monitor-04':r=svg(list(r)[0],p('M9 16V20H15V16'))
  return r,'brand-device-desktop-lined'
 if base.startswith('cpu-chip'):return copy.deepcopy(pilot('cpu-chip-01')),'brand-chip-lined (approved live reconstruction)'
 if base.startswith('book-open'):return copy.deepcopy(pilot('book-open-01')),'book (approved live reconstruction)'
 if base.startswith('book-closed'):return svg(frame(5,3,14,18,'BL',3),p('M5 17H19M8 17V3')),'brand-doc-lined'
 if family=='briefcase':
  r=ref('brand-briefcase-lined')
  if base.endswith('02'):r.append(p('M8 7V19M16 7V19'))
  return r,'brand-briefcase-lined'
 if family=='glasses':
  r=ref('brand-glasses-lined')
  if base.endswith('01'):
   for n in r:
    if n.get('d'):
     parts=g.subpaths(n.get('d'));n.set('d',''.join(d for d in parts if not d.startswith(('M3.43494','M20.5653'))))
  return r,'brand-glasses-lined'
 if family=='clock':
  if mod:
   r=svg(p('M12 22A10 10 0 1 1 22 12M11.5 6.5V12L15.5 14.5'),*glyph(mod,18.5,18.5,.9))
  else:
   r=ref('clock')
   if 'rewind' in base:r.extend(glyph('left',18,18,.8))
   if 'fast' in base:r.extend(glyph('right',18,18,.8))
   if 'snooze' in base:r.append(p('M17 17H21L17 21H21'))
   if 'stopwatch' in base:r.append(p('M9 1.5H15'))
  return r,'clock'
 if family=='alarm':
  r=svg(c(12,13,7.5),p('M4 4 1.5 6.5M20 4 22.5 6.5M5.5 20 3.5 22M18.5 20 20.5 22'))
  if mod:r.extend(glyph(mod,12,13,.9))
  elif 'off' in base:r.append(p('M3 3 21 21'))
  else:r.append(p('M11.5 8V13L15 15'))
  return r,'clock / bell rhythm'
 if family=='bell':
  r=ref('bell');body=g.subpaths(list(r)[0].get('d'))[-1]
  r=svg(p(body),p('M10 21H14' if base=='bell-02' else 'M9.27516 21C10.0014 21.6224 10.9553 22 12 22C13.0447 22 13.9986 21.6224 14.7248 21'))
  if 'ringing' in base:r.append(p('M2 6 1 9M22 6 23 9'))
  if 'off' in base:r.append(p('M3 3 21 21'))
  if mod in ['plus','minus']:r.extend(glyph(mod,20.5,4,.65))
  return r,'bell'
 if family=='flag':
  r=ref('flag')
  if base in ['flag-04','flag-05']:r.append(p('M8 12 19 16 8 20Z'))
  elif base=='flag-06':r.append(p('M13.5 5.5V12'))
  elif base=='flag-03':r=svg(p('M8 3V21M8 3H20L16 8.5 20 14H8Z'))
  return r,'flag'
 if family=='trophy':return ref('trophy'),'trophy'
 if family=='award':return ref('brand-award1-lined' if base=='award-03' else 'reward'),'brand-award1-lined / reward'
 if family=='graduation':return ref('brand-academic-lined'),'brand-academic-lined'
 if family=='medical':
  r=ref('medical')
  if 'circle' in base:r=svg(c(12,12,10),*children(resize(r,.6)))
  if 'square' in base:r=svg(frame(),*children(resize(r,.6)))
  return r,'medical'
 if family=='code':
  has_slash=base.endswith('02') or 'snippet-02' in base
  r=ref('brand-code-lined')
  if not has_slash:
   for n in r:
    if n.get('d'):n.set('d',''.join(d for d in g.subpaths(n.get('d')) if not d.startswith('M14.4963')))
  if 'circle' in base:r=svg(c(12,12,10),*children(resize(r,.6)))
  elif 'square' in base or 'browser' in base:r=svg(frame(),*children(resize(r,.6)))
  return r,'brand-code-lined'
 if family=='search':
  r=ref('search')
  if base.endswith('lg'):r=resize(r,1.08)
  if base.endswith('sm'):r=resize(r,.9)
  if 'refraction' in base:r.append(p('M10.5 6A4.5 4.5 0 0 1 15 10.5'))
  return r,'search'
 if family=='sun':
  if base=='sun':return ref('sun-lined'),'sun-lined'
 if family=='moon':
  r=ref('moon-02-lined')
  if 'star' in base:
   r=resize(r,.82,1.2,4);star=ref('brand-shine-lined');star=resize(star,.25,15.4,0);r.extend(children(star))
  return r,'moon-02-lined'
 if family=='wifi':
  rr=ref('wifi');r=svg(*[copy.deepcopy(n) for n in rr if n.tag.endswith('path')]);r.append(c(12,19.25,.25))
  if 'off' in base:r.append(p('M3 3 21 21'))
  return r,'wifi'
 if family=='face':
  if base=='face-smile':return ref('brand-smile-lined'),'brand-smile-lined'
  r=svg(c(12,12,10),c(8.68182,9.77277,.22727),c(15.2271,9.77277,.22727))
  mouths={'frown':'M9.28109 16C10.3686 14.568 13.6313 14.568 14.7189 16','sad':'M9 17A3.5 3.5 0 0 1 15 17','neutral':'M9 15H15','happy':'M8.5 13.5H15.5A3.5 3.5 0 0 1 8.5 13.5Z','wink':'M9.28109 14.249C10.3686 15.6809 13.6313 15.6809 14.7189 14.249','content':'M9.28109 14.249C10.3686 15.6809 13.6313 15.6809 14.7189 14.249'}
  mood=base.split('-')[-1]
  if mood in mouths:r.append(p(mouths[mood]))
  else:return None,None
  if mood in ['content','sad']:r.remove(list(r)[1]);r.remove(list(r)[1]);r.extend([p('M7 9.5A2 2 0 0 0 10.5 9.5M13.5 9.5A2 2 0 0 0 17 9.5')])
  if mood=='wink':r.remove(list(r)[2]);r.append(p('M13.5 10H16.5'))
  return r,'brand-smile-lined'
 if family in ['database'] or base=='data':
  r=ref('data')
  if base=='database-03':r=resize(r,.8,1.2,0);r.append(p('M12 17V21M4 21H20'));r.extend([c(12,21,.5),c(4,21,.25),c(20,21,.25)])
  return r,'data'
 if family in ['edit','pencil']:
  r=ref('edit-02')
  if base in ['edit-01','edit-04','edit-05']:r=resize(r,.78,1.5,1);r.append(p('M4 22H20'))
  if base=='edit-05':r.append(p('M3 7V20H15'))
  return r,'edit-02'
 if family in ['download','upload']:
  r=ref('download')
  if family=='upload':list(r)[0].set('d','M7 8L12 3L17 8M12 3V15')
  if 'cloud' in base:return None,None
  if base.endswith(('03','04')):r=svg(c(12,12,10),p('M12 17.5V6.5M6.5 12 12 6.5 17.5 12' if family=='upload' else 'M12 6.5V17.5M6.5 12 12 17.5 17.5 12'))
  return r,'download'
 if family in ['beaker']:
  return E.parse(ROOT/'staging/geometry-v2/beaker-02-lined.svg').getroot(),'brand-biotech-lined (live reconstruction)'
 if family=='line' and 'chart' in base or family=='trend':
  rr=ref('brand-chart-lined')
  if 'down' in base:g.apply(rr,1,-1,0,24)
  if base.endswith(('03','04')):rr=svg(frame(),*children(resize(rr,.67)))
  elif base.endswith('05'):rr=svg(c(12,12,10),*children(resize(rr,.6)))
  elif family=='line' and base.endswith('02'):rr.append(p('M18 4H22V8' if 'up' in base else 'M18 20H22V16'))
  return rr,'brand-chart-lined'
 if family=='rocket':
  rr=ref('brand-rocket-lined');g.apply(rr,.9,.9,1.2,1.2)
  # Preserve the launch direction while using the reference body, fins and capsule window.
  wrapper=g.el('g',transform='rotate(45 12 12)');wrapper.extend(children(rr));return svg(wrapper),'brand-rocket-lined'
 return None,None

def rebuild_source_containers(root,base):
 # New containers inherit the two opposite rounded corners of ref/calendar and ref/device.
 changes=0
 for n in root.iter():
  if not n.get('d'):continue
  d,num=g.adapt_corners(n.get('d'),{'TL','BR'});n.set('d',d);changes+=num
 return changes

def main():
 import importlib.util
 exspec=importlib.util.spec_from_file_location('extensions',Path(__file__).with_name('v2-extensions.py'));extensions=importlib.util.module_from_spec(exspec);exspec.loader.exec_module(extensions)
 extensions.install(sys.modules.get(__name__) or sys.modules['__main__'])
 m=json.loads((ROOT/'manifest.json').read_text());prior=json.loads((ROOT/'review/reports/reference-series-authoring.json').read_text()) if (ROOT/'review/reports/reference-series-authoring.json').exists() else {};baseline=json.loads((ROOT/'specification/v2-source-baseline.json').read_text()) if (ROOT/'specification/v2-source-baseline.json').exists() else {};wanted=set(sys.argv[1:]);report=dict(prior) if wanted else {};out=ROOT/'staging/reference-series';out.mkdir(exist_ok=True)
 for i,icon in m['icons'].items():
  if icon['status']=='Approved' or wanted and i not in wanted:continue
  base=i.removesuffix('-lined');src=(ROOT/m['sources'][icon['source']]['path']).read_bytes();old=(ROOT/baseline.get(i,{}).get('path',icon['path'])).read_bytes()
  rr,anchor=direct(base,old)
  if rr is None:rr,anchor=extensions.direct(base,old)
  if rr is not None:method='reference-reconstruction'
  else:
   rr=E.fromstring(old);family=base.split('-')[0]
   # Containers which were missed in v1 are now rebuilt using explicit reference corner primitives.
   container=any(k in base for k in ['square','browser','grid','layout','building','battery','camera','wallet','server','keyboard','presentation','passcode','passport','luggage','briefcase','shopping-bag','tablet','laptop','mail','image','toggle','columns','rows','dice','film','safe','printer','tv','watch','briefcase','reorder'])
   count=extensions.reconstruct_rectangles(rr) if container else 0
   if not count and container:count=rebuild_source_containers(rr,base)
   if family in ['cube','package','box','diamond','bezier','brush','scissors','eraser','pen','ticket','truck','car','train','tram','bus','save','simcard','ruler','scale','scales','luggage','bank','certificate','receipt','film','tag']:
    sharp=extensions.sharpen_geometric_corners(rr);count+=sharp
   anchor='calendar / brand-device-desktop-lined / brand-home-lined' if count else 'geometry-review-required'
   method='reference-container-reconstruction' if count else 'retained-pending-family-review'
  rr.attrib.pop('xmlns',None);data=E.tostring(rr,encoding='utf-8')+b'\n';(out/(i+'.svg')).write_bytes(data)
  report[i]={'method':method,'reference':anchor,'previous_path':baseline.get(i,{}).get('path',icon['path']),'previous_sha256':baseline.get(i,{}).get('sha256',icon['sha256']),'candidate':str((out/(i+'.svg')).relative_to(ROOT))}
 (ROOT/'review/reports/reference-series-authoring.json').write_text(json.dumps(report,indent=2)+'\n')
 from collections import Counter
 print(Counter(x['method'] for x in report.values()))
if __name__=='__main__':main()
