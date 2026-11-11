---
id: PW-1671
title: With polities in the history, confederations still read the history's own places, not the ledger's
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: peoples
effort: s
impact: med
found_by: lane281, lane281b
blocked_by: []
relates: [PW-1583, PW-1597]
refs: [docs/review/culture/polities/round25.md, docs/review/culture/polities/round25/missing.py, docs/review/culture/polities/round24.md, docs/review/culture/polities/round24/live_seats.patch, "planet/lineages/history/polity_live.py::LivePolities._confederations", "planet/lineages/history/polity_live.py::LivePolities._seat_places", "planet/lineages/polities.py::_confederations"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
**In plain words.** Lane 281 (round24.md) found that with polities in the history on, the first state came 1,700 years later than
the read-out on the very same history (L7 world 899985 seed 7), because the history sized its seats without a mining people's
halls and asked for the `cities` tech by name. Its patch makes the seats read the ledger's own places (town_cells). The
confederations (step 1b: a people with a state's institutions but no city, banding together beside a foreign state) still count
heads in the history's own places (`place` in `_step`), which miss the same halls. Once the patch is in, make 1b read the same
places as the seats, and check the confederation counts on/off on one pair.

**What misleads if never done.** A mining people (gnomes, dwarves) could form a confederation off but not on, or the other way,
so the on/off state maps differ for an accounting reason.

**Measured (lane 281b, round25.md section 3).** The seats patch is in (8ba3d691). On one switch-on history (L7 899985 seed 7,
scratch run 560796, gone), standing confederations live / read-out on the same history: 4 / 9 at 2,000 years ago, 11 / 23 at
1,000, 17 / 21 now: a real part of the live state counts running under the read-out's. **A prerequisite of the PW-1596 flip**:
with the switch on by default, every run would lose these. Fix: step 1b reads town_cells' places (both slots, summed per holder
line, as the read-out sums a people's sites); `_places`, `_second_places` and `_site` then go from `_step`, with the PW-1587 test
moved onto town_cells' site factor.

## Updates
- 2026-11-10: Created from inbox draft draft-live-confederations-read-history-places.md (found by lane281).
