# Polities round 8: the tech tree inside the history (PW-1466), and the town arms after the ledger (PW-1464; lane 192)

## In plain words

- **What this round is.** The polities that run inside the history (round 7, behind a switch that is off by default) needed to know
  which people knew chiefdoms, writing, kingship and law at each century. The tech tree that says so was only made after the
  history had finished, so they used a stand-in: every farming people got each gate on the same date (the "era proxy"), or a test
  harness lent them another run's calendar. Now the tech tree runs inside the history, a century at a time, behind the same switch.
  Each polity step reads what its own people really knew by then. At the end of the run the same calendar is written out as the
  run's tech tree, so the polities in the history and the after-run read-out read one calendar.
- **What stays the same.** The tree's rules, its steps and its luck do not change. Every draw is keyed on (seed, people, tech, step)
  (round 6, PW-1459), and the steps are the same log-spaced 361 steps, so a step run early meets the same luck as one run after the
  history. Only what the tree reads changes: the populations, contacts, tamings and goods known by then, not those of the whole run.
  With the switch off nothing changes: a run is bit for bit the same as before (section 5).
- **The town arms (PW-1464).** Two of D52's ways to speed writing, B (across a people's towns) and E (a court takes writing once the
  front reaches its nearest town), need to know where each people's towns are. The settlement ledger that says so is built from
  the tree. Now a new run builds the tree without B and E, then the ledger, then the tree with them. E never changes what the ledger
  reads, so one round settles it; B can, so it repeats up to three rounds. All of this only runs when a tree file switches B or E
  on. Nothing is switched on: D53 is still Daniel's call.

## 1. Where the tree's step goes in the history loop

The history's loop (`history/model.py::run`) calls `rule.begin_step(step)` on every step, after the starts, the animals, the crops
and the waves, and before the peoples move. That is the seam (`history/rule.py`). The stand-ins do nothing there. The live polities
(`history/polity_live.LivePolities`) now do two things there, in this order:

1. **The tree's step, every step** (deep, glacial and recent: `history/tech_live.LiveTech.step`). The tree runs its own steps down to
   the history's time (`techtree.Calendar.advance(step.ago)`). Before that it reads what the history knows at the start of the step:
   - the lines' starts and ends so far. A line not yet started is not alive in the tree;
   - when a frame has been stored since its last read: the tracks of the frames so far (the populations and ranges), the contacts so
     far (each pair's first contact and its border series so far; a pair touching at the last stored frame is still in touch), and
     the goods each people's country holds now (its range at that frame, all peoples in one matrix product);
   - the tamings so far (crops.py and animals.py record them as they happen).
2. **The polity step, recent pass only** (as round 7). Its gates read the tree: `LivePolities.knows` is the read-out's
   `knows` on the live calendar.

At the end, `output.save` feeds the tree the whole run (exactly what the after-run tree reads), runs any steps left (none: the last
history step is the present, so every step has already run) and writes it as `meta.techtree`, marked `inside_history`.

| the tree reads | after the run (switch off) | inside the history (switch on) |
|---|---|---|
| a line's start and end | its start (or its scheduled date if it never started) | its start once it has started; not alive before |
| population and range | its track, every stored frame, interpolated | its track so far; held at the last stored frame until the next (0.5 kyr in the recent pass) |
| contacts | intervals over the whole run, the border's median over the whole run | intervals and median border so far; still in touch if touching at the last frame |
| tamings | the run's record | the record so far (the same dates) |
| goods held | the present range | the range at the last stored frame |
| steps and draws | 361 log-spaced steps; keyed draws | the same steps, the same keys |

**The gates also follow D49 now.** Round 7's live seats needed writing for a chiefdom and no writing for a state. They now ask what
the read-out asks: a chiefdom needs proto-writing or writing, its own or a neighbour's (`polities.WRITING_TECHS`), and a state needs
its own people's writing (`polities.STATE_WRITING`). `CALENDAR` and `PROXY_LEV` are gone.

## 2. What stays keyed

`techtree.keyed` draws stay keyed: (seed, "front", giver, taker) for a pair's front and (seed, "invent", people, tech, step) for an
invention test, `step` the index into the same fixed steps. The steps are fixed at the tree's first step from the oldest line's
start, which is known from the history's first step (the root starts then). So a nudge to one people still leaves an unrelated
people's dates alone (PW-1459's test). A test runs the calendar in pieces and once, fed the same, and gets the same calendar
(`tests/test_techtree.py::test_the_calendar_run_in_pieces_is_the_tree_built_at_once`).

## 3. What it costs

The tree's own steps cost what they cost after the run (12-20 s on an L7 showcase run). Inside the history they are spread over its
steps. The reads add one matrix product for the goods and a pass over the contact pairs at each stored frame. Measured in section 6.

## 4. What is not in this cut

- The town arms (B, E) inside the history. The tree inside the history has no ledger, so it runs without them and says so. The live
  seats are a town footprint of the history's own. Using them would make B and E work with the switch on (inbox draft).
- The after-run tree with the switch off is unchanged. The ticket's other check, "with polities off, the calendar matches today's
  within the 12-seed spread", is measured in section 6 as the live calendar against the after-run calendar of the same history.

## 5. Bit-identity with the switch off

**The tree alone.** The old `techtree.build` (main at de3741d2) against the new one (a `Calendar` fed once), on the three showcase
runs' stored inputs (07c755, 0141d1, a2b637), arms off, E, and B+C+K: the whole tech-tree doc is identical in all nine cases, and
as fast (12-17 s each, either way).

**A whole run.** World 4360a3 (L6), dnd, one try, seed 7, in a scratch data root with copies of the world and its runs. Old code
(a `git archive` of main at de3741d2) against this branch, switch off, arms off. All 102 files of the two runs are byte-identical
once the run ids, timings and the code's own path are taken out (`run.json`, `run.txt`, the ledger, the cultures, the gods, every
layer). The stored tree is also exactly what `techtree.rebuild` makes of the run.

## 6. Results

## Status

**The town arms (PW-1464).** The same world and seed with arm E switched on in the tree's defaults (a test override, scratch run):
the stored tree is exactly `techtree.rebuild(run, arms="E")` of it, the "need a town footprint" warning did not fire, and the ledger
is byte-identical to the arms-off run's (E moves only writing, the alphabet and law, which the ledger does not read: one round).
Writing came earlier for 26 of the 28 peoples that write (for example the dwarves 3,730 years ago against 2,420 with E off).

## 6. Results (world 899985, L7, seed 7, one try, polities in the history on; scratch runs, deleted)

**Cost.** The tree inside the history took 15.9 s of a 1,279 s dnd history (1.2%), the polity step 3.9 s. The humans-only run: 0.7 s.

**The live calendar against the after-run tree of the same history** (`techtree.rebuild` of the switch-on run: the same history,
the tree built after it as with the switch off). Over the twelve largest peoples and villages, towns, chiefdoms, proto-writing,
writing, cities, kingship and law: the median date moves by 0 years, and 79 of 96 dates are known in both. But the moves are all
one way, late, and they fall on writing and what follows it:

| people | writing live / after | cities | kingship | law |
|---|---|---|---|---|
| humans | never / 2,511 | 1,817 / 3,597 | 1,023 / 1,884 | never / 952 |
| hobgoblins | 641 / 2,603 | 3,470 / 3,470 | 2,603 / 2,603 | 147 / 918 |
| orcs | 312 / 2,603 | 3,115 / 3,229 | 2,255 / 2,255 | never / 952 |
| elves | never / 3,115 | 1,363 / 2,024 | 576 / 1,181 | never / 795 |

Villages, towns, chiefdoms and proto-writing are the same or within a few centuries. So the ticket's check ("the calendar matches
today's within the 12-seed spread") **fails for writing**: in the live calendar writing arrives about 2,000 years later, or never.
The live polities follow: chiefdoms from 4,900 years ago (577 now), but the first states only about 500 years ago (36 now, largest
0.19 Mkm2, the tabaxi), against round 7's read-out of 58 states now on the same world and seed.

**Why (a hypothesis, not yet tested).** Writing spreads almost only by contact. A pair's front delay is fixed the first time the tree
looks at it (`arrive`, never later), from the border's median so far. Early in a contact the border is short, so the live tree fixes
a slow front that the after-run tree, reading the whole run's median border, does not. Inbox draft.

**Humans alone (tools/peoples_robust/trees/humans_only.toml), same world and seed, switch on.** Against the dnd tree above as the
baseline: the humans found no chiefdom, no state, and never take up writing. This is not the live tree's doing: the after-run tree
of the same history agrees, because in this draw the humans never invent huts, so never villages or towns. Over 8 draws of the tree's
luck on the same history: huts never in 3, villages and towns in 5 (towns 600 to 6,000 years ago), chiefdoms in 2 (3,300 and 9,400
years ago), proto-writing and writing in 0, so states in 0 (D49). In the dnd tree every one of those steps reached the humans by
contact (run 0141d1: huts from the orcs through their archaic ancestors, villages from the leonin, towns and chiefdoms from the
gnomes). Inbox draft (needs-decision).

## Status

Done: `techtree.Calendar` (the tree as a step function; `build` unchanged bit for bit), `history/tech_live.py` (the tree inside the
history, behind `params.POLITIES_LIVE`, off by default), the live gates on the live calendar with D49's writing rules, `CALENDAR` and
`PROXY_LEV` removed, `output._towns_first` (PW-1464). Not done: the live calendar's late writing (above); the town arms inside the
history (inbox draft).
