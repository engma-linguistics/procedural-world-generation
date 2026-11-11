---
id: PW-1720
title: "Machine-aware setup: probe cores, RAM, disk and GPU, write presets (level, jobs, tile cap, memory caps, L8 and 2 Myr gates) and show them in a viewer Machine panel"
type: story
status: todo
parent: null
milestone: v1.0
subsystem: infra
effort: l
impact: med
found_by: plan-v1-lane
blocked_by: []
relates: [PW-1678, PW-1691, PW-1661]
refs: [docs/review/plan/milestones-to-v1.md, planet/tiles.py, planet/api.py, planet/make.py, docs/coordination.md, docs/wiki/decisions.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: owner 2026-11-11 stretch goal: the installer knows roughly what machine it is on, and allows, warns about or switches off the heavy features, so a smaller machine never tries a 69 GB job.

If it is never done, every install gets Threadripper defaults: `--jobs 4`, a 60 GB tile cache, 3 tile builds at once, and L8 splits and 2 Myr offered. On a 16–32 GB machine those run out of memory (L8 split at 2 Myr: 69.3 GB; level-1 tile: 8.3 GB + 8 GB spare).

The tier table and its sources are in docs/review/plan/milestones-to-v1.md section 4. The thresholds are estimates for this ticket to tune.
- Probe: os.cpu_count, RAM (/proc/meminfo, or sysctl on macOS), free disk on PLANET_DATA, and the GPU (coarse: lspci or nvidia-smi). On first open the viewer reports WebGL2 limits and the renderer string.
- Presets in config.toml: default level, `--jobs`, tile AT_ONCE, PLANET_TILE_CACHE_GB, a per-process memory cap (RLIMIT_AS, or systemd-run MemoryMax on Linux), and feature gates (L7 peoples, LOD tile levels, refine L8 and L9, L8 split at 1 or 2 Myr, time zoom length).
- The server and `planet make` read the gates, and a disallowed request returns a clear message, not an OOM.
- A Machine panel in the viewer's settings lists each feature as allowed, warned or off, with the deciding number, and lets the user override a warning.
- Minimum machine (proposed): 8 cores, 32 GB, 100 GB free, WebGL2. Recommended: 16+ cores, 64 GB, 250 GB SSD, a GPU with 4 GB or more.

- [ ] On a 32 GB machine, or one simulated with a capped cgroup, the presets switch L8 splits off and run tiles one at a time, and nothing OOMs on the v1.0 walk
- [ ] The Machine panel shows the probe and the gates; an override is remembered

## Updates
- 2026-11-11: Created from inbox draft draft-machine-aware-presets.md (found by plan-v1-lane).
- 2026-11-11: Lane 313: probe, presets, gates (server, `planet make`, refine estimate, lineages, tile service), `planet self probe`, first-run probes, `self open` capped at mem_cap_gb, Machine panel with overrides (docs/review/plan/machine-presets.md, tests/test_machine.py). Checked under a 24 GB cgroup: L8 splits off, tiles one at a time, L8 make refused with the reason. Not run: the full v1.0 walk on a 32 GB machine.
