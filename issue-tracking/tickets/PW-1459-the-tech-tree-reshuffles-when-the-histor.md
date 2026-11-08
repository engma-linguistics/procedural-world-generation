---
id: PW-1459
title: The tech tree reshuffles when the history is nudged; key its draws per people and tech, not one shared stream
type: task
status: done
parent: null
milestone: v3
subsystem: culture
effort: s
impact: high
found_by: lane180
blocked_by: []
relates: [PW-1280, PW-1434]
refs: ["planet/lineages/techtree.py::build", "planet/lineages/techtree.py::keyed", "planet/lineages/polities.py::draw", "planet/lineages/polities.py::derive", "planet/lineages/settlements.py::build", docs/review/culture/polities/round5.md, docs/review/culture/polities/round6.md, docs/review/peoples/ledger/round1.md, "tests/test_techtree.py::test_a_nudge_elsewhere_leaves_a_peoples_dates_alone", "world 899985 (time zoom fc5311) L7, dnd seeds 7 and 10 (scratch runs, deleted)"]
created: 2026-11-04
updated: 2026-11-04
---

## Description
**In plain words.** v3's nudge test ("change one wish weight, the states are recognisably the same") fails, and the cause is the
technology tree, not the peoples or the polities. Lane 180 changed the dnd tree's halfling-among-human wish weight from 0.8 to 0.9
and re-ran on world 899985 at L7 (scratch runs, seed 7). The peoples barely moved: humans went from 38.3% to 42.5% of all people,
and each of the next seven peoples moved by under 3 points. That is inside lane 176's one-try chance. But the tech tree came out very
differently. The humans never learn writing in the nudged run (base: 3,865 years ago, from the tritons), and kingship and law dates
moved by 1-2 thousand years for the hobgoblins, leonin and orcs. Polities gate chiefdoms and states on writing, kingship and law.
So human states covered 3.6 Mkm² 1,000 years ago in the base run and almost none in the nudged one, and only 3-6 of the 10 largest
states kept their people and capital.

**Why.** `techtree.build` draws everything from one random stream, `np.random.default_rng((seed, 675))`: each pair's contact front
(`rng.exponential`) and each invention test (`rng.random()`), in loop order. A small change in who meets whom, or in who can invent
what, shifts every draw after it, so every people's dates reshuffle. Polities already avoid this: `polities.draw(run, key, step,
what)` hashes its key.

**What breaks if never done.** Any nudge (a wish weight, a preset edit, a scheduled invasion in v4) redraws the whole technology
calendar. The states, empires, calendars and the brief's dates then change for reasons nobody can see. This is the north star's
"prone to exploding when nudged", and v4's done-when 5 ("the nudge test from v3 still holds") cannot pass.

**Try.** Draw each random number from a generator keyed on what it is for: (seed, pair x, y) for a contact front, and (seed, people,
tech, step) for an invention test (zlib.crc32 keys, as `polities.draw` and `counter._cull` do). Then re-run lane 180's nudge check
(round5.md section 3). The goldens will change.
- [x] keyed draws in techtree.build; goldens updated on purpose (none moved: the goldens cover sim and climate)
- [x] nudge check re-run: the same people hold the largest states at 1,000 years ago and at the present, on 2 seeds (5-8 of 10 now; see round6)

## Updates
- 2026-11-04: Lane 182: done. Tech-tree draws keyed per (seed, giver, taker) for a contact front and (seed, people, tech, step) for an invention test (`techtree.keyed`); the settlement ledger's spot and river draws keyed on slot, cell and year; polities' fall and war luck on the run's seed and the seat's cell and founding (it was the random run id and the ledger index). Same odds (anchor check, 12-seed sweep). Nudge check: the dates of peoples the nudge does not touch stay the same; top 10 states kept now 7/10, 8/10 (s7) and 5/10, 6/10 (s10), against lane 180's 3-6; same ruler now 41% and 44% (was 21% and 38%). About half of the ruled land still moves: inbox draft. docs/review/culture/polities/round6.md.
- 2026-11-04: Coordinator: v3, a slam dunk for the north star; lane 182 does it.
- 2026-11-04: Created from inbox draft draft-techtree-keyed-draws.md (found by lane180).
