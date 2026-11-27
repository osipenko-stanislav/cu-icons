"""Additional semantic recipes for the remaining user-reported motion groups."""
import copy,math
from pathlib import Path

def author(A,id,es):
 G=A['G'];V=A['V'];N=A['N'];prop=A['prop'];wave=A['wave'];group=A['group'];layer=A['layer'];box=A['box'];ctr=A['ctr'];glyph_parts=A['glyph_parts'];family=id.split('-')[0];layers=None;behavior='hover-replay';description=''
 def static(items):return group(items)
 def trace(items,delay=0):
  g=group(items)
  def start(t):
   u=max(0,min(1,(t-delay)/max(.1,1-delay)));return 100*min(1,u/.4) if u<.45 else 0
  def end(t):
   u=max(0,min(1,(t-delay)/max(.1,1-delay)));return 100 if u<.45 else 100*min(1,(u-.45)/.4)
  g['it'].insert(-1,{'ty':'tm','s':prop(lambda t:[start(t)]),'e':prop(lambda t:[end(t)]),'o':V(0),'m':1});return g
 def warp(path,fn):
  out=copy.deepcopy(path)
  for i,v in enumerate(path['v']):
   q=fn(v);out['v'][i]=q
   for h in ['i','o']:
    p=fn([v[a]+path[h][i][a] for a in [0,1]]);out[h][i]=[p[a]-q[a] for a in [0,1]]
  return out
 def deform(items,fn):
  groups=[]
  for e in items:
   g=G.paint_group(e);g['it'][0]['ks']=prop(lambda t,e=e:[warp(e['path'],lambda p:fn(p,t))]);groups.append(g)
  return groups
 def circle(x,y,r):return G.extract(f'<svg xmlns="http://www.w3.org/2000/svg"><circle cx="{x}" cy="{y}" r="{r}" fill="currentColor"/></svg>'.encode())[0]
 def trace_signal(items):
  # Keep the complete graph readable and send highlights through its parts.
  return [group([e],opacity=lambda t,i=i:100-45*wave(t,(i%5)*.07,.65+(i%5)*.07)) for i,e in enumerate(items)]
 def scale_gesture(items,amount=.035,pivot=(12,12)):return group(items,scale=lambda t:[1+amount*wave(t)]*2,pivot=pivot)
 def source(name):
  raw=(Path('work')/(name+'.svg')).read_bytes();out=G.extract(raw)
  for e in out:
   for k in ['stroke','fill']:
    if e['style'].get(k) not in ['none',None,'transparent']:e['style'][k]='currentColor'
  return out
 if family=='bar':
  bars=[e for e in es if len(e['path']['v'])==2 and box(e)[2]-box(e)[0]<.01 and box(e)[3]-box(e)[1]>1];fixed=[e for e in es if e not in bars];layers=[layer([static(fixed)]+[group([e],scale=lambda t,i=i:[1,1+.12*wave(t,i*.08,.75+i*.08)],pivot=(ctr(e)[0],box(e)[3])) for i,e in enumerate(bars)])];description='Chart axes and linked trend stay fixed; bars respond from their shared baseline.'
 elif family=='delete':
  fixed,moving=glyph_parts(es);layers=[layer([static(fixed),scale_gesture(moving,.12)])];behavior='click-replay';description='A local delete-sign response inside the stable backspace frame; no false deletion state.'
 elif family=='bookmark':
  fixed,moving=glyph_parts(es);outer=max((e for e in es if e['path']['c']),key=lambda e:(box(e)[2]-box(e)[0])*(box(e)[3]-box(e)[1]));positive=any(x in id for x in ['add','check']);g=G.paint_group(outer,force='fill');g['it'][-1]['o']=prop(lambda t:[100*t*t*(3-2*t) if positive else 0]);layers=[layer([{'ty':'gr','it':[g,copy.deepcopy(G.IDENTITY_TRANSFORM)]},static(fixed),group(moving,opacity=lambda t:100*(1-t*t*(3-2*t)))])];behavior='click-toggle';description='Bookmark state changes on its own silhouette; action badge fades coherently without distorting the contour.'
 elif family in ['camera','eye','video']:
  off='off' in id;names={'camera':'camera-01-lined','eye':'eye-lined','video':'video-recorder-lined'};on=source(names[family])
  if not off:
   on=es;slash=G.extract(b'<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor"><path d="M3 3L21 21" stroke-linecap="round"/></svg>');target=on+slash
  else:target=on
  layers=A['morph_state'](es,target);behavior='click-toggle';description='Two explicit on/off states on own artwork; the slash is a state sign, not a drifting construction fragment.'
 elif family in ['play','pause']:
  fixed,glyph=glyph_parts(es)
  if not glyph:glyph=es;fixed=[]
  target=G.extract((b'<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor"><path d="M9 7V17M15 7V17" stroke-linecap="round"/></svg>') if family=='play' else b'<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor"><path d="M9 6L18 12L9 18Z" stroke-linejoin="round"/></svg>')
  layers=[layer([static(fixed),group(glyph,opacity=lambda t:100*(1-min(1,max(0,(t-.2)/.4)))),group(target,opacity=lambda t:100*min(1,max(0,(t-.3)/.4)))])];behavior='click-toggle';description='Actual play/pause pair; the frame is fixed and both glyphs stay readable through the transition.'
 elif family=='menu':
  bars=sorted(es,key=lambda e:ctr(e)[1]);groups=[]
  for i,e in enumerate(bars):
   c=ctr(e);g=group([e]);tr=g['it'][-1]
   if i==len(bars)//2:tr['o']=prop(lambda t:[100*(1-t*t*(3-2*t))])
   else:
    sign=1 if i==0 else -1;tr.update(a=V(c),p=prop(lambda t,c=c:[c[0],c[1]+(12-c[1])*t*t*(3-2*t)]),r=prop(lambda t,sign=sign:[sign*45*t*t*(3-2*t)]))
   groups.append(g)
  layers=[layer(groups)];behavior='click-toggle';description='Menu bars form a coherent close symbol; reverse playback restores the menu.'
 elif family in ['hearts','star','stars']:
  groups=[static(es)]
  for e in es:
   if not e['path']['c']:continue
   g=G.paint_group(e,force='fill');g['it'][-1]['o']=prop(lambda t:[100*t*t*(3-2*t)]);groups.append({'ty':'gr','it':[g,copy.deepcopy(G.IDENTITY_TRANSFORM)]})
  layers=[layer(groups)];behavior='click-toggle';description='Fill transition uses the original closed silhouettes and preserves the number of symbols.'
 elif family in ['bezier','arrows'] or id=='reorder-lined':
  if id=='reorder-lined':
   groups=[group([e],move=lambda t,i=i:[(.5 if i%2==0 else -.5)*wave(t,min(.2,i*.035),1),0]) for i,e in enumerate(es)];description='Restore the earlier staggered grip movement.'
  else:groups=[trace([e],(i%3)*.07) for i,e in enumerate(es)];description='User-requested stroke treatment on the editable original paths.'
  layers=[layer(groups)]
 elif family=='compass':
  if id=='compass-lined':
   groups=[group([e],rotate=lambda t,i=i:(-4 if i%2==0 else 4)*wave(t),pivot=(ctr(e)[0],max(3,box(e)[1]))) for i,e in enumerate(es)];description='Restore a small articulated compass-opening gesture instead of whole-object distortion.'
  else:
   fixed,moving=glyph_parts(es);layers=[layer([static(fixed),group(moving or es,rotate=lambda t:20*math.sin(t*math.pi*2)*wave(t))])];description='Compass needle reacts around its center; dial remains anchored.'
  if layers is None:layers=[layer(groups)]
 elif family in ['activity','dataflow','git','share','signal','old','codepen']:
  layers=[layer(trace_signal(es))];behavior='hover-loop' if family in ['activity','signal'] else 'hover-replay';description='Signal progresses through the existing parts with phases; graph topology and symbol count remain fixed.'
 elif family in ['align','distribute','spacing','expand','transform','switch']:
  horizontal='horizontal' in id or 'width' in id or 'left' in id or 'right' in id;axis=0 if horizontal else 1;groups=[]
  for e in es:
   b=box(e);c=ctr(e);is_frame=(e['path']['c'] and b[2]-b[0]>15 and b[3]-b[1]>15) or (family in ['align','distribute','spacing'] and ((axis==0 and b[2]-b[0]<.05 and b[3]-b[1]>8) or (axis==1 and b[3]-b[1]<.05 and b[2]-b[0]>8)))
   if is_frame:groups.append(static([e]));continue
   if family in ['expand','transform']:groups.append(scale_gesture([e],.045));continue
   if family=='spacing':groups.append(group([e],scale=lambda t,axis=axis:[1+.045*wave(t) if axis==0 else 1,1+.045*wave(t) if axis==1 else 1]));continue
   sign=-1 if c[axis]<12 else 1
   if family=='align':
    if ('left' in id or 'top' in id):sign=-1
    elif 'center' in id or 'centre' in id:sign=-sign
    elif 'right' in id or 'bottom' in id:sign=1
   if family=='switch':axis=1;sign=-1 if c[0]>12 else 1
   groups.append(group([e],move=lambda t,axis=axis,sign=sign:[sign*.75*wave(t) if axis==0 else 0,sign*.75*wave(t) if axis==1 else 0]))
  layers=[layer(groups)];description='Parts move along the operation axis; enclosing frames stay anchored.'
 elif family in ['colors','contrast','diamond','fingerprint','medical']:
  layers=[layer([group(es,rotate=lambda t:360*t)])];behavior='hover-loop';description='Coherent complete rotation forms a seamless hover cycle; artwork never deforms fragment by fragment.'
 elif family=='cpu':
  cores=[e for e in es if e['path']['c'] and 4<box(e)[2]-box(e)[0]<12];fixed=[e for e in es if e not in cores];layers=[layer([static(fixed),scale_gesture(cores,.075)])];description='Processor core pulses inside a stable chip body; pins never detach.'
 elif family=='hurricane' and id!='hurricane-02-lined':
  layers=[layer([group([e],move=lambda t,i=i:[.55*math.sin(t*math.pi*2+i*.4)*wave(t),0]) for i,e in enumerate(es)])];description='Wind bands respond in phases while the vertical funnel stays legible.'
 elif family in ['dice','disc','cryptocurrency','eagle','hurricane']:
  angle=8 if family=='dice' else 10 if family in ['disc','cryptocurrency'] else 6
  layers=[layer([group(es,rotate=lambda t:angle*math.sin(t*math.pi*2)*wave(t))])];description='One coherent rotational response; pips, internal symbols and joined contours stay attached.'
 elif family in ['data','database','coins','divider','dots','droplets','grid']:
  groups=[]
  for i,e in enumerate(es):
   b=box(e);large=b[3]-b[1]>12
   if large:groups.append(static([e]));continue
   if family=='dots':groups.append(group([e],move=lambda t,i=i:[(.65 if i%2 else -.65)*wave(t,(i%3)*.1,.75+(i%3)*.1),0]))
   elif family=='droplets':groups.append(group([e],move=lambda t,i=i:[0,.6*wave(t,(i%3)*.13,.7+(i%3)*.13)]))
   else:groups.append(trace([e],min(.3,i*.07)))
  layers=[layer(groups)];description='Sequential detail response; container/large envelope stays intact and every original element remains represented.'
 elif family in ['folder','archive']:
  front=max(es,key=lambda e:(box(e)[2]-box(e)[0])*(box(e)[3]-box(e)[1]) if e['path']['c'] else -1);b=box(front);moving=[e for e in es if e is front or (box(e)[0]>=b[0] and box(e)[2]<=b[2] and box(e)[1]>=b[1] and box(e)[3]<=b[3] and e['path']['c'])];fixed=[e for e in es if e not in moving]
  # Every small badge below the top edge belongs to the same front plane.
  for e in list(fixed):
   eb=box(e)
   if eb[2]-eb[0]<8 and eb[3]-eb[1]<8 and eb[1]>b[1]+1:moving.append(e);fixed.remove(e)
  layers=[layer([static(fixed),group(moving,scale=lambda t:[1,1-.09*t*t*(3-2*t)],pivot=(12,b[3]))])];behavior='hover';description='Front plane opens together with its badge, so question/code signs stay inside it.'
 elif family in ['brush','eraser','car','bus','train','download']:
  if family=='download':
   fixed=[e for e in es if box(e)[1]>14 and box(e)[2]-box(e)[0]>10];moving=[e for e in es if e not in fixed];layers=[layer([static(fixed),group(moving,move=lambda t:[0,1.3*wave(t)])])];behavior='click-replay';description='Download arrow moves downward; tray stays anchored without implying successful network completion.'
  else:layers=[layer([group(es,move=lambda t:[.9*wave(t),0])])];description='Short movement consistent with a tool stroke or travel; all construction parts stay together.'
 elif family in ['battery','announcement','alert','award','book','check','filter','lightbulb','pie','placeholder','scales','settings','sticker','sun','user','zoom']:
  if family=='scales':
   layers=[layer(deform(es,lambda p,t:[p[0],p[1]+.65*wave(t)*max(-1,min(1,(p[0]-12)/2))]))];description='Balance pans move oppositely with a shared deformation that preserves every junction.'
  elif family=='pie':
   fixed=[e for e in es if e['path']['c'] and box(e)[2]-box(e)[0]>15];moving=[e for e in es if e not in fixed];layers=[layer([static(fixed),group(moving,rotate=lambda t:8*wave(t))])];description='Interior sectors react around the center while the outer chart stays fixed.'
  elif family=='user':
   fixed,moving=glyph_parts(es);layers=[layer([group(fixed,opacity=lambda t:100-60*t*t*(3-2*t)),group(moving,scale=lambda t:[1+.1*t*t*(3-2*t)]*2,pivot=(18,17))])];behavior='hover';description='Hover focuses the action badge while retaining user context; no false success state.'
  elif family=='sticker':
   layers=[layer(deform(es,lambda p,t:[p[0]-.7*wave(t)*max(0,(p[0]+p[1]-25)/15),p[1]-.45*wave(t)*max(0,(p[0]+p[1]-25)/15)]))];description='A local peel hint bends the own corner continuously, rather than morphing into an unrelated bookmark.'
  elif family in ['filter','settings']:
   knobs=[e for e in es if e['path']['c'] and abs((box(e)[2]-box(e)[0])-(box(e)[3]-box(e)[1]))<.05 and 4<box(e)[2]-box(e)[0]<8]
   if knobs:
    layers=[]
    for knob in knobs:
     cx,cy=ctr(knob);delta=24-2*cx
     if id=='settings-03-lined':guide=G.extract(f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor"><rect x="3" y="{cy-2.5}" width="18" height="5" rx="2.5"/></svg>'.encode())[0]
     else:guide=G.extract(f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor"><path d="M3 {cy}H21"/></svg>'.encode())[0]
     for e in [guide]:e['style']['stroke-linecap']='round';e['style']['stroke-linejoin']='round'
     def shift(path,t):return G.transform_path(path,[1,0,0,1,delta*t*t*(3-2*t),0])
     track=layer([static([guide])]);track.update(hasMask=True,masksProperties=[{'inv':False,'mode':'s','pt':prop(lambda t,knob=knob,delta=delta:[G.transform_path(knob['path'],[1,0,0,1,delta*t*t*(3-2*t),0])]),'o':V(100),'x':V(0),'nm':'Own moving knob occludes its guide'}]);
     if id!='settings-03-lined':
      segments=[]
      for left in [True,False]:
       g=G.paint_group(guide);r=(box(knob)[2]-box(knob)[0])/2
       g['it'][0]['ks']=prop(lambda t,left=left,cx=cx,cy=cy,r=r,delta=delta:[G.bezier_paths(f'M{3 if left else cx+delta*t*t*(3-2*t)+r} {cy}H{cx+delta*t*t*(3-2*t)-r if left else 21}')[0]])
       segments.append(g)
      track=layer(segments)
     layers.append(track);layers.append(layer([group([knob],move=lambda t,delta=delta:[delta*t*t*(3-2*t),0])]))
    behavior='click-toggle';description='Round knobs move along fixed guides; subtractive masks keep the track out of their interiors.'
   else:layers=[layer(trace_signal(es))];description='Filter lines respond in sequence without collapsing the frame or changing line count.'
  elif family=='book':
   layers=[layer([group(es,scale=lambda t:[1-.045*wave(t),1],pivot=(12,21))])];description='Slightly stronger approved squeeze; no new or turning pages.'
  elif family=='sun':
   fixed=[e for e in es if box(e)[1]>=16];moving=[e for e in es if e not in fixed];layers=[layer([static(fixed)]),layer([group(moving,move=lambda t:[0,.7*wave(t)])],G.bezier_paths('M0 0H24V15H0Z')[0])];description='Sun moves behind the stationary horizon with its rays; the horizon masks the movement.'
  elif family=='placeholder':
   layers=[layer([group(es,scale=lambda t:[1+.05*wave(t)]*2)])];description='Visible restrained response replaces the imperceptible default motion.'
  elif id=='check-verified-01-lined':
   fixed,moving=glyph_parts(es);outer=group([],scale=lambda t:[1+.05*wave(t,.6,1)]*2);outer['it']=[static(fixed),group(moving,scale=lambda t:[1+.08*wave(t,.05,.65)]*2),outer['it'][-1]];layers=[layer([outer])];description='Check reacts first, followed by the requested final star-badge emphasis.'
  elif family in ['lightbulb','battery','announcement','alert','award','check']:
   fixed,moving=glyph_parts(es)
   if not moving:moving=es;fixed=[]
   groups=[static(fixed)]+[group([e],scale=lambda t,i=i:[1+.08*wave(t,(i%3)*.06,.8+(i%3)*.06)]*2,pivot=ctr(e)) for i,e in enumerate(moving)];layers=[layer(groups)];description='Emphasize the meaningful internal detail; preserve stable frame and modifier count.'
  else:layers=[layer([scale_gesture(es,.035)])];description='One controlled semantic response without unrelated morphing or fragmentation.'
 else:return None
 return layers,behavior,description
