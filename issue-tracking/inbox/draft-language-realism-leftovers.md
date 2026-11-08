---
title: "Language realism leftovers: diminutive renewal overused, ɹ ɫ ʁ ɦ far too common, tone re-phonemicised, shifts leave synonyms, growls in bird/reptile protos, function words coined"
type: task
status: todo
parent: PW-767
subsystem: culture
effort: m
impact: med
found_by: lang-design (sinks, compounds and shifts rounds)
blocked_by: []
relates: [PW-982, PW-1423]
refs: [planet/language/lect.py::rule_factor, planet/language/lect.py::keep_part, planet/language/inventory.py::_pool_for, planet/language/profiles.py, planet/language/data/voice_profiles.toml, planet/language/data/sound_changes.tsv, tools/language/knowledge_tables.py, planet/language/lexicon.py::step, planet/language/data/derivations.tsv, planet/language/data/grammaticalization_paths.tsv, docs/review/language/calibration.md, docs/review/language/voice-profiles.md, "scratchpad sinkH/flow.py", "scratchpad compJ/coins.py", "Heine & Kuteva 2002", "run a24559"]
---

## Description
In plain words: several things still look made up to a linguist reading the language pages. Each has a measured number
and a fix idea.

**Diminutive renewal (worst; seen first on the pages).** 9.1% of all living words are 'X + little' meaning X (the
expressive renewal, Latin auricula > oreille), and the commonest affix ends the history of a median 11% of a lect's words
(up to 19%). In family p306, 11-20% of each human lect's words begin with that lect's 'little' prefix: ear, eye, blood,
new and tooth are all ṭii-. The compounds and shifts round widened the renewal to tools, plants and kin terms to hold
coinage down; coinage is still 10.6% of replacements (design weight 3%). Fix: count renewals against AFFIX_CAP, limit
renewal to the classes where it is attested (body parts, small animals, kin), and find a non-coinage fallback (draft
item "function words" below is one). Measured by `scratchpad/demo_meas/` (s4a.py, s8d.py).
- [x] 'X + little' renewals under ~3% of words; no lect with over 8% of words sharing one affix (round 5 core lane: 1.7%,
  0 lects; coinage 10.6% -> 2.9% of replacements; calibration.md "Round 5, core lane")

**Same-word shifts (done, round 5: contrast sets; brother = sister 0.18 -> 0.01, I = we 0.13 -> 0.03).** 33.5% of shifted words are identical to their source concept's word in the same lect, so
brother = sister in 114 of 627 lects, I = we in 84, father = husband in 29. Real shifts mostly replace the old meaning's
word rather than leave both on one form. Fix: a shift either vacates the source concept (which then renews) or is
skipped for pairs that languages keep apart (kin gender pairs, pronoun persons).

**Tone re-phonemicised (done, round 5: 221 lines -> 0).** "tone became phonemic" fires two or more times on 221 of 627 living lines, and on 137 lines
whose proto was already tonal. Fix: the tonogenesis rule needs "no tones yet" as a condition.

**Sounds.** Over all 627 living lects (not just the human-voiced ones the check reads): ɹ 0.51 (PHOIBLE 0.017), ɫ 0.20
(0.007), ʁ 0.43 (0.037), ɦ 0.24 (0.031), ʐ 0.20 (0.026). The segment check should read all lects (non-human ones
judged against their own profile) so this is caught. Protos can reach 99 consonants (p200) and 50 vowels (p216).
Living lects on run a24559 have p in 0.72 of lects (PHOIBLE 0.85), with t and k fine. The over-common
sounds are ʁ 0.38 (PHOIBLE 0.04), ɹ 0.28 (0.03) and ɦ 0.27 (0.03). They come from context-free r > ʁ, r > ɹ and S173,
which have no exits in the catalogue. ɡ 0.31 (0.56) and d 0.30 (0.48) are rare. If this is never done, phonology
tables read as oddly uvular and breathy. Fix: condition those rows or add attested exits (calibration.md "Sinks round"
has the inflow/outflow audit method).
- [x] ʁ, ɹ, ɦ each within ~3x PHOIBLE for humans (round 5: all lects ɹ 0.05, ʁ 0.19 (humans 0.10), ɦ 0.01, ʐ 0.01; new
  all-lect check "overused segments")
- [ ] p within 0.15 of PHOIBLE (all lects 0.60, humans 0.71, PHOIBLE 0.85)
- [ ] all-lect check passes: still over are ɒ 0.20 (humans 18%, PHOIBLE 1.7%, source not traced), ɖ 0.27, ɫ 0.11 and
  y 0.18 (kobold, dragonborn, kenku, aarakocra: do their profiles mean to favour them? if so mark it in make_cost), and
  the two-voiced vowel u‼ 0.12, which `species_cost(HUMAN, ...)` does not class as non-human

**Non-human variants.** Each species' growled, purred or two-voiced variants get a per-candidate share over its 30
commonest sounds. So 54% of avian, 78% of reptilian and 82% of tortle proto-inventories contain a growled sound,
though the profiles call it "possible but not the norm". Humans were fudged to harsh x30 to compensate. Fix: one target
share per species and key, spread over the candidates; then set human harsh back to x8.
- [ ] growl share under ~40% for avian/reptilian, ~1-3% for humans at x8 (200 draws per profile, rng 1)

**Function words.** About 30% of replacements of AT, BECAUSE, WITH, IF, SOME, ALL and OTHER are fresh coinages
(isolated-lect harness `compJ/coins.py`, 8 protos, 10 kyr), against 10-20% for content words. Real languages
grammaticalize content words instead ('belly' > 'in', 'say' > 'because'). The pages show prepositions of "unknown
origin" everywhere. Fix: let a function word's replacement draw from the content > function paths in
grammaticalization_paths.tsv (shared with grammar.py) before coining.
- [ ] function-word coinage share near the content-word share

**Homophones after the vocabulary round (judgement call for Daniel).** With 712 words per lect (was 376) the median
homophone share is 0.22 (was 0.125): nearly all CLICS-attested polysemy (NOW / TODAY, POT / BOWL, LOW / SHALLOW), the
core 100 at 0.12, accidental homophones under 1%. The lexicon test bar moved 0.16 -> 0.20 mean. If the pages read as too
polysemous, lower shift's draw weight for the WOLD meanings or have a shift vacate its source more often.
- [ ] Daniel: is ~22% polysemy on a 700-meaning list acceptable?

