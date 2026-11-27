#!/usr/bin/env python3
"""Run the installed cu-iconizer with local resvg on macOS.
Bounds are conservative raster bounds at 1024 px (not analytic bounds).
Original skill files are unchanged. Dependencies live in /private/tmp/cu-iconizer-env.
"""
from pathlib import Path
import sys, runpy, types, hashlib
from io import BytesIO
import resvg_py
import xml.etree.ElementTree as ET
from PIL import Image

class Renderer:
    version = 'resvg-py-0.2.0/raster-bounds-1024-v2'
    def render(self, svg, size, cache=None):
        key = hashlib.sha256(self.version.encode()+str(size).encode()+b':'+svg).hexdigest()
        path = cache/(key+'.png') if cache else None
        if path and path.exists():
            with Image.open(path) as im: return im.convert('RGBA')
        node=ET.fromstring(svg); node.set('width',str(size)); node.set('height',str(size))
        raw=resvg_py.svg_to_bytes(svg_string=ET.tostring(node,encoding='unicode'), skip_system_fonts=True)
        im=Image.open(BytesIO(raw)).convert('RGBA')
        if path:
            path.parent.mkdir(parents=True,exist_ok=True); im.save(path)
        return im
    def bounds(self, svg, viewbox):
        box=self.render(svg,1024).getchannel('A').getbbox()
        if box is None: return [0,0,0,0]
        x,y,w,h=viewbox
        return [x+box[0]*w/1024,y+box[1]*h/1024,x+box[2]*w/1024,y+box[3]*h/1024]

module=types.ModuleType('renderer'); module.Renderer=Renderer; sys.modules['renderer']=module
skill=Path('/Users/st.osipenko/.codex/skills/cu-iconizer/scripts')
sys.path.insert(0,str(skill))
if __name__=='__main__': runpy.run_path(str(skill/'iconizer'),run_name='__main__')
