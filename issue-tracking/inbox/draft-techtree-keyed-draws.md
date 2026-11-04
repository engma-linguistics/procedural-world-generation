---
title: The tech tree reshuffles when the history is nudged; key its draws per people and tech, not one shared stream
type: task
status: todo
parent: null
milestone: later
subsystem: culture
effort: s
impact: high
found_by: lane180
blocked_by: []
relates: [PW-1280, PW-1434]
refs: [planet/lineages/techtree.py::build, planet/lineages/polities.py::draw, docs/review/culture/polities/round5.md, docs/review/peoples/ledger/round1.md]
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
- [ ] keyed draws in techtree.build; goldens updated on purpose
- [ ] nudge check re-run: the same people hold the largest states at 1,000 years ago and at the present, on 2 seeds
