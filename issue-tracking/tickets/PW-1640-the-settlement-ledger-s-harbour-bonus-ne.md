---
id: PW-1640
title: "The settlement ledger's harbour bonus never fires: the harbour layer is on sea cells, the ledger reads it on the land coast"
type: task
status: done
parent: null
milestone: v5
subsystem: peoples
effort: s
impact: med
found_by: lane270-pw1627
blocked_by: []
relates: [PW-1627, PW-1630, PW-1011]
refs: ["planet/lineages/settlements.py::_site_factor", "planet/lineages/settlements.py::derive", "planet/lineages/history/polity_live.py::LivePolities._site", "planet/humanuse.py::harbours", "world 899985", "world 69958b (899985 refined to L8, lane 270 scratch root l270/root, may be gone)"]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words
A town on a good natural harbour is meant to grow bigger and to keep more of its fishers settled. The harbour map marks the
harbour water (sea cells), but the town rules look for the harbour on the shore's land cell, so they never find one: no town
on any world gets its harbour bonus. Coastal towns are undersized against river towns, on every grid.

## Description
`humanuse.harbours` writes `harbour` (0-3) on sea cells ("natural harbours at sea", the layer's spec). `settlements._site_factor`
adds `SITE_HARBOUR[harbour]` only where the cell is `coastal` (a land cell next to the sea), and `derive`'s settled share adds
`FISHER_SHARE` on `(harbour > 0) & coastal`. A cell is never both, so both terms are zero. Measured (lane 270, `hbcheck.py` /
`coastcmp.py` in the lane's scratch): world 899985 (L7) has 1,161 harbour cells, 0 on land, 0 on its 7,182 coast cells; its
refined L8 world 69958b has 2,307, again 0 on land. On the old split run (025b98) 16% of the L8 harbour cells happened to fall on
the prolonged frame's coast (the frame coast was off by a cell), so the bonus fired there only by accident; lane 270 aligned
that coast, which also ends the accident. The live polities' `_site` reads the same function.

Fix (small): take each coastal land cell's harbour as the best of its sea neighbours' (`nbr_reduce(max)` over sea neighbours)
in `_world_layers` or `_site_factor`. This changes every L7 ledger (more and larger coastal towns), so it needs its own golden
update and a before/after on Earth-like A; it is not a grid question, which is why lane 270 left it.

If never done: every world's coastal towns lack the harbour and fisher terms the rules describe, so ports are rarer and smaller
than the model claims and the coast-vs-river balance of towns (a number lanes compare) is biased toward rivers.
- [x] harbour read from the sea neighbours of a coastal land cell (ledger and live polities)
- [x] before/after coast share and harbour towns on Earth-like A L7

## Updates
- 2026-11-10: Lane 272 (commit 2a2876cd): `settlements.coast_harbour` gives each coastal land cell the best harbour of its neighbours that are sea at that frame; the ledger's site factor and fishers, and polity_live's `_site` and central places, read it. Goldens do not cover the ledger (unchanged). Before/after on Earth-like A L7 (run 732ed6, dnd, one try; it reproduces lane 270's 2e0a95 exactly; the "before" is the same run's ledger redone with main f16cf7a7's code, the control redo with the fix reproduces the run's own ledger byte for byte), read on 899985's own coast (12.3% of the land; 5.75% of the land is coast beside a harbour): villages/towns/cities 22,399/6,170/283 -> 22,493/6,209/286; towns+cities on the coast 14.8% -> 15.2%; beside a harbour 7.0% -> 7.45%; small islands (< 0.3 Mkm2) with a town 20 -> 21; on rivers 46.4% -> 46.1%; people unchanged (1,042 M; the history does not read the ledger, live polities are off). Read on the L8 refine 9cf1c3: coast 7.3% -> 7.6%, ~60 km band 14.8% -> 15.2%, islands 21 -> 22. A small, real effect: the bonus is +0.15..0.4 on a cell that must still be the best of its 60 km ring, and harbour coast is rare.
- 2026-11-10: Created from inbox draft draft-ledger-harbour-on-sea-cells.md (found by lane270-pw1627).
