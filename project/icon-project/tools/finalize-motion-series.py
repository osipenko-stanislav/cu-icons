# -*- coding: utf-8 -*-
from pathlib import Path
from zipfile import ZipFile
import json,hashlib,collections
P=Path('icon-project');S=P/'motion/series';G=P/'gallery/motion-review';R=P/'review/motion/series'
catalog=json.loads((S/'catalog.json').read_text());config=json.loads((S/'motion.json').read_text());checks=json.loads((R/'checks.json').read_text());player=(P/'motion/assets/motion/player.js').read_bytes();svg={r['id']:(S/'svg'/f"{r['id']}.svg").read_bytes() for r in catalog};archives=list((G/'exports').rglob('*.zip'))
assert len(archives)==12*(len(catalog)+1)
for p in archives:
 with ZipFile(p) as z:
  assert z.testzip() is None,p
  assert z.read('player.js')==player,p
  motion=json.loads(z.read('motion.json'))
  assert not any(t[1]=='pulse' for s in motion['scenes'] for t in s['tracks']),p
  if p.stem=='pack':
   assert len(motion['scenes'])==1189,p
   for id,raw in svg.items():assert z.read(f'svg/{id}.svg')==raw,(p,id)
assert not checks['browser_failures'] and not checks['static_mismatches'] and not checks['clipped_frames']
for r in catalog:r['motion_review_status']='agent-reviewed';r['review_method']='Sequential raster sheet at 24px light/dark; 3-preset Chromium runtime checks and targeted Expressive frames'
(S/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
checks.update(visual_review='sequential: all 17 sheets at 24px light/dark; revised families rechecked',archives={'count':len(archives),'status':'pass'},static_inputs_unchanged=True)
(R/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
status={'total':1189,'animated':1189,'unprocessed':0,'pilot_approved':4,'series_pending_user_review':1185,'presets':['Smooth','Balanced','Expressive'],'default_preset':'Balanced','trigger':dict(collections.Counter(s['trigger'] for s in config['scenes'])),'start_end':'complete original SVG pose','opacity_animation':False,'static_inputs_unchanged':True,'static_approval_statuses_unchanged':True,'patterns':dict(collections.Counter(r['pattern'] for r in catalog)),'runtime':'Standalone shared JavaScript + editable JSON and SVG; Chromium verified','checks':{'preset_runs':checks['preset_runs'],'sampled_raster_frames':checks['sampled_raster_frames'],'static_equivalence_sizes':[16,24,32],'failures':0},'approval_scope':'User approved four-scene pilot and authorized all current SVGs for motion production. Remaining scenes are review candidates, not automatically user-approved.','release_status':'complete-motion-review-set','player_sha256':hashlib.sha256(player).hexdigest(),'balanced_pack_bytes':(G/'exports/balanced-1/pack.zip').stat().st_size,'runtime_correction':'Arrow translation moved to canvas coordinates; 64 vectors verified. Per-icon trigger guards and scale channels added. Approved pilot choreography retained.'}
(S/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
(S/'README.md').write_text('''# Анимационная библиотека — 1189 иконок

Галерея: http://127.0.0.1:8766/ (при запущенном локальном сервере).

Полный пак Balanced 1×: ../../gallery/motion-review/exports/balanced-1/pack.zip.
Другие пресеты и скорости доступны через галерею. В каждом архиве: svg/, geometry/, motion.json, player.js и автономный preview.html. Геометрия, части и дорожки доступны для редактирования.

Начальная и конечная позы полные. Способы запуска предложены по смыслу: только наведение, только нажатие или оба способа. В карточках можно изменить режим; выбор сохраняется в проекте и включается в скачивание через галерею. Сохранённые изменения — trigger-overrides.json; локальные ZIP на диске содержат исходные рекомендации, поэтому для актуальных настроек скачивать через галерею. При reduced motion сохраняется статичная поза. Это одноразовые демонстрационные реакции: их завершение не означает выполнения продуктовой операции.

Утверждён пилот из четырёх сцен. Новые 1185 сцен готовы к пользовательскому просмотру. Статические файлы и статусы их согласования не менялись. Поле filename в catalog.json сохраняет связь с исходным именем.

Дополнительные JSON-каналы scale/scale-x/scale-y меняют размер фигуры вокруг явной опоры. hover означает только наведение, click-replay — только нажатие, hover-click — оба способа. JSON-канал erase-redraw проводит dash и gap вдоль path: полный контур → стирание → появление → полный контур. Амплитуда пресета не обрезает крайние состояния этого канала. Игрок хранится в проекте, зависимости от фреймворка нет. Стандартный CLI-плеер навыка не поддерживает этот дополнительный канал: для сборки использовать tools/build-motion-gallery.py, для сервера — tools/serve-motion-local.py. Типовые движения назначены по семействам; это не 1189 уникальных хореографий.

Проверено: Chromium, все сцены в трёх пресетах, reduced motion, повторный запуск, полное восстановление, выборочные промежуточные кадры, 17 обзорных листов в светлой/тёмной теме на 24px, неизменность статичной позы на 16/24/32px, валидность SVG и архивов. Другие браузеры и реальные устройства отдельно не проверялись. Полный отчёт: ../../review/motion/series/checks.json.
''')
print(json.dumps(status,ensure_ascii=False,indent=2))
