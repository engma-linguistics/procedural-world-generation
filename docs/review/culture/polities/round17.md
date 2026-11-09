# Polities round 17: the humans' share at L7, and the site factor in the history (PW-1587; lane 245)

## In plain words

- **The humans' jump at L7 is not the switch.** Round 16 compared lane 241's switch-on run (code 24f33270) with lane 234's
  switch-off run (code 5723d08c). Between those two commits, PW-1558 (lane 233, 12f38974: an empty stem holds out by its last
  land) changed the deep history. On world 899985 it already moves the humans from 9% to 26% of all people 38,000 years ago, long
  before any polity. Re-run with the switch off on today's main, the same seed gives humans 66.0% now; with the switch on, 65.5%.
  On seed 10, 56.4% off and 56.9% on. **On the same code the switch moves no people's share by more than about half a point at
  L7, and 1.3 points at L6 (section 1).** Whether humans at over half of all people at L7 is right is a question about
  PW-1558's peoples, not about the polities: draft `draft-l7-humans-over-half-after-pw1558.md`.
- **The same mix-up hid the L7 state count.** Lane 241 read "more states on than off at L7" (148 against 122). Against today's
  switch-off run the off side has 193 states now, so on still had fewer at L7 too.
- **And at L6 the switch-off side moved too.** PW-820 (4389d72a: river water thresholds in m3/s) raises the L6 peoples by about
  half (936 to 1,431 million now, seed 7). Every L6 comparison below is on today's main, on and off alike.
- **Why the history had fewer states: it had no site factor (not memory).** The ticket's guess was that the ledger's towns keep
  their people for a while (growth lag, slow decline) and the history's central places do not. Re-making the switch-off run's
  ledger without that memory gives *more* states, not fewer (120 to 133 now, seed 7, code 24f33270). Re-making it without the
  ledger's site factor (harbour, navigable river, fresh water, fertile ground, pass: `settlements._site_factor`, 0.6-2.0) drops
  them from 120 to 74, about the history's 78 (section 2). The history's central places were sized on the bare hinterland.
- **What was built (behind the switch):** the history's central places now use the ledger's own site factor, on the world's own
  site layers, for the size and for which cell is the best of its ring, as the ledger does; the second people's place and the
  confederations' villages too. No new number. Switch off is untouched (LivePolities is not made).
- **What it does (today's main; section 3).** With the switch on, the states now:
  - **L6** (world 4360a3, seeds 7 / 3 / 10, now): 116 / 144 / 123, against 174 / 187 / 213 off. That is 58-77% of off, from
    about 50-75% before (lane 241's runs, older code).
  - **L7** (world 899985, seeds 7 / 10, now): 243 / 206, against 193 / 146 off and 148 / 114 on before the change. L7 now
    overshoots, by 26-41%.
  - **The largest polity** (median over the last 3,000 years): L6 0.72 / 1.81 / 2.05 against 0.76 / 1.95 / 2.32 off; L7 0.88 / 1.02
    against 1.08 / 0.91. The medians are now close on every seed; the peaks stay under off on four seeds of five.
  - **Peoples' shares:** within 1.3 points of off for every people on all five pairs.
- **Still not ready to flip.** The state count is under off at L6 and over it at L7. The map is also less steady under the nudge
  (L6 seed 7: 22% / 16% of ruled land with the same ruler, 1,000 years ago / now, against 27% / 27% off). So there is no flip draft;
  the remaining gap is a draft that says what was ruled out.

## 1. Peoples' shares, on and off on the same code

(`round17/shares.py`: each people's share of all people now, from the run's tracks; the largest few peoples.)

| pair | humans | 2nd | 3rd | 4th | all people (M) |
|---|---|---|---|---|---|
| L7 s7, lane 234 off (5723d08c, 0a1c30) | 39.8 | hobgoblin 13.6 | halfling 8.8 | orc 8.5 | 886 |
| L7 s7, lane 241 on (24f33270, 16b49e) | 65.5 | orc 13.4 | kenku 9.2 | elf 3.3 | 1,077 |
| L7 s7, off, today's main (7bf29c) | **66.0** | orc 13.3 | kenku 9.1 | elf 3.3 | 1,116 |
| L7 s7, on, this change (4d3e0a) | 65.5 | orc 13.4 | kenku 9.3 | elf 3.3 | 1,080 |
| L7 s10, off, today's main (b08650) | 56.4 | hobgoblin 19.0 | elf 6.1 | dragonborn 4.9 | 824 |
| L7 s10, on, main (495cda) | 56.9 | hobgoblin 18.5 | elf 5.9 | dragonborn 5.0 | 807 |
| L7 s10, on, this change (92ff72) | 56.9 | hobgoblin 18.9 | elf 5.8 | dragonborn 5.0 | 815 |
| L6 s7, off / on this change (38b40b / 489391) | 32.8 / 32.7 | hobgoblin 21.2 / 20.9 | kenku 9.2 / 9.1 | orc 8.4 / 8.5 | 1,431 / 1,402 |
| L6 s3, off / on (d60e31 / a8bae4) | 27.5 / 27.4 | hobgoblin 22.3 / 22.4 | tabaxi 15.5 / 15.5 | leonin 9.1 / 9.1 | 1,248 / 1,226 |
| L6 s10, off / on (dc21ac / 219933) | 23.2 / 24.5 | hobgoblin 18.6 / 18.2 | tabaxi 9.2 / 9.0 | orc 8.9 / 8.7 | 1,415 / 1,429 |

Humans' share over time, L7 seed 7 (tracks): lane 234's off run 9% 38 kyr ago, 26% 5 kyr ago, 40% now; lane 241's on run (and
today's off run) 26% 38 kyr ago, 72% 5 kyr ago, 65-66% now. Lane 241's on run and today's off run have the same 267 M people and the
same shares 5,000 years ago. The only commit touching the history's deep steps between the two codes is 12f38974 (PW-1558;
dispersal.py, origins.py, model.py, params.py). The switch costs 1-3% of all people (not chased).

## 2. What the ledger's parts are worth (`round17/decomp.py`)

A switch-off run's settlement ledger re-made with one ledger constant changed (`settlements.derive(run, **over)`), in a mirror folder,
then `polities.derive`. States 2,000 / 1,000 / 0 years ago; city sites (10,000 people or more) at the same dates.

| run (L6 seed 7, off) | ledger | states | city sites | largest median / peak (Mkm²) |
|---|---|---|---|---|
| 6e880f (24f33270) | as is | 66 / 116 / 120 | 133 / 172 / 177 | 0.40 / 2.28 |
| | no memory (TAU_KYR 0.0001) | 75 / 129 / 133 | 136 / 186 / 190 | 0.40 / 3.00 |
| | no site factor (SITE_MIN = SITE_MAX = 1) | 48 / 66 / 74 | 49 / 103 / 115 | 0.30 / 3.00 |
| | no fishers (FISHER_SHARE 0) | 73 / 117 / 124 | 136 / 173 / 183 | 0.40 / 2.28 |
| | none of the three | 52 / 73 / 84 | 59 / 114 / 120 | 0.34 / 1.89 |
| 38b40b (today's main) | as is | 147 / 166 / 174 | | 0.76 / 2.02 |
| | no site factor | 95 / 110 / 136 | 139 / 167 / 165 | 0.85 / 2.37 |
| | as the history now sizes places (no memory, no fishers, site factor) | 166 / 183 / 191 | 255 / 238 / 273 | 0.81 / 1.79 |

Reading: the site factor is the one part of the ledger the history lacked that carries the state count. A ledger sized the way the
history now sizes its places gives as many states as the ledger itself, or more. So what still separates on from off after this
change is not the size of the places but what the history does with them (section 4).

## 3. On and off after the change (`round16/measure_v1.py`; dnd, 30 kyr, languages skipped)

Switch off: the read-out. Switch on: the live map (the read-out draws it). "on, main" is the switch on without this change.

| world, seed | run | first state | states 2,000 / 1,000 / 0 ya | largest, last 3 kyr: median / peak (Mkm²) | centuries >= 2.3 |
|---|---|---|---|---|---|
| L6 4360a3, 7 | off (38b40b) | 3,700 ya | 147 / 166 / 174 | 0.76 / 2.02 | 0/31 |
| | on, this change (489391) | 3,300 ya | 84 / 97 / 116 | 0.72 / 3.11 | 4/31 |
| L6, 3 | off (d60e31) | 6,300 ya | 146 / 168 / 187 | 1.95 / 3.32 | 9/31 |
| | on, this change (a8bae4) | 6,600 ya | 133 / 144 / 144 | 1.81 / 2.89 | 5/31 |
| L6, 10 | off (dc21ac) | 5,300 ya | 139 / 162 / 213 | 2.32 / 5.24 | 16/31 |
| | on, this change (219933) | 4,900 ya | 107 / 109 / 123 | 2.05 / 3.05 | 10/31 |
| L7 899985, 7 | off (7bf29c) | 4,100 ya | 108 / 153 / 193 | 1.08 / 1.87 | 0/31 |
| | on, main (lane 241's 16b49e) | 3,300 ya | 89 / 121 / 148 | 0.77 / 1.23 | 0/31 |
| | on, this change (4d3e0a) | 3,300 ya | 176 / 208 / 243 | 0.88 / 1.59 | 0/31 |
| L7, 10 | off (b08650) | 4,500 ya | 70 / 105 / 146 | 0.91 / 4.04 | 4/31 |
| | on, main (495cda) | 4,600 ya | 22 / 61 / 114 | 0.72 / 2.03 | 0/31 |
| | on, this change (92ff72) | 4,600 ya | 90 / 178 / 206 | 1.02 / 2.89 | 3/31 |

(16b49e is lane 241's code; the only change since, PW-820, is built to keep the L7 thresholds where they were, and 16b49e has the
same people as today's off run 5,000 years ago.) The L6 "on, main" runs on today's code were not made (the machine ran at load
45-80 from other sessions); lane 241's L6 on runs (older code, before PW-820) had 78 / 100 / 100 states now against 120 / 134 / 203 off
on that code.

**Steadiness under the nudge** (halflings among humans 0.8 -> 0.9, L6 seed 7, `--pair`; live map for on):

| pair | 1,000 ya: top 10 kept / same ruler | now: top 10 kept / same ruler |
|---|---|---|
| off, today's main (38b40b vs 1d1592) | 4/10, 4/10 / 27% | 7/10, 4/10 / 27% |
| on, this change (489391 vs b50f2c) | 1/10, 5/10 / 22% | 1/10, 1/10 / 16% |
| on, lane 241 (older code; round16) | 3/10, 1/10 / 16% | 4/10, 0/10 / 11% |

## 4. What is left

- **States:** under off at L6 (58-77%), over it at L7 (126-141%). The places are no longer the cause: a ledger sized as the
  history now sizes its places gives about as many states as off (section 2). So the gap is in what the history does with its
  places. Candidates not tested here: the live tech calendar runs late (the first state 400 years later on L6 seed 7, writing
  median 3,005 against 3,347 ya; round 14 found the live calendar about 170 years late); the history's hemmed-in term is the
  people's whole border (`StandIns.hem`), while the read-out's is the seat's own two rings (`polities._hemmed`); and seats are keyed
  by cell, so a seat whose best cell moves one ring starts over, without its incumbency. Why L6 and L7 go opposite ways is open.
- **Steadiness:** worse than off on the one pair (16% against 27% now). Not judged on one pair, but it is the larger miss.
- Draft: `draft-live-polities-states-and-steadiness-after-site-factor.md`.

Runs (scratch, gone after the lane): `scratchpad/l245/data` (L6) and `scratchpad/l245/data7` (L7); runner `round17/live_run.py`.
