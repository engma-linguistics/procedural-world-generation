---
title: "languages.json is about 150 MB and the pass takes 15+ minutes on a24559: thin it into sidecars and fix the three hot spots before it joins every peoples run"
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
In plain words: the language pass writes one ~150 MB file per run (149 MB after the 11-04 rounds; the felt-roots table doubled the root entries) (target was 40-60 MB) and takes about 15 minutes with
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
Round 5 (core lane, 2026-11-07) made it bigger: `etym_roots` (+8.5 MB) and lexicons of 712 words (was 376) bring the
file to 236 MB (etym_nodes 70 MB, roots table 44 MB, lexicons 67 MB, snapshots 24 MB) and the pass to 1284 s (steps
806 s, wave 117 s) on a loaded machine. Not started this round. Plan worked out: (a) shared tables: one doc-level
concept table and interned root ids; a columnar lexicon per lect; `etym_roots` written only where it differs from
`roots`; (b) sidecars `languages-etym.json` (etym_nodes, roots) and `languages-snapshots.json`; (c) one expander on each
side (`output.load`/`expand` in Python for sketch.py, families.py's stored-json reader, horizon_offline.py and the
tests; `LC.expand` in viewer/langcore.js, with langview.js fetching the sidecars) so readers keep today's in-memory
shape; format procgen-languages/2 documented in architecture.md §11; (d) speed: memoize the wave's `ease_factor` /
`size_factor` per (receiver, rule) per interval (they recompute `touched_by`, `load_forms`, `keep_part` per offer),
and stop `load_forms` sorting the whole lexicon on every call; profile one worker with cProfile first.
Finish lane (2026-11-08): the size half is done. Format procgen-languages/2 (architecture.md §11): the main file is 36.4 MB
(9.5 MB gzipped), with the sidecars languages-etym.json at 63.1 MB and languages-snapshots.json at 26.2 MB, 125.7 MB in all.
The baseline was one 241.5 MB file. One expander on each side: output.load/expand and LangCore.expand. Every reader is
switched over, and the output is identical across hash seeds. The speed half is not done. The 6-frame single-process profile
fell from 765 s to about 680 s (cached Segment hash, wave memo, lazy homophones), but the full pass is still about 1260 s,
because the non-human ease drag added steps time. A parent profile puts the remaining time in the workers' rule
application: `rules._apply_one`, the Pattern memo dict and `dataclasses.replace`.
- [x] main file under 40 MB, viewer unchanged for the owner (36.4 MB; the sidecars load in parallel)
- [ ] pass under 5 minutes with 12 workers on a24559 (now ~21 min wall: worker-side rule application is next)
