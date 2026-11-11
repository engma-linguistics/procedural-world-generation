---
title: "Languages: real-language benchmark misses its bar, 3 of 7 languages keep their character (bar 4)"
type: task
status: todo
parent: PW-1736
milestone: v4
subsystem: culture
effort: m
impact: med
found_by: lane18
blocked_by: []
relates: [PW-1737, PW-1642, PW-1641]
refs: [tools/language/real_inventory.py, tools/language/data/real_inventory_baseline.json]
---

## Description
In plain words: the benchmark seeds a proto with a real language's sounds and habits and lets it change for 2.5 kyr. Only
3 of the 7 (Swahili, Japanese, Hawaiian) still look like themselves afterwards. Spanish (+0.60), Mandarin (+0.65) and
Arabic (+0.75) drift further than the 0.5 the benchmark allows, toward the engine's own middle. Lane 18 made "at least 4 of
7 keep their character" a fixed bar of `real_inventory.py --check` (the owner's 11-10 ruling: benchmark gaps are now-work),
so `--check` exits 1 until this is fixed.

Measured on main 88855b5a (20 seeds): mean growth 0.49; the one change fired in >= 80% of daughters is "simplification"
(89%); closed syllables fall in Mandarin and Arabic (0.29 > 0.26, 0.43 > 0.36), final consonants too.

What misleads if never done: the standing benchmark stays red, so lanes learn to ignore it, and languages with closed
syllables and big consonant sets keep sliding toward one middle shape over time (PW-1642's worry).

Start: per language, which changes carry the growth (the `changes` list per daughter in `--json`), and whether
cluster/coda simplification fires on lines whose anchor holds closed syllables.
