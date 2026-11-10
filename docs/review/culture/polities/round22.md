# Polities round 22: the one-step residual found (the two trees mapped a people's regions differently); the town count at the end of a step (PW-1597, PW-1612 B; lane 265)

## 1. Diagnosis of R (L6 4360a3 seed 7, switch on, main a6ed6954; written before the code below)

R (round20.md section 4): on the same history and the same town footprint, the live tree and the after-run tree land a step
apart. Run fee5e2 (switch on, main a6ed6954, dnd, 30 kyr, languages skipped): the live tree's writing median of the 12 largest
is 2,698 ya; `techtree.rebuild` on the same run with the footprint the live tree read gives 2,899 ya (`round22/diff_known.py`).

**Where the two first part.** Listing every (people, tech) record that differs, oldest first: the first is nowhere near writing
or towns but 2.6 Myr ago: the tortles invent innate magic at 2,579.684 kyr live and 2,674.059 kyr (one tree step earlier)
rebuilt; their bone tools follow one step apart (1,213 against 1,257 kyr), and from there the contacts and everything
downstream: 3,824 records differ by the present.

**Why.** Tracing what each tree reads for the tortles at each of its steps (`round22/trace.py`, live and rebuilt on the same
run): same techs, same landmasses reached, different *region learners* (PW-1471, D55). At 2,978 kyr the live tree splits the
tortles' pool over two regions (landmass 2: 0.611, landmass 7: 0.283 of the range), the rebuilt tree over three (0: 0.113,
2: 0.570, 7: 0.297); three learners give a larger summed hazard, so the rebuilt tortles invent a step sooner. Reading the
stored frame (3,296 kyr) both ways (`round22/regions_check.py`): 18% of the tortles' weight then lay on cells that are sea
today. The after-run tree's landmass map (`techtree.landmass_of`, `demes.landmass_rank`) gives today's sea the nearest
landmass; the live tree read Crossings' own label, which leaves it out (-1). Leaving it out reproduces the live split
(2: 0.611, 7: 0.283). A smaller second difference: the live tree read the raw presence (each line, every cell down to 0.05),
the after-run tree the frame's presence table (peoples as wholes, established cells only, EST 0.12, whole %): 0.6112 against
0.6109 on landmass 2. Neither is something the live tree reads *as the history runs*: it is the same frame read through two
different maps.

**A third, after-run only: the tracks look ahead.** Between stored frames the after-run tree drew each people's population,
density and range straight toward the *next* frame (`techtree._at`, `_area_at`); the live tree has only the frames so far and
holds the last. Holding the rebuilt tree's tracks at the frame at or before each time moves its writing median 2,899 -> 2,848 ya
on fee5e2 and leaves the first divergence where it was: the same kind of anachronism as the ledger's (PW-1612 A), up to 0.5 kyr
ahead in the recent epoch and a whole frame gap in the deep.

**Ruled out on fee5e2** (`round22/replay.py`, the rebuilt tree on the live footprint, one live habit at a time): stepping in the
history's steps, tamings as known then, goods on the range of the time: none moves the first divergence or writing (2,899).

## 2. What changed (three commits on a6ed6954)

- **PW-1612 B.** `History.run` calls `rule.end_step(step)` after the peoples move (beside the frame); `LivePolities` counts its
  town cells there (`town_cells`, rule unchanged, `fresh` on a step that stores a frame), so a frame's step takes the state that
  frame stores, as the ledger reads it; the tree reads the count from the next step. Before: at the start of the step, on the
  state one century older.
- **R.** `LiveTech` maps regions on the after-run tree's landmass map (`LiveTech.landmass`: Crossings' ranks, today's sea taking
  the nearest) and on the presence as the frame stores it (`History.presence_stored`, sharing `FrameMixin._presence` with
  `_frame`), kept at the end of a storing step (`LiveTech.at_frame`) and read at the next feed (peoples may start or arrive in
  between). Switch-on path only.
- **Tracks.** `techtree._at`, `_area_at` read the stored frame at or before a time (`_frame_of`). This changes the default
  (switch off) calendar: the after-run tree no longer reads up to a frame gap of its future (coordinator's PW-1612 ruling: a
  read-out must not see the future). The live tree read so already.
- No number changed. Tests: `test_the_live_town_count_is_taken_at_the_end_of_a_step`,
  `test_the_live_tree_maps_regions_as_the_after_run_tree`.

On the switch-on run with all three (314c9b), the first difference between the live and the rebuilt tree is now 1,560 kyr ago
and only in *who* gave the hominids language (same date); the first date that differs is the felines' spirit ritual (943 kyr,
by contact, live; never before the felines end, rebuilt). Writing: live 2,848, rebuilt on the live footprint 2,899 ya (one
step). What is left there is the contacts: the live tree reads each pair's border at its last stored touch and re-times fronts
as it grows (PW-1473, `LiveTech._links`, `_retime`), the after-run tree one interval per pair with the whole run's median
border (`techtree.links_of`). The live tree cannot know the whole run's median; the after-run tree could read the border of the
time, but that is a change to how every front is timed, not done here.

## 3. PW-1597 on this code (on and off both on 3e0e8b80's planet/; dnd, 30 kyr, languages skipped; `round19/live_run.py`, `round16/measure_v1.py`)

The tree's own steps here (`round22/grid.py`; the same grid in every run): ... 2,797, 2,899, 3,005, 3,115 ... 4,153, 4,305, 4,462,
4,625, 4,795 ... 6,625, 6,868 ya. A median of 12 that falls between two steps is their mean (2,848 = 2,797 and 2,899).

| world, seed | on: first state / writing median | off: first state / writing median | on - off (writing in tree steps) | lane 262 on 061c6eca |
|---|---|---|---|---|
| L6 4360a3, 7 | 3,400 / 2,848 ya (314c9b) | 3,400 / 3,005 (3bc51d) | equal; writing 157 later (1.5 steps) | 100 / 307 later |
| L6, 3 | 6,600 / 6,746 (898473) | 6,600 / 6,868 (ed58ba) | equal; writing 122 later (0.5 step) | equal |
| L6, 10 | 4,900 / 4,153 (2638a0) | 4,900 / 4,153 (39b7c4) | equal | 400 / 309 later |
| L7 899985, 7 | 3,500 / 4,305 (a40118) | 3,500 / 4,305 (2ca8e9) | equal | 100 / 152 later |
| L7, 10 | 4,600 / 4,384 (e19ccb) | 4,200 / 4,710 (780e24) | first state 400 earlier; writing 326 later (2 steps) | 200 earlier / 333 later |

**Fails the bar** (within one tree step on every pair, no consistent sign): L7 seed 10 is two steps apart and L6 seed 7 one and a
half, and writing with the switch on is later or equal on all five pairs. Closer than lane 262's (two pairs now equal in both,
L6 seed 3 half a step), but not through. **Not flipped (PW-1596); no steadiness runs; goldens untouched.** This was the third
attempt at this gap (lanes 258, 262, 265).

What each change did to the live calendar, L6 seed 7 (switch on; first state / writing): main a6ed6954 3,300 / 2,698 (fee5e2);
+ B 3,400 / 2,848 (ab1aa0); + B, R and the tracks 3,400 / 2,848 (314c9b). B moved it one step toward off; R and the tracks
changed nothing there (R moved the tortles' early inventions, which did not reach writing on this seed).

What is left (section 2, last paragraph): on the same history the two trees still read contacts differently (draft
`draft-after-run-tree-reads-whole-run-borders.md`). L7 seed 10 is not that alone: its on and off histories differ (states 2,000
years ago 53 on against 80 off), so part of the gap may be the history itself, which the bar does not allow for.

## 4. The default (switch off): main a6ed6954 against this code (same world, seed, tree; `round21/firsts.py`)

| world, seed | first state, main / new | writing median, main / new | sites founded, main / new | median founding |
|---|---|---|---|---|
| L6 4360a3, 7 (4d51eb / 3bc51d) | 3,400 / 3,400 ya | 3,060 / 3,005 | 13,717 / 13,717 | 3,900 / 3,900 ya |
| L6, 3 (7a0fc4 / ed58ba) | 6,600 / 6,600 | 6,868 / 6,868 | 12,701 / 12,701 | 4,100 / 4,100 |
| L6, 10 (7b30e7 / 39b7c4) | 4,900 / 4,900 | 4,153 / 4,153 | 13,734 / 13,733 | 4,300 / 4,300 |
| L7 899985, 7 (f9b953 / 2ca8e9) | 3,500 / 3,500 | 4,305 / 4,305 | 32,173 / 32,174 | 3,400 / 3,400 |
| L7, 10 (0aadc9 / 780e24) | 4,300 / 4,200 | 4,710 / 4,710 | 35,452 / 35,447 | 2,000 / 2,000 |

Only the tracks change touches the default (B and R are switch-on only). First towns of the 12 largest are unchanged except one
people (L6 seed 10 gnomes, 300 years later). Per-people writing moves on a few: L6 seed 7 humans 110 years later, orcs 114 and
leonin 208 earlier, tabaxi 92 earlier; L6 seed 10 orcs 131 later, gnomes 527 later; L7 seed 7 half-elves 163 earlier. One first state
moved (L7 seed 10, 100 years later).

Scratch runs under the lane's scratch root, deleted after the lane.
