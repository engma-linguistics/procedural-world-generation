---
id: PW-740
title: A peoples run spends ~4 of its ~5 minutes working out the world's land goods in memory (cache them in the world or on disk)
type: task
status: todo
parent: null
milestone: v2
subsystem: infra
effort: s
impact: med
found_by: fun7
blocked_by: []
relates: [PW-722, PW-721]
refs: [planet/lineages/land.py, planet/lineages/run.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
`land.goods(world)` works out the game attributes (and resources and coast forms, for worlds without them) in memory on every
`planet lineages` run: ~3-4 min at L7 for 1df1c3 / 3e9e7d, before a real-mode try that takes ~60 s once the recent pass has
its climates. The cache is per process, so a sweep in one process pays it once (tools like the fun7 sweep), the CLI and the
server's jobs every time. `fuels.py` and `landuse.py` call `goods` again (cached in the same process).
Options: (A) write the made game attributes into the world (`planet gameattrs WORLD`, already a command?) so
`land._layers` finds them, (B) pickle the goods next to the run store keyed by world id and code version, (C) leave.
- [ ] a peoples run on a world with its goods made costs the history, not the goods

## Updates
- 2026-10-24: Created from inbox draft draft-goods-cache-per-world.md (found by fun7).
