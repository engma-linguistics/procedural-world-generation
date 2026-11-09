---
id: PW-1569
title: "Languages: 'many cases' label fires on 35% of living lects while real case counts run light (no 8+ systems; catalogue has 9 case functions)"
type: task
status: needs-decision
parent: PW-767
milestone: null
subsystem: culture
effort: s
impact: med
found_by: language lane (owner question, 2026-11-08)
blocked_by: []
relates: [PW-1538]
refs: ["planet/language/grammar.py::RICH_CASE", "planet/language/grammar.py (typology case label, line ~1459)", "run a24559"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: Daniel asked whether too many languages mark case heavily. By count they don't; by label they look as if they do.

Living lects in a24559 (617), cases = bound case affixes + 1, against WALS 49A (Iggesen 2013, 261 languages):
- no case 28% (WALS 38%); 2 cases 22% (9%); 3: 22% (3%); 4: 18% (3%); 5: 7.5% (5%); 6-7: 2.7% (14%); 8+: 0% (WALS 8-9 9%, 10+ 9%).
- So ours bunch in 2-4 cases and never build Finnish/Hungarian/Tsez-size systems: the catalogue has only 9 case functions (ACC GEN DAT LOC ERG ALL INS ABL COM).

But the typology label says "many" for 216 lects (35%): `case` reads "many" when a lect has 4+ case markers (clitics included) or any one RICH_CASE function, so a language with accusative + locative is labelled like Finnish.

Options: (1, slam dunk) label by count in WALS 49A bins, affixes only (clitic case = "borderline", as WALS does); (2) add the missing case functions so big systems can grow: local-case series (inessive/elative/illative, adessive/ablative/allative from 'inside/top/side' nouns, Heine & Kuteva), essive/translative, comitative/privative ('without'), vocative, so the 6+ share can approach WALS's ~30%; (3) also thin the 2-4 band (mostly LOC/GEN/DAT becoming affixes early). Lean: 1 now, 2 as a small grammar lane.
- [ ] label by count (WALS bins); sketches and viewer read it
- [ ] owner: grow the case catalogue (2)?

## Updates
- 2026-11-08: Created from inbox draft draft-language-case-label-and-ceiling.md (found by language lane (owner question, 2026-11-08)).
