> Superseded in part by [round2.md](round2.md) (lane 200b): regions on with the anchor re-set, the floor redefined (off), arm T on.

# Tech tree round 1: stable dates, region learners, trade-weighted town network (PW-1483, PW-1471, PW-1461; lane 200)

## In plain words

- **Stability (PW-1483), done and on.** Each people used to get a fresh random number at every step for every tech. A small nudge
  upstream could make an invention just miss one step and then wait thousands of years for the next lucky one. Now each people
  gets **one** waiting time per tech, drawn once, and invents when its build-up of chances reaches it. A small nudge now moves the
  date a little. The chance of inventing in any one step is unchanged. On run 0141d1 (dnd, world 899985), over 12 draws, a 10% cut
  to every border used to move a people's writing by up to 2,601 years. Now the most it moves is 399 years (section 1).
- **Humans alone (PW-1471, D55): built, measured, switched off.** Two mechanisms are in the code:
  (a) a floor on a people's own inventing, set from Earth's independent inventions of writing (four, fetched), and
  (b) region learners: each continent a people holds is a learner of its own, with its own share of the people.
  On the humans-only world, (b) gives the humans chiefdoms, cities and kingship in 7 of 8 draws (main: 1, 3 and 1 of 8). Writing
  still comes in only 1 of 8, because clay tokens almost never come. But on the dnd world (b) brings the world's first writing to
  8,219 years ago (median of 12 draws). Main gives 4,153 and Earth 5,300. That is too early, so both switches are off until the
  rates are reset for region learners. That reset is a judgement call for Daniel (inbox draft). The floor (a) is off for its own
  reason. With Earth's numbers, the "floor" for writing is faster than the calibrated rate, so it would speed up every big people,
  not only the small ones it is meant for (section 2).
- **D53 (PW-1461): built, off, not yet judged.** Arm T is arm B (writing crosses the taker's towns, not its whole land), weighted by
  the *giver's* trade-mindedness: 1 - insularity, + 0.1 if cosmopolitan. Lane 199 found that is the tree's trade axis
  (attitudes.py). I measured it only with region learners on, and there it changes no writing date (section 3). It needs a
  measure on the plain tree, which is a hand-off.
- **What moves with the switches as they ship (POLITIES_LIVE off).** Only PW-1483. Every tech date of every tree is re-drawn with
  the new waiting times: a new draw of the same odds, not a model change. Nothing else moves: the floor, regions and arm T are off.
  The history is untouched. The tree inside the history (tech_live) and the after-run tree run the same Calendar code. The live tree
  also reads the regions (from the range at the last stored frame) and the dated landmass arrivals, so the two trees stay
  consistent when the switch is turned on.

## 1. PW-1483: one keyed waiting time per (people, tech)

`techtree.Calendar.wait_of`: E = -ln(1 - keyed(seed, "wait", people, tech)), an exponential with mean 1. The people invents in the
step where the hazard summed since it could start (ramp included, the same h as before) reaches E. A tech that arrives by contact
partway through a step can still be invented over the part of the step before it arrived, as before. Inverse-method sampling: the
chance in a step, given none before, is 1 - exp(-h dt), the same as one draw per step.

**Harness** (`round1/sens.py`, `round1/sens_sum.py`; output `round1/sens_0141d1.txt`). Run 0141d1 (stored, read-only). 12 draws
(tree seeds 7002-7013). Two codes, each against its own un-nudged draw: main (main's techtree.py and techtree.toml at 01b03c34) and
this branch (floor and regions off). Two nudges:
- border: every contact's border x 0.9 (fronts a little slower, like round 9's short early borders);
- pop: the population of the draw's first writer x 1.05.

| writing | world's first writing moves: median, max, draws over 1,000 yr | a people's writing moves: median, 90th pct, max | known in one run only |
|---|---|---|---|
| border, main | 0, 1,510, 1/12 | 0, 178, 2,601 | 1 |
| border, branch | 0, 232, 0/12 | 0, 199, 399 | 0 |
| pop, main | 0, 0, 0/12 | 0, 0, 0 | 0 |
| pop, branch | 0, 95, 0/12 | 0, 0, 126 | 0 |

Towns, border nudge: max move 2,441 years on main, 443 on the branch. Cities: 250 against 425, both small. The tail is what
PW-1483 was about, and it is gone. Under the pop nudge main moves nothing at all: a 5% higher hazard rarely flips a per-step draw,
and when it does the jump is large. The branch moves a little, every time, the way a rate change should.

**Spread over the 12 draws** (world's first writing, years ago): main median 4,153 (2,797-4,795); branch 4,562 (2,098-6,625). Both
are draws of the same odds. The branch's range is wider over these 12 draws. Its median is within main's range.

## 2. PW-1471: the floor and the region learners

**Sources.** Writing's independent inventions (en.wikipedia.org/wiki/History_of_writing, fetched 2026-11-05): "Four independent
inventions of writing are most commonly recognized": Mesopotamia c. 3400-3100 BC, Egypt c. 3250 BC, China before c. 1250 BC,
Mesoamerica before c. 1 AD. The Indus script is not counted (undeciphered). In the tree: `origins_kyr = [5.25, 5.25, 3.25, 2.0]`.
The catalogue's tokens and proto-writing origins are marked unverified there, so I did not use them.

**The floor** (`techtree.own_floor`, `[defaults] own_floor`, off). A lone learner that meets a soft tech's conditions invents it no
slower than Earth's median independent inventor did after Earth's prerequisites: RAMP_MEDIAN / (ready - median origin). For
writing: 8.6 - 4.25 = 4.35 kyr median, a floor of 0.336 per kyr. **Why it is off:** the tree's anchor rate for writing is set so that
the first of 4 anchor peoples writes 3.3 kyr after its prerequisites (Earth's lag). With the floor on, `anchor_check` gives 1.86 kyr
(test_anchor_check_meets_earths_lag fails; the bound is 0.6 x 3.3). The two Earth numbers disagree: four learners, each with a
median wait of 4.35 kyr, would find writing much sooner than 3.3 kyr after Mesopotamia's prerequisites. A floor must be below the
anchor's own rate to be a floor. Defined this way it is not, so it is off.

**Region learners** (`techtree.region_shares`, `Calendar.learners`, `[defaults] regions`, off). Each present-day landmass holding at
least 10% of a people's range (presence-weighted; `region_min_share`, a judgement) counts as a learner, from the date the people
reached it (`crossing.Crossings.reached`, saved in meta.lineages). Each region learns on its share of the pool, and the people's
hazard is the sum. Knowledge stays per people: once one region invents a tech, the whole people knows it (draft 2). After the run,
the regions come from the present range (as the goods do). Inside the history they come from the range at the last stored frame.
The landmass labels are `Crossings.label`, and `techtree.landmass_of` rebuilds them for a stored run.

**Humans alone** (world 899985, L7, seed 7, polities off; scratch run c1dd46, humans start 200 kyr ago, 1.4 billion over 145 Mkm2
today; 8 draws, tree seeds 7000-7007; `round1/humans_only_c1dd46.txt`). Baseline: main's tree on the same history and draws.
Lane 192's history (round8.md) was a different run, so its 0/8 is not this baseline.

| humans | main | branch, wait only | + regions |
|---|---|---|---|
| huts | 7/8 | 6/8 | 7/8 |
| villages | 6/8 | 6/8 | 7/8 |
| towns | 5/8 | 3/8 | 7/8 |
| chiefdoms | 1/8 | 1/8 | 7/8 |
| tokens | 1/8 | 0/8 | 2/8 |
| proto-writing, writing | 0/8, 0/8 | 0/8, 0/8 | 1/8, 1/8 |
| cities, kingship | 3/8, 1/8 | 3/8, 0/8 | 7/8, 7/8 |

So with regions the humans alone climb to chiefdoms and cities in most draws. Writing is held up by clay tokens. Tokens need
tallies, pottery and villages, and the tree has no sourced floor for them.

**The dnd world** (run 0141d1, 12 draws; `round1/dnd_0141d1.txt`). Baseline: main on the same run and draws.

| world's first (median of 12, years ago) | main | wait only | + floor | + regions (and floor) |
|---|---|---|---|---|
| writing | 4,153 | 4,562 | 5,246 | 8,219 |
| towns | 7,649 | 6,994 | 6,994 | 9,490 |
| cities | 5,061 | 4,384 | 4,384 | 7,119 |
| kingship | 4,153 | 3,238 | 3,238 | 6,994 |

Region learners move every urban step 2-4 kyr earlier. Writing at 8.2 kyr ago is 3 kyr before Earth's first and outside main's
12-draw range (2,797-4,795), so the ticket's second check fails. The cause is the calibration, not the mechanism. The anchor rates
(`anchor_peers = 4`: Earth's date is the first find among 4 one-learner peoples) were set for one learner per people. A dnd people
on 3-10 continents is now 3-10 learners, each with nearly the whole people's skill strength, because strength goes as ln N.
Switching regions on needs the anchor re-set so that the world's first dates stay Earth-like. That is a needs-decision draft.

## 3. PW-1461 (D53): arm T

`contact_arms` letter T, used with B: for a tech that needs towns, the front's width is (the taker's range width)^(1 - tau) x (its
town network's width)^tau. Tau is the giver's trade-mindedness (`techtree.trade_of`). A trading giver's writing crosses the taker's
towns; an inward one's crosses its whole land, as with the arm off. On 0141d1 with region learners on, B and T change no people's
writing date. Writing is invented so early there that the fronts do not matter. B and T do move cities and kingship from invented
to taken. **Not measured:** T on the plain tree (regions off), the case that matters while regions are off. Hand-off command below.

## 4. Tests

`uv run pytest -q -n 2 -m "not slow" tests/test_techtree.py tests/test_techspread.py tests/test_lineages.py tests/test_settlements.py`:
194 passed. `tests/test_golden.py`: 2 passed. Two tests now search for their first usable draw instead of a fixed seed; their
assertions are unchanged (test_a_nudge_elsewhere_leaves_a_peoples_dates_alone, test_a_live_front_speeds_up_as_the_border_grows_and_never_slows).

## 5. Not done (hand-off)

- Arm T on the plain tree: `measure.py RUN 12 OUT 4 wait,waitB,waitBt` (add the two variants: regions off, B / BT on), on 0141d1
  and a2b637 (a2b637's world, dba204, must be copied into the scratch root for the goods).
- The robustness suite: `uv run python tools/peoples_robust.py run --out <scratch> --family authored --trees humans_only,no_dragons
  --arms now --jobs 2 --threads 4`, then `report`. With POLITIES_LIVE off the tree is built after the history and does not feed it,
  so the suite's people shares cannot move.
- A switch-on (POLITIES_LIVE) run, to check that the live tree and the after-run tree agree with regions on.
