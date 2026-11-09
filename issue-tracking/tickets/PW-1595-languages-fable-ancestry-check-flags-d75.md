---
id: PW-1595
title: "Languages: fable ancestry check flags d754 SAY (deep root p314:NAME not in the split copy) on a24559"
type: task
status: done
parent: PW-767
milestone: null
subsystem: culture
effort: s
impact: low
found_by: coordinator, demo build after lane 6 (PW-1592)
blocked_by: []
relates: [PW-1592, PW-1537]
refs: ["planet/language/texts.py::fable_descent", "planet/language/history.py::birth", "tools/language/demo_page.py::fable_section"]
created: 2026-11-09
updated: 2026-11-09
---

## Description

In plain words: the fable is now told in the ancestor language as it stood at the split, and a check confirms each
daughter's fable words come from that ancestor. On a24559's demo family (ancestor d754 at 4.5 kyr) one word still fails:
d754's SAY has the deep etymological root p314:NAME, older than the split, but no word in the split copy carries that root.

Either the check reads the wrong layer (a word coined after the split from an inherited word: its own root is new, its
deep root old, and the copy's word for the source may have been renamed since), or the copy misses something it should
hold. Two other flags on the same family were a same-frame boundary in the check (roots coined in the split's own frame,
after the bud copied the parent), fixed by the coordinator 11-09.

If never done: the demo build prints a one-line warning; the fable shown may contain one word not traceable to the
shown ancestor.

## Acceptance
- [ ] Diagnose which case it is; fix the check or the copy; demo build on a24559 prints no fable warning.

## Updates
- 2026-11-09: Status todo -> done. Lane 8 (8fd43582): the check was wrong. d754 coined a new SIT at 6 kyr (in the split copy), then borrowed back cousin d216.1's reflex of d584:SIT@8.5 at 3 kyr (borrow:d216.1, contact). fable_descent now passes a word with a borrow step after the split (etym nodes passed from demo_page). Demo build prints no fable warning on stored a24559 and on lane 8's fresh pass.
- 2026-11-09: Created from inbox draft draft-fable-check-say-from-name.md (found by coordinator, demo build after lane 6 (PW-1592)).
