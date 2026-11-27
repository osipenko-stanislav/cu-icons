from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
import json,hashlib
R=Path('icon-project/references/motion/useanimations');rows=json.loads((R/'catalog.json').read_text())['icons']
def fetch(row):
 p=R/'json'/(row['id']+'.json')
 try:
  if not p.exists():
   with urlopen(row['lottie'],timeout=25) as response:raw=response.read()
   json.loads(raw);p.write_bytes(raw)
  raw=p.read_bytes();d=json.loads(raw)
  return {'id':row['id'],'url':row['lottie'],'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'fps':d['fr'],'duration_ms':(d['op']-d.get('ip',0))/d['fr']*1000,'interaction':row['interaction'],'status':'downloaded'}
 except Exception as e:return {'id':row['id'],'status':'failed','error':str(e)}
with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(fetch,rows))
(R/'sources.json').write_text(json.dumps(records,indent=2)+'\n');print('Fetched',sum(r['status']=='downloaded' for r in records),'/',len(records));print([r for r in records if r['status']=='failed'])
