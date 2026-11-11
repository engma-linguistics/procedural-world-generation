---
id: PW-1747
title: "Languages: set the matrix pass bar (70% of cells per check, invariants always, no check down more than one cell)"
type: task
status: done
parent: PW-1736
milestone: v4
subsystem: culture
effort: xs
impact: high
found_by: lane18
blocked_by: []
relates: [PW-1737, PW-1738, PW-1740]
refs: [tools/language/matrix.py, docs/review/language/matrix/, docs/review/language/for-daniel.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: every language lane is now judged on a table of 4 worlds x 2 seeds (8 language passes), not on one draw of
a24559. That needs a pass mark. The proposal, from the first baseline (docs/review/language/matrix/baseline-2026-11-11.md):

- each realism or guard check passes in at least 70% of the cells (6 of 8), the usual seed-pass-rate convention;
- the three invariants (typology agrees, no impossible segments, second voice) pass in every cell;
- the horizon is shown, not barred (owner 11-08: about 11 kyr and more is close enough; the check now only fails a
  reading under 6 kyr);
- and, because main itself is under 70% on some checks today, a lane may not lower any check's pass rate by more than one
  cell against main's matrix (`matrix.py --compare main.json branch.json`).

Checks under the bar on main today (see the baseline table) are not widened. Each belongs to an open ticket: pronoun loans
(WOLD check) to PW-1738, living inventory sizes and overused segments to PW-1740.

What misleads if never decided: lanes keep being accepted or rejected on whichever single draw they happened to run, and a
check that fails on half the worlds reads as "green" on a24559.

Decision needed (owner): accept the bar above, or name another (e.g. 5 of 8).

## Updates
- 2026-11-11: Created from inbox draft draft-language-matrix-pass-bar.md (found by lane18).
- 2026-11-11: Put on the Language Desk as card m.bar (A 6 of 8 lean; B 5 of 8; C A plus an upper horizon limit ~16 kyr).
- 2026-11-11: RULING (owner, 2026-11-11, Language Desk m.bar A): realism and guard checks pass in >= 70% of cells (6 of 8), invariants in all, horizon shown not barred, and no check down more than one cell against main. In tools/language/matrix.py (PASS_BAR, MAX_DROP_CELLS; --compare prints the lane verdict), 13f0bba6.
