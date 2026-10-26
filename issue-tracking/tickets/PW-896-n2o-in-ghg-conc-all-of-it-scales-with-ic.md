---
id: PW-896
title: "N2O in ghg_conc: all of it scales with ice-free land (the ocean's ~1/3 shouldn't), and there is no deep-time N2O"
type: task
status: todo
parent: null
milestone: v1
subsystem: climate
effort: xs
impact: low
found_by: v1-finish-14
blocked_by: []
relates: [PW-859]
refs: [planet/tectonics/earth.py]
created: 2026-10-26
updated: 2026-10-26
---

## Description
`earth.ghg_conc` scales all of N2O's source by the ice-free land. That gives LGM N2O ~175 ppb, against ~200 ppb in the
ice cores (Schilt et al. 2010). The ocean's ~1/3 of the source (Ciais et al. 2013, AR5) should scale with temperature
only. Proterozoic N2O, which may have been higher in a copper-poor ocean (Roberson et al. 2011, Buick 2007), is not
counted. Small: ~0.1 W/m2 at the LGM.

## Updates
- 2026-10-26: Milestone null -> v1. (PW-900 backlog reorg).
- 2026-10-26: Created from inbox draft draft-n2o-ocean-share-and-deep-time.md (found by v1-finish-14).
