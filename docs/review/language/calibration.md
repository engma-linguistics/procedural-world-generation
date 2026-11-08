# Language pass calibration on a24559 (PW-986, builder E, 2026-11-03)

Target: the scholars' horizon for **human lects** lands in 6-10 kyr (architecture section 10, check 3). Levers:
`history.RATE_SCALE` (multiplies `lect.RATE_RULE` sound-change events per generation at rate 1: 0.05 for t1-t3, 0.1 from t4 on, so t3's 6 equals 3 now) and
`history.REPLACE_SCALE` (multiplies the generations handed to `lexicon.step`, i.e. C's `BASE_REPLACE` = 0.0016475 per
generation, calibrated by C to 86% Swadesh-100 retention per millennium at 27.7-yr generations). Both are also read from the
environment (`LANG_RATE_SCALE`, `LANG_REPLACE_SCALE`) for trials.

**Horizon, as measured** (`families.analyse`): among living human lects, pairs are binned by true divergence (1 kyr bins);
a pair is "reconstructable" when its blind core-100 cognate share (normalized percept edit distance < `COGNATE_DIST` 0.45)
beats the pair's **own** chance level: its share with one lect's concepts shuffled (19 permutations, Kessler-style), by
2 sd and by at least `MIN_EXCESS` = 5 of the 100 words. The horizon is the end of the oldest bin where at least half the
pairs pass. (t1-t3 used one global floor from random lect pairs; see below why that was replaced.) `clade_all` is the oldest true clade (all lects) that
the scholars' UPGMA reproduces exactly with its link above chance.

Every trial: `planet languages a24559 --out <scratchpad>`, seed 12, a24559 frames 20 -> 0 kyr ago.

## Trials

| Trial | RATE_SCALE | REPLACE_SCALE | other | horizon human (kyr) | all / clade | sisters <=2 kyr | cross-family | chance floor | shifts | wall time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| t1 | 1 | 1 | SHIFT_K 0.03, wave not scaled by generations | 21 | 21 / 20 | 0.68 | 0.001 | 0.014 | 613 | 394 s (12 workers, load ~90) |
| t2 | 3 | 2 | wave x generation ratio, SHIFT_K 0.015 | 21 (11 by the per-pair test, offline) | 21 / - | 0.541 | 0.006 | 0.006 global; 0.015 per pair | 399 | 656 s (7 workers) |
| t3 | 6 | 2.5 | as t2 | 21 (9 by the per-pair test, offline) | 17 / - | 0.473 | - | 0.011 per pair | - | 794 s (7 workers) |
| t4 | 3 | 2 | RATE_RULE 0.1, per-pair floor (MIN_EXCESS 0.05) | **9** | 10 / 20 | 0.453 | 0.002 | 0.005 per pair | 399 | 1329 s (7 workers, load ~50) |
| t5 | 4 | 2 | as t4 | - | - | - | - | - | - | stopped (romanizer crash, then superseded) |
| t6 | 3 | 1.5 | as t4 | 11 | 11 / 20 | 0.471 (true 0.566) | 0.002 | 0.005 | 399 | 1243 s |
| t7 | 4 | 1.25 | as t4 | 19 by the old rule, **11** contiguous | 15 / 20 | **0.531** (true 0.596) | 0.004 | 0.009 | 399 | 1400 s |
| t8 | 4 | 1.25 | + inventory cap, new-segment weight 0.3, core_roman, rules table | 11 | 11 / 20 | 0.499 (true 0.577) | 0.004 | 0.014 | 399 | 1280 s |
| t9 | 5 | 1.25 | as t8 | 11 | 11 / 20 | 0.497 (true 0.579) | 0.005 | 0.017 | 399 | ~1300 s |
| **final** | 5 | 1.25 | as t9 + voiceless-breathy > aspirated tidy, stable simplification ids | 13 | 13 / 20 | **0.506** (true 0.585) | 0.005 | 0.016 | 399 | 855 s (12 workers) |

t1 notes: blind shares stay above the floor at every depth (0.022 at 19 kyr against a floor of 0.014): lexical retention
along human lines ran at ~92%/kyr (mean true share 0.134 at 12 kyr; Pagel's 86%/kyr gives 0.027), partly from borrowing
between related lects (a loan shares the root), and sound change rarely hid a cognate (blind 0.33 vs true 0.29 at 6 kyr).
Long-lived peoples showed *more* changes per kyr than humans (4.3 vs 2.8): the wave handed them their short-lived
neighbours' rules at full rate. Fixed before t2: wave adoption x min(1, giver generation / receiver generation) (children
carry a change); SHIFT_K 0.03 -> 0.015 (613 shifts, 22% of living lects off their deme's descent, was too many).

t2 notes: shifts takeover 246, swamp 146, trade 6, elite 1; 83 living lects off their descent; long-lived ratio 4.0 (pass);
hubs check failed narrowly; 0 koine changes; 201 MB.

**Why the floor changed (after t3).** The global floor (random lect pairs, ~0.6%) is far below the chance resemblance of
*related* lects, which share sound inventories and word shapes: at 19 kyr human pairs had a blind share of 1.6% against a
true shared-root share of 0.3%, so every bin stayed "above chance" and the horizon pinned at the start (21). Recomputed
offline from the stored t2/t3 files (`tools/language/horizon_offline.py`, current `families.horizon_pairs`) under the per-pair test:

| file | COGNATE_DIST | MIN_EXCESS 0 | 0.03 | 0.05 |
| --- | --- | --- | --- | --- |
| t2 | 0.45 | 21 | 14 | 11 |
| t2 | 0.6 | 21 | 21 | 21 |
| t3 | 0.45 | 21 | 19 | 9 |
| t3 | 0.6 | 20 | 20 | 13 |

A pure 2-sd test (excess 0) still passes noise: with ~15-30 comparable words per old pair, one or two lookalikes beat a
near-zero chance level. Requiring five words over chance is what a comparativist needs before claiming a family (a handful of
regular correspondence sets), so `MIN_EXCESS` 0.05 and `COGNATE_DIST` 0.45 are kept. Sisters <= 2 kyr need REPLACE <= ~2
(t3's 2.5 fell to 0.47), so the remaining lever is RATE_SCALE.

t4 notes: the human horizon lands at 9 kyr (bins: 6-7 kyr 0.77, 7-8 0.82, 8-9 0.57, 10-11 0.0); human chain sound changes
16.6/kyr against 4.4 for long-lived peoples (ratio 3.8, pass); hubs 1.25 vs isolated 2.20 (pass); shifts 399 (83 living
lects off their descent); sisters <= 2 kyr 0.453 (fail). 0 koine changes: a24559's mixed cities (192 city-frames) are all
humans with halflings, gnomes, elves or dragonborn, whose voices are human-like, so no sound is hard for a city majority
(koine pressure is working as specified; it needs a city with non-human-voiced heads). 125 MB file. The run crashed once in
romanization (non-human long vowels ə ɨ ɑ spelled as nothing); fixed in romanize.spell, and the output's Speller now falls back
to IPA and counts failures (`romanization_failures`) instead of stopping the pass.

t6-t7 notes: sisters <= 2 kyr are held down mostly by lexical replacement, not by hidden cognates (true shared-root share
0.57 at REPLACE 1.5, blind 0.47), so REPLACE came down and RATE went up. t7's bins: 0-9 kyr all pass, 10-11 kyr 2 of 3 pairs,
12-13 kyr 0 of 35, then 13-14 kyr 10 of 13 and 18-19 kyr 3 of 6: the old rule ("oldest bin with half passing") let a
6-pair bin at 18 kyr set the horizon. **Horizon rule changed** (families._horizon): contiguous from the present, ending at
the first bin of >= 5 pairs (MIN_BIN) where fewer than half pass; t4/t6/t7 recomputed: 9 / 11 / 11. Human pairs leave a gap
between 9 and 12 kyr in a24559 (few splits at that depth), so the human horizon reads 9 or 11 depending on a 3-pair bin.

**Inventory cap (coordinator, after t7).** Living lects at the present in t6 had consonants Q1/median/Q3 34/44/58 (max
127) and "vowels" 34/49/67 (tone variants included): rules that phonemicize allophones (labialization, breathy voice,
secondary articulations) added segments without limit. Now (lect.py): rules that would add a segment the lect lacks are
drawn at 0.3 of their weight, and after each interval's rule events the consonants above min(1.5 x the proto count, 45) and
vowel qualities (length and nasality count, tone not) above min(1.5 x, 20) fold, rarest new ones first, into their nearest
remaining sound (`simplification:` change, cause "dispersion"). t8 on are with the cap.

t8-t9 notes: with the cap, living inventories at the present are PHOIBLE-sized (t9: consonants min/Q1/median/Q3/max
7/21/27/33/45, vowel qualities 4/9/13/17/20; ~14,000 `simplification` events over the run). A faster rate no longer hides
cognates much (merged sounds come back together, and the chance level of a pair rises: 0.009 -> 0.017), so RATE 4 -> 5 left
the horizon at 11 and sisters at 0.50. Human bins in t9: 0-11 kyr pass (the 10-11 bin is 3 pairs), 12-13 kyr 14 of 35.

**Where it lands.** In a24559 the two targets pull against each other through the slow core words (lexicon's per-concept
rates give a long tail of retention): sisters <= 2 kyr above 0.5 need REPLACE <= ~1.25, and at that replacement 40% of human
pairs still beat chance at 12-13 kyr. Human pair depths have a gap between 9 and 12 kyr, so the horizon reads 9 (t4: sisters
0.45) or 11 (t7-t9: sisters 0.50). **Final constants: RATE_SCALE 5, REPLACE_SCALE 1.25** (RATE_RULE 0.1, COGNATE_DIST 0.45,
MIN_EXCESS 0.05, MIN_BIN 5): horizon 11 kyr, one bin outside 6-10, sisters at the 0.5 line. Moving a check's target is the
owner's call, not a calibration step (reported as a judgement call).

Final run (written to runs/a24559/languages.json): 5 of 6 checks pass; the human horizon reads 13 kyr this time (12-13 kyr
bin: 20 of 35 pairs pass, 0.57; t9 at the same constants: 14 of 35, 0.40): the 12-13 kyr bin sits on the 50% line, so the
reading flips between 11 and 13 between runs. The scholars clearly lose human families between ~11 and ~14 kyr in a24559.


## The horizon by splits, under a stricter cognate test (2026-11-04, after the review)

The review (review-output.md section 8) judged the pair measure loose and fragile: its human reading (11-13 kyr) rests on one
12-13 kyr bin of 35 pairs drawn from one or two old splits, and an edit distance under 0.45 is not the comparative method.
`families.horizon(result_or_doc)` is the replacement measure (the pair measure stays as `horizon_pairs`/`analyse`);
`tools/language/horizon_offline.py` reports both from a stored file.

- **Strict cognates** (`strict_shares`): two forms are cognate when their aligned distance is under COGNATE_DIST (0.45) *and*
  every segment correspondence of the alignment (x:y, x:-, -:y; tone set apart, tone letters skipped) recurs in at least
  REC_MIN = 2 other close pairs of the same two lects. Correspondences are counted over the whole stored vocabulary the
  living lects share (~345 concepts: core 100 plus every concept at least half the living lects have), shares are scored on
  the core 100. One pass (REC_ITERATE False): dropping the failures and recounting until stable collapses small cognate
  sets to nothing (a human pair 5 kyr apart: 53 close pairs, 28 fail the first pass on rare identities such as ɗ:ɗ or
  lʷ:lʷ, and the cascade then takes all of them; strict share 0 with a true shared-root share of 0.28).
- **Splits, not pairs** (`true_splits`, `split_horizon`): each node of the true lect tree among living lects (lines parting in
  the same frame folded into one multi-way split) is recovered when the scholars' UPGMA over 1 - strict share (lects in a
  random order) holds a clade matching the split's lects at Jaccard >= SPLIT_JACCARD 0.8, and the mean strict share across
  the split's groups beats the pairs' own shuffled chance level (19 permutations) by SPLIT_EXCESS 0.03. Windows of 2 kyr
  stepped by 1 kyr; splits with two groups of >= 3 lects are scored alone when a window has >= 3 of them (rare: 0-3 per
  window in a24559), else all; the horizon is the 0.5 crossing, linear between window centres, from the present, skipping
  windows of < 3 splits. Under the strict test the shuffled chance level is ~0 (0.0000-0.0001 per split), so the excess
  is in effect a minimum of three regular cognates in the hundred.
- Synthetic check (tests/test_language_families.py): three families, 25 splits each over 16 kyr, 75% of words kept per kyr
  per line and one merging sound law per kyr: the horizon reads 4.5-5.0 kyr over seeds, where 10-5% of the words survive
  (the measure needs ~5-10 regular cognates in the hundred, not 3: rare segments fail recurrence).

**a24559 (runs/a24559/languages.json as stored, 573 living lects, 60 human splits, 243 in all):**

| measure | human | all lects |
| --- | --- | --- |
| pairs, loose test (stored / recomputed) | 11 | 11 |
| splits, strict, SPLIT_EXCESS 0.03 (lect-order seeds 12, 1, 2, 3) | **9.7**, 9.7, 9.7, 8.6 | 12.0 |
| splits, strict, SPLIT_EXCESS 0.02 / 0.05 | 10.5 / 4.7 | 12.0 / 9.3 |
| splits, strict, exact clades (Jaccard 1) | 4.9 | 5.4 |

| shares | pairs | loose (old) | strict | true roots |
| --- | --- | --- | --- | --- |
| sisters <= 2 kyr | 151 | 0.532 | **0.452** | 0.588 |
| different true families | 162,128 | 0.005 | 0.000 | - |

Human recovery curve (strict, SPLIT_EXCESS 0.03; "share" is the mean strict share across the window's splits):

| window kyr | 0-2 | 1-3 | 2-4 | 3-5 | 4-6 | 5-7 | 6-8 | 7-9 | 8-10 | 9-11 | 10-12 | 11-13 | 12-14 | 13-15 | 14-16 | 15-17 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| splits | 11 | 11 | 5 | 8 | 11 | 9 | 7 | 8 | 5 | 2 | 2 | 1 | 3 | 3 | 5 | 4 |
| recovered | 1.00 | 1.00 | 1.00 | 0.75 | 0.55 | 0.67 | 1.00 | 0.75 | 0.60 | 0.50 | 0.50 | 0.00 | 0.00 | 0.00 | 0.20 | 0.25 |
| share | 0.54 | 0.44 | 0.29 | 0.15 | 0.14 | 0.14 | 0.12 | 0.06 | 0.04 | 0.04 | 0.04 | 0.01 | 0.00 | 0.01 | 0.02 | 0.01 |

All lects: >= 0.5 to 11-13 kyr (0.50), then 0.36, 0.27, 0.31, 0.25, 0.20, 0.09 to 17-19 kyr.

Reading. (1) The human horizon by splits is **~9.7 kyr**, inside 6-10, but thinly resolved: human splits between 9 and 14 kyr
number 8, so the crossing sits between the 8-10 kyr window (5 splits, 0.60) and 12-14 (3 splits, 0.00). It is steady
against the lect order (8.6-9.7) and SPLIT_EXCESS 0.02-0.03; it is sensitive to 0.05 (4.7, one weak 4-6 kyr window) and to
exact clades (4.9: past ~4 kyr one or two lects per split are misplaced, by loans or shifts). (2) Sisters fall below the 0.5
bar under the strict test (0.452): about a quarter of the true cognates of sisters fail recurrence, mostly identical words
with a rare segment. The sisters check should stay on the loose test (recognisable resemblance is what a speaker or a first
survey sees) or have its bar re-set for the strict one; that is a target change and the owner's call. (3) Lexical
retention, not sound change, sets the strict horizon: across human splits at 6-8 kyr the loose share (0.17-0.29) is close
to the true shared-root share (0.13-0.30), so sound change rarely pushes a cognate past the distance threshold; what the
strict test loses is regularity and sample size. The true share is still 0.13-0.20 at 7-9 kyr (Swadesh 86%/kyr: ~0.1) and
0.59 for sisters <= 2 kyr (~0.7 expected): replacement is too fast young and too slow in the tail.

## After the tidy-up round (2026-11-04 02:30, commit e0520b9f)

The tidy-up (tone phonemic only with marks on 30% of core vowels; tone and reduction rules down-weighted; derivation affixes
capped; shifts 6-kyr cooldown and 3 per deme; inventory cap 1.25x) made the languages more conservative, and the split-based
human horizon moved from 9.0 to 11.0 kyr. The rule-rate lever does not move it:

| LANG_RATE_SCALE | lects (living) | shifts | horizon human / all | sisters check | notes |
| --- | --- | --- | --- | --- | --- |
| 5 (default) | 1194 (623) | 159 | 11.0 / 10.0 | ok | tonal 48% of living lects; C quartiles 18/22/27, V 7/9/12; i 35% of vowel tokens |
| 6 | 1196 (623) | 161 | 11.0 / 10.0 | **FAIL** (sisters drop under 0.5) | |
| 7 | 1198 (622) | 163 | 11.0 / 12.0 | ok | |

So the horizon is set by the lexical-replacement curve (how fast core words are replaced at 5-12 kyr), not by the sound-change
rate, which only hurts the young sisters. The next lever is the replacement shape (faster rare end, slower core end) or the
measure's tolerances; both are in the needs-decision draft. Shipped: RATE_SCALE 5, this run (`runs/a24559/languages.json`).

## Word length and typology drift round (2026-11-04)

**Word length.** Roots, derivations, compounds and coinages now scale with the lect's syllable space
(`lexicon.syllable_space`, `length_scale = (7.7 / ln sigma) ** 0.7`, clipped 0.7-2.0; caps MAX_SYLL / MAX_SYLL_COMPOUND /
MAX_SEG scale up with it), re-measured on the current inventory at every lexical step, with derivation and compounding
favoured (x scale, x2 for a homophone's renewal) when a lect's space has shrunk. Grounding: Nettle 1995 and 1998, combined
fit X = 17.87 S^-0.31 segments per stem; the exponent 0.7 was set so a Rotokas-sized CV language gets ~1.6-1.8x the
syllables of a 25 C (C)V(C) one (architecture.md §6).

Unit check (`tests/test_language_lexicon.py::test_small_syllable_space_gives_longer_words`, proto lexicons): 6-8 C and 3-5 V,
CV only (sigma 27-35, scale 1.6-1.7): core mean 3.3 syllables, 6.4 segments, class-1 words 2.8 syllables, class-5 4.1;
25 C / 8 V (C)V(C) (sigma ~2200, scale 1.0): core 1.8 syllables, 4.5 segments; 40 C / 12 V complex: 1.6 and 4.4.

Typology: `grammar.drift` existed but nothing called it (`grammar.step` had `drift_typology=False` and `lect.grammar_step`
never passed it), so living lects kept 98-100% of their proto's values; the 1-3% that moved were calques on shift. Now on,
per generation x the lect's rate x (1 + L2 share), with the STABILITY rates unchanged (they already gave the target
spread once run) and a new disharmony boost (x up to 10 for a word-order harmony feature the basic order disfavours).

| trial | change | core syl (all living) | core syl, scale >= 1.2 (sigma < ~330) | corr(scale, core syl) | human: very stable / stable / medium / fickle / very fickle kept | long-lived (gen >= 60 yr) | OV>post, VO>pre |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shipped (`runs/a24559/languages.json`) | - | 2.41 (4.73 seg) | 2.36-2.59 (n 52) | 0.05 | 0.99 / 0.99 / 0.99 / 0.99 / 0.98 | 1.00 / 1.00 / 1.00 / 0.99 / 1.00 | 0.95, 0.76 |
| runB (scratchpad `runB/a24559/languages.json`) | length scale + drift on + disharmony | 2.44 (4.73 seg) | 2.86-3.51 (n 29) | 0.40 | 0.85 / 0.76 / 0.68 / 0.55 / 0.76 (human people, n 103) | 0.95 / 0.92 / 0.89 / 0.82 / 0.81 (n 243, median 145 yr) | 0.94, 0.87 |

runB by length scale (living lects; the shipped file re-measured with the same function in brackets): scale < 0.85 (sigma
~27k) 2.24 syllables (2.28); 0.85-0.95 2.35 (2.39); 0.95-1.05 2.49 (2.49); 1.05-1.2 2.61 (2.42); 1.2-1.4 (sigma ~180) 2.86
(2.36); > 1.4 (sigma 85, hill giant d28, 17 C 5 V CV) 3.51 (2.59). By consonant count alone the curve stays flat (10-15 C
2.82, 30-40 C 2.34), because in this run the small consonant inventories carry 10+ vowels or tones and (C)V(C) templates:
their syllable space is not small (median ~1100). No living lect here has under 12 consonants and a CV template; the
inventory-size round running in parallel widens that end, and the unit tests cover it. Homophone share over all words 0.135
(0.136 before), longest word 19 segments (20 before). Horizon 11.0 kyr human (unchanged), sisters check ok.

Typology per feature (runB, short-generation lects, n 378): word order 0.84, adposition 0.81, gender 0.83, alignment 0.63,
genitive 0.67, negation 0.53, adjective order 0.56, definite article 0.53, diminutive 0.43, progressive 0.58; indefinite
article 0.81 and habitual 0.69 stay high because their re-draw lands on the common value most of the time. Lects of peoples
with generations of 60-430 yr (46-330 generations in 20 kyr) keep 0.8-0.95, as intended (hazards are per generation).

## Sound realism round (2026-11-04)

Goal (owner): a light ease/markedness drag on sound change, return paths in the catalogue, soft PHOIBLE-shaped inventory
sizes instead of hard caps, clicks at PHOIBLE's rate, and checks that measure living human-voiced lects against PHOIBLE.
Baseline: the shipped run `runs/a24559/languages.json` (309 living human-voiced lects). Iteration used an isolated-lect
harness (protos stepped 20 kyr with no wave or shift; 40-60 lects, ~30 s) to find what removes and creates each segment,
then full runs.

What the harness showed. Every lect undergoes ~300 sound changes in 20 kyr, so nearly every catalogue rule fires at least
once per line and each segment's share settles where its creation and removal rates balance. p, t, k died through
*context-free* stop shifts (lenition.p_f `p > f`, its duplicate S015 and Grimm S177, ~1.3 removals per line), with no way
back except b > p; ʒ came from context-free j > ʒ (S030) and dʒ > ʒ; ɹ, v, the breathy stops from context-free r > ɹ, w > v
and S165 `D > D̤`, none with an exit (S098 was written with bʰ and never matched a breathy stop; Grassmann, S093, does not
parse). Big proto inventories shrank to ~35 because FOLD_RARE folded every new unit under 1% of tokens, which in a 60-unit
inventory is most of them; the size caps did the rest.

Trials (harness, human protos; p/t/k/b share of end states, C quartiles):

| trial | p | t | k | b | ʒ | ɹ | C q1/med/q3 (max) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shipped code | 0 | 25 | 28 | 0 | 81 | 50 | 16/19.5/22 (34) |
| + ease drag (K 0.5) + caps -> soft steer, S030/S098/S165 fixed, 9 return rows | 6 | 26 | 28 | 2 | 10 | 54 | 17/19/22 (33) |
| + p > f and Grimm conditioned (#_, V_: kept after s and obstruents), S163 from geminates, ɹ > ʋ, v > b | 38-65 | 72-90 | 75-92 | 40-60 | 8-20 | 8-20 | 18/20/24 (38) |
| + size anchor to the proto count, FOLD_RARE relative to the mean unit share | 62-65 | 75 | 63-78 | 60-65 | 13-22 | 13 | 17-18/21/24 (50-55) |

EASE_K 0.75 and 1.0 changed nothing beyond sampling noise (the clamp and the catalogue's structure dominate), so it stays
at 0.5 (the light setting: p > f at 0.71x, f-type returns at 1.4x). SIZE_K 0 vs 1 changed little; the anchor and the
relative FOLD_RARE are what keep a wide living spread.

Full run A (`scratchpad/runA`, 14 min, 8 workers; living human-voiced lects, n = 307; shipped in brackets):
p 67% (1), t 75 (8), k 73 (13), b 40 (5), d 31 (8), ɡ 26 (12); ʒ 16 (95), ɹ 17 (56), bʱ/dʱ/ɡʱ 0 (43/42/33), kx 4 (31);
consonants p5/q1/med/q3/p95 13/18/23/27/39, max 59, 3.3% above PHOIBLE's p95 of 42 (12/17/22/26/32, max 35); vowels
5/7/9/12/17, max 28 (5/7/9/12/16); clicks in 3.6% of living human-voiced lects (0). Top-20 overlap with PHOIBLE 14 (11).
Tonal: 37% of living lects (48%). Horizon 10.2 human / 7.6 all (11.0 / 9.2). Checks: the six as before (horizon still
just outside 6-10), living sizes pass, living segments fail on one monoculture, ʁ in 66% (PHOIBLE 6%): r > ʁ (S148,
context-free) with no exit. Kenku tonal 63% (93%), aarakocra 96% (88%), dragons keep their harsh marks (5.9 per lect, was 5.3).
Fix for run B: S148 naturalness 3 -> 2 (uvular r is essentially one European areal spread) and the coda r-loss S102 takes
ʁ too (Standard German coda /ʁ/ vocalization).

Full run B (`scratchpad/runB`, 13 min): ʁ gone from the monoculture list; p 61, t 68, k 58, b 35, d 25, ɡ 25; ʒ 21, ɹ 16,
breathy 0, kx 2; C 13/18/22/26/37 (max 57, 2.2% above 42), V 5/7/10/12/16 (max 23); tonal 39% of living lects; kenku 81%,
aarakocra 92% tonal (so run A's kenku 63% was sampling, 27 lects from 8 protos); horizon 10.2 / 9.2. Living segments failed
on ʊ (53%, PHOIBLE 14%): the Great Vowel Shift row S179 wrote its first stage as əɪ əʊ, which the percept space splits into
vowel + ɪ/ʊ, so every firing brought in two lax vowels with no exit. Rewritten with plain offglides (iː uː > ei ou, the
stage most handbooks give); in the harness ɪ and ʊ are then created by nothing.

Full run C (`scratchpad/runC`, 13 min): ɪ/ʊ gone; ʁ back at 58% (B 49%, A 66%): uvular r mostly arrives by the wave
(contact), which ignored the ease drag. p 61, t 67, k 59, b 45, d 29, ɡ 30; ʒ 16, ɹ 16, kx 7; C 14/18/22/27/40 (max 59,
3.6% above 42), V 4/6/8.5/11/15; tonal 39%; horizon 9.5 human / 9.2 all (inside 6-10). Change for run D: wave adoption
probability x min(1, the receiver's ease factor for the rule) (`lect.ease_factor`, human voices only): a change toward rarer
sounds spreads by contact as reluctantly as it arises at home.

Full run D (`scratchpad/runD`, 14 min; the round's result). Living human-voiced lects, n = 307 (shipped run in brackets):

| | p | t | k | b | d | ɡ | ʒ | ɹ | bʱ/dʱ/ɡʱ | kx | ʔ | clicks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| run D | 68 | 85 | 78 | 43 | 32 | 31 | 14 | 21 | 0/0/0 | 3 | 78 | 3.6 |
| shipped | 1 | 8 | 13 | 5 | 8 | 12 | 95 | 56 | 43/42/33 | 31 | 86 | 0 |
| PHOIBLE | 85 | 72 | 90 | 62 | 48 | 56 | 14 | 2 | 1/0/2 | 0 | 38 | ~1.5 |

Consonants p5/q1/med/q3/p95 14/18/22/27/39 (PHOIBLE 12/17/21/27/42), min 8, max 53, 3.6% above 42 and 4.2% above 40
(shipped 12/17/22/26/32, max 35); vowels 5/6/8/11/16 (PHOIBLE 3/6/9/12/22), max 27. Top-20 overlap 15 (11). In over half
the lects outside PHOIBLE's top 12: ɲ 92, ŋ 89, e 80, ʔ 78, f 74, h 69, ɛ 69, o 68, ɾ 57 (ɲ, ʔ and f are the
over-represented ones: nasal place assimilation and n > ɲ / _i make splits that a phonologist would call allophones, and
this engine counts every distinct segment in the forms as a phoneme). Tonal 38% of living lects (48%); kenku 85% (93%),
aarakocra 96% (88%) tonal; dragons 5.7 harsh-voice units per lect (5.3).

Checks: proto inventories, sisters, shift, long generations, hubs pass as before; **horizon 4.25 human / 5.4 all, now under
6-10** (runs A-C: 10.2, 10.2, 9.5). Runs A-D also carried the parallel lexicon/grammar round's edits as they stood, and the
split-based horizon rests on bins of a few splits, so this move is not attributed; it needs a look before the round ships.
New checks: living sizes pass; living segments pass (no monoculture; p t k m n i a u all within half of PHOIBLE's share).

Constants: EASE_K 0.5, EASE_CLAMP [0.25, 3]; SIZE_K 0.5, SIZE_ANCHOR 0.2, SIZE_CLAMP [0.1, 2]; FOLD_RARE 0.2 of the mean unit
share; INV_MAX 1x PHOIBLE's largest count (130 C, 50 V); CLICK_SHARE 1.5%, CLICK_MIN_C 28, CLICK_PART 0.45.

## Measures and phonemes round (2026-11-04)

Owner rulings to implement: a horizon that needs two windows in a row, with a smoothed read beside it; per-people horizons
(long-lived peoples longer); strict sisters at 0.5; generation length from the current preset; a phonemic inventory with
allophones found by complementary distribution; a small end of inventories at roughly PHOIBLE's rate; food routes that agree
with the receiver's etymology; romanization fixes. Baseline: the shipped run `runs/a24559/languages.json`. Full run F:
`scratchpad/runF/a24559/languages.json` (832 s, 8 workers; it carries the parallel lexicon round's edits as they stood).

**Horizon reads.** The horizon is now the crossing of one half into the first run of two consecutive scored windows under
half (linear from the previous passing window's centre; a run cut short by the end of the curve counts; never failing =
censored at the last scored window's end, a lower bound). Beside it: the former single-window read and a smoothed read
(split-count-weighted moving average over 3 scored windows, first crossing). The measure's strictness (clade Jaccard 0.8,
chance excess 0.03, strict cognates with REC_MIN 2) is unchanged: the failing young splits on the shipped file are real
measure failures (one bud pair with a true share of 0.24 has a strict share of 0.02, its correspondences not recurring;
two-lect splits misgrouped after shifts or contact), and loosening them would read lookalikes. Run F's human splits are thin
at 9-13 kyr (1-3 per window): skipping those windows let the crossing be interpolated across 4 kyr with no evidence (11.0 in
the run). Sparse windows now widen by 0.5 kyr per side, up to 1 kyr, before they are skipped (`SPLIT_WIDEN`,
`widened_kyr` on the curve row).

| file | human (two-window / smoothed / single) | long-lived (gen >= 60 yr) | elves | dragons | dwarves | all lects |
| --- | --- | --- | --- | --- | --- | --- |
| shipped | 4.25 / 4.35 / 4.25 | 15.3 | >= 16 (censored) | >= 22 (censored) | 3 splits | 9.0 |
| run F, in the run | 11.0 / 13.2 / 11.0 | >= 22 (censored) | >= 14 | >= 21 | 3 splits | 13.0 |
| run F, widened windows | 10.25 / 10.5 / 10.25 | >= 22 (censored) | >= 16 | >= 22 | 3 splits | 13.0 |

The shipped file's 4-7 kyr dip (two overlapping windows at 0.20 and 0.36) is a genuine run of two, so it stays a fail
there; in run F those windows recover 0.55-0.67 and the human curve holds 0.9-1.0 to 9 kyr and drops to 0 from 10 kyr. The
human read moved from 4.25 to 10.25 between the two files with no change to the measure beyond the run rule; most of the
move is the lexicon round's replacement sources (not calibrated here: replacement belongs to the lexicon builder). The
check asserts human in 6-10 and the long-lived horizon longer than the human one or censored; the long-lived part passes on
both files, the human part fails run F by 0.25 kyr.

**Sisters.** `sister_distant` now scores the strict cognate share (bar 0.5) and reports loose and true beside it: shipped
0.470 strict (0.533 loose); run F 0.495 strict (0.568 loose, 0.605 true), cross-family 0.0001. Fails by a hair; not
calibrated here (replacement curve).

**Generation length.** The language pass now takes each line's generation length from the current preset when it differs
from the stored run by more than 5% (`inputs.generation_overrides`, mirrors the lineages code: life-history T, dragon ages
for flying megafauna), logs it, and exposes it as `constants.generation_overrides`. On a24559 only aarakocra: 5.82 yr
stored, 18.58 yr now (kenku 19.27). Check 5 passes in run F: human 12.9 rules per kyr, long-lived 3.7, ratio 3.45.

**Phonemes and allophones.** `inventory.phonemic` reads the lect's own forms: a rarer sound is an allophone of a phoneme
when they differ in one feature and never stand in the same environment, under one of seven tests (nasal place before a
consonant, palatal before front vowels or j, intervocalic, word-final, word-initial, nasal vowel next to a nasal, ʔ before an
initial vowel or in hiatus). A phoneme cannot itself be an allophone, and two allophones of one phoneme must not share an
environment. The inventory keeps phonemes in `consonants`/`vowels` and allophones beside them; new words and repairs draw
phonemes and then realize the allophones, so the allophony persists. Checks, the size steer (counts) and the output use the
phonemic inventory. On the shipped forms almost nothing is allophonic: ŋ, ɲ and ʔ stand before vowels and word-initially
(11,767 vowel-initial words), so they are genuinely contrastive on the surface. In run F, 92 of 313 living human-voiced lects
have at least one allophone (mean 0.47): intervocalic voicing (d of t 12, z of s 9, ɡ of k 9, v of f 7), nasal vowels (ã 8,
ũ 7, ĩ 5), final devoicing (p of b 5). ɲ/ŋ/ʔ stay phonemes at 90/86/75% (PHOIBLE 42/64/38%), now a catalogue and proto-draw
question (draft-language-plain-stops-erode).

**Small end.** PHOIBLE: 1.4% of languages have 10 or fewer consonants, 6.2% 12 or fewer. Protos matched it, but lines drifted
up (harness: 7 -> 11, 10 -> 13 consonants in 20 kyr) because the catalogue offers a small inventory about five times as
many splits as mergers and nasal place assimilation was not steered. Changes: assimilation counted by the outputs it makes
(`lect.touched_by`), wave adoption damped by the size steer as well as the ease drag, SIZE_ANCHOR 0.2 -> 0.12, SIZE_CLAMP
[0.1, 2] -> [0.02, 3]. Harness (isolated human lects, 20 kyr): 8-C protos end at a median of 10 (was 12), 22 at 20 (21), 35
at 28 (26). Run F living human-voiced consonants p5/q1/med/q3/p95 11/16/19/23/39 (PHOIBLE 12/17/21/27/42; run D
14/18/22/27/39), min 8; 3.2% have 10 or fewer, 11.2% 12 or fewer: the small end now arises, slightly more than PHOIBLE's.
Vowels 4/6/9/11/15.

**Plain stops (regression, not this round's).** Run F: p 42%, t 53%, k 44% (run D 68/85/78, PHOIBLE 85/72/90), so the
segment-frequency check fails. Harness A/B: the size constants make no difference (k 0.38 vs 0.34); the lexicon's replacement
sources (coin 0.15 -> 0.03) do (22-C protos, n = 96: t 0.50 vs 0.71, k 0.43 vs 0.64 with the old shares). A coinage refills
the common stops from the inventory; without it lenition wears them away. Filed as draft-language-plain-stops-erode.

**Food routes.** One source of truth: each route hop is keyed by the etymology step that made it (`route_ev`), and a hop's
status is read from the receiver lect's own word (`now`: kept / replaced / lost, `by`: the step that replaced it). Run F:
2911 hops, 1906 kept and 1005 replaced (into living lects 1792 and 867).

**Romanization.** Full mode spells ɹ as ř, so ɹ and ɾ no longer share r (full mode stays injective up to MERGES). Book mode
reads a `book` column: cç ky, ɟʝ gy, ɡɣ g, qχ q, dɮ dl (no more "gyyh"). No romanization failures in run F.

Checks in run F: proto inventories, shift, long generations change less, hubs/isolated, living sizes pass; sisters (0.495),
horizon (11.0 in the run, 10.25 with widened windows) and living segment frequencies (plain stops) fail.

## Word families and derivation round (2026-11-04)

Goal (owner): derivations a linguist believes (each affix has a meaning; base > target fits it), at most two felt affixes
on a word, opaque old derivations read as simple roots, PIE-like root families that daughters inherit, coinage well under
15% of replacements, and the replacement curve recalibrated (Swadesh 80-86%/kyr, frequent words several times slower,
sisters >= 0.5, human horizon 6-10 kyr, cross-family < 0.15). Baseline: the shipped run `runs/a24559/languages.json`.

Mechanism. `data/derivations.tsv` (new; ~200 rows over agent, thing, place, little, like, do, cause, plus renewals and
function-word reinforcers; sources in its header: Buck 1949, Urban 2012, Koch 2008, Pokorny/LIV2, WOLD, Heine & Kuteva
2002, CLICS3 counts joined at load) is the only way an affix meets a base. Felt layers (`word_layers`) stop at a
derivation older than OPAQUE_KYR (3 kyr), a replaced base or a renewal; MAX_AFFIXES 2, MAX_MORPHEMES 3. A word never
derives, compounds or shifts back into a meaning it had (`_worn`: SING > SONG > SING, KNIFE > CUT > KNIFE, LEG + CLAW =
FOOT > FOOT + CLAW = LEG, PUSH > GRIND > PUSH were all common on run E1). Failed derivations fall back to compound, shift,
a weaker CLICS shift (4 families; 3 is mostly chance: DOG ~ MOON), borrow, then coin. Protos derive part of their stock
from their own roots, and every word carries `roots` (architecture.md §6, §11). Curve: FREQ_SPREAD 10 -> 3 (rare words 3x
the rate of frequent ones), BASE_REPLACE re-solved to 0.0026726 for 86%/kyr, history.REPLACE_SCALE 1.25 -> 1.0.

Harness (two sister lineages, no contact, 8-12 seeds): spread 4 / scale 1.0 kept 0.857/kyr and gave true shared roots
0.64 at 1.5 kyr and 0.09 at 10 kyr (spread 10 / scale 1.25: 0.60 and 0.105). Analytically, at 86%/kyr spread 4 -> 3 keeps
the 1.5-kyr share within 1% and cuts the 10-kyr share 17%; spread 2 at 86.5% would help both bars a little more, but that
is no longer "several times slower".

Plain stops (draft-language-plain-stops-erode, from the measures builder). With coinage down to 3% nothing refilled the
stops that lenition, spirantization, Grimm and debuccalization wear down: in the isolated-lect harness (96 human lects,
22-C protos, 20 kyr) p/t/k fell from 24% of consonant tokens to 3.5%, and lects with p/t/k from ~95% to 0.48/0.50/0.43.
The lexicon alone keeps the shares (sound change off: unchanged after 20 kyr). New `lect` stop steer (STOP_NORM 0.33,
STOP_K 2, clamp 0.1-4; architecture.md, rule weights): harness 0.69/0.78/0.73 (K 1: 0.60/0.70/0.65; K 3 saturates at
0.72/0.81/0.70, because the pick redraws among applicable rules). Still open there: ʔ is 17% of consonant tokens at the
end, mostly from S042 prothesis (#_V) that nothing removes, and j 10% from glide formation.

Full runs (8 workers, ~14 min each; scratchpad `runE`..`runE4`):

| run | change | sisters strict | horizon human (smoothed) | p/t/k living | coin share of replacements |
| --- | --- | --- | --- | --- | --- |
| shipped | - | 0.470 | (other measure) | 0.01/0.08/0.13 | 0.33 of latest steps |
| E1 | table, roots, spread 4 | 0.512 | 10.6 (11.66) | 0.38/0.53/0.37 | 0.083 |
| E2 | spread 3, no derive round trips | 0.509 | 11.0 (13.27) | - | - |
| E3 | + stop steer | 0.498 | 10.25 (10.43) | 0.51/0.75/0.65 | - |
| E4 | + no compound/shift round trips, weak shift 4 families | 0.504 | 10.67 (11.11) | 0.55/0.80/0.70 | 0.095 |

E4 (the round's result, `scratchpad/runE4/a24559/languages.json`): cross-family strict 0.0001 (loose 0.003); replacement
events in living lects derive 0.22, compound 0.18, borrow 0.18, shift 0.17, renew 0.16, coin 0.095; living segments and
sisters pass; the horizon stays just over 10 (E1-E4: 10.6, 11.0, 10.25, 10.67, with single-window reads of 4.5-10.6: the
bins near 10 kyr hold 2 splits each, so run-to-run noise is about the size of the gap). What holds deep sisters together
(E2, pairs parted 5-9 kyr): of core concepts sharing a root, 38% are inherited untouched, 11% are later loans and 51% were
re-formed after the split from a shared root (renewals 40% of those, compounds on a shared head 43%, shifts 31%,
derivations 19%; several per word). Root families make words look related after their parts are replaced, so the
horizon now leans on the cognate test's strictness more than on the replacement rate.

Before (shipped, 10 random derived words of living human lects): ROUND + 'like' = sharp, RAIN + 'agent' = worm, HOUSE +
'little' = snow, YESTERDAY + 'little' = belly, SAY + 'do' > SPEAK + 'thing' = village > house. After (E4): WIND + 'do' =
blow; FLY + 'agent' = bird, later BIRD + 'little'; EAR + 'do' = hear > shift 'carry' > CARRY + 'thing' = burden; FOOT +
'do' = walk > WALK + 'place' = road; DRINK + 'place' = spring; LAUGH, GIVE + 'intens' (renewals); WHO + PERSON = who >
'what' > WHAT + 'place' = when > 'if'. Root families (E4, one true family each): *tjaʔnɛ 'dig' > dig, grave, scratch,
claw, axe, split; *ɲamukna 'sky' > day, sun, moon, sunrise, hot; *rɔ̃phɔbnib 'burning' > burn, fire, heat, hot, red,
smithing; E1 p286 *tɔ 'who' > who, what, where, when, how (and not). Living human lects average 209 roots, 34 of them with
3+ words, the largest 14 words.

## Typology and grams round (2026-11-04)

Problem: the sketch generator found 320 of 621 living lects on the shipped run (272 of 623 on run E4) whose typology
contradicted their live grams ('case: none' with a live locative, 'number: none' with a live plural, the negator on the
other side from the negation feature, an inclusive/exclusive 'we' with one form). The two layers were drawn and drifted
apart; drift had just been switched on.

Mechanism (architecture.md §7, "One system"): the drift now moves `Grammar.aims`; the shown `Grammar.typology` reads every
gram-realised feature from the live grams (`grammar.realise`, `grammar.REALISED`), so it cannot contradict them. The aims
steer the ladder: per category the aims mark and no live gram realises, `PRESSURE` 0.03 per generation (x the social
recruit factor) recruits from that category's attested paths; a bound gram the aims no longer want erodes
(`UNWANTED_LOSS` 0.002 x social loss); an unwanted gram that binds anyway sets the aim (`_adopt`). After an order flip,
free grams (level 0) move to the new side and bound ones stay (Givon); a negator stranded on the old side lets a
reinforcer be recruited on the new one. Clusivity is set from what exists (two distinct 'we' forms in the lexicon; the
lexicon has one 'WE', so 'no' everywhere); object agreement is 'none' (no gram marks the object). Calques on shift write
the aim (`grammar.Shown`). `grammar.clashes` lists contradictions; `checks.typology_consistency` counts them per run.

Harness (scratchpad `gramG/sim.py`: 40 human lects, 700 generations through `lect.step`, l2 0.5, 160k speakers): shown
value = aim for number/past/future/progressive in 55-65% of lects at PRESSURE 0, ~80% at 0.02-0.04; median live functions
6 at 0, 10-11 at 0.02-0.04. Aim retention is unchanged by the pressure (0.82-0.95 / 0.74-0.81 / 0.64-0.69 / 0.51-0.57).

| run | clashes (sketch, any) | clashes (`grammar.clashes`) | human aims kept: very stable / stable / medium / fickle / very fickle | human shown kept | long-lived aims kept | median live functions |
| --- | --- | --- | --- | --- | --- | --- |
| shipped a24559 | 320 / 621 | - | (no drift) | - | - | 2 |
| run E4 (scratchpad `runE4`) | 272 / 623 | - | 0.85 / 0.76 / 0.68 / 0.55 / 0.76 (runB, typology) | - | - | 5 |
| run G (scratchpad `runG`, this round) | 0 / 622 | 0 / 622 | 0.89 / 0.73 / 0.64 / 0.56 / 0.74 (n 103) | 0.89 / 0.74 / 0.59 / 0.64 / 0.68 | 0.95 / 0.92 / 0.89 / 0.81 / 0.83 (n 241) | 10 |

Run G shown values (living lects): number marked 66% (E4 58%), case none 28% (39%), definite article none 60% (71%), past
marked 55% (57%), future 54% (56%), progressive 38% (36%), gender none 58% (63%), verb agreement none 44% (35%),
clusivity no 100% (58%). Shown = aim for 72% of realised-feature values (alignment 0.94, negation 0.96, number 0.76, past
0.81; low where the grams cannot yet carry the aim: verb agreement side 0.40, causative 'bound' 0.48, clusivity 0.55,
object agreement 0.58). Gram load doubled (median live functions 5 > 10; languages.json 138 MB, as before). Other checks as
on run F: sisters 0.48 (threshold 0.5, 0.495 on run F), human horizon 10.7 kyr (fails on E4 and F too), segment
frequencies red (p/k, the other lane's), the rest green; the six sketches regenerate with no "Note on the data" line.

Judgement calls: a free case-function gram (a postposition at level 0) counts as case marking, matching the sketch's
checker; a stricter reading (clitic or tighter) would make 'a few cases' rarer and needs the sketch to agree. A lone
witnessed evidential shows as 'direct+indirect'. Diminutive, agent noun and causative read the grams only, not the
lexicon's derivational affixes (word formation, every lexicon has them).

## Sinks round (2026-11-04)

Problem (run E4, `scratchpad/runE4/a24559/languages.json`, living human-voiced lects vs PHOIBLE's share of languages): ŋ 86%
(64%), ɲ 89% (42%), ʔ 71% (38%) too common; p 55% (85%) and k 70% (90%) too rare. A sink is a segment with a strong one-way
path in and weak paths out. Baseline for every comparison below: run E4 (same world, the catalogue before this round).

**Audit.** Isolated-lect harness (`scratchpad/sinkH/flow.py`: human protos drawn from PHOIBLE's size distribution, stepped
20 kyr in 0.5-kyr intervals, no wave, shift or contact; every rule firing, fold and lexicon step diffed for consonant tokens).
Flows are consonant tokens per lect per kyr; "lexicon" is replacement (net positive for most sounds: words grow longer over
time); "lects" is the share of lects with the phoneme, proto -> end.

| seg | before (E4 catalogue, 48 lects): lects; in / out; main paths | after (this round, 96 lects, seed 7) |
| --- | --- | --- |
| ʔ | 0.60 -> 0.94 (token share 1.4% -> 15.5%); in 11.8 / out 5.5; in: S042 prothesis 4.3 (88 tokens a firing, 31 of 48 lects), lexicon 4.6 (compounds of ʔ-initial words), S037 p t k > ʔ / _# 1.4, S038 0.9, S036 0.3 (S036 = S037's k part, drawn twice); out: S191 1.8, tone 0.8 | 0.56 -> 0.59 (2.7%); in 5.6 / out 5.1; S042 1.0, S037 1.3; out: S197 initial loss 1.9, S191 1.4 |
| ɲ | 0.50 -> 0.83 (2.2% -> 6.4%); in 4.0 / out 2.4; in: S057 n > ɲ / _j, _i 1.6, lexicon 2.0; out: only S121 compensatory lengthening 0.6 and final C loss: no depalatalization at all | 0.51 -> 0.31; in 3.5 / out 4.4; S198 n > ɲ / _i 1.9; out: S199 1.8, S202 1.7, S200 0.4 |
| ŋ | 0.67 -> 0.69; in 6.7 / out 6.8: S144 n > ŋ / _# 4.2 against S143 ŋ > n / _# 3.9 (they cycle, ~3 firings each per lect) | 0.74 -> 0.75, unchanged (balanced, not a sink; within 1.5x PHOIBLE) |
| j | 0.83 -> 0.98 (4.4% -> 10.7%); in: S174 ɛ ɔ > je we 2.9, glide formation 1.6, hiatus glide 1.5; out: S121 2.0, S041 1.1. Coalescence rows (S056-S058) left the j behind (t > tʃ / _j gave tʃj) | 0.86 -> 0.95 (5.6%); out: S201 j > ∅ / V_V 7.7, coalescence absorbs the j |
| p | 0.92 -> 0.65; in: S097 b d g > p t k 7.8; out: S022 p > ∅ 5.0, lenition.p_f 4.5, S010 p > b 2.6 (S010 = the demo intervocalic voicing again), Grimm S177 1.3 | 0.92 -> 0.74 |
| k | 0.94 -> 0.62; out: S003 k > h 2.0, S012 k > g 1.9 (twin), S177 1.9, S004 k > x 1.1 | 0.92 -> 0.75 |
| w | 0.77 -> 0.33; out: labial.w_v w > v 4.1 (context-free), S027; in: glide formation, l-vocalization | 0.82 -> 0.56 |
| ʋ | 0.04 -> 0.40; in: S195 ɹ > ʋ 1.0; out: none (pure sink) | 0.03 -> 0.03 |
| ʁ | 0.02 -> 0.44; in: S148 r > ʁ (context-free) 1.8; out: S102 coda loss 0.2 | 0.01 -> 0.22 |

The catalogue view (expected firings per kyr of rules that can rewrite or make a segment, from the weighted pool at the
lect's state; `HPATHS=1`) says the same in another unit, with one lesson: the engine draws ~13 changes per kyr, so in 20 kyr
nearly every applicable rule fires one to four times per line, and a segment's presence is decided by whether a
near-total exit (context-free, or "#_, V_") has fired since the last creation. Weight then matters little: S197 as a
context-free ʔ > ∅ gave ʔ 0.14-0.16 at naturalness 1-2 and 0.74 at 0. Hence conditioned exits rather than weights.
Proto draws are not the cause (600 draws: ʔ 0.49, ɲ 0.56, ŋ 0.81, about the 1.2-1.4x of every segment at a median of 23 C).

**Changes** (tools/language/knowledge_tables.py, regenerated tsv; ids stable, new rows appended):
- S042 prothetic ʔ: `∅ > ʔ / #_V́`, before a stressed initial vowel only (German Apfel, Abend; a boundary onset, usually
  absent before unstressed vowels, Kohler 1994). Still naturalness 1 (rules.ROW_OVERRIDES) x 0.15 (history.RULE_WEIGHT).
- S056/S057/S058 coalescence: `t, d, s, z > tʃ, dʒ, ʃ, ʒ / _j ; then j > ∅ / [+sibilant]_`, `n > ɲ / _j ; then j > ∅ / ɲ_`,
  `l > ʎ / _j ; then j > ∅ / ʎ_` (Latin vinea > vigna, palea > paglia, English nature): the j is absorbed. S057 loses its
  `_i` half, now S198 `n > ɲ / _i` at 2 (Polish nie, niebo; allophonic in Japanese).
- S022 p > ∅ (Celtic, a one-step shortcut of p > ɸ > h > ∅ the catalogue has stepwise) 3 -> 1. S148 r > ʁ 2 -> 1 (one
  areal spread from Paris), S195 ɹ > ʋ 2 -> 1 (one British innovation).
- New exits: S197 `ʔ > ∅ / #_` 3 (Middle Chinese ʔ- > Mandarin zero initial: ʔan > ān); S199 `ɲ > j / V_` 3 (Romanian
  vinea > vie, cuneus > cui); S200 `ɲ > n / _C, _#` 3 (Slovene konj [kɔːn]); S201 `j > ∅ / V_V` 2 (Proto-Greek *trejes >
  treîs); S202 `ɲ > n` 1 (Finnic: Proto-Uralic *ńëlɜ > Finnish nuoli, Hungarian nyíl); S203 `ʋ > v` 3 (OHG w > German [v]);
  S204 `β > w / _C, _#` 3 (Catalan bibere > beure, debitum > deute).
- `rules.SAME_AS` (drawn once): S010-S012 (p t k > b d g / V_V, parts of the demo intervocalic voicing), S005-S007 (b d g >
  β ð ɣ / V_V, parts of the demo spirantization), S036 (k > ʔ / _#, part of S037).
- Keep steer (`lect.keep_part`, KEEP_SHARE 0.7, KEEP_FACTOR 0.25; architecture.md §5): a rule that would leave no token of
  a near-universal phoneme (p t k m n l j w i u a) in the lect's frequent words is drawn a quarter as often, at home and by
  wave. This is the mechanism draft-language-plain-stops-erode proposed. The catalogue changes alone gave p/k 0.48/0.48 on
  run H (k worse than E4's 0.70; harness 0.66/0.64 against 0.67/0.65 on the E4 catalogue): with every applicable rule
  firing a few times, the near-total stop lenitions (lenition.p_f and Grimm `#_, V_`, k > x / V_ with k > tʃ before front
  vowels) take the last p or k in most lines whatever their weights; harness with the steer 0.68-0.81 / 0.72-0.76 (three
  seeds), no slower (the check stops at the first surviving token).
Not changed: S143/S144 (ŋ is balanced; they cycle, a churn of the final nasal, not a sink), the ease drag constants.

**Full runs** (8 workers, ~15 min; living human-voiced lects, lect share / family-weighted share over 96 true families):

| run | ʔ | ɲ | ŋ | p | t | k | w | ʁ | ʋ | ɹ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PHOIBLE | 0.38 | 0.42 | 0.64 | 0.85 | 0.72 | 0.90 | 0.85 | 0.04 | 0.02 | 0.03 |
| E4 (baseline) | 0.71/0.81 | 0.89/0.88 | 0.86/0.84 | 0.55/0.53 | 0.80/0.76 | 0.70/0.64 | 0.41/0.45 | 0.49/0.47 | 0.30 | 0.16/0.21 |
| H, catalogue only (`scratchpad/runH`) | 0.46/0.57 | 0.42/0.39 | 0.86/0.83 | 0.48/0.52 | 0.70/0.67 | 0.48/0.53 | 0.50/0.49 | 0.37/0.36 | 0.04 | 0.34/0.31 |
| H2, + keep steer (`scratchpad/runH2`) | 0.47/0.52 | 0.36/0.39 | 0.86/0.82 | 0.66/0.71 | 0.89/0.88 | 0.81/0.84 | 0.71/0.70 | 0.38/0.32 | 0.01 | 0.28/0.30 |

H2 (the round's result, `scratchpad/runH2/a24559/languages.json`): ʔ 1.24x, ɲ 0.86x, ŋ 1.34x PHOIBLE; p 0.66, k 0.81.
Checks: proto inventories, sisters (strict 0.502, loose 0.563, cross-family 0.0001), shift, long generations (ratio 3.7),
hubs, living sizes (C 11/16/20/24/39, 4.2% above 42), living segments (top-20 overlap 17, was 15) and typology pass; the
human horizon fails as before at 10.5 (smoothed 10.6; E4 10.67). Kenku tonal 85% (E4 70%), aarakocra 76% (84%; 25 lects
from few protos); dragons keep 4.5 harsh units per lect (4.6). Still over-represented: ʁ (0.38, 10x), ɹ (0.28: with ɹ > ʋ
rarer the r > ɹ sink shows), ɦ (0.27, 9x); under: ɡ 0.31 (0.56), d 0.30 (0.48), tʃ 0.28 (0.39).

## Compounds and shifts round (2026-11-04)

Goal (owner): compounds and semantic shifts a linguist believes. The shipped run (`runs/a24559`, = H2) built compounds
from a class head plus a CLICS neighbour or a quality (halfling d646.2's family of 'tree': TREE + RED = 'fire', TREE +
SHARP = 'grass', TREE + BONE = 'seed', GRASS + GREEN = 'bark', FOOD + TOOTH = 'egg') and shifted words along any CLICS
edge of 4+ families, chained (SEED > EYE, EGG > NAME, PULL > SUCK > EAT > TREE); word families followed every link.

Mechanism (architecture.md §6):
- **Compounds only from recipes**: `data/compounds.tsv` (205 rows over 137 targets; 41 of them `SELF`, generic +
  specific renewals; sources in its header: Urban 2012, Brown 1976 / 1999, Witkowski & Brown, Buck 1949, WOLD, the
  Southeast Asian generic + specific compounds). The head is the category: SKIN + TREE = bark, HAIR + BIRD = feather, EYE
  + DAY = sun, EYE + WATER = spring, SUN + NIGHT = moon, WATER + SALTY = sea, LAND + WATER = island, CHILD + WOMAN = girl,
  MOTHER + BIG = grandmother, FATHER + SMALL = uncle, MAN + BIG = chief, FIVE + ONE = six, HAND + TWO = ten, DOG + BIG =
  horse, FRUIT + EARTH = potato, DOG + SEA = seal. ELABORATIONS is the recipe of the elaborated concepts (soured milk,
  calf, pasture: without it they fell to fresh roots, +2 points of coinage in the contact harness). No recipe, no
  compound (EGG, FLOWER, TREE, GRASS, verbs, qualities). A generic + specific compound or a function-word reinforcement
  happens once per word ('deer-animal-animal' and 'they-that-that' were in the first full run).
- **Shifts**: a CLICS3 edge of >= 5 families (>= 6 for the Swadesh-100 and frequency classes 1-2) between concepts of one
  semantic field and part of speech, or an attested pathway (42 `shift` rows in derivations.tsv: TREE > WOOD, SKIN >
  BARK, SUN > DAY, BREAST > MILK, TONGUE > LANGUAGE, SKY > GOD, BREATH > SPIRIT, SEE > KNOW, HAND > FIVE, and
  grammaticalization BELLY > IN, WITH > AND, ONE > SOME, SAY > BECAUSE; Buck, Wilkins 1996, Sweetser 1990, Heine & Kuteva
  2002). The weak 4-family fallback is gone; a word shifted within SHIFT_CHAIN_KYR (3) is not taken again. Floors tried
  in the contact-free harness (`scratchpad/compJ/harness.py`, 12 protos x 10 kyr): 6 / 10 -> coin 24% (HEAD 18%), 5 / 8 ->
  23%, 5 / 6 -> 22%; with the tool / plant / kin diminutive renewals (RENEW_LITTLE: couteau < cultellus, abuelo <
  aviolus) and the elaboration recipes, the 700-generation contact harness (`compJ/contact.py`) gives coin 10.8% (HEAD
  10.4%).
- **Felt roots**: `roots` are what a speaker still analyses (`felt_roots`, re-read every step): a transparent
  derivation, compound or taboo paraphrase (younger than OPAQUE_KYR, parts not replaced since) has its parts' roots, a
  renewal keeps the word's own; a proto root, coinage, old derivation, shift, loan or substrate word is a root of its own
  from that step (`root_step`; output.py's root table points at that node of the word's chain, so no nodes are added).

Isolated sister lineages (`compJ/sisters.py`, 24 protos, two daughters 1.5 kyr apart, no sound change): core words of
identical form 0.682 (HEAD 0.669), same true root 0.789 (0.753): the round keeps sisters closer, not further apart.

Full runs (8 workers, ~16 min):

| run | sisters strict (loose) | horizon human (smoothed) | homophones, median per lect | coin share | file |
| --- | --- | --- | --- | --- | --- |
| shipped (H2) | 0.502 (0.563) | 10.5 (10.62) | 0.136 | 0.100 | 139 MB |
| I, hiatus builder, HEAD lexicon (`scratchpad/runI`) | 0.438 (0.504) | 10.67 (11.11) | - | - | 139 MB |
| J, this round (`scratchpad/runJ`) | 0.475 (0.534) | 10.67 (11.11) | 0.128 | 0.104 | 158 MB |
| J2, + once-per-word renewals, root nodes reused (`scratchpad/runJ2`) | 0.479 (0.544) | 10.25 (10.49) | 0.125 | 0.104 | 149 MB |

The sisters check fails on J and J2, but the uncommitted sound-change work in the same tree does it: run I (HEAD's
lexicon with that work) is at 0.438, below J2, and the harness shows the lexicon change raising sister similarity. The
horizon moves toward 10 (10.25). Replacements in living lects (J2): derive 0.22, renew 0.20, borrow 0.19, compound 0.15
(0.18), shift 0.13 (0.18), coin 0.104 (0.100). Word families of living human lects: 321 roots per lect (211), 9 families
of 3+ words (32), the largest 5 words (15), 25% of words in a family (62%): most proto derivations are older than 3 kyr,
so a speaker no longer feels them (draft-language-felt-vs-etymological-roots asks whether to keep an etymological view
too). The file grows 10 MB: 2.3x as many root-table entries (every opaque word is a root).

Before (shipped, 15 random compounds of living human lects, seed 1): ANIMAL + FISH = seals, SEED + BROWN = peanuts, GRASS +
ROUND = rye, STICK + SHARP = spear, VILLAGE + HOUSE = camp, GRASS + SHARP = tree, MOON + SEA = tide, WHO + PERSON = who,
SMOKE + LAND = dust, BIRD + WHITE = animal, TREE + LONG = twig, GRASS + BONE = seed (twice), FEATHER + HEAD = hair, YOU +
OTHER = you (three times in one word). Shifts: DIG > scratch, WHO > what, FOREST > grass (twice), THREE > four, GIRL >
child, SALTY > sour, LAKE > water, WOOD > tree, SQUEEZE > grind (and chains such as SCRATCH + 'thing' = claw > hand).

After (J2, same sampler): PERSON + NEW = guest, HOUSE + MANY = village, CHILD + TREE = fruit, HAND + LEFT = north, EYE +
SKY = sun (twice; then SUN + FALL = west), STICK + SHARP = spear, FATHER + BIG = grandfather, STONE + SHARP = knife, HE +
THAT = he, PERSON + GOOD = friend, ARM + BIRD = wing, SEED + ROUND = lentils, WATER + SALTY = sea, YOU + OTHER = you.
Shifts: HE OR SHE OR IT > thou, TAKE > hold, DAUGHTER > girl, HEAR > smell, CLOUD > fog, FLOW > run, HAND > five, WASH
> wipe, HORN > tooth, RUN > flow. Still thin: function words are often fresh roots (AT, BECAUSE, WITH;
draft-language-function-words-coined).

## Hiatus round (2026-11-04)

Problem (shipped `runs/a24559/languages.json`): 14.6% of living-lect words held a run of 3+ vowels (human-voiced 15.5%,
halfling 18%, hobgoblin 19%), 2.4% three identical vowels in a row (tiiin, niiiini, kuuuŋ). Baseline for every comparison
below: the shipped run (same world, HEAD code).

**Measure.** Isolated-lect harness (scratchpad `hiatusI/flow.py`, 48 human protos, 20 kyr, no wave): VVV share 0 at the
proto, 0.035 at 4 kyr, 0.18 at 20 kyr. Hiatus made per lect per kyr (VV junctions): lenition.h_loss (h > ∅, context-free)
11.4, S201 (j > ∅ / V_V) 8.2, S176/S179 (diphthongization, mostly real diphthongs) 3.9/3.7, S027 (w > ∅) 2.8, S022, S009,
S008. Nothing resolved it: S126 (elision) and S175 (monophthongization) failed to parse and never fired; the only repairs,
S125/S127 (hiatus glides, glide formation), were family "epenthesis", capped at two firings a line.

**Changes.** (tools/language/knowledge_tables.py, tsv regenerated, ids stable, S205-S207 appended.)
- Catalogue: S125-S127 become family "hiatus"; S126 rewritten so it parses, `V[−stress] > ∅ / _V[−high]` (V1 elision:
  Greek ἀπ' ἐμοῦ, French l'ami; the commonest resolution, Casali 1997); S175 staged so it parses (`ai > eː ; then au > oː`,
  Latin causa > cosa, Sanskrit sandhi a + i > e); S205 `e, ɛ > j / _V[−high]` (Vulgar Latin vinea > *vinja, palea >
  *palja); S206 Attic contraction (*genea > genē, géneos > génous, timáomen > timômen); S207 `∅ > j / e_V[−high]` (Old
  Portuguese chẽo > cheio, cẽa > ceia).
- Repair path (architecture.md §5 "Hiatus"): `lect.normalize` fuses two vowels of one quality (long where the lect has long
  vowels, short where not, as Old Portuguese door > dor; two level tones make a contour) and simplifies word-initial
  geminates; `Lect.resolve_hiatus` fires the line's preferred hiatus repair once a change leaves >= HIATUS_MIN (8) new
  hiatus junctions in the lexicon, HIATUS_REPAIRS (1) firing (preference: weight x a lognormal keyed by the proto line, so
  daughters keep it). `inventory.legal` rejects VVV, identical VV and initial geminates; `repair` resolves them (fusion,
  glide, V1 elision), so coinages, compounds and loans come out clean.
- First version (3 repairs after any new hiatus, run I, `scratchpad/runI`, HEAD lexicon) cut VVV to 0.9% but put ~18 repair
  firings into each human lect (1.5 before) and took sisters strict 0.502 > 0.438. A two-sister harness with a wave
  (`hiatusI/sis.py`, 96 pairs, 6 + 2 kyr, 3 seeds) gave strict 0.382 (HEAD) / 0.346 (3 repairs) / 0.366 (1 repair,
  HIATUS_MIN 8); fusion to long always, higher HIATUS_MIN, spreading repairs by wave and S175 off made no difference
  inside the noise (~0.01).

**Final run** (run I2, `scratchpad/runI2/a24559/languages.json`, the worktree with the compounds/shifts lexicon too):

| measure | shipped | run I2 |
| --- | --- | --- |
| words with a 3+ vowel run, all living / human-voiced | 0.146 / 0.155 | 0.016 / 0.012 (halfling 0.007, hobgoblin 0.017, kenku 0.030) |
| three identical vowels in a row | 0.0236 | 0.0002 |
| words with any VV / identical VV | 0.525 / 0.200 | 0.260 / 0.010 |
| word-initial geminates | 0.0007 | 0.0000 |
| sisters strict / loose / true | 0.502 / 0.563 / 0.591 | **0.494** / 0.564 / 0.603 (FAIL, bar 0.5) |
| human horizon | 10.5 | 12.0 (fails as before, now longer) |
| living human-voiced p / k / t | 0.66 / 0.81 / 0.89 | 0.72 / 0.87 / 0.93 |
| ʔ / ɲ / ŋ (x PHOIBLE) | 1.24 / 0.86 / 1.34 | 1.21 / 0.82 / 1.32 |
| ɾ share | 0.55 | 0.61 (2.4x, the monoculture bar is 2.5x; run I had 2.58x and failed) |
| long-vowel lects (human-voiced) / vowels p5-p95 | 0.58 / 4 6 8 11 15 | 0.76 / 5 7 9 12 15 |
| kenku / aarakocra tonal | 0.85 / 0.76 | 0.89 / 0.76 |
| dragons' harsh units per lect | 4.5 | 4.6 |
| core syllables, all living; corr(length scale, syllables) | 2.69; 0.31 | 2.22; 0.28 |
| core syllables by length scale <0.85 / 0.95-1.05 / 1.2-1.4 / >1.4 | 2.48 / 2.71 / 2.99 / 3.67 | 2.12 / 2.21 / 2.52 / 2.58 |

Other checks pass (proto inventories, shift, long generations, hubs, living sizes, living segments, typology). Words are
shorter by ~0.45 syllables everywhere: the old counts included hiatus vowels that were syllables only on paper (kaha >
kaa counted 2). The slope with syllable space is kept; the small-space end is ~2.5 syllables, not 3+.

## Final run (2026-11-04 evening)

Baseline: the shipped run of the morning (same world). Code: all rounds of 11-04 together, plus two exits for the tap
(S208 ɾ > r word-initially, Spanish; S209 ɾ > l, Polynesian). Without them the combined run read ɾ in 67% of living lects
(2.7x PHOIBLE's 0.25) and failed the segment-frequency check; ɾ had one source (S013 flapping) and no exit. With them the
check passes (no monoculture, top-20 overlap 18; p / t / k 0.72 / 0.89 / 0.82).

Final `runs/a24559/languages.json` (two runs identical apart from timing): sisters strict 0.499 / loose 0.563 / true
0.599 (bar 0.5 on strict: fail); human horizon 10.67 kyr (smoothed 11.11; target 6-10: fail), long-lived censored at 22;
rules per kyr human 15.2, long-lived 4.1; living consonants p5-p95 11/17/21/24/37, vowels 5/7/9/12/16; tonal 38% (kenku
67%, aarakocra 80%, human 40%); clicks 2.1%; words with a 3+ vowel run 1.7%; median homophone share 0.125; replacements
derive 0.22, renew 0.20, borrow 0.19, compound 0.15, shift 0.13, coin 0.11.

## Round 5, core lane (2026-11-07)

Baseline: the shipped `runs/a24559/languages.json` (same world, identical to the round-start code apart from timing).
Each later column adds one task; runs on a snapshot of the lane's `planet/`, 12-14 workers, machine load 40-45 from
other lanes (so timing is noisy; compare the pass's own `timing.total_s`).

| measure (living lects) | shipped | task 1 (rulings) | task 2 (diminutives, coinage) | task 3 (segments) | task 4 (vocabulary; S211 widened) |
|---|---|---|---|---|---|
| BROTHER = SISTER same form | 0.182 | 0.035 | 0.055 | 0.063 | 0.010 |
| I = WE same form | 0.134 | 0.011 | 0.021 | 0.032 | 0.026 |
| lines where "tone became phonemic" fires twice or more | 221 | 0 | 0 | 1 (tone lost, then reborn) | 0 |
| words that are "X + little" renewals | 9.1% | 9.3% | 1.5% | 1.5% | 1.7% |
| busiest affix's share of a lexicon, median / max | 0.113 / 0.193 | 0.114 | 0.052 / 0.075 | 0.052 / 0.075 | 0.055 / 0.076 |
| lects whose busiest affix is over 8% | 492 | 496 | 0 | 0 | 0 |
| coinage share of replacements | 0.106 | 0.106 | 0.030 | 0.030 | 0.029 |
| homophone share, median (polysemy included) | 0.125 | 0.117 | 0.174 | 0.166 | 0.224 (core 100: 0.12) |
| sisters strict (bar 0.5) | 0.499 fail | 0.519 | 0.523 | 0.515 | 0.588 |
| ɹ / ʁ / ɫ / ɦ / ʐ, share of all living lects (PHOIBLE 0.017 / 0.037 / 0.007 / 0.031 / 0.026) | 0.51 / 0.43 / 0.20 / 0.24 / 0.20 | | 0.54 / 0.35 / 0.23 / 0.27 / 0.23 | 0.05 / 0.54 / 0.14 / 0.01 / 0.02 | 0.05 / 0.19 (humans 0.10) / 0.11 / 0.01 / 0.01 |
| words per living lect, median | 376 | 376 | 376 | 376 | 712 |
| file size | 149.8 MB | 158.3 MB | 152.7 MB | 152.5 MB | 235.6 MB |
| pass `timing.total_s` | 1041 | 947 | 886 | 791 | 1284 (steps 806 s) |

Task 1. Generation softening (rate x (28/gen)^0.7 below 28-yr generations) changed little on this world (its short-lived
peoples are few). `etym_roots` adds 8.5 MB (task 5 should store it only where it differs from `roots`). The contrast sets
(kin sex pairs, pronouns, numerals, wh-words, deictics, directions) damp colexification and shifts between members to
10%, and a homophone inside a pair is always repaired first.

Task 2. The diminutive renewal is limited to body parts, small animals and kin (Latin auricula > oreille, avicellus >
oiseau), capped at 2% of a lexicon, and no longer fills a draw nothing else could: a replacement that no source can make
keeps the old word ("keep", 22% of draws) instead of coining a fresh root, and the hazard is raised by KEEP_COMPENSATION
to hold 86% Swadesh retention per millennium. Coinage fell from 10.6% to 3.0%. The homophone share rose (0.125 -> 0.17):
the extra groups are CLICS polysemies kept instead of being coined away (accidental homophones 4.1% -> 5.4%).

Task 3. The over-produced sounds each came from one context-free rule with no way out: S149 r > ɹ, S148 r > ʁ, S152
l > ɫ (coda), S173 Verner's law (it also voiced h to ɦ), S087 RUKI. S149 now applies in the coda only (Dutch, caipira
Portuguese), where a new "coda" allophone test lists ɹ and ɫ as allophones of r and l (English, Dutch); S173 names
f θ s x; new exits S210-S214 (ʁ > χ in the coda, ʁ > h, ɫ > w, intervocalic ɦ lost, ʂ ʐ > s z). ɹ fell from 0.54 to
0.05, ɦ to 0.01, ʐ to 0.02; ʁ rose (0.35 -> 0.54, humans 0.47) because more r survives to meet S148: S211 is widened to
between vowels (Brazilian carro [ˈkahu]) in the task-4 run. The new check "overused segments (all living lects)" counts
every living lect, skipping a segment its own voice profile favours (make_cost below 1) or one humans cannot make.

Task 4. 339 WOLD 1460 meanings (Haspelmath & Tadmor 2009) join the 240 Leipzig-Jakarta / Swadesh rows: lexicons go from
376 to 712 words (1.9x). ~95 derivation rows and ~60 compound recipes were written for them, so they are built and
renewed like the old meanings (else they fell to loans: borrowing reached 40% of replacements in the harness); the new
pairs joined the contrast sets. Replacements: derive 0.17, compound 0.11, shift 0.15, borrow 0.25, keep 0.25, coin 0.03.
The homophone share rose to 0.22: almost all of it CLICS polysemy (NOW / TODAY, POT / BOWL, LOW / SHALLOW), which a
700-meaning list has more of per meaning; accidental homophones stay under 1% in the harness, and the core 100 hold at
0.12. Sisters rose to 0.588 (more slow-changing vocabulary per lect). Size and time grew with the lexicon (236 MB,
1284 s): task 5 is now more pressing. Still over in the all-lect check: ɫ 0.11 and y 0.18 (kobold, dragonborn, kenku,
aarakocra lects; their profiles do not mark them as favoured), ɒ 0.20 (humans 18%, source not yet traced), ɖ 0.27 and a
two-voiced vowel u‼ (0.12) that the human-cost test does not class as non-human.

## Final run (2026-11-08, finish lane)

Baseline: the round-5 core-lane code on the same world (`lang-design` at a6f293a3). Its run was in scratch, 12 workers, on a loaded machine. Final: `runs/a24559/languages.json` plus its sidecars `languages-etym.json` and `languages-snapshots.json` (format procgen-languages/2, architecture.md §11). Determinism: a second run to scratch with a different `PYTHONHASHSEED` (7) is identical apart from `timing`. It was not identical before this lane's fix: `shift_candidates` iterated a frozenset of strings, so two processes picked differently among equal weights (1181 vs 1187 lects). The new slow test `test_deterministic_across_hash_seeds` guards this.

| measure (living lects) | baseline (core lane) | final |
|---|---|---|
| files | one 241.5 MB file | 36.4 MB main + 63.1 MB etym + 26.2 MB snapshots = 125.7 MB (gzip 9.5 + 15.5 + 6.6 = 31.7 MB) |
| pass `timing.total_s` (steps / wave / observe) | 1264.8 (807 / 118 / 43) | 1262.7 (921 / 96 / 40); wall 21m53s at 12 workers, with another run sharing the machine |
| living lects / all lects | 625 / ~1180 | 617 / 1181 |
| overused segments (all lects) | FAIL: ɖ 0.24, y 0.19, ɒ 0.16, ɫ 0.15, u‼ 0.12 | pass (none over; worst ratio e̞ 2.6x) |
| ɖ / ɒ / ɫ / y / ø, all lects | 0.242 / 0.163 / 0.152 / 0.192 / - | 0.100 / 0.010 / 0.070 / 0.066 / 0.019 |
| u‼ (two-voiced, non-human; exempt now) | 0.118 | 0.112 |
| p: all / human-voiced / humans (PHOIBLE 0.85) | 0.613 / 0.718 / 0.714 | 0.613 / 0.691 / 0.767 |
| ʁ / ɹ / ɦ / ʐ, all lects | 0.203 / 0.040 / 0.008 / 0.014 | 0.125 / 0.029 / 0.010 / 0.003 |
| sisters strict / loose / true (bar 0.5) | 0.588 (core lane, task 4) | 0.554 / 0.591 / 0.639: pass |
| scholars' horizon, human lects (target 6-10 kyr) | 11.4: FAIL | 10.67 (smoothed 11.11): FAIL |
| rules per kyr, human / long-lived | | 14.6 / 3.7 (ratio 3.98) |
| replacements | borrow .252, keep .251, derive .167, shift .148, compound .114, renew .037, coin .029, taboo .003 | borrow .251, keep .251, derive .168, shift .148, compound .113, renew .037, coin .029, taboo .003 |
| homophone share, median | 0.232 | 0.217 |
| words per living lect, median (min) | 712 (699) | 712 (698) |
| sentences | 10 for every living lect, 0 break mismatches | 10 for every living lect, 0 break mismatches |

All other checks pass:
- proto inventories (top-20 overlap 20);
- living inventory sizes (consonants p5-p95 12/16/20/24/37, vowels 5/7/9/12/16);
- living segment frequencies (top-20 overlap 18);
- language shift (146 shifts; 88 living lects off their descent);
- hubs simpler (2.0 vs 5.0);
- typology agrees with the live grams (0 clashes).

**Size.** The doc is packed on disk: one concept table and lect table per document, columnar lexicons, interned root ids, and etymology nodes as columns with a parent gap. Etymology and dead-lect snapshots go to sidecars. The main file the viewer needs first went from 241.5 MB to 36.4 MB (9.5 MB gzipped).

**Speed.** The single-process profile of 6 frames fell from 765 s to about 680 s, from:
- a cached Segment hash;
- the wave steer memo;
- memoized `_unit` / `_strip_tone`;
- lazy homophones in `shift_candidates`.

The full pass did not get faster on the wall clock. The non-human ease drag adds steps time (807 → 921 s), and the machine was shared. A parent-process profile shows the time is in the workers' stepping, not in pool start-up or pickling.

**Overused segments.** Each was traced to its cause:
- ɒ came from rounding harmony rounding non-high vowels. Now only high vowels copy rounding, as in Turkish.
- ɖ had no exit. Added S215 ɖ > ɽ / V_V (Hindi-Urdu), S216 ɽ > ɾ (Eastern Bengali) and S217 ɖ > r / #_ (Romani).
- y and ɫ in kenku, aarakocra, kobold and dragonborn lects: those voices had no ease drag, so u > y and S152 ran unchecked. The profiles do not favour y or ɫ. Non-human voices now feel the drag of their own species cost.
- u‼ counts as non-human in the check.
- p is rare overall because beaked and lipless mouths find labials dear (aarakocra labial cost 5, reptilian 4). In human lects p is 0.77 (PHOIBLE 0.85), so nothing was forced.

**Sentences.** The templates now draw on the WOLD verbs (build, carve, bring, find, catch, sell, buy, dance, shout), kin terms (older brother, younger sibling), numbers (three, four), motion to a goal with the allative, and objects (boat, basket, pot). The English for the polar question now reads "Do you hear the thunder?".
