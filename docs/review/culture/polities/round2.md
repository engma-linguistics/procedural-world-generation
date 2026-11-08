# Polities round 2: war v0 and the fall hazard (PW-1432, PW-1447, lane 175)

## In plain words

States now **conquer** and **fall apart**. Both are worked out after the run, like the rest of the Polities layer, so a rebuild is
cheap. `/api/polities` remakes the doc once per run, in about 35-70 seconds, and keeps it under `.godscache`. Nothing re-runs the
history.

**What you see on the globe (Polities layer):**
- Borders now move from century to century. A state swallows a neighbour, and an empire breaks up into its provinces.
- The legend says how many polities were taken by war and how many fell apart that century. For example, a2b637 at the present
  says "49 taken by war, 139 fell apart".
- The card of a cell now has these rows:
  - **this land: taken from X, N years ago** when the cell is a province that war took;
  - **fell: N years ago: conquered by Y** or **collapsed**. A dragon realm instead says "its ruler died and the realm broke up";
  - **conquests:** the polities it took, and when.
- Dates use `NumFmt.ago`, so a "present is year N" setting shows years.

**The rule of war (one per century step):**
- Two town polities that border each other and both stood a century ago may fight.
- A polity's strength is its settled people. It is multiplied by 1.5 for each military edge its rulers know: bronze, iron, riding,
  standing armies.
- A state or empire at least 1.5 times as strong as its neighbour takes it with a 1 in 4 chance per century.
- The loser's army breaks, and all of its land changes hands. Its capital becomes a **province** of the winner. A province goes on
  claiming its own reach, for the winner, until the winner falls; then it rules again, as a successor.
- Nobody dies or moves. Deaths and refugees come in v4.
- Dragon realms neither attack nor are attacked. Their land is still set by your O4 claim order.

**The fall hazard:**
- Every state and empire ends with Arbesman 2011's chance of about 0.46 per century. His lifetimes are exponential, with a mean of
  about 220 years.
- A fallen capital rules at most a chiefdom for the next century: complexity falls one step at a time (Currie et al. 2010). Its
  provinces go free.
- A **dragon realm** ends when its ruler dies. The ruler is an ancient dragon, dying at the run's own dragon mortality schedule:
  0.1% a year, about 0.1 per century, on the default schedule you approved on 10-28. Dragons are sapient, and their realms outlast
  human states about threefold.

**Is it plausible? Yes, in both checks the tickets asked for:**
- **Empire sizes (3c1caf, Seven Meals):**
  - The largest polity at the present is now 2.9 Mkm². Before this lane it was 1.95 Mkm² (same run, the rules of lane 169).
  - The largest ever is 3.8 Mkm², 2,100 years ago. Before, it was 2.1 Mkm².
  - The baseline is Taagepera 1997 (via `proposal.md` 2.1.2). After "government at a distance" the largest polity was never under
    2.3 Mkm², and the record before the Mongols is the Achaemenid empire's 5.5 Mkm².
  - So the run now sits inside that band, where before it was under its floor.
- **State lifetimes:**
  - The median state now lasts 200 years from founding to fall on both runs. Before, it was 1,700 years on 3c1caf (the 59 states
    that fell, under lane 169's rules) and 600 years on a2b637 (lane 169's figure).
  - The baseline is Taagepera's median of 130 years at half its peak size or more. The ticket asked for within 2x.
  - Measured Taagepera's way, at half peak or more, ours is 200 years (3c1caf) and 100 years (a2b637).
  - In his sample, 16 of 78 polities (21%) lasted 300 years or more. Ours: 24% (3c1caf) and 14% (a2b637).
- **D&D run (a2b637):** the largest polity at the present is now 1.8 Mkm². Before, it was 1.23 Mkm² (lane 169). It is still under
  Taagepera's 2.3 floor. The reason is your writing gate: there are no states there until 1,100 years ago, so conquest has had about
  ten centuries to work. PW-1448 is yours to decide, and this lane left it alone.

**One thing that is not right yet (draft filed):** far too many polities are huge at once. 3c1caf has 25 polities over 1 Mkm² at the
present, and it had 25 before this lane too. That comes from the reach rules of lane 169, not from war. The baseline is Turchin 2009's
60+ empires of 1 Mkm² or more between 3000 BCE and 1800 CE. If each lasted about 200 years, that is about 2-3 at any one time (my
arithmetic on his count, not his figure). So our planets have roughly ten times too many. Each state's reach alone is about 1 Mkm²,
so empires hardly stand out from ordinary states.

**Robust when nudged:** yes. Each main constant was moved ±10% on 3c1caf. The counts per century moved by under 15%, and the median
life did not move (200 years every time). The single largest polity is the touchiest number: it ranges from 2.9 to 5.0 Mkm² across the
nudges. Every value stays inside Taagepera's 2.3-5.5 band, and nothing explodes (table below).

## The rules, exactly

`planet/lineages/polities.py`. The module docstring has steps 0, 3b and 4, and every constant is labelled sourced or judgement. A test
checks the labels.

**Falls (PW-1447):**
- **FALL_PER_CENTURY = 0.46 (sourced).** Arbesman 2011: lifetimes exponential, λ = 0.46 per century, 41 empires from Taagepera. At
  century steps that is a 37% chance per step, a seeded draw per run, polity and step. A rebuild gives the same map. A nudged
  constant meets the same luck, so the ±10% checks compare like with like.
- **FALL_TIERS (judgement).** Only states and empires carry the hazard. Chiefdoms are a town and its cell, and they already come and
  go with the town's size.
- **COOL_STEPS = 1 (judgement, after Currie et al. 2010's "small steps").** A fallen capital can only be a chiefdom for a century,
  and then it may found a new state.
- **DRAGON_RULER = "ancient" (judgement).** A realm ends when its ruler dies. The death rate is read from
  `dragon_ages.SCHEDULES[meta.dragon_ages or DEFAULT]`, so a run on the "harsher" schedule loses its realms faster.
- **Double counting.** Arbesman's lifetimes include conquest, and here war comes on top of his hazard. War ends only 6% of the
  states that fall on 3c1caf (38 of 612), so the double count is small.

**War (PW-1432):**
- `war_v0`, plugged in at `polities.WAR`. `no_war` stays for tests.
- **Eligibility.** Both sides must be town polities that ruled last step, and the attacker must be a state.
- **Choosing a fight.** Each loser faces only its strongest eligible neighbour, and the strongest attack first. A polity taken
  this step attacks no one.
- **WAR_P = 0.25, WAR_ODDS = 1.5, MIL_X = 1.5 (all judgement).** WAR_P is checked against Taagepera's sizes above.
- **MIL_TECHS = bronze, iron, riding, standing_army.** These are the techs the brief names ("technology such as riding or iron").
- **Provinces (step 3b).** A province's seat claims right after its conqueror's capital, with its own reach. A small town that was
  taken can grow into a provincial capital with a state's reach. It stays a province until one of these happens:
  - its conqueror falls, which frees it as a successor;
  - someone else holds its town;
  - its conqueror's capital stops being a seat.
- **The cell record.** Each cell remembers which polity it was taken from: the 6th field of a map entry, `provinces` in `step_view`.
  The card reads it.

**The hook for invasions you schedule (PW-1433):** `derive(run_dir, invasions=[...])`. Each row is
`{"who": people, "whom": people or None, "from_kyr", "to_kyr", "strength": "light" | "strong"}`. Inside its window, a row multiplies
WAR_P between those peoples by INVADE_X (x2 light, x4 strong, judgement). A strong row also waives the strength odds. A conquest it
causes is logged with how = "invasion", and the card says "(an invasion)" and "invaded and conquered by". PW-1433's lane has three
jobs: feed `invasions` from the run's authored rows, and add the rows to the server's cache key (the doc is cached per run.json mtime
and VERSION). The "it happened / it didn't" read-out can count `took` entries with how = "invasion".

## Numbers

Read-only from `runs/` (L7, cells of ~3,113 km²). "Before" in the tables is the same run with WAR_P = 0 and FALL_PER_CENTURY = 0,
which is exactly lane 169's rules. Both runs are the ones lane 169 measured.

**3c1caf** (`v010-earthlike-a-seven-meals`, Seven Meals peoples):

| | before (lane 169 rules) | falls only | war and falls |
|---|---|---|---|
| largest polity at the present | 1.95 Mkm² | 1.95 | **2.86** (an empire of the humans) |
| largest at 2,000 years ago | 1.94 | 1.94 | 2.25 |
| largest ever | 2.06 | 2.06 | **3.83** (2,100 years ago) |
| polities over 1 Mkm² at the present | 25 | 24 | 25 |
| states / empires at the present | 12 / 55 | 11 / 46 | 10 / 40 |
| state life, founding to fall (median) | 1,700 years | 200 | **200** |
| state life at half peak or more (median) | 800 years | 200 | **200** |
| dragon realm life (median) | 900 years | 500 | 500 |
| conquests over the run | 0 | 0 | 387 (38 of them states or empires) |

**a2b637** (D&D peoples on dba204):

| | before (lane 169, its report) | falls only | war and falls |
|---|---|---|---|
| largest polity at the present | 1.23 Mkm² | 1.17 | **1.80** (a state of the humans) |
| polities over 1 Mkm² at the present | - | 9 | 14 |
| state life, founding to fall (median) | 600 years | 200 | **200** |
| state life at half peak or more (median) | - | 100 | **100** |
| dragon realm life (median) | - | 700 | 700 |
| conquests | 0 | 0 | 705 (104 of them states or empires) |

**How the states and empires fell on 3c1caf:** 552 collapsed, 38 were conquered, and 22 faded (their capital shrank or emptied).
Most conquests (349 of 387) take a chiefdom next to a state. War between states is rarer, because a state is seldom 1.5 times as
strong as another state that borders it.

**Lifetimes are counted in whole centuries.** A state founded at one century step and gone at the next counts as 100 years. That is
why ours have more 300-year lives than an exponential with Arbesman's mean would give, measured from founding (44% against 25%).
On Taagepera's measure, at half peak or more, the shares agree: 24% and 14% against his 21%.

## Robust when nudged (3c1caf, each constant ±10%)

| nudge | largest at the present | largest ever | states + empires at the present | median life |
|---|---|---|---|---|
| none | 2.86 Mkm² | 3.83 | 50 | 200 years |
| WAR_P 0.225 / 0.275 | 2.86 / 2.86 | 3.83 / 4.77 | 51 / 50 | 200 / 200 |
| FALL_PER_CENTURY 0.414 / 0.506 | 2.86 / 2.86 | 3.86 / 4.67 | 50 / 50 | 200 / 200 |
| WAR_ODDS 1.35 / 1.65 | 3.63 / 2.86 | 3.83 / 3.35 | 48 / 51 | 200 / 200 |
| MIL_X 1.35 / 1.65 | 2.86 / 2.86 | 3.83 / 3.83 | 50 / 50 | 200 / 200 |
| STATE_KM 135 / 165 | 3.07 / 3.75 | 3.18 / 4.96 | 57 / 47 | 200 / 200 |

- **Counts and lifetimes** hold steady.
- **The largest polity** is a maximum, and it is luck-dependent: one lucky conquest chain decides it. It ranges from 2.9 to 5.0 Mkm²,
  always inside Taagepera's band.
- **MIL_X changes nothing**, because almost every conquest is a state over a chiefdom, where the head count alone gives the odds.
- **On a2b637, raising WAR_P and the fall hazard together by 10%** moves the largest polity from 1.80 to 1.82 Mkm².

## The other runs

- **a2b637 (D&D) and 3c1caf (Seven Meals):** above.
- **cb0e0a (the new D&D showcase, made 2026-11-03 on current code):** it has cultures.json, but **no settlement ledger**, so it has no
  Polities layer. `planet settlements` on a scratch copy refuses it: "no land-use inputs per frame (meta.eraq)". Its meta.eraq is
  null. History only stores those inputs when `self.goods` is set (`planet/lineages/history/frame.py`, the eraq line). Draft filed.

## What is not in war v0

These are left out on purpose; each is a candidate for later:
- **Deaths, refugees, enslavement, tolerance** (proposal 3.3, P3 B): v4, with polities inside the history.
- **Partial conquest.** War takes the whole neighbour, never a border strip.
- **Frontiers breeding empires** (Turchin 2009, Turchin et al. 2013: herder-farmer edges that spread war techs). Our military edges
  are flat multipliers.
- **A hazard that grows with size, cultural mix and bad years** (proposal 2.1.2). Only the base hazard is here.
- **Dragons in war.** Dragon realms neither attack nor are attacked. Kobold and dragonborn realms stay as they were.

## Files

- `planet/lineages/polities.py`: `war_v0` (the WAR seam), `draw`, `strength`, the fall step and provinces in `derive`
  (`derive(..., invasions=, over=)`), `lifetimes`, the new `report` and `step_view`'s `provinces`. VERSION is now 2, so cached docs
  are remade.
- `viewer/globe/polities.js`: the "this land", "fell" and "conquests" rows, and the war line in the legend.
- `tests/test_polities.py`: war takes a weaker neighbour whole; the odds and chance gates; the invasion row; seeded draws;
  lifetimes.
