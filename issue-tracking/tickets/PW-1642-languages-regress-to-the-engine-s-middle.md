---
id: PW-1642
title: "Languages regress to the engine's middle: give each lineage persistent change tendencies and let a language's own pattern resist changes that break it"
type: task
status: in-progress
parent: PW-767
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: lang-coordinator
blocked_by: []
relates: [PW-1622, PW-1623, PW-1638]
refs: ["planet/language/lect.py::Lect.rule_pool", "planet/language/lect.py::Lect.weighted_rules", "planet/language/rules.py::pick_rule", "planet/language/rules.py::natural_weight", "planet/language/history.py::RULE_WEIGHT", "planet/language/inventory.py::Inventory", tools/language/real_inventory.py, "run a24559", "run de1cc6"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: every language draws its sound changes from one shared, frequency-weighted pool, and each draw
forgets the last. Mathematically that is a single Markov chain, and every line run on it long enough heads to the same
stationary mix: the engine's "middle". The real-inventory experiment shows it: six of seven fully configured
languages lose most of their character in 2,500 years, the same few changes fire in nearly every line, back-vowel
harmony appears in 8-10 of 10 daughters of every language. Real families instead sit in different stable basins for
millennia (Polynesian and Bantu stay open-syllable; Chinese lost its codas and stayed that way; Germanic keeps
reducing unstressed vowels; Romance keeps lenition going).

Mechanism (literature: Sapir's "drift"; Kisseberth's conspiracies; the stable-state view of typology):
1. Lineage tendencies: at proto birth draw a small persistent bias over rule families (lenition, final-vowel loss,
   vowel reduction, palatalisation, coda loss vs gain, harmony...), inherited by daughters with a little mutation and
   a slow decay. Changes are weighted by it, so a line keeps moving in its own direction instead of random-walking.
2. A language's own pattern resists: changes that would break its current majority pattern (open syllables, a coda
   class, harmony, word length) are weighted down in proportion to how firmly it holds; changes that fit it are
   weighted up (PW-1622 did the hard-veto part; this is the soft, general part).
3. Fix the supply asymmetry (PW-1638): add the real coda-making routes (apocope, syncope, final-vowel loss after
   stress) so coda gain and loss are both possible and the pattern, not the menu, decides.
4. Token frequencies (PW-1623) so the pool is not pulled to world-wide type frequencies.
Acceptance on the real-language benchmark: +2.5 kyr distances near birth distances for most of the seven; daughters
of one family visibly alike, different families visibly different; checks (sisters, WOLD, areal, horizon) hold.
If never done, every world's languages blur toward one sound over time, which is the opposite of what peoples need.

## Updates
- 2026-11-10: Status todo -> in-progress. Lane 14/14b built lineage tendencies (OU walk, LINE_FAMILY_SIGMA 1.5), signature changes at splits and the word-shape anchor; 14b made allophones productive (word building on phonemes, allophone rules apply to new tokens), which cleared overused ɹ. Families read as families (families_apart: a24559 same-branch sound distance 2.16 -> 1.74, other family 5.23 -> 4.93; 25 of 50 branches carry a signature). Open: ʁ overused on a24559 (12.1% of living lects vs PHOIBLE 3.7%, bar 3x): r > ʁ fires less than on main but its product lasts (kept clusters and codas, fewer changes a kyr, r back beside ʁ in 77 of 115 lects). de1cc6 passes it.
- 2026-11-10: Created from inbox draft draft-lineage-drift-tendencies.md (found by lang-coordinator).
- 2026-11-10: Lane 16 (merged 15b6fea2): RULE_WEIGHT S148 = 0.3, so ʁ no longer counts as overused on a24559. A de1cc6 re-roll still has ʁ at 14.5%. The root cause is PW-1692 (re-fire cap saturation); remove the per-row weight once that is fixed.
