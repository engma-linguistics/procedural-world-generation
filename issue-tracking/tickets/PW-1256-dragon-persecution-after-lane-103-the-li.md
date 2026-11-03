---
id: PW-1256
title: "Dragon persecution after lane 103: the lions' threshold carried to dragons, Woodroffe 2000 unread, option C not built"
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: s
impact: low
found_by: lane103
blocked_by: []
relates: [PW-1246, PW-1068, PW-1221]
refs: [planet/lineages/history/megafauna.py, docs/review/dragon-numbers/round2.md]
created: 2026-11-01
updated: 2026-11-03
---

## Description
**In plain words.** Dragons are now lost from land as busy as the farmland where lions die out (25 people per km²), and thinned below
it. That replaces the old "10 farmers per km² keep 10% of their dragons" rule. A few loose ends remain. None of them changes the
numbers much, because little of the model's land is that busy (0.5% of dragon country is above 20 people per km²).

Open points (lane 103, round2.md section 2):
- [ ] Read Woodroffe 2000 (Animal Conservation 3:165) itself. The 26 per km² is quoted by Riggio et al. 2013 (p. 30), and only the
  abstract was seen in a search summary. It may give thresholds for other big carnivores (tiger, wolf), which would show how much the
  threshold varies by species.
- [ ] The carry from lions to dragons is a judgement. KILL_Q is set so the *dragon's* life table is lost at 25 farmers per km². At a
  lion's per-head kill rate, the slow-breeding dragon would be lost at ~0.7 farmers per km², which would leave almost no dragons
  beside any people. The vulnerability by stage and tech (VULNERABILITY) carries the difference and is still a judgement.
- [ ] KILL_Q is calibrated on the default age schedule (`dragon_ages.DEFAULT`). A world on another schedule keeps the same KILL_Q, so its
  threshold moves with its own life table (base: ~19 farmers per km² at tech 1). Intended, but worth a line in the viewer if anyone
  switches schedules.
- [ ] Option C of PW-1246 (dragons avoid busy country) is not built. B carries the pattern. C would only matter if the viewer's maps
  show dragons smeared evenly over farmland.
- [ ] The giants use the same KILL_Q, so they are now pressed about 10x less per person than before (the old KILL_Q was 10x higher).
  Check the giants' counts on the next census (lane 99's census counts dragons only).

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Dragon-density tail; PW-961 stays.
- 2026-11-01: Created from inbox draft draft-dragon-persecution-follow-ups.md (found by lane103).
