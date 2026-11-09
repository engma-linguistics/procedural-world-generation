---
title: "Languages: on the second world (de1cc6) current code fails three checks a24559 passes: sisters 0.47, overused ⁿt/ᵑk, pronoun loans 0.10"
type: task
status: todo
parent: PW-767
subsystem: culture
effort: m
impact: med
found_by: language lane 9 (PW-1566 second seed)
blocked_by: []
relates: [PW-1566, PW-1537]
refs: [planet/language/checks.py, "planet/language/checks.py::living_sizes", "run de1cc6", docs/review/language/calibration.md]
---

## Description
In plain words: the language checks are tuned on one world (a24559). Lane 9 ran the full language pass on the second
world, de1cc6, with main's code (41c71b12) and with lane 9's code, to confirm the raised-e fix. Both fail three checks
that a24559 passes, so these failures come from the world, not from lane 9:

| check | stored de1cc6 (11-08 code) | main 41c71b12 | lane 9 | pass mark |
| --- | --- | --- | --- | --- |
| sisters recognisable (strict) | 0.537 | 0.474 | 0.488 | > 0.5 |
| overused segments | ᵑk 20%, c̟ 14%, ʁ 12%, ⁿt 11% | ɖ 24%, ⁿt 10% | ⁿt 12.5%, ᵑk 11% | none over 10% and 3x PHOIBLE |
| WOLD pronoun loans | 0.095 | 0.103 | 0.092 | cap 0.08 |
| inventory sizes (human-voiced vowel median) | 7 | 7 | 6 (edge; 6.5 on a first lane-9 pass) | within 2 of 9 |

(The second-voice check also failed on lane 9's first de1cc6 pass, from stone giants who took up an aarakocra language;
fixed in lane 9: a sound a people cannot make at all is nativised in every word.)

**What misleads if never done:** a24559 is the only world the language model is checked on; de1cc6 has fewer living
lects (530 vs 616), and three checks fail there. Either the
model leans on a24559's history, or the checks' marks are tighter than one world's spread.

What I'd try: read which families carry ⁿt and ᵑk on de1cc6 (one family's founder effect would be fine; a rule weight
would not); count sister pairs per family for the strict share (a few big young families can pull it); for pronoun loans,
list the borrowing pairs (a shift-heavy history may borrow pronouns more). Then decide per check
whether it is a model fix or a world that is allowed to differ.
- [ ] a per-check reading of de1cc6 with the cause named
- [ ] each of the three either passes on de1cc6 or has a written reason it may differ there
