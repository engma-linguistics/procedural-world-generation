---
id: PW-176
title: Half the dune-field cells are cold polar deserts (a 1100-cell erg at 59N, -5 C)
type: task
status: done
parent: PW-005
subsystem: surface
effort: s
impact: med
found_by: zoomland3
blocked_by: []
relates: [PW-012, PW-096]
refs: [planet/landform.py, "world:a08983(59.34,-137.96)", "zoom:ee587f"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
On world a08983 (run 8571dd @ 408 Myr) dunes cover 5.6% of land, and more
than half of those cells are cold: the biggest erg (1142 cells, centred
58.7N -138E) has a mean of -4.6 C and 83 mm/yr; others at -58S (518 cells,
-6 C) and -52S. Why it is classed so: the rule is only `precip < 150 mm`
plus sand still piling up (top stratum sandstone grown within 20 Myr). At
59.3N the land lies in the rain shadow of an ice-capped range 4.3 km high
(1.7 km of ice at -169E) under steady westerlies, so it gets 20-40 mm/yr,
and the outwash from that range keeps laying sand on the plain east of it:
a periglacial sand sea is physically plausible (Kobuk dunes 67N, the
European sand belt in the last glacial, Antarctic dry valleys), but on
Earth active ergs are mostly warm subtropical deserts; cold ones are small
and frozen, snow-covered ground holds the sand much of the year. The zoom
(PW-012) already makes cold ergs half as active (lower dunes; zoom ee587f
shows a field of low barchans).

Options:
- A: keep the rule (cold ergs stay; the zoom damps them). Cheapest.
- B: add a cold limit to the class rule: warm-month temperature above
  ~10 C or mean above ~-2 C (frozen, snowy ground: sand sheets / tundra,
  hills instead).
- C: use aridity (P / PET < 0.05, hyper-arid) instead of raw precipitation:
  cold deserts with tiny PET drop out naturally, hot ones with 150-200 mm
  but huge PET get in.
Lean: C, maybe with B's warm-month floor; a run change (landform.py), so
goldens and the showcase move.

## Updates
- 2026-10-14: Status todo -> done. Dune rule: aridity index P/PET < 0.12 (landform.aridity; Oudin PET with the seasons, climate.pet_months; ~UNEP 0.06 since our PET is ~half Penman in hot deserts): a hot desert qualifies up to ~150-170 mm, a cold one below ~30-40 mm. Run 8571dd replayed to 408 Myr: dunes 5.5% -> 3.0% of land, cells with T < 0 C 1544 -> 258, hills 62.0 -> 64.7%, other classes unchanged. Zoom dune activity uses aridity too. Golden regenerated. World a08983 keeps the old classes until the next run (inbox draft). Needed a 2-line change in tectonics/output.py (pass t_warm/t_cold/tilt) (zoompolish).
- 2026-10-14: Status needs-decision -> todo. Coordinator decision (owner's north star: take the proper fix when it's cheap): use an aridity index (P/PET) for the dune rule instead of raw precipitation, so cold, low-evaporation deserts don't count as ergs unless genuinely arid with an active sand supply.
- 2026-10-14: Created from inbox draft draft-cold-ergs-dune-rule.md (found by zoomland3).
