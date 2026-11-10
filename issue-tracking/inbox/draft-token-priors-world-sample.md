---
title: "Languages: token-frequency priors come from a Eurasian sample; glottal stop, approximant r and taps fall back to presence"
type: task
status: todo
parent: PW-767
subsystem: peoples
effort: s
impact: low
found_by: lang-lane14
blocked_by: []
relates: [PW-1623, PW-1641]
refs: [planet/language/data/token_frequency.tsv, tools/language/token_priors.py, "planet/language/inventory.py::token_class", "planet/language/inventory.py::_lexical", tools/language/real_inventory.py]
---

## Description
In plain words: lane 14 (PW-1623) made words use sounds by how busy each kind of sound is in real words, read off
NorthEuraLex 0.9 (107 Eurasian languages). Classes found in fewer than 20 of them keep the old weight by how many
inventories have the sound: the glottal stop (17, mostly a marginal coda there), approximant r (8), taps (18), retroflexes,
clicks. So Hawaiian- and Arabic-seeded protos still use ʔ at about 2% of segments against 7-8% real, and English ɹ stays
rare. If never done, Polynesian- and Semitic-like languages keep a thinner, less glottal texture than their real models,
and the benchmark's texture term stays their main gap.

Try: rebuild the table from a world sample (Lexibank / ASJP word lists; ASJP needs its code mapped to segments) with
`tools/language/token_priors.py`, keep the 20-language floor; re-run `real_inventory.py --check`.
- [ ] ʔ and ɹ classes in the table from a world sample; Hawaiian/Arabic ʔ token share within 2x real in the benchmark
