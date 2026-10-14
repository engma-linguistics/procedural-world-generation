---
id: PW-143
title: "Cloud cover: a diagnostic cloud fraction per season (and its effect on sunshine and temperature)"
type: task
status: todo
parent: PW-013
subsystem: climate
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: [PW-142]
refs: [planet/climate.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner (2026-10-14): there is no cloud layer. The rain model already has what clouds need: humidity relative to saturation (rh, rh_c), rising motion (convection from moist static energy, uplift on windward slopes, fronts) and stable air (deserts, cool seas). Add a diagnostic cloud fraction per half-year: high where air is near saturation and rising (ITCZ, storm tracks, windward mountains, monsoon summers), low under subsiding dry air (subtropical deserts), and marine stratocumulus over cold upwelling seas off western coasts (Namibia, California, Peru). Store cloud_jul/jan on worlds, with a viewer layer, and derive sunshine (hours or fraction) for highlights (PW-142, the beach finder). Phase 2 (physics depth): let clouds feed back on temperature (shade by day, warmth at night, so a smaller daily range under cloud) and on snow/ice melt. Check against Earth's cloud climatology (e.g. ISCCP/MODIS annual means) via tools/earth_check.py as an analogue, not a parity target.

## Updates
- 2026-10-14: Created.
