# Sound-change coverage review: eight real sound histories against the generator

Branch `lang-design` at 45737e8a. This was a read-only review: nothing in the repository was changed. Code paths below are
relative to the worktree. "Live" figures come from run a24559 (`runs/a24559/languages.json`), read-only. They cover its
321 living lects with a human-type voice (19 peoples: humans, elves, dwarves, giants, orcs and so on), and each lect's full
line of descent back to 20 kyr. The scripts are in the scratchpad folder `sc/` next to this file. Real-language facts are
textbook knowledge (Campbell, Hock, Ringe, Pope, Baxter, Blust). Figures written from memory are marked "≈".

This is the sister review to `docs/review/language/grammar-gaps.md`, and it reads coverage the same way.

**Run a24559 predates round 5.** Round 5 rewrote S149 (r > ɹ in the coda only) and S173 (Verner on f θ s x only), and
added S210–S214. The run used the older rows. None of the findings below depend on those rows.

## How to read "coverage"

- **full**: the change type exists in the catalogue or the driver, it fires, and its result can be seen in a lect's
  history.
- **partial**: some of it exists, but it is thinner than the real thing, conditioned wrongly, or present only as single
  steps that never form the real pattern.
- **label only**: a row names the real change (its example column cites the real language), but the engine cannot carry
  out what makes it distinctive.
- **none**: the engine cannot produce it.

---

## 1. Summary table

| History | Distinctive feature | Coverage | Note |
|---|---|---|---|
| **PIE > Germanic** | Grimm's law: three stop series rotate with no merger | partial | Rows S177, S097, S098 exist. The chain order arises only by chance: in 109 of 253 lects, D > T fires first, so D and T merge |
| | Verner's law: fricatives voiced after an unstressed syllable | partial | S173 exists. It never fires in the 44% of lects with no stress |
| | Stress fixed on the root, which makes Verner opaque (*grammatischer Wechsel*) | none | Stress is recomputed from position on every form. There is no stress-shift change |
| | Grimm feeds Verner, Verner feeds rhotacism | partial (by chance) | Order is draw order. Verner comes after Grimm in 79 lects and before it in 83 |
| **Latin > French** | Intervocalic lenition to zero (t > d > ð > ∅) | full | S010–S012, S005–S008 |
| | Palatalisation in waves; k > tʃ before *a* | partial | Front-vowel palatalisation only. No k > tʃ / _a |
| | Diphthongisation in stressed open syllables | partial | S174 has no open-syllable condition |
| | Nasal vowels, u > y, l-vocalisation, s-loss before C | full | S088 + S140, S073, S151, S020 + h-loss |
| | Final-syllable loss: the stressed syllable survives, so stress ends up final | none | Penult stress is recomputed after every loss |
| | Very fast erosion; heavy homophony; learned doublets | none | The rate spread is 2.6×; the merger veto resists homophony; no borrowing from an older stage |
| **Middle Chinese > Mandarin** | Tone split from onset voicing, with devoicing | full | S166, `tone.onset_voicing_split` |
| | Stop codas lost through ʔ; -m > -n | full | S037, S191, S072 |
| | Devoiced stops aspirated in one tone and not the other (tone-conditioned) | none | Rules cannot read tone |
| | Tone mergers (8 categories > 4), sandhi, irregular redistribution of the entering tone | none | No tone-to-tone change; no lexical diffusion |
| | Velars palatalised before i; loss of ŋ- | partial | Palatalisation yes; no ŋ > ∅ |
| **Proto-Polynesian > Hawaiian** | Drag chain: k > ʔ, then t > k | none | Neither change is in the catalogue |
| | f, s > h; r, l > l; h, ʔ > ∅ | partial | Most rows exist; no intervocalic ʔ-loss; no ŋ > n |
| | A 13-consonant inventory collapses to 8 in about 2 kyr | partial (rare, slow) | The size anchor and keep steer push against it. 6.5% of lines lose 30% or more of their consonants, but over 20 kyr |
| **English Great Vowel Shift** | A chain shift of the long vowels within about 300 years | partial | Three separate rows (S179–S181). In lects that have all three, the median gap between first and last is 4.75 kyr |
| | Push chain against drag chain | partial | Push only, through the merger veto (`rules.py:762`); 525 pushes in the run |
| | Quantity changes (lengthening in open syllables, shortening in closed ones) | full | S119, S120 |
| | Alternations later morphologised (*divine*/*divinity*) | partial | Only in the 8 exemplar paradigms |
| **Sanskrit > Pali > Hindi** | Cluster assimilation into geminates; law of two moras | partial | Specific rows (pt, kt, ks, mb, nd) only; no general total assimilation; S119 |
| | Sibilants merge; final consonants lost; intervocalic stops lost with a y-glide | full | S214 / S189, S099, S008–S009 + S125 hiatus glide |
| | Degemination with compensatory lengthening; spontaneous nasalisation | full | S121, S089 |
| | Syllabic ṛ > a, i, u | none | No syllabic consonants |
| **Old Irish** | Lenition and nasalisation across word boundaries, morphologised once apocope removed the trigger | none | Sound change runs inside single stored forms; S021 fails to parse |
| | Broad/slender: every consonant splits into velarised and palatalised | none | No C > Cʲ / _front-vowel row |
| | Alternating syncope | full | S104 / `reduction.syncope`, applied left to right |
| **Proto-Bantu > Swahili** | Stops spirantised before the super-high vowels, then the 7 vowels merge to 5 (a split by merger) | partial | The mechanism would work (allophones become phonemes when their conditioning goes), but there is no t > s / _i̧ and no lax/tense merger row |
| | Tone lost, stress fixed on the penult | none | S172 fails to parse; stress never changes |
| | Meinhof's law and Dahl's law (long-distance dissimilation) | none | Long-distance rules are refused (`rules.py:1016`) |
| | Nasal + l > nd (prefix-triggered) | full (phonetically) | S048; the morphological trigger is not modelled |

**Cross-cutting, in one line each** (section 5):
- Every change is exceptionless, with no lexical diffusion. The `scope` field is never read.
- Stress is not historical: it is recomputed from position on every form.
- Tone cannot change once it exists.
- No sandhi across word boundaries feeds history.
- No long-distance rules.
- The catalogue saturates: each lect fires about 98 of roughly 200 rows in 20 kyr, so families have no sound "personality".
- The comparative method works on the output, a little too easily.

---

## 2. Why these eight

The brief suggested ten candidates. I picked eight so that each tests a different part of the engine, and together they
cover every kind of change in the brief.

- **PIE > Germanic**: a series-wide chain shift, a stress-conditioned change, and the textbook case of rule ordering
  (Grimm, then Verner, then the stress shift). It tests whether order can matter and whether stress has a history.
- **Latin > French**: the fastest, most erosive well-documented history. Lenition to zero, several waves of palatalisation,
  nasal vowels, final-syllable loss and heavy homophony. It tests the catalogue's breadth, the rate range and the
  functional-load veto.
- **Middle Chinese > Mandarin**: tonogenesis and what happens to tones afterwards: merger, conditioning by tone, and
  irregular redistribution. It tests the tone layer beyond its birth.
- **Proto-Polynesian > Hawaiian**: losses and mergers that are almost all context-free, a drag chain, and a collapsing
  inventory. It tests the steers that hold inventories near PHOIBLE's middle.
- **English Great Vowel Shift**: the standard chain shift, with the push-against-drag debate and a very short time span.
  It tests the engine's one chain-shift mechanism, the dispersion push.
- **Sanskrit > Pali > Hindi**: cluster simplification, compensatory lengthening, and a two-stage history in which
  assimilation makes geminates and later degemination lengthens the vowel. It tests the syllable-weight and cluster rows.
- **Old Irish**: initial mutations born from sandhi, morphologised when apocope removed the trigger, plus a split of the
  whole consonant system into broad and slender. It tests whether history can run across word boundaries.
- **Proto-Bantu > Swahili**: a split by merger (spirantisation, then the vowel merger), tone loss, and long-distance
  dissimilation elsewhere in Bantu (Meinhof, Dahl). It tests phonologisation, tone loss and non-adjacent change.

**Not chosen.**
- *Proto-Semitic > Arabic and Hebrew*: its sound history mostly repeats points already covered. Begadkefat
  spirantisation phonologised by degemination is the same split-by-merger as Bantu. Guttural mergers are mergers. What
  makes Semitic distinctive is root-and-pattern morphology, which belongs to the grammar review.
- *Danish stød*: noted under gaps. The percept space has creaky phonation (`percepts.py:36`), but no row creates it.
- *Malagasy*: its paragogic final vowels are S124.

---

## 3. What the engine has, in brief (checked in code)

- **A rule** (`rules.py:273`):
  - a focus pattern over natural classes, plus an optional span (a cluster);
  - a change: set, map, delete, insert, split, metathesis, rewrite, or assimilate from the left, the right, the previous
    vowel or the root's first vowel;
  - an environment (`rules.py:257`): left and right tokens (segments, classes, `#`, optional, any number), the focus
    vowel's stress, an unstressed or stressed context vowel, and the syllable flags coda, onset, final, nonfinal, open and
    closed;
  - a cause, the articulators it needs, a weight, and a `scope` of regular or diffusing;
  - staged steps (`then`, `rules.py:286`), parsed from rows written with "then" (`rules.py:1440`).
- **The catalogue** is 30 demo rules (`rules.py:1739`) plus 202 rules parsed from the 214 rows of
  `data/sound_changes.tsv`.
  - 21 rows fail to parse and are skipped (`rules.py:1016` `_BLOCK`): S021 (Irish mutation), S059, S060, S114 (cluster
    lists), S091–S094 (dissimilations, including Grassmann), S106 (haplology), S132–S134 (suffix harmony, ATR), S137 (ǫ),
    S142, S145, S162, S170–S172 (pitch accent, Meeussen, tone loss), and S183–S184 (analogy).
  - A chain row "a > b > c" keeps only its first step (`rules.py:1463`).
- **Application.**
  - One rule is applied regularly, left to right, to every stored form at once: words (`lexicon.py:2043`), affixes, gram
    forms and exemplar cells (`grammar.py:2053`).
  - Matching ignores tone (`rules.py:11`; patterns test no tone axis).
  - Stress is recomputed on every form from a fixed pattern: none 44%, initial 19%, penult 27%, final 10%
    (`inventory.py:35`; `rules.py:298`, `:314`). Segments have no stress axis (`percepts.py:28-50`).
- **Drawing rules** (`lect.py:642`).
  - k events ~ Poisson(generations × RATE_RULE 0.1 × RATE_SCALE 5 × lect rate). The lect rate is lognormal with sigma 0.3
    (`lect.py:22`), redrawn with sigma 0.1 at budding.
  - Each event is weighted by: the species' cost, a new-segment penalty, the ease drag, the stop steer, the keep steer and
    the inventory-size steer (architecture §5).
  - A drawn rule is then vetoed with probability 1 − exp(−15 × functional load) (`rules.py:40`, `:722`). A vetoed vowel
    merger offers a push-chain step instead (`rules.py:762`).
  - A rule that fired cannot fire again for 3 kyr. Epenthesis, harmony and tone rows may fire at most twice per line
    (`lect.py:75-80`).
- **Driver-side changes outside the catalogue:**
  - hiatus repairs, with a strategy preference inherited along the line (`lect.py:539`, `:581`);
  - inventory folds, where rare new units merge into a neighbour (`lect.py:398`, logged as `simplification`);
  - tone hygiene: tone is stripped unless 30% of the core vowels carry it; once tonal, every vowel gets a tone
    (`lect.py:957`);
  - the wave: a fired rule is offered to contact lects (`history.py:265-300`);
  - accent substitution at a language shift, and koine levelling (`history.py:385`, `:621`).
- **Allophones are found after the fact** from the distribution of sounds (`inventory.py:950-1095`). So a conditioned
  change makes an allophone, and when a later change removes its conditioning, the allophone becomes a phoneme. This is
  real phonologisation, and it emerges without any code written for it.
- **Analogy** exists only in the 8 exemplar paradigms (`grammar.py:59`, `:1979`). The lexicon has none.

**Live, run a24559, 321 living human-voiced lects, whole lines of descent:**
- **Rate.** 81,459 events, median 12.8 per kyr; humans alone 13.4 (p10 6.7, p90 17.2).
- **Where events come from.** 26% arrived by the wave. 10.1% are inventory folds and 9.1% hiatus repairs. Lenition is the
  largest family, at 19.9%.
- **Conditioning.** 69% of events are conditioned and 20% context-free; the rest are folds and tone bookkeeping.
- **Saturation.** Each lect line fires about 98 distinct rows, and 57 of them fire twice or more.

---

## 4. Per-history sections

### 4.1 Proto-Indo-European > Proto-Germanic

**What makes it distinctive.**
- *Grimm's law* is a rotation of whole series: voiceless stops became fricatives (*p t k > f θ x*), voiced stops became
  voiceless (*b d g > p t k*), and breathy-voiced stops became plain voiced (*bʰ dʰ gʰ > b d g*, through β ð ɣ). No two
  series merged, because the steps ran in drag order: each series moved only after the one ahead of it had vacated its slot.
- *Verner's law* voiced the new fricatives (and *s*) when the preceding syllable was unstressed under the old mobile PIE
  accent. Then the accent was fixed on the root. That removed Verner's conditioning and left the alternations
  (*grammatischer Wechsel*: *was*/*were*, Old English *cweþan*/*cwǣdon*) as morphology.
- *Ordering*:
  - Grimm feeds Verner, because Verner acts on Grimm's fricatives.
  - Verner's *z* feeds rhotacism in North and West Germanic (*were*).
  - The stress shift comes after Verner. Had it come first, Verner's conditioning would have been gone before Verner
    could apply.
- *Vowel mergers* (*o* with *a*, *ā* with *ō*) and the Auslautgesetze erosion of final syllables.
- *Speed*: a few centuries (≈), with dates contested.

**Coverage.**
- **The steps exist.**
  - S177, "p t k > f θ x / #_, V_" (`sound_changes.tsv:185`), and `lenition.p_f` (`rules.py:1742`).
  - S097, b d g > p t k (`:105`), and S098, the loss of breathy voice (`:106`).
  - S173, Verner (`:181`); S147, rhotacism; S188, β ð ɣ > b d g.
  - **The steps are too common.** T > F fired in 265 of the 321 lects (83%), and D > T in 300 (93%).
- **The chain is luck.**
  - Of the 253 lects with both steps, T > F came first in 144. In the other 109, D > T came first, so old D and old T
    became one F (the merger Grimm's law famously avoided).
  - All three steps fired in only 19 lects.
  - Nothing in the engine prefers drag order.
- **Verner's conditioning.**
  - Verner came after T > F in 79 lects and before it in 83.
  - In the 44% of lects with stress "none", no unstressed context ever matches (`rules.py:579`), so S173 can never fire.
- **The stress shift does not exist.**
  - Stress is not stored. Every form gets penult, initial or final stress from its current shape (`rules.py:314`).
  - So Verner's conditioning cannot be removed by a later change, and *grammatischer Wechsel* cannot arise in the
    lexicon.
  - One happy accident: in the exemplar paradigms, a suffix moves penult stress, so Verner-like alternations can appear
    between a cell and its stem.
- **A small error in the environment.**
  - S177's "#_, V_" blocks Grimm after sonorants as well as after obstruents.
  - Real Grimm applied after r, l and n (\*wĺ̥kʷos > *wolf*). Only obstruents blocked it (*sp, st, sk*, *ft*).
  - "#_, [+son]_" would be right; `SON` already exists (`rules.py:169`).

**Could a generated history read like this?** The individual lines can: the sketch even prints Grimm's own examples. But
the shape is missing: a series rotation in drag order, and a stress shift that makes Verner opaque. **Partial.**

### 4.2 Latin > French

**What makes it distinctive.**
- Erosion of everything after the stressed syllable:
  - intervocalic stops went to zero (*vita* > *vie*; *augustum* > *août* [u]);
  - final vowels were lost except *a*, which became [ə];
  - pre- and post-tonic syncope.
- Palatalisation in several waves: *k* before a front vowel > *ts* > *s* (*centum* > *cent*), and *k* before *a* > *tʃ* >
  *ʃ* (*cantare* > *chanter*, Bartsch's law).
- Diphthongisation in stressed open syllables (*mare* > *mer*, *pedem* > *pied*).
- Nasal vowels from VN, followed by nasal loss; *u* > *y*; *l* vocalised before a consonant; *s* lost before a consonant
  with compensatory lengthening (*beste* > *bête*).
- Stress-driven outcome: Latin's weight-sensitive antepenult/penult stress survived, the syllables after it fell, and so
  French stress is final.
- Speed: very fast (≈ 2 kyr to the modern language).
- Two side effects: massive homophony (*sain, saint, sein, ceint, cinq* in some contexts), and learned borrowings from
  written Latin that sit beside the inherited words as irregular doublets (*frêle*/*fragile*).

**Coverage.**
- **The catalogue covers most single changes.**
  - S010–S012, S005–S008 (the lenition ladder); S049 and S051 (palatalisation before front vowels); S064 (a > ɛ in
    stressed open syllables); S174 (diphthongisation); S088 + S140 (nasal vowels); S073 (u > y); S151; S020; S122 (e-
    prothesis); S104 and the demo syncope; S103 (apocope).
  - S073 is weighted 0.1 (`history.py:70`), because together with y > i it drained *u* from every lect.
- **Missing pieces.**
  - k > tʃ / _a.
  - S174 has no open-syllable condition, though the notation could express one: `[open]` is a house flag.
  - Latin's weight-sensitive stress is not a stress option (`inventory.py:35`).
- **The decisive mechanism fails.**
  - Because stress is recomputed after each change, penult stress jumps after apocope or syncope.
  - So the next reduction can erode the syllable that was historically stressed, and protect one that was not.
  - A French-like final stress cannot emerge. Old French's stressed-syllable survival happens only by chance.
- **Speed is too narrow.**
  - The human p90 is 17.2 events per kyr, against a p10 of 6.7. The lognormal sigma of 0.3 (`lect.py:22`) gives only
    about a 2.6× spread.
  - French needs several times the median; conservative lines (Lithuanian, Icelandic ≈) need a fraction of it.
- **Homophony is resisted.**
  - The veto counts every pair of words a rule would make identical (`rules.py:643`), and at FL_K 15 a load of 0.05 is
    vetoed 53% of the time.
  - French-scale homophony needs many such changes to get through. I could not measure the veto share, because
    `PICK_STATS` is not saved in the output.
- **No learned doublets.** Loans come only from contemporary contact lects, never from an older or written stage.

**Could a generated history read like this?** As a list of changes, yes, more than for any other history here. As a
trajectory (a stress-anchored collapse into short words), no. **Partial; good on single changes.**

### 4.3 Middle Chinese > Mandarin

**What makes it distinctive.**
- *Tone split*: voiced initials lowered the tone (the *yang* registers), and then they devoiced. Four tone categories
  became eight.
- *A tone-conditioned outcome*: the devoiced stops became aspirated in the level tone and plain in the oblique tones.
  This is a segmental change conditioned by tone.
- *Codas*: -p -t -k went through -ʔ to zero, and their "entering tone" syllables were spread over the other tones. In
  Mandarin that spread is famously irregular: lexical diffusion plus dialect borrowing. -m merged into -n.
- *Tone mergers*, down to four Mandarin tones; tone sandhi (3 + 3 > 2 + 3).
- *Palatalisation*: velars and dental affricates before high front vowels became tɕ (the *jian/tuan* merger).
- Loss of ŋ- at the start of a word; growth of a retroflex series.

**Coverage.**
- **Tone birth: full.**
  - S166 and `tone.onset_voicing_split` (`rules.py:1780`) do the split and devoicing in one staged rule.
  - S167, S168 and S169 give tone from glottal and *h* codas, after Haudricourt.
  - S037 (p t k > ʔ / _#), S191 (ʔ-loss), S072 (m > n / _#).
  - Live: 226 of 321 lects had a tone event, and 101 (31%) are tonal now. The share over all voices is 38%, against
    WALS 13A ≈ 42%. That is fine.
- **Tone afterwards: none.**
  - Patterns ignore tone, so no change can be conditioned by it. The aspiration split is impossible.
  - No rule changes one tone into another. Meeussen's rule (S171) and tone loss (S172) fail to parse, and the `_BLOCK`
    list refuses "tone" rows (`rules.py:1019`).
  - When a vowel is deleted its tone goes with it (`rules.py:585`). Tone is not stable, as it is in real tone systems.
  - Tone hygiene gives every unmarked vowel the commonest tone (`lect.py:957`), so the redistribution of a lost category
    is uniform, never irregular.
- **Missing single changes:** ŋ > ∅ / #_ at the start of a word.
- **Palatalisation: partial.** S049 and S055 give tʃ and ʃ rather than tɕ and ɕ, but in the right environment.
- **Word shape.** Words average about 2.4 syllables. A tone on every vowel of a polysyllabic word suits Bantu or
  Yoruba-like systems better than a Chinese-like one. Pitch accent (S170) is refused.

**Could a generated history read like this?** The first half, yes. Nothing after tonogenesis does. **Partial.**

### 4.4 Proto-Polynesian > Hawaiian

**What makes it distinctive.**
- Almost purely context-free losses and mergers in a CV language with no clusters:
  - *k > ʔ*, and then *t > k*: a drag chain that kept a /k/;
  - *f* and *s* > *h*; *r* and *l* > *l*; *ŋ > n*; *h* and *ʔ* > zero.
- *w* has [v] and [w] as allophones.
- Thirteen consonants (≈) fell to eight (p k ʔ h m n l w) in roughly 1.5–2 kyr.
- Few new segments arose, and the syllable shape did not change.

**Coverage.**
- **Rows that exist:**
  - S019, s > h / #_, V_V, which in a CV language is everywhere (`:27`);
  - S017 and `lenition.f_h`; S018 and `lenition.h_loss`;
  - S209, ɾ > l (`:217`), citing this very change;
  - S197, ʔ-loss at the start of a word; S191, ʔ-loss before a consonant and at the end. There is no ʔ-loss between vowels.
- **Missing:**
  - k > ʔ without conditioning (only S036 and S037, at the end of a word);
  - t > k (nowhere in the catalogue);
  - ŋ > n (only S143, at the end of a word).
- **The steers resist the collapse, on purpose.**
  - The size anchor (`lect.py:35`) holds each line within sigma 0.12 in ln n of its proto's count. Thirteen to eight is
    ln 0.49, about 4 sigma.
  - The keep steer multiplies by 0.25 any rule that would remove the last *t* or *k* (`lect.py:69-70`). So the drag chain
    would be penalised at both ends even if its rows existed.
  - Live: consonants now / proto, p5 0.68, median 0.89. 6.5% of lines lost 30% or more, but over 20 kyr, not 2.

**Could a generated history read like this?** It could produce a Polynesian-flavoured loss list. It could not produce the
signature drag chain or the speed. **Partial.** Daniel set the steers deliberately (calibration.md, sinks round). Allowing
a Hawaiian-like line is a judgement call (section 6, item 9).

### 4.5 English: the Great Vowel Shift

**What makes it distinctive.**
- Between about 1400 and 1700 (≈), the long vowels rose one step each: aː > ɛː > eː, ɛː > eː, eː > iː, oː > uː,
  ɔː > oː. The high vowels became diphthongs: iː > əi > ai, uː > əu > au.
- Hardly any merger happened inside the chain. (The *meet*/*meat* merger came later.) Whether the shift was a push chain
  or a drag chain is still argued.
- It interacts with quantity: lengthening in open syllables and shortening in closed ones, and trisyllabic laxing.
  Together they left alternations that became morphology (*divine*/*divinity*, *keep*/*kept*).

**Coverage.**
- **Rows.**
  - S179 (iː uː > ei ou), S180 (eː oː > iː uː) and S181 (aː > ɛː); `sound_changes.tsv:187-189`, plus
    `chain_shift.raise_mid`.
  - Their second steps are dropped (`rules.py:1463`).
  - Quantity: S119 and S120. The diphthongs are V + V sequences, which the hiatus check treats as falling diphthongs.
- **The chain is not a chain.**
  - All three rows fired in 162 of 321 lects (50%), so a signature change is in half of everything.
  - Median spread between the first and last of them: 4.75 kyr. Only 2.5% fell within 0.5 kyr.
  - Top first (the drag order) in 102 of 162. The merger veto blocks some of the wrong orders.
- **The push mechanism exists but is generic.**
  - 525 dispersion pushes in the run, mostly a central vowel lowering (ə 97, ɨ 87).
  - There is no drag mechanism: a vacated slot does not raise the weight of the change that would fill it.
- **Morphologised alternations** come only from exemplar cells.

**Could a generated history read like this?** The steps, yes. The event, no: it is spread over five millennia. The staged
notation (`then`, `rules.py:1440`) could already express the shift as one row. **Partial.**

### 4.6 Sanskrit > Pali/Prakrit > Hindi

**What makes it distinctive.**
- *Middle Indo-Aryan*:
  - regressive total assimilation of clusters (*bhakta* > *bhatta*, *sapta* > *satta*, *karma* > *kamma*);
  - the law of two moras: a long vowel shortened before a geminate;
  - sibilants merged (ś ṣ s > s); syllabic ṛ became a, i or u; final consonants were lost;
  - later Prakrits lost single stops between vowels, leaving a y-glide (*ya-śruti*).
- *Hindi*:
  - degemination with compensatory lengthening (*satta* > *sāt*), a counter-feeding pair with the earlier shortening;
  - loss of final short vowels (schwa deletion); spontaneous nasalisation; breathy-voiced stops kept;
  - a retroflex flap from a retroflex stop between vowels.

**Coverage.** This is the best-covered history.
- **Present:**
  - S078 (pt > tt), S079 (kt > tt), S080 (ks > ss) and S081 (mb > mm, nd > nn);
  - S119 (law of two moras), S214 (ʂ ʐ > s z), S189, S099;
  - S008 and S009, with the y-glide hiatus repair S125a (`lect.py:539`). This is the *ya-śruti* exactly;
  - S121, VC > Vː / _C: degemination with lengthening (`:129`); S089, spontaneous nasalisation (`:97`); S103.
- **Missing:**
  - A general total assimilation. The notation copies only place, back, round and voice (`rules.py:211`), so each
    cluster needs its own row, and rk, rm or sm cannot assimilate.
  - Syllabic consonants. The percept space has none.
  - ɖ > ɽ between vowels.

**Could a generated history read like this?** Yes, closely, provided the draws fall in the right order. **Partial, close to
full.**

### 4.7 Old Irish: initial mutations

**What makes it distinctive.**
- In close-knit phrases (article + noun, possessive + noun, preverb + verb), a consonant at the start of a word lenited
  after a word ending in a vowel, and nasalised after a word ending in *-n*.
- Apocope then removed the final vowels and nasals that caused this. So the mutations became the only mark of the
  grammatical difference: *a chat* 'his cat', *a cat* 'her cat', *a gcat* 'their cat'.
- Syncope removed every second vowel.
- Consonant quality (broad/slender) became phonemic on almost every consonant. Vowels were affected by the next syllable.

**Coverage.**
- **Sandhi between words cannot feed history.**
  - A rule runs on one stored form at a time: a word, a gram or an exemplar cell (`lexicon.py:2043`,
    `grammar.py:2053`).
  - A phrase is assembled only at render time. The joining rules there do two things (`sentences.py:243`): a glide
    between vowels, and nasal place before a stop. Neither is ever recorded as history.
- **The rows that would carry it are missing.**
  - S021, the initial-mutation row, fails to parse ("alternative outputs").
  - No row makes a consonant palatalised before a front vowel (`secondary` = 2 exists, `percepts.py:37`). So no
    broad/slender split.
- **What exists.**
  - Syncope alternates as Irish requires (`reduction.syncope`, applied left to right: `rules.py:9`).
  - A prefix gram that binds to a stem can pick up lenition inside an exemplar cell. The grammar review notes it never
    reaches sentences (grammar-gaps §5.1 #8).

**Could a generated history read like this?** No. **None** for the defining feature.

### 4.8 Proto-Bantu > Swahili

**What makes it distinctive.**
- Proto-Bantu had seven vowels with two super-high ones (\*į \*ų). Stops before the super-high vowels spirantised
  (Bantu spirantisation, mostly to s, f or z ≈). Then the super-high vowels merged with i and u.
  - This is the classic split by merger: the fricatives became phonemes once their conditioning vowel disappeared.
- Swahili lost tone and fixed stress on the penult.
- A nasal prefix changes the next consonant (class 9/10 N + l > nd).
- Elsewhere in Bantu there is long-distance dissimilation: Meinhof's law (NC…NC) and Dahl's law (voiceless…voiceless).

**Coverage.**
- **The mechanism for a split by merger works.**
  - A conditioned change makes an allophone, and once its conditioning vowel merges away, the allophone analysis
    (`inventory.py:1056`) reads it as a phoneme.
  - Live: i-umlaut followed by loss or reduction of the trigger vowel happened in 108 of 165 umlaut lects. VN
    nasalisation followed by nasal loss happened in 36 of 80.
- **The rows are missing.**
  - There is no t, k > s / _i (only palatalisations to tʃ and ʃ: S053, S055).
  - No lax-into-tense vowel merger (ɪ > i, ʊ > u). The percept heights 0–6 could carry one.
- **Tone loss and stress.** Tone loss (S172) fails to parse. Tone disappears only when hygiene strips it, below 30% of
  core vowels. Stress never changes, so a penult stress cannot replace tone.
- **Long-distance dissimilation** is refused by the parser (`rules.py:1016`).
- **The nasal prefix.** S048 (l > d / N_) is there, but it is phonetic. No morphological trigger exists.

**Could a generated history read like this?** Its first half, if two rows were added. Not the tone loss. **Partial.**

---

## 5. Cross-cutting picture

### 5.1 Missing entirely

1. **Lexical diffusion and sporadic change.**
   - The `scope` field (`rules.py:37`, `:280`) is set by family and weight (`:1571`), overridden for S042 (`:899`), and
     printed in no output. Nothing reads it.
   - `filtered_apply` → `apply_rule_to_lexicon` changes every word that matches (`lect.py:133`; `lexicon.py:2043`).
   - So every metathesis, the CCC cluster rule and the ʔ-prothesis, though all marked "diffusing", act as exceptionless
     laws.
   - Real histories have both kinds (Labov 1994):
     - regular for gradual phonetic changes;
     - word-by-word for abrupt substitutions, metathesis, dissimilation, and the Chinese entering-tone redistribution
       (Wang 1969).
   - They also have a residue of sporadic one-word changes.
2. **Long-distance change.**
   - The parser refuses dissimilation (Grassmann, Latin *r…r* > *l…r*), haplology and consonant harmony
     (`rules.py:1016-1021`; S091–S094, S106).
   - Vowel harmony exists only as the one demo rule, at most once per line (`lect.py:77`).
3. **Stress with a history.**
   - Stress is a position recomputed on every form (`rules.py:298-323`). Segments carry no stress (`percepts.py:28`), and
     the pattern never changes (`inventory.py:542`).
   - So there is no stress shift, no weight-sensitive stress, and no "the stressed syllable survives".
   - In the 44% of lects with stress "none", every stress-conditioned row is dead: reduction, syncope, apocope, Verner, S013
     and S047.
4. **Tone after tonogenesis.**
   - No tone-to-tone change (merger, split, spreading, Meeussen), and no tone sandhi.
   - No change conditioned on tone; tone is dropped when its vowel is deleted; tone loss is not a change (S172).
5. **Sandhi across word boundaries in history.** Hence no Celtic mutations, no begadkefat across words, no French liaison
   or *h aspiré*.
6. **Analogy in the lexicon.**
   - S183 and S184 are refused as "not a sound change". Analogy lives only in exemplar cells (`grammar.py:1979`).
   - Derived words and their bases drift apart without levelling.
   - Morphologically conditioned rows (S132, S133) are refused.
7. **A drag chain.** Only the push exists, through the veto (`rules.py:762`). Chain rows keep their first step
   (`rules.py:1463`), although the staged `then` notation would let them run whole.
8. **Specific common changes missing from the catalogue:**
   - t > k; k > ʔ without conditioning; ŋ > n or zero everywhere;
   - C > Cʲ / _front vowel (secondary palatalisation, as in Irish and Russian);
   - a(ː) > ɔ(ː) or o(ː) (Old English *stān* > *stone*, the Canaanite shift);
   - lax-into-tense mergers (ɪ > i, ʊ > u, the 7 > 5 vowel collapse);
   - t, k > s / _i (spirantisation); ɖ > ɽ / V_V;
   - total regressive assimilation; creaky voice or stød.
9. **Syllabic consonants** (Sanskrit ṛ, PIE \*m̥ \*n̥).
10. **Borrowing from an older stage of the line** (learned doublets).
11. **Frequency-conditioned reduction.** Frequent and function words reduce first (Bybee). Every word changes at once.

### 5.2 Modelled too thinly

- **Conditioning environments.**
  - What exists is good: classes, word edges, optional and starred tokens, stress on the focus or on a context vowel, and
    six syllable flags.
  - Missing: morpheme boundaries; position counted in syllables (Irish second-syllable syncope, Polynesian accent units);
    tone; negation ("not after an obstruent", which is Grimm's real condition); non-adjacent context.
- **Rules are events, not rules of the grammar.**
  - Once a change has fired, its pattern does not apply to words made later. `inventory.realize` helps a little: it keeps
    new coinages in allophone patterns (`inventory.py:1098`).
  - So the classic dynamics of rules in a grammar cannot happen: rule inversion, rule telescoping, and morphologisation
    outside exemplars.
- **Order is only draw order.** Feeding and bleeding do happen, but by chance.
  - Grimm in chain order in 144 of 253 lects. Verner after Grimm in 79 and before it in 83.
  - The history list is truthful, but nothing makes the changes cohere into a recognisable trajectory.
- **Rate variation is narrow.** Sigma 0.3 per lect (`lect.py:22`); human p10–p90 is 6.7–17.2 events per kyr (2.6×).
  There are no bursts after a shift, strong contact or a small founding population.
- **Diphthongs are two vowels**, and chain rows stop after their first step, so the GVS top ends at *ei*/*ou*.

### 5.3 Exists but wrongly calibrated

| Feature | Live (a24559, 321 human-voiced lects) | Real reference | Cause in code |
|---|---|---|---|
| **Catalogue saturation** | ~98 distinct rows per line in 20 kyr, 57 of them fired twice or more. "Grimm" T > F in 83% of lects, D > T in 93%, all three GVS rows in 50% | Named shifts are signatures of one family. Families show "drift" (Sapir), parallel tendencies across branches | A row may fire again after REFIRE_KYR 3 with no lifetime cap outside epenthesis, harmony and tone (`lect.py:75-80`). Weights are the same for every line; only the hiatus strategy is inherited (`lect.py:581`) |
| GVS as an event | median 4.75 kyr between its three rows; 2.5% within 0.5 kyr | ≈ 300 years | Three independent rows |
| Rate spread | humans p10 6.7, p90 17.2 events per kyr | Several-fold differences between conservative and innovative lines (≈) | `RATE_SIGMA` 0.3 |
| **Inventory folds** | 10.1% of all events are `simplification` folds | Real mergers have a phonetic path | `cap_inventory` (`lect.py:398`) folds rare new units into a neighbour one axis away. Sketches count these "merger rounds" but do not list them |
| Inventory collapse | consonants now / proto: p5 0.68 over 20 kyr | Hawaiian ≈ 0.6 in 2 kyr; Rotokas-like small inventories | Size anchor sigma 0.12, keep factor 0.25, stop steer (`lect.py:34-70`). Deliberate |
| Functional-load veto | not measurable from the output | Wedel et al. 2013: a real but probabilistic effect; French, English and Chinese tolerate heavy homophony | FL_K 15 (`rules.py:40`); `PICK_STATS` is not saved |
| Tonal share | 31% of human-voiced lects, 38% of all | WALS 13A ≈ 42% | Fine |
| Median rate | 13 events per kyr | Plausible middle (≈) | Calibrated by the horizon check |

### 5.4 Regularity and the comparative method

- **Neogrammarian regularity: total, by construction.**
  - Every change applies to every stored form that matches.
  - Irregularity in correspondences comes only from the lexicon: replacement, loans (including koine levelling,
    `history.py:438`), and accent substitution at a shift. These are real sources of irregularity.
  - There is no sporadic phonological residue at all. Real histories always have some.
- **What a comparativist would see.** I measured this from the true etymologies (the scratchpad `sc/comp.py` script).
  - Method:
    - Take every living daughter's words that changed only by sound change since time T.
    - Align each word with the ancestor's form at T.
    - Ask how often a proto segment, given its two neighbours, has its majority reflex.
  - Results:

    | T | Daughters (groups) | Words still inherited by sound change alone | Majority-reflex share (median, p10–p90) | Proto contrasts merged in every daughter (groups with 3 or more daughters) |
    |---|---|---|---|---|
    | 2 kyr | 73 (21) | 61% | 0.93 (0.86–0.99) | 0.3% |
    | 5 kyr | 126 (36) | 35% | 0.90 (0.78–0.98) | 3.8% |
    | 8 kyr | 149 (31) | 20% | 0.875 (0.75–0.95) | 3.8% |

  - Because these words are exceptionless by construction, the shortfall from 1.0 is the measure's floor.
    - It reflects conditioning wider than one segment either side (stress, word position, harmony) and alignment noise.
    - That conditioning is wide enough to need more than the adjacent segment, which is realistic.
  - The decisive figure is the last column. About 96% of proto contrasts at 5–8 kyr survive in at least one daughter, so
    a comparativist could recover the proto inventory almost whole.
  - The limiting factor is the lexicon (35% inherited at 5 kyr), not the sound changes.
- **The scholars' tree already uses recurring correspondences**, a light comparative method (`families.py:530-545`,
  REC_MIN 2). It never reconstructs.
- **A label that claims too much.** The sketches call the true proto "the reconstructed ancestor"
  (`tools/language/sketch.py:656`; e.g. `sketches/d725-drow.md:26`). It is the true ancestor; nobody reconstructed it.
- **Verdict.**
  - The comparative method works on the output, and works a little too cleanly: no sporadic changes, no analogy, no
    doublets.
  - Each history reads as a list of textbook laws, each perfectly regular, with no residue for the historian to explain.

---

## 6. Ranked recommendations

Value is how much more like a real sound history the output becomes (H/M/L). Cost: S = under a day; M = a few days;
L = a week or more, or an architecture change. **Before merge** means cheap and fixing something the pages already show
or claim.

| # | Recommendation | Value | Cost | When |
|---|---|---|---|---|
| 1 | **Line-level drift and less saturation.** Give each proto a lognormal preference per rule family and per row, inherited and re-drawn a little at budding, exactly as `hiatus_pref` does (`lect.py:581`). Cap named one-off rows (chain shifts, Grimm, Verner, GVS) at one firing per line, and lengthen REFIRE_KYR for the rest. Families then get a sound personality (Germanic umlaut in every branch, Romance lenition, Polynesian losses), and "Grimm's law" stops appearing in 83% of lects. Check with the horizon. | H | S | Before merge |
| 2 | **Chain shifts as single staged events.** Rewrite S177 + S097 + S098 (Grimm) and S179–S181 (GVS) as staged rows in drag order using the existing `then` notation (`rules.py:1440`). Keep the second steps of chain rows (`rules.py:1463`). Add a drag offer: after a change empties a slot, raise for a while the weight of a change that would fill it. Fix S177's environment to "#_, [+son]_". | M | S | Before merge |
| 3 | **Add the missing common rows** (§5.1 #8): t > k (drag, after k > ʔ); k > ʔ; ŋ > n; C > Cʲ / _[+front V]; a(ː) > ɔ(ː)/o(ː); ɪ > i and ʊ > u; t, k > s / _i (spirantisation); ɖ > ɽ / V_V; k > tʃ / _a; an `[open]` condition on S174. Make S059, S060, S114, S137, S142 and S162 parse. | M | S | Before merge |
| 4 | **Save the veto statistics and measure homophony.** Persist `PICK_STATS` per lect. Report homophone share against real figures. Put FL_K to Daniel as a needs-decision ticket. | M | S | Before merge |
| 5 | **Use `scope`: lexical diffusion and a sporadic channel.** A diffusing row spreads over the lexicon across several intervals, frequent words first for reductive changes. It can stall and leave a residue. Add a small rate of one-word changes (metathesis, dissimilation, assimilation). This gives real irregularity in correspondences and a Chinese-style irregular redistribution of a lost tone class. | H | M | First after merge |
| 6 | **Stress as a historical property.** Store the stressed vowel on each form and carry it through changes: a deletion moves nothing, and a merged syllable keeps it. Add stress-shift rows (to the initial; weight-sensitive; to the final after apocope), and let "none" lects gain stress. This unlocks Verner made opaque, Romance stressed-syllable survival and French final stress, and makes the 44% stressless lects reachable by stress rows once they shift. | H | M | First after merge |
| 7 | **Tone after tonogenesis.** Let patterns test tone. Add tone-to-tone rows (merger, raising and lowering, contour simplification, Meeussen). Move a deleted vowel's tone to its neighbour (tone stability). Make tone loss a change, with penult stress gained. | M (31% of lines are tonal) | M | Later |
| 8 | **Long-distance rules in the parser.** Non-adjacent "X…Y" contexts and identity (haplology). This unlocks S091–S094 (Grassmann), Meinhof and Dahl, and consonant harmony. | M | M | Later |
| 9 | **Rate spread and bursts.** RATE_SIGMA 0.3 > about 0.6, and a temporary boost after a language shift or a founder split. Allow a Hawaiian-like collapse on some lines by loosening the size anchor for a few lines. This is a judgement call for Daniel (needs-decision), since the steers are deliberate. | M | S + a run | Later (needs decision) |
| 10 | **A reconstruction step.** From each scholars' clade, build correspondence sets and a reconstructed proto inventory with asterisked forms. Show it beside the true proto, and change the sketch's "the reconstructed ancestor" label (`sketch.py:656`) to "the true ancestor". This doubles as a check on recoverability (§5.4). | M | M | Later |
| 11 | **Phrase sandhi with a history.** Treat fixed phrases (article + noun, possessive + noun, preverb + verb) as single forms for sound change, as exemplar cells are. When the trigger erodes, the changed first consonant becomes the exponent. This gives Celtic mutations and ties into grammar-gaps recommendation 15. | H for a Celtic type | L | Later |
| 12 | **Analogy in the lexicon.** Level derived words back toward their base, and let S183/S184-type extension run on word families. | M | M | Later |
| 13 | **Make inventory folds legible.** List them in the sketches with the old and new sound, or route them through the nearest catalogue merger, so a 10% share of events is not an unexplained merger. | L–M | S | Later |
| 14 | **Learned doublets.** Borrow occasionally from the line's own older stage (a "classical" lect frozen at a frame), for prestige lects with writing. | L | M | Later |
| 15 | **Syllabic consonants** (sonorants as syllable nuclei), so ṛ > ri/ru and \*n̥ > un/a can happen. | L | M | Later |

**Before the first merge**, items 1–4 are all S cost:
- 1 is the largest single gain: lines get a sound personality, and named laws stop being universal.
- 2 turns the two famous chain shifts into the events they were.
- 3 adds the commonest attested changes the catalogue lacks.
- 4 makes a deliberate, unmeasured constant visible.

Items 5 (diffusion and a sporadic channel) and 6 (stress with a history) are the two largest gains in how real the
histories *read*. Both are new layers and belong after the merge.

---

## 7. Caveats

- The live figures come from a24559, which predates round 5's rewritten rows (S149, S173, S210–S214).
- **Regularity.** The ±1-segment regularity figure is a lower bound by construction. It shows how wide the conditioning
  is, not that any change is irregular.
- **Recoverability.** The "merged in every daughter" figure uses unconditioned majority reflexes, so a conditioned
  survival of a contrast is missed: the true recoverable share is higher.
- **Real-language details** are from memory and textbooks, and marked ≈ where approximate: Hawaiian counts, dates,
  Bantu spirantisation outputs and real rate ranges. Check them before quoting.
- **"Human-voiced"** follows `profiles.human_voiced` on the stored profiles: 19 peoples. Dragons, kenku and the other
  non-human voices are left out of every live figure.
- **No inbox drafts.** The brief was read-only, so I did not write any. Items 4 and 9 are needs-decision candidates;
  items 1–3 are slam dunks.
