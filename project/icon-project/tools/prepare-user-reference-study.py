"""Prepare a read-only comparison of selected references and active project scenes."""
from pathlib import Path
import json,copy
P=Path('icon-project');R=P/'references/motion/user-selection-2026-11-27';D=P/'gallery/motion-review/reference-study-2026-11-27';D.mkdir(exist_ok=True)
selection=json.loads((R/'selection.json').read_text());cat={r['id']:r for r in json.loads((P/'references/motion/useanimations/catalog.json').read_text())['icons']};active={r['id'] for r in json.loads((P/'result/curated/catalog.json').read_text())};scenes={s['id']:s for s in json.loads((P/'motion/reference-series/motion.json').read_text())['scenes'] if s['id'] in active}
preferred={'inbox':'inbox-01-lined','file':'file-02-lined','file-text':'file-02-lined','phone-call':'phone-call-02-lined','message-circle':'message-circle-01-lined','battery-charging':'battery-charging-02-lined','cloud-rain':'cloud-raining-01-lined','sun':'sun-lined','gift':'gift-01-lined','scissors':'scissors-01-lined','tool':'tool-01-lined','hard-drive':'hard-drive-lined','smartphone':'phone-01-lined','video-v2':'video-recorder-lined','settings-v2':'settings-03-lined','folder':'folder-lined','calendar':'calendar-lined','notification-v4':'bell-01-lined','more-horizontal':'dots-horizontal-lined','wifi':'wifi-lined','rss':'rss-01-lined','shuffle':'shuffle-01-lined','menu-v2':'menu-01-lined','arrow-left':'arrow-left-lined','notification-v2':'bell-off-01-lined','microphone-v2':'microphone-01-lined','volume':'volume-max-lined','heart':'heart-lined','thumb-up':'thumbs-up-lined','user-plus':'user-plus-01-lined','user-x':'user-x-01-lined'}
rows=[]
for id in dict.fromkeys(i for ids in selection['classes'].values() for i in ids):
 data=json.loads((P/'references/motion/useanimations/json'/(id+'.json')).read_text());scene={'id':'reference-'+id,'label':id,'trigger':'reference','duration':(data['op']-data.get('ip',0))/data['fr']*1000,'tracks':[[0,'reference-lottie',1,0,0,0,1,{'version':1,'interaction':cat[id]['interaction'],'animationData':data,'overflow':True}]]}
 target=preferred.get(id);target=target if target in scenes else None
 rows.append({'reference':id,'classes':[k for k,v in selection['classes'].items() if id in v],'source':scene,'project':scenes.get(target),'project_id':target})
(D/'study.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(R/'project-mapping.json').write_text(json.dumps([{k:v for k,v in r.items() if k not in ['source','project']} for r in rows],indent=2)+'\n')
js=r'''
(async()=>{
 const result={rows:[],errors:[]},rows=await(await fetch('study.json')).json(),host=document.getElementById('host');
 for(const row of rows.filter(r=>!new URLSearchParams(location.search).has('reference')||r.reference===new URLSearchParams(location.search).get('reference'))){const item={reference:row.reference,classes:row.classes,project_id:row.project_id};
  for(const side of ['source','project']){
   const scene=row[side];if(!scene){item[side]=null;continue}
   try{host.innerHTML='';const c=mountMotion(host,[],scene,()=>({duration:1}));await c.ready;c.stop();item[side]=[];
    for(const t of [0,.15,.33,.5,.67,.85,1]){c.seek(t);const original=host.querySelector('.exact-renderer svg'),svg=original.cloneNode(true);svg.setAttribute('width','48');svg.setAttribute('height','48');svg.style.width='48px';svg.style.height='48px';svg.style.color='#111';
     for(const p of svg.querySelectorAll('path')){if(p.closest('defs,mask,clipPath'))continue;p.setAttribute('stroke-width','1');p.setAttribute('vector-effect','non-scaling-stroke')}
     item[side].push({t,svg:svg.outerHTML});
    }c.destroy();
   }catch(e){result.errors.push({reference:row.reference,side,error:String(e)})}
  }result.rows.push(item);
 }
 document.getElementById('result').textContent=JSON.stringify(result);document.body.dataset.complete='true';
})();
'''
(D/'index.html').write_text('<!doctype html><meta charset="utf-8"><style>#host{width:48px;height:48px;color:#111}</style><div id="host"></div><pre id="result"></pre><script src="../reference-series/player.js"></script><script>'+js+'</script>')
print('Prepared',len(rows),'references; no matching production icon:',[r['reference'] for r in rows if not r['project_id']])
