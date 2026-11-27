from pathlib import Path
from zipfile import ZipFile
import json,hashlib,collections
P=Path('icon-project');S=P/'motion/series';R=P/'review/motion/series';G=P/'gallery/motion-review';catalog=json.loads((S/'catalog.json').read_text());config=json.loads((S/'motion.json').read_text());checks=json.loads((R/'checks.json').read_text());status=json.loads((S/'status.json').read_text());contacts=json.loads((R/'contact-audit-after.json').read_text());crossings=json.loads((R/'crossing-audit-after.json').read_text());pilot_checks=json.loads((P/'review/motion/reference-pilot/checks.json').read_text());pilot_cross=json.loads((P/'review/motion/reference-pilot/crossing-audit.json').read_text())
assert not checks['browser_failures'] and not checks['static_mismatches'] and not checks['clipped_frames'];assert not crossings['findings'];assert pilot_checks['status']=='pass' and not pilot_cross['findings']
expected=[];unexpected=[]
for finding in contacts['findings']:
 for c in finding['broken']:
  is_lid_release=finding['id'] in ['trash-01-lined','trash-03-lined','trash-04-lined'] and abs(c['point'][0]-19)<.001 and abs(c['point'][1]-6)<.001
  (expected if is_lid_release else unexpected).append({'id':finding['id'],**c})
assert not unexpected,unexpected
for file in ['pack','file-03-lined','folder-lined','globe-01-lined','settings-03-lined','trash-01-lined']:
 with ZipFile(G/f'exports/balanced-1/{file}.zip') as z:
  assert z.testzip() is None;assert z.read('player.js')==(P/'motion/assets/motion/player.js').read_bytes()
  if file=='pack':assert len(json.loads(z.read('motion.json'))['scenes'])==1189
  else:assert z.read(f'geometry/{file}.svg')==(S/f'geometry/{file}.svg').read_bytes()
for r in catalog:r['motion_review_status']='agent-reviewed';r['review_method']='Sequential: initial full-series sheets, measured contact/crossing audit, all 169 revised geometries on three focused comparison sheets'
(S/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
audit={'source_contacts_checked':contacts['counts']['contacts'],'source_icons':contacts['counts']['icons'],'geometric_preset_runs':contacts['counts']['presetRuns'],'unexpected_separations':0,'intentional_releases':{'count':len(expected),'reason':'Right edge of trash lid opens while the left hinge at (5,6) stays fixed'},'new_contour_crossings':0,'moving_pairs_sampled':crossings['counts']['movingPairs'],'revised_geometry_count':len(json.loads((R/'structural-revisions.json').read_text())),'limitations':'Sampled Chromium trajectories and contour polylines; no analytic proof for every instant or cross-browser verification','review':'Sequential; no independent agent'}
checks.update(structural_audit=audit,visual_review='Sequential: all changed geometries checked on three focused sheets; default full-series checks retained',stroke_control=status.get('stroke_control'),archive_samples='Full pack and five targeted individual packages: pass');(R/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
status.update(structural_audit=audit,patterns=dict(collections.Counter(r['pattern'] for r in catalog)),geometry_motion_scenes=sum(any(t[1] not in ['draw','erase-redraw'] for t in s['tracks']) for s in config['scenes']),player_sha256=hashlib.sha256((P/'motion/assets/motion/player.js').read_bytes()).hexdigest(),reference_motion_pilot={'scenes':9,'status':'pending-user-review','url':'http://127.0.0.1:8766/reference-pilot/'},balanced_pack_bytes=(G/'exports/balanced-1/pack.zip').stat().st_size);(S/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
reference_status={'scenes':9,'user_approval':'pending','reference':'https://useanimations.com/#icons','browser_checks':len(pilot_checks['browser_checks']),'full_initial_final_pose':True,'authored_svg_static_equivalent':True,'new_contour_crossings':0,'downloaded_pack_valid':True,'choreography':'Original authoring; timing profiles, inner-page geometry and runtime are project-owned work. Upstream samples were used only for reference research.'}
(P/'motion/reference-pilot/status.json').write_text(json.dumps(reference_status,ensure_ascii=False,indent=2)+'\n')
(P/'motion/reference-pilot/README.md').write_text('''# Новое направление движения — 9 примеров

Прототип: http://127.0.0.1:8766/reference-pilot/.

Изучены реальные кадры девяти анимаций https://useanimations.com/#icons. На существующей переработанной графике нарисован собственный внутренний лист книги и спроектированы самостоятельные фазы движения: подготовка, действие, пауза, возврат. Подробности в direction.json и ../../review/reports/useanimations-direction-study.json.

Исходные статические SVG не менялись. В motion.json — отдельные сцены; geometry/ содержит производную геометрию. Необязательное восьмое поле дорожки выбирает авторский профиль из ../profiles.json. page-turn управляет внутренним листом и его видимостью в крайних позах. Полная исходная иконка видна в начале и конце.

Пилот нового направления ожидает пользовательского просмотра и утверждения. Полная текущая библиотека отдельно доступна на http://127.0.0.1:8766/; в ней исправлены конструктивные разрывы и новые пересечения. Браузерный движок проверен в Chromium; другие браузеры отдельно не проверялись.
''')
print(json.dumps(audit,ensure_ascii=False,indent=2));print('Reference motion pilot: nine checked original proposals ready')
