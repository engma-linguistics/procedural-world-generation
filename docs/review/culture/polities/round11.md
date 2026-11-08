# Polities round 11: aggressive conquerors are harsher, and campaigns reach ~1,000 km or an empire's own radius (PW-1487, PW-1478; lane 204)

## In plain words

- **Harsher conquerors (Daniel D59 C, PW-1487).** A winner's aggression now makes it harsher to the peoples on the land it takes, not
  only more likely to fight. How much depends on its tolerance. A martial, intolerant winner expels or razes in any era. A martial,
  tolerant one (Cyrus) still keeps the peoples it takes. A plain winner (aggression 0.3, most peoples) is judged exactly as before.
- **What came of it** (same world, same tree seeds, same six invasion rows, against today's main with the switch on, three tree
  seeds): martial, intolerant winners now expel. On seed 10 they kept 6, thinned 3 and expelled none on main. On the branch they kept
  1, thinned 7 and expelled 48. Tolerant winners still keep nearly everyone: 92-99% of the peoples they took on every seed (main
  97-99%). Seed 7 had no martial, intolerant winner at all, on main or the branch.
- **Campaign range (Daniel D56 B plus Rome, PW-1478).** An invasion you write can now send its expedition up to 1,000 km across open
  land. Nomads and pastoral nomads go twice as far. A state larger than about 3.1 million km2 goes as far as its own radius. Rome in
  AD 117 was 5.0 million km2 (radius about 1,260 km). Its campaign that year ran about 1,130 km from the Euphrates to the Persian Gulf.
- **Rows that happen.** In the history (live switch on): 2 rows of 18 took land on main over three seeds, 9 of 18 on the branch. In the
  read-out after the run (lane 198's scheduled-invasion score): a2b637 (D&D) 11 of 30 rows happen on main and 15 of 30 on the branch.
  3c1caf (Seven Meals) was not scored: the lane stopped at its tool budget (section 4).
- **Ordinary wars** were fought as often as on main: 95/94, 208/207 and 250/251 per seed, main/branch. More of them are harsh now: 9/12,
  4/11 and 19/47 harsh fates. Peoples' shares today stay within 0.2 percentage points of main. Writing dates are identical, and the
  states 0 years ago are within 3.
- **The cost in heads is now large where martial, intolerant peoples invade.** Over the last 2,000 years conquest took 0.15 M heads on
  seed 7 (main 0.014 M), 5.2 M on seed 10 (main 0.025 M) and 18.8 M on seed 3 (main 0.17 M). The present population is about 0.9-1.0
  billion on every run, and it is the same as main within 0.1%: the land refills. Most of the toll is the invasion rows that now
  happen: on seed 3, the dwarves' row on the hobgoblins took 12.3 M heads in 61 expulsions. Today an expelled people simply dies. So
  these numbers read as massacres, never as refugees. That is a mechanism Daniel has not ruled on. It is filed as a needs-decision
  draft (`draft-expelled-peoples-go-where.md`).
- **PW-1465** (kept / thinned / expelled thresholds) is answered for its harshness part (section 3). Its open part, where the
  expelled go, is the draft above.

## 1. What changed

**Harshness (PW-1487, `history/polity_live.py::harshness`).** It was: old enmity + TOL_X x (0.5 - tolerance). It is now:

    harshness = old enmity + TOL_X x (0.5 - tolerance) + TOL_X x (aggression - AGG_HARSH) x (1 - tolerance)

with TOL_X = 2 (unchanged) and AGG_HARSH = attitudes.AGG_BASE = 0.3, a plain people's aggression. It is read against the same cut
points (FATE_AT 0.25 / 0.6), and the cut still scales with aggression / AGG_MID. Why this form, and no new tuned number:
- **The gate (1 - tolerance)** comes from Daniel's own two poles (D54): Genghis Khan and Cyrus were *both* great conquerors. So
  aggression cannot make every conqueror harsh. It makes an intolerant one harsher, and a fully tolerant one not at all.
- **The weight** reuses TOL_X. For a fully intolerant winner, a unit of aggression moves harshness exactly as a unit of tolerance does.
- **The anchor** is a plain people (0.3). A plain winner is judged exactly as before. A peaceful one (aggression under 0.3: the elves
  and firbolgs here run at 0.04-0.10) is now a little milder. That is the same line continued. On seed 7 it turned the firbolgs'
  expulsion of humans into a thinning.
- Examples. Round 10's orcs (tolerance 0.36, aggression 0.60) with no old enmity: 0.28 + 0.38 = 0.66, expelled (round 10: 0.28,
  thinned only where the tree had an old quarrel). A tolerant horde (0.8, 0.8): -0.6 + 0.2, kept. A middling, martial winner
  (0.5, 0.5) facing an old enemy (0.5): 0.7, expelled (before: 0.5, thinned).

**Campaign range (PW-1478, `invasions.campaign_budget`).** The expedition's budget in foot-km is:

    max(CAMPAIGN_KM = 1000, EXTENT_X x sqrt(state's area / pi)) x mobility

with EXTENT_X = 1 and mobility unchanged (x2 for nomads and pastoral nomads, x1.6 for transhumant herders). It was the state's own
reach again (about 150 foot-km for a settled state on these runs). Riding and roads still make each km cheaper (polities.RIDE_X,
ROAD_X), so a road-building empire's 1,000 foot-km cover more map than 1,000 km.
- **1,000 km and x2** are Daniel's D56 B ("from that part of the continent", invasions.FROM_KM's range).
- **The radius term** answers his "the Roman Empire sure did campaign waaaaay away". Rome at its peak in AD 117 held 5.0 million km2
  (Taagepera 1979, "Size and Duration of Empires: Growth-Decline Curves, 600 B.C. to 600 A.D.", *Social Science History* 3(3/4):
  115-138; via Wikipedia's *List of largest empires*, fetched 2026-11-07). That gives a radius of sqrt(5.0e6 / pi) = 1,262 km.
  In 116 Trajan took Ctesiphon and "sailed downriver to the Persian Gulf", where the king of Charax submitted (Wikipedia, *Trajan's
  Parthian campaign*, fetched 2026-11-07, citing Bennett 2001 and Birley 2013). The great-circle distance from the Roman Euphrates
  crossing at Zeugma (37.059 N, 37.866 E, Wikipedia *Zeugma, Commagene*) to Charax Spasinu (30.895 N, 47.578 E, Wikipedia
  *Charax Spasinu*) is about 1,130 km, 0.9 of the radius. EXTENT_X = 1 rounds that. It is one data point, so treat it as a
  judgement checked against Rome, not a fit. The organisation that lets an empire campaign far is already in its size: an empire gets
  past STATE_MAX_KM only by ruling at a distance (polities.WIDE_BY).
- No state on these runs is that large (the largest live polity is 1.6 million km2, radius 715 km), so the fixed 1,000 km does all the
  work today. The radius term lets a run that grows a Rome campaign further.
- The viewer's invasion help text says the new range. `invasions.VERSION` is 3, so the server's cached polities docs with rows are
  remade. The derive doc with no rows is unchanged (section 5).

## 2. Fates by the winner's tolerance and aggression (history, switch on)

World 899985 (L7), dnd tree, round 10's six strong rows (`round11/live_run.py`), tree seeds 7, 10 and 3, polities in the history on.
Main = a `git archive` of 330b021b, in the same scratch data root. Measured by `round11/measure.py` (the winner's tolerance and
aggression at the conquest, `winner_att`: intolerant under 0.5, martial at 0.45 or more). Peoples counted once per conquest.

| seed | run | winner | kept | thinned | expelled | heads lost |
|---|---|---|---|---|---|---|
| 7 | main 83ba0a | intolerant, plain | 7 | 5 | 2 | 11,608 |
| | | tolerant, martial | 39 | 1 | 0 | 2,528 |
| | | tolerant, plain | 91 | 1 | 0 | 170 |
| 7 | branch 5072b4 | intolerant, plain | 4 | 10 | 0 | 149,079 |
| | | tolerant, martial | 50 | 1 | 0 | 2,343 |
| | | tolerant, plain | 130 | 1 | 0 | 170 |
| 10 | main 99662c | **intolerant, martial** | 6 | 3 | **0** | 13,284 |
| | | intolerant, plain | 1 | 0 | 0 | 0 |
| | | tolerant, martial | 15 | 1 | 0 | 11,908 |
| | | tolerant, plain | 122 | 0 | 0 | 0 |
| 10 | branch 07694c | **intolerant, martial** | 1 | 7 | **48** | 3,667,855 |
| | | intolerant, plain | 1 | 8 | 1 | 600,957 |
| | | tolerant, martial | 41 | 9 | 1 | 874,501 |
| | | tolerant, plain | 129 | 1 | 0 | 12,889 |
| 3 | main c25614 | **intolerant, martial** | 7 | 0 | 1 | 179 |
| | | intolerant, plain | 12 | 3 | 7 | 40,048 |
| | | tolerant, martial | 276 | 4 | 1 | 120,217 |
| | | tolerant, plain | 73 | 5 | 0 | 9,957 |
| 3 | branch 716767 | **intolerant, martial** | 0 | 13 | 2 | 2,742,756 |
| | | intolerant, plain | 9 | 21 | 67 | 13,658,084 |
| | | tolerant, martial | 275 | 20 | 4 | 2,383,894 |
| | | tolerant, plain | 72 | 6 | 0 | 10,445 |

- **Does a martial, intolerant winner raze now?** Yes, on both seeds that had one. On seed 10 such winners expelled 48 of the 56
  peoples they took (main: 0 of 9). They were the leonins (tolerance 0.38-0.45, aggression 0.63-0.77), the dwarves (0.16-0.38,
  0.50-0.67) and the orcs (0.26-0.37, 0.57-0.74). On seed 3 none of the 15 they took was kept (main: 7 of 8 kept). Seed 7 never had
  one, on main or the branch: its winners are humans, tabaxi and halflings, tolerant peoples.
- **Does a tolerant winner still keep?** Mostly. Tolerant, plain winners kept 92-99% on the branch (main 94-100%). Tolerant, martial
  ones kept 80-98% (main 94-98%). The extra thinnings are by leonins of tolerance 0.57 and aggression 0.79-0.85 on seed 10. That is
  middling tolerance and a very high aggression, which their own invasion wins raised (attitudes.WIN_AGG). It is the mechanism working
  as written: a conqueror that has just won grows more aggressive.
- **"Intolerant, plain" on seed 3** is the dwarves' invasion row (aggression just under 0.45 at those times; they are insular, so
  intolerant). Most of its toll comes from the row now happening at all (section 4), not from the aggression term: on main that row
  never reached the hobgoblins.
- Sizes: the heads lost are per conquest, capped at 10% of a people's heads a century (FATE_MAX, unchanged). The present population
  is 873-874 M (seed 7), 946-948 M (seed 10) and 1,035-1,037 M (seed 3) on main and branch alike.

## 3. PW-1465: answered, apart from where the expelled go

PW-1465 asked how harsh a conqueror should be (the kept / thinned / expelled cut points and cuts) and where the expelled go. Daniel
ruled the cut points a placeholder (D54) and asked for "Genghis Khan razing cities to Cyrus's tolerance, in any era". With PW-1481
(the winner's tolerance) and now D59 C (its aggression, gated by intolerance), the harshness is a mechanism. The cut points only
place the boundaries on a scale that the winner's attitudes span from end to end. Section 2 shows both poles on the same seeds:
- intolerant, martial winners expel (seed 10: 48 of 56);
- tolerant winners keep (seeds 7, 10, 3: 99%, 94%, 92%).
So the harshness question is closed by evidence. What is left is a mechanism question, not a number: the expelled vanish instead of
moving. That goes to Daniel as a needs-decision draft (A keep, B they move to their own nearest free land, C a martial winner razes
and a less martial one drives out; lean C).

## 4. Scheduled invasions that happen (the read-out, lane 198's score)

`invasions_reach_score.py` (lane 198's recipe: the 6 peoples that rule the most polity-centuries, one strong one-century row per
ordered pair, each row scored alone with `polities.derive`), on the finished run a2b637 (D&D), today's main (a `git archive` of
330b021b) against the branch. Output: `round11/score_main_a2b637.json`, `round11/score_br_a2b637.json`.

| run | rows | happened on main (330b021b) | happened on the branch | new, and how far the expedition went |
|---|---|---|---|---|
| a2b637 (D&D) | 30 | 11 | **15** | human>orc 514 km, human>hobgoblin 572 km, human>drow 367 km, gnome>hobgoblin 1,419 km on the map |
| 3c1caf (Seven Meals) | 42 | not run | not run | |

- The peoples picked are humans, orcs, gnomes, hobgoblins, kobolds and drow, the same on both sides. Lane 198 picked elves, gnomes,
  humans, drow, kobolds and halflings, on older code (its 9 -> 11 of 30). So main's 11 here is this recipe's baseline today.
- The gnomes' 1,419 map-km is more than 1,000 foot-km because roads and riding make each km cheaper (polities.ROAD_X, RIDE_X).
- **Ordinary wars in the read-out did not change.** With no rows, the whole doc is identical on main and the branch (`base_sha`
  equal). With a row, the plain wars in the row's own century are the same as the no-row doc's on all 30 rows, on both sides. The
  plain wars before the window are identical on all 30. The run's plain-war total moves by at most 3 of 3,069, the same on both
  sides.
- **3c1caf (Seven Meals) is not scored.** One scorer takes about 35 minutes for 30 rows on this shared machine (load 35-60). The
  lane stopped both 3c1caf scorers at its tool budget, before they finished. To finish (about 50 minutes, two jobs):
  `invasions_reach_score.py /…/runs/3c1caf 7 OUT.json --jobs 1`, once from a `git archive` of main and once from this branch.

## 5. Ordinary wars and stability (history, switch on; against main on the same seed)

| | seed 7 main / branch | seed 10 main / branch | seed 3 main / branch |
|---|---|---|---|
| ordinary wars (conquests not by a row) | 95 / 94 | 208 / 207 | 250 / 251 |
| harsh fates in ordinary wars (thinned + expelled) | 9 / 12 | 4 / 11 | 19 / 47 |
| heads lost in ordinary wars | 14,306 / 151,592 | 25,192 / 409,414 | 170,281 / 4,904,937 |
| invasions (conquests by a row) | 1 / 23 | 0 / 40 | 7 / 32 |
| rows that took land (of 6) | 1 / 2 | 0 / 4 | 1 / 3 |
| states 2,000 / 1,000 / 500 / 0 years ago | 36/65/70/85 ; 36/65/70/84 | 99/99/106/116 ; 97/99/105/114 | 95/96/136/124 ; 94/95/134/121 |
| shares, largest three (%) | human 41.2, hobgoblin 13.3, halfling 9.1 ; 41.1, 13.4, 9.0 | human 62.8, halfling 12.3, hobgoblin 5.2 ; 62.6, 12.3, 5.5 | human 60.6, hobgoblin 8.8, orc 6.5 ; 60.6, 8.8, 6.6 |
| first writing / kingship / law / cities (kyr ago) | identical | identical | identical |
| live step s | 19.1 / 55.2 | 35.4 / 87.2 | 23.6 / 36.3 |

- Wars are fought as often. They are harsher where the winner is martial and intolerant, which is the ruling. The ordinary-war toll
  also rises because winners of invasions grow more aggressive afterwards (WIN_AGG). So a people that has won an invasion fights its
  next ordinary war harder.
- The live step costs more (larger expedition budgets search further). It is still under 1.5 minutes of a 23-35 minute run.
- Rows in the history (switch on): orc_human now happens on seeds 7, 10 and 3, with expeditions of 110-2,779 km on the map. Over the
  rest of the rows, dwarf_hob happens on 10 and 3, leonin_human on 10, and human_kenku on all three. hob_elf and elf_orc still never
  reach: their victims lie beyond 4,000-5,200 foot-km, across the sea or past other peoples' states.

## 6. Switch off, and the after-run read-out with no rows

The history with the switch off does not call either change. `_fates` and the expedition run only in `LivePolities`, and `polities.derive`
calls the expedition only for a strong row. So a switch-off run is byte-identical to main (by construction; not re-run here). The
read-out with no rows gives the same doc as main on a2b637 (`base_sha` in section 4's score files, main against the branch).

## 7. Tests

- New: `tests/test_lineages.py::test_aggression_makes_an_intolerant_conqueror_harsher_not_a_tolerant_one` and
  `::test_campaign_budget_is_a_fixed_range_or_the_states_own_radius_times_mobility`.
- Changed on purpose: `test_live_conquest_harshness_reads_the_winners_attitudes`. The "middling winner thins an old enemy as the old
  rule" case now uses a plain winner (aggression 0.3). A middling, martial (0.5) one now expels, and the test asserts that.
  `test_live_polities_send_a_strong_rows_expedition_across_a_gap`'s short arm is CAMPAIGN_KM 1 with no radius term (there is no
  "None" any more).
- `NUMBA_NUM_THREADS=2 uv run pytest -q -n 2 -m "not slow" tests/test_lineages.py tests/test_techtree.py tests/test_faith_spread.py`:
  **192 passed** (523 s). `tests/test_invasions.py tests/test_polities.py`: **27 passed**. The full suite and the goldens were not
  run (coordinator, at merge). No golden should move: the history's default (switch off) and derive with no rows do not reach the
  changed code.

## Files

`round11/live_run.py` (the runs), `round11/measure.py` (section 2 and 5 tables). Runs (scratch data root, gone after the lane):
main 83ba0a, 99662c, c25614; branch 5072b4, 07694c, 716767. Scores: `round11/score_main_a2b637.json`, `round11/score_br_a2b637.json`.
