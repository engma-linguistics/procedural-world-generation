---
title: "languages.json is 140 MB and the pass takes 15 minutes on a24559: thin it into sidecars and fix the three hot spots before it joins every peoples run"
type: task
status: todo
parent: PW-767
subsystem: culture
effort: m
impact: med
found_by: lang-design
blocked_by: []
relates: [PW-986, PW-1423]
refs: [planet/language/output.py, planet/language/history.py, planet/language/percepts.py, planet/language/profiles.py, planet/language/rules.py, viewer/langview.js]
---

## Description
In plain words: the language pass writes one 140 MB file per run (target was 40-60 MB) and takes about 15 minutes with
12 workers (steps 560 s, inventory observation 55 s). The viewer copes (1.3-2 s load on this machine) and `output.save`
only calls the pass through a guarded hook, but if this is never done every peoples run grows by 15 minutes and 140 MB, the
viewer gets slow on a laptop, and the file is too big to keep several runs around for the "across seeds" check.

Where the bytes are: etym_nodes 44 MB, snapshots 45 MB (core_roman ~11), lexicons 25 MB, changes 11 MB.
Where the time is: `Segment.__hash__` (frozen dataclass hashing on every dict lookup), `profiles.hear_word` (nearest-segment
search per segment with no cache), and `functional_load` running `apply` twice per form.

Fix: (1) split the file: `languages.json` keeps lects, names, families, checks, intelligibility; `languages-snapshots.json`
and `languages-etym.json` are fetched by the viewer on demand (the time tab and the etymology chains); (2) cache
`hear_word` per (segment, inventory id); precompute a per-segment hash; make `functional_load` reuse one `apply` pass;
(3) parallelize `inventory.observed` with the steps. Keep the output identical (determinism test).
- [ ] main file under 40 MB, pass under 5 minutes with 12 workers on a24559, viewer unchanged for the owner
