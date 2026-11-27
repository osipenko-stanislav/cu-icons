from pathlib import Path
from importlib.machinery import SourceFileLoader
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
import json,math,hashlib,xml.etree.ElementTree as E,resvg_py
P=Path('icon-project');R=P/'review/motion/ref-refinements-2026-11-27';d=json.loads((R/'browser-checks.json').read_text());assert not d['errors'] and not [c for c in d['checks'] if any(v is False for v in c.values())]
scenes={s['id']:s for s in json.loads((P/'motion/reference-series/motion.json').read_text())['scenes']};targets={'ref-shower','ref-steam','ref-kitchen','ref-bio','ref-bed','ref-brand-network'}
M=SourceFileLoader('verify_ref_properties',str(P/'tools/retarget-motion-library.py')).load_module()
for id,sign in [('ref-shower',1),('ref-steam',-1)]:
 data=scenes[id]['tracks'][0][7]['animationData']
 for layer in data['layers']:
  for group in layer['shapes']:
   tr=group['it'][-1]
   if not tr.get('p',{}).get('a'):continue
   previous=None
   for i in range(301):
    t=i/300*data['op'];y=M.evaluate(tr['p'],t)[1];alpha=M.evaluate(tr['o'],t)[0]
    if previous and alpha>1 and previous[1]>1:assert (y-previous[0])*sign>=-1e-4,(id,t)
    previous=(y,alpha)
cut=scenes['ref-kitchen']['tracks'];assert not any(t[1] in ['draw','erase-redraw'] for t in cut);assert all(t[2]<0 for t in cut if t[0] in [1,4]);assert all(t[2]>0 for t in cut if t[0] in [2,3]);assert cut[0][2:]==cut[1][2:] and cut[2][2:]==cut[3][2:]
bio=scenes['ref-bio']['tracks'][0][7]['animationData']['layers'][0]['shapes'];shape=lambda g:g['it'][0]['ks']
def center(path):return [(min(v[a] for v in path['v'])+max(v[a] for v in path['v']))/2 for a in [0,1]]
for i in range(6):
 original=M.evaluate(shape(bio[i]),0)[0];outer=max(range(2),key=lambda j:math.dist(original['v'][j],[12,12]));node=min(range(7,13),key=lambda j:math.dist(original['v'][outer],center(M.evaluate(shape(bio[j]),0)[0])));offset=[original['v'][outer][a]-center(M.evaluate(shape(bio[node]),0)[0])[a] for a in [0,1]]
 for f in range(49):
  edge=M.evaluate(shape(bio[i]),f)[0];c=center(M.evaluate(shape(bio[node]),f)[0]);assert max(abs(edge['v'][outer][a]-c[a]-offset[a]) for a in [0,1])<.00015
bed=scenes['ref-bed']['tracks'][0][7]['animationData']['layers'][0]['shapes'];assert not shape(bed[0])['a'] and not shape(bed[1])['a'];mattress=shape(bed[2]);base=M.evaluate(mattress,0)[0]
for f in range(49):
 p=M.evaluate(mattress,f)[0]
 for j,v in enumerate(base['v']):
  if abs(v[1]-17.5789)<.0001:assert math.dist(v,p['v'][j])<.0001
network=scenes['ref-brand-network']['tracks'][0][7]['animationData']['layers'][0]['shapes'];assert all(not shape(g)['a'] for g in network[:5]);assert all(abs(M.evaluate(g['it'][-1]['o'],0)[0])<1e-6 and abs(M.evaluate(g['it'][-1]['o'],48)[0])<1e-6 for g in network[5:])
original=json.loads((P/'review/motion/ref-weather-2026-11-27/authoring.json').read_text())['other_scene_hashes'];assert all(hashlib.sha256(json.dumps(scenes[id],sort_keys=True).encode()).hexdigest()==h for id,h in original.items() if id not in targets)
# Contact sheet uses half-unit strokes at 48px to represent the gallery's 1px line.
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',12);ids=['ref-shower','ref-steam','ref-kitchen','ref-bio','ref-bed','ref-brand-network'];im=Image.new('RGB',(1000,660),'white');draw=ImageDraw.Draw(im)
for row,id in enumerate(ids):
 y=row*110;draw.text((8,y+10),id,font=font,fill='#111')
 for col,f in enumerate(f for f in d['frames'] if f['id']==id):
  root=E.fromstring(f['svg'])
  for n in root.iter():
   if n.tag.split('}')[-1] in ['path','circle','ellipse','line','rect','polygon','polyline']:n.set('stroke-width','.5')
  sprite=Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=E.tostring(root).decode(),skip_system_fonts=True))).convert('RGBA');im.paste(sprite,(150+col*116,y+15),sprite);draw.text((162+col*116,y+72),str(round(f['t']*100))+'%',font=font,fill='#777')
 draw.line((0,y+109,1000,y+109),fill='#ddd')
im.save(R/'frames.png');(R/'structure-checks.json').write_text(json.dumps({'weather_visible_direction':'pass','cutlery_opposite_direction_and_coherent_parts':'pass','bio_all_bond_endpoints_attached':'pass','bed_posts_and_baseline_fixed':'pass','network_graph_fixed_and_accents_hidden_at_rest':'pass','all_other_scenes_unchanged':'pass','browser_checks':len(d['checks']),'browser_errors':d['errors']},indent=2)+'\n');print('Structural checks passed; six-scene contact sheet rendered')
