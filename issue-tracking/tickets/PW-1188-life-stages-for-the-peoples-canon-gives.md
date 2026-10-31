---
id: PW-1188
title: Life stages for the peoples canon gives no ages for (troglodytes, giants, stems)
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: highlights
effort: xs
impact: low
found_by: lane78
blocked_by: []
relates: [PW-1148, PW-1147]
refs: [planet/lineages/samples/dnd.toml, planet/lineages/life_history.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
Lane 78 put lane 76's canon ages into dnd.toml for 23 peoples. Their groups and their splits inherit them.

Still on a hand `generation_yr` with x = 1:
- the troglodytes (no canon row was read);
- the stems (reptilian, mammalian, hominid, goblinoid...);
- the true giants and the dragons. Megafauna keep their own schedules (dragon_ages; giants' `generation_yr` 65).

What's needed:
- Giants want a life table of their own if PW-1147's rates should reach them. A dragon life table already exists in dragon_ages.py.
- The troglodytes need a canon read (VGtM has no troglodyte lineage; Monster Manual only) or a judgement.

Other notes:
- Seven Meals has no ages yet.
- The aarakocra (brood class, adulthood 3 yr) come out at x 6.6 of the human growth rate.
  - On world 4360a3 seed 7 they did not balloon: 0.08% of people both before and after.
  - If they ever do, the lever is their breeding class, not a cap.
- [ ] troglodyte and giant ages (sourced or labelled judgement)
- [ ] Seven Meals ages

## Updates
- 2026-10-30: Created from inbox draft draft-life-history-for-peoples-without-canon-ages.md (found by lane78).
