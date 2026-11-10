---
id: PW-1568
title: "Languages: pronoun loans sit at the 0.08 cap (0.070-0.088 across passes); the a24559 final pass fails the WOLD loans check at 0.083"
type: task
status: todo
parent: PW-767
milestone: v4
subsystem: culture
effort: s
impact: low
found_by: language lane (2026-11-08)
blocked_by: []
relates: [PW-1539, PW-1551]
refs: ["planet/language/checks.py::CLOSED_LOAN_MAX", "run a24559"]
created: 2026-11-08
updated: 2026-11-10
---

## Description
In plain words: real languages almost never borrow pronouns (WOLD: a few percent; English "they" is the famous case). Our
check allows a mean living loan share of 0.08 for pronouns. After the 11-08 rulings and syrinx merges the share wobbles
around the cap from pass to pass: 0.088 (rulings "alone" pass, syrinx pass A), 0.070-0.077 (other passes), 0.083 in the
a24559 final pass of 11-08 (rho 0.411 still passes). Noise around a cap that is itself generous, so the real question is
which route carries pronouns (shift relexification, the new partial nativisation, or ordinary contact) and whether that
route should spare closed-class words.

**What misleads if never done:** the loans check flips between passes, so a lane can't tell its own regression from noise.

- [ ] find which history step makes the pronoun loans in a24559 (count by route)
- [ ] spare pronouns on that route (or confirm it's a real shift-language pattern and say so); share back under ~0.06

## Updates
- 2026-11-10: 11-10: pronoun loans flip around the 0.08 cap from rebuild to rebuild (0.065-0.089; 0.081 after lane 13). Pulled back to v4: find why pronouns borrow near the cap and fix the mechanism, rather than calling it noise each time.
- 2026-11-09: Language wrap-up 11-09: realism polish, parked as later (owner: language good enough to move forward).
- 2026-11-09: 11-09 lane 4 pass: pronoun loans 0.077, under the 0.08 cap (WOLD check passes), likely from shorter pronouns; earlier passes ranged 0.074-0.089, so keep open until a second seed confirms.
- 2026-11-08: Created from inbox draft draft-language-pronoun-loans-borderline.md (found by language lane (2026-11-08)).
