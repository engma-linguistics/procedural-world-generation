---
id: PW-607
title: "Resources: keep the fantasy exotics (mithril-, adamant-like, star-iron) and add ley/arrival-site crystals?"
type: task
status: done
parent: PW-155
milestone: v2
subsystem: surface
effort: s
impact: low
found_by: resources
blocked_by: []
relates: [PW-155]
refs: [planet/resources.py, docs/proposals/resources.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Stage 1 adds three clearly marked fantasy resources (group 'fantasy', '[fantasy]' in every name,
listed apart in hover and summary, never on the dominant map), each tied to a plausible geological setting:
deep-silver (oldest craton roots a plume rose under), adamant (deepest collision roots, exhumed), star-iron
(deterministic impact sites kept on old surfaces). A fourth idea, aether crystals at ley lines / the lineages'
arrival sites, needs the lineages data on worlds (not there yet).

Options: **A.** keep as is, off by default nowhere (now); **B.** hide them behind a world option
(`--fantasy`) and a viewer toggle; **C.** drop them. Also: add the lineage-site crystals when lineages land on
worlds (yes/no).

Lean: **A**, and yes to the lineage crystals later (small: a likelihood around arrival sites).

## Updates
- 2026-10-23: Status todo -> done. Merged (fun lane 4, bfddaaf): see docs/proposals/lineages.md 'Fun lane 4'.
- 2026-10-23: fun4: option B built: planet resources WORLD --mode real drops the res_x_* layers, zoom deposits follow, peoples' land use drops mithril in real mode. Viewer toggle and arrival-site crystals: see drafts.
- 2026-10-23: Status needs-decision -> todo. Owner (2026-10-24): B: fantasy resources behind a toggle (a world option and a viewer toggle); the owner wants a 'real world only' mode (humans, real materials and animals) and a 'fantasy' mode (races, fantasy metals, maybe magic). Arrival-site crystals belong with the fantasy mode.
- 2026-10-23: Created from inbox draft draft-resources-fantasy.md (found by resources).
