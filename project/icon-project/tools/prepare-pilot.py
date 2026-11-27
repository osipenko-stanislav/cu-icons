from pathlib import Path
import json, re, xml.etree.ElementTree as E
root=Path('icon-project'); out=root/'staging/pilot';out.mkdir(parents=True,exist_ok=True)
# Explicit geometry, authored for this pilot; existing source retained only where compatible.
def path(d,cap='round',join='round'):
 return f'<path d="{d}" stroke-linecap="{cap}" stroke-linejoin="{join}"/>'
def circle(x,y,r,filled=False):
 return f'<circle cx="{x}" cy="{y}" r="{r}"'+(' fill="currentColor" stroke="none"' if filled else '')+'/>'
def save(n,body):
 (out/(n+'-lined.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">\n'+body+'\n</svg>\n')
P={}
P['arrow-left']=path('M22 12H2M12 2 2 12 12 22')
P['arrow-right']=path('M2 12H22M12 2 22 12 12 22')
# Source silhouette already identical in character to ref/heart; keep source editable centerline.
heart=E.parse('work/heart-lined.svg').getroot()[0].get('d')
P['heart']=path(heart)
# Keep the plain-house meaning of home-01 (no door), with the reference pitched roof and straight base.
P['home-01']=path('M4 11 12 3 20 11V21H4Z','butt','miter')
filebase='M19.5 3H5.5V18A3 3 0 0 0 8.5 21H19.5Z'
filetext='M9 8H16M9 12H14M9 16H11'
P['file-02']=path(filebase)+path(filetext)
P['file-plus-02']=path('M19.5 10V3H5.5V18A3 3 0 0 0 8.5 21H11.5')+path(filetext)+path('M18 15V21M15 18H21')
calbase='M20.5 3.5H6.5A3 3 0 0 0 3.5 6.5V20.5H17.5A3 3 0 0 0 20.5 17.5Z'
P['calendar']=path(calbase)+path('M3.5 7.5H20.5','butt')
# The unmarked source calendar has no date dots; keep date-grid as a distinct existing variant.
P['calendar-check-01']=P['calendar']+path('M8 14 11 17 16 11.5')
P['monitor-01']=path('M21.5 3.5H5.5A3 3 0 0 0 2.5 6.5V16H18.5A3 3 0 0 0 21.5 13Z')+path('M6 20.5A2 2 0 0 1 8 18.5H16A2 2 0 0 1 18 20.5Z')
P['cpu-chip-01']=path('M19 5H8A3 3 0 0 0 5 8V19H19Z')+path('M16 8H10A2 2 0 0 0 8 10V16H16Z')+path('M9 2V5M15 2V5M9 19V22M15 19V22M2 9H5M2 15H5M19 9H22M19 15H22')
userbody='M4.5 19A6 6 0 0 1 10.5 13H13.5A6 6 0 0 1 19.5 19V20.5H4.5Z'
P['user-01']=path(userbody,'butt','miter')+circle(12,7.5,3.5)
# Back person is drawn as live arcs with deliberate breaks; no expanded-stroke knockouts.
P['users-01']=path('M14.5 4.5A3.5 3.5 0 1 1 14.5 10.5M16.5 13A6 6 0 0 1 22.5 19V20.5H18.5','butt')+path('M1.5 19A6 6 0 0 1 7.5 13H10.5A6 6 0 0 1 16.5 19V20.5H1.5Z','butt')+circle(9,7.5,3.5)
P['users-plus']=circle(8.5,7.5,3.5)+path('M14 4.5A3.5 3.5 0 1 1 14 10.5M2 20.5V19A6 6 0 0 1 8 13H10.5M19 15V22M15.5 18.5H22.5')
# Keep the left-facing message tail from source; ref/message has the mirrored metaphor.
msg='M3.5 3.5H17.5A3 3 0 0 1 20.5 6.5V13.5A3 3 0 0 1 17.5 16.5H9A4.5 4.5 0 0 0 5.5 18L3.5 20.5Z'
P['message-square-01']=path(msg)
P['message-text-square-01']=path(msg)+path('M7 8H12M7 11.5H16')
P['shield-tick']=path('M4 3H20V13.5A5 5 0 0 1 17.8 17.65L12 21.5 6.2 17.65A5 5 0 0 1 4 13.5Z')+path('M8 11.5 11 14 16 8')
# Retain diagonal launch orientation and propulsion trace from the existing source.
P['rocket-01']='<g transform="rotate(45 12 12)">'+path('M7.5 17.5V10A7 7 0 0 1 9.55 5.05L12 2.6 14.45 5.05A7 7 0 0 1 16.5 10V17.5Z','butt','miter')+path('M8 7.5H16M7.5 13A4.5 4.5 0 0 0 4.5 17.25V20L7.5 17.5M16.5 13A4.5 4.5 0 0 1 19.5 17.25V20L16.5 17.5M12 17.5V22','butt','miter')+'</g>'
P['book-open-01']=path('M12 6A5 5 0 0 0 7.5 3.5H2V16.5A2.5 2.5 0 0 0 4.5 19H8A4 4 0 0 1 10.5 19.9L12 21 13.5 19.9A4 4 0 0 1 16 19H19.5A2.5 2.5 0 0 0 22 16.5V3.5H16.5A5 5 0 0 0 12 6ZM12 6V21','butt','miter')
P['bell-01']=path('M9.25 21A4.25 4.25 0 0 0 14.75 21M6 8A6 6 0 0 1 18 8C18 12 19 14.5 21 17H3C5 14.5 6 12 6 8Z')
P['trash-01']=path('M9 5.5V4.5A1.5 1.5 0 0 1 10.5 3H13.5A1.5 1.5 0 0 1 15 4.5V5.5M4 6H20M5 6 6.5 21H17.5L19 6M10 11V16M14 11V16')
P['credit-card-lock']=path('M21.5 11V5H5.5A3 3 0 0 0 2.5 8V18.5H11M2.5 9.5H21.5')+path('M15 17.5H22V21.5H15ZM16.5 17.5V15.5A2 2 0 0 1 20.5 15.5V17.5')
P['folder-question']=path('M3 7V3.5H9.5A2 2 0 0 1 11.3 4.6L12.5 7M3 7H18A3 3 0 0 1 21 10V20.5H6A3 3 0 0 1 3 17.5Z')+path('M10 11.5A2 2 0 0 1 14 11.5C14 13 12 13 12 14.5')+circle(12,17,0.5,True)
# No exact gear reference: retain eight teeth with an evenly spaced geometric outline.
import math
points=[]
for tooth in range(8):
 for offset,r in [(-18,7.5),(-8,10),(8,10),(18,7.5)]:
  a=math.radians(-90+tooth*45+offset); points.append(f'{12+r*math.cos(a):.3f} {12+r*math.sin(a):.3f}')
P['settings-01']=path('M'+'L'.join(points)+'Z')+circle(12,12,3)
P['cloud-raining-01']=path('M4 15.5A4.5 4.5 0 0 1 6 7 6 6 0 0 1 18 7 4.5 4.5 0 0 1 20 15.5M8 12V14M8 18V20M12 14V16M12 20V22M16 12V14M16 18V20')
P['rocket-01']=P['rocket-01'].replace('stroke-linejoin="miter"','stroke-linejoin="round"')
for n,b in P.items():save(n,b)
pilot=[n+'-lined' for n in P]
(root/'pilot-ids.json').write_text(json.dumps(pilot,indent=2)+'\n')
# Every source gets a stable entry, original filename mapping and an inferred family.
manifest=json.loads((root/'manifest.json').read_text()); entries=[]
for identifier,src in manifest['sources'].items():
 base=identifier.removesuffix('-lined'); tokens=base.split('-'); fam='-'.join(tokens[:2]) if tokens[0] in ['credit','bar','line','marker','cpu','book'] else tokens[0]
 modifier=next((t for t in tokens if t in ['plus','minus','check','x','lock','question','heart','shield','off','up','down','left','right']),None)
 entry={'id':identifier,'name':base.replace('-',' ').title(),'meaning':'Preserve the metaphor and variant in work/'+Path(src.get('name',identifier+'.svg')).name,'category':fam,'family':fam,'geometry':'outline','metaphor':fam,'source':identifier}
 if modifier:entry['modifier']=modifier
 entries.append(entry)
(root/'specification/registry.json').write_text(json.dumps(entries,indent=2,ensure_ascii=False)+'\n')
style={'version':'cu-ref-1.0','draft':False,'default_geometry':'outline','profiles':{},'exceptions':{'folder-question-lined':{'reason':'Question dot is a small filled accent; principal contours remain live strokes.','rules':{'allow_outline_fills':True}}},'target_sizes':[16,24,32],'rules':{'viewbox':[0,0,24,24],'canvas':['24','24'],'stroke_widths':[1],'caps':['round','butt'],'joins':['round','miter'],'colors':['currentColor'],'current_color':True,'transforms':True,'work_area':[0.5,0.5,23.5,23.5],'max_precision':5,'opacities':[1]}}
(root/'specification/icon-style.json').write_text(json.dumps(style,indent=2)+'\n')
print('Pilot:',len(P),'Registry:',len(entries));print(','.join(pilot))
