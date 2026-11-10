# Where peoples begin: founding fallbacks and origins per landmass (lane 228; PW-1184, PW-888)

## In plain words
- **The three founding fixes PW-1184 asks for are already on main** (lane 83's D20 work, commit 4a01368b). A stem now ends only once
  all its children have started, including those written to die out (`_unsplit`); a stem with children still to come is kept alive in a
  refuge (`_hold_out`); and the "no room by the parent" case founds at the nearest suitable country, weighted by distance from the
  parent, not at the world's best cell. The ticket was simply never closed.
- **On the lane 77 suite (dnd and Seven Meals, base and jitter, both worlds: 24 runs) main has no real "parent gone" teleports.** The
  only two "parent gone" cases were the merfolk in Seven Meals, a sea people of a land stem: by design (PW-779) a sea child never keeps
  a land stem alive, so it is founded by the stem's last land. This lane relabels that case so the count reads 0.
- **There is still one hidden teleport,** and it matters. When a daughter's founding takes the last of a small stem's land, the stem's
  refuge is placed at the best land anywhere in the world. On world af2677 that happens in every dnd run, and it is what gives the
  leonins, goblins, hobgoblins and halflings empty country to grow into. Making the refuge stay near the stem's last land collapsed those
  four peoples to about 0.1 Mkm2 each, so this lane reverted that change and filed it as a draft with the numbers and a better fix.
- **Origins per landmass:** no landmass under 15% of the ice-free land held most peoples' origins in any of 34 tries (the PW-888 bar
  passes). But on world 4360a3 the third continent (15.5% of the land) held more than half the origins in 5 of 8 dnd seeds, because
  the mammals' root often starts there and its whole family branches off nearby. That is descent, not the landmass draw, which already
  follows the species-area rule (habitable area to the 0.3, fun lane 30). Whether to spread a family over the sea more is a judgement
  call; it is a needs-decision draft.
- **What this lane kept:** a daughter that takes the last of its stem's land now records it as the stem's last land, so a sibling
  or a sub-stem due at the same moment is founded by it instead of at the world's best cell. On af2677 (dnd, 3 base seeds) this
  narrowed the halflings' swing from 154x to 2.8x and the goblins' from 10.9x to 5.1x, and the brittle peoples fell from 8 to 4; the
  leonins' swing went from 5.6x to 9.8x (still under the 10x line). The af2677 jitters did not change (11 brittle, leonin 998x,
  halfling 547x: that swing is the hidden teleport above).

## What changed in the code
`planet/lineages/history/origins.py`:
- `_take(pk, blob, P)`: a daughter's founding take of the stem's land (D20) now keeps the stem's land as its last land
  (`_last_held`) when the take leaves the stem nothing, so a line split from it at the same step (a sibling, or a sub-stem, which the
  suite does not list) founds by it (`_origin_fallback` with `near`) rather than at the best habitat anywhere. It fired in dnd seeds 7
  and 10 on af2677.
- `_origin_split`: a sea child of a land stem that has ended is logged "by its land stem's last land (a sea people; the stem ended
  before it)", not "parent gone" (same founding; label only).

Tried and reverted: `_hold_out` looking near the stem's last land when it holds nothing (see "The hidden teleport").

## Method
- `tools/peoples_robust.py run --family base,jitter --arms now --trees dnd` and `--trees seven_meals`, both suite worlds (4360a3,
  af2677), 2 jobs x 2 threads; main's code from a copy of commit a9ee9710, the branch from a copy of the worktree.
- Origins per landmass (a lane script, `exports/lane228/origins_audit.py` in the lane worktree, not committed): each people's origin
  lat/lon mapped to its nearest grid cell; landmasses are the connected land at the present of the world's time zoom; a landmass's share
  is its share of the ice-free land. A people whose origin is now sea (a low glacial coast) counts as "-1".
- 8 seeds: the suite's seeds 7, 10, 13 plus seeds 1-5 of the stock dnd tree, each world.
- 2a7385 (named in PW-888) could not be used: its time zoom (f778ab) is no longer on disk. The two suite worlds stand in.

## Founding fallbacks (24 runs: dnd and Seven Meals, base 3 seeds + jitters, both worlds)

| case | main | this branch (kept code) |
|---|---|---|
| parent gone | 2 (merfolk, Seven Meals jitter 1, both worlds) | 0 (the 2 merfolk now labelled as founded by the stem's last land) |
| no room by the parent (near-weighted already) | 4 (dwarf 2, orc 2; dnd on af2677) | 8 (dwarf 4, orc 4; dnd on af2677) |

Runs of the kept code: dnd base and jitter on af2677 (7), Seven Meals jitters on 4360a3 (2, identical to the run with the relabel).
The other 15 were not re-run with the kept code alone: a run with the kept code plus the reverted refuge change differed from main in
only 1 of 12 runs on 4360a3 and in none of the Seven Meals runs on af2677, so they are taken as main's.

The "no room" fallback is already the nearest-habitat one PW-1184 asks for: it is a dwarf or orc whose parent's country has no
cell within 4 rings where they can live (they are mountain and cold peoples off a lowland stem), founded at the nearest such country.

## The hidden teleport (tried, reverted)
`_hold_out` keeps a stem with splits still to come alive at its lowest, but when it holds nothing at all it searches the whole world.
With the search limited to the stem's last land, all 7 dnd base/jitter runs on af2677 changed (1 of 12 on 4360a3). On af2677, dnd:

| people | seed 7: main -> near refuge (Mkm2) | seed 10: main -> near refuge (Mkm2) |
|---|---|---|
| leonin | 27.5 -> 0.11 | 39.7 -> 1.6 |
| goblin | 11.4 -> 0.10 | 12.1 -> 0.10 |
| hobgoblin | 10.8 -> 0.12 | 45.8 -> 1.6 |
| halfling | 0.55 -> 0.03 | 12.0 -> 0.03 |
| human (share of all people) | 0.002 -> 0.33 | 0.13 -> 0.32 |

The suite's swing for these looked better (af2677 jitter: leonin 998x -> 1x, brittle peoples 11 -> 7) only because they sat at the
share floor in every run. The teleport is wrong (a stem jumps continents) but load-bearing: it is where these peoples find room.
A fix that keeps the refuge near the last land and picks it by free room is drafted
(`issue-tracking/inbox/draft-stem-refuge-teleport-carries-peoples.md`).

## Lane 233: the refuge by the last land, in a free country big enough for founders (PW-1558)

Why lane 228's near refuge failed (af2677, dnd seed 7): the mammal radiation's stems live on an islet near (-2, 180). Held out by
their last land (lane 228's rule, and a first lane 233 try that picked the nearest free 3-ring pocket), the feline, goblinoid and
archaic-human stems stayed on islets, so each daughter was founded on 0.1 Mkm2 (main: 0.5-0.6, a full founders' country) and, with no
boats before the humans, never left (leonin 0 jumps, 0 crossings; range 0.06 Mkm2). Main's jump put each stem on the world's best cell
9,800-13,300 km away.

Mechanism (`dispersal._refuge_cell`): a line with no land left holds out within LAST_LAND_REACH x FOUNDER_KM (8,000 km, the reach
`_origin_fallback` already used) of its last land, in a **free country** (connected cells whose habitat less what the living peoples
take, `_rivals_here`, is of the first ARRIVAL_ROOM tier that has one) **at least one founders' country in size** (the cells within
FOUNDER_KM, what a split's founding take removes), the nearest first (exp(-d / FOUNDER_KM)). So the next daughter's take cannot empty the
stem again, and the stem lands on the nearest land where its splits to come have room. The last land is the stem's land at the start of
the step, else `_last_held` (set by `_take`). No constant was added beyond naming the existing 20 x FOUNDER_KM reach.

Suite (tools/peoples_robust.py, arm now, af2677 dnd: base seeds 7/10/13 and jitters 1-4; main = 1cffe90c, same seeds):

| measure | main | lane 233 |
|---|---|---|
| empty-stem refuges, distance from last land (median, max) | base 9,795 / 13,426 km (9 of 10 over 8,000); jitter 9,901 / 13,532 | base 3,280 / 5,592 (0 over 8,000); jitter 1,876 / 2,779 |
| brittle peoples (swing > 10x or dead), base / jitter | 3 / 9 | 4 / 4 |
| swing base: leonin, goblin, hobgoblin, halfling, human | 9.8, 5.1, 7.8, 2.8, 1.4 | 13.8, 1.4, 1.3, 1.7, 2.1 |
| swing jitter: leonin, goblin, hobgoblin, halfling, human | 998, 2.0, 3,140, 547, 14.1 | 84, 1.9, 1,900, 524, 7.2 |
| range median, base (Mkm2): leonin, goblin, hobgoblin, halfling | 27.8, 10.4, 11.2, 32.9 | 5.5, 4.7, 47.5, 7.6 |
| range median, jitter: leonin, goblin, hobgoblin, halfling | 13.5, 8.4, 24.1, 0.70 | 2.6, 3.8, 44.2, 2.9 |
| humans' share of all people, base / jitter | 0.16-0.21 / 0.01-0.19 | 0.06-0.13 / 0.05-0.37 |
| founding fallbacks (all lines): parent gone / no room, base; jitter | 2 / 12; 0 / 7 | 2 / 12; 0 / 7 |
| top people's share (any run) | at most 0.31 | at most 0.37 (hobgoblins lead 5 of 7) |

Reading: the jump is gone (every refuge within 5,600 km, the bar's 8,000), the jitter brittle count falls 9 -> 4 and the four peoples'
founding no longer depends on where a teleport lands, but their ranges are smaller than main's (main's came from the jump to an empty
continent), so the ticket's "not below main's median" range bar is not met for leonin, goblin and halfling (decision draft
`draft-stem-refuge-range-bar.md`). Still brittle: leonin (two jitters at 0.11 Mkm2, and its share swings 13.8x on the base seeds with a
steady 4.9-5.8 Mkm2 range), halfling (one jitter at 0.05), hobgoblin and bugbear in one jitter each. PW-1184's remaining bar (swing of leonin, goblin, halfling on the
dnd jitters narrowing) narrows for leonin (998 -> 84) and goblin (2.0 -> 1.9) but not for halfling (547 -> 524): not met.
4360a3 was not re-run (load 55-100 from other sessions all night; lane 228 saw 1 of 12 runs change there).

## Brittle peoples' swing on main (share max / min across runs, floor 1e-4)

| world, family, tree | leonin | goblin | halfling | brittle peoples (swing > 10x or dead) |
|---|---|---|---|---|
| 4360a3 base dnd | 13.7x | 9.6x | 4.3x | 6 |
| 4360a3 jitter dnd | 6.6x | 6.5x | 5.0x | 6 |
| af2677 base dnd | 5.6x | 10.9x | 154x | 8 |
| af2677 jitter dnd | 998x | 2.0x | 547x | 11 |
| 4360a3 base Seven Meals | 9.5x | 4.4x | 18.8x | 6 |
| af2677 base Seven Meals | 18.9x | 9.8x | 1.8x | 4 |

With the kept code, af2677 base dnd: leonin 9.8x, goblin 5.1x, halfling 2.8x, brittle 4 (worst: drow 45x, dwarf 39x, firbolg
13x); af2677 jitter dnd unchanged. The jitter swing of the halflings and leonins on af2677 comes from the teleport above (whether the
stem's refuge lands on roomy land), not from a founding fallback.

## Origins per landmass
Landmasses as a share of the ice-free land at the present. 4360a3: 29.0%, 22.3%, 15.5%, then small ones. af2677: 48.7%, 20.8%,
12.5%, 9.2%, 7.3%, then islets.

**dnd, 8 seeds** (peoples of 23 whose origin lies on the landmass that holds the most):

| seed | 4360a3 | af2677 |
|---|---|---|
| 1 | 15.5%: 12 | 9.2%: 6 (48.7%: 5) |
| 2 | 15.5%: 12 | 48.7%: 9 |
| 3 | 15.5%: 7 | 48.7%: 9 |
| 4 | 15.5%: 13 | 48.7%: 8 |
| 5 | 15.5%: 15 | 48.7%: 8 |
| 7 | 22.3%: 11 | 48.7%: 18 |
| 10 | 15.5%: 11 | 48.7%: 9 |
| 13 | 15.5%: 12 | 48.7%: 10 |

(Seeds 1-5 were run with the refuge change later reverted. It changed 1 of 12 runs on 4360a3, so its column stands for main; on
af2677 it moved peoples off the big landmass, so seeds 1-5 there are not main's: main's seeds 7, 10, 13 had 18, 9 and 10.)

**Seven Meals (main), base seeds 7/10/13 and jitters 1-2:** 4360a3: 15.5%: 11, 22.3%: 12, 22.3%: 12, 15.5%: 12, 15.5%: 14 (of 22);
af2677: the 48.7% landmass holds 14-16 of 21-22 in every try.

Reading: no landmass under 15% holds most peoples in any try. On af2677 the largest landmass holds most, as the species-area rule
would have it. On 4360a3 the 15.5% continent holds over half in 5 of 8 dnd seeds and 2 of 5 Seven Meals tries. The cause is the
mammals' root starting there: every split is founded inside or beside its parent's range (cut-off parts weighted 3x), and the
across-sea branch rarely wins, so the dwarves, orcs, goblinoids, felines, humans and halflings all begin where the root did. The owner
ruled on 10-27 that related peoples clustering near their ancestor is fine before boats; a sourced over-sea founder rate for splits is
the candidate if he wants more spread (`issue-tracking/inbox/draft-radiation-crowds-one-continent.md`). No mechanism was added here:
the landmass draw already uses a species-area exponent, and the crowding comes from descent.

## Tests
`tests/test_lineages.py` and `tests/test_peoples_robust.py` (area) and the not-slow suite, NUMBA_NUM_THREADS=4, -n 2, on the final code.

## Lane 269: the 1 Mkm2 floor (PW-1558, owner D71 B)

### Diagnosis (written before the code change; main 673436c0, af2677, arm now)
On main, 4 of the 17 dnd runs of the suite (base 3, jitter 4, portal 4, knob 6) leave one of the four peoples under 1 Mkm2:
jitter 2 hobgoblin 0.14, jitter 3 leonin 0.11, jitter 4 leonin 0.11 and halfling 0.05. Each was *founded* on 1-9 cells
(found 0.012-0.10 Mkm2; in the passing runs 0.11-0.71). A probe of the three runs (each traced line's range, its landmass, the
good cells next to it and how many another people holds, every ~5 kyr) shows one cause, and it is not the refuge:

- The mammal radiation starts on an islet of 0.10-0.16 Mkm2 near (0, 178). A stem founded there "at the edge of its parent's
  range" (feline in jitters 3 and 4, greater goblinoid in jitter 2, archaic humans in jitter 4) holds 3-14 cells of it for
  0.3-6 Myr: every good cell next to it is held by a sibling (good cells next door 1-8, all taken), it has no boats and no
  jump reaches land (0 jumps, 0 crossings). It never holds fewer than 3 cells, so `_hold_out` never fires: lane 233's refuge
  is not involved. (In jitter 2 the refuge did fire for the goblinoid, which moved to a 20 Mkm2 continent; the goblins there
  are fine at 2.1 Mkm2. The greater goblinoid, split off just before onto the same islet, stayed.)
- Its daughter is then founded by the usual split rule (inside, at the edge of, or beside the parent's range), which on that
  islet is the islet itself or a 1-2 cell rock next to it: leonin "beside the parent's range" on 1 cell (jitter 4) or 7 cells
  (jitter 3); hobgoblin at the edge, 8 cells; halfling beside, 2 cells. It too has no way off before boats, so it stays at
  0.05-0.14 Mkm2 to the present (leonin jitter 4: 1-3 cells for 1.4 Myr; crossings come only in the last 30 kyr).
- So: not a refuge too small, not a failure to re-expand after a hold-out, and not rivals around a refuge. It is the
  founders' country rule: a split is founded where its parent is, even when the country there cannot hold a founders'
  country. Lane 233 already required a held-out stem's refuge to be a free country at least one founders' country in size;
  a split born beside a stranded stem had no such check.

### Mechanism (lane 269)
`origins._origin_split`: before a land split is founded, `_founders_room` asks whether the landmass under the chosen cell
holds at least one founders' country (`_founders_cells`: the cells within FOUNDER_KM, the size lane 233's refuge already
requires) of country the daughter can live in (K > 2 EST), anywhere on it. If not (an islet, or an island with little of its
habitat), the founders arise at `_refuge_cell(line, K, parent's range)`: the nearest free country of founders' size within
LAST_LAND_REACH x FOUNDER_KM of the parent's range: the same choice as a stem with no land, so no new constant. Origin
reason: "no founders' country on the parent's islet: the nearest free country". `_refuge_cell`'s reach is now also checked in
great-circle km (`_km_from`): counted in grid steps it let a fire-giant refuge land 8,180 km out (grid steps are longer than
cell_km in places).

First try (landmass size only, without the habitat count), partial suite (af2677 arm now; main = 673436c0, same seeds):
base s7/s10/s13 and jitters 1-3 all changed (the mammal islet sits in every dnd run: feline, hominid and goblinoid are now
founded 1,570-1,700 km off it); Seven Meals runs identical to main. Leonin 4.9-5.8 -> 19-29 Mkm2 on the base seeds and
jitters 1 and 3, but jitter 2's leonin fell 5.2 -> 0.51 (founded on an island of more than a founders' country of land
but only ~0.5 Mkm2 of its grassland, no boats). Hence the habitat count. The full suite on the final rule is still to run.

### Full suite (lane 269b; branch = c6907d5b merged with main 31c3b00d; baseline = main 673436c0)
Main 31c3b00d has no change under planet/, tools/ or tests/ since 673436c0, so the 673436c0 suite is the baseline (af2677, arm
now, 22 runs: dnd base 3 + jitter 4 + knob 6 + sites 4, Seven Meals base 3 + jitter 2; 2 jobs x 4 threads).

| people | main min (run) | main median | main runs < 1 | branch min (run) | branch median | branch runs < 1 |
|---|---|---|---|---|---|---|
| leonin | 0.11 (dnd-j3) | 4.93 | 2 | 0.51 (dnd-j2) | 21.6 | 1 |
| goblin | 2.13 (dnd-j2) | 4.13 | 0 | 1.91 (dnd-j3) | 2.43 | 0 |
| hobgoblin | 0.14 (dnd-j2) | 46.8 | 1 | 24.6 (dnd-dwarfx2-s7) | 44.2 | 0 |
| halfling | 0.05 (dnd-j4) | 7.66 | 1 | 0.46 (dnd-bugbearx0.5-s7) | 5.06 | 4 |
| tabaxi | 0.10 (dnd-bugbearx0.5-s7) | 0.12 | 17 | 7.24 (sm-s10) | 8.10 | 0 |
| goliath | 0.10 (sm-j1) | 8.09 | 5 | 0.10 (sm-j1) | 0.70 | 17 |
| firbolg | 1.17 (dnd-j3) | 10.8 | 0 | 0.86 (dnd-j2) | 1.47 | 3 |
| bugbear | 0.03 (dnd-j2) | 8.25 | 4 | 0.40 (dnd-s10) | 4.35 | 3 |
| gnome | 0.51 (dnd-sites1-s10) | 12.4 | 1 | 1.32 (sm-j1) | 14.6 | 0 |
| kobold | 0.51 (sm-s7) | 19.7 | 1 | 0.50 (dnd-j1) | 16.5 | 2 |
| human | 20.8 (dnd-j4) | 23.7 | 0 | 21.0 (sm-s13) | 39.4 | 0 |
| aarakocra | 1.08 (dnd-j3) | 3.99 | 0 | 1.22 (dnd-j1) | 15.3 | 0 |
| tortle | 1.99 (dnd-j2) | 4.21 | 0 | 1.56 (dnd-bugbearx2-s7) | 2.23 | 0 |
| lizardfolk | 14.2 (dnd-sites3-s7) | 24.7 | 0 | 5.80 (dnd-j3) | 22.0 | 0 |
| drow | 0.04 (dnd-sites1-s7) | 0.75 | 17 | 0.04 (dnd-sites1-s7) | 0.75 | 17 |
| troglodyte | 0 (extinct, all 17 dnd) | 0 | 17 | 0 (extinct, all 17 dnd) | 0 | 17 |

(Mkm2 at the present. Unchanged or above 1 everywhere on both: dwarf (one run at 0.40, sm-s13, both), elf (2 runs, 0.24, sm-s13, both),
half_orc (never founded in sm-j1, both), dragonborn, kenku, orc, the Seven Meals-only peoples. Sea peoples (sea_elf, triton) are not
land peoples.)

- **Seven Meals: identical** to main in all 5 runs (every people's area and share).
- **Brittle (dnd, base + jitter): 7 -> 5**; worst swing 2,210x (hobgoblin) -> 110x (bugbear); worst within one family 2,170x ->
  50x (drow). Seven Meals 6 -> 6, unchanged.
- **Refuge and founder picks:** 53 picks, median 1,629 km, farthest 7,911 km (fire_giant, dnd-j3); the split founders' picks
  (feline, hominid, goblinoid, once kobold) 1,415-2,020 km. The run's own refuge log (distance from the stem's last land) puts that
  fire-giant refuge at 8,041 km: it measures from a different mask than the pick (the last land on record, not the range passed
  in), 41 km over.

**The floor is not met.** The islet stranding is gone (tabaxi, hobgoblin, leonin jitter 3/4, halfling jitter 4 founded off the islet;
the stems are founded 1,400-2,000 km away), but 34 people-runs of land peoples other than drow and troglodytes still end under 1
Mkm2 (main: 36, of which 17 tabaxi), and goliaths now do so in every dnd run (5 -> 17 of 22).

### Why the rest fall short (written before any further change; probes of dnd-s7, dnd-j2, dnd-j4, sm-s7 on the branch)
- The remaining small peoples are not on islets. Goliath (s7, 0.93), leonin (j2, 0.51), halfling (j4, 0.54), firbolg (j1/j2,
  0.86) are each founded on the 20 Mkm2 continent that the moved hominid, feline and goblinoid stems now share, 175-540 kyr ago, on
  8-43 cells, and every good cell next to them is held by another people for the rest of the run (good cells next door 12-129, all
  taken; habitat on the landmass that no other people holds: 0-4 cells). They sit at 0.5-0.9 Mkm2: the refuge floor the history
  stops pushing a losing people back at (PW-1182, ~0.5 Mkm2), not the founding rule.
- No landmass count at the founding step separates them from splits that thrive: at each land split of dnd-j4 and sm-s7 the
  landmass's habitat, its free room by the rivals' load (at 50%, 20% or any of the best K), the parent's own patch, or the cells
  no other people holds, are as low for hobgoblins (44 Mkm2 at the end), dwarves or orcs as for goliaths or halflings (e.g.
  hobgoblin: parent's patch 0, unheld 0; goliath: 22 and 0). A stricter founding check would move thriving peoples too (and Seven
  Meals, which is now untouched).
- Goliaths and firbolgs got worse because the hominid stem now starts beside the continent where humans grow (human median 23.7 ->
  39.4 Mkm2): giantkin's later daughters are born into that crowd; on main they started on the far continent (28 N, 43 W) and grew.
- So D71's 1 Mkm2 sits above the history's own loser floor (~0.5 Mkm2, PW-1182). The founding change cannot carry it; the floor
  needs PW-1182's mechanism (a losing people finds a niche of its own, or is pushed to ~1 Mkm2 rather than ~0.5) or a ruling.

## Lane 269c: the goliath regression and PW-1182 (losers at the refuge floor)

### Diagnosis (written before the sweep; probes of the lane 269b branch c6907d5b+main 31c3b00d, af2677, arm now)
Two lane probes (scratch, not committed): `probe_pin.py` records, for each land people at the last step (ago <= 1 kyr), the cells
where it has room of its own (room = K less its rivals' load, as `_compete` computes it, >= 0.3 with K >= 0.3) split by on its
landmass / within its jump reach / anywhere, and held by another people or free; `probe_patch.py` records, at each land split, the
connected patch of the daughter's habitat (K > 2 EST) at the founding cell, against a founders' country (37 cells at L6).

- **Goliath and firbolg** (dnd-s7: goliath 0.93, firbolg 1.44 Mkm2; main 12.4 and 11.1): on main the giantkin stem was founded "no
  room for it by the parent: nearest habitat", on the cold northern continent (goliath origin 28 N, 43 W). On the branch the hominid
  stem moves off the islet at once (lane 269's rule) onto the tropical continent, and the giantkin (cold, mountain) arises at the edge
  of its range on a highland patch of its habitat of **18 cells** (s7; 52 in dnd-j4), under one founders' country. Goliath is then
  founded on a 46-48 cell patch (an "isolated part of the parent's range" at 9-29 S) and fills it: 0.5-0.9 Mkm2. A sky-island endemic.
  Firbolg's patch is large (891-986 cells) but only 344-378 of them are free of rivals; it ends at 1.4-1.5.
- **The same patch shape** explains the other small founders: halfling dnd-j4 (26-cell patch, 0 free: 0.54 Mkm2), dwarf dnd-s7 (2
  cells: 1.98), leonin (1 cell, but a nomad: it thrives at 21-25). The lane 269 check reads the whole landmass's habitat, so a
  daughter whose own patch by its parent is a sliver of a big landmass passes it.
- **Losers pinned at the floor have no own room on their landmass** (dnd-s7, at the present): goliath 23 cells with room >= 0.3 on
  its landmass (all held by others), firbolg 2, goblin 10, bugbear 26, dwarf 5, each 0 free; but within their jump reach (mostly
  over the sea) 345-1,103 such cells held by others and 0-24 free. Their ring (the cells next to their range) has 0 good cells, so
  they are hemmed in, but a jump founds only on land no people holds (`_jump`: "a jump founds new country, not a mixed one"), and
  a crowded continent has none. So specialisation into habitat the winners do not use (option 1) has almost nothing to work with on
  their own landmass; the room is over the sea, among other peoples.

Candidates:
- **G (founding, PW-1558):** lane 269's founders' room check on the daughter's own habitat patch at the founding cell, not the
  whole landmass: a split whose patch by its parent cannot hold one founders' country arises at the nearest free country that can
  (`_refuge_cell`, as now). No new constant: the same founders' country. Variant **GF**: the patch counted on its free part (habitat
  less the rivals' load, `_rivals_here`), the same free country `_refuge_cell` asks for.
- **A (PW-1182 option A):** a line held at the refuge floor (range under 2 x REFUGE_MKM2, where `_compete`'s displacement is slowed
  by the floor) jumps to where it has room of its own, held by others or not (`_jump` drops the "free land only" filter for it).
  No new constant; the jump rate and kernel are unchanged.
- Rejected: raising REFUGE_MKM2 or FOUNDER_KM to 1 Mkm2 (a clamp that meets the bar by fiat, and does nothing for a people that never
  grew past its founding patch, which is the goliath case); a per-people habitat or rate.
