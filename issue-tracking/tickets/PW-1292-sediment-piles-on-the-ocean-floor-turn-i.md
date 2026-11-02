---
id: PW-1292
title: Sediment piles on the ocean floor turn into continent at 20 km, and with the sea-floor creep that churn steers both crust thermostats
type: task
status: in-progress
parent: null
milestone: null
subsystem: tectonics
effort: m
impact: med
found_by: lane-100e
blocked_by: []
relates: [PW-950, PW-1276]
refs: [planet/tectonics/crust.py, planet/tectonics/isostasy.py, planet/tectonics/crust.py::birth_and_cratons, planet/tectonics/isostasy.py::sediment_iso, planet/surface.py::_creep, docs/review/tectonics/margin/deep-dive.md, docs/review/tectonics/margin/tracediag.py, docs/review/tectonics/margin/sinkdiag.py, docs/review/tectonics/margin/handoff.md, tests/test_sea_level.py]
created: 2026-11-01
updated: 2026-11-01
---

## Description
In plain words: when sediment piles up on the ocean floor to 20 km of crust, the model turns that spot into
continent. Real thick sediment on the ocean floor stays sediment on oceanic crust. It becomes part of a continent
only when a trench scrapes it on, or a collision welds it on. With the sea-floor creep (PW-950), over three times as
much of this "born" continent appears late in a run. Much of it sits isolated and is shredded again by the
coherence rule. That churn (+45 000 born and -40 000 shredded per 400 Myr, km x L5 cells) is the biggest flux in the
late crust budget, and both thermostats answer it.

Where: `crust.birth_and_cratons` (`born = ~cont & (t >= BECOMES_CONT_KM) & ((rock != HOTSPOT) | sedimented)`).
Numbers: docs/review/tectonics/margin/deep-dive.md (screens table).

Options:
- A. Sediment-born birth only where the pile touches continental crust on its own plate (a margin wedge that joins
  its continent). Isolated piles stay oceanic, however thick. Arcs are unchanged.
- B. No birth from sediment. Piles join continents only through `crust.accrete` and collisions.
- C. Leave it.
Lean: A (it keeps sediment-built coastal plains). Screen it on seeds 1 and 3 with and without the creep, then run a
paired judge. Lane 100e tried keeping drowned piles out of the area count only (pile_area). It didn't help.
- [ ] decision A / B / C

## Updates
- 2026-11-01: refs enriched (lane 113): code functions, margin notes and harnesses, papers by key.
- 2026-11-01: Status needs-decision -> in-progress. Daniel 11-01: option A, next physics lane (lane 112).
- 2026-11-01: Created from inbox draft draft-sediment-piles-born-continental.md (found by lane-100e).
