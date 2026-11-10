# Polities round 23: the last on/off calendar gap was the ledger's thinned town series (PW-1597, PW-1596; lane 278)

## In plain words

- **Where the two calendars part (L7 world 899985 seed 10, the worst pair).** On main 3bd4bd28, with polities in the history
  (`POLITIES_LIVE`) on, the 12 largest peoples' writing median is 5,340 years ago; off, 5,637. The split (section 1) puts all of it
  in one place: **the town footprint the tree reads**, not the history and not the contacts. The after-run tree rebuilt on the
  switch-on history gives off's 5,637 with the settlement ledger's footprint and the live tree's 5,340 with the footprint the live
  tree counted. The first record that parts is the hobgoblins inventing writing: 6,391 years ago with the ledger's footprint,
  5,948 with the live one. The world's writing then comes from them.
- **Why.** The hobgoblins learned `towns` 7,379 years ago. Before that their places are capped a person under a town (999).
  The ledger keeps each place's population as 40 points (SERIES_KEEP) and the footprint reads it back by straight lines between
  them; two of their places stored 985 at 7.5 kyr and 1,097 at 7.3 kyr, so at 7.4 kyr they read 1,041: two "towns" a century
  before the ledger itself made any. The tree then read the footprint drawn toward the *next* sample, so its step at 7,379 years
  ago saw 15 town cells: the hobgoblins counted as settled (arm S, D60 B: writing needs towns of one's own) one tree step
  (260 years) early, and the waiting hazard started a step sooner. The live tree, counting step by step with only the counts so
  far, saw none.
- **Real feedback or accounting?** Accounting. The two histories are the same until 7.0 kyr ago (the first track that differs:
  hill giants, 7,000 years ago, 9 people in 888,000), and the after-run tree on the switch-on history against the switch-off
  history gives the same writing median (5,637 both: section 1, line "history"). Live states change one people's writing
  (aarakocra, 300 years) and nothing in the median. So the done-check stays as the coordinator set it (on against off), and no
  decision for Daniel is needed on this point.
- **The fix (9306190c), by mechanism, and it moves the default.** The ledger's thinning now keeps every point where a place's
  size class turns (a village becoming a town, a town a city, and the point before), so reading it back puts every step on the
  right side of each threshold; and the after-run tree reads the footprint at the sample at or before each time, held, as it
  already reads the tracks (lane 265) and as the ledger reads frames (PW-1612). Both are read-outs losing a look-ahead.
- **PW-1625 (contacts) does not reach writing here.** The live tree and the after-run tree on the same history and footprint
  still differ in thousands of deep records (the tortles' meteoric iron 1,257 against 3,087 kyr ago, by contact), all from the
  contact fronts, but writing is the same for all 12 (section 1, "accounting (tree)"). Not built here; left with its ticket.

## 1. The split (L7 899985 seed 10, main 3bd4bd28, same code on and off; dnd, 30 kyr, languages skipped)

Runs 77ef27 (on) and 2e818e (off) with `round19/live_run.py`; `round23/split.py` rebuilds the after-run tree (techtree.rebuild) on
each history with the ledger's footprint and with the footprint the live tree read, and lists the oldest records that differ.

| calendar | writing median of the 12 largest |
|---|---|
| live tree (switch on, as stored) | 5,340 ya |
| after-run tree on the switch-on history, the live tree's footprint | 5,340 |
| after-run tree on the switch-on history, the ledger's footprint | 5,637 |
| after-run tree on the switch-off history (ledger) = off as stored | 5,637 |

- history (rebuilt on-history against rebuilt off-history, same tree): 942 records differ, the oldest at 23.3 kyr (who passed
  the leonin netting, same date); writing differs for one people (aarakocra, 4,305 against 4,006 ya). Median unchanged.
- accounting, tree (live against rebuilt on the same history and footprint): 4,935 records differ, the oldest from the contact
  fronts (PW-1625); writing differs for none.
- accounting, footprint (rebuilt on-history, live against ledger footprint): the oldest record that differs is the hobgoblins'
  writing (5,948 against 6,391 ya, invented), then everything downstream; writing differs for 14 peoples.

`round23/trace_tech.py` (the hobgoblins' writing at each tree step, both footprints): at 7,379 ya the ledger's footprint reads
15.3 town cells (settled, may invent), the live one 0 (not yet); from 7,119 both read 137-139. Ready 7,379 against 7,119; the
hazard summed reaches the hobgoblins' draw at 6,391 against 5,948. `round23/foot_when.py`: the hobgoblins' town cells, live /
ledger, 7.4 kyr 0 / 2, 7.3 77 / 66, 7.2 122 / 114, then within 3%; all peoples together within 4% from 7.6 kyr on (7.7 kyr:
191 / 260).
The two at 7.4 kyr are second-people places (sites 4234, 6688) whose stored series runs 985 (7.5) -> 1,097 (7.3).

With the footprint held alone (`split.py ... hold`), off moves 5,637 -> 5,539 and the hobgoblins still invent at 6,391 on the
ledger's footprint: both halves are needed.

## 2. The five pairs on the same code

**Before the fix, main 3bd4bd28** (on and off both on 3bd4bd28's planet/; dnd, 30 kyr, languages skipped; `round19/live_run.py`,
`round16/measure_v1.py`). First state / writing median of the 12 largest:

| world, seed | on | off | on - off |
|---|---|---|---|
| L6 4360a3, 7 | 3,800 / 3,172 ya (6f9aec) | 4,000 / 3,172 (8baaea) | writing equal; first state 200 later |
| L6, 3 | 6,600 / 6,166 (4487f0) | 6,800 / 6,166 (1597be) | writing equal; first state 200 later |
| L6, 10 | 5,900 / 5,061 (50c4d5) | (queued, not measured by hand-off) | |
| L7 899985, 7 | (queued) | (queued) | |
| L7, 10 | 5,500 / 5,340 (77ef27) | 5,500 / 5,637 (2e818e) | first state equal; writing 297 later (1.5 steps) |

All the default numbers moved since lane 265's table (round22.md section 3) with the merges since (PW-1584 km rules, PW-1627 km
rings, PW-1640 harbour water), so these are not comparable with it.

**On the fix, 9306190c: not measured by hand-off.** The ten runs are queued in the lane's scratch (jobs4: N6s7, N6s3, N6s10,
N7s10, N7s7, on and off). What to expect, from the mechanism: the switch-on runs do not move (the live tree already read the
footprint as it was counted, and the ledger's thinning does not enter the history); the switch-off calendars move later where a
people's first towns were read early. An offline re-make of an off run's read-outs on the new code (`round23/offline_off.py`) did
not reproduce the stored off tree on its own code (L6 seed 7: 3,470 against 3,172 ya; the run's first tree is built with Crossings'
raw label and the history's own frames, the rebuild with the filled map), so it is not used; the measure needs the real reruns.

## 3. Logistics: where the live war code would read a reach (for the logistics lane; nothing built here)

Daniel's picture: small early kingdoms raiding each other, campaign and siege reach growing with logistics. The places in
`history/polity_live.py` (and the shared `polities.py` it calls) where a logistics reach would plug in:

- **`polities._reach`** (called by `LivePolities._step` for every seat's claim and by `_confederations`): today a seat's budget
  in foot-km is CHIEF_KM or STATE_KM x LAW_X x DISTANCE_X, capped at STATE_MAX_KM unless `wide` (WIDE_BY), with riding and roads
  making a km cheaper. A logistics tech (or a tier of them) is a multiplier here, on the budget or on the cap; it moves how far a
  polity *rules*, not how far it can strike.
- **`polities.war_v0`'s pairs** (`ctx["borders"]`, `PO.borders(owner, g)`): plain war today is only between polities that share a
  border. Raiding at a distance needs a second source of pairs: polities within a campaign reach of each other (as `_expedition`
  already finds for authored invasions, through unruled land). A `ctx["reach"]` hook beside `ctx["borders"]` is the seam.
- **`invasions.campaign_budget` and `polities._expedition`** (the history's hook is `ctx["expedition"]` with `need_x=NEED_X`):
  the expedition budget is max(CAMPAIGN_KM, EXTENT_X x radius) x mobility. Logistics would scale this budget; the same function
  serves the read-out and the history, so one change reaches both.
- **`polities.strength`** (ctx["strength"], `S_pid` in `_step`): settled people x MIL_X per military edge. A loss-of-strength
  gradient (Boulding 1962: power falls with distance from the base) would read the distance from the capital to the front and a
  logistics reach; a siege (taking a walled capital: settlements' `walled_kyr`, `_War.walled`) could read its own siege reach here.
- **`WAR_P`, `WAR_ODDS`** (war_v0): a raid that takes goods or people but not land would be a new outcome beside "taken", with the
  winner's fates (`LivePolities._fates`) as the template for what happens to the people.

## 4. Left

- The five pairs on 9306190c (section 2), then the bar (within one tree step on every pair, no consistent sign). If it passes:
  PW-1596's flip in its own commit, the not-slow suite and goldens, and the steadiness table under the nudge.
- PW-1625 (contacts): real, thousands of deep records, but no writing date on L7 seed 10; check on the other pairs before building.
- The sensitivity itself: one or two town cells a century apart move the world's writing a tree step or two (draft
  `draft-writing-hinges-on-one-peoples-first-town.md`).
- The first states with the switch on were 200 years later on both L6 pairs measured on 3bd4bd28 with writing equal: not
  diagnosed (the state gate reads writing and kingship or law and a city; the live history's seats are counted in the history).

Scratch runs under the lane's scratch root, to be deleted after the lane.
