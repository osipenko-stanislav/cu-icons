"""Fetch the user's registry reference wrappers without installing packages."""
from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,re
P=Path('icon-project');R=P/'references/motion/user-selection-2026-11-27';R.mkdir(parents=True,exist_ok=True)
groups={
 'object-gesture':'inbox file file-text phone-call message-circle battery-charging cloud-rain sun gift scissors coffee'.split(),
 'mechanism':'tool hard-drive smartphone battery-charging video-v2 settings-v2 folder calendar notification-v4 more-horizontal'.split(),
 'signal-propagation':'wifi phone-call rss shuffle'.split(),
 'state-transition':'menu-v2 arrow-left notification-v2 microphone-v2 volume heart thumb-up user-plus user-x'.split(),
}
(R/'selection.json').write_text(json.dumps({'date':'2026-11-27','source':'user','classes':groups,'notes':{'video-v2':'User note is truncated after «это пример для вкыл»; intended on/off direction remains unspecified.'}},ensure_ascii=False,indent=2)+'\n')
local={r['id']:r for r in json.loads((P/'references/motion/useanimations/catalog.json').read_text())['icons']}
def fetch(id):
 url=f'https://useanimations.com/r/{id}.json';path=R/(id+'.registry.json')
 try:
  if not path.exists():
   with urlopen(url,timeout=30) as response:raw=response.read()
   json.loads(raw);path.write_bytes(raw)
  raw=path.read_bytes();d=json.loads(raw);source='\n'.join(f.get('content','') for f in d.get('files',[]));match=re.search(r'interaction="([^"]+)"',source);ref=local.get(id)
  return {'id':id,'url':url,'registry_sha256':hashlib.sha256(raw).hexdigest(),'interaction':match[1] if match else None,'description':d.get('description'),'component_source':source,'local_animation':'../useanimations/json/'+id+'.json' if ref else None,'reference_page':ref.get('page') if ref else None,'status':'fetched'}
 except Exception as e:return {'id':id,'url':url,'status':'failed','error':str(e)}
ids=list(dict.fromkeys(i for g in groups.values() for i in g))
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,ids))
(R/'sources.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print('References',len(ids),'fetched',sum(r['status']=='fetched' for r in rows));print('Failures',[r for r in rows if r['status']!='fetched']);print('Behaviors',[(r['id'],r.get('interaction')) for r in rows])
