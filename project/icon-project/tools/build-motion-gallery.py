from pathlib import Path
import sys
from importlib.machinery import SourceFileLoader
SourceFileLoader('local_adapter','icon-project/tools/iconizer-local.py').load_module()
import motion_gallery
# Apply the native draw-track geometry validation to the project's round-trip channel.
checked_tracks=motion_gallery.checked_tracks
def validate_round_trip(scene,parts):
    import json
    profiles=json.loads(Path('icon-project/motion/profiles.json').read_text())['profiles']
    tracks=[]
    for track in scene['tracks']:
        if len(track) not in [7,8] or (len(track)==8 and track[7] not in profiles):raise ValueError('Invalid motion profile')
        i,k,*rest=track[:7]
        tracks.append([i,'draw' if k=='erase-redraw' else 'x' if k in ['scale','scale-x','scale-y','page-turn'] else k,*rest])
    checked_tracks({**scene,'trigger':'hover' if scene['trigger']=='hover-click' else scene['trigger'],'tracks':tracks},parts)
motion_gallery.checked_tracks=validate_round_trip
motion_gallery.ASSETS=Path('icon-project/motion/assets').resolve()
print(motion_gallery.build_motion_gallery(Path(sys.argv[2] if len(sys.argv)>2 else 'icon-project').resolve(),Path(sys.argv[1] if len(sys.argv)>1 else 'icon-project/motion/pilot/motion.json').resolve()))
