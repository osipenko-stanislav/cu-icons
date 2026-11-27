# useAnimations motion comparison pilot

13 explicitly retargeted scenes. Current project SVGs supply all visible production shapes; upstream timing and easing are preserved using the vendored SVG renderer. Original reference drawings are included only in the labeled review comparison.

Reference states and cycles were explicitly authorized by the user. Book is an exception: retain the existing mild squeeze without added pages.

Review: http://127.0.0.1:8766/exact-reference/

Status: pending user pilot approval; do not mark the entire 1189-scene collection as converted. 395 direct name matches across 184 source animations are candidates requiring explicit part mapping; the remainder needs semantic motion mapping.

Build: `/private/tmp/cu-iconizer-env/bin/python icon-project/tools/prepare-exact-reference.py`, then `.../python icon-project/tools/build-exact-reference.py`.

Balanced at 1x retains native source timing. Other presets affect duration; state endpoints remain fixed. Hover/click overrides persist in an isolated local collection namespace. Export embeds the shared player and both MIT notices, and remains offline.
