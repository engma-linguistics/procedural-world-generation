---
id: PW-406
title: Jet stream overlay draws the yearly mean upper wind everywhere; show the jet's core ribbon by season instead
type: task
status: done
parent: null
subsystem: viewer
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-156]
refs: [viewer/index.html, planet/world.py, planet/store.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Owner: the "Jet stream" overlay shows arrows over most of the planet, but a weather map's jet stream is a single meandering ribbon. Why: the overlay is the yearly average of all upper-level winds (`jet_e/jet_n`), drawn as arrows everywhere. A weather map shows one day's jet: the fast core (> ~30 m/s) that meanders in 3-6 Rossby waves which move from day to day. Averaged over a year the meanders cancel into a smooth band, so a mean climate can't show them.

Fix (viewer, no physics):
- Draw only the core, where upper wind exceeds a threshold (~25-30 m/s), as a ribbon along the speed maximum, for January and July separately, as the jet shifts poleward in summer. It should be wavy where mountains and land-sea contrasts bend it.
- Rename the overlay "Jet stream (seasonal core)".

The day-to-day meandering jet belongs to the weather generator (PW-156): add a note there that a "typical day" snapshot with Rossby waves is one of its first outputs.

## Updates
- 2026-10-16: Owner (2026-10-16 night): drop the jet stream overlay. A real jet changes by the hour, so a Myr-scale mean is not worth drawing; a jet view waits for single-day weather (PW-156). Overlay removed from the viewer. The stored jet layers stay: they're small, and a physics test uses them. Upper-air simulation stays (coordinator's call): it places the storm tracks, rain belts and subtropical deserts.
- 2026-10-16: Status todo -> done. The overlay is "Jet stream (seasonal core)" (`jetCore` in viewer/index.html).
  It draws ribbons (3 px) where the half-year mean upper wind is at least 25 m/s (or 70% of the season's peak) and
  no faster a cell spacing to either side across the flow, each cell joined to the next core cell downwind; pieces
  under 6 cells are dropped. January is blue, July orange; the season picker shows one. Worlds now store `jet_jul_e/n`
  and `jet_jan_e/n` (planet/world.py, store.py), so worlds made before this, and runs (keyframes hold only the
  year's mean), draw one violet ribbon for the year. On an L6 test world (seed 7, since deleted) each hemisphere's
  winter jet is a continuous band; the Southern Hemisphere's July jet bends over the continents, and in July there is
  also an equatorial (tropical easterly) core. The model's mean jet is quite zonal, so the meanders are small; the
  day-to-day Rossby waves stay with PW-156 (its note is already there).
- 2026-10-16: Created from inbox draft draft-jet-stream-core.md (found by daniel).
