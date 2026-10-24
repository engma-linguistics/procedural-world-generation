---
title: A peoples run's minutes are the history loop (animals, crops, habitat), not the land's goods; the cached goods and climates leave ~6 of ~9 min
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun8
blocked_by: []
relates: [PW-740, PW-722]
refs: [planet/lineages/history.py, planet/lineages/animals.py, planet/lineages/crops.py, planet/lineages/recent.py]
---

## Description
PW-740 assumed the land's goods took ~4 of a peoples run's ~5 minutes. Measured on world 1df1c3 at L7 (run `--tries 1`,
the box under load 11-16): `land.goods` is 3-4 s when the world already has its game attributes, resources and coast
forms (it does; `made` is empty), not minutes. The progress label "the land's goods" stays on screen while
`History.__init__` computes the recent pass's 16 full climates (`recent._climate`, ~100-125 s), which is what looked
like the goods. Both are now kept on disk (PW-740): goods in `worlds/goods/<id>.npz`, the climates in
`runs/<timezoom>/recent_rain.npz`, each keyed by file stats and a digest of the model source.

Result: a CLI run went 8.5-9 min cold to 6.2 min warm. What remains is the step loop (cProfile of a `--tries 1` run,
total 512 s): `History.run` 381 s of which `animals.step` 78 s (6435 calls, mostly in one function), `crops.step` 67 s
(450 steps), `history._K` 53 s, `_wishes`/`_stepmask` 40 s. The tries each repeat all of it.
- [ ] profile `animals.step` and `crops.step` (the spread sweeps each step) and vectorise or do them every Nth step
- [ ] share the world-and-time-zoom-only inputs between tries (the habitat fields per step do not depend on the seed)
- [ ] label the progress "recent pass: full climates" instead of "the land's goods" while the climates run
