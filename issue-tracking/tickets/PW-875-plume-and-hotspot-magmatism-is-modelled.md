---
id: PW-875
title: Plume and hotspot magmatism is modelled but never outgasses CO2; the resized drift no longer stands in for it
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: coupling-audit
blocked_by: []
relates: [PW-819]
refs: [planet/tectonics/earth.py, planet/tectonics/volcanism.py, planet/tectonics/params.py, docs/review/coupling-audit/]
created: 2026-10-25
updated: 2026-10-26
---

## Description
Coupling audit finding C2 (severity medium for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**Physics lane:** take second.

**One side:** planet/tectonics/earth.py (v1-finish-12) global_temperature L310: source = new ocean floor + 20 x arc growth, times the drift.

**Other side:** planet/tectonics/simulation.py (v1-finish-12) _physics L253-263: volcanism.hotspots / cap_plumes make plume heads, aprons and vents (lava added to the crust), scaled by mantle heat; no CO2 term anywhere in volcanism.py or events.py. params.py (v1-finish-12) climate_drift comment L109-121 now sizes the drift for organic burial and ocean chemistry only.

**Why they disagree:** The ridge and arc fluxes became explicit and the drift was shrunk to the terms "the model lacks", but plume degassing is a term the model has the magma for and still lacks the carbon for. Hotspot/plume degassing is of the same order as ridge degassing (Marty & Tolstikhin 1998: ridges ~2e12, arcs ~2.5e12, plumes ~3e12 mol C/yr, wide error), and plume heads (LIPs) are the Phanerozoic's main warm-pulse drivers.

**Measured:** Code read only: grep finds no co2/outgas/degass in volcanism.py, events.py, mantle.py. Magnitude from the literature, not measured (plume lava volume is not stored in runs).

**What to try:** Options: (A) add plume lava x a CO2 yield to the source (learnt into the reference like the rest, so it adds variance and LIP pulses rather than shifting the mean); (B) keep it out and put plume degassing back into the drift's sizing; (C) leave and document. Lean A: the magma is already there, and LIP pulses are a feature for history.

## Updates
- 2026-10-26: Merged PW-898: plume degassing is ~2% of the carbon source (max ~5%) because the modelled plume melt is small next to the ridges; the literature puts plume CO2 near the ridges' order. (PW-900 backlog reorg).
- 2026-10-25: v1-finish-13 (1b52cdf): plume melt (head + apron + vents, before the height caps) degasses at PLUME_CO2 3.3x the ridges' yield per km3 (MORB ~0.15 wt%, Marty & Tolstikhin 1998, Crisp 1984; plume/flood basalt ~0.5 wt%, Self et al. 2006, Black & Gibson 2019). Smoke seed 11 L6: plumes 1.8% of the source (max 4.6%), below the literature's share: draft-plume-melt-small-share-of-source.md.
- 2026-10-25: Status needs-decision -> todo. RULING (coordinator): add plume/LIP degassing as a CO2 source tied to the modelled plume heads and vents, sized from the literature (e.g. Self et al. 2006, Black & Gibson 2019), as a mechanism, not tuned. Physics lane, with PW-880/881/873.
- 2026-10-25: Created from inbox draft draft-plume-volcanism-never-outgasses.md (found by coupling-audit).
