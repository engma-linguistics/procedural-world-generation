# Polities round 20: the live town count as the ledger's sites (PW-1608; PW-1597's check; lane 258)

## In plain words

- **The town count now matches the ledger.** With polities in the history (`POLITIES_LIVE`), the live tech tree reads how many
  town-sized places each people has. The history now keeps the settlement ledger's own sites while it runs: per cell a chief
  place and a second people's place, founded, grown, handed on and left by the ledger's rule, and sized on the ledger's own inputs
  (the land use's people and farmers per cell, and who leads a cell and who is second), taken from the history as a stored frame
  takes them. Live against the same run's ledger, town cells now agree within about 3% at every time on L6 and L7 seed 7
  (L7 seed 7, 3,000 years ago: 2,806 against 2,853; before, 4,252 against 2,811). No new numbers.
- **The calendars still differ, for two reasons.** The totals agree, but each people's *first* towns come 0.2-0.5 kyr later live:
  the ledger, built after the run, reads density from the next stored frame (up to 0.5 kyr ahead) and the history counts at the
  start of each step. Rebuilding the after-run tree on the same history with the live count gives the live tree's writing date
  on L6 seed 3 (5,536 ya) and L7 seed 10 (4,462): there that timing is the whole gap (307 and 333 years). On L6 seed 7 it is 106
  of 257 years; on L7 seed 7 none of 152: there the live tree itself lands one of its steps from the after-run tree on the same
  history and town count (L6 seed 7 later, L7 seed 7 earlier), for a reason not found.
- **PW-1597's check fails on all five pairs** (section 3: writing 152-333 years apart), so the switch stays off and the goldens
  are untouched. The default (switch off) did not move: the off run on this code equals the off run on the code before it.

## 1. What was built (`LivePolities.town_cells`, `frame._composition`)

Lane 254 had the history count, each century, every cell whose central place (sized on the history's own densities, led by the
people with the most heads by the history's own count) was of town size that step. The ledger (`settlements.derive`) differs in
two ways, and the count now follows it in both:

- **Sites with a lifecycle.** A site is founded where its target holds FOUND for FOUND_STEPS (a second people's place only once
  that people has been the cell's second for MINORITY_STEPS), grows toward its target with TAU_KYR, changes hands with the cell's
  lead (a chief place), and is left when its target stays under ABANDON for ABANDON_STEPS (MINORITY_ABANDON_STEPS), under the sea
  or ice, or merged once its own people has led the cell for HAND_KYR. A town cell is a site whose people reach TOWN_MIN for its
  holder's stage. Targets as the ledger: the largest of a village on the cell's own settled, a town on its ring where it is the
  best of the ring, a city on two rings where it is the best of those, each capped by stage (caps_of); tiers by the holder's
  villages / towns / cities (a mining people's delving or fortifications counting as cities).
- **The ledger's inputs.** The settled are the land use's people per cell (`landuse.frame_inputs`, quantised as stored) times
  its farmers' share, FISHER_SHARE of the rest on a harbour or navigable river, and a mining lead's halls; the cell's lead and
  second people and their shares are compose's (`frame._composition`, now shared with `_frame`). Before, the history used each
  people's own density and farm share, and its own lead by heads: per people the live and ledger counts were off both ways
  (L6 seed 7, 3,000 years ago: humans 432 live against 216 in the ledger, hobgoblins 215 against 337).

Not kept: war's sacks and razings, the ledger's seeded river shifts, and its blending of the frames either side of a step (the
ledger reads density from the next frame too, up to 0.5 kyr ahead; the history cannot). First town cells come 0.1-0.2 kyr later
live than in the ledger for most peoples (gnomes at L6 seed 7: 5.6 against 6.8 kyr ago), which is that look-ahead.

A first try (code_A: the lifecycle only, on the history's own densities and leads) undercounted (L6 seed 7: 2,200 against
2,416 three kyr ago; 3,088 against 3,778 one kyr ago) and pushed writing to 2,797 ya; it was replaced.

## 2. Town cells, live / the same run's ledger (`round19/footprint.py`; dnd, 30 kyr, languages skipped)

| run | 7 kyr | 6 kyr | 5 kyr | 4 kyr | 3 kyr | 2 kyr | 1 kyr | now |
|---|---|---|---|---|---|---|---|---|
| L6 4360a3 seed 7, on (5b3c79) | 92/103 | 763/791 | 1,196/1,221 | 1,695/1,738 | 2,409/2,414 | 2,906/2,973 | 3,735/3,784 | 4,116/4,071 |
| L7 899985 seed 7, on (831945) | 259/282 | 540/591 | 1,299/1,213 | 1,718/1,671 | 2,806/2,853 | 4,181/4,223 | 5,846/5,796 | 7,265/7,125 |

Lane 254b on 81fc3851 (round19.md section 4): L6 seed 7 3 kyr 2,770/2,422; L7 seed 7 3 kyr 4,252/2,811, 1 kyr 6,128/5,737.

The after-run tree on the switch-on history, writing median of the 12 largest (`round20/rebuild_live_foot.py`):

| run | live tree (stored) | rebuilt, ledger footprint | rebuilt, live footprint |
|---|---|---|---|
| L6 seed 7 (5b3c79) | 2,748 ya | 3,005 | 2,899 |
| L7 seed 7 (831945) | 4,153 | 4,305 | 4,305 |
| L6 seed 3 (f6c2e8) | 5,536 | 5,843 | 5,536 |

So the town count still carries the whole gap on L6 seed 3 and 106 of 257 years on L6 seed 7, though the totals agree within a
few per cent: what differs is *when* each people's first towns come. First town cell, live / ledger, kyr ago, L6 seed 3: humans
10.3 / 10.8, elves 8.7 / 9.1, triton 5.8 / 6.2, dragonborn 8.2 / 8.5, leonin 9.2 / 9.4, kenku 8.0 / 8.2 (hobgoblins, tabaxi and gnomes
equal or 0.1 the other way). Two things make the ledger's first towns 0.2-0.5 kyr earlier, neither of them history:
- the history counts at the start of a century step (the peoples have not moved yet: the state at the end of the last step),
  while the ledger's step at that date reads the frames at that date (the state at its end): one step, 0.1 kyr;
- the ledger blends the stored frames either side of a step (frames every 0.5 kyr): the people per cell drawn straight between
  two frames (the later one up to 0.5 kyr ahead), and the cell's lead taken from the nearer frame, up to 0.25 kyr ahead. The
  after-run read-out sees a little of its own future (draft `draft-ledger-reads-next-frame.md`).

## 3. The five pairs on 3a52d1bc (same code on and off; dnd, 30 kyr, languages skipped; `round19/live_run.py`, `round16/measure_v1.py`)

| world, seed | on: first state / writing median | off: first state / writing median | on - off | lane 254b on 81fc3851 (on - off) |
|---|---|---|---|---|
| L6 4360a3, 7 | 3,300 / 2,748 ya (5b3c79) | 3,400 / 3,005 ya (b48385) | first state 100 later, writing 257 later | 200 / 106 later |
| L6, 3 | 6,300 / 5,536 (f6c2e8) | 6,600 / 5,843 (19913f) | 300 / 307 later | equal |
| L6, 10 | 5,100 / 4,305 (fb737f) | 5,300 / 4,462 (29810d) | 200 / 157 later | 400 / 546 later |
| L7 899985, 7 | 3,400 / 4,153 (831945) | 3,600 / 4,305 (9a6da2) | 200 / 152 earlier | 400 / 226 earlier |
| L7, 10 | 4,600 / 4,462 (40f324) | 4,300 / 4,795 (63b624) | first state 300 earlier, writing 333 later | 100 earlier / 490 later |

The after-run tree on each switch-on history with the live town count in place of the ledger's (`round20/rebuild_live_foot.py`)
gives the live tree's writing on L6 seed 3 (5,536) and L7 seed 10 (4,462): there the whole gap is the town count's timing. On
L6 seed 7 it gives 2,899 (106 of the 257 years), on L7 seed 7 the ledger's own 4,305 (none of the 152). L7 seed 10's town cells,
live / ledger: 3 kyr 1,326/1,363, 1 kyr 4,811/4,409 (+9%), now 3,599/3,468.

Scratch runs, deleted after the lane; the live footprints were kept only as long as the lane.

The off runs on this code equal the off runs on its parent (L6 seed 7: b48385 here and 5cf853 on code_A, both 3,400 / 3,005;
the frame refactor is the same arithmetic).

**PW-1597's check fails on all five pairs** (writing 152-333 years apart; first states 100-300). The gap narrowed on L6 seed 10
and L7 seeds 7 and 10 and widened on L6 seeds 7 and 3, and it is now mostly later with the switch on at L6. Not flipped (PW-1596). The tree's writing dates are its steps (2,748, 2,899, 3,005, ... 4,153, 4,305 ya: 106-157 years apart
here), so "within ~100 years" asks for the same step or, barely, the next.

## 4. Left

- The live tree lands a step from the after-run tree on the same history and the same town count, both ways (L6 seed 7 later,
  L7 seed 7 earlier). Round 19 ruled out contacts, tracks, starts, tamings, goods and regions one at a time on 81fc3851; what is
  left is what the live tree reads *as the history runs* that the after-run tree reads finished (PW-1597).
- The ledger's look-ahead and the history's start-of-step count (section 2; draft `draft-ledger-reads-next-frame.md`).
- PW-1596 (the flip) waits on PW-1597; no steadiness runs were made.
