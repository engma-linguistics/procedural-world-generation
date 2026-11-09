# Polities round 18: the state test in the history (PW-1594; lane 248)

## In plain words

- **What was wrong.** With polities in the history (the switch `POLITIES_LIVE`), a seat could become a state only if its place
  was a *city* in the ledger's sense, the best cell of two rings around it. The read-out (switch off) lets any town or city whose
  people reach a city's size, less how hemmed in it is, be a state; a hemmed-in town (best of one ring, up to 9,999 people) can
  qualify there. The history also read "hemmed in" as one number for the whole people's border, which goes up as foreign states
  border it; the read-out reads the seat's own two rings.
- **What was built (behind the switch):** the history now tests a seat for a state on its place whichever its tier, with the town
  capped under a city's size as the ledger caps it, and reads "hemmed in" over the seat's own two rings with the read-out's rule
  (`polities._hemmed`): sea for a people without boats, ice and peaks of 3,000 m or more bar fully; land only other peoples hold bars
  SOCIAL_Q. No new number. Switch off is untouched (LivePolities is not made).
- **What it does (all on this code, on and off alike; section 2).** States now, switch on as a share of switch off: L6 seeds
  7 / 3 / 10: 95% / 105% / 80%; L7 seeds 7 / 10: 99% / 103%. Before, on the same code: L6 seed 7 67% (lane 245's other seeds 58-77%,
  L7 126-141%).
- **Which candidate mattered (section 1, L6 seed 7, one change at a time):** the state test on any tier (alone it overshoots:
  290 states now against 174 off, because the people-wide hemmed-in is high); the seat's own hemmed-in (alone it moves nothing: 113
  against 116); both together give 165. Seats keyed by cell (candidate 1): keeping a seat's key when its best cell moves one ring
  changes neither the count (165) nor the steadiness. Giving the places the ledger's whole lifecycle (founding, growth lag,
  abandonment) gave fewer states (134) and later writing; not kept.
- **Steadiness under the nudge** (halflings among humans 0.8 -> 0.9): share of ruled land with the same ruler 1,000 years ago /
  now, on against off: seed 7 24% / 23% against 27% / 27% (16% now before the change, lane 245's pair); seed 3 34% / 31% against
  30% / 36%. At 1,000 years it is mixed (3 under, 4 over); now, on is 4-5 points under off on both seeds (it was 11 under on
  seed 7). On seed 10 the nudge changes nothing at all (switch on, the base and nudged runs are identical), so it measures nothing.
- **The live calendar still runs late** (candidate 3): the first state comes 400-800 years later than off on 3 of 5 pairs (and
  100-300 years earlier on the other two), writing's median 160-380 years later on 4 of 5 (the same on the fifth). It moves *when*
  states start, not how many there are now. Draft: `draft-live-tech-calendar-runs-late.md`.
- **Ready to flip?** States match within reason at both levels; steadiness is mixed at 1,000 years and a little under off now.
  Draft `draft-flip-polities-live-on.md` (needs-decision) puts the numbers to Daniel; the switch is not flipped here.

## 1. Which candidate moves the state count (L6 world 4360a3, seed 7)

`round18/live_run.py`, dnd, 30 kyr, languages skipped; `round16/measure_v1.py`. The arms are the diagnosis switches in
`round18/diag.patch` (on 4fccab70, each off the code as before); the off run and the base on run reproduce lane 245's own numbers
exactly (147 / 166 / 174 and 84 / 97 / 116), so main has not moved these since.

| run | first state | states 2,000 / 1,000 / 0 ya | largest, last 3 kyr: median / peak (Mkm²) | writing median |
|---|---|---|---|---|
| off (9c2a54) | 3,700 ya | 147 / 166 / 174 | 0.76 / 2.02 | 3,347 ya |
| on, as main (d5565c) | 3,300 ya | 84 / 97 / 116 | 0.72 / 3.11 | 3,005 ya |
| on, state test on any tier (8d99ec) | 3,300 ya | 239 / 247 / 290 | 0.88 / 2.94 | 3,005 ya |
| on, the seat's own hemmed-in (91e36d) | 3,300 ya | 83 / 92 / 113 | 0.72 / 3.11 | 3,005 ya |
| on, both (ccf353; = this change, 3f16ac, maps byte-identical) | 3,300 ya | 120 / 141 / 165 | 0.98 / 2.49 | 3,005 ya |
| on, both + the ledger's lifecycle for places (6e83e6) | 3,200 ya | 102 / 129 / 134 | 0.41 / 3.41 | 2,798 ya |
| on, this change + seat keeps its key one ring away (74ca3d) | 3,300 ya | 123 / 140 / 165 | 0.72 / 2.68 | 3,005 ya |

Reading: the state test was the cause, in two parts that pull opposite ways. Testing only the best cell of two rings made too few
states; testing every town against the people-wide hemmed-in makes far too many, because that number is high (it counts the whole
border, and a foreign state across it bars fully, `LivePolities.circumscribed`). Read as the read-out reads it, per seat over its
own two rings, a town in its people's heartland is not hemmed in and only a crowded one passes. Why L6 and L7 used to go opposite
ways was not isolated; both now land near off.

The ledger's lifecycle (`_ledger` in diag.patch: places founded at FOUND for FOUND_STEPS, growing with TAU_KYR, abandoned under
ABANDON) cost states and moved writing 200 years later (the new towns grow slowly, so the town footprint the tech tree reads is
smaller). The seat-move arm (a key passes to a place one ring away of the same people, when the old cell has no place) changed
nothing measurable: the cell keys were not what made the map unsteady.

## 2. On and off on the same code (this change, 9dc89be2; off runs on 4fccab70 + the diagnosis switches, all off: off never makes LivePolities)

| world, seed | run | first state | states 2,000 / 1,000 / 0 ya | on / off now | largest, last 3 kyr: median / peak (Mkm²) | writing median |
|---|---|---|---|---|---|---|
| L6 4360a3, 7 | off (9c2a54) | 3,700 ya | 147 / 166 / 174 | | 0.76 / 2.02 | 3,347 ya |
| | on (3f16ac) | 3,300 ya | 120 / 141 / 165 | 95% | 0.98 / 2.49 | 3,005 ya |
| L6, 3 | off (6dbd43) | 6,300 ya | 146 / 168 / 187 | | 1.95 / 3.32 | 5,738 ya |
| | on (33f4ea) | 6,600 ya | 181 / 182 / 196 | 105% | 1.74 / 3.72 | 5,738 ya |
| L6, 10 | off (a31ba2) | 5,300 ya | 139 / 162 / 213 | | 2.32 / 5.24 | 4,625 ya |
| | on (13c632) | 4,900 ya | 134 / 143 / 170 | 80% | 2.18 / 5.63 | 4,462 ya |
| L7 899985, 7 | off (251461) | 4,100 ya | 108 / 153 / 193 | | 1.08 / 1.87 | 4,462 ya |
| | on (c9c32f) | 3,300 ya | 119 / 168 / 191 | 99% | 0.81 / 2.02 | 4,079 ya |
| L7, 10 | off (2c10cc) | 4,500 ya | 70 / 105 / 146 | | 0.91 / 4.04 | 4,795 ya |
| | on (7add81) | 4,600 ya | 45 / 107 / 150 | 103% | 0.74 / 3.02 | 4,544 ya |

(c9c32f was made with the two switches on rather than as the code: on L6 seed 7 the same arm, ccf353, and this change, 3f16ac,
wrote byte-identical maps; only the timings differ.) The peoples' shares on and off are within 0.5 points of each other on every
pair here (the measure's "shares now" line).

**Steadiness under the nudge** (PW-1460's measure, `round14/measure.py --pair`; live map for on):

| pair | 1,000 ya: top 10 kept / same ruler | now: top 10 kept / same ruler |
|---|---|---|
| seed 7 off (9c2a54 vs 8340ec) | 4/10, 4/10 / 27% | 7/10, 4/10 / 27% |
| seed 7 on, this change (3f16ac vs b740a8) | 3/10, 5/10 / 24% | 5/10, 1/10 / 23% |
| seed 7 on, + seat keeps its key (74ca3d vs 24826c) | 4/10, 4/10 / 24% | 2/10, 2/10 / 20% |
| seed 7 on, before (lane 245, 489391 vs b50f2c) | 1/10, 5/10 / 22% | 1/10, 1/10 / 16% |
| seed 3 off (6dbd43 vs 035142) | 5/10, 5/10 / 30% | 6/10, 7/10 / 36% |
| seed 3 on, this change (33f4ea vs c0458e) | 6/10, 5/10 / 34% | 5/10, 5/10 / 31% |
| seed 10 on, this change (13c632 vs ce7a50) | identical runs: the nudge changes nothing on this seed (off not run) | |

## 3. What is left

- **The calendar** (candidate 3): first state later on 3 of 5 pairs (by 400-800 years), writing's median later on 4 of 5 (by
  160-380 years).
  Not what sets the count now. A likely part, not tested: the town footprint the live tree reads (D52's town arms) counts only the
  live seats' best-of-ring places of the lead people, while the read-out's counts every ledger site of town size, minority places
  and towns still shrinking included (`techspread.town_footprint`). Draft `draft-live-tech-calendar-runs-late.md`.
- **Steadiness now** is 4-5 points under off on both measured seeds; at 1,000 years it is mixed. The nudge pairs are one pair per
  seed; whether 4-5 points is more than one pair swings was not measured (re-rolled draws would tell).
- The lane 77 stress suite was not run: it measures the peoples' shares, which this change cannot move with the switch off (the
  default), and the switch-on shares match off within 0.5 points on all five pairs here.

Runs (scratch, deleted after the lane): `scratchpad/l248/data`; runner `round18/live_run.py`; arms `round18/diag.patch`.
