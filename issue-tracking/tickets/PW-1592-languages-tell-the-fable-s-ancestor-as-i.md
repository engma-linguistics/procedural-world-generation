---
id: PW-1592
title: "Languages: tell the fable's ancestor as it stood at the split (snapshot state), not a lect that later innovated"
type: task
status: todo
parent: PW-767
milestone: null
subsystem: culture
effort: m
impact: med
found_by: lang-lane5
blocked_by: []
relates: [PW-1537]
refs: ["planet/language/texts.py::pick_family", "planet/language/texts.py::fable", "planet/language/lect.py::Lect.copy", "planet/language/output.py::thin_snapshots", "tools/language/demo_page.py::fable_section", "run a24559 (fable ancestor p320, its copy d767)", "PW-1537 R2 (diagnosis by lang-last)"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: the demo's fable is told in an "ancestor" and three or four living daughters, to show sound change the
way Schleicher did. On a24559 the shown ancestor (p320, an arrival proto) had a single child copy (d767), and all
daughters came down through d767 after it had replaced 'say', 'see', 'bird', 'fish', 'come', 'give' and 'good'. So the
daughters agree with each other against the ancestor, and a linguist reads the page's centrepiece as a fake
reconstruction. If nothing is done, the cold review's R2 stays true on every run where the chosen ancestor buds before
it changes.

Why it is not a one-line fix: lects bud and live on (no dead lect in 2-9 kyr ago splits into 2+ living lines at its
death), so the true common ancestor of the daughters is a lect at the time of its first bud, and the output keeps only
its final state plus snapshots (core-100 forms with spellings, a short typology, gram forms and levels: enough words,
not enough grammar: sides, hosts, paradigms, the full typology the sentence builder reads).

What to try (one of):
- A. `texts.pick_family` picks the daughters' most recent common lect M and the earliest bud time t among them; the pass
  stores a full lect json of M at t (the history knows M's buds as they happen: `Lect.copy` could ask the driver to
  keep a frozen `lect_json` of the parent at the first bud in 2-9 kyr ago, a few dozen per run).
- B. Build the ancestor line from M's final json with its core-100 words and gram forms swapped for the snapshot at t
  (cheap, no pass; mixes a 6 kyr lexicon with today's paradigms, so the grammar line can still contradict).
Lean: A.
- [x] fable daughters descend from the shown ancestor: a `demo_page.py` check that each daughter's fable word shares
  a root (`etym_roots`) with the ancestor's or is marked replaced or borrowed

## Updates
- 2026-11-09: Done (lang-lane6), option A. `History.splits` keeps a lect as it stood at its first bud 2-9 kyr ago
  (`history.SPLIT_KYR`); `output.splits_json` writes those with living lines on 2+ branches as the doc's `fable_splits`
  (core lexicon, as a dead lect keeps; 56 on a24559); `texts.pick_family` picks among them with daughters on 2+
  branches; `texts.fable_descent` (run by `demo_page.py`, a stderr warning) checks the fable words by etymological root:
  a pre-split root of the line must be in the ancestor, a post-split root of the family must not be shared across
  branches. a24559 pass: d767 as it stood at 4.5 kyr, daughters d767, d820, d819, d818, 0 problems (stored run: p320
  at 6.0, all daughters through d767). The check sees lexical innovations only; the split state makes the shared sound
  changes right by construction.
- 2026-11-09: Created from inbox draft draft-language-fable-ancestor-at-split.md (found by lang-lane5).
