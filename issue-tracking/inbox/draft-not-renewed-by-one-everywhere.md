---
title: "Languages: 'not' is renewed as 'not one' in ~40% of living lects (only one reinforcer for the Jespersen cycle)"
type: task
status: todo
parent: PW-767
milestone: v4
subsystem: peoples
effort: s
impact: med
found_by: lang-lane15
blocked_by: []
relates: [PW-1653]
refs: [planet/language/data/derivations.tsv, planet/language/lexicon.py::_compound_parts, planet/language/lexicon.py::reinforcers, "runs/a24559/languages.json (main)", "scratch pass a24559 (lane 15)"]
---

## Description
In plain words: the only row that renews 'not' is 'not + one' (derivations.tsv `reinforce ONE NOT`, after Old English
na-wiht and Latin non < ne oinom). On a24559, 242 of 622 living lects on main (279 after lane 15) say 'not' with a
compound of NOT + ONE as its last word-making step, across unrelated families. Real reinforcers vary: 'a step' (French
pas), 'a thing' (English not < na-wiht 'no thing'), 'a crumb' (mie), 'a point' (point), 'a bit', 'ever', 'nothing'
(German nicht < ni-wiht), and many languages renew by a second negator or a negative verb instead. What misleads if never
done: 'not' carries the word for 'one' in two of five languages of every family, an Earth-wide sameness a linguist spots
at once, and it feeds the WHAT = ONE / NOT = ONE homophones lane 15 had to repair (now 0 after repair, but repaired by a
renewal the sound change keeps re-creating).

Try: add reinforce rows for NOT (THING, STEP, SMALL/LITTLE piece, NOTHING-like, EVER where the concepts exist) with
weights, and a 'second negator' path (NOT + NOT) for some; check the share of lects whose NOT holds ONE drops under ~15%.
