"""Check explicit same-meaning aliases at 24 and 48 px; no motion edits."""
from pathlib import Path
from PIL import Image
from io import BytesIO
import xml.etree.ElementTree as E
import json,hashlib,resvg_py
P=Path('icon-project');R=P/'review/motion/user-selection-2026-11-27';R.mkdir(exist_ok=True);active={r['id']:r for r in json.loads((P/'result/curated/catalog.json').read_text())}
text='''
message-alert-circle message-alert-square
message-check-circle message-check-square
message-dots-circle message-dots-square
message-heart-circle message-heart-square
message-plus-circle message-plus-square
message-question-circle message-question-square
message-x-circle message-x-square
award-01 award-02 award-04 award-05
beaker-01 beaker-02
check-circle-broken check-circle
check-small-16 check-small
check-square-broken check-square
cloud-raining-03 cloud-raining-05
cloud-snowing-01 cloud-snowing-02
cloud-sun-01 cloud-sun-02 cloud-sun-03
code-01 code-snippet-01
code-02 code-snippet-02
coins-01 coins-03
coins-02 coins-04
coins-stacked-01 coins-stacked-03
dotpoints-01 list
file-03 file-07
file-04 file-05
flag-01 flag-02
flag-04 flag-05
flash lightning-01 zap
flash-off zap-off
heart heart-rounded
home-02 home-03 home-05
image-01 image-03 image-04
indeterminate-small-16 indeterminate-small
lightbulb-01 lightbulb-03
line-chart-down-01 trend-down-01 trend-down-02
line-chart-down-03 line-chart-down-04
line-chart-up-01 trend-up-01 trend-up-02
line-chart-up-03 line-chart-up-04
loading-01 loading-tui
marker-pin-01 marker-pin-02 marker-pin-03
message-chat-circle message-chat-square
message-notification-circle message-notification-square
message-smile-circle message-smile-square
refresh-ccw-02 refresh-ccw-05
refresh-ccw-03 refresh-ccw-04
refresh-cw-02 refresh-cw-05
refresh-cw-03 refresh-cw-04
repeat-01 repeat-03 repeat-04
sale-02 sale-03 sale-04
share-01 share-02
share-03 share-04
share-05 share-06
sliders-01 sliders-02
star-03 star-07
star-04 star-05
'''
cache={}
def signatures(id):
 if id in cache:return cache[id]
 raw=(P/'result/svg'/active[id]['file']).read_bytes();out=[]
 for size in [24,48]:
  root=E.fromstring(raw);root.set('width',str(size));root.set('height',str(size))
  for n in root.iter():
   for attr in ['stroke','fill']:
    if n.get(attr)=='currentColor':n.set(attr,'#111111')
  im=Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=E.tostring(root).decode(),skip_system_fonts=True))).convert('RGBA');out.append(hashlib.sha256(im.getchannel('A').tobytes()).hexdigest())
 cache[id]=out;return out
valid=[];rejected=[]
for line in text.strip().splitlines():
 ids=[s+'-lined' for s in line.split() if s+'-lined' in active]
 if len(ids)<2:continue
 if len({tuple(signatures(id)) for id in ids})==1:valid.append({'members':ids,'semantic_basis':'Same named action/status/metaphor or explicit synonyms; frame style alternatives only.','evidence':'Exact alpha-mask equality at both 24 and 48px.'})
 else:rejected.append({'members':ids,'reason':'Not exactly equal at both checked sizes; left active.'})
report={'confirmed_groups':valid,'not_exact':rejected,'deferred_distinct_semantics':['annotation vs message (annotation and chat contexts)','circle vs placeholder','cloud vs cloud-blank (weather/storage context)','data/database vs coins (wrong geometry is not semantic equivalence)','filter/settings/sliders (product context)','flip vs reverse (flip and undo)','moon vs eclipse (state)','repeat vs switch (repeat and swap)','share vs upload (action)','users/stars (object counts)','x-close vs x (dismiss vs generic cross)']}
(R/'remaining-aliases.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Confirmed groups',len(valid),'additional alternatives',sum(len(r['members'])-1 for r in valid),'not exact',len(rejected))
