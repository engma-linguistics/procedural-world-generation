---
id: PW-958
title: Dragon age structure (wyrmling, young, adult, ancient) with counts reported by stage
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: [PW-924, PW-923]
refs: [docs/proposals/megafauna-scaling.md, planet/lineages/history/megafauna.py, docs/review/megafauna/scaling.py]
created: 2026-10-28
updated: 2026-10-28
---

## Description
Owner 2026-10-28: report dragons by stage. This is for dragons only; giants don't need it.

The base case the owner approved:

| stage | ages | annual mortality | share of individuals |
|---|---|---|---|
| wyrmling | 0-5 | 20% | 9% |
| young | 6-100 | 1.5% | 33% |
| adult | 101-800 | 0.25% | 51% |
| ancient | 801+ | 0.4% | 7% |

The oldest age is 3,000 years. Ancients hold 34% of the biomass and 31% of the food. The ecological mass is 3.2 t.

- Each counted pocket splits its count into stages. Draw it, as summary() already draws counts, so a pocket of 2 is usually two adults or a young dragon and an adult. Ancients turn up roughly once per ~14 dragons.
- Report the stages in line_text, the brief and the viewer: "~12 red dragons: 1 ancient, 6 adults, 4 young, 1 wyrmling".
- Keep the mortality schedule as data on the line, inherited by the kinds. The ancient share is very sensitive to adult mortality (0.3% to 26% between doubled and halved rates), so it may want a user option later.
- The ecological mass from this structure feeds the natural density (PW-957) and food use (PW-960).
- Consider making mated pairs and "a pair with young" in groups_note follow the stages: young dragons with an adult.

## Updates
- 2026-10-28: Owner 10-28: intuition 'California has ~2 ancients, ~10 adults, 30+ young' fits a younger pyramid than the base case. Proposed (owner to confirm on the draft-megafauna-9 maps): annual mortality wyrmling 20%, young 3%, adult 0.5%, ancient ~0.1% (the survivors are near-untouchable). Gives wyrmling 24%, young 53%, adult 20%, ancient 3.5%; generation time ~480 yr. At 1/5,000 km2 a California-sized dragon country holds ~85 dragons: ~20 wyrmlings, ~45 young, ~17 adults, ~3 ancients.
- 2026-10-28: Created from inbox draft draft-megafauna-2-dragon-age-structure.md (found by daniel).
