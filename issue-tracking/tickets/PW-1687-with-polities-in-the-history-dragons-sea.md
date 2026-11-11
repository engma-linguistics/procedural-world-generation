---
id: PW-1687
title: With polities in the history, dragons seat 4-6 realms against the read-out's 16-26; how should the history cut a dragon people into realms?
type: task
status: done
parent: PW-661
milestone: v4
subsystem: peoples
effort: s
impact: high
found_by: lane281c
blocked_by: []
relates: [PW-1596, PW-1671]
refs: [docs/review/culture/polities/round26.md, docs/review/culture/polities/round26/measure.py, docs/review/culture/polities/round26/dragon_ranges.py, docs/review/culture/polities/round25.md, "planet/lineages/history/polity_live.py::LivePolities._step", "planet/lineages/polities.py::_dragon_cultures", "planet/lineages/polities.py::_core", "world 4360a3", "world 899985"]
created: 2026-11-10
updated: 2026-11-11
---

## Description
**In plain words.** With states worked out inside the history (the switch `POLITIES_LIVE`), dragon peoples now rule realms there
too, but far fewer than the after-run read-out shows: 4-6 at any date against 16-26, on all five test pairs (round26.md section 3;
L6 world 4360a3 seeds 7, 3, 10 and L7 world 899985 seeds 7, 10). The read-out seats one realm per dragon *culture*, and the
cultures engine, which runs after the history, splits each dragon kind into a few regional cultures (45 alive at the end of L6 seed
7). The history has no cultures. It used to seat a realm on every connected piece of a dragon people's range, which gave about 300
realms because a dragon range is hundreds of scattered pieces (round26.md section 2). Lane 281c changed that to one realm per dragon
people, which is too few. This blocks the switch going on by default (PW-1596): flipped now, every map would show a quarter of
today's dragon realms.

**What misleads if never decided.** Either the switch stays off (states never affect the history), or it goes on and dragons
(sapient peoples with their own polities) lose three quarters of their realms on every card and map, with that land going to
states instead.

**Options.**
- A: one realm per dragon people (now). Simple; 4-6 realms. Matches "one culture per dragon kind" literally, not the read-out.
- B: a realm per region of a dragon people's range, regions cut the way the cultures engine cuts a people (by distance and time
  apart), done cheaply inside the history: e.g. pieces joined within a wider radius than a dragon's flight
  (`round26/dragon_ranges.py`: ~100 groups at ~720 km, too many still) and only pieces of a minimum size. Needs one new number.
- C: the read-out keeps drawing dragon realms (per culture) on top of the live map, the history keeps A for its own feedback.
  Two sources of truth for one layer.
Lean: B, sized against the read-out on the same history (round26/measure.py's RO-on rows), then re-run the five pairs and flip.
- [ ] live dragon realms within ~25 % of the read-out on the same history on the five pairs, five-step averages

## Updates
- 2026-11-11: Status todo -> done. Live dragon realms merged (281d/e); states on by default (PW-1700).
- 2026-11-10: Coordinator ruling 11-10: B. One realm per region of a dragon people's range, regions cut the way the cultures engine cuts a people, sized against the read-out on the same history. Not A (loses three quarters of dragon realms) and not C (two sources of truth for one map layer). Lane 281d.
- 2026-11-10: Created from inbox draft draft-live-dragon-realms-per-people-too-few.md (found by lane281c).
