---
id: PW-769
title: "Incursions that settle among the old people (co-residence) are not derived yet: only displacement is"
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun14
blocked_by: []
relates: [PW-756, PW-730, PW-731, PW-734]
refs: [planet/lineages/contacts.py, planet/lineages/reputation.py, "world 1df1c3", planet/lineages/samples/seven_meals.toml]
created: 2026-10-24
updated: 2026-10-24
---

## Description
PW-756 derived incursions (`contacts.Contacts.incursions`, `meta.contacts.incursions`) find episodes where a people becomes the lead people in cells another
held (the old one drops under the held threshold), the taker gaining >= 10% of its range in a 2 kyr window (>= 0.05 Mkm2). On world 1df1c3 with the
seven_meals preset that finds ~50 incursions per run (goblins, hobgoblins, bugbears, elves, tabaxi, leonin, halflings), none by the antelope-kin or cervid-kin:
with the pastoral-herder press (spec.WAY_PRESS) the antelope-kin grow from 3.85 to 11.7 Mkm2, but by living thinly among the humans (the humans stay the lead people
in those cells), not by displacing them. The substrate shows only 82 cells taken from the humans (38 kyr ago). So the world still has no "devil conquest" in the sim's
own terms and the two authored `[[event]]` rows carry it.

Decision for the owner / coordinator: should a fast, large rise of a people's presence inside another's held cells (a settlement wave, an elite overlay) count as an
incursion too, with the loss measured as the share of the old people's local cells the newcomer now shares? It would give the fiends a derived basis on this world,
but it blurs "conquest" with "migration into shared land", and the humans' memory of it would be a weaker valence than `feared` (closer to the polity case, PW-661). My lean:
add it as a separate `settled` incursion kind that feeds `feared` only when the old people also lost lead share, and leave pure co-residence to the polity pass.
After the owner's guidance the preset ships no authored conquests and gives the fiends the `aggressive` trait (rivals' load x0.7) beside the herder press: on 1df1c3 (tries 1, same
seed) the antelope-kin go 3.85 -> 14.0 Mkm2 and the cervid-kin 18.5 -> 39.2 Mkm2 (humans 112 -> 90), yet the sim still finds no incursion by either (the 39 derived ones are goblinoids, giants,
elves; the cervid-kin are on the losing side of hobgoblin ones), so on this world nobody calls them devils or demons now. This makes the co-residence decision below the one that matters for the owner's names.
- [ ] Decide whether co-residence counts; if so, record presence rises per frame (Contacts._note) next to lead flips.
- [ ] Judgement: INCURSION_GAIN 0.10, INCURSION_SPAN 2 kyr, INCURSION_MIN_MKM2 0.05, LOCAL_KM 1000 are first guesses; no sweep done (one world, tries 1).

## Updates
- 2026-10-24: fun15: done on the branch. contacts.py notes `settled_among` rises (presence +0.15 in one frame in cells another people still leads) into the same episode/threshold machinery; incursions carry `kind` (displacement | settled_among); reputation names the kind. Follow-up in draft-settled-incursions-reputation-gate.
- 2026-10-24: Owner 2026-10-24: yes, a ruling-minority fast rise counts; keep it light.
- 2026-10-24: Created from inbox draft draft-incursions-by-co-residence.md (found by fun14).
