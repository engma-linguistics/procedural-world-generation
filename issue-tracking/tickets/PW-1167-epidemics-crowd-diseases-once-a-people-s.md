---
id: PW-1167
title: "Epidemics: crowd diseases once a people's towns pass a few hundred thousand, virgin-soil losses at first contact, rare plague waves"
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: peoples
effort: l
impact: high
found_by: lane-82
blocked_by: []
relates: [PW-917, PW-1108, PW-661]
refs: [docs/review/peoples-counterpressures/design.md, planet/lineages/contacts.py, planet/lineages/history/cities.py]
created: 2026-10-30
updated: 2026-10-31
---

## Description
**In plain words.** Measles-like crowd diseases need several hundred thousand people living close together, so only farming peoples
with linked villages and towns carry them.
- **Virgin soil.** When such a people first meets one that has never had those diseases, the newcomers to the diseases lose a large
  share, up to 90% in the Americas after 1492, and the farmers take much of their land. That favours the dense peoples, as it did on Earth.
- **Plague waves.** Rare great plagues strike the carriers' towns and kill 20-80% there, then return for two or three centuries. Their
  neighbours move into the emptied land and keep some of it. This is the brake on humans.
- **Dials.** The viewer gets "how often plagues strike" (early and late eras) and "how hard first contact hits".

Design: docs/review/peoples-counterpressures/design.md, section (c). Depends on draft-counterpressure-plug.

- **Carriers.** A people becomes a carrier once its largest linked crowd reaches CCS_POP = 300k: cells at 5 /km² or more, linked by
  corridors. The threshold is "at least several hundred thousand" (Wolfe, Dunavan & Diamond 2007). Non-carriers season toward each
  carrier pool by contact, with e-folding 4 generations.
- **Virgin soil.** At first contact, a pulse `virgin_soil x (1 - seasoning)` (default 0.6; Koch et al. 2019's 90% is the top) falls on
  the contact component over one century.
- **Plague.** Poisson, 1.3 per kyr from the classical era (two pandemic eras in ~1.5 kyr, Jedwab, Johnson & Koyama), times the era
  dial.
  - Seeded at a carrier town, spreading over corridors within 4,000 km.
  - Loss 0.4 (their 274-locality mean) x a severity draw 0.1-1.5 (low end: Mordechai et al. 2019's "inconsequential" Justinianic
    plague), capped at 0.8.
  - A 250-year recurrence era adds 0.5%/yr.
  - Recovery takes ~150 yr for humans (cities recovered by 1500), slower for slow breeders.
- **No double count.** No endemic load is added: lane 78's agrarian schedule (Sweden 1751-59) already carries one.

- [ ] carrier state and seasoning per people
- [ ] virgin-soil pulse from the contact record; event text
- [ ] plague pulses in the recent epoch; events for settlements (PW-1108) and the brief
- [ ] meta.plague_early / plague_late / virgin_soil, per-line plague_x and crowd_disease, viewer controls
- [ ] lane 77 arms (off / default / x4; virgin_soil 0 / 0.6 / 0.9) with post-pulse cell flips reported

## Updates
- 2026-10-31: Owner 2026-10-31: virgin-soil epidemics stay OFF by default for now; the events system design (docs/review/peoples-events/design.md) covers epidemics as events.
- 2026-10-30: Created from inbox draft draft-epidemics-counterpressure.md (found by lane-82).
