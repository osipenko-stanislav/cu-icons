from pathlib import Path
from importlib.machinery import SourceFileLoader
from zipfile import ZipFile,ZIP_DEFLATED
from io import BytesIO
import json
P=Path('icon-project').resolve();O=P/'motion/exact-reference';A=O/'assets'
legacy=(P/'motion/assets/motion/player.js').read_text().replace('function mountMotion(', 'function mountLegacyMotion(',1)
(A/'player.js').write_text((O/'vendor/lottie-light-5.13.0.js').read_text()+';\n'+legacy+'\n'+(A/'exact-player.js').read_text())
(A/'export.html').write_text((P/'motion/assets/motion/export.html').read_text())
SourceFileLoader('local_adapter',str(P/'tools/iconizer-local.py')).load_module()
import motion_gallery
native_check=motion_gallery.checked_tracks

def validate(scene,parts):
 t=scene['tracks'][0]
 if len(scene['tracks'])!=1 or len(t)!=8 or t[1]!='reference-lottie' or t[7].get('version')!=1:raise ValueError('Invalid reference scene')
 data=t[7]['animationData']
 if data.get('assets') or any(l.get('ty')!=4 for l in data['layers']):raise ValueError('Unsupported embedded media')
 native_check({**scene,'trigger':'hover','tracks':[[0,'x',0,0,0,0,1]]},parts)
motion_gallery.checked_tracks=validate;motion_gallery.ASSETS=O/'..'/'exact-reference'
# Motion gallery expects an assets/motion folder.
motion_gallery.ASSETS=O/'build-assets';target=motion_gallery.ASSETS/'motion';target.mkdir(parents=True,exist_ok=True)
for name in ['player.js','gallery.html','export.html']:(target/name).write_bytes((A/name).read_bytes())
native_export=motion_gallery.export_archive

def export(*args,**kwargs):
 raw=native_export(*args,**kwargs);out=BytesIO()
 with ZipFile(BytesIO(raw)) as original,ZipFile(out,'w',ZIP_DEFLATED) as z:
  for n in original.namelist():z.writestr(n,original.read(n))
  z.writestr('licenses/useAnimations-MIT.txt',(P/'references/motion/useanimations/LICENSE.txt').read_bytes())
  z.writestr('licenses/lottie-web-MIT.md',(O/'vendor/LICENSE.lottie-web.md').read_bytes())
 return out.getvalue()
motion_gallery.export_archive=export
project=O/'preview';page=motion_gallery.build_motion_gallery(project,O/'motion.json')
manifest=json.loads((O/'manifest.json').read_text());references={r['id']:json.loads((P/'references/motion/useanimations/json'/(r['reference']+'.json')).read_text()) for r in manifest};page.write_text(page.read_text().replace('@@REFERENCE_DATA@@',motion_gallery.inline_json(references)))
import shutil
published=P/'gallery/motion-review/exact-reference';shutil.copytree(page.parent,published,dirs_exist_ok=True);print(published/'index.html')
