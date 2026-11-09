---
id: PW-888
title: Peoples' origins should spread across landmasses roughly by habitable area (species-area), not crowd onto one small continent
type: task
status: done
parent: PW-692
milestone: v5
subsystem: peoples
effort: m
impact: high
found_by: owner
blocked_by: []
relates: [PW-887, PW-885, PW-869]
refs: [planet/lineages/history.py]
created: 2026-10-25
updated: 2026-11-08
---

## Description
Owner, 2026-10-25: "I do think it thus very important to not have most species evolve on a smaller single landmass." On 2a7385 (dnd tree), 13-15 peoples share the small continent (landmass 1, 11.5k land cells). That leaves no room for anyone, and humans stay at about 2k cells until the Holocene (PW-885).

Coordinator: the species-area relationship says larger, more varied landmasses host more lineages. Isolation also drives speciation, so small landmasses and islands still get some, just fewer per peoples' habitat. Measure where origins land now, per landmass, against the habitable area there. Then make the origin draw honour this (a per-landmass expected count, roughly proportional to habitable area to the power ~0.25-0.35, z from the species-area literature, e.g. Rosenzweig 1995), in place of the per-cell habitat noise. Origin noise is heavy-tailed (fun lane 24 found that the best cell wins by hundreds of times a typical one).
- [ ] origins per landmass tracked against habitable area over 8 seeds on 2a7385 and one other world; no landmass under ~15% of the land holds most peoples

## Updates
- 2026-11-08: Status todo -> done. Lane 228 (d01c4a08) measured 34 tries on 4360a3 and af2677: no landmass under 15% held most origins; bar met. The 15.5% continent on 4360a3 sits on the line through descent, parked as PW-1559 (later, coordinator A under the 10-27 ruling). Write-up docs/review/peoples/origins-spread.md.
- 2026-11-03: Milestones 11-03: v2 -> v5: v5 must-have: Seven Meals origins spread across continents
- 2026-10-27: Status needs-decision -> todo. Owner 2026-10-27: each root ancestor line (reptilian, mammalian, avian, ...) starts on a different landmass (always intended). Related peoples clustering near their ancestor is fine until the civ stage (boats, ~last 20 kyr).
- 2026-10-27: Status todo -> needs-decision. Merged partial (fun lanes 30-33): area^0.3 origins, sea-crossing founders, persistence-horizon MVP (c=1), trees retimed. Open: overland jump dispersal (lean yes) and roots on separate landmasses (lean yes); asked owner 2026-10-27.
- 2026-10-26: (fun-lane-30) Ruling applied: origins need a long-term viable landmass (history.ORIGIN_MVP_MULT 8 x viable_pop, Traill 2007 / Frankham 2014). It holds the no-majority line but not elves/half-elves/humans-at-100-kyr targets; founders sit on 1-2 cell places because a cell holds the MVP in people. See draft-small-landmass-founders-start-thin.
- 2026-10-25: (fun-lane-30) Built (branch commit c0af1b1): `history._by_landmass` draws an origin's landmass by (habitable cells)^0.3 (Rosenzweig 1995), viable founders only, habitat picks the cell; splits may found across the sea on a landmass the parent does not touch. 2a7385 over 8 tries: the share of peoples on the 19% continent 26% -> 17% (tries 7000/7005/7006 held 57-61% there before); 1df1c3: the 15% landmass held 54-57% on 5 tries, now no landmass holds most. Costs: humans at 100 kyr ago and elves on 1df1c3 (see draft-small-landmass-founders-start-thin).
- 2026-10-25: Created from inbox draft draft-origins-spread-by-landmass-area.md (found by owner).
