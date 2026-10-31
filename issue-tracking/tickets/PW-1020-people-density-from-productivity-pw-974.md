---
id: PW-1020
title: "People density from productivity (PW-974): judgement calls in the form of f - linear, absolute, farmers exempt, deep epoch flat"
type: task
status: done
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: fun-lane-45b
blocked_by: []
relates: [PW-974, PW-833, PW-964]
refs: [planet/lineages/prey.py, planet/lineages/history/model.py, docs/review/megafauna/people_density.py]
created: 2026-10-29
updated: 2026-10-30
---

## Description
**In plain words.** People now live more densely on rich land and more thinly on poor land: herders follow how much grass grows, and foragers follow how much wild food there is. This is measured against fixed yardsticks, so a poorer planet holds fewer people overall. Farmers don't follow this yet; their numbers already depend on good soil. The question: keep it like this (A), make farmers follow land productivity too (B), or soften the effect so poor land isn't as empty (C)? Coordinator's lean: keep it (A). B is a small add-on if you want it.

Fun lanes 45/45b built PW-974 as density = way-of-life number x f per cell (`prey.people_fields`, read through `History.dens_at`).
The choices below are the lane's, not the owner's:
1. **Layers.** Herders read the grazing NPP (g C/m2/yr). Foragers read the `foraging` layer (0-5: mast and fruit, game, wetlands,
   river fish), not the grazing, which undercounts forest foragers (the ticket's note). Farmers read nothing: their fertile soil
   already sets their habitat K. Fishers and sea peoples read nothing. Mixed ways are weighted by their use shares.
2. **Absolute, not relative.** f = layer / a fixed reference (GRAZE_REF, FORAGE_REF), so a poor planet holds fewer people. The
   references are fitted once on the 6 x 4 dnd sweep (`people_density.py --fit` on an arm run with the factor off), so each way's
   mean density over that sweep stays at its number. The WIP version divided by each world's own mean, which is relative.
3. **Linear.** f is proportional to the layer, with no floor or cap. The foraging score saturates at 5, so foragers span ~0-2x
   their number; grazing NPP is unbounded, so the best grassland holds several times the herders' number. Binford-style
   forager data are said to span orders of magnitude (owner's PW-833 ruling; Binford 2001 not on file), so linear is, if
   anything, mild.
4. **Deep epoch flat.** Before the present plates, density is the number (the present's productivity field does not apply).

Options:
- **A.** Keep as built.
- **B.** Farmers read a productivity too (the fertile layer or total NPP), so that "way-of-life factor x productivity" covers
  every way.
- **C.** A concave f (e.g. square root) to soften poor-country densities if remnants rise.

Lean: A. B is a small follow-up if the owner wants farmers to track productivity too.

## Updates
- 2026-10-30: Status todo -> done. Merged lane 63 (a23f20e0): option B with a smidge of C (density follows productivity^0.75).
- 2026-10-30: Option B done in fun lane 63 with "a smidge of C": every way's density follows its layer to the power 0.75 (absolute: foragers the foraging layer over 2.83, herders grazing NPP over 263, farmers total NPP over 330; refs are power means over the r2 off-arm cells).
- 2026-10-30: Status needs-decision -> todo. Owner 10-30 D8: B (farmers follow land productivity too) first, with a smidge of C (a concave f so poor land isn't empty: humans live nearly anywhere); fold the evidence into paper P2.
- 2026-10-29: Created from inbox draft draft-people-density-productivity-form.md (found by fun-lane-45b).
