---
id: PW-605
title: "Resources: BIF and diamond rules use Earth's absolute geological clocks (1.8 / 2.5 Gyr)"
type: task
status: needs-decision
parent: PW-155
milestone: v2
subsystem: surface
effort: xs
impact: low
found_by: resources
blocked_by: []
relates: [PW-155, PW-443]
refs: [planet/resources.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Banded iron needs crust >= 1.8-2.7 Gyr old (Earth's iron-ocean era before oxygenation) and
diamonds a craton root >= 2-2.8 Gyr, greenstone gold >= 2.4 Gyr. These are absolute ages; the run gives
initial cratons Earth-like ages (up to ~3.7 Gyr), so every planet so far has an Archean. A planet with a
different oxygenation history would differ.

Options: **A.** keep absolute ages (Earth's Great Oxidation as a universal clock); **B.** scale to the planet's
own oldest crust (the oldest 30% of crust ages); **C.** make the oxygenation time a planet parameter
(weird-worlds work, PW-443).

Lean: **A** for v2, **C** with PW-443.

## Updates
- 2026-10-23: Created from inbox draft draft-resources-clocks.md (found by resources).
