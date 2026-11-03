---
id: PW-1247
title: "Dragons' sea food (D28 B): read Ryther 1969 itself, an areal sea-ice production, the peoples' fishing take, and a polar-bear check"
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: s
impact: low
found_by: lane99
blocked_by: []
relates: [PW-1221]
refs: [planet/lineages/prey.py, planet/lineages/history/megafauna.py, docs/review/dragon-numbers/report.md]
created: 2026-10-31
updated: 2026-11-03
---

## Description
**In plain words.** The coast and ice dragons now also eat seals and other sea mammals, worked out from how much the sea grows. Some
of the numbers behind it were read only second-hand, and two things are left out: what the peoples themselves fish and seal, and
whether the frozen seas grow as much as the model says. None of this changes the picture by more than a factor of two or so.

Lane 99 added `prey.sea_npp` / `prey.sea_prey` and `megafauna.sea_food` (trait `sea_hunter`: white, bronze, blue). Open points:
- [ ] Ryther 1969 (Science 166:72) Table 1 read in the original: the 50 / 100 / 300 g C/m2/yr come via Pauly 1996 and a UCT thesis;
  later estimates (Martin et al. 1987, via a NOAA review) are 1.4-2.6x higher, which would raise the sea food by as much.
- [ ] An areal figure for ice-covered seas: the model keeps Ryther's coastal 100 under seasonal ice and cuts only perennial ice
  (coastform's 0.8 x ramp(ice share, 0.6, 0.98)); polar shelves may grow less.
- [ ] The peoples' fishing and sealing are not taken from the sea food (fisher-foragers, sea nomads, tritons, sea elves).
- [ ] A cross-check on a real seal-eating apex predator: polar bear densities (Hamilton & Derocher; a search snippet gave a mean of
  2.36 per 1,000 km2, unverified) against the model's sea-hunter density per km2 of coastal sea, with the bear's yearly intake.
- [ ] The prey's trophic level (seals 4.0; Pauly et al. 1998) against the marine mammals' share of primary production (Trites et al.
  1997, all mammals, whales included, whose diets are lower): one mixed figure; a seal-only share would be smaller.

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Dragon-density tail; PW-961 stays.
- 2026-10-31: Created from inbox draft draft-sea-food-follow-ups.md (found by lane99).
