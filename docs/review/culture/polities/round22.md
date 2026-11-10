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

## 3. Where lane 265 stopped (paused by the coordinator, 11-09 20:45)

- PW-1597's check on this code was **not made**: the queue (`scratchpad/l265/jobs3.txt`: C on/off for the five pairs on code
  f43385ce's planet/ (= 3e0e8b80), plus main a6ed6954 off for the three L6 pairs) was killed 18 minutes in, with no run finished.
- Measured so far, L6 4360a3 seed 7 switch on (first state / writing median of the 12 largest): main a6ed6954 3,300 / 2,698 ya
  (fee5e2); + PW-1612 B 3,400 / 2,848 (ab1aa0); + B + R + tracks 3,400 / 2,848 (314c9b): B moves the live writing 150 years later
  (one step); R and the tracks change nothing on this run's live tree (the tracks change is after-run only). The switch-off run on
  this code is still to make; round21's off on 061c6eca was 3,400 / 3,005, but main has history changes since (counter, dispersal),
  so the baseline must be rerun on a6ed6954.
- L6 seed 10 on, main a6ed6954: 4,900 / 4,079 ya (4e67d8).
- To resume: rebuild the scratch root (`scratchpad/l265/mkroot.sh`), re-run `q.sh jobs3.txt` (go.sh waits for load <= 30),
  measure with `m.sh measure <tag> ...`, then the on/off table, flip or not (PW-1596). This is the third attempt at PW-1597's gap.
