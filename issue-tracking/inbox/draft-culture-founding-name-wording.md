---
title: "Founding cultures are named 'first halflings of ...', so faith names read 'the sea faith of first halflings of ...'"
type: task
status: todo
parent: null
subsystem: culture
effort: xs
impact: low
found_by: lang-design (grammar D lane, faiths pass 3, 2026-11-08)
blocked_by: []
relates: [PW-1249, PW-1436]
refs: [planet/lineages/cultures.py::document, tools/language/sketch.py::faith_label, docs/review/language/for-daniel.md, "run a24559"]
---

## Description
In plain words: the culture builder names a founding culture "first tortles of the south of Simath", without an
article, and faiths take the culture's name, so every faith reads "the sea faith of first tortles of ...". It reads
like a translation slip on every faith line in the brief, viewer and language pages.

**Now.** `planet/lineages/cultures.py::document`, line ~430:
`nm = f"{u.adapted + ' ' if u.adapted else ''}{'first ' if u.how == 'founding' else ''}{pn}" + ...`.
The language pages patch it at print time ("the sea faith of the earliest tortles of ...", `sketch.faith_label`), but
the cause is here. Changing it renames the stored cultures of every run, which is fine under the no-backward-compat
rule (rebuild cultures, or patch the readers).

**Wanted.**
- [ ] founding cultures read "the first tortles of ..." (or "the earliest ...") at the source, faith names follow
- [ ] `sketch.faith_label` patch removed
- [ ] fold into PW-1249 (gloss names) if that lands first
