---
id: PW-936
title: Megafauna reach under half their core country for about half the kinds (hill giants ~0.1, red dragons ~0.25)
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-37
blocked_by: []
relates: [PW-924, PW-923]
refs: [planet/lineages/history/megafauna.py, planet/lineages/samples/dnd.toml, "world 2a7385, dnd 7000-7002"]
created: 2026-10-27
updated: 2026-10-28
---

## Description
After the PW-924 fixes, `suitable` is the kind's core country (its prefers; elsewhere its habitat is x MEGAFAUNA_OFF 0.1), and
scatter founds pockets at SCATTER_RATE 1.0/kyr within 5 reaches. On 2a7385 dnd 7000-7002 at 1 per 5,000 km2, 5-7 of 15 kinds reach
>= 0.5 of their core country (target ~70%). Short across all three seeds: hill giants 0.09-0.11, cloud giants 0.16, red dragons
0.24-0.35, copper 0.2-0.35, gold 0.34-0.46, frost and fire giants 0.1-0.5. Met: blue, green, brass, bronze, white; storm giants on
two of three. The raised scatter rate gained ~2 kinds; most of the remaining gap is not reach. Likely causes to check: the
viable-number fade (`_viable` with line_mvp) clearing new small pockets; competition among overlapping megafauna (copper vs hill
giants on hills, red vs fire giants); core patches on landmasses a walker cannot reach (giants walk, 800 km).
Green dragons run to ~4,000 at 1 per 5,000 (forest is most of the land); a narrower country (old or deep forest) would bring them
into the few-hundred band.
- [ ] a per-kind diagnosis: core patches reached, founded and then faded, against those never reached
- [ ] ~70% of kinds at suitable_reached >= 0.5 on the 2a7385 seeds

## Updates
- 2026-10-28: Status todo -> done. Merged 94c5a318: megafauna coverage 48 -> 106/116; recurring remnants follow up in PW-964.
- 2026-10-28: 10-28: giant_km2 default 5,000 (lane 38) is 15-35x sparser than forager-scaled giants (1/130-345 km2, docs/proposals/megafauna-scaling.md) and 50-150x sparser than culinary-dnd's herding giants (1/30-100 km2); owner decision drafted (inbox draft-megafauna-7-giant-density-reconcile).
- 2026-10-27: Created from inbox draft draft-megafauna-coverage-short.md (found by fun-lane-37).
