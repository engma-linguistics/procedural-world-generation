---
id: PW-859
title: "Track non-CO2 greenhouse gases (CH4, N2O) as their own forcing: climate reads CO2 + others, plants read CO2 only"
type: task
status: in-progress
parent: PW-244
milestone: v1
subsystem: climate
effort: m
impact: critical
found_by: owner-feedback-2026-10-25
blocked_by: []
relates: [PW-828]
refs: []
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner 2026-10-25: 'let's definitely track CO2 separately from stuff what can help make our ice ages and trees and such not all wonky. Feels a very important thread to follow.' Today the model is CO2-only (climate.pco2, earth.co2_term), so every bit of greenhouse warming the climate needs has to come from CO2, and plants feel all of it. On Earth: CH4 and N2O add ~a third again to CO2's glacial-interglacial forcing (LGM ~-2.8 W/m2 total GHG vs ~-2.0 CO2); in deep time methane was far higher under low oxygen (a classic part of the faint-young-Sun answer before ~2.4 Ga and plausibly in the Proterozoic). Plan: (1) a separate non-CO2 forcing term with crude, physically motivated sources and sinks (wetland/biosphere CH4 scaling with temperature and wet area, oxidation lifetime; a deep-time background tied to the plant/oxygen calendar); (2) the time zoom's glacial drop uses CO2 and CH4/N2O separately (PW-828); (3) vegetation reads pCO2 only. Measure whether it moves the CO2 needed for the strict bar and the wet-tropics forests.

## Updates
- 2026-10-25: Status todo -> in-progress. Owner 2026-10-25: top of the physics queue. Folded into v1-finish-14 with the 2 Gyr icebox (faint young Sun); methane is part of that answer.
- 2026-10-25: Created.
