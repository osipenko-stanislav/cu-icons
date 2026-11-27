from pathlib import Path
import xml.etree.ElementTree as E
import re,json,hashlib,copy
P=Path('icon-project'); out=P/'motion/pilot'
E.register_namespace('','http://www.w3.org/2000/svg')
scenes=[]; provenance=[]
def scene(id,label,duration,tracks,prepare,idea):
    raw=(P/'result/svg'/f'{id}.svg').read_bytes(); root=E.fromstring(raw)
    prepare(root)
    active=E.Element('{http://www.w3.org/2000/svg}g',{'id':'motion-active','visibility':'hidden'})
    for n in list(root):root.remove(n);active.append(n)
    idle=E.Element('{http://www.w3.org/2000/svg}g',{'id':'motion-idle'})
    for n in E.fromstring(raw):idle.append(copy.deepcopy(n))
    root.append(idle);root.append(active)
    (out/'svg'/f'{id}.svg').write_bytes(raw)
    derived=E.tostring(root,encoding='utf-8')
    (out/'geometry'/f'{id}.svg').write_bytes(derived)
    scenes.append(dict(id=id,label=label,trigger='hover',duration=duration,tracks=tracks))
    provenance.append(dict(id=id,static_sha256=hashlib.sha256(raw).hexdigest(),geometry_sha256=hashlib.sha256(derived).hexdigest(),idea=idea,approval='pending-motion-pilot',static_approval='previously-user-approved'))
def split(root):
    for node in list(root):
        if node.tag.endswith('path'):
            paths=re.findall(r'[Mm][^Mm]*',node.attrib['d'])
            if len(paths)>1:
                at=list(root).index(node); root.remove(node)
                for i,d in enumerate(paths):
                    n=copy.deepcopy(node); n.set('d',d);root.insert(at+i,n)
def parts(root,indices):
    for part,idx in enumerate(indices):root[idx].set('data-part',str(part))
def glasses(r):split(r);parts(r,[1,2])
scene('glasses-02-lined','Glasses · temple adjustment',900,[[0,'rotate',-9,3.43494,13,0,.8],[1,'rotate',9,20.5653,13,.15,1]],glasses,'Дужки слегка расходятся у шарниров; линзы и переносица неподвижны.')
def database(r):parts(r,[0,1,2])
scene('database-01-lined','Database · data sweep',1100,[[0,'erase-redraw',1,0,0,.45,1],[1,'erase-redraw',1,0,0,.2,.7],[2,'erase-redraw',1,0,0,0,.45]],database,'Полные уровни последовательно стираются и прорисовываются вдоль контура; начало и конец полностью видимы.')
def hat(r):split(r);parts(r,[1])
scene('graduation-hat-01-lined','Graduation hat · tassel swing',1000,[[0,'rotate',-14,1.5,8.88934,0,1]],hat,'Шнур качается вокруг точки крепления; шапочка неподвижна.')
def chip(r):split(r);parts(r,list(range(1,10)))
scene('cpu-chip-01-lined','CPU chip · signal route',1800,[[i,'erase-redraw',1,0,0,a,b] for i,a,b in [(0,.25,.65),(1,0,.3),(2,.04,.34),(3,.6,.9),(4,.64,.94),(5,.08,.38),(6,.12,.42),(7,.66,.96),(8,.7,1)]],chip,'Контакты и ядро последовательно стираются и прорисовываются вдоль path; полный вид в начале и конце.')
config=dict(version=1,defaultPreset='Balanced',presets={'Smooth':dict(duration=.85,amplitude=.65,curve='cosine'),'Balanced':dict(duration=1,amplitude=1,curve='cosine'),'Expressive':dict(duration=1.2,amplitude=1.2,curve='spring')},scenes=scenes)
(out/'motion.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
(out/'provenance.json').write_text(json.dumps(dict(review='sequential',pilot_approval='pending',scenes=provenance),ensure_ascii=False,indent=2)+'\n')
(P/'specification/motion-direction.json').write_text(json.dumps({'motion_mode':{'value':'animate','source':'user','confidence':'high'},'motion_preset':{'value':'balanced','source':'default','confidence':'high'},'trigger_policy':{'value':{'default':['hover','click-replay']},'source':'inferred','confidence':'medium'}},indent=2)+'\n')
print('Prepared',len(scenes),'non-obvious scenes')
