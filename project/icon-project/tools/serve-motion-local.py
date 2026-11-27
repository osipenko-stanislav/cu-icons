"""Loopback-only review server with per-icon triggers and consistent ZIP exports."""
from pathlib import Path
from importlib.machinery import SourceFileLoader
from http.server import ThreadingHTTPServer
from functools import partial
from urllib.parse import urlsplit,parse_qs
from io import BytesIO
from zipfile import ZipFile,ZIP_DEFLATED
import json
from threading import Lock
state_lock=Lock()
SourceFileLoader('local_adapter','icon-project/tools/iconizer-local.py').load_module()
from motion_gallery import ReviewHandler,EXPORT,AFFIX,named_archive,inline_json,export_archive
P=Path('icon-project').resolve();directory=P/'gallery/motion-review';state=P/'motion/series/trigger-overrides.json'
ids={s['id'] for s in json.loads((P/'motion/series/motion.json').read_text())['scenes']};modes={'hover','click-replay','hover-click'}
ids.update(s['id'] for s in json.loads((P/'motion/reference-series/motion.json').read_text())['scenes'])
def collection_for(path):
 collection=parse_qs(urlsplit(path).query).get('collection',['series'])[0]
 if collection not in ['series','reference-pilot','exact-reference','reference-series']:raise ValueError('Invalid collection')
 return collection
def state_for(collection):return P/'motion'/collection/'trigger-overrides.json' if collection in ['exact-reference','reference-series'] else state
def read_modes(collection='series'):
 target=state_for(collection)
 return json.loads(target.read_text()) if target.exists() else {}
def validate(values,collection='series'):
 allowed=modes|{'reference'} if collection in ['exact-reference','reference-series'] else modes
 if not isinstance(values,dict) or any(i not in ids or m not in allowed for i,m in values.items()):raise ValueError('Invalid trigger selection')
 return values

def archive(source,overrides,prefix='',suffix='',stroke_width=1):
 if not isinstance(stroke_width,(int,float)) or not .5<=stroke_width<=3:raise ValueError('Invalid stroke width')
 data=BytesIO()
 with ZipFile(source) as z,ZipFile(data,'w',ZIP_DEFLATED) as out:
  for entry in z.namelist():
   raw=z.read(entry)
   if entry=='motion.json':
    config=json.loads(raw);config['strokeWidth']=stroke_width
    for scene in config['scenes']:scene['trigger']=overrides.get(scene['id'],scene['trigger'])
    raw=(json.dumps(config,ensure_ascii=False,indent=2)+'\n').encode()
   elif entry=='preview.html':
    text=raw.decode();marker='const scenes=';start=text.index(marker)+len(marker);scenes,offset=json.JSONDecoder().raw_decode(text[start:])
    for scene in scenes:scene['trigger']=overrides.get(scene['id'],scene['trigger'])
    text=text[:start]+inline_json(scenes)+text[start+offset:];text=text.replace('</style>',f':root{{--icon-stroke:{stroke_width}px}}</style>');raw=text.encode()
   out.writestr(entry,raw)
 data.seek(0)
 if prefix or suffix:return named_archive(data,prefix,suffix)
 return data.getvalue()
def build_series_export(icon,preset,speed):
 root=P/'motion/reference-series';config=json.loads((root/'gallery-config.json').read_text());scenes=[s for s in config['scenes'] if icon=='pack' or s['id']==icon]
 if not scenes:raise ValueError('Unknown icon')
 files={s['id']:((root/'svg'/(s['id']+'.svg')).read_bytes(),(root/'geometry'/(s['id']+'.svg')).read_bytes()) for s in scenes}
 assets=P/'motion/exact-reference/assets';raw=export_archive(scenes,config,files,preset.title(),float(speed),(assets/'player.js').read_text(),(root/'export.html').read_text());output=BytesIO()
 with ZipFile(BytesIO(raw)) as src,ZipFile(output,'w',ZIP_DEFLATED) as z:
  for name in src.namelist():z.writestr(name,src.read(name))
  z.writestr('licenses/useAnimations-MIT.txt',(P/'references/motion/useanimations/LICENSE.txt').read_bytes());z.writestr('licenses/lottie-web-MIT.md',(P/'motion/exact-reference/vendor/LICENSE.lottie-web.md').read_bytes())
 return BytesIO(output.getvalue())
class Handler(ReviewHandler):
 def payload(self):
  length=int(self.headers.get('Content-Length','0'))
  if not 0<length<=200000:raise ValueError('Invalid body size')
  return json.loads(self.rfile.read(length))
 def reply(self,data,kind='application/json',name=None):
  self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)))
  if name:self.send_header('Content-Disposition',f'attachment; filename="{name}"')
  self.end_headers();self.wfile.write(data)
 def do_GET(self):
  if urlsplit(self.path).path=='/api/triggers':
   try:self.reply(json.dumps(read_modes(collection_for(self.path))).encode())
   except ValueError as e:self.send_error(400,str(e))
   return
  super().do_GET()
 def send_head(self):
  match=EXPORT.fullmatch(urlsplit(self.path).path)
  overrides=read_modes('exact-reference' if urlsplit(self.path).path.startswith('/exact-reference/') else 'series')
  if match and (overrides or 'stroke=' in urlsplit(self.path).query):
   from urllib.parse import parse_qs
   q=parse_qs(urlsplit(self.path).query);prefix=q.get('prefix',[''])[0];suffix=q.get('suffix',[''])[0]
   if not all(AFFIX.fullmatch(v) for v in [prefix,suffix]):self.send_error(400);return None
   source=Path(self.translate_path(urlsplit(self.path).path))
   if not source.is_file():self.send_error(404);return None
   data=archive(source,overrides,prefix,suffix,float(q.get('stroke',['1'])[0]));self.send_response(200);self.send_header('Content-Type','application/zip');self.send_header('Content-Length',str(len(data)));self.send_header('Content-Disposition','attachment; filename="'+source.name+'"');self.end_headers();return BytesIO(data)
  return super().send_head()
 def do_POST(self):
  # Only the review page origin may write local preferences or request exports.
  origin=self.headers.get('Origin')
  if origin and origin not in [f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}']:
   self.send_error(403);return
  try:
   data=self.payload();path=urlsplit(self.path).path
   if path=='/api/triggers':
    collection=collection_for(self.path);updates=validate(data,collection);target=state_for(collection)
    with state_lock:
     values={**read_modes(collection),**updates};temporary=target.with_suffix('.tmp');temporary.write_text(json.dumps(values,indent=2)+'\n');temporary.replace(target)
    self.reply(json.dumps(values).encode());return
   if path=='/api/export':
    preset=data['preset'].lower();speed=str(data['speed']);icon=data['icon'];prefix=data.get('prefix','');suffix=data.get('suffix','')
    if preset not in ['smooth','balanced','expressive'] or speed not in ['0.75','1','1.25','1.5'] or icon not in ids|{'pack'} or not all(AFFIX.fullmatch(v) for v in [prefix,suffix]):raise ValueError('Invalid export settings')
    collection=data.get('collection','series')
    if collection not in ['series','reference-pilot','exact-reference','reference-series']:raise ValueError('Invalid collection')
    export_root=directory if collection=='series' else directory/collection
    overrides={**read_modes(collection),**validate(data.get('overrides',{}),collection)};source=export_root/'exports'/f'{preset}-{speed}'/f'{icon}.zip'
    if collection=='reference-series':source=build_series_export(icon,preset,speed)
    elif not source.is_file():raise ValueError('Icon not present in this collection')
    payload=archive(source,overrides,prefix,suffix,data.get('strokeWidth',1));name=('cu-iconizer' if icon=='pack' else prefix+icon+suffix)+f'-{preset}-{speed}x.zip'
    self.reply(payload,'application/zip',name);return
   self.send_error(404)
  except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:self.send_error(400,str(e))
if __name__=='__main__':
 with ThreadingHTTPServer(('127.0.0.1',8766),partial(Handler,directory=str(directory))) as server:
  print('Motion review at http://127.0.0.1:8766/',flush=True);server.serve_forever()
