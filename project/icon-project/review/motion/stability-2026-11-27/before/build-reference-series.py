# -*- coding: utf-8 -*-
"""Publish the curated retargeted library; ZIPs use the same scene selection."""
from pathlib import Path
from importlib.machinery import SourceFileLoader
import json,hashlib
P=Path('icon-project');O=P/'motion/reference-series';A=P/'motion/exact-reference/assets';D=P/'gallery/motion-review/reference-series';D.mkdir(parents=True,exist_ok=True)
SourceFileLoader('local_adapter',str(P/'tools/iconizer-local.py')).load_module()
from motion_gallery import svg_input,inline_json
from ref_svg_input import svg_input_ref
config=json.loads((O/'motion.json').read_text());scenes=[]
active_ids={r['id'] for r in json.loads((P/'result/curated/catalog.json').read_text())}
assert active_ids and active_ids <= {s['id'] for s in config['scenes']}
for scene in config['scenes']:
 if scene['id'] not in active_ids:continue
 if scene['id'].startswith('ref-'):
  raw,svg,parts=svg_input_ref(O/'geometry'/(scene['id']+'.svg'),scene['id']+'-motion')
 else:
  raw,svg,parts=svg_input(O/'geometry'/(scene['id']+'.svg'),scene['id']+'-motion',True)
 if scene['tracks'][0][1]=='reference-lottie':
  assert len(scene['tracks'])==1 and scene['tracks'][0][7]['version']==1
  assert 0<scene['duration']<=20000
 scenes.append({**scene,'svg':svg,'source':(O/'svg'/(scene['id']+'.svg')).read_text()})
config.update(project='reference-series-v1',collection='reference-series',scenes=scenes)
(D/'scenes.json').write_text(json.dumps(config,separators=(',',':'))+'\n')
(D/'player.js').write_bytes((A/'player.js').read_bytes())
s=(P/'motion/assets/motion/gallery.html').read_text().replace('Проверка анимаций','Анимации · основной набор').replace('Способы запуска предложены по смыслу. Их можно изменить в каждой карточке.','Архивные альтернативы исключены из просмотра и скачивания. Способ запуска можно изменить для каждой иконки.')
s=s.replace('@@PLAYER@@','').replace('const config = @@CONFIG@@;',"const config = await (await fetch('scenes.json')).json();window.referenceSeriesConfig=config;window.seriesControllers=[];")
s=s.replace('<script>\n','<script src="player.js"></script><script type="module">\n',1)
s=s.replace("fetch('/api/triggers'","fetch('/api/triggers?collection=reference-series'")
s=s.replace("const validModes=['hover'","const validModes=['reference','hover'").replace("[['hover','Только наведение']","[['reference','Как в референсе'],['hover','Только наведение']")
s=s.replace('motion=mountMotion(preview,', 'motion=mountDeferred(preview,')
s=s.replace("motion?.stop?.();scene.trigger=trigger.value;", "motion?.setTrigger?.(trigger.value);scene.trigger=trigger.value;")
s=s.replace("$('icon-size').onchange=()=>{let size=$('icon-size').value;document.querySelectorAll('.preview svg').forEach(svg=>{svg.style.width=size+'px';svg.style.height=size+'px'})};", "$('icon-size').onchange=()=>document.body.style.setProperty('--icon-size',$('icon-size').value+'px');$('icon-size').onchange();")
s=s.replace('.preview svg{width:48px;height:48px;', '.preview svg{width:var(--icon-size,48px);height:var(--icon-size,48px);')
s=s.replace("$('motion-type').onchange=$('speed').onchange=updateDownloads;", "$('motion-type').onchange=$('speed').onchange=()=>{updateDownloads();for(const c of window.seriesControllers)c.updateSpeed?.()};")
s=s.replace('<div class="toolbar">','<p><a href="/exact-reference/">Сравнение с useAnimations</a> · <a href="/previous-series/">Предыдущая анимация</a></p><div class="toolbar">',1)
s=s.replace("for(const scene of config.scenes) {",'''const observed=new WeakMap();
const observer=new IntersectionObserver(entries=>{for(const e of entries){const c=observed.get(e.target);if(e.isIntersecting)c.load();else c.pause()}},{rootMargin:'120px'});
function mountDeferred(root,parts,scene,preset){
 let motion=null,visible=false;
 const load=()=>{visible=true;if(!motion){motion=mountMotion(root,parts,scene,preset);window.seriesControllers.push(motion)}else if(motion.animation&&scene.trigger==='reference'&&scene.tracks[0][7]?.interaction==='loop'&&!matchMedia('(prefers-reduced-motion: reduce)').matches)motion.animation.play();return motion};
 const pause=()=>{visible=false;motion?.animation?.pause()};
 observed.set(root,{load,pause});observer.observe(root);
 root.addEventListener('pointerenter',()=>{if(!motion){const m=load();m.ready?.then(()=>{if(root.matches(':hover'))root.dispatchEvent(new Event('pointerenter'))})}});
 root.addEventListener('click',()=>{if(!motion){const m=load();m.ready?.then(()=>root.click())}});
 return {setTrigger(value){scene.trigger=value;motion?.setTrigger?.(value)},stop(){motion?.stop?.()},load};
}
for(const scene of config.scenes) {''',1)
# Keep a source link and a seek control on motion cards.
s=s.replace('card.append(preview);', '''card.append(preview);
    if(scene.tracks[0][1]==='reference-lottie'){
     const payload=scene.tracks[0][7],link=document.createElement(payload.authored?'span':'a');link.textContent=payload.authored?'Авторская анимация':'useAnimations · '+payload.sourceId;if(!payload.authored)link.href=payload.sourceUrl;link.target='_blank';link.rel='noopener';link.style.cssText='display:block;font-size:11px;opacity:.6;margin-bottom:8px';card.append(link);
     const slider=document.createElement('input');slider.type='range';slider.min=0;slider.max=1000;slider.value=0;slider.style.cssText='width:100%;padding:0';slider.setAttribute('aria-label','Кадр: '+scene.label);slider.oninput=()=>{const m=motion.load();m.ready?.then(()=>m.seek(Number(slider.value)/1000))};card.append(slider);
    }''')
(D/'index.html').write_text(s)
(O/'gallery-config.json').write_text(json.dumps(config,separators=(',',':'))+'\n')
print('Published',len(scenes),'scenes:',D/'index.html')
