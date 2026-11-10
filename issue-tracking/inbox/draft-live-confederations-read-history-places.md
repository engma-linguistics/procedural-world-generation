---
title: With polities in the history, confederations still read the history's own places, not the ledger's
type: task
status: todo
parent: PW-661
milestone: later
subsystem: peoples
effort: s
impact: low
found_by: lane281
blocked_by: [PW-1596]
relates: [PW-1583, PW-1597]
refs: [docs/review/culture/polities/round24.md, docs/review/culture/polities/round24/live_seats.patch, "planet/lineages/history/polity_live.py::LivePolities._confederations", "planet/lineages/history/polity_live.py::LivePolities._seat_places", "planet/lineages/polities.py::_confederations"]
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
