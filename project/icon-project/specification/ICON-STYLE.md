# CU reference style · 1.0

## Brief and scope
Restyle the 1189 supplied work SVGs in the visual language of the 108 supplied reference SVGs. Original folders are immutable inputs. Static icons only. Keep source meaning, direction, modifiers, variant distinctions and original filename mapping. The pilot comprises 24 icons; all further production requires explicit user approval of the pilot and its current hashes.

## Evidence
Inspected all 108 original geometries in four reference contact sheets (24 and 64 px). Preview paint on these sheets is normalized to black; original SVGs remain unchanged. Measured reference viewBox: 24×24 for 108/108. Nearly all active strokes use SVG's implicit 1 unit width; two local width outliers (2 and 0.909091) are not global rules. Black and white copies are presentation variants, not separate styles. Many reference fills are expanded outlines from export; reproduce their visible contour using editable centerline strokes.

## Required rules
- Canvas and viewBox 24×24, transparent background. Default 1 unit live stroke, giving 1 px at 24 px and 0.667 px at 16 px. Small size review is advisory; do not silently thicken the established style.
- Monochrome currentColor output, allowing black/light preview and white/dark preview without changing artwork. This is an inferred implementation choice from the black/white references.
- Principal optical envelope typically 2–22; large arrows, books and people may extend toward 1–23.5. Keep painted bounds inside the canvas. Use half-unit coordinates where they improve horizontal/vertical edges.
- Most reference terminals and joins are round. Architectural outlines (home, book, rocket) also use butt caps and miter joins. Do not round every family indiscriminately.
- Distinctive rectilinear containers combine square corners with a 2–3 unit rounding at selected corners: document lower-left; monitor/chip upper-left; calendar upper-left and lower-right. Do not substitute a uniformly rounded rectangle throughout.
- Generous negative space, usually at least 1.5–2 units where lines are not intentionally joined. Inspect dense modifiers at 16 px. Preserve deliberate contour breaks and overlaps without opaque background cutouts.
- Use geometric arcs, simple lines and a small number of Bézier segments. Preserve organic source silhouettes where they already match (heart, bell). Do not simplify away meaningful teeth, weather marks or modifiers.
- Filled accents are limited to semantic dots (e.g. the question dot). No expanded strokes or filled rings used to imitate outlines.

## Family anchors
- arrow-left.svg and arrow-right.svg: long 20-unit shaft and broad chevron. Their filenames are reversed relative to the visible arrow direction; preserve work's actual direction.
- brand-home-lined.svg / home.svg: straight-sided pitched roof. The source home-01 has no door, so its restyle remains without a door.
- brand-doc-lined.svg / file.svg: asymmetric document corners. Preserve a source variant's fold/no-fold and text/no-text distinction.
- calendar.svg: opposing rounded corners and shallow header. The source calendar has no dates; retain a plain body to avoid collapsing it with calendar-date.
- brand-device-desktop-lined.svg: one rounded screen corner and detached low base.
- brand-chip-lined.svg: nested rectilinear outlines with one curved corner.
- profile.svg / users.svg / users-plus.svg: circular heads, broad dome bodies, clear overlaps and independent plus. Use live arcs for the occluded rear person instead of expanded-stroke fragments.
- message.svg / brand-message-lined.svg: asymmetric containers and restrained text. Preserve the tail side of the work variant.
- brand-shield-lined.svg: flat top, straight sides, pointed bottom and simple check.
- brand-rocket-lined.svg: geometric body and fins. Keep the diagonal orientation and launch trace of rocket-01.
- book.svg: open pages with upright outer edges and central seam. Reconstruct as live strokes; do not copy the exported outline mask.
- bell.svg / trash.svg: simplified readable silhouettes; keep distinguishing lines of the source variant.
- No exact gear, cloud, card or folder anchor exists. Infer their treatment from the container, line and density rules; include these in the pilot to review that extrapolation.

## Anti-examples
A uniform 1.5-to-1 width conversion misses container geometry. Uniform round rectangles miss asymmetric corner logic. Replacing all variants with the nearest reference destroys distinctions. Source arrows must not reverse to follow mislabeled ref filenames. Filled paths must not replace editable strokes.

## Review and tools
Target sizes: 16, 24, 32 px, plus 64 px inspection. Compare original / nearest reference / candidate, and check light/dark backgrounds. Visual critique is sequential by the same agent; no independent critic was used. Technical readiness and user approval are separate.

The installed skill CLI is run through tools/iconizer-local.py, a project-local renderer adapter because system librsvg/Cairo are unavailable on this Mac. Rendering uses resvg-py 0.2.0. Bounds are conservative alpha bounds rasterized at 1024 px, with about 0.024-unit quantization. They cannot prove absence of off-canvas geometry because the renderer clips; an independent enlarged-viewBox clipping check accompanies the pilot. No installed skill files were modified.
