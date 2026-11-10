# Polities round 25: the live seats fix landed, the state counts, and the flip (PW-1596; lane 281b)

Lane 281b picks up round 24's hand-off: land the live-seats fix (`round24/live_seats.patch`), find out why the live state counts
run under the read-out's, measure the five pairs on one commit, and flip `POLITIES_LIVE` if the bar holds.

## 1. The fix and its tests

The patch applies cleanly on main 652d6cb8. The two fixtures that seated nothing (round24 section 3) did so because the fake
history's lent calendar had no `villages`: the ledger's tiers start there (`_allowed`: no towns without villages, as settlements'
`allowed`), so `town_cells` founded no place at all, whatever the farmers. `_live_setup` now lends `villages` too and grows the
ledger's places from nothing over 4 to 1.3 kyr ago (`_grow_places`, 28 century steps of `end_step`). The expedition test moves its
peoples first, so it grows the places again on its own layout. The two tests that grow places from nothing themselves (the live
tree's town footprint, PW-1472; the held frame inputs, PW-1612) take `places=False`. No assertion changed.

## 2. Why the live state counts run under the read-out's: written diagnosis (before any run)

Round 24 measured, L7 899985 seed 7 (patch on caa44c4d, run e65944 on, 11a7fe off): states 2,000 / 1,000 / 0 years ago 75 / 148
/ 212 on against 90 / 182 / 240 off. The read-out (derive, switch off) and the live polities share the war (`polities.war_v0`),
the claims (`_claim`, `_reach`), the cool-down after a fall and the tier rule; with the patch both seat on the ledger's places.
What still differs:

1. **The history.** Switched on, the live polities feed the history from their first state on: the winners' fates (expulsion,
   razing: `_fates`), pacification under a state, the frontier. Fewer or smaller peoples where wars were mean fewer places big
   enough for a state. Legitimate: it is the switch doing its job.
2. **Consolidation.** With the patch the first live state comes 1,700 years earlier on this pair (5,100 against 3,400 ya), so
   the live states fight for longer. A war that takes a capital ends a state (its seat becomes a province: `lord`). If the live run
   has as many states founded but more ended by conquest, the lower count is states dying in wars. Legitimate as far as the war
   is the read-out's own (it is the same function), but the conquest's feedback on the history (fates) is live-only.
3. **The seat test's inputs.** `town_cells` is the ledger's rule on the history's inputs, but not the whole ledger: no war sacks
   and razings (those would make live places *bigger*, not fewer), no seeded river shifts, no blending of the frames either side of
   a step; and the seats read the places one step behind (end of the last step). A systematic shortfall of state-sized places
   here would be a bug.
4. **The confederations (1b)** still read the history's own places in the live path, the ledger's in the read-out. Fewer live
   confederations would show as fewer states with fewer founded.

**The measure that separates them** (`round25/counts.py`): on the switch-on run, the live counts against the read-out on the same
history (derive with the live map hidden). Live ~ read-out-on-the-on-history, both under off: the history (1, 2's feedback). Live
under read-out-on-the-on-history: the live path itself, then split by "ever a state by then" (fewer founded: 3 or 4) against
"ended by conquest" (more conquered: 2's war).

## 3. Measured (L7 899985 seed 7, dnd, 30 kyr, languages skipped; `round19/live_run.py`)

Code: 8ba3d691 (main 652d6cb8 + the patch + the fixture fix). Runs in the lane's scratch root: **560796** (on), **5f4b2e** (off),
**509cb7** (on again, through `round25/seat_dump.py`, which writes each live seat's place out and changes nothing else).

| run | first state | writing median (12 largest) | states 2,000 / 1,000 / 0 ya |
|---|---|---|---|
| on 560796 | 5,100 ya | 5,340 ya | 75 / 148 / 212 |
| on again 509cb7 | 5,100 ya | 5,340 ya | 75 / 148 / 212 |
| off 5f4b2e | 5,100 ya | 5,438 ya | 90 / 182 / 240 |
| read-out on the on history (560796, live map hidden) | 5,100 ya | - | 95 / 187 / 223 |

The on and off numbers equal round 24's (e65944 / 11a7fe on caa44c4d): the merges since did not touch this path. The same seed
twice gives the same result (560796 = 509cb7 in every number; this is L7, the L6 check is still to do).

**Not the history, not war.** On one history (560796) the read-out seats 95 / 187 / 223 states and the live polities 75 / 148 /
212 (`round25/counts.py`). The live run's history is not what costs the states: the read-out on it is as high as off. Nor is it
consolidation: by 2,000 ya the live run had 25 states conquered against 23 for the read-out on the same history (54 / 55 by 1,000
ya); the live run *founded* fewer (549 states ever by 2,000 ya against 615).

**Where the missing states are** (`round25/missing.py`, 560796): of the read-out's 95 states at 2,000 ya that the live map lacks,
40 are live chiefdoms on the same cell, 20 are inside another live polity; at 1,000 ya 57 and 53. Three causes, measured:

1. **The one-step lag, inherent.** `round25/place_bias.py` on 509cb7: every live seat's place equals the ledger's place on that
   cell **one step earlier** (median ratio 1.00, quartiles 1.00-1.00, at every half-kyr from 3,000 ya to now), and runs 3-5 %
   under the ledger's place at the same step (median 0.95-0.99). town_cells is the ledger, exactly; the seats read it as at the
   end of the last step because the ledger's place at step t is built from the end of step t, which the history has not lived
   yet when its polities act at the start of t. The read-out looks one step ahead. The lag bites hardest on a **frame step**
   (every 0.5 kyr): the ledger takes the new frame's inputs there and its places jump 28 % of the way at once (TAU_KYR 0.3); the
   live seats see that a step later. Over the last 3 kyr (`round25/series.py`) live / read-out-on-the-same-history is **0.89 on
   frame steps and 0.97 between them**, and 2,000 / 1,000 / 0 ya are all frame steps. Of the 40 read-out states that are live
   chiefdoms at 2,000 ya, 36 have a smaller live place (median 0.76 of the ledger's: towns growing through a city's size).
   Not a bug: the live polities cannot see a place before it exists. It makes the three-date comparison read worse than it is.
2. **The confederations still read the history's own places.** Standing confederations live / read-out on the same history:
   4 / 9 (2,000 ya), 11 / 23 (1,000 ya), 17 / 21 (now). Same accounting gap as the seats before the patch (no halls, fishers or
   second peoples' own places). A fix, not yet made: draft `draft-live-confederations-read-history-places.md` (updated).
3. **Step-to-step noise.** States standing swing 20-25 % from one century to the next in every path (off: 93, 90, 103 at
   2,100 / 2,000 / 1,900 ya; live 99, 75, 99): the collapse hazard (FALL_PER_CENTURY 0.46: 37 % of states per century) and
   re-seating. A single date is a poor measure. Averaged over the five steps around each date (2.2-1.8, 1.2-0.8, 0.4-0 kyr ago):
   live 93 / 174 / 214, read-out on the same history 105 / 185 / 218, off 96 / 184 / 233: live is 3 %, 6 % and 8 % under off.

**And a bug found on the way: the live polities never seated a dragon realm.** `LivePolities.__init__` picked the dragons with
`l.trait("flies", 0.0)`, which reads a trait *knob* called "flies" (none exists), so it was always 0 and `self.dragons` empty since
the first cut (2e93efa3). polities_live.json of 560796: 0 dragon realms in any step; the read-out on the same history has 23 / 17 /
17 at 2,000 / 1,000 / 0 ya. Fixed (`polity_live.is_dragon`: 'dragon' in the id and the trait 'flies', as the read-out's
`_Run.dragons`), with a test. Dragon realms take land, so this moves the live state counts too; the on runs above predate it.

## 4. State at hand-off (lane 281b, ~100 tool calls)

- Committed: 8ba3d691 (the patch and the fixture fix; not-slow suite 2009 passed, 15 skipped; lineages / polities / settlements /
  techtree files incl. slow 245 passed). Then the dragon fix with its test (this commit; `tests/test_lineages.py` and
  `tests/test_polities.py` not-slow run on it).
- **Not flipped.** The first state and writing pass on L7 seed 7, but the five pairs are not measured on the final code, the
  dragon fix changes every on run, and the confederations still read the history's places.
- L6 4360a3 seed 7 off on 8ba3d691 (the off path does not import polity_live, so it stands for off on the dragon fix too): run
  fdee9d, first state 2,600 ya, writing median 3,288 ya, states 53 / 214 / 232 (moved from round 23's 4,000 ya with the merges
  since).
- Next, in order: (1) make step 1b read town_cells' places (both slots, summed per holder line, as the read-out sums a people's
  sites); `_places`, `_second_places` and `_site` are then unused in `_step` and go, with the PW-1587 test moved onto town_cells'
  site factor; (2) the five pairs on that code, on and off, measuring states as five-step averages around each date as well as
  the single dates; dragon realms per step on and off; (3) the same seed twice on one L6 pair; (4) the flip.
- Scratch: runs deleted at hand-off.

Scripts: `round25/counts.py` (states, founded, how they ended), `round25/missing.py` (read-out states the live map lacks),
`round25/seat_dump.py` (a live run writing its seats out), `round25/dump_cmp.py`, `round25/place_bias.py` (live seats against the
ledger), `round25/series.py` (states per step).
