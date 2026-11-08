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
