from pathlib import Path
import json,copy,sys,importlib.util,xml.etree.ElementTree as E,hashlib
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT.parent;NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)
sp=importlib.util.spec_from_file_location('series',Path(__file__).with_name('produce-series.py'));s=importlib.util.module_from_spec(sp);sp.loader.exec_module(s)
def svg(*children):
 r=s.el('svg',width=24,height=24,viewBox='0 0 24 24',fill='none',stroke='currentColor',stroke_width=1);r.extend(children);return r
p=s.path;c=s.circle

def ref(name):
 r=E.parse(WORK/'ref'/(name+'.svg')).getroot();s.normalize(r)
 return r
specs={
 'code-02-lined':('brand-code-lined','Shorter angled brackets and slanted central slash follow the actual reference angles and spans.'),
 'search-md-lined':('search','Reference lens is centred at 10.5/10.5 with radius 7.5 and a longer handle.'),
 'sun-lined':('sun-lined','Central disc radius grows from 5 to 6; reference disc-to-ray gaps retained.'),
 'glasses-02-lined':('brand-glasses-lined','Diagonal temples, smaller/lower lenses and a narrow arched bridge replace near-vertical temples.'),
 'briefcase-01-lined':('brand-briefcase-lined','Reference handle, horizontal seam and opposing curved corners replace source rounded rectangle.'),
 'trash-02-lined':('trash','Tapered straight-sided body, narrow cap and low handle replace the U-shaped source bin.'),
 'flag-01-lined':('flag','Triangular pennant and pole at x8 replace the wavy rectangular flag, per explicit reference-priority decision.'),
 'trophy-01-lined':('trophy','Reference bowl proportions, separate side strokes and straight stem replace handles and heavy pedestal.'),
 'award-01-lined':('reward','Reference medallion with the CU four-point star and a continuous ribbon base.'),
 'edit-02-lined':('edit-02','Reference shallow pencil angle, asymmetric tip and long barrel replace the 45-degree pencil.'),
 'graduation-hat-01-lined':('brand-academic-lined','Reference diamond, wider crown and separate left tassel replace source cap construction.'),
 'line-chart-up-01-lined':('brand-chart-lined','Reference zigzag rhythm and long final climb replace source softened plot and axes.'),
 'face-smile-lined':('brand-smile-lined','Reference compact shallow mouth and eye placement replace large U-shaped smile.'),
 'database-01-lined':('data','Reference cylinder proportions, shallow ellipses and horizontal band rhythm replace stock cylinder.'),
 'clock-lined':('clock','Reference offset hand pivot, hand lengths and steeper short hand.'),
 'medical-cross-lined':('medical','Reference cross has deliberate straight and curved corners instead of uniform rounded corners.'),
 'file-01-lined':('brand-doc-lined','Reference folded corner, one rounded lower corner and two text strokes replace blank all-round rectangle.'),
}
custom={
 'beaker-02-lined':(svg(p('M8 3.25H16M9 3.25V9.75L3.9 16.8A2.5 2.5 0 0 0 5.9 20.75H18.1A2.5 2.5 0 0 0 20.1 16.8L15 9.75V3.25'),p('M6.5 13.25C8 12.5 10 13.5 12.25 15C15 16.9 17.75 16.4 19 15.5')),'brand-biotech-lined','Reference straight neck, slanted shoulders, rounded base and organic liquid boundary replace stepped vessel and thick stopper.'),
 'mail-01-lined':(svg(p('M3.5 5H17.5A3 3 0 0 1 20.5 8V19H6.5A3 3 0 0 1 3.5 16Z'),p('M3.5 6.5 12 12.5 20.5 6.5')),'message','Reference asymmetric message contour applied to an envelope; flap remains recognizable.'),
 'camera-01-lined':(svg(p('M3.5 8H7L9 4.5H15L17 8H20.5V20H6.5A3 3 0 0 1 3.5 17Z'),c(12,13,4)),'brand-chip-lined','Reference square/curved corner contrast applied to the camera body; angular stepped shoulders and a larger clear lens.'),
 'lock-01-lined':(svg(p('M19 10H8A3 3 0 0 0 5 13V21H19Z'),p('M9 10V6A3 3 0 0 1 15 6V10M12 15V17')),'brand-home-lined','Straight base and a single curved body corner follow the architectural reference; the shackle is an explicit semicircle.'),
 'phone-01-lined':(svg(p('M18.5 3H8.5A3 3 0 0 0 5.5 6V21H15.5A3 3 0 0 0 18.5 18Z'),p('M11 17.5H13')),'calendar','Reference opposing rounded corners and half-unit frame, replacing four rounded corners.'),
 'shopping-bag-01-lined':(svg(p('M20.5 6.5H6.5A3 3 0 0 0 3.5 9.5V20H17.5A3 3 0 0 0 20.5 17Z'),p('M8.5 6.5V5A3.5 3.5 0 0 1 15.5 5V6.5M8.5 12.5A3.5 3.5 0 0 0 15.5 12.5')),'brand-briefcase-lined','Reference bag proportions and handle with asymmetric corners; the source smile remains as its modifier.'),
}
out=ROOT/'staging/geometry-v2';out.mkdir(parents=True,exist_ok=True);m=json.loads((ROOT/'manifest.json').read_text());records=[]
for i,(anchor,note) in specs.items():
 r=ref(anchor);(out/(i+'.svg')).write_bytes(E.tostring(r)+b'\n');records.append({'id':i,'reference':anchor,'reason':note,'previous_path':m['icons'][i]['path'],'previous_sha256':m['icons'][i]['sha256']})
for i,(r,anchor,note) in custom.items():
 (out/(i+'.svg')).write_bytes(E.tostring(r)+b'\n');records.append({'id':i,'reference':anchor,'reason':note,'previous_path':m['icons'][i]['path'],'previous_sha256':m['icons'][i]['sha256']})
(ROOT/'review/reports/geometry-v2-samples.json').write_text(json.dumps({'user_policy':'Reference form first, icon meaning preserved. Direct reuse of user-supplied reference forms explicitly authorized in chat.','samples':records},indent=2)+'\n')
print('Reference-based candidates:',len(records))
