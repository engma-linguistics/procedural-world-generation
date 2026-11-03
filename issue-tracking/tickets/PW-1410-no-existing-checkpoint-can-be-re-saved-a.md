---
id: PW-1410
title: "No existing checkpoint can be re-saved: all 68 runs' checkpoints lack state fields added since they were written"
type: task
status: todo
parent: null
milestone: v2
subsystem: store
effort: xs
impact: low
found_by: lane 149
blocked_by: []
relates: [PW-1390, PW-1035]
refs: [tools/resave_checkpoints.py, "planet/tectonics/simulation.py::Simulation.STATE", "planet/timeline.py::replay", docs/review/peoples/den-raids/round1.md]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: PW-1408 assumed the old checkpoints fail only because PW-1390 changed how the plates are stored, so a one-off
conversion would make them usable again. They fail for a bigger reason. Every checkpoint under runs/ (687 files in 68 runs; 6 more
runs have a state/ folder but no run.json) lacks fields the simulation has gained since: the newest runs (1 Nov) lack `sea_sed` and
`sed_water_ref` (PW-950, merged 3 Nov), older ones also `climate_in`, `ice_warm`, `cont_water_ref`, `sea_cont` and, the oldest,
`ice_share`, `npp_*`, `shade_*`, `sst`, `star_ctl`, `wv_*`, `pot_*`. Even the pre-PW-1390 code (cfd7d1cf) cannot resume from them
(`load_state` reads every name in STATE), so `replay` was already falling back to t=0 for all of them before PW-1390. The missing
fields (the start's ocean-floor sediment water, the climate caches) cannot be rebuilt from the file, and filling in defaults would
make a replay that is not the run's.

What was done: `tools/resave_checkpoints.py` converts old-format checkpoints that do hold the full state (verify-then-rename, entry
by entry against the old code's state, see below). It found nothing to convert in runs/: 0 converted, 687 left as they are, 6 runs
skipped (no run.json). It was proven on a fresh run made by the old code (L5, 300 Myr, 3 checkpoints): all 3 converted, read back
identical, and a slice at 125 Myr from the converted checkpoint equals the slice replayed from t=0 (only ids and creation times
differ). Nothing under runs/ was written.

So for runs Daniel keeps, the way to fast slices is a re-simulation (`planet simulate`; checkpoints then include the current state), or
accepting t=0 replays. The same will happen at every future change to STATE: each such change strands the earlier runs' checkpoints.
- [ ] decide which runs to keep and re-simulate them (or delete the runs; outputs are freely deletable)
- [ ] close PW-1408 with this finding; keep `tools/resave_checkpoints.py` for a future format-only change (it stops with "lacks state" otherwise)
- [ ] optional: have `planet simulate`/`replay` say once, in plain words, that a checkpoint is from older code and the run replays from t=0

## Updates
- 2026-11-03: Created from inbox draft draft-all-old-checkpoints-lack-state.md (found by lane 149).
