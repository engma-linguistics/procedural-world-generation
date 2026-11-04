---
id: PW-155
title: "Resources layer: ores, coal, gems, building stone (Dwarf Fortress-style), coarse from history, filled in by fine passes"
type: epic
status: todo
parent: null
milestone: later
subsystem: surface
effort: xl
impact: med
found_by: daniel
blocked_by: []
relates: [PW-145, PW-005]
refs: []
created: 2026-10-14
updated: 2026-11-03
---

## Description
Owner (2026-10-14): a resources layer for game worlds, 'looking at you, Dwarf Fortress'. Not scheduled yet. Approach: the run's geological record (strata, rocks, history) gives each cell a coarse likelihood of each resource from the processes that make it: coal (coal measures in strata, PW-145), evaporite salt and potash, limestone/marble/granite building stone, porphyry copper and gold (arcs, exhumed plutons), banded iron and diamonds (old cratons, kimberlite pipes), placer gold and tin (rivers draining ore-bearing uplands), bauxite (deep tropical weathering), oil and gas (buried organic-rich basins), hydrothermal deposits (rifts, hotspots). Zooms and later fine passes place actual deposits (seams, veins, pipes, placers) consistent with the coarse layer.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: resources/ore layer or salt-mining detail; not needed for the first culinary brief
- 2026-10-29: 2026-10-29 landscape review: World Orogen models ~30 ore systems per cell (source x trap x timing x exposure) from a rock column (docs/review/landscape/world-orogen.md; GPL-3.0, ideas only). Owner wants more ore types in v2. Tech gating by deposit already exists (techtree.py: a tech needing a deposit arises only where the people's range holds it); what's new there is depth/exposure reachable per age.
- 2026-10-20: 2026-10-20: cost note. More rock or resource types are labels (one small int per cell), so they are essentially free when derived at finish or zoom time. Only time-stepped processes cost run time. Detailed rock: PW-474.
- 2026-10-14: Created.
