---
id: PW-1763
title: "Languages: the pass's memory peak grew past the matrix's 24G cap at 8 workers (21.6G -> 25.3G on a24559)"
type: task
status: todo
parent: PW-1736
milestone: null
subsystem: culture
effort: s
impact: med
found_by: lang-lane20
blocked_by: []
relates: [PW-1737, PW-1745]
refs: [planet/language/history.py, planet/language/lexicon.py, tools/language/matrix.py, "run a24559", "journalctl --user: run-p335861 scope, 25.3G memory peak"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: the language pass now needs more memory than the cap the check matrix and the lanes give it, so a pass at
8 workers under `MemoryMax=24G` is killed by the OOM killer (lane 20 hit this on a24559 at 7 min 49 s).

Measured with systemd scope peaks on a24559, 8 workers: main 4306f7b2 21.6G; lane 20 (55 more concepts, 969 -> 1,024,
words for late animals, biome kinds and tech items) 25.3G. languages.json grew only 2.4% (65.4 -> 67.0 MB), so the peak
is not the output; it is most likely the forked step workers each holding a copy-on-write image of the main process
plus their own lexicon batches, which scales with workers x lexicon size. The matrix (4 workers per cell) was run with
`--memory-max 30G` for lane 20.

What breaks if never done: every later lane that adds concepts tips the pass over the cap; at 8 workers in `planet make`
under the house memory rule an OOM kill loses ~10 min of pass.
- [ ] measure where the peak is (tracemalloc on the main process; RSS per worker during `steps`)
- [ ] bring a24559 at 8 workers back under 24G (e.g. ship only the touched lects to workers, or drop dead lects' full
      lexicons once their descendants are born), or raise the documented cap with the owner

## Updates
- 2026-11-11: Created from inbox draft draft-language-pass-memory-peak.md (found by lang-lane20).
- 2026-11-11: Matrix cells run at MemoryMax 30G meanwhile; coordinator rebuilds use 40G.
