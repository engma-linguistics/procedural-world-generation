---
id: PW-1259
title: "Overlapping demes: store every people's presence per frame, cut demes from it, show overlaps on the map"
type: task
status: todo
parent: PW-670
milestone: null
subsystem: timezoom
effort: l
impact: med
found_by: lane108
blocked_by: []
relates: [PW-981, PW-670, PW-924, PW-703]
refs: [planet/lineages/demes.py, planet/lineages/compose.py, planet/lineages/output.py, planet/lineages/cultures.py, viewer/lineages.html, "runs cc22df 622c00"]
created: 2026-11-01
updated: 2026-11-01
---

## Description
In plain words (Daniel, 2026-10-31): a kobold culture and a hobgoblin culture living in the same hills should be separate
demes that overlap, and dragons that range widely should have demes lying over the peoples below them. Demes are already
cut per people, so kobold and hobgoblin demes can overlap. But two limits get in the way:
- (a) The frames store only each cell's two leading peoples (peoples_whole, mix_lead, and mix_second at SECOND_MIN 10%,
  in compose.py). A third people in a cell is unseen. Megafauna rarely lead a cell, so they drop in and out of view. On
  cc22df the red dragons have 64 demes: 1 first deme and 63 that come back after a gap. The fire giants have 21.
- (b) layers/demes.bin holds one deme per cell (the leading people's), so the map cannot show overlaps.

Lane 108 left this as a draft because it needs a history storage change, a demes rework and a viewer change. That is too
much to do well alongside cultures round 2. Round 2 works around (a) for the cultures only: a cohesive kind's returning
pockets rejoin its first culture.

Plan:
1. **Fuller presence per frame** (history output; output.py writes the frames). For each line, including megafauna and
   excluding overlays, store the cells where its presence is at least PRES_MIN (say 5% of K, a judgement) as a sparse
   table. Per frame, use a CSR: line offsets, then uint16 cell ids at L6 (uint32 at L7) and a uint8 quantised presence.
   Size estimate: cells x share occupied x lines x frames x 3-5 bytes. At L6 with about 70 lines at about 2% occupancy
   each, that is about 57k entries a frame, about 170 KB, so about 22 MB for 129 frames. At L7 it is about 4x the cells
   and 5 bytes an entry, so about 110 MB. Measure the real occupancy first. Top-k per cell (k = 4) is the fallback if it
   is too big: 4 x (1 + 1 bytes) x cells x frames, about 42 MB at L6. Bitsets per line cost about 46 MB at L6 and lose the
   share.
2. **Demes from it** (demes.py `occupied`). When the run has the presence table, use it instead of the lead and second
   peoples, so every people that lives in a cell is cut, overlapping freely. Contacts then count co-presence (both peoples
   in the cell) as well as shared borders. Runs without the table keep the two-people data: no other back-compat path.
3. **Map layer for overlaps.** Store each people's deme per cell sparsely: the same CSR shape as 1, with a uint16 deme id
   in place of the presence. Or store per-people layers, written only for the cells it holds. Keep demes.bin as the
   leading people's view. The viewer gets a "whose demes" picker (default: the leading people). The Cultures tab's
   "map" link sets the picker to that culture's people. brief.py and cultures.py read the per-people layer when present.
4. **Re-runs.** Daniel's runs are not rebuilt. A re-run of a dnd tree would add the presence table. Its demes would then
   show the dragons and giants as steady, wide populations over the peoples, and third peoples in mixed cells would be
   counted.
- [ ] presence table in the history output, size measured on an L6 and an L7 run
- [ ] demes cut from it, contacts by co-presence
- [ ] per-people deme layer and the viewer picker

## Updates
- 2026-11-01: Created from inbox draft draft-megafauna-underseen-in-deme-frames.md (found by lane108).
