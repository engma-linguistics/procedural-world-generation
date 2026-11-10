# Polities round 21: the ledger stops reading the next frame (PW-1612 A); PW-1597 re-checked (lane 262)

## In plain words

- **The settlement ledger no longer sees its own future.** Built after a run, it read each century step's people per cell
  drawn toward the *next* stored frame (up to 0.5 kyr ahead) and each cell's leading people from the nearer frame (up to
  0.25 kyr ahead). Now each step reads the stored frame at or before it, as it stands, until the next frame (frames every
  0.5 kyr). With polities in the history (`POLITIES_LIVE`), the history's own town count (lane 258's site keeping, which uses
  the ledger's inputs) now does the same: it takes its inputs only on a step that stores a frame and holds them until the next.
- **How far the default (switch off) dates moved.** Same five worlds and seeds, switch off, the code before (main, 6f230c7f) against
  this lane's (061c6eca): each people's first town comes 0-400 years later (one people 900 years, a few 100-300 earlier), the
  median founding date of all places moves 0-300 years later, and 3-8% fewer places are founded. The first state moved on 2 of 5
  pairs (L6 seed 3: 6,600 to 6,300 ya; L7 seed 7: 3,600 to 3,500) and one moved 100 years earlier (L7 seed 10: 4,300 to 4,400).
  The 12 largest peoples' writing median moved on one pair (L6 seed 3: 5,843 to 5,536 ya), unchanged on four.
- **PW-1597's check, new bar: fails.** On/off within one tree step on every pair with no consistent sign: on this code the first
  state and writing median agree exactly on L6 seed 3 and within one step on L7 seed 7, but writing is 307-333 years (two to three
  tree steps) later with the switch on on L6 seeds 7 and 10 and L7 seed 10, and on is later or equal on all five. **Not flipped**
  (PW-1596); no steadiness runs; goldens untouched (they hold no peoples output).

## 1. The change (`settlements.derive`, `LivePolities.town_cells`)

- `settlements.derive`: per step, `j` = the last stored frame with `ago_kyr >= step` (a 1e-9 tolerance); density, farm share,
  herd share, rain, land, ice, composition (lead, second, shares), the colonies' country and the raiders' presence all read frame
  `j`. Before: `(1 - w) * frame[j] + w * frame[j+1]` for density, farm, herd and rain, and frame `j+1` for the rest once `w >= 0.5`.
- `LivePolities.town_cells(ago, fresh)`: `fresh` (begin_step passes `step.store`) takes the inputs (frame_inputs, composition, land,
  ice, coast) from the history now; any other step keeps the last ones. Before, it took them every step. The site lifecycle,
  tech stages and caps still run every step, as the ledger's.
- Not kept: the history takes a frame's inputs at the *start* of that frame's step, the stored frame holds the state at its
  *end*: one century at each frame date (PW-1612's option B, not chosen).
- Test: `test_the_live_town_count_holds_a_frames_inputs_until_the_next` (tests/test_lineages.py).

## 2. The default (switch off) on main and on this code (same world, seed, tree; dnd, 30 kyr, languages skipped)

Runs: `round19/live_run.py` on frozen code snapshots; `round21/firsts.py` (first town cell of the 12 largest, sites' founding) and
`round16/measure_v1.py` (first state, writing median). Main's off runs reproduce lane 258's off numbers on 3a52d1bc exactly (no
planet/ change since), so main here is that baseline.

| world, seed | first state, main / new | writing median, main / new | sites founded, main / new | median founding, main / new | first town of the 12 largest, new - main |
|---|---|---|---|---|---|
| L6 4360a3, 7 (87f739 / 000027) | 3,400 / 3,400 ya | 3,005 / 3,005 | 14,605 / 14,175 | 3,700 / 3,500 ya | 100-300 later on 5, equal on 4, earlier on 2 (hobgoblins 300, dragonborn 100) |
| L6, 3 (6c158e / 7a1a5a) | 6,600 / 6,300 | 5,843 / 5,536 | 14,013 / 13,634 | 5,100 / 4,900 | 200-400 later on 7, equal on 3, humans 100 earlier |
| L6, 10 (a6281f / 22c1cd) | 5,300 / 5,300 | 4,462 / 4,462 | 14,597 / 13,940 | 4,100 / 3,900 | 100-300 later on 6, equal on 5, leonin 100 earlier |
| L7 899985, 7 (8b031f / 3b21e5) | 3,600 / 3,500 | 4,305 / 4,305 | 33,790 / 32,625 | 3,700 / 3,400 | 200-900 later on 4 (elves 7,300 / 6,400), equal on 6 |
| L7, 10 (c058e3 / eeca58) | 4,300 / 4,400 | 4,795 / 4,795 | 39,241 / 35,904 | 1,900 / 1,900 | 100-300 later on 6, equal on 4 |

Per people, writing mostly holds; it moves one or two steps for a few (L6 seed 3: all 12 later by 196-432 years; L7 seed 10:
orcs 258 and kenku 187 later, and the dragonborn 2,370 years *earlier*, 2,255 to 4,625 ya: one people's calendar crossing an arm's
threshold on a slightly different town footprint; L6 seed 7: orcs 114 and leonin 208 years earlier). Peoples
with no town of their own (half-elves, half-orcs) are left out of the first-town counts.

## 3. PW-1597 on this code (on and off both 061c6eca; the new bar: within one tree step, 106-157 years, with no consistent sign)

| world, seed | on: first state / writing median | off: first state / writing median | on - off | lane 258 on 3a52d1bc |
|---|---|---|---|---|
| L6 4360a3, 7 | 3,300 / 2,698 ya (4f2d7f) | 3,400 / 3,005 (000027) | first state 100 later; writing 307 later (3 steps) | 100 / 257 later |
| L6, 3 | 6,300 / 5,536 (0fa770) | 6,300 / 5,536 (7a1a5a) | equal | 300 / 307 later |
| L6, 10 | 4,900 / 4,153 (547f77) | 5,300 / 4,462 (22c1cd) | 400 later; writing 309 later (2 steps) | 200 / 157 later |
| L7 899985, 7 | 3,400 / 4,153 (722809) | 3,500 / 4,305 (3b21e5) | 100 later; writing 152 later (1 step) | 200 / 152 earlier |
| L7, 10 | 4,600 / 4,462 (3e4250) | 4,400 / 4,795 (eeca58) | first state 200 earlier; writing 333 later (2 steps) | 300 earlier / 333 later |

Passes on L6 seed 3 (where the look-ahead was the whole gap, round20.md section 2) and L7 seed 7; fails on three, and the sign is
consistent (writing on later or equal on all five). The live calendar is now late: holding the frame's inputs for five steps
delays the live town count as much as the ledger's (the totals per frame agree), but the history still takes each frame's inputs
one century before the frame it stands for, and its tree runs a step from the after-run tree on the same history (round20.md
section 4, L6 seed 7 and L7 seed 7, cause not found). **Not flipped (PW-1596); the steadiness runs were not made.**

Scratch runs under the lane's scratch root, deleted after the lane.
