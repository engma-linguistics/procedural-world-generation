---
id: PW-406
title: Jet stream overlay draws the yearly mean upper wind everywhere; show the jet's core ribbon by season instead
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-156]
refs: [viewer/index.html]
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
- 2026-10-16: Created from inbox draft draft-jet-stream-core.md (found by daniel).
