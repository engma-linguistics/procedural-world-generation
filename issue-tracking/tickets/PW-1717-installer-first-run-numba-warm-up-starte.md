---
id: PW-1717
title: "Installer first run: numba warm-up, starter world (generate L6 by default, download optional), optional voice and Earth data"
type: task
status: done
parent: null
milestone: v1.0
subsystem: infra
effort: m
impact: high
found_by: plan-v1-lane
blocked_by: []
relates: [PW-1439]
refs: [docs/review/plan/milestones-to-v1.md, README.md, planet/make.py, planet/language/speak.py, docs/coordination.md, data/language/tts, data/earth]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: the first time a new install opens, it should compile what it needs, make a first world and show it, instead of an empty start screen and a long silent pause on the first click.

numba is JIT-compiled with cache=True at 190 sites, so the first run of each kernel compiles. Nobody has measured how long that takes from cold. If this is never done, a new user's first `make` stalls for an unknown time, and the viewer opens on nothing.

- A warm-up at level 4 for a few Myr runs in a scratch data folder; measure and record the time.
- Starter world by default: `planet make --seed 7` at L6 (~6 min per README). The progress shows in the viewer.
- A downloadable sample is optional, and only after measuring what one finished world plus the run layers it needs weighs. An L7 run is 2.7 GB (runs/a19366), too big.
- Optional extras, each with its size shown: the piper voice (data/language/tts, 121 MB; espeak is the fallback) and the Earth datasets (data/earth, 1.8 GB; only for the Earth reference world). Check whether data/language/raw (161 MB) is needed at runtime or only by tools.

- [ ] Cold first launch to an open L6 world, timed on two machines; the numbers recorded in docs/coordination.md
- [ ] The viewer shows first-run progress (Daniel uses the viewer, not the CLI)

## Updates
- 2026-11-11: Status todo -> done. merged (lanes 304/306)
- 2026-11-11: Created from inbox draft draft-installer-first-run.md (found by plan-v1-lane).
