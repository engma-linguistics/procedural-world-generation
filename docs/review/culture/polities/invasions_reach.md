# Invasions that reach (PW-1450, lane 198)

## In plain words

Before this, an invasion you schedule acted only where the invaders' state already touched the victims. Daniel ruled (D50, 11-04):
B and C, plus far reach for highly mobile peoples. A **strong** row now does three more things in the polities read after the run:

- **War band (C).** If the invaders rule only chiefdoms in the window, their largest town that already stood last century rules as
  a state for the window. It claims a state's reach and can attack.
- **Expedition (B).** If no state of theirs borders the victims, their nearest state sends an expedition. It crosses unruled land
  (and sea, if they have boats) up to its own reach again. It claims that corridor for the century and attacks the first polity of
  the victims it meets.
- **Mobile peoples.** The expedition's reach is multiplied by the people's mobility, using numbers the model already has. Nomads
  (the `nomadic` trait: spec.TRAITS speed x2) and pastoral nomads (spec.WAY_MOBILE 1.0) go x2 and transhumant herders x1.6. Settled
  peoples stay at x1. Mobile peoples may also ride *through* other peoples' states, at half pace. Riding and roads already make each
  km cheaper (polities.RIDE_X, ROAD_X), so a mounted horde gets both. Nothing is coded per people.

Light rows are unchanged. Runs with no rows give the same output as main, byte for byte.

**What came of it, on the same strong one-century rows, main against this branch:**

| run | rows | happened on main | happened now | new by expedition | new by war band |
|---|---|---|---|---|---|
| a2b637 (D&D) | 30 | 9 | **11** | 2 (122, 184 km) | 0 (5 war bands seated, none reached the victims) |
| 3c1caf (Seven Meals, frozen: measured only) | 42 | 8 | **11** | 3 (165, 239 and 689 km; the 689 km one was the half-orcs, mobility x2) | 0 |

That is a small gain. Most rows that still say "it didn't" fail for one reason: the victims are further away than one more state's
reach. A settled state on these runs has 150 foot-km (no law, no distance techs), so the expedition can cross only about 150 km of
open land. The read-out now says how far the nearest polity of the victims was, so Daniel can see the gap. How far an expedition
should go is a judgement call that is not sourced here. It is in an inbox draft (`draft-expedition-range.md`), not tuned.

Round 7's long row ("the antelope-kin come down on the humans", 2,000-300 years ago, strong) on 3c1caf: on main it took 4 polities,
1,478,746 km² (scratch `extra_main.json`, below). On this branch, in a check run during the lane: 10 conquests, 1,509,876 km². Five
expeditions went 111-896 km, with mobility x2. A war band was seated in 5 centuries of the window.

## The rows (how they were rebuilt)

Lane 177's 30 and 42 rows were not saved, so they were rebuilt the same way they are described, with a fixed recipe
(`invasions_reach_score.py`, beside this doc). Take the N peoples (groups rolled up into their people, dragons apart) that rule the
most polity-centuries on the run with no rows: 6 on a2b637 (elves, gnomes, humans, drow, kobolds, halflings) and 7 on 3c1caf
(hobgoblins, humans, antelope-kin, gnomes, dwarves, half-orcs, kobolds). Write one strong row per ordered pair, in one century: the
invaders' peak century as a state (most land), else as a chiefdom. Each row is scored alone (one derive per row). Because the
recipe differs from lane 177's, main's counts here (9 and 8) are this recipe's baseline, not lane 177's 5 and 2. The antelope-kin
peak as a state on 3c1caf is 2,400 years ago, so their row on the humans already happened on main under this recipe.

## Sanity: ordinary wars did not change

- **No rows:** the whole polities doc (`made_s` zeroed, sorted JSON, SHA-1) is identical on main and the branch. a2b637:
  `82afc2a2...`; 3c1caf: `6115ac3d...`.
- **With a row, the plain wars in the row's own century** (not taken by the row), compared with the no-row doc: the branch equals main
  on all 72 rows. Where main already differed (4 rows on a2b637, where the row itself took a polity that plain war would have
  taken), the branch differs in exactly the same way. On the 5 new rows the plain wars of the window century are identical.
- **Plain wars before the window** are identical on every row. After the window the map has changed, so later wars may differ. The
  run's total moved by at most 4 of 640 (3c1caf dwarves on humans) and 1 of 930 (a2b637 drow on humans).
- **How it is kept apart:** plain war never uses an expedition's pair. The pair is added to the war step for that row only. The
  corridor is claimed after the borders are read, so it gives no third people a new border that century.

## Robust, not brittle

- The reach is one rule built on numbers that already exist (a state's own reach, the model's mobility tables). There is no
  per-people setting and no new tuned constant except FOREIGN_X (judgement: riding through a third people's land costs x2).
- A row that finds nothing still says why, now with the expedition's reach and the nearest victim's distance. Odd rows (unknown
  people, invaders who are the victims) are untouched.
- The war band needs a town that already stood last century, so it never seats a polity out of nothing. It has no writing gate. That
  goes against D49 ("real states have writing"), but it is what C asks for. The card marks it (`war_band`).
- Not run: the peoples robustness suite (tools/peoples_robust.py). It runs only the peoples history, and this change does not touch
  the history. It still needs one run at merge, as asked (see the lane report).

## Where it lives

`planet/lineages/invasions.py` (mobility, expedition, REACH_RULE, VERSION 2), `polities.py` (`_war_bands`, `_expedition`, war_v0's
optional `expedition` hook), `server.py` (the cache key adds invasions.VERSION only for runs with rows), `viewer/invasiontab.js`
(how a row reached). The live polities inside the history (POLITIES_LIVE, off) are not wired: `polity_live.py` was lane 196's file
(draft `draft-live-polities-invasions-reach.md`).

Scratch results (gone after the lane): `main_a2b637.json`, `branch_a2b637.json`, `main_3c1caf.json`, `branch_3c1caf.json`,
`extra_main.json`, under the lane's scratch dir.
