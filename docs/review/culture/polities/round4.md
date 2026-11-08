# Polities round 4: fewer giant polities (PW-1449, lane 179)

## In plain words

**Before:** on the Seven Meals showcase (3c1caf), 30 polities were over 1 million km² at the present. Almost every one was a single
capital's own reach, not an empire built by war.

**What changed:** a city-state now rules at most 250 km from its capital, the top of Spencer 2010's measured range. Law, a distance
tech, riding and roads still help, but only up to that line. Two kinds of polity keep the old, longer reach:
- a polity that has **conquered another state** (Taagepera 1997: the jumps in empire size came with "government at a distance");
- a **confederation** (lane 178; Turchin 2009: the frontier breeds empires).

**After, at the present:**
- 3c1caf has **8** polities over 1 Mkm². Over the last 3,000 years the median century has **3**.
- a2b637 (D&D) has **0**, b4d502 (D&D) has **5**, and the new Seven Meals showcase 07c755 has **11**.
- A typical state is now about 0.1-0.15 Mkm². Before, it was 0.5-0.96 Mkm² on the Seven Meals and b4d502 runs.
- State lives did not change: the median is 200 years (300 on b4d502), as in round 3.
- **The antelope-kin empire is still there.** "North of Razukum (antelope-kin)" stands at the present on the same capital as
  before (site 33467). It is now number 10, not 16, because fewer polities share the name. It is 0.52 Mkm² (was 0.39), founded 300
  years ago (was 200). A second, smaller antelope-kin empire (0.22 Mkm²) also stands.

**What is not fixed:** the largest polity on 3c1caf is 1.4 Mkm² at the present and 2.6 at most in the last 3,000 years. Taagepera's
floor is 2.3, so we are under it in most centuries. War v0 cannot chain conquests fast enough to build a giant out of 250 km states
(draft filed). On 07c755 the largest is 4.2 Mkm², inside Taagepera's band.

## Diagnosis (written before the change)

The baseline is main at 702d658b, read-only from `runs/`.

**At the present, 29 of 3c1caf's 30 polities over 1 Mkm² are one capital's own reach.** Only one has more than half its land in
provinces that war took. b4d502: 0 of 14. a2b637: 1 of 14.

**Every state on 3c1caf has the full kit.** 59 of its 66 states and empires at the present know law, a distance tech, riding and
roads. The reach then stacks:
- 150 foot-km x 4/3 (law) x 2 (distance) = 400 foot-km;
- riding and roads each make a km cost 2/3, so 400 / (2/3 x 2/3) = **900 km of flat travel**;
- that is ~2 Mkm² of open land. The largest single capital on 3c1caf holds 1.95 Mkm². The median state or empire is 0.96 Mkm².

| run | states and empires at the present | with all four techs | flat reach | median own reach (without provinces) |
|---|---|---|---|---|
| 3c1caf | 66 | 59 | 900 km | 0.93 Mkm² |
| b4d502 | 34 | 22 | 900 km | 0.85 Mkm² |
| a2b637 | 289 | 0 (70 have distance, riding and roads) | 150-675 km | 0.07 Mkm² |

**Why a2b637 still had 14:** its humans have distance, riding and roads, so 675 km, about 1.15 Mkm² for one capital. The other
states there are smaller, because many peoples have none of these techs.

**What history says** (sources via `docs/review/cultures-proposal/proposal.md` 2.1.2):
- Spencer 2010: six primary states reached **50-250 km** soon after state institutions appeared (Indus ~400 km).
- Taagepera 1997: after ~650 BC the largest polity was never under 2.3 Mkm²; the record before the Mongols is 5.5 Mkm²
  (Achaemenid). The jumps in size came with "government at a distance".
- Turchin 2009: 60+ "mega-empires" of 1 Mkm² or more between 3000 BCE and 1800 CE, over 90% in or next to the arid belt. If each
  lasted about 200 years, that is 2-3 at once. This is lane 175's arithmetic on his count, not his figure.

**So the cause** is that four judgement multipliers (round 1) stack to more than three times Spencer's top, and every state of a
people that knows the techs gets them all. A tech known by a whole people makes every one of its states a giant.

## The rule

`planet/lineages/polities.py`, `_reach`:
- **STATE_MAX_KM = 250 (sourced, Spencer 2010's top).** A city-state's reach is at most 250 km over flat land and 250 km by sea.
  Below that the old rule holds. A bare state reaches 150 km; law takes it to 200; anything more reaches the line. Climbing still
  costs, and claimed land is still a border.
- **WIDE_BY = conquest, confederation (judgement form, sourced mechanisms).** These keep the stacked reach (up to 900 km):
  - a polity holding a province that was a **state** when war took it (taking a chiefdom does not count). This is Taagepera's
    "government at a distance": a conqueror of states rules far. It lasts while it holds the province.
  - a **confederation** (step 1b, untouched otherwise). Turchin's mirror empires: herders who band together beside a state, and
    ride.
- Chiefdoms and dragon realms are unchanged. VERSION is 5, so cached docs are remade.

**Why not just shrink the multipliers?** Any rule that gives every state the same reach gives either many giants or none. Giants
need something that differs from state to state. Conquest and the frontier are the two the sources name.

## Numbers

All read-only from `runs/`, L7 (cells of ~3,113 km²). "Before" is main at 702d658b (lane 178's rules). "Median state" is the median
area of the states and empires standing at the present. "Life" is the median from founding to fall, then at half peak or more.

| run | over 1 Mkm² now | per century, last 3,000 years (median, max) | largest now | largest ever | median state | life | land ruled now |
|---|---|---|---|---|---|---|---|
| 3c1caf before | 30 | 19, 32 | 2.86 Mkm² | 4.57 (1,000 years ago) | 0.96 Mkm² | 200 / 100 years | 75.3 Mkm² |
| 3c1caf after | **8** | **3**, 10 | 1.40 | 2.60 (300 years ago) | **0.14** | 200 / 100 | 41.0 |
| a2b637 before | 14 | mean 0.8, 14 | 1.80 | 1.80 | 0.09 | 200 / 100 | 78.7 |
| a2b637 after | **0** | 0, 2 | 0.98 | 1.21 | 0.10 | 200 / 100 | 56.0 |
| b4d502 before | 14 | mean 5.2, 15 | 1.98 | 3.23 | 0.92 | 300 / 100 | 38.4 |
| b4d502 after | **5** | 0, 7 | 1.93 | 1.98 | 0.15 | 300 / 100 | 27.0 |
| 07c755 before | 33 | mean 27, 37 | 3.60 | 4.83 | 0.53 | 200 / 100 | 107.4 |
| 07c755 after | **11** | 4, 11 | **4.17** | 4.17 | 0.13 | 200 / 100 | 68.0 |

**Against the ticket's bar** ("under ~8 over 1 Mkm² at the present on 3c1caf and a2b637; the largest still inside 2.3-5.5 Mkm² on
3c1caf"):
- The count: met on a2b637 (0). On 3c1caf, 8 at the present is on the line; the present is near this run's busiest century (the
  max is 10, the median 3). The median century matches Turchin's 2-3.
- The largest on 3c1caf: **not met.** 1.40 Mkm² at the present. The largest per century over the last 3,000 years runs from 0.91 to
  2.60 Mkm², median about 1.6. Before, the band was met because one capital's reach alone was 1.95 Mkm².
- The new Seven Meals showcase 07c755 meets the band (4.17 Mkm²) but has 11 over 1 Mkm² at the present (median century 4).

**What the giants are now (3c1caf, the present).** Of the 8 over 1 Mkm², 6 are confederations (half-orcs, hobgoblins twice, dragonborn,
lizardfolk, humans) and 2 are human states that took another state. None has much land in provinces. Before, they were all human city-states.
Turchin puts over 90% of mega-empires in or next to the arid belt, where herder confederations sit, so this is in character. A
decision draft asks whether confederations should keep the long reach.

**Land ruled** drops by a third to a half: states no longer reach across the unclaimed land between them.

**What I tried first, and why it failed:**

| 3c1caf | over 1 Mkm² now | largest now | largest ever | antelope-kin empire now |
|---|---|---|---|---|
| cap only, nobody wide | 0 | 0.35 | 0.37 | none (4 states over the run) |
| cap only, WAR_P 0.5 / 1.0 | 0 / 0 | 0.40 / 0.59 | 0.41 / 0.59 | none |
| cap only, a province rules with its conqueror's reach | 0 | 0.43 | 0.66 | none |
| cap at 400 km (Spencer's Indus) | 0 | 0.68 | 1.04 | none |
| cap, conquest wide only | 1 | 1.06 | 1.72 | none |
| cap, conquest wide only, WAR_P 1.0 | 4 | 2.37 | 2.37 | none |
| **cap, conquest and confederations wide (chosen)** | 8 | 1.40 | 2.60 | yes |

The cap alone fixes the count on every run (0 over 1 Mkm²) but leaves no empires: war v0 rarely lets one state take another, because
states 250 km apart seldom touch. Raising WAR_P to 1.0 (a stronger state always takes its weaker neighbour) still does not reach
2.3 Mkm² without the conquest rule, and it is a forced number. So I left war's constants as they were.

## Robust when nudged (3c1caf, ±20%)

**What I introduced, STATE_MAX_KM:**

| STATE_MAX_KM | over 1 Mkm² now | per century (median, max) | largest now | largest ever | median state | life | antelope-kin empire now |
|---|---|---|---|---|---|---|---|
| 200 | 4 | 3, 7 | 1.48 | 2.71 | 0.10 | 200 | yes (0.51 Mkm²) |
| 250 | 8 | 3, 10 | 1.40 | 2.60 | 0.14 | 200 | yes (0.52) |
| 300 | 5 | 3, 8 | 1.36 | 2.54 | 0.19 | 200 | no (49 antelope-kin states over the run) |

- The median century holds at 3 and the largest moves by under 10%. The median state scales with the cap, as it should.
- On a2b637, 300 km gives 0 over 1 Mkm² (largest 0.96).
- **The antelope-kin empire at the present is luck-sensitive.** It stands at 200 and 250 km, not at 300. At 300 km the human states
  next door reach further and the confederation's own heads within reach change. Their confederations still form 49 times over the
  run. Round 3 found the same: they hold one in 47 of 64 centuries, so the present is one draw.

**The old multipliers, which now act only on conquerors and confederations, are touchy:**

| nudge | over 1 Mkm² now | per century (median, max) | largest now | largest ever |
|---|---|---|---|---|
| DISTANCE_X 1.6 / 2.4 | 0 / 6 | 1, 5 / 5, 12 | 0.97 / 4.05 | 2.16 / 4.05 |
| RIDE_X and ROAD_X 1.2 / 1.8 | 1 / 8 | 0, 1 / 10, 17 | 1.59 / 5.21 | 1.59 / 7.12 |

Riding and roads together at 1.8 put the largest past the Achaemenid record (7.1 against 5.5 Mkm²). These four multipliers were
judgement calls in round 1, and they now set the size of every giant. This is the next lever, and a draft is filed. I did not tune
them here.

## Checks that still hold

- **War v0:** median state life 200 years on 3c1caf and a2b637, 300 on b4d502 (round 3: the same). At half peak or more: 100 years
  on all three (round 3: the same). Taagepera's median is 130.
- **Scheduled invasions:** `tests/test_invasions.py` passes.
- **Confederations:** the antelope-kin empire stands (above).

## Files

- `planet/lineages/polities.py`: `STATE_MAX_KM`, `WIDE_BY`, `_reach(..., wide)`, the conquered-state set `prov_state` in `derive`;
  VERSION 5.
- `tests/test_polities.py`: the cap and the wide reach.
