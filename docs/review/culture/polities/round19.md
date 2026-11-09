# Polities round 19: why the live tech calendar ran late (PW-1597; lane 254, part 1)

## In plain words

- **The town footprint was not the cause.** With polities in the history (`POLITIES_LIVE`), the live tree counted only the lead
  people's town-sized places: about a seventh of the ledger's town cells (L6 world 4360a3, seed 7, now: 569 against 4,075; the ledger's
  are mostly second peoples' own places and mining peoples' halls). Feeding the live tree the switch-off run's own ledger footprint
  moved writing only 50 years (median of the 12 largest peoples: 2,952 ya against 3,005 ya live, 3,347 ya off) and the first state
  100 years (3,200 against 3,300; off 3,700). The footprint is now counted as the ledger counts it anyway (below): writing 2,899 ya.
- **Nor the contacts, the tracks, the tamings, the starts or the stepping.** Each fed whole (live runs with the finished run's
  contacts or tracks; offline replays of the after-run tree in the history's steps, with starts, ends and tamings as known then):
  writing 2,899 / 2,899 ya live, 3,347 ya on every replay.
- **The cause: the after-run tree read today's ranges for every century before.** Region learners (PW-1471, D55: a people over
  several landmasses, or a big stretch of one, is several learners) were read from the *present* range, gated only by the date each
  landmass was reached. The live tree reads the range of the time. Replaying the after-run tree on the switch-on run with each
  frame's range gives exactly the live calendar (writing 3,005 ya, towns' median 6,625 ya, against 3,347 and 6,868 with today's
  range). The after-run tree on the *same history* gives off's dates (3,347 ya): the history is the same, the input was not.
- **What was built.** The after-run tree (techtree.build, rebuild) now reads each people's regions from its range at each stored
  frame (`Calendar.regions_through`, `regions_at`; the presence table), as the live tree does. The live tree's town footprint
  (`LivePolities.town_cells`) now counts the ledger's places: the second people's own place and mining peoples' halls, fishers on
  harbours and navigable rivers (settlements' FISHER_SHARE, HOLD_SHARE, MINORITY_SHARE/MAX, HOLD_MAX; no new number).
- **What it does to the default (switch off).** The calendar moves later, to the live one's: on L6 seed 7 the rebuilt off run's
  writing median goes from 3,347 to 3,005 ya (rebuilt on and off now both 3,005). This is the read-out losing an anachronism, not
  the history changing.
- **Not done in this part (handed off):** the five-pair on/off table on the new code, PW-1596's re-rolled steadiness check, and
  the flip decision. Runner, nudged trees and scripts are ready (section 3).

## 1. The diagnosis runs (L6 4360a3, seed 7, dnd, 30 kyr, languages skipped; `round19/live_run.py`, `round16/measure_v1.py`)

| run | code | first state | states 2,000 / 1,000 / 0 ya | writing median (12 largest) |
|---|---|---|---|---|
| off (20211a) | f1c313b6 | 3,700 ya | 146 / 163 / 177 | 3,347 ya |
| on (be8750) | f1c313b6 | 3,300 ya | 120 / 141 / 165 | 3,005 ya |
| on, fed off's ledger footprint (11bdb7) | + footprint arm | 3,200 ya | 124 / 138 / 167 | 2,952 ya |
| on, town cells as the ledger's (babe9e) | + town_cells | 3,200 ya | 130 / 145 / 167 | 2,899 ya |
| on, + whole-run contacts (54cfd0) | + town_cells | 3,300 ya | 105 / 151 / 176 | 2,899 ya |
| on, + whole-run tracks (cbeb1c) | + town_cells | 3,200 ya | 132 / 146 / 166 | 2,899 ya |

Town cells, all peoples (`round19/footprint.py`, live / the ledger's), 6 / 3 / 0 kyr ago: before 233 / 454 / 569 against 831 / 2,427 /
4,075 (off); with the ledger's places 626 / 2,770 / 4,149 against 792 / 2,422 / 4,116 (that run's ledger).

## 2. The replays (`round19/replay.py`, `round19/rebuild.py`; read-only, on be8750's history)

| after-run tree | writing median | towns median |
|---|---|---|
| in one go (techtree.build, as stored for an off run) | 3,347 ya | 6,868 ya |
| in the history's steps | 3,347 | 6,868 |
| + starts and ends as known then | 3,347 | 6,868 |
| + tamings as known then | 3,347 | 6,868 |
| + goods held on the range then | 3,347 | 6,868 |
| + regions on the range then | **3,005** | **6,625** |
| the live tree (stored) | 3,005 | (12 peoples: 4,305-7,649) |

After the change, `techtree.rebuild` gives 3,005 ya on both be8750 (on) and 20211a (off).

## 3. Left for the next lane

- The calendar table on the new code: L6 4360a3 seeds 7, 3, 10 and L7 899985 seeds 7, 10, on and off (`round19/live_run.py`;
  scratch runner `go.sh tree seed on|off tag world`).
- PW-1596: same ruler 1,000 years ago / now, on against off, three nudges per seed (halflings among humans 0.8 -> 0.9, goblins
  among hobgoblins 0.8 -> 0.9, gnomes among dwarves 0.6 -> 0.7) on seeds 7 and 3 (`round14/measure.py --pair`).
