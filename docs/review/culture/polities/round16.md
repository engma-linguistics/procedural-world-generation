# Polities round 16: why the history's states stay small (PW-1583; lane 241)

## In plain words

- **The question.** With polities in the history switched on (`params.POLITIES_LIVE`), the states that fight inside the history
  are fewer and much smaller than the read-out draws with the switch off (round15.md section 3: largest 0.44 Mkm² at its peak on,
  2.28 off, on world 4360a3, L6, seed 7).
- **It is not the peoples.** The same switch-on runs, read by the ledger read-out instead of the live map (the run's
  `polities_live.json` hidden), give states about as big as the switch-off runs: peaks of 2.78 (L6) and 1.56 Mkm² (L7), against
  2.28 and 2.33 switch off. The peoples the switch-on history makes can carry large states. The live polity rules don't let them form.
- **What the large polities are made of.** With the switch off, a polity over about 0.2 Mkm² (one city-state's reach,
  `STATE_MAX_KM` 250 km) only grows in two ways. It holds land it conquered from another polity, or it is a confederation. Only
  two things let a polity reach past 250 km (`WIDE_BY`): holding a province that was a state when taken, or being a confederation.
  The largest polity of a century is one of those in every century of the last 3,000 years of both switch-off runs.
- **What the history lacks.**
  1. **No confederations** (the read-out's step 1b). Switch off, the read-out has 2 (L6) to 8 (L7) confederations a century. At L7
     a confederation is the largest polity in 11 of 31 centuries, and confederations are most of the first states: at L7 the first
     state forms 3,800 years ago on the ledger and 2,600 on the live map, on the same peoples.
  2. **Far fewer conquests, because there are far fewer small polities to conquer.** The read-out takes its seats from the
     settlement ledger, and about 80% of the ledger's town-size seats are a second people's own place (`minority` sites: a hold, a
     quarter), next to the cell's chief town. The history seats only its central places, one per ring at most. So the history has
     ~250-450 chiefdoms a century against ~1,700-4,400. States grow by taking chiefdoms (92 conquests in the history against
     ~1,700 on the ledger, same peoples), and only after that do they meet other states: 1 (L6) and 6 (L7) states or empires
     conquered in the history against 24-41 on the ledger. That is the only other route past 250 km.
- **What was built (behind the switch):** the history now uses the read-out's own rules in three places where it did not before.
  1. It has the read-out's step 1b, so confederations form (candidate A).
  2. A second people's own town is a seat, as the ledger's minority places are (B).
  3. A town is a seat at its people's stage threshold (C).
  There is no new number. Switch off is byte-identical: the read-out's hash is unchanged, and a switch-off run on this branch
  measures exactly as main's.
- **Before and after, switch on, the same three L6 seeds** (largest polity over the last 3,000 years, median / peak, Mkm²):
  - seed 7: 0.21 / 0.44 before, **0.29 / 3.11** now; switch off 0.40 / 2.28.
  - seed 3: 0.42 / 1.03 before, **0.90 / 2.05** now; switch off 1.01 / 1.56.
  - seed 10: 0.44 / 2.89 before, **1.43 / 3.27** now; switch off 1.79 / 3.35.
  The peaks now reach Taagepera's 2.3 Mkm² floor (PW-1456) on two seeds of three, as often as with the switch off. The medians are
  10-28% under the switch-off ones.
- **Not yet as good as off.** There are still fewer states (78-100 now, against 120-203 off). The largest state's median is still a
  little lower. On the one nudge pair measured, the map holds less steady: at the present, 11% of ruled land has the same ruler in
  base and nudge, against 16% off and 21% before this change. So no draft to flip the switch: section 5.

## 1. Evidence (`round16/diag.py`, `round16/seats.py`; read-only)

Runs: L6 world 4360a3 seed 7 (lane 238: f4fb14 on, 6418c8 off); L7 world 899985 seed 7 (lane 234: 746ed2 on, 0a1c30 off).
"on, ledger" is the switch-on run read by `polities.derive` with its `polities_live.json` hidden (a mirror folder without it), i.e.
the read-out's rules on the switch-on history's peoples. All figures are over the last 3,000 years unless named.

| run | source | first state | largest: median / peak (Mkm²) | largest is (centuries) | states, median | confederations, median | conquests | states or empires conquered |
|---|---|---|---|---|---|---|---|---|
| L6 on | live | 2,500 ya | 0.21 / 0.44 | plain 12, with provinces 14 | 50 | 0 | 93 | 1 |
| L6 on | ledger | 2,500 ya | 0.32 / 2.78 | provinces 20, confed 5, plain 1 | 89 | 1 | 1,654 | 24 |
| L6 off | ledger | 2,800 ya | 0.40 / 2.28 | provinces 22, confed 7 | 99 | 2 | 1,766 | 36 |
| L7 on | live | 2,600 ya | 0.18 / 0.64 | plain 27 | 51 | 0 | 92 | 6 |
| L7 on | ledger | 3,800 ya | 0.42 / 1.56 | provinces 19, confed 12 | 54 | 7 | 1,886 | 41 |
| L7 off | ledger | 4,100 ya | 0.46 / 2.33 | provinces 20, confed 11 | 68 | 8 | 1,798 | 39 |

("plain": a state with no provinces and no confederation, so inside one city-state's reach; "provinces": it holds land it took by war.
The largest plain state is 0.18-0.22 Mkm² in every source: that is `STATE_MAX_KM`'s 250 km disc on this land.)

Chiefdoms a century (L6, 1,000 years ago): 231 live, 2,153 on the ledger for the same run. The ledger's town-size seat cells on the
switch-on run (`seats.py`): 2,854 at 1,000 years ago, of which 510 are chief places and 2,344 are minority places; 2,191 of them have a
bigger seat in their own ring, so the history's one-per-ring central places cannot stand for them.

Reading:
- The switch-on peoples are not the cause: their ledger read-out is within the switch-off spread (median 0.32 vs 0.40 at L6, 0.42 vs
  0.46 at L7). The first state at L6 is 2,500 years ago on both the live map and the ledger of the switch-on run. So the L6 gap in
  the first state (2,500 vs 2,800) is the peoples', and the L7 gap (2,600 vs 3,800) is the live rules'.
- Growth stops at one city-state's reach. In the live history the largest polity is a plain state in 12 of 26 centuries with a
  state (L6) and 27 of 27 (L7), and plain states never pass ~0.22 Mkm². The 0.44 and 0.64 peaks are one-off conquests that
  last a century.
- The two ways past 250 km are almost absent from the live history: no confederations, and 1 or 6 conquered states against 24-41.

## 2. Candidate mechanisms

A. **Confederations in the history.** This is the read-out's step 1b: Turchin 2009's mirror empires, already sourced and ruled in
   the read-out (PW-785, PW-1449). It uses the same rule on the history's own places: each cell's central place, held by the cell's
   lead people. That place is a village of SHARE[1] of the cell's own settled heads, or a town or city where `_places` seats one.
   Confederations bring the stacked reach (WIDE_BY "confederation") and the early frontier states. They also bring more borders
   between states, so more conquests of states (the other WIDE_BY route) follow from the dynamics, not from a number.
B. **A second people's own place as a seat.** The ledger's minority places (a second people's own town beside the cell's chief
   place) are most of its chiefdoms, and so most of what states conquer. The history now sizes one per cell the way the ledger
   does. That is MINORITY_SHARE of the second people's settled heads, saturating toward MINORITY_MAX, where it is SECOND_MIN of the
   cell's heads and not the lead people's kin. The seat goes to the bigger of the two places on the cell, as derive's "biggest town
   per cell". The ledger's site factor, harbours, holds and five-step wait are not modelled (`_places` lacks them too).
C. **The town threshold by stage.** The history seated a town at 2,000 people (`TOWN_MIN[-1]`, the roads-and-cities stage) for
   every people. The ledger, and the history's own `town_cells`, use the people's stage instead (1,000 before roads). B needs C:
   a second people's place saturates under 2,000, so under the old threshold it could never seat a town.

Not candidates: raising `STATE_MAX_KM`, `WAR_P` or the reach for live polities only. Those would chase the number, and the read-out
gets its size with the same values.

Arms measured on seed 7 (L6): A alone gives median 0.22 and peak 1.83. B alone gives 0.22 / 1.88, because nothing changes without C.
C with A gives 0.22 / 1.83, adding a few chief towns. A, B and C together give 0.29 / 3.11, and 846 conquests against 93 before.
All three are built.

## 3. What was built

- `polity_live.LivePolities._confederations` (step 1b, after the town seats) is the read-out's `polities._confederations` rule,
  read on the history's places. `PO._reach` and `PO._claim` are shared, and so are `CONFED`, `CONFED_HEADS_X`, `CONFED_TRY`,
  `CONFED_AGAINST`, `HOLD`, `INCUMBENT` and `STATE_WRITING`. A confederation keeps the stacked reach (`wide`, as derive). Its
  record carries `confed` ([kyr ago, heads]), and `_from_live` copies it to the card. The viewer's "confederation" row then shows
  it as in the read-out (`_LIVE_READ` 2).
- `_second_places` (B) reads settlements' CONST (SECOND_MIN, MINORITY_SHARE, MINORITY_MAX), as `_places` reads SHARE.
- The seat's town threshold is `TOWN_MIN[stage]`, through `_stage`, which `town_cells` now shares (C).
- A latent bug, fixed. When one people was cut by two conquests in the same century, the second expulsion could send refugees
  onto a cell the first had emptied. That gave NaN heads, and the run crashed on seed 3 once conquests were frequent. Now the cut
  zeroes those heads, and `_refuge` only uses cells the people still holds.
- Daniel's D56, D59, D61 and D67 are untouched: the fates, submission, the risings and REVOLT read the same seats as before,
  now including confederations and second peoples' towns.
- Tests: `uv run pytest -n 2 -m 'not slow' tests/test_lineages.py tests/test_polities.py tests/test_golden.py`: 167 passed, goldens
  unchanged. New: `tests/test_lineages.py::test_live_confederation_bands_a_peoples_villages_beside_a_foreign_state` and
  `::test_live_refugees_skip_land_their_people_has_already_left` (it fails without the fix).

## 4. On and off, the same seeds (L6 world 4360a3, dnd, 30 kyr; `round14/measure.py`, `round16/diag.py`)

Languages were skipped in these runs: they come after the polities and do not feed them. Switch off: the read-out. Switch on: the
live map, which is what the read-out draws.

| seed | run | first state | states 2,000 / 1,000 / 0 ya | largest, last 3 kyr: median / peak (Mkm²) | centuries >= 2.3 | most > 1 Mkm² | conquests (run) |
|---|---|---|---|---|---|---|---|
| 7 | off (6418c8; this branch 6e880f, the same) | 2,800 ya | 66 / 116 / 120 | 0.40 / 2.28 | 0/31 | 4 | 1,766 |
| 7 | on, main (f4fb14) | 2,500 ya | 40 / 57 / 68 | 0.21 / 0.44 | 0/31 | 0 | 93 |
| 7 | on, A only (ae810f) | 2,500 ya | 40 / 57 / 69 | 0.22 / 1.83 | 0/31 | 2 | 93 |
| 7 | **on, this branch** (02a90b) | 2,500 ya | 43 / 68 / 78 | 0.29 / 3.11 | 3/31 | 3 | 846 |
| 3 | off (14ae84) | 7,100 ya | 129 / 145 / 134 | 1.01 / 1.56 | 0/31 | 3 | 3,388 |
| 3 | on, main (b6aaf6) | 6,600 ya | 88 / 92 / 92 | 0.42 / 1.03 | 0/31 | 1 | |
| 3 | on, A only (d4b7df) | 6,600 ya | 89 / 92 / 100 | 0.83 / 1.63 | 0/31 | 2 | 345 |
| 3 | **on, this branch** (dbd75c) | 6,600 ya | 98 / 94 / 100 | 0.90 / 2.05 | 0/31 | 2 | 1,920 |
| 10 | off (4c6c89) | 5,500 ya | 144 / 197 / 203 | 1.79 / 3.35 | 4/31 | 9 | 2,325 |
| 10 | on, main (37467e) | 5,300 ya | 68 / 68 / 79 | 0.44 / 2.89 | 1/31 | 2 | |
| 10 | on, A only (b200cf) | 5,300 ya | 80 / 77 / 88 | 0.95 / 2.37 | 1/31 | 7 | 292 |
| 10 | **on, this branch** (0119b9) | 5,300 ya | 84 / 89 / 100 | 1.43 / 3.27 | 6/31 | 8 | 1,404 |

The "this branch" runs were made with the three parts behind lane flags. The committed code, with no flags, remade seed 7 (15f636):
every measure is the same, and the live file differs only in its timing field. On this branch with the switch on, the largest polity is a confederation in 13 (seed 7), 26 (seed 3) and 25 (seed 10) of 31
centuries. The first state is the same on and off within each run's peoples; the 300-500 year gap is the peoples' (section 1).
Writing is unchanged (11/12 or 12/12 of the largest peoples).

**Steadiness under a nudge** (PW-1460's measure, round14/measure.py `--pair`; the nudge is halflings among humans, wish weight
0.8 -> 0.9, seed 7). "Top 10 kept" is base in nudge, then nudge in base. "Same ruler" is the share of ruled land with the same
ruling people in both.

| | 1,000 ya: top 10 kept / same ruler | now: top 10 kept / same ruler |
|---|---|---|
| L6 off (6418c8 vs 863ee2) | 6/10, 2/10 / 19% | 3/10, 4/10 / 16% |
| L6 on, main (f4fb14 vs 27a117) | 3/10, 2/10 / 19% | 4/10, 5/10 / 21% |
| L6 on, A only (ae810f vs 6ca9c2) | 3/10, 2/10 / 19% | 3/10, 0/10 / 13% |
| L6 on, this branch (02a90b vs 1dbb64) | 3/10, 1/10 / 16% | 4/10, 0/10 / 11% |
| L7 on, main (lane 234: 746ed2 vs f5e523) | 5/10, 4/10 / 21% | 1/10, 0/10 / 14% |
| L7 off (lane 234: 0a1c30 vs 19e53f) | 6/10, 4/10 / 19% | 1/10, 2/10 / 20% |

The bigger polities make the live map less steady under this nudge: one pair, one seed, a few points. Larger polities make "same
ruler" swing more, because one empire more or less moves a large share of the ruled land. Not judged on one pair.

L7 (lane 234's world 899985, before this branch; round14.md sections 2-4, and `round16/measure_v1.py` for their /1 live files):
- seed 7: on 0.18 / 0.64 Mkm², first state 2,600 ya, 85 states now; off 0.46 / 2.33, 4,100 ya, 122.
- seed 10: on 0.71 / 1.66, 4,100 ya, 116; off 1.12 / 1.58, 4,600 ya, 177.
L7 seed 7 on this branch, switch on (16b49e; nudge 2b7069; landed after the handoff), against lane 234's switch-off 0a1c30 / 19e53f:
- first state 3,300 ya, against 4,100 off (2,600 on main);
- states 2,000 / 1,000 / 0 ya: 89 / 121 / 148, against 50 / 89 / 122 off;
- largest: median 0.77 / peak 1.23 Mkm², against 0.46 / 2.33 off (0.18 / 0.64 on main); 0/31 centuries at 2.3, against 1/31.
- Nudge, now: top 10 kept 1/10, 3/10, same ruler 19%. Off: 1/10, 2/10, 20%. On main: 1/10, 0/10, 14%.

At L7, then, switch-on is as good as off or better on states, the median and steadiness, and lower on the peak. It is one seed.

Nudge caveat (lane 234): the nudged tree is loaded by file path, and the humans' share moved much more than round 6's nudge moved it
(40% to 23% at L7). In `planet/lineages`, the tree's name is used only for labels (output.py: the run's name, `tree_name`, the
report header), so the path load changes no rule. A bigger nudge still makes every steadiness number here lower, on and off alike.

## 5. Where this leaves the switch

- Against the ticket's second box ("with the switch on, the largest polity over the last 3 kyr is within the spread of the
  switch-off read-out on the same seeds"):
  - the peaks are within it (2.05-3.27 against 1.56-3.35);
  - the medians are close but under it on every seed (0.29 / 0.90 / 1.43 against 0.40 / 1.01 / 1.79).
- Still short with the switch on, against off:
  - **states:** about half as many on seed 10, and 60-75% on seeds 7 and 3. The read-out's sites keep a city's people for a
    while after its cell stops being the best of its rings (the ledger's growth lag and slow decline). The history's central
    places are recomputed every century, with only HOLD to keep an incumbent. So the history has fewer cities at any one time.
  - **steadiness under the nudge:** lower on the one pair.
- So this lane does not file the flip. A draft carries the L7 check and the remaining gap (states, steadiness).
