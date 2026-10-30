---
id: PW-1117
title: "Settlements: second peoples' own places churn (thousands of short-lived ones) and their holds pile up at the 9,999 town cap"
type: task
status: todo
parent: PW-856
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: fun-lane-61
blocked_by: []
relates: [PW-1105, PW-1011]
refs: [planet/lineages/settlements.py, "run 488d7e", "run 6128a3", "run 114231", "run 570701", "world 4360a3"]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. Fun lane 61 (PW-1105) lets a cell's second people found a place of its own (a dwarf hold, a kobold warren, a halfling village among humans). Two side effects are worth a look.

1. Churn. Over the last 12.5 kyr, the four runs on world 4360a3 founded 20,662 to 24,223 places, against 7,782 to 9,071 before. About 5,000 of the living places are second peoples' own. But many are short-lived:
   - 2,000 to 2,800 end because "its people left";
   - 2,100 to 3,600 merge into the main place (no ruin) when their people come to lead the cell.

   The cause is that a cell's second people changes often in mixed country. Each change can found a new place, and each fall-off ends one. Ruins rose from ~700 to 3,100 to 4,600 a run. The village and town ruins only show when zoomed in (PW-1106), but the ledger is noisy.
   Try: a longer founding streak for second-people places (FOUND_STEPS x 3), or founding only where the second people has been second for ~1 kyr.
2. The cap. A mining people's own place is its halls: HOLD_SHARE (0.5) of its heads in the cell. Where dwarves or kobolds are 20%+ of a dense cell, that is far more than 10,000. The place then sits at the town cap of 9,999, because a minority place is never a city. On run 488d7e the five largest dwarf holds are all 9,989 to 9,998. Kobolds hold 641 to 715 such warren-towns a run.
   Try: size the halls with a share of the hold (like the chief place's SHARE), or let a hold grow into a city of its own.

Numbers: `cmp_holds`-style table in fun lane 61's report (PW-1105 Updates).
- [ ] fewer short-lived second-people places; holds not pinned at the cap

## Updates
- 2026-10-30: Created from inbox draft draft-settlements-minority-churn-and-cap.md (found by fun-lane-61).
- 2026-10-30: Fun lane 66: second-people places must stand 0.5 kyr before founding and 1 kyr low before ending; short-lived ones fell from ~800-1,050 to ~30-40 a run, no hold at the 9,999 cap (holds may be cities). See overview 2.25 and draft-hold-size-by-hierarchy.
