---
id: PW-888
title: Peoples' origins should spread across landmasses roughly by habitable area (species-area), not crowd onto one small continent
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: owner
blocked_by: []
relates: [PW-887, PW-885, PW-869]
refs: [planet/lineages/history.py]
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner, 2026-10-25: "I do think it thus very important to not have most species evolve on a smaller single landmass." On 2a7385 (dnd tree), 13-15 peoples share the small continent (landmass 1, 11.5k land cells). That leaves no room for anyone, and humans stay at about 2k cells until the Holocene (PW-885).

Coordinator: the species-area relationship says larger, more varied landmasses host more lineages. Isolation also drives speciation, so small landmasses and islands still get some, just fewer per peoples' habitat. Measure where origins land now, per landmass, against the habitable area there. Then make the origin draw honour this (a per-landmass expected count, roughly proportional to habitable area to the power ~0.25-0.35, z from the species-area literature, e.g. Rosenzweig 1995), in place of the per-cell habitat noise. Origin noise is heavy-tailed (fun lane 24 found that the best cell wins by hundreds of times a typical one).
- [ ] origins per landmass tracked against habitable area over 8 seeds on 2a7385 and one other world; no landmass under ~15% of the land holds most peoples

## Updates
- 2026-10-25: Created from inbox draft draft-origins-spread-by-landmass-area.md (found by owner).
