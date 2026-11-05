# Polities round 10: invasions that reach inside the history, and conquest harshness from attitudes (PW-1479, PW-1481, PW-1465; lanes 201, 201b)

## In plain words

- **What changed.** When polities run inside the history (the switch POLITIES_LIVE, off by default), invasions you write now reach
  victims the way they already do in the polities read after the run (PW-1450). That means a war band if the invaders have only
  chiefdoms, and an expedition across a gap if they share no border. The history also keeps each people's attitudes (tolerance and
  aggression), stepped every recent century from its own wars, rule and contacts. A conquest's fate (kept, thinned or expelled) now
  follows the winner's tolerance, and its toll follows the winner's aggression. Before, every winner was equally harsh to a people it
  disliked the same amount.
- **Every comparison below** is against main with the switch on, on the same world (899985, L7), the same tree (dnd) and the same tree
  seed, with the same six strong invasion rows written into the history (`round10/live_run.py`). Main is commit 01b03c34. Its runs are
  51916e (seed 7) and 70cf9f (seed 10).
- **Rows that happen.** Seed 7: 1 of 6, the same as main. Seed 10: 0 of 6, the same as main. The war bands now seat states for the
  invaders (on seed 10, 90 seatings over the six rows). But the victims lie further than one more state's reach, about 150 foot-km
  (the nearest at 287 to 6,795 foot-km on seed 7). As a test arm only, a fixed campaign range of 1,000 km (D56's option B) made 2 of 6
  rows take land on seed 7, with 19 invasions against 2. The default stays option A until Daniel answers D56.
- **Fates by the winner's tolerance.** A tolerant winner keeps its peoples. Winners of tolerance 0.6 or more kept every people on
  the land they took: 118 of 118 on seed 7, 33 of 33 on seed 10. Harsh fates came only from winners under 0.6. A harsh conqueror is
  rare, though: on seed 7 conquest cost 2,745 heads in all, against 19,571 on main. One expulsion happened, of 28 heads. The peoples
  who win wars here are mostly tolerant ones, and the walk drifts conquerors further up. Seed 10 cost more than main (44,444 heads
  against 24,865), all of it in thinnings. That is a judgement call for Daniel (new inbox draft); see section 3.
- **Not destabilised.** States, shares and writing are the same as main within a few states and 0.1 percentage points. Writing
  dates are identical on both seeds. Seed 10 gains states early (4 against 0, 2,000 years ago), from the war bands.
- **Cost.** The live step rose from 4.0 s (main) to 108.7 s with lane 201's code. Nearly all of that was one unbounded search on every
  missed expedition: how far was the nearest victim, for the read-out's "why not". Inside the history that search now looks only
  4 budgets out (`polity_live.NEED_X`); past that the why-not says "none lay within N km". The read-out still searches without limit.
  After the bound: SEE6 (seed 7), 15.5 s on seed 10 (main 3.2 s).
- **Switch off:** a run is still byte-identical to main, apart from timings and the code's own hash (section 7).

## 1. What changed in the code

**Invasions inside the history (PW-1479).** `history/polity_live.py` now calls the read-out's own functions; nothing is copied.
- Before the claims, `polities._war_bands` (D50 C) runs. A strong row whose invaders rule only chiefdoms that stood last century
  seats their largest town as a state for the century. The record and the row's log mark it (`war_band`), as derive does.
- The war step gets `ctx["expedition"]` = `polities._expedition` over the live arrays (`edz`, `sea`, `ice`). Each expedition's two sides
  are turned into record ids after the war, as derive does. LivePolities carries `lines` / `lidx` (each line's id, traits, way and
  demography), so `invasions.mobility` reads the same numbers in both paths.
- **The expedition's range is one constant** (`invasions.CAMPAIGN_KM`, PW-1478 / D56). `None` (now) keeps option A, the state's own
  reach again. Daniel's answer is one edit (D56's lean B: `1000.0`), read by both the read-out and the history through
  `invasions.campaign_budget`. With `None` the read-out's budget is the same float as before (`b * mob`).
- **The why-not search is bounded inside the history (lane 201b, cost).** `_expedition(..., need_x=None)`: the read-out keeps the
  unbounded search for how far the nearest victim was. The history passes `need_x = NEED_X` (4). The war log then keeps either
  `exped_need` (found within the bound) or `exped_need_gt` (the bound searched). The read-out's why-not says "none lay within N km on
  the same terms" for the second. Test: `tests/test_invasions.py::test_the_historys_bounded_why_not_search_says_more_than_the_bound`.

**Conquest harshness from attitudes (PW-1481, unblocks PW-1465).** `attitudes.Attitudes` does no I/O and `attitudes.temperament` is
pure, so the history keeps its own:
- one `Attitudes` per people (the history has peoples, not cultures), seeded from the run's seed and stepped each recent century in
  `LivePolities._attitudes` from the history's own signals. Conquest: the winner of a war or invasion. Rule: each polity's ruler, with
  the number of foreign peoples on its land, and those peoples as subjects. Contact: the number of other peoples on or beside its land.
  There is no faith term (faiths are made after the run);
- the fate (`_fates`) reads the winner's **harshness** to each people on the taken land: **old enmity + TOL_X x (0.5 - the winner's
  tolerance)**, with TOL_X = 2 (judgement). The enmity is the tree's (`StandIns.hostility`), as before. A 0.5 winner reproduces the old
  rule exactly. At 1.0 harshness drops by 1, so even an old enemy is kept. At 0 it rises by 1, so even strangers are expelled. The same
  cut points (FATE_AT 0.25 / 0.6) now read this harshness;
- the cut scales with the winner's **aggression / AGG_MID** (0.5, judgement), never more than all of it. A martial people's starting
  aggression cuts as the old placeholder did; a plain people's 0.3 cuts 0.6 of it. FATE_MAX (10% of a people's heads a century) stays
  as the guard against a chain of conquests ending a people;
- `polities_live.json` gains `attitudes` (per people: temperament, and a track every 500 years), and each conquest gains `winner_att`.

Not done (third bullet of PW-1465): the expelled still simply die. "The expelled move" (option B's refugees) is a mechanism Daniel
has not ruled on.

## 2. Rows that happen

Six strong rows per tree (`round10/live_run.py` ROWS): orc_human, hob_elf, dwarf_hob, leonin_human, human_kenku, elf_orc. Measures
from `round10/measure.py`; outputs `round10/m_*.txt`.

| run | rows that took land | invasions (conquests by a row) | expeditions sent / missed | war-band seatings |
|---|---|---|---|---|
| seed 7, main on (51916e) | 1 (human_kenku, by a shared border, 2 times) | 2 | - | - |
| seed 7, branch (cbf74f) | 1 (human_kenku, the same) | 2 | 0 / 74 | 13 |
| seed 7, branch, CAMPAIGN_KM 1000 (2b4817, test arm) | 2 (orc_human 6 times, human_kenku 13) | 19 | 18 / 56 | 13 |
| seed 10, main on (70cf9f) | 0 | 0 | - | - |
| seed 10, branch (4bd35e) | 0 | 0 | 0 / 94 | 90 |

Why still mostly "it didn't" under option A: one more state's reach is about 150 foot-km, and the nearest victim polities lay
287 (human_kenku), 374 (leonin_human), 843 (orc_human), 5,802 (hob_elf) and 6,795 (elf_orc) foot-km away on seed 7 (cbf74f's
unbounded why-not). On seed 10 only dwarf_hob had a victim within the 4-budget bound (461 foot-km). The others lay beyond 600 to
1,200. dwarf_hob on seed 7 never had a dwarf state (`state 0`), This is
PW-1478's open question (D56); the evidence is now on that ticket.

## 3. Fates by the winner's tolerance

The tolerance and aggression are the winner's at the conquest (`winner_att`). Main has no attitudes; its fates read the enmity alone.

| run | winner tolerance | kept | thinned | expelled | heads lost |
|---|---|---|---|---|---|
| seed 7, main (51916e) | (no attitudes) | 152 | 11 | 0 | 19,571 |
| seed 7, branch (cbf74f) | >= 0.6 | 118 | 0 | 0 | 0 |
| | 0.4-0.6 | 41 | 2 | 0 | 2,356 |
| | < 0.4 | 3 | 2 | 1 | 389 |
| seed 10, main (70cf9f) | (no attitudes) | 25 | 7 | 0 | 24,865 |
| seed 10, branch (4bd35e) | >= 0.6 | 33 | 0 | 0 | 0 |
| | 0.4-0.6 | 4 | 2 | 0 | 18,739 |
| | < 0.4 | 0 | 3 | 0 | 25,705 |

- **Does a tolerant winner keep?** Yes, on both seeds: no winner of tolerance 0.6 or more thinned or expelled anyone.
- **Does an aggressive, intolerant one raze?** Hardly. On seed 7 the one expulsion was by the firbolgs (tolerance 0.33, aggression 0.0),
  so its cut was almost nothing (28 heads). On seed 10 the orcs 500 years ago were intolerant and aggressive (0.36, 0.60). They
  thinned the leonins and hobgoblins they took (23,071 heads) and expelled no one, because the tree's orcs bear those peoples little
  old enmity. In any era the model can now make a Cyrus. It makes a Genghis Khan only when an intolerant people wins against one it
  already hates.
- **Why winners are mostly tolerant.** The winners on seed 7 were humans (40 conquests, tolerance median 0.76), hobgoblins (25, 0.57),
  orcs (13, 0.69), tabaxi (13, 0.92) and halflings (5, 0.83). Humans and tabaxi start tolerant (0.72, 0.78, `attitudes.temperament`).
  The orcs start at 0.5 and drift up: contact up to +0.05, ruling many peoples +0.05, plus their own offset and drift (SD 0.1 each).
  With TOL_X = 2 a winner of 0.76 takes 0.52 off every harshness. Whether that is right is a judgement for Daniel, not a fix
  (inbox draft `draft-live-conquerors-rarely-harsh.md`: keep; TOL_X 1; or let aggression raise the harshness too).
- Seed 10 lost more heads than main because its harsher winners met larger peoples on the land they took. The count of harsh fates
  fell (5 against 7).

## 4. The expedition's range (PW-1478, D56): a test arm

CAMPAIGN_KM = 1000 on seed 7 (run 2b4817, set only in the arm's process by `live_run.py`; the default stays None). Against the same
branch on option A (cbf74f):
- rows that took land 2 of 6 (against 1). orc_human took land 6 times; its six expeditions went 385-2,414 km on the map (a km ridden or on a road costs less than a foot-km).
  human_kenku took land 13 times, by 11 expeditions (the first six went 607-811 km). leonin_human sent one expedition (509 km) and lost the war. hob_elf
  and elf_orc still reached no victim within the bound (their victims lie beyond 4,000-5,200 foot-km). dwarf_hob had no dwarf state;
- invasions 19 against 2; wars 96 against 98; live states now 87 against 84; shares within 0.1 point; writing dates the same;
- fates: kept 201, thinned 4, expelled 1, the same harsh fates as cbf74f (the extra conquests were all by tolerant winners);
- live step 40.3 s (the expeditions themselves cost more at a 1,000 foot-km budget).

This is on PW-1478's ticket as an update.

## 5. Not destabilised (against main on, same world and seed)

| | seed 7 main (51916e) | seed 7 branch (cbf74f) | seed 10 main (70cf9f) | seed 10 branch (4bd35e) |
|---|---|---|---|---|
| wars (conquests not by a row) | 96 | 98 | 40 | 48 |
| states 2,000 / 1,000 / 500 / 0 years ago | 38 / 58 / 71 / 84 | 39 / 59 / 72 / 84 | 0 / 0 / 27 / 125 | 4 / 6 / 31 / 125 |
| live polities (records) | 3,022 | 3,032 | 2,583 | 2,679 |
| shares, largest four (%) | human 41.1, hobgoblin 13.4, halfling 9.0, orc 8.7 | 41.1, 13.4, 9.0, 8.7 | human 62.7, halfling 12.3, hobgoblin 5.2, elf 4.7 | 62.7, 12.3, 5.2, 4.7 |
| first writing / kingship / law / cities (kyr ago) | 4.305 / 2.698 / 2.024 / 3.597 | the same | 1.753 / 3.229 / never / 3.47 | the same |
| writing, each people | | identical (28 peoples) | | identical (15 peoples) |

Seed 10's early states are the war bands: a strong row's invaders seated a state at their largest town (section 2).

**Seven Meals, tree seed 7 (frozen tree: measured only, nothing tuned).** Main on (run 0ea92b) against the branch (run 647e2f), with
its own six rows:
- rows that took land 4 of 6 on both. The branch took land more often: ant_human 43 times against 40, human_tabaxi 15 against 8 (7
  expeditions of 122-560 km), elf_orc 4 against 2. Invasions 110 against 97, wars 411 against 402;
- states 0 years ago 209 against 219 (3,000 to 1,000 years ago the same: 98, 170, 188); shares within 0.1 point (human 39.8 against
  39.9, half_orc 22.5, antelope_folk 18.5); writing, kingship, law and cities identical for every people;
- fates: winners of tolerance 0.6 or more kept all 1,107. Winners under 0.4 thinned 34 of 64 (906,832 heads). In all the branch lost
  977,787 heads to conquest against 606,663 on main (kept 1,658, thinned 44, expelled 0; main kept 1,545, thinned 54, expelled 4). So
  on this tree the intolerant winners are harsher than main's placeholder, and the tolerant ones gentler;
- live step 26.1 s against 5.8 s.

## 6. Cost

The live step is `made_s` in `polities_live.json` (the live polities' own time, the tech tree apart).

| run | live step s | run's history s (generated_in_s) |
|---|---|---|
| seed 7 main (51916e) | 4.0 | 1,162 |
| seed 7 lane 201, unbounded why-not (cbf74f) | 108.7 | 1,245 |
| SEE6 | | |
| seed 7 CAMPAIGN_KM 1000, bounded (2b4817) | 40.3 | 1,289 |
| seed 10 main (70cf9f) | 3.2 | 1,135 |
| seed 10 bounded (4bd35e) | 15.5 | 1,240 |

What is left over main is the expeditions themselves, plus the bounded why-not (up to 4 budgets' search on each miss). Each century
a strong row whose invaders border no victim runs one Dijkstra per invader state. The whole-run times were measured on a shared
machine, so they vary by tens of seconds between runs of the same code.

## 7. Switch off: byte-identical to main

As rounds 8 and 9: world 4360a3 (L6), dnd, one try, tree seed 7, switch off and no rows, in the scratch data root. Old code: a `git
archive` of 01b03c34 (main); run 62e373. New code: this branch with lane 201b's bound; run 81ede2. Both runs have the same 102 files.
99 of them are byte-identical once the run ids, the runs' names and the code's path are swapped for placeholders
(`round9/samefiles.py`, which now takes the names as arguments; output `round10/offcheck.txt`). The other three differ only in timings
(`generated_in_s` in `run.json` and `gods.json`, the times in `run.txt`), the creation stamp and the code's own source hash and dirty
flag (`round9/jsondiff.py`, output `round10/offcheck_json.txt`).

## 8. Robustness suite, switch on

SEE8

## 9. Tests

SEE9

## Status

SEE10
