---
id: PW-110
title: Lakes cover ~1.8x more land since the hierarchical MIN_DEPTH fill; keep, or add a shore rule?
type: task
status: done
parent: null
subsystem: hydrology
effort: s
impact: med
found_by: hydrofix
blocked_by: []
relates: [PW-058]
refs: [planet/hydrology.py, planet/kernels.py, "run 28e6be", "run a61cd5", "world 84ce45", docs/review/lakes/]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-058 replaced the per-cell 20 m MIN_DEPTH test (`filled - ground < 20` against
the basin's final spill level) with `kernels.fill_shallow`, which fills shallow
hollows per basin, at every saddle. Side effect: the old test also raised every
cell of a deep basin that lay within 20 m of the spill level to the spill
level, so those rim cells could never be under a lake. Now a deep basin's lake
covers every cell below its surface, so lakes are bigger:

- Same terrain (checkpoints of 796a25, 01b0f7, 07fb28, every 200 Myr): closed-lake
  cells 338 -> 927, open-lake cells 1309 -> 2972.
- Seed 13, L6, 600 Myr (a61cd5 before, 28e6be after): open + closed lakes
  0.9% -> 1.6% of land, averaged over all frames (Earth: ~1.8% incl. the Caspian).
- Earth check (L6): lake cells 517 -> 687; closed basins 21% -> 22% of land;
  big-river discharge 3-20% lower (more lake evaporation); Nile with GPCC rain
  2.65 -> 0.10 of observed (it ends in a lake either way).
- Flat basins just over 20 m deep now hold very large shallow lakes, e.g. world
  84ce45 (run 28e6be @ 240 Myr): biggest salt lake 2.9 million km^2 (the old code
  had the same lake there, broken into ~20 speckled pieces).

Options:
- A. Keep (lean): a lake covering everything below its level is the consistent
  rule, and the totals are in Earth's range.
- B. Shore rule: cells less than X m (5-10) below the lake surface count as
  marsh/shore (not drawn as lake, no open-water evaporation). Shrinks lake
  outlines, but a per-cell threshold on a rough floor speckles again near X.
- C. Scale the whole-basin drain threshold with basin area (a 1500 km wide
  basin 22 m deep is very flat), so huge flat basins drain unless they are
  clearly deep.

Minor, same area: two lobes of one closed lake can stay separate pieces when
the lake stops exactly at the height of a broad flat saddle (28e6be @ 200 Myr
(20.7,-177.3): two ~100-cell lobes at 648.1 m joined by dry cells at
648.05-648.25 m). It's correct shoreline behaviour, but it reads as two lakes.

Coordinator notes (intake): a 2.9 million km^2 salt lake is ~8x the Caspian (0.37 million km^2), so option C (scale with basin size) deserves weight even if the global total is Earth-like. Also the Earth check's Nile at Khartoum went 2.65 -> 0.10 of observed (before: too wet, now: too dry, as an upstream lake evaporates almost all of it); check which lake, since the real Nile passes the Sudd and still delivers ~2800 m^3/s.

## Updates
- 2026-10-14: Status todo -> done. A + C (lakesize): kept the consistent rule; added hydrology.MIN_SLOPE = 0.1 m/km, so a basin must be max(20 m, 0.1 m/km x sqrt(area/pi)) deep at its rim to hold water (kernels.fill_shallow tracks basin area). Earth's L6 artefact basins (Sudd 0.09, W Siberia 0.10, Amazon 0.11 m/km) drain; real closed basins (>= 0.2) unchanged, closed-basin share 22%. Same terrain (24 checkpoints): lake share 1.76 -> 0.90% of land, lakes > 1M km2 13 -> 2, single-cell lakes 337 -> 324 (no speckle back). World 84ce45's 2.8M km2 salt lake drains (largest lake there now 840k). Run c3bf56 vs 28e6be: lake share 1.63 -> 0.96%, frames with a lake > 1M km2 40 -> 13%. Nile: the Sudd was a 250k km2 closed lake (27 m deep, 274k km2 hollow) swallowing the White and Blue Nile; GPCC Nile at Khartoum 0.10 -> 2.78. Lake-share drop: inbox draft (needs-decision).
- 2026-10-14: Status needs-decision -> todo. Owner decision: A + C. Keep the consistent rule (a lake covers everything below its surface) and scale the whole-basin drain threshold with basin size so huge, very shallow basins drain. Also investigate the Earth-check Nile drop (2.65 -> 0.10 of observed at Khartoum).
- 2026-10-14: Created from inbox draft draft-lake-area-after-hierarchical-fill.md (found by hydrofix).
