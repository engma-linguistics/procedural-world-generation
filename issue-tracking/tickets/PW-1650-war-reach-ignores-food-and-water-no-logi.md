---
id: PW-1650
title: "War reach ignores food and water: no logistics scalar, no supply-distance falloff, no siege length"
type: story
status: todo
parent: PW-661
milestone: v4
subsystem: culture
effort: l
impact: high
found_by: lane279
blocked_by: []
relates: [PW-1449, PW-1478, PW-1479, PW-1108, PW-1457]
refs: [docs/review/culture/polities/logistics-proposal.md, planet/lineages/polities.py, planet/lineages/invasions.py, planet/lineages/history/polity_live.py, docs/review/culture/polities/invasions_reach.md]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words
Early kingdoms should raid a short way, campaign further as they learn to keep and carry food, and over-reach into being nipped at
on the edges, while a power that stays compact stays strong. Today an expedition's range is a fixed budget (D56's ~1,000 km) and a
war is one coin flip a century, so none of that can show up. If never done, a state's reach reads the same at every tech level and
the "settling down" pattern cannot appear.

## Description
Build the plan in `logistics-proposal.md` section 6: a logistics scalar LOG from techs (steps 2-3), supply-distance strength falloff
and a siege model (4-5), partial conquest (6) and live wiring (7, depends on the live-polities lane 278, no ticket id yet). Decisions
for Daniel are in section 5 of the proposal: magic strength against mundane (lean: a ceiling of ~1.5x), caster limits (lean: for the
strong spells only), what LOG = 1 means (lean: D56 at iron-age tech), and partial conquest versus all-or-nothing war (lean: partial).
- [ ] decisions 1-4 answered
- [ ] measures in proposal section 4 pass on five re-rolled draws, same commit on/off

## Updates
- 2026-11-10: Owner 11-10 D73 C (magical supply capped ~1.5x; magic supply draws on magical/alchemical resources and trade goods; potency and prevalence grow with the tech tree like other war techs), D75 A (iron age = today's ~1,000 km reach), D76 A (small polities conquered whole; larger empires lose edges piecemeal and see rebellious breakaways).
- 2026-11-10: Created from inbox draft draft-logistics-reach-and-siege.md (found by lane279).
