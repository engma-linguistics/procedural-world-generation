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
