---
title: Dragons at their natural density where no people presses them, suppressed to ~1 per 5,000 km2 by peoples (the age of dragons)
type: story
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: l
impact: high
found_by: daniel
blocked_by: []
relates: [PW-923, PW-924, PW-936]
refs: [docs/proposals/megafauna-scaling.md, planet/lineages/history/megafauna.py, planet/lineages/samples/dnd.toml, docs/references/megafauna/]
---

## Description
Owner 2026-10-28 (approved docs/proposals/megafauna-scaling.md). The present dragon density, 1 per 5,000 km2 (PW-923), is 35-75x below what Damuth's law gives a dragon. With Marshall et al.'s mesotherm intercept (log10 a = 2.99, M in g), the 3.2 t ecological mass of the base age structure gives ~1 per 65 km2 across all ages. On the mammal-carnivore intercept it is ~1 per 137 km2. Either way, 1/5,000 is outside the 95% Damuth band.

The realistic reason for the gap is pressure from peoples. Real large carnivores in human-dominated land run at a few percent of their potential: tigers are at ~3-4% of their historical numbers (Ripple et al. 2014).

Model it:
- **Natural density.** A dragon kind's natural density comes from Damuth's law at its ecological mass (draft-megafauna-2), on Marshall's mesotherm intercept. That intercept is also where reptile field metabolic rate lands at dragon size: the reptile/mammal energy use ratio is ~0.55 at 20 t.
- **Pressed density.** Where peoples hold the land, density falls with their pressure (people density, or farmers more than foragers; to be chosen). The present-day world average over the dragons' country should land near the owner's user option (default 1/5,000 km2).
- **Unpeopled country.** Country no people holds keeps closer to natural density.
- **The age of dragons.** Before peoples spread, dragons are far more numerous. The history and brief should say so.
- **Derivation note.** Fix the comments in dnd.toml and megafauna.py. "An apex hunter two to three orders below the herbivore line (Carbone & Gittleman)" is unsupported: the carnivore line is ~1.5 orders below, and reptile physiology raises it again. Cite Marshall 2021 and Nagy et al. 1999.

The user option should probably become "present-day density in peopled country", with the natural density derived from mass. Ask the owner if that reading doesn't fit the workbench control.

- [ ] natural density from mass and physiology per kind
- [ ] suppression by peoples' pressure, calibrated so the present default is ~1/5,000 km2 in peopled dragon country
- [ ] counts before the peoples spread shown in the history and brief ("the age of dragons")
- [ ] comments and citations corrected
