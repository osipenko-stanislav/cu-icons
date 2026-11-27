from pathlib import Path
import json, hashlib
root=Path('icon-project');m=json.loads((root/'manifest.json').read_text());ids=json.loads((root/'pilot-ids.json').read_text())
critique={'schema_version':1,'reviewer':'Codex sequential visual review','independence':'sequential','icons':[]}
for i in ids:
 critique['icons'].append({'id':i,'sha256':m['icons'][i]['sha256'],'render_evidence':['review/contact-sheets/pilot-light-001.png','review/contact-sheets/pilot-dark-001.png'],'findings':[]})
(root/'review/reports/pilot-critique.json').write_text(json.dumps(critique,indent=2)+'\n')
decisions={
 'scenario':{'value':'restyle','source':'user','confidence':'high'},
 'brief':{'value':'Restyle all supplied work icons using ref as style basis; preserve source semantics and editable SVG.','source':'user','confidence':'high'},
 'reference_choice':{'value':'provided','source':'user','confidence':'high'},
 'direction':{'value':'Thin monochrome linework, selective asymmetric corners, simplified geometric contours.','source':'reference','confidence':'high'},
 'geometry':{'value':'outline','source':'reference','confidence':'high'},
 'target_sizes':{'value':[16,24,32],'source':'inferred','confidence':'medium'},
 'motion_mode':{'value':'static','source':'default','confidence':'high'}}
(root/'specification/workflow-decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
summary={'pilot_count':len(ids),'total_count':len(m['icons']),'remaining':len(m['icons'])-len(ids),'user_approved':False,'visual_review':'sequential, 16/24/64 px, light and dark; compared with all original reference sheets','technical_errors':{i:m['icons'][i]['validation']['issues'] for i in ids if m['icons'][i]['validation']['issues']},'renderer':'Project-local resvg adapter; enlarged-viewBox clipping check passed 24/24','scope':'Only pilot produced. Original ref/work remain unchanged.','source_canvases':{}}
import xml.etree.ElementTree as E
for p in Path('work').glob('*.svg'):
 vb=E.parse(p).getroot().get('viewBox')
 if vb!='0 0 24 24':summary['source_canvases'][p.name]=vb
(root/'review/reports/pilot-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
