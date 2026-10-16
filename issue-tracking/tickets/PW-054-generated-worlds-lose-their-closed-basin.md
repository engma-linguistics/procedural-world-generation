---
id: PW-054
title: Generated worlds lose their closed basins over time
type: task
status: todo
parent: null
subsystem: tectonics
effort: l
impact: high
found_by: water
blocked_by: []
relates: [PW-056]
refs: [planet/tectonics/, planet/surface.py, docs/review/rivers_lakes_deltas.md, planet/tectonics/isostasy.py, planet/hydrology.py]
created: 2026-10-14
updated: 2026-10-16
---

## Description
Generated worlds have almost no closed (endorheic) basins after ~150 Myr: 0–4% of land drains inland,
against ~20% on Earth's terrain (the model gets 21% on Earth). Sediment and erosion fill every hollow,
and the tectonics makes no new interior basins: foreland basins, intermontane basins (Tarim, Altiplano),
rift-flank highs. Needs tectonic sources of basins, possibly less filling.

## Updates
- 2026-10-16: After PW-299 (2026-10-16): L6 inland 4.9 -> 4.2%, L7 8.8 -> 6.0% (L7/L6 1.8 -> 1.4). Hollows mostly come from plate motion/resampling (PW-359) and refill within a few Myr.
- 2026-10-16: Basins-lakes lane (health frames after 50 Myr, 500 Myr): inland drainage L6 8 seeds 4.9 -> 4.2% with PW-299 (floodplains no longer build hollow rims, so hollows fill), L7 seeds 3199/21/11 8.8 -> 6.0%. Without the flexural moat (diagnostic) L6 falls to ~3.7% (raw measure 6.4 -> 3.7). Hollow budget: plate resampling (resolve) makes most closed-hollow volume per step and erosion refills it (draft). Giant closed lakes count 10-25 Mkm2 catchments as inland; a fix for humid open-water evaporation (draft) would lower inland further. docs/review/audit/basins-lakes.md.
- 2026-10-15: Context from PW-302 (wontdo): run stream-power incision on headwater cells falls with grid level (2.2 / 1.6 / 1.1 m per 2-Myr step at L5 / L6 / L7, synthetic continent) because finer cells resolve smaller catchments; hillslope term is level-consistent (2.5 m). Total lowering 9.4 / 8.8 / 8.3 m per step. Likely part of why L7 and L6 inland-basin shares differ; a sub-cell headwater channel term is the option if it matters here. Details: docs/review/audit/fixes-surface-hydro.md.
- 2026-10-15: Post-audit 1 Gyr sweep: inland drainage medians L6 3.5-5.2%, L7 6.2-7.7% (Earth ~18%); part is PW-239 (frames no longer stale), part PW-280/PW-266. Still the open problem.
- 2026-10-15: After the audit fixes: L6 inland drainage 7.3-7.9% (below the 8% envelope; Earth ~18%), L7 16.3%. Basins now pass excess load over their rims (PW-280), so they fill less from overload but drain more.
- 2026-10-15: Status in-progress -> todo. Tect2 (merged): flexural moats beside belts and McKenzie thermal sag after rifting (isostasy.subsidence). L6 inland drainage 5.6-7.1% -> 8.4-9.9% (arid land 10-12% -> 16.5-17.7%); L7 ~20% (unchanged, already near Earth). Remaining: L6/L7 gap and back-arc/pull-apart basins (new tickets).
- 2026-10-15: Status todo -> in-progress. Worktree tect2.
- 2026-10-15: Status in-progress -> todo. Hydro (merged): diagnosis: 2/3 of closed-hollow loss is sediment infill, 1/3 rim wear; the rest needs tectonic subsidence (flexural and sag basins) - see merged draft. Back to the tectonics queue.
- 2026-10-15: Merged inbox draft draft-basins-need-subsidence.md ("Closed basins need tectonic subsidence (flexural foreland / intermontane basins, sag basins) to reach Earth's ~18% inland drainage", found by hydro).
  Follow-up of PW-054 from the hydro branch (measured with a per-step basin budget, L6, seeds 11 and 12,
  400 Myr; script in the hydro job's tmp dir, basin_diag.py):
  - Closed hollows (kept basins draining inland) lose volume to **deposition ~2/3** (the whole catchment's
    load stays in them: ~20-30% of all land deposition lands in the ~5% of land that drains inland) and to
    **erosion ~1/3** (rims wearing down, headward capture). A closed hollow is refilled in ~10-20 Myr;
    only tectonics makes new ones.
  - PW-055 (hydro: outlets cut down, so big through-flowing lakes no longer trap sediment and fill their
    hollows flat) doubled the terrain's closed-hollow potential (land that would drain to a kept hollow:
    17% -> 33-35%; Earth's L6 terrain 43%) and the land draining inland (3.9 -> 8.5%, 5.2 -> 10.6%, frames
    after 100 Myr). Earth: ~18%.
  - Upper bound from the surface side: deleting *all* deposition in closed basins gives ~12%. Blowing 40%
    of arid closed basins' deposits away as dust (deflation) gave nothing measurable (6.4% vs 8.5%, noise).
    So the rest must come from basins that subside.
  On Earth closed basins persist because they sink as fast as they fill (Tarim, Qaidam, Great Basin,
  Altiplano: 0.1-0.5 mm/yr), which the model lacks: isostasy is local (Airy) per cell, so a range's load
  doesn't press down the plain beside it (foreland and intermontane basins), there is no thermal sag after
  rifting or over cold mantle (Chad, Eyre, Congo, Michigan), and crustal flow (>40 km crust) fills thin
  spots between thick ranges. Try a flexural response (a range's load spread over ~100-300 km, making a
  moat beside it; the same flexure would give rift flanks their uplift, PW-135) and a slow sag over
  stretched or cold-mantle crust; re-measure the inland share and closed-lake count at L6 and L7.
- 2026-10-15: Moved from tectfound to the hydro agent (with PW-055).
- 2026-10-15: Status todo -> in-progress. Foundation round, worktree tectfound.
- 2026-10-14: Owner (2026-10-14): this is the right fix for too few closed basins (generated land draining inland is 4.2% after PW-110's slope rule, vs Earth ~18-20%). Scheduled with the tectonics-quality set.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Rivers, lakes, sediment and morning_report biggest problem 2.
