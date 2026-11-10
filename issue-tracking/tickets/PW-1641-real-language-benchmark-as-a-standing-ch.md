---
id: PW-1641
title: Real-language benchmark as a standing check for the language model (like earth_check for physics)
type: task
status: done
parent: PW-767
milestone: v4
subsystem: culture
effort: s
impact: high
found_by: lang-coordinator
blocked_by: []
relates: [PW-1622, PW-1623, PW-1624, PW-1638]
refs: [tools/language/real_inventory.py, tools/language/data/real_inventories.tsv, tools/language/find.py, tools/earth_check.py, docs/wiki/index.md, "https://claude.ai/artifact/D9zoxQnya6RG5uYspUJX84"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: Daniel ruled 11-10 that the real-inventory experiment (seven real languages given to the engine as
proto-languages, then aged 2,500 years) is the language model's Earth: a plausibility anchor run after every language
model change, not a one-off. Today it is a tool with a page; nothing records a baseline or says when a change made it
worse. If never done, the regression-to-the-middle the experiment found can come back unseen.

Do: a `--check` mode with a stored baseline (birth distance, +2.5 kyr distance, closed-syllable share, harmony and
coda drift per language) and bands, printed like earth_check; add it to the language lane playbook in the wiki and to
lane briefs; fix the finder's sparse-profile scoring (PW-1624) since the benchmark scores with it. Plausible-or-better,
never a fidelity target: the goal is that a Hawaiian-like or English-like people stays recognisably itself, not that
it reproduces Hawaiian.

## Updates
- 2026-11-10: Status todo -> done. Lane 14/14b: real_inventory.py --check with a stored baseline (main 80d89894) and bands, in the language lane playbook. After lane 14b: mean distance growth 1.29 -> 0.73, drift signatures 6 -> 1, kept character 1 -> 2 of 7, 0 metrics worse.
- 2026-11-10: Created from inbox draft draft-real-language-benchmark.md (found by lang-coordinator).
