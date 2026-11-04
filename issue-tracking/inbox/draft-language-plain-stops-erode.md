---
title: "Languages: plain p, t, k are lost in half the living lects since fresh coinages became rare (segment-frequency check fails)"
type: task
status: todo
parent: PW-767
subsystem: culture
effort: s
impact: med
found_by: lang-design (measures and phonemes round)
blocked_by: []
relates: [PW-982]
refs: [planet/language/lexicon.py, planet/language/lect.py, planet/language/lect.py::keep_part, planet/language/rules.py::SAME_AS, planet/language/data/sound_changes.tsv, tools/language/knowledge_tables.py, docs/review/language/calibration.md, scratchpad sinkH/flow.py (isolated-lect flow harness), scratchpad runH2/a24559/languages.json]
---

## Description
In plain words: almost every real language has p, t and k (PHOIBLE: 85%, 72%, 91%). On the shipped run our living
languages had them in 68%, 85% and 78%. On run F (measures and phonemes round, same world, current tree) only 42%, 53% and
44% do, so the "living segment frequencies vs PHOIBLE" check fails. The lost stops are not replaced by close relatives
(only about 20 of 180 lects without p have p' or pf); they are lenited away (Grimm p t k > f θ x, p > ∅, p > f > h > ∅) and
nothing brings them back.

What changed: the lexicon's replacement sources went from coin 0.15 to 0.03 (renew, derive and compound took the share).
A fresh coinage draws its sounds from the inventory, so it kept refilling the common stops in the vocabulary while sound
change wore them down. In the isolated-lect harness (96 human lects, 22-consonant protos, 20 kyr, no contact), changing
only SOURCES back to the old shares gives p/t/k at the end 0.54/0.71/0.64 against 0.48/0.50/0.43 with the current shares.
The size-steer constants changed in the same round make no difference (anchor 0.2 vs 0.12: k 0.34 vs 0.38).

Also seen (older, not new): ɲ and ŋ are phonemes in 90% and 86% of living lects (PHOIBLE 42% and 64%), and ʔ in 75% (PHOIBLE 38%).
They stand before vowels and word-initially, so the new allophone pass correctly finds them contrastive; the excess comes
from the change catalogue and the proto draw, not from counting.

What breaks if never done: phonology pages read as lenition-heavy and unnatural (no k in 56% of languages), and check 10
stays red.

What I'd try (a mechanism, not a per-language fix): either give coinages back part of their share (the lexicon owner's
call), or let the ease drag in `lect.py` weigh a rule that removes a very common PHOIBLE segment (frequency over 0.7) more
heavily, so lenition of the last p is rarer than lenition of one p among several stops. Measure with an isolated-lect
harness first (about 10 s per 32 lects), then one full run.
Progress (word families round, 2026-11-04): a stop steer in `lect.rule_factor` (STOP_NORM 0.33, STOP_K 2; architecture.md,
calibration.md "Word families and derivation round") brought run E4 to p/t/k 0.55/0.80/0.70 and check 10 green. p and k
are still more than 0.15 under PHOIBLE; ʔ (17% of consonant tokens in the harness, mostly S042 prothesis that nothing
removes) and j (10%, glide formation) are the remaining sinks.
Progress (sinks round, 2026-11-04; calibration.md "Sinks round"): an inflow/outflow audit found ʔ, ɲ, ʋ (and j in
tokens) were sinks. S042 prothesis now only before stressed initial vowels; coalescence rows absorb their j; exits added from
real changes (initial ʔ loss, Middle Chinese > Mandarin; ɲ > j after vowels, Romanian; final ɲ > n, Slovene; ɲ > n,
Finnic; j loss between vowels, Greek; ʋ > v, German; β > w in the coda, Catalan); twin rows of the demo lenitions drawn
once; a keep steer (`lect.keep_part`) draws a quarter as often a rule that would leave no p, t, k, m, n, l, j, w, i, u or a
in a lect's frequent words. Run H2 (`scratchpad/runH2/a24559/languages.json`, against E4): ʔ 0.47 (0.71), ɲ 0.36 (0.89),
ŋ 0.86 (0.86), p 0.66 (0.55), t 0.89 (0.80), k 0.81 (0.70), w 0.71 (0.41); check 10 green; sisters strict 0.502.
Left: p is 0.19 under PHOIBLE (k 0.09); ŋ stays at 0.86 (1.34x PHOIBLE: S143/S144 balance, not a sink); new-visible
over-representations ʁ 0.38 (PHOIBLE 0.04), ɹ 0.28 (0.03), ɦ 0.27 (0.03) from context-free r > ʁ, r > ɹ and S173 with no
exits in the catalogue; ɡ 0.31 (0.56) and d 0.30 (0.48) under.
- [ ] living p/t/k shares within 0.15 of PHOIBLE on a full a24559 run, check 10 green (H2: t, k yes; p 0.66 vs 0.85)
- [x] ɲ/ŋ prevalence reviewed (catalogue or proto draw), below 0.75 (ɲ 0.36; ŋ 0.86 left as balanced, within 1.5x)
- [ ] rhotic and breathy sinks (ʁ, ɹ, ɦ) given attested exits or conditioning, each within ~3x PHOIBLE
