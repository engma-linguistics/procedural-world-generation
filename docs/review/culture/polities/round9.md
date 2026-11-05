# Polities round 9: why writing came late inside the history (PW-1473), and the town arms from the live seats (PW-1472; lanes 195-196)

## In plain words

- **The problem.** With polities in the history switched on (off by default), the tech tree runs inside the history (round 8). On
  world 899985, seed 7, it gave writing about 2,000 years later than the tree built after the same history, or never: the humans
  never wrote (after-run tree: 2,511 years ago), and the live states only began about 600 years ago.
- **The cause.** When two peoples first meet, their shared border is short; it grows as they spread into each other. The live tree
  timed each spreading "front" of know-how from the median border *so far*, which early in a contact is short, and it never
  re-timed it. The after-run tree uses the median over the whole run, which is longer. Where the border is under 1,500 km (the
  length that counts in full) a shorter border means a slower front. Those small delays added up down a chain of peoples. On seed 7
  the clay tokens reached the gnomes 250 years later. That was enough for the gnomes to miss inventing proto-writing and writing,
  and in this world the gnomes were the first to write: they then wrote 665 years ago instead of 4,305.
- **The fix (a mechanism, not a fudge).** The live tree now reads the border two peoples share *now*. A front still on its way is
  re-timed each time the history stores a frame: if the border has grown, the front speeds up; it never slows down (the front keeps
  the ground it has crossed). The D52 arms already worked this way. Only `history/tech_live.py` changed; the after-run tree is not
  touched.
- **The result.** Seed 7: writing for all 12 of the largest peoples now falls within the spread of 12 draws of the after-run tree
  on the same history (before: 1 of 12). Live states now 84 (before: 36), the first about 2,400 years ago (before: 600). Seed 10:
  7 of 12. That draw of the tree's luck is itself a late one: the after-run tree's own date for the humans is the latest of its 12
  draws. Over 12 draws, the fixed live tree and the after-run tree agree on the median date of the first writing (section 3).
- **Town arms (PW-1472).** D52's town arms B and E need to know where each people's towns are. Inside the history there is no
  settlement ledger yet, so they now read the live polities' own central places of town size. Arm E switched on as a test: writing
  came earlier for 20 of the 28 peoples that write, and no "needs a town footprint" warning fired. Nothing is switched on by
  default (D53 is still Daniel's call).
- **Switch off:** a run is still byte-identical to main (section 6).

## 1. Finding the first divergence

Lane 195 left an instrumented switch-on run (899985 L7, dnd, tree seed 7, so the tree's draw seed is 7000; run 89f217 in a scratch
data root, on the code of main at 3673d338). Its log kept, for each front of the watched techs, the border, the taker's area and
the giver's date the live tree used, and the goods each people held at every feed.

**Replaying the tree with one input at a time as the live tree saw it.** `round9/emulate.py` rebuilds the tree of the stored run step by
step. Each input is either the whole run's (as the after-run tree reads it) or the history's as known at that step:

- km: each pair's median border so far (from the run's stored border series, 14 points per pair);
- ser: each people's population and area so far, held at the last stored frame;
- have: the goods each people held, as the live tree was fed them (lane 195's log).

Baseline: the after-run tree of the same run (`techtree.rebuild`; output `round9/replay_7000.txt`). Measures: over the 12 largest peoples and 9 techs (villages,
towns, chiefdoms, tokens, proto-writing, writing, cities, kingship, law), the median and mean |date move| in years, and the
count of dates known in one calendar only.

| inputs as the live tree saw them | against the after-run tree: median, mean, in one only | against the live calendar | writing: gnomes, humans, hobgoblins, orcs |
|---|---|---|---|
| none (the after-run tree) | 0, 0, 0 | 57, 424, 17 | 4,305, 2,511, 2,603, 2,603 |
| km | 0, 258, 17 | 0, 192, 0 | 665, never, 641, 312 |
| ser | 0, 9, 0 | 57, 429, 17 | 4,305, 2,511, 2,603, 2,603 |
| have | 0, 0, 0 | 57, 424, 17 | 4,305, 2,511, 2,603, 2,603 |
| km + ser + have | 0, 256, 17 | 0, 170, 0 | 665, never, 641, 312 |
| the live calendar | | | 665, never, 641, 312 |

The border alone reproduces the live calendar's writing exactly; the populations held at the last frame and the goods do nothing
to writing. So lane 195's ruling-out of the border was too quick. It is true that the big pairs' borders are 2-17 times
`contact_full_km` (1,500 km), so the border counts in full either way. But the chain that matters runs through short borders.

**The chain on seed 7** (`round9/fronts.py`, the after-run tree's fronts logged as lane 195's run logged the live ones;
years ago, live / after-run):

1. tabaxi to fire giants, tokens: border 1,113 / 1,444 km, so the border counts 0.74 / 0.96; the front arrives 7,202 / 7,435;
2. the fire giants know tokens 7,119 / 7,379, so the front to the gnomes (border 602 km either way) arrives 7,061 / 7,321;
3. the gnomes know tokens 6,868 / 7,119. With the ramp of their own invention starting later, the gnomes no longer invent
   proto-writing at 6,391 (they take it by contact at 4,462), and no longer invent writing at 4,305 (they invent it at 665);
4. in this draw the gnomes are the first to write (after-run: 4,305), and everyone else takes writing from them or from their
   takers. Every writer of the after-run tree is late or never in the live calendar.

The jump from a 250-year delay to a 3,600-year one is the tree's luck: each invention step has its own fixed draw, and a later
start of the ramp misses a draw the after-run tree just made. Over 12 draws the delay is a few hundred years (next section). That
sensitivity is a property of the tree itself, not of the live tree; inbox draft.

## 2. The fix and the alternatives tried

All on the seed 7 history (run 89f217), over 12 draws of the tree's luck (seeds 7000-7011, the run's own first). For each variant
of the live tree, the median over the 12 draws of the first date anyone writes, and of each people's writing date (years ago).
Baseline: the after-run tree on the same history, the same 12 draws (`round9/seeds7_summary.txt`, made by `round9/seedsum.py`).

| live tree variant | first writer | humans | halflings | elves | dragonborn | gnomes |
|---|---|---|---|---|---|---|
| after-run tree (baseline) | 3,867 | 2,604 | 2,604 | 3,007 | 2,557 | 2,424 |
| median border so far, fixed once (the old live tree) | 3,349 | 2,255 | 1,753 | 2,511 | 1,817 | 2,099 |
| border now, fixed once | 3,867 | 2,339 | 2,180 | 2,813 | 2,467 | 2,296 |
| border now, re-timed, never later (**the fix**) | 3,867 | 2,423 | 2,467 | 3,007 | 2,557 | 2,424 |
| peak border so far | 3,867 | 2,560 | 2,267 | 2,813 | 2,467 | 2,337 |
| peak border so far, re-timed | 3,867 | 2,747 | 2,604 | 3,007 | 2,654 | 2,470 |

On the run's own draw (7000), against the after-run tree: the fix moves dates by a mean of 47 years (the old live tree: 258), with
1 date known in one only (the old: 17). The peak border overshoots on this draw (mean 239 years, hobgoblin writing 3,865 against
2,603) because a border that once spiked keeps counting at its peak. Median so far plus re-timing alone did not help on this draw
(gnome writing still 665): by the time the median has grown, the front from the tabaxi has already arrived late.

**What the fix is** (`history/tech_live.py`):

- `LiveTech._links`: a pair's border is the one it shares at its last stored touch, not the median so far.
- `LiveTech._retime`, after each feed (once per stored frame): every plain front not yet arrived, whose pair is in touch and whose
  taker has not taken the tech, gets the arrival advance would give it at today's rate (the taker's area now, the border now, the
  same keyed delay). It keeps the new date only if it is earlier. A front whose rate was 0 when it was fixed (a border of 0, so it
  never arrives) is timed once the border opens. D52's arm-touched fronts are left to advance, which already re-times them each
  step the same way; language to a people under no sapiens node still never arrives.
- `tests/test_techtree.py::test_a_live_front_speeds_up_as_the_border_grows_and_never_slows`: the same border leaves a front where
  advance put it (the rate is the same expression), a longer one brings it earlier, a shorter one never makes it later.

## 3. Results (899985 L7, dnd, one try, polities in the history on; scratch runs)

Baseline for every row: the after-run tree of the same run (`techtree.rebuild`), its own draw and 12 draws (the run's own seed
and the next 11) for the spread. "In the spread": the live date lies within the 12 draws' earliest and latest dates (`round9/check.py`; outputs `round9/check_<run>.txt`).

**Seed 7 (draw 7000)**: the old live tree (run 89f217, lane 195) and the fixed one (run c19b5c). The two histories differ a little
(the live polities act on the history, so a different calendar makes a slightly different history: 782 and 783 contact pairs), but their after-run trees give the same dates below.

| people | writing: old live / fixed live / after-run | 12 draws: earliest-median-latest |
|---|---|---|
| humans | never / 2,255 / 2,511 | 952-2,604-4,462 |
| hobgoblins | 641 / 2,423 / 2,603 | 1,269-3,072-4,795 |
| halflings | never / 2,423 / 2,698 | 1,224-2,604-3,728 |
| orcs | 312 / 2,603 / 2,603 | 1,753-2,901-4,305 |
| leonin | 189 / 2,255 / 2,337 | 1,465-2,952-4,305 |
| kenku | never / 1,817 / 2,024 | 1,060-2,577-3,865 |
| tabaxi | 665 / 2,175 / 2,175 | 1,953-2,952-4,625 |
| firbolgs | never / 2,024 / 2,024 | 597-2,136-3,728 |
| bugbears | 137 / 2,899 / 2,899 | 1,691-2,952-4,006 |
| elves | never / 3,115 / 3,115 | 1,315-3,007-5,948 |
| half-orcs | never / 2,423 / 1,884 | 1,753-2,797-4,400 |
| dragonborn | never / 2,603 / 2,603 | 1,023-2,557-3,597 |

| seed 7 | old live tree | fixed live tree |
|---|---|---|
| writing in the spread (12 largest peoples) | 1 / 12 | 12 / 12 |
| kingship, law, cities in the spread | 7, 3, 8 / 12 | 12, 12, 11 / 12 |
| all 9 techs: mean date move against the after-run tree; dates in one only | 373 years later; 17 | 27 years later; 1 |
| live polities now: chiefdoms; states and empires | 577; 6 + 30 = 36 | 423; 17 + 67 = 84 |
| the first state | 600 years ago | 2,400 years ago |
| largest polity now | 0.19 Mkm2 (tabaxi) | 0.43 Mkm2 (tabaxi) |

The one date out of the spread is the half-orcs' cities: 1,465 against the 12 draws' 2,098-4,400 (after-run: 2,098).

**Seed 10 (draw 10000), fixed live tree** (run 052319). There is no old-code run on this seed. The baseline is the after-run tree
and, for the old live tree, the replay of section 1 on this history.

- Writing in the spread: 7 of 12. Kingship, law and cities: 12, 12 and 12 of 12. All 9 techs: dates move by a mean of 83 years
  later against the after-run tree, 5 in one only.
- This draw is a late one for the after-run tree too: its humans write 536 years ago, the latest of its 12 draws (536-2,567-4,795),
  and the hobgoblins 1,315 (1,181-2,758-4,305). The five out of the spread are later still: humans 301, hobgoblins 714, kenku 118
  (after-run 182), leonin 252 (1,632), bugbears 147 (1,518).
- The replay reproduces the live calendar (mean move against it 12 years). So what is left is again the border: on this draw, the
  border now is shorter than the whole run's median for some pair on the chain. The replay of the old live tree on this history
  is further off (a mean move of 486 years against the after-run tree, 10 dates in one only; the fix: 110, 5).
- Over 12 draws on this history (`round9/seeds10_summary.txt`), the median date of the first writer is 3,229 years ago for the after-run tree
  and for the fixed live tree (the old live tree: 3,117); per people, the fixed tree's medians sit 0-490 years from the after-run
  tree's, on both sides (humans 2,350 against 2,567, orcs 2,797 against 2,307).
- Live polities now: 469 chiefdoms, 75 states and 50 empires; the first state 700 years ago.

So the ticket's first check holds on seed 7 and holds in the median on seed 10, but not draw by draw on seed 10. The after-run tree
reads the whole run's median border, which a tree inside the history cannot know; on a draw where writing comes late and hangs on a
few short borders, the two can differ by up to 1,400 years for one people. I do not think the live tree should chase that. The
after-run tree is the one that reads the future here.

**Cost.** The tree inside the history took 17.8 s of a 1,492 s run (seed 7, `generated_in_s`; before: 18.9 s of 1,415 s).

## 4. Town arms from the live seats (PW-1472)

Round 8 left the tree inside the history without D52's town arms (B, E), which need each people's town cells, and the ledger that
gives them is made after the run. Now (`history/polity_live.py`, `history/tech_live.py`):

- `LivePolities.town_cells(ago)`: each people's town cells now. These are the cells whose central place (the history's own: the
  settlements' SHARE of the hinterland's farmers, at a cell that is the best of its ring, as the live seats use) is of town size
  for the stage its people knows (the settlements' TOWN_MIN by stage, as the ledger sizes a town), for peoples that know towns.
  The central places are computed by one helper, `_places`, which the seats also use.
- `LiveTech.note_towns`: each recent step adds these counts to the footprint the tree reads, in the shape the ledger's
  `techspread.town_footprint` gives ({people: (dates oldest first, town cells)}); a people seen before and not now has none now.
- With B and E off (the default) no footprint is kept and nothing changes.
- `tests/test_lineages.py::test_the_live_tree_reads_the_live_seats_as_its_town_footprint`.

**The E check** (as round 8's: arm E switched on in the tree's defaults as a test override; here with polities in the history on;
seed 7, run 8f5b77). Baseline: the same switch-on run with arms off (run c19b5c), and the after-run tree with E of the same history
(`techtree.rebuild(run, arms="E")`, which reads the ledger's town footprint).

- No "needs a town footprint" warning.
- Writing came earlier for 20 of the 28 peoples that write, the same for 7, later for 1 (half-orcs 1,465 years ago, against
  2,423; they now take it from the leonin, not the tortles). For example the humans 3,728 (arms off: 2,255) and the dwarves 3,597
  (2,698). Round 8's after-run E check on the switch-off path: earlier for 26 of 28.
- Against the after-run tree with E: writing for the 12 largest peoples within the spread of its 12 draws (12 of 12), dates move
  by a mean of 158 years later, none known in one calendar only. The live footprint (central places counted every century) is
  not the ledger's, so the two do not match date for date.
- Live states now 82 (arms off: 84), the first 2,800 years ago (arms off: 2,400).

## 5. What is not in this cut

- The after-run tree (switch off) is unchanged; it still reads the whole run's median border.
- How sensitive the tree's dates are to its luck: a 250-year shift in one front moved the world's first writing by 3,600 years
  on seed 7. Inbox draft (it touches `techtree.py`, so it goes after D55's lane).

## 6. Bit-identity with the switch off

As round 8: world 4360a3 (L6), dnd, one try, tree seed 7, in a scratch data root with copies of the world and its runs (ea33de,
cdc275). Old code: a `git archive` of 81a44075 (the main this branch merged). New code: this branch. Switch off, arms off.
Both runs have the same 102 files. 98 of them are byte-identical once the run ids and the code's path are swapped for
placeholders (`round9/samefiles.py`, output `round9/offcheck.txt`). The other four differ only in timings (`generated_in_s` in `run.json`, `gods.json` and
`taboos.json`, and the times in `run.txt`), the creation stamp and the code's own commit and source hash (`round9/jsondiff.py`).

The runs were made with `round9/live_run.py` (lane 195's instrumented one: `round9/l195_live_run.py`) in a scratch data root and
deleted after; the outputs above are kept in `round9/`.

## Status

Done: PW-1473 (the live tree's late writing: the border now and re-timed fronts, `history/tech_live.py`), PW-1472 (town arms B and E
from the live seats). Checks: seed 7 within the spread for writing, kingship and law (12 of 12) and cities (11 of 12); seed 10
within the spread in the median over 12 draws, 7 of 12 on its own draw; switch off byte-identical; live E acts without a warning.
Tests: `tests/test_techtree.py` and `tests/test_lineages.py`, not slow: 178 passed.
