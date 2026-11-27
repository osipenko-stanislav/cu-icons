"""Build a static GitHub Pages view and a reproducible project snapshot."""
from pathlib import Path
import shutil,json,hashlib
W=Path.cwd();P=W/'icon-project';D=Path('/private/tmp/cu-icons-publish-20261127');S=D/'site';S.mkdir(exist_ok=True)
for name in ['scenes.json','player.js']:shutil.copy2(P/'gallery/motion-review/reference-series'/name,S/name)
shutil.copy2(P/'publication/github/static-export.js',S/'static-export.js');shutil.copy2(P/'motion/reference-series/export.html',S/'export-template.html')
(S/'licenses').mkdir(exist_ok=True)
for source,name in [(P/'references/motion/useanimations/LICENSE.txt','useAnimations-MIT.txt'),(P/'motion/exact-reference/vendor/LICENSE.lottie-web.md','lottie-web-MIT.md')]:shutil.copy2(source,S/'licenses'/name)
s=(P/'gallery/motion-review/reference-series/index.html').read_text().replace('<script src="player.js">','<script src="static-export.js"></script><script src="player.js">');s=s.replace('<p><a href="/exact-reference/">Сравнение с useAnimations</a> · <a href="/previous-series/">Предыдущая анимация</a></p>','<p><a href="https://github.com/osipenko-stanislav/cu-icons">Исходники на GitHub</a> · <a href="downloads/cu-icons-balanced-1x.zip" download>Готовый пак · Balanced 1×</a></p>');s=s.replace('Не удалось скачать пак. Откройте галерею на localhost и повторите.','Не удалось собрать пак. Обновите страницу и повторите.');s=s.replace('Выбор сохранён в браузере. Для сохранения в проекте откройте галерею на localhost.','Способ запуска сохранён в этом браузере.');(S/'index.html').write_text(s)
(S/'downloads').mkdir(exist_ok=True);shutil.copy2(P/'exports/current/cu-icons-balanced-1x.zip',S/'downloads/cu-icons-balanced-1x.zip');shutil.copy2(P/'exports/current/status.json',S/'version.json')
# Preserve source/review history, excluding regenerated ZIP permutations and raw
# browser frame dumps. They remain in the original local project.
def ignore(path,names):
 out={n for n in names if n in ['.DS_Store','__pycache__','.manifest.lock'] or n.endswith('.pyc')}
 rel=Path(path).relative_to(W)
 if rel==Path('icon-project/gallery'):out.update(n for n in names if n!='motion-review')
 if rel==Path('icon-project/gallery/motion-review'):out.update(n for n in names if n!='reference-series')
 if rel==Path('icon-project/gallery/motion-review/reference-series'):out.update(n for n in names if n not in ['index.html','scenes.json','player.js'])
 if rel==Path('icon-project/review'):out.add('cache')
 if 'review' in rel.parts:
  out.update(n for n in names if n in ['browser-capture.json','browser-frames.json','frames.json','browser-checks.json','before-frames.json','after-frames.json'])
 if rel==Path('icon-project/motion'):pass
 if 'exports' in rel.parts and rel!=Path('icon-project/exports') and rel!=Path('icon-project/exports/current'):out.update(names)
 if rel==Path('icon-project/exports'):out.update(n for n in names if n!='current')
 # Historical per-preset download permutations are generated artifacts.
 if 'gallery' in rel.parts:out.update(n for n in names if n in ['exports','downloads'])
 return out
project=D/'project';project.mkdir(exist_ok=True)
for name in ['icon-project','ref','work']:shutil.copytree(W/name,project/name,dirs_exist_ok=True,ignore=ignore)
# Local project paths remain unchanged inside project/; run tools from there.
(D/'README.md').write_text('''# CU Icons

Текущая версия от 27 ноября 2026: **902 активные иконки**, 306 альтернатив сохранены отдельно в архиве проекта.

**[Открыть галерею](https://osipenko-stanislav.github.io/cu-icons/)** · [Скачать готовый пак](site/downloads/cu-icons-balanced-1x.zip)

Анимации, темы, размеры, пресеты и выбор запуска работают в статической галерее. Пак или отдельная иконка собираются в браузере с выбранными настройками, префиксом и суффиксом. На каждый размер используется одна и та же анимация. Пользовательские правки и способы запуска сохраняются в браузере; сервер не требуется.

## Структура

- `site/` — публикуемая галерея GitHub Pages, актуальные данные, проигрыватель и ZIP.
- `project/icon-project/` — исходники, спецификации, активный каталог, архив альтернатив, инструменты и результаты ревью.
- `project/ref/`, `project/work/` — неизменённые исходные SVG.

Старый набор 233 иконок и прежняя галерея доступны в истории Git. Архивные альтернативы не возвращаются в текущую галерею.

## Запуск

Статическая версия: `python3 -m http.server 8765 --directory site`, затем http://localhost:8765/.

Полный рабочий проект расположен в `project/`: команды локальных инструментов запускаются из этой директории. Для Python-инструментов требуется cu-iconizer и его окружение; инструкция сохранена в `project/icon-project/README.md`. Готовая статическая галерея и ZIP не требуют Python-зависимостей проекта.

## Состояние

Исправлены ошибки наследования цвета в 22 сценах и зависания при скрытии/смене reduced motion. Усилены 15 жестов и перестроены пять переходов Play/Pause. Новые варианты технически проверены и ожидают визуального одобрения пользователя. Данные: [последнее ревью](project/icon-project/review/motion/stability-2026-11-27/README.md), [версия пака](site/version.json).

Генерируемые исторические ZIP-перестановки и сырые дампы браузерных кадров не включены; текущий пак, исходники и отчёты сохранены. Лицензии используемых анимационных библиотек находятся в `site/licenses/` и внутри ZIP. Собственная общая лицензия на библиотеку в этой публикации не назначается.
''')
(D/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=site/"><a href="site/">Открыть актуальную галерею</a>')
(D/'.gitignore').write_text('.DS_Store\n__pycache__/\n*.pyc\n.venv/\n.manifest.lock\n.env\n.env.*\n')
p=D/'.github/workflows/pages.yml';s=p.read_text().replace('path: .','path: site');p.write_text(s)
files=[f for f in D.rglob('*') if f.is_file() and '.git' not in f.parts];size=sum(f.stat().st_size for f in files);status={'files':len(files),'bytes':size,'active_scenes':902,'repository':'osipenko-stanislav/cu-icons','site_path':'site','pack_sha256':hashlib.sha256((S/'downloads/cu-icons-balanced-1x.zip').read_bytes()).hexdigest()};(P/'publication/github/preparation.json').write_text(json.dumps(status,indent=2)+'\n');print(status)
