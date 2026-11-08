# Tech tree round 2: region learners on, the anchor re-set for them, D55's floor redefined, arm T judged (PW-1471, PW-1461; lane 200b)

Follows [round1.md](round1.md) (lane 200). The baseline in every comparison is **main's tree** (main's techtree.py and techtree.toml at
01b03c34) built over the **same stored history** and the **same draws of the tree's luck**. Earth's date for first writing is ~5,300
years ago (the tree's `earliest_kyr = 5.3`).

## In plain words

- **Each region of a people now learns on its own (D55), and this is on.** A region is a people's part of a landmass. A big part is
  cut into pieces of at most 24 Mkm2, so a people spread over a continent counts as several learners, not one.
- **The invention rates are re-set for that.** Earth's first dates are now read as the first find among **24** regional learners.
  Round 1 used 4 peoples. The 24 comes from Earth's count of independent centres of farming: "at least 11" (Larson et al. 2014) and
  "perhaps more than 20" (Fuller et al. 2014), both fetched. Each learner is now slower, and a world with many learners still finds
  things sooner than a world with few.
- **The dnd worlds' first writing is back within main's range.** Medians of 12 draws:
  - run 0141d1: **4,716** years ago (main 4,153, main's range 2,797-4,795);
  - run a2b637: **4,006** (main 3,796, range 2,175-5,738).

  Region learners with round 1's rates gave 7,514 on 0141d1.
- **The humans alone now climb on their own, without being forced** (humans-only world, 8 draws; main's tree on the same history in
  brackets):
  - chiefdoms in 8 of 8 draws (main 1);
  - cities 6 (main 3);
  - kingship 6 (main 1);
  - writing 3 (main 0).
- **D55's floor is redefined and stays off.** It now lifts only regions slower than the anchor learner, so it can never speed up a
  people as big as the anchor (the anchor test passes unchanged). But the humans alone are bigger than the anchor, so it does
  nothing for them. Meanwhile it lifts nearly every small dnd region and brings the dnd worlds' first writing ~1.5 kyr early. It is
  a needs-decision draft (lean: keep it off).
- **Arm T (D53) does something useful, so it is on.** Writing now crosses a people's towns more as the people giving it is
  trade-minded. The median wait from the world's first writing to each people that takes it by contact:
  - 0141d1: 1,221 years with no arm, 953 with T;
  - a2b637: 1,001 with no arm, 665 with T.

  Arm B on its own (every giver treated as a trader) gives 608 and 409. T sits between the two, set by culture, as D53 asked.
- **Checks.** Seven Meals (07c755, measured only): first writing 5,152 years ago (main 4,625, range 3,115-5,948). Robustness
  suite: 8 runs, nothing breaks. Switch-on run (polities in the history, seed 7): writing in the live tree agrees with the
  after-run tree for all 12 big peoples, and states start at 2.6 kyr ago (main's run: 2.4). Kingship comes later in the live tree:
  it sees each people's range as it was at the time, while the after-run tree uses today's range for all of history
  (draft, later).
- **One data fix.** Tally sticks were dated 45 kyr while their own cited source says ~44. Because of that mismatch, the tree ignored
  the tallies' dated origins and gave them a very slow default rate, which stalled the humans alone before clay tokens. Now 44. On
  the dnd runs nothing moves: same medians to the year.

## 1. Re-setting the anchor (ruling 1: option A)

**Sources** (fetched 2026-11-05):
- Larson et al. 2014, "Current perspectives and the future of domestication studies", PNAS 111(17):6139-6146
  (pmc.ncbi.nlm.nih.gov/articles/PMC4035915): "At least 11 regions of the Old and New World were involved as independent centers
  of origin".
- Fuller et al. 2014, "Convergent evolution and parallelism in plant domestication revealed by an expanding archaeological record",
  PNAS 111(17):6147-6152 (pmc.ncbi.nlm.nih.gov/articles/PMC4035951): "recognition of a larger number of centers of agricultural
  origins, perhaps more than 20".

`anchor_peers` is the number of learners whose first find is Earth's date (`rate_of`: ramp_first(anchor_peers) / (lag x S)). With
regions, a learner is a region, so it is Earth's count of regional centres, from 11 to more than 20. Measured
(`round2/measure.py`, 12 draws on each dnd run, 8 on humans-only; files `round2/dnd_0141d1.txt`, `dnd_a2b637.txt`,
`humans_only_c1dd46.txt`). World's first writing, median of 12 (years ago):

| variant | 0141d1 | a2b637 |
|---|---|---|
| main | 4,153 (2,797-4,795) | 3,796 (2,175-5,738) |
| regions by landmass, 4 peers (round 1's rates) | 7,514 | - |
| landmass, 11 peers | 5,843 | 5,539 |
| landmass, 16 | 5,344 | 4,625 |
| landmass, 20 | 4,889 | 4,156 |
| landmass, 24 | 4,716 | 3,728 |
| landmass, 32 | 3,875 | 3,115 |
| **24 Mkm2 regions, 24 peers (shipped)** | **4,716 (1,574-7,119)** | **4,006 (1,269-6,625)** |
| 16 Mkm2, 24 | 4,901 | 5,061 |
| 12 Mkm2, 24 | 4,999 | 5,438 |
| 8 Mkm2, 32 | 4,625 | 6,057 |

**Why regions by area too (`region_mkm2`).** With landmass regions alone, the dnd check passes at 24 peers, but the humans-only
world fails. The humans there cover 168 Mkm2 yet make only 3 landmass learners. The dnd world makes 84 learners out of 37 peoples.
So the rate that suits the dnd world leaves the lone humans with chiefdoms in 5 of 8 draws, kingship in 2 and writing in 0. Earth's
20-odd centres were stretches of land, not continents. So a people's part of a landmass is now ceil(area / region_mkm2) learners,
the share split evenly (`techtree.region_shares`). Learner counts (`round2/learners_area.py`-style count, alive peoples, present
range):

| region_mkm2 | landmass only | 32 | 24 | 16 | 12 |
|---|---|---|---|---|---|
| 0141d1 (37 peoples) | 85 | 85 | 85 | 86 | 89 |
| a2b637 | 88 | 89 | 89 | 93 | 97 |
| humans alone (c1dd46) | 3 | 3 | 4 | 6 | 7 |

So 24 Mkm2 leaves the dnd worlds almost alone. dnd peoples' parts of a landmass are mostly smaller than that. On the humans-only world
it splits the humans' one largest part in two (3 learners to 4). **That is a sharp step.** One extra learner on the main landmass
nearly doubles the hazard there, and the urban chain has 5 links (towns, chiefdoms, tokens, proto-writing, writing), so it
compounds. The value is a JUDGEMENT, measured (humans-only, 8 draws, 24 peers):

| humans alone | main | landmass | 32 Mkm2 | **24 Mkm2** | 16 Mkm2 | 12 Mkm2 |
|---|---|---|---|---|---|---|
| chiefdoms | 1/8 | 5/8 | 5/8 | **8/8** | 8/8 | 8/8 |
| tokens, proto-writing | 1/8, 0/8 | 4/8, 3/8 | 4/8, 3/8 | **8/8, 7/8** | 8/8, 8/8 | 8/8, 8/8 |
| writing | 0/8 | 0/8 | 0/8 | **3/8 (median 2,763 yr ago)** | 8/8 (3,838) | 8/8 (4,794) |
| cities, kingship | 3/8, 1/8 | 4/8, 2/8 | 4/8, 2/8 | **6/8, 6/8** | 8/8, 8/8 | 8/8, 8/8 |

The landmass and 32 Mkm2 columns include the tallies fix. Without it, tokens were 2/8 and proto-writing 1/8. 16 Mkm2 and below make
writing come in every draw for a people alone. That is "forcing it" (D55), so I chose 24.

**The spread over draws is wider than main's** (0141d1: 1,574-7,119 against 2,797-4,795). With many independent learners the first
date rests on luck more than on one big people's clock. The median is where the check is set.

**anchor_check** (`test_anchor_check_meets_earths_lag`, unchanged) passes. It builds `anchor_peers` anchor learners, so it moves
with the setting. Three tests needed a longer window, assertions unchanged: test_small_peoples_rarely_invent_the_specialist_techs
(16 to 60 kyr) and test_needs_any_one_of_them (6 to 12 kyr). One isolated people is now slower than Earth's first of 24.

**Regions know apart (draft 2)?** It was not needed for the check, so it stays a draft (later).

## 2. D55's floor, redefined (ruling 2)

`techtree.own_floor`: for a soft tech rated by the anchor, the floor is the anchor learner's own hazard (rate_of x anchor_strength).
Where the tech has at least two dated independent origins (`origins_kyr`), it is no faster than Earth's median independent inventor
either (round 1's floor). A learner with any specialists to spare gets max(its own hazard, floor). The anchor learner sits exactly
at the floor, so `anchor_check` is identical with the floor on or off (new test,
test_own_floor_lifts_the_slow_and_never_speeds_the_anchor). The floor needs no source of its own for tokens and proto-writing: it is
the calibrated anchor rate, which is already set from Earth's dates. For writing, round 1's origin-based rate (0.336 per kyr) is
faster than the anchor learner's, so the cap is the one that binds.

With the shipped tree (24 Mkm2, 24 peers):

| floor on vs off | 0141d1 first writing | a2b637 first writing | humans alone |
|---|---|---|---|
| off (shipped) | 4,716 | 4,006 | as above |
| on | 6,166 | 5,637 | identical, every tech, all 8 draws |

The humans alone are bigger than the anchor learner, so the floor never binds for them. The dnd regions are mostly smaller, so
nearly all are lifted. Off; needs-decision draft (draft-own-floor-faster-than-anchor.md).

## 3. Arm T (ruling 3, D53)

On the shipped tree, 12 draws on each dnd run (`round2/spread.py`, `round2/arms_ABT.txt`). A = no arm, B = writing crosses the
taker's towns, T = B weighted by the giver's trade-mindedness (`techtree.trade_of`).

| run, variant | first writing (median) | lag first -> each contact taker (median yr) | humans | dwarves | gnomes |
|---|---|---|---|---|---|
| 0141d1 main | 4,153 | 1,209 | 3,007 | 2,470 | 2,899 |
| 0141d1 A | 4,716 | 1,221 | 4,006 | 3,731 | 3,597 |
| 0141d1 B | 4,716 | 608 | 4,234 | 4,474 | 4,009 |
| 0141d1 **T** | 4,716 | **953** | 3,867 | 4,153 | 3,728 |
| a2b637 main | 3,796 | 1,106 | 2,513 | 2,429 | 2,098 |
| a2b637 A | 4,006 | 1,001 | 3,288 | 3,728 | 3,060 |
| a2b637 B | 4,006 | 409 | 3,662 | 3,662 | 3,597 |
| a2b637 **T** | 4,006 | **665** | 3,597 | 3,599 | 3,347 |

(The peoples' columns are their writing dates, median years ago.) T shortens the wait by 22-34% against no arm, and the shortening
depends on the giver's culture. It never moves the first date, which is an invention. So T is on: `[defaults] contact_arms = "BT"`.
output.save then builds the tree twice to read the town footprint (PW-1464), and the live tree reads the live seats (PW-1472).

## 4. Robustness suite, Seven Meals, the switch-on run

**Robustness suite** (`peoples_robust.py run --family authored --trees humans_only,no_dragons --arms now`, worlds 4360a3 and af2677,
seeds 7 and 10; `round2/robust_report.md`). 8 runs: 0 crashes, 0 peoples extinct, 0 runs with one people over 85% (humans_only is
100% human by construction and is not counted). With POLITIES_LIVE off the tree is built after the history and does not feed it, so
these shares cannot differ from main's; the suite checks only that nothing breaks.

**Seven Meals** (run 07c755, frozen: measured only, nothing tuned; 12 draws; `round2/seven_meals_07c755.txt`). Baseline main on the
same run and draws.

| 07c755 | main | shipped |
|---|---|---|
| world's first writing, median (range) | 4,625 (3,115-5,948) | 5,152 (3,229-7,119) |
| towns / cities / kingship, world's first | 7,789 / 5,952 / 5,340 | 8,520 / 5,155 / 4,628 |
| lag first writing -> each contact taker, median | 848 yr | 608 yr |
| humans' writing, median | 3,865 | 4,710 |

First writing stays within main's range. The humans, PW-1461's example of a big people waiting at the border, write 845 years
earlier at the median.

**Switch-on run** (POLITIES_LIVE on, 899985 L7, dnd, tree seed 7, final defaults; `../polities/round9/live_run.py dnd 7 on - tag`,
scratch run f72bf3, 1,813 s; `../polities/round9/check.py`, output `round2/check_f72bf3.txt`). Baseline: lane 196's switch-on run
c19b5c, the same world and seed on main's code with the arms off (`../polities/round9/check_c19b5c.txt`).

| switch-on, seed 7 | c19b5c (main) | f72bf3 (this branch) |
|---|---|---|
| live writing inside the after-run tree's 12-draw spread (12 biggest peoples) | 12/12 | 12/12 |
| kingship / law / cities inside it | 12/12, 12/12, 11/12 | 8/12, 12/12, 11/12 |
| live polities now: chiefdoms, states, empires | 423, 17, 67 | 455, 18, 67 |
| first state, kyr ago | 2.4 | 2.6 |
| largest polity's share, people | 0.43 tabaxi | 0.19 human |
| tree inside the history, s | 17.8 | 25.2 |

Writing agrees. Kingship in the live tree is later than in the after-run tree on the same draw for all 12 peoples, and 4 fall below
its spread (elves 243 against 1,099 years ago). The live tree reads each frame's range, so a people small early has few region
learners early. The after-run tree has only today's range and gives every people its present regions for all time. The live tree is
the more faithful of the two. Draft draft-after-run-regions-from-present-range.md. The states come at nearly the same time. The
largest polity's share differs (0.43 tabaxi against 0.19 human), but this is one history, a re-draw, not a measure of the change.

## 5. Tests

`NUMBA_NUM_THREADS=4 uv run pytest -q -m "not slow" tests/test_techtree.py tests/test_techspread.py tests/test_lineages.py
tests/test_settlements.py tests/test_golden.py`: 198 passed. Changed tests:
- test_arms_off_is_the_plain_front_bit_for_bit compares "" against the default with contact_arms "" (the default is now "BT").
- test_the_live_tree_reads_the_live_seats_as_its_town_footprint switches the arms off explicitly for its "no footprint" check.
- Two tests got longer windows with their assertions unchanged: test_small_peoples_rarely_invent_the_specialist_techs and
  test_needs_any_one_of_them.

New tests: test_own_floor_lifts_the_slow_and_never_speeds_the_anchor and test_region_learners_split_a_continent_by_area.
test_anchor_check_meets_earths_lag is unchanged and passes.

## 6. What moves with the defaults as they ship

Every tree's dates are re-drawn: the regions are on, the anchor is 24 learners and arm T is on. With POLITIES_LIVE off the history
is untouched. With it on, the live tree feeds the polities (writing gates states, D49), so states can come at other dates. Showcase
runs keep their stored tree until rebuilt (`techtree.for_run`).
