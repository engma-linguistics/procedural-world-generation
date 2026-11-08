# Phonology coverage review: eight real languages against the generator

Branch `lang-design` at 2ab724ea. This was a read-only review: nothing was changed. Code paths below are relative to the
worktree. "Live" figures are from the 627 living lects of run a24559, tallied read-only from `runs/a24559/languages.json`.
I split them by voice:

- **321 human-voiced lects.** Their people's profile has the human articulators, and no non-human percept is cheaper than
  harsh voice, as `profiles.py:414 human_voiced` defines it. These are bugbear, the five giants, drow, dwarf, elf, firbolg,
  gnome, goblin, goliath, halfling, hobgoblin, human, orc, sea elf and triton. They are judged against the real world.
- **306 other lects.** These are dragons, dragonborn, kobolds, lizardfolk, tortles, kenku, aarakocra, tabaxi and leonin.
  They are judged against their own profiles (§5.4).

The scripts are in the scratchpad `pg/` folder. PHOIBLE figures are from `planet/language/data/phoible_segments.tsv` and
`phoible_inventory_sizes.tsv`. WALS and other typological figures are from memory and approximate, and are marked "≈".

**Run a24559 predates round 5's segment fixes.** The file is from 11-04. Round 5 (calibration.md "Round 5, core lane")
cut the over-produced ɹ, ʁ, ɫ, ɦ and ʐ. Where those sounds matter below, I give the round-5 figure beside the live one.
Nothing else in this review depends on round 5.

## How to read "coverage"

The scale is the same as in the grammar review:

- **full**: the engine draws or derives the feature, keeps it, and shows it in the IPA, the sketch and the audio.
- **partial**: something exists, but it is thinner than the real feature, rarely realised, or lost over time.
- **label only**: a value is stored and printed, but nothing in the forms or the audio carries it out.
- **none**: no axis, no draw, no rule and no output.

---

## 1. Summary table

| Language | Distinctive feature | Coverage | Note |
|---|---|---|---|
| **English** | 24 C incl. θ ð ɹ; ~12 vowel qualities, tense/lax, diphthongs | full / partial | diphthongs only as V+V sequences |
| | Onsets up to 3 (spl-), codas up to 4 (-ksts) | none | `MAX_ONSET = MAX_CODA = 2` (`inventory.py:44`) |
| | Lexical, weight-sensitive stress; unstressed vowels reduce | label only | stress is a fixed-position enum, never written into the IPA or passed to the audio |
| | Allophony: aspiration, flapping, dark l, glottalling | partial | word-initial aspiration and coda dark l only; no stress conditioning |
| | -s/-z/-ɪz and -t/-d/-ɪd allomorphy | none | boundary rules are hiatus glides and nasal assimilation only |
| **Hawaiian** (+ Rotokas) | 8 C (Rotokas 6), 5 V | partial | the sizes arise; the makeup is wrong (rare sounds in tiny inventories) |
| | Strict (C)V | partial | 12% of protos; 2% of living lects still realise it |
| | Length on every vowel quality | partial | long vowels are drawn per quality (median: a third paired) |
| | Long words from a small syllable space | full | `lexicon.syllable_space` |
| **Taa (!Xóõ)** | 80+ clicks at 5 places with ~17 accompaniments | partial | 5 places possible, at most 6 accompaniments; max 53 C (human) |
| | Clicks almost only root-initial | none | 30% of click tokens are word-initial |
| | Breathy, pharyngealised and epiglottalised vowels | partial | the axes exist; harsh costs ×30; no pharyngealised vowels |
| | Tight root canon (CVCV, CVV, CVN) | none | |
| **Georgian** | Voiced/aspirated/ejective at each place, incl. qʼ | partial | ejectives exist (24%), but series are drawn segment by segment |
| | Onsets of 3–6+ consonants, "harmonic" clusters | none | hard cap of 2; no lect has more than 4% of words with a 3-C onset |
| | 5 vowels, no length, no tone | full | |
| **Yoruba** | Labial-velar stops k͡p ɡ͡b, no p | none | **bug: the PHOIBLE draw pool drops multi-letter segments** (`inventory.py:221`) |
| | Three level tones on every syllable | partial | 79 of 101 tonal human lects have 5 tones; tones are random per syllable |
| | 7 oral vowels (ATR-type e/ɛ, o/ɔ) + nasal vowels | partial | no ATR axis; nasal vowels in 14% (WALS ≈ 26%) |
| | (C)V and syllabic nasals | partial / none | a word must have a vowel (`inventory.py:690`) |
| | Vowel assimilation and elision across words | partial | hiatus repairs in history; glides at boundaries in sentences |
| **Finnish** | Front/back harmony with neutral i e | partial (fades) | one sound change; nothing keeps it alive |
| | Length contrast on all 8 vowels and on consonants | partial | geminates: 18% of protos, 1% of living lects |
| | Consonant gradation | none | |
| | Initial stress + secondary stress | partial | initial yes, secondary none, never heard |
| **Arabic** | Pharyngeals ħ ʕ, uvulars q χ | partial | ħ/ʕ in 2 human lects (WALS ≈ 4%); q nearly gone, ʁ everywhere |
| | Emphatics (tˤ sˤ dˤ ðˤ) and emphasis spread | none in practice | the axis exists; 0 human lects |
| | 3 qualities × length; superheavy syllables | partial | 3-quality systems in 2%; no syllable weight |
| | Weight-sensitive stress | none | |
| | Root-and-pattern (k-t-b) | none | concatenative only |
| **Japanese** | Moras; codas only N and the first half of a geminate | partial | a "nasal-only coda" class exists in ~8% of protos |
| | Lexical pitch accent | none | |
| | t>tɕ/_i, t>ts/_ɯ, s>ɕ/_i, high-vowel devoicing | partial | a "palatal" place test, no affrication, no devoicing |
| | Rendaku (compound voicing) | none | |

---

## 2. Why these eight

The brief fixed English. I picked the other seven so that every row of the brief's checklist has one extreme case, and so
that each tests a different part of the engine.

- **Hawaiian.** The smallest common type: 8 consonants, 5 vowels with length, strict (C)V and long words. It tests the
  small end of the size prior, the "simple" syllable type and whether the template survives 20 kyr of sound change.
  Rotokas (6 consonants, no nasals) is the more extreme inventory, so I note it inside the Hawaiian section rather than
  spend a slot on a second CV language.
- **Taa (!Xóõ, East).** The largest inventory on record: clicks, many accompaniments and vowel phonation. It tests the
  click system and the top of the size range.
- **Georgian.** Large clusters and a three-way laryngeal contrast with ejectives. It tests the cluster caps and whether
  consonants come in series.
- **Yoruba.** Three level tones, labial-velars, ATR-type vowels, nasal vowels and no codas. I chose it over Cantonese
  because it also tests West African segments and the CV template. Cantonese's six tones come up in §5.
- **Finnish.** Vowel harmony, length on every vowel, consonant gemination and gradation. I chose it over Turkish because it
  adds geminates and gradation. Turkish rounding harmony is covered by the same harmony code.
- **Arabic.** Pharyngeals, emphatics, uvulars, a 3-vowel system with length, weight-sensitive stress and root-and-pattern
  morphology.
- **Japanese.** Moras, lexical pitch accent and a cluster of well-known allophonic rules. It tests prosody beyond stress
  and tone. French nasal vowels and Danish stød are covered in §5 instead.

---

## 3. What the engine has, in brief (checked in code)

**The percept space** (`percepts.py:29-51`):

- 20 ordinal axes: 9 places, 10 manners, voice, 4 airstream/VOT values, 5 phonations, 4 secondary articulations, sibilant,
  vowel height (7) / backness (5) / rounding, nasal, length, 7 tone codes, plus retroflex, labiodental, lateral, double
  (labial-velar) and prenasal.
- IPA in and out is injective (`to_ipa`, `:371`). The space is rich enough for almost every PHOIBLE segment.
- **There is no ATR, stress, syllabicity or fortis/lenis axis.**

**Drawing a proto-inventory** (`inventory.py:509 draw_inventory`):

- Sizes come from PHOIBLE. Segments are picked one at a time, weighted `freq / (1 + cost)` with a saturating
  feature-economy bonus (`ECON 0.6`, `:395-411`) and a vowel dispersion floor (`MIN_V_DIST 1.5`, `:414-443`).
- Clicks come as a places × accompaniments system (`:453-477`).
- Tone: PHOIBLE's tonal share, with the count from PHOIBLE's tone counts mapped onto fixed sets (`:480`, `:528-537`).
- One of three WALS 12A syllable types (`:491-506`), a coda class of any / sonorant / nasal (`:539-541`), and a stress
  value from four (`:35`, `:542`).

**Words.** `draw_word` (`:613`) builds words from the templates. `legal` (`:680`) and `repair` (`:817`) enforce them on
new words, loans and derivations, but not on the output of sound change.

**Allophones.** Eight complementary-distribution tests (`:957-966`) are run on the lect's own forms (`phonemic`, `:1055`).

**Sound change** (`rules.py`):

- About 220 catalogue rows plus ~25 demo rules.
- Stress-conditioned rules use the fixed stress position (`rules.py:298`).
- Rows that need a tone system, a morphological condition ("suffix") or an ATR axis are skipped by the parser
  (`rules.py:1015-1020`). That includes S132–S134, the suffix-harmony and ATR-harmony rows.
- Vowel harmony is one demo rule, `harmony.back`, which assimilates every vowel to the root's first vowel
  (`rules.py:1768`).
- Tonogenesis has three pathways (`rules.py:1776-1793`), and tone phonemicizes in `lect.py:958 tone_hygiene`.

**Morpheme boundaries in sentences** (`sentences.py:242 join`): a glide or ʔ is put into hiatus, and a nasal takes the
place of a following stop. Nothing else.

**Audio** (`speak.py`):

- Piper (an English VITS voice) or eSpeak NG ('hi' phoneme table), with numpy effects for tone, clicks, phonation and the
  non-human percepts.
- The server takes only IPA and a people id (`planet/server.py:208`).
- **No stress mark is ever in the IPA it receives.**

---

## 4. Per-language sections

### 4.1 English

**What makes it distinctive:**

1. A medium consonant inventory (24) with typologically rare θ ð (WALS 19A ≈ 7%) and the very rare approximant ɹ (PHOIBLE
   1.7%).
2. A large vowel system: about 12 monophthong qualities (RP), tense/lax pairs (iː ɪ, uː ʊ), several phonemic diphthongs
   (aɪ aʊ ɔɪ eɪ əʊ), and no phonemic nasality.
3. Complex syllables. Onsets go up to 3 consonants (*spl-*, *str-*, *skw-*: s + stop + liquid or glide only). Codas go up
   to 4 (*texts* -ksts, *sixths* -ksθs).
4. Lexical, partly weight-sensitive stress, with heavy reduction of unstressed vowels to ə. Stress-timed rhythm, and stress
   shifts in derivation (*phótograph*, *photógraphy*).
5. Rich allophony: aspiration of voiceless stops at the start of stressed syllables, American flapping (*water* [ɾ]),
   velarised coda l, glottal reinforcement and t-glottalling, vowel lengthening before voiced codas.
6. Morphophonology:
   - plural and past allomorphy by voicing assimilation and epenthesis (-s/-z/-ɪz, -t/-d/-ɪd);
   - trisyllabic laxing (*divine*, *divinity*);
   - velar softening (*electric*, *electricity*).

**Coverage:**

- **Inventory: full.** Everything English has is in the pool. Sizes are well calibrated: living human consonants are
  11/17/21/24/37 at p5/q1/med/q3/p95, against PHOIBLE's 12/17/21/27/42. θ/ð are in 6% of living human lects (≈ WALS).
- **The ɹ was over-produced** (34% live, PHOIBLE 1.7%). Round 5 brought it to 5%.
- **Vowels: partial.**
  - Tense/lax pairs exist as segments (ɪ ʊ; 16 human lects, 5%, have three or more of the i/ɪ u/ʊ e/ɛ o/ɔ pairs).
  - Diphthongs are never phonemes. PHOIBLE's diphthong rows are dropped from the pool (`inventory.py:224`). A falling V+V
    sequence is allowed in words (`inventory.py:117 _diphthong`) and is written as two vowels.
  - There is no synchronic reduction to ə. The reduction and syncope rules are diachronic (`rules.py:1755`).
- **Clusters: none.**
  - `MAX_ONSET = MAX_CODA = 2` (`inventory.py:44-45`) is a hard cap on every drawn and repaired word. The comment says
    this keeps the demo readable.
  - s + stop is the only falling onset allowed (`_s_cluster`, `:48`). *str-* (s + stop + liquid) is therefore impossible.
  - Sound change does make a few 3-C onsets (89 human lects have at least one), but never in a structured way, and at most
    3.8% of a lect's words.
- **Stress: label only.**
  - The lect has a fixed-position value: none 32%, penult 40%, initial 21%, final 6% of living human lects. It conditions
    sound change correctly.
  - But no form in `languages.json` carries a stress mark. The sketch prints a sentence about it
    (`tools/language/sketch.py:804`).
  - The audio never hears it. Piper is given no marks, so it stresses the **first vowel of every word**
    (`speak.py:335-337`). eSpeak gets none either (`speak.py:241`).
  - Lexical stress, weight sensitivity and secondary stress do not exist (`rules.py:298 stressed_vowel`).
- **Allophony: partial.**
  - Present: word-initial aspiration (the `initial` test, not conditioned by stress) and coda ɹ/ɫ (round 5).
  - Missing: flapping (t → ɾ is a manner change that no test covers: `_pair_tests`, `inventory.py:988`), glottalling and
    vowel length before voiced codas.
- **Morphophonology: none.**
  - `sentences.py:242 join` only inserts glides in hiatus and assimilates a nasal's place.
  - A C-final stem plus an s-suffix is joined raw, with no voicing agreement and no epenthesis.

**Could a generated language look and sound like English?** It could look somewhat like English, but it would not sound
like it.

- The most English-like living lect, halfling d646.2 (score 0.770, `sketches/d646.2-halfling.md`), has p b d k ɡ f s m n ŋ
  l ɹ j w, five of English's vowels and initial stress.
- But it has no /t/ beside /d/, words like *kajbpu* and *iəjnə*, and syllables of at most CCVCC.
- Its English-like rhythm would come from the TTS, not from the lect: Piper's first-vowel stress happens to match an
  "initial" lect.

### 4.2 Hawaiian (with Rotokas)

**What makes it distinctive:**

1. A tiny inventory: /p k ʔ h m n l w/ plus 5 vowels. Rotokas has /p t k b d ɡ/ (with β ɾ allophones), no nasals and 5
   vowels.
2. Strictly (C)V. No clusters, no codas, frequent VV sequences, and diphthongs.
3. Length contrast on all five vowels (the kahakō).
4. ʔ as a full phoneme (the ʻokina).
5. Long words, because the syllable space is so small.
6. Penultimate stress by moraic feet, with secondary stress.
7. Small inventories are built from the commonest sounds, which is the universal pattern (Lindblom & Maddieson 1988).

**Coverage:**

- **Size: full.**
  - 13% of living human lects have 14 or fewer consonants, and the smallest has 7.
  - The calibration rounds tuned this end on purpose (3.2% at 10 or fewer in run F, against PHOIBLE's 1.4%).
- **Makeup: wrong.**
  - Small lects carry rare sounds. In human lects with 14 or fewer consonants, 17% of the consonants have a PHOIBLE share
    under 10%. In lects with 25 or more consonants the figure is 33%, so there is some gradient, but not enough.
  - Fire giant d196.2 has 8 consonants: n t k dʒ s ʁ h j. That is a uvular and a postalveolar affricate, but no labial at
    all, and vowels i e ɛː a with no back vowel. It is the inherited dragon inventory (§5.4).
  - Human d686.1 has 11 consonants, p h m ħ ɭ t s ʂ j f ʁ: a pharyngeal, two retroflexes and a uvular, but no k and no n.
  - Hawaiian's and Rotokas's inventories are their languages' commonest sounds.
  - Cause: the pick weight `freq / (1 + cost)` (`inventory.py:391`) does not depend on the target size. The size steer in
    sound change counts phonemes, not which ones survive.
- **(C)V: partial.**
  - "Simple" is drawn for 12% of protos (`inventory.py:36`, WALS 12A). Half of those require an onset (`:548`).
  - Only **6 of 321** living human lects still realise (C)V words with no clusters and no codas. 10 have no codas.
  - The template is never re-derived after sound change. Of the 43 human lects that declare "no codas", 9 have more than
    5% consonant-final words. Of the 87 that declare single onsets, 34 have more than 2% cluster-initial words.
  - The sketch prints the proto template as if it were current (`sketch.py:801`).
- **Vowel length: partial.**
  - Long vowels are drawn one quality at a time from PHOIBLE (iː 32%, aː 31% …).
  - In the median lect with long vowels, only a third of its short qualities have a long partner. Hawaiian, Finnish,
    Arabic and Japanese pair all of them.
- **ʔ: full.**
- **Long words: full.**
  - `lexicon.syllable_space` and `length_scale` lengthen words in small syllable spaces.
  - Hill giant d27 (12 C, CV) has *iɹiʔijiɹeli*, *lɨpɛnʷoʔa*. That reads very Polynesian in shape, but with ɕ ʑ nʷ ɹ in
    the inventory.
- **Penult stress: partial.** It is fixed penult only, with no feet, no secondary stress, and nothing audible.

**Could a generated language look and sound like Hawaiian?** In shape, rarely. In segments, not yet.

- d27 is the closest: CV-only, 12 consonants and long vowel-rich words. But a Hawaiian-like lect would need the core
  inventory, all qualities paired for length, and a template that sound change cannot break.
- A Rotokas-like lect (10 or fewer C, 5 or fewer qualities, no tone) exists once (d196.2), and its makeup is far from
  Rotokas.

### 4.3 Taa (!Xóõ, East Taa)

**What makes it distinctive:**

1. The largest inventory known: ~85–160 consonants depending on the analysis (Traill 1985), of which ~80 are clicks.
2. Clicks at five places (ʘ ǀ ǃ ǂ ǁ), each with up to ~17 accompaniments. These include voiced, nasal, aspirated,
   glottalised, delayed-aspirated, uvular-affricated and uvular-ejective releases.
3. Clicks occur almost only root-initially. Most lexical roots begin with a click, and the "back vowel constraint" links
   the click type to the following vowel.
4. Vowel phonation contrasts: plain, breathy, pharyngealised, epiglottalised (strident) and nasal, plus length.
5. A tight root canon: CVCV, CVV, CVN.
6. Tone (two or more levels, with contours).

**Coverage:**

- **Clicks: partial, with a good mechanism.**
  - `click_system` (`inventory.py:467`) gives 3–5 places × up to 6 accompaniments (plain, voiced, nasal, aspirated,
    glottalised, breathy).
  - Clicks are found in 3% of living human lects (WALS 19A ≈ 1.6%). That is fine at this sample size.
  - Two lects reach 50 or more consonants: drow d725, the sketched one, with 51; and elf d551.
  - There are no uvular-contour or delayed-aspiration series, so the ceiling is 30 clicks.
  - The top human inventory is 53 consonants, against Taa's ~130.
- **Click position: none.**
  - Clicks are weighted `CLICK_LEX_FREQ 0.5` and drawn into any onset (`_onset_cluster`, `inventory.py:577`).
  - In click lects, **only 30% of click tokens are word-initial**, and 17% of words have a click.
  - In Taa the share is the reverse: clicks are mostly root-initial, and medial clicks are rare.
  - The drow sketch shows medial clicks freely (*no̞ǂ̬oto*, *ʃɛjat̪e̞ʘe*).
- **Vowel phonation: partial.**
  - Breathy and creaky vowels exist on the phonation axis, and harsh (epiglottalised) exists at ×30 cost for humans
    (`profiles.py:86`).
  - A pharyngealised vowel (secondary 4 on a V) is not in the pool. No human lect has one.
- **Root canon: none.** There is no notion of a root template separate from the word template.
- **Tone: full** (but see §5.3 for the tone counts).

**Could a generated language look and sound like Taa?**

- On a page, partly: d725 has ~30 clicks at all five places, with voiced, nasal, aspirated and ejective series.
- To a Khoisanist, no. The clicks fall anywhere in the word, the vowels are plain (with an implausible e/e̞/ɛ three-way
  contrast), and the roots have no shape.
- In audio, the clicks are numpy transients over a closure (`speak.py:462-480`), which the brief accepts.

### 4.4 Georgian

**What makes it distinctive:**

1. A three-way laryngeal contrast at each stop and affricate place: voiced b d ɡ dz dʒ, aspirated pʰ tʰ kʰ tsʰ tʃʰ, and
   ejective pʼ tʼ kʼ tsʼ tʃʼ, plus uvular qʼ.
2. Uvular and velar fricatives (χ ʁ, or x ɣ by analysis).
3. Very large onset clusters: up to 6–8 consonants (*gvprckvni* 'you peel us', *mtsvrtneli* 'trainer'), with no sonority
   rise required.
4. "Harmonic clusters": coarticulated front-to-back pairs that share a laryngeal setting (bɡ, tʼkʼ, tsʰkʰ).
5. A plain five-vowel system /i e a o u/, with no length, no tone and weak (initial or antepenult) stress.
6. Stem syncope in inflection (*kʰalakʰi*, *kʰalakʰ-is*).

**Coverage:**

- **Laryngeal series: partial.**
  - Ejectives are in 24% of human lects (WALS 7A ≈ 17% with ejectives).
  - But each segment is drawn on its own. The economy bonus counts a "series" only as an exact manner.voice.larynx.secondary
    match (`inventory.py:399`) and saturates at 3. So a lect with kʼ often lacks pʼ and tʼ.
  - Aspirates are in only 7% of human lects (PHOIBLE kʰ alone 17%).
  - A full voiced/aspirated/ejective grid at three places is something I did not find in any living human lect.
- **Uvulars: full but skewed.**
  - Uvulars are in 36% of human lects (WALS 6A ≈ 17%). Almost all of it is ʁ (32%), from r > ʁ.
  - q is in 0.3% (PHOIBLE 7.6%) and χ in 1% (PHOIBLE 7.7%).
  - Round 5 cut ʁ to 10% of human lects, but q and χ were not addressed.
- **Clusters: none.**
  - There is a hard cap of 2 and sonority-rising onsets only (`_onset_pair_ok`, `inventory.py:54`), apart from s + stop.
  - No living lect has 3-C onsets in more than 3.8% of its words.
  - Harmonic clusters (stop + stop) are explicitly illegal.
- **Five vowels: full.** But the exact system /i e a o u/ appears in **14 of 321** human lects (4%). Most lects have 7–9
  qualities (§5.3).
- **Syncope: partial.** It happens as a sound change, and as an alternation only in the 4+4 exemplar paradigms (grammar
  review §5.2).

**Could a generated language look and sound like Georgian?** No. The defining feature, the cluster, is capped away.

### 4.5 Yoruba

**What makes it distinctive:**

1. Labial-velar stops k͡p ɡ͡b, and no /p/.
2. Seven oral vowels with an ATR-type split (e/ɛ, o/ɔ) and five nasal vowels (ĩ ɛ̃ ã ɔ̃ ũ).
3. Three level tones (H M L) on every syllable. Contours arise from sequences. There are downdrift and downstep.
4. Syllables V, CV and syllabic nasal (N̩, as in *ń lọ* 'I am going'). No codas, no clusters.
5. Partial ATR vowel harmony: prefix vowels agree with the root.
6. Heavy vowel assimilation and elision across word boundaries, with tone stability (the tone of an elided vowel stays).
7. Nasal assimilation, and nasalisation of vowels after nasals.

**Coverage:**

- **Labial-velar stops: none. This is a bug, the most important single finding.**
  - `phoible_pool` parses each PHOIBLE row with `from_ipa` and drops any row that does not parse to exactly one segment
    (`inventory.py:220-225`).
  - PHOIBLE writes these sounds as plain letter sequences: kp (13.9%), ɡb (13.8%), mb (11.7%), nd (10.9%), ŋɡ (10.9%),
    n̠d̠ʒ, ŋm, ndz. Each of them parses to two segments, so each is dropped. I counted 121 rows dropped in all, against
    296 consonants and 121 vowels kept.
  - `profiles.human_freq` does use `parse_segment`, which folds these sequences (`percepts.py:304`). So the cost table
    knows them, but the draw never offers them.
  - Result: k͡p and ɡ͡b are in **0** living lects. Prenasalised stops are in 3%, and those are almost all clicks. WALS 19A
    puts labial-velars at ≈ 8%.
  - Fix: use `parse_segment` in `phoible_pool`, and keep the diphthong rows out explicitly.
- **Tone: partial.**
  - Tonal shares are good: 38% of all living lects and 31% of human ones (WALS 13A ≈ 42%).
  - But **79 of the 101 tonal human lects have 5 tones and 20 have 4. One has 3 and one has 2.** WALS 13A has about 60% of
    tonal languages "simple" (two-tone). PHOIBLE's own counts, among tonal inventories, are 2: 28%, 3: 35%, 4: 20%,
    5: 10%, 6+: 7%.
  - The likely cause, found in the code: identical-vowel fusion turns two level tones into a contour
    (`inventory.py:86 _fused_tone`, used by `fuse_vowels` and `_resolve_vowels`). `observed` then lists each new contour
    as a tone of the lect (`lect.py:939-946`).
  - So a [L, H] system becomes [L, H, rising, falling]. In Yoruba and Bantu, such contours are a sequence of two levels on
    a long vowel, not new tonemes. Proto tone counts are already skewed (human protos: 2: 11%, 3: 13%, 4: 31%, 5: 45%),
    because the protos' words have been through repair.
  - `_TONE_SETS` (`inventory.py:480`) also stops at 5, so Cantonese and Hmong (6–8) cannot arise.
  - Tones are drawn at random per vowel (`_toned`, `:607`). The share of words carrying one tone throughout is at chance
    (0.40 against 0.38).
  - There is no OCP, no word melody, no downstep, no floating tone and no tonal morphology. The tone-rule rows are skipped
    (`rules.py:1018`).
  - The audio has a gentle downdrift, but only in the speech layer (`speak.py:668`).
- **ATR vowels: partial.** The qualities exist (ɪ ʊ ɛ ɔ), but no ATR feature groups them, and S134 (ATR harmony) is
  skipped (`rules.py:1020`).
- **Nasal vowels: partial.**
  - Present in 31% of human protos (WALS 10A ≈ 26%), but in only 14% of living human lects.
  - They erode over time. Some are also reclassified as allophones before a nasal (the `nasal_vowel` test), which is
    correct for French-type histories.
- **(C)V: partial** (see §4.2).
- **Syllabic nasal: none.** `legal` needs a vowel in every word (`inventory.py:690`), and tone sits only on vowels.
- **Cross-word vowel elision: partial.**
  - Hiatus is resolved inside words in history (calibration.md "Hiatus round").
  - In sentences, `join` inserts a glide or ʔ (`sentences.py:248`). Yoruba would elide instead.

**Could a generated language look and sound like Yoruba?** Only roughly.

- One lect comes close: triton d817 has 3 tones, nasal vowels, ŋ͡m and few codas.
- Its tone set is L, H and *falling*, assigned at random. It has no k͡p or ɡ͡b, and its vowel system is 16 phonemes.
- The pitch rendering is credible: level tones are pitch-shifted on the vowel span.

### 4.6 Finnish

**What makes it distinctive:**

1. Front/back vowel harmony (y ø æ against u o ɑ), with i and e neutral. It controls every suffix (*talo-ssa*,
   *kylä-ssä*).
2. Length contrast on all 8 vowels, plus many diphthongs.
3. Contrastive consonant gemination (*tuli* 'fire', *tulli* 'customs'; *kuka*, *kukka*).
4. Consonant gradation: a morphophonological weakening in closed syllables (kk~k, t~d, nt~nn, k~∅).
5. Fixed initial stress, with secondary stress on odd syllables.
6. A small consonant inventory (13 native), few word-final consonants, and no initial clusters in native words.

**Coverage:**

- **Vowel harmony: partial, and it fades.**
  - `harmony.back` (`rules.py:1768`) is a one-time sound change. When it fires, every vowel in every stored form takes the
    backness and rounding of the root's first vowel.
  - Nothing keeps the pattern afterwards. `draw_word`, `repair`, compounds, derivations, loans and the sentence `join` all
    ignore it.
  - The two suffix-harmony rows S132 and S133, which would make affixes alternate, are skipped as "morphology-conditioned"
    (`rules.py:1019`).
  - There is no neutral-vowel concept, so the rule harmonises i and e as well.
  - Measured: in 133 human lects where the rule fired somewhere in the line, the adjacent-pair front/back agreement ratio
    is 1.24× chance, against 1.19× over all human lects. The harmony has washed out by the present day.
  - No living human lect looks harmonic once trivial cases are removed. The 1.0 agreements are elf lects such as d846,
    which have no back non-low vowel at all.
- **Vowel length: partial** (per quality, see §4.2). Long vowels are in 77% of human lects, which is too many (§5.3).
- **Geminates: partial, and they decay.**
  - Long consonants are drawn in 18% of human protos but survive in **1%** of living ones.
  - Identical CC sequences, functionally geminates, appear in more than 2% of words in 47 human lects (15%). But these are
    two segments, so the phoneme table, the sketch and the romanization never call them geminates.
- **Gradation: none.** Alternations exist only where sound change ran over the exemplar paradigms.
- **Initial stress: partial** (label only in the output; no secondary stress).
- **Coda restrictions: partial.** The coda class (any / sonorant / nasal) exists only for non-complex lects
  (`inventory.py:540`) and is not updated after change.
- **Front rounded vowels: full, but over-produced.** 13% of human lects (WALS 11A ≈ 7%) and 38% of the others.

**Could a generated language look and sound like Finnish?** At the surface, briefly, as "long vowels plus y ø æ plus
initial stress". Harmony, the trait any reader would look for, cannot be kept, and neither can gemination.

### 4.7 Arabic (Classical / Modern Standard)

**What makes it distinctive:**

1. Pharyngeals ħ ʕ, uvulars q χ ʁ, glottals ʔ h. No p and no v.
2. The emphatics tˤ dˤ sˤ ðˤ: a pharyngealised series whose emphasis spreads to neighbouring vowels, backing and lowering
   them.
3. Three vowel qualities (a i u), each with length, and the diphthongs ay aw.
4. Syllables CV, CVV, CVC and superheavy CVVC, CVCC. Obligatory onsets, and no onset clusters in Classical.
5. Contrastive gemination.
6. Weight-sensitive stress: on a superheavy final syllable, else on a heavy penult, else on the antepenult.
7. Root-and-pattern morphology: consonantal roots (k-t-b) interleaved with vowel templates (*kataba*, *kitāb*, *maktab*).
8. Assimilation of the article to coronals (*al-šams* > *aš-šams*).

**Coverage:**

- **Pharyngeals: partial.**
  - ħ (2.7%) and ʕ (2.0%) are in the pool.
  - But **2 of 321** living human lects (0.6%) have one (WALS 19A ≈ 3.7%). Among the other lects it is 24%: kenku, dragons
    and dragonborn.
- **Uvulars: skewed** (§4.4). q is almost gone.
- **Emphatics: none in practice.**
  - Secondary 4 (pharyngealised) is an axis, and pharyngealised segments are in PHOIBLE (sˤ 0.4%, tˤ 0.3%, dˤ 0.3%). That
    gives them a near-zero draw weight one by one.
  - No living human lect has one, because there is no series-level draw.
  - No emphasis-spread allophony exists. Book mode drops ˤ (`romanize.py:294 _BOOK_DROP`).
  - The audio drops it too (`ipa_to_speech.tsv` row ˤ: "no backend renders it").
- **Three vowels with length: partial.** Three-quality systems are in 2% of human lects (WALS 2A "small", 2–4 qualities,
  ≈ 16%). Length pairing is incomplete.
- **Weight, superheavies, weight-sensitive stress: none.** There is no mora or weight concept anywhere.
- **Gemination: partial** (§4.6).
- **Root-and-pattern: none.** It needs non-concatenative morphology (grammar review §5.1 item 8).
- **Article assimilation: none.** `join` assimilates nasals only.

**Could a generated language look and sound like Arabic?** No. No living lect has a pharyngeal, a uvular stop, long vowels
and 4 or fewer qualities together, and the emphatic series, the most recognisable Arabic sound, never forms.

### 4.8 Japanese

**What makes it distinctive:**

1. Mora timing. Syllables are (C)(j)V(N/Q): the only codas are the moraic nasal and the first half of a geminate.
2. A lexical pitch accent. Each word is either unaccented or has an H*L fall after a given mora (*háshi* 'chopsticks',
   *hashí* 'bridge', *hashi* 'edge').
3. Five vowels (a i ɯ e o) with length. Diphthongs are sequences.
4. Well-known allophony:
   - t → tɕ before i, and t → ts before ɯ;
   - s → ɕ before i;
   - h → ç before i, and h → ɸ before ɯ;
   - high vowels devoice between voiceless consonants;
   - the moraic nasal takes the place of what follows.
5. Rendaku: voicing at the start of the second member of a compound (*hito* + *hito* > *hitobito*).

**Coverage:**

- **Mora codas: partial.**
  - `coda_class = "nasal"` (`inventory.py:151`, drawn in 15% of moderate lects) gives CV(N).
  - There is no mora, no Q (a geminate as a coda), and no mora count anywhere.
- **Pitch accent: none.** Tone is either per-vowel lexical tone or nothing, and stress is a fixed position. There is no
  "one accent per word, or none" system.
- **Five vowels with length: partial.** One near-match: elf d744 has 16 C, 5 qualities, long vowels and few codas.
- **Allophony: partial.**
  - The `palatal` test (`inventory.py:997`) covers a change of place before front vowels.
  - Affrication (t → ts) and vowel devoicing are not tests.
  - The engine can produce these changes as sound changes, but cannot treat them as allophones.
- **Rendaku: none.** Compounds concatenate and `repair` (`lexicon.py:1489`). No linking or voicing process exists.
- **Moraic nasal assimilation: full**, at boundaries (`sentences.py:255`) and as the `nasal_place` allophone test.
- **Mora-timed audio: none.** The voice is English (Piper) or Hindi-table eSpeak, at word level.

**Could a generated language look and sound like Japanese?** It could look somewhat like Japanese: CV(N), five vowels,
long vowels. It could not sound like it, because there is no pitch accent.

---

## 5. Cross-cutting picture

### 5.1 Missing entirely

1. **Audible and visible stress.**
   - No form carries ˈ, so the viewer, the sketches and the audio never show stress.
   - The audio stresses every word's first vowel (`speak.py:335-337`).
   - Lexical stress, weight-sensitive stress, secondary stress, stress-timed rhythm and vowel reduction as allophony are
     all absent.
2. **Syllable weight and moras.** These are needed for Arabic, Latin and Finnish-type stress, Japanese, and
   compensatory-lengthening logic.
3. **Pitch accent** (Japanese, Swedish/Norwegian word tones, Serbo-Croatian, Lithuanian).
4. **Clusters beyond two** (`inventory.py:44-45`), stop + stop onsets, harmonic clusters, and syllabic consonants (Czech
   *vlk*, Berber, English *button*).
5. **Synchronic vowel harmony** as a property of the lect, ATR as a feature, and neutral vowels.
6. **Tone structure.** Tonal phonotactics (OCP, privative H systems as in Bantu), downstep, floating tones, tone sandhi
   (Mandarin 3-3, Min circles), grammatical tone, and tone on syllabic nasals.
7. **Positional phonotactics per segment.**
   - ŋ is word-initial in **276 of 277** human lects that have it (WALS 9A ≈ 38%).
   - Clicks can stand anywhere.
   - h, ʔ and the glides take no positional limits.
   - Only the onset-cluster and coda-class rules exist.
8. **Labial-velar and prenasalised stops in protos** (the `phoible_pool` bug, §4.5).
9. **An emphatic (pharyngealised) series** and emphasis spread.
10. **Morphophonology beyond hiatus and nasal place.** Missing: voicing assimilation and epenthesis at affix boundaries,
    consonant gradation, rendaku, Celtic-type mutation, sandhi between words, and templatic root-and-pattern morphology
    (this last is shared with the grammar review's Phase C).
11. **Phonemic diphthongs** (dropped from the pool, by design). This is defensible, but English, Finnish and Vietnamese
    count them.
12. **Prosodic laryngealisation** (Danish stød, Vietnamese glottalised tones) and **fortis/lenis** (Korean;
    voice-profiles.md open doubt 7).

### 5.2 Modelled too thinly

- **Allophony.**
  - 88 of 321 living human lects (27%) have any allophone, and most of those have one. Real languages essentially all have
    several.
  - The tests seen are intervocalic voicing or spirantisation (97), vowel nasalisation (35), final devoicing (14), nasal
    place (10) and palatal (3).
  - Missing: aspiration conditioned by stress, flapping, affrication before high vowels, vowel reduction, high-vowel
    devoicing, dark/clear l by position, emphasis spread, and vowel backing after uvulars.
  - And the allophones are only recorded. The IPA is the surface form, but nothing marks which segments are allophonic in
    a word.
- **The syllable template is a proto fossil.** `shapes`, `max_onset`, `max_coda` and `coda_class` are set at the draw and
  never updated. Sound change and wave borrowing can break them; only new words obey them. The sketch reports the
  fossil. Realised WALS 12A classes (my classifier over the lexicon) are in §5.3.
- **Vowel dispersion is checked only at the draw.**
  - 35% of living human lects have two vowel qualities closer than the draw's own floor (`MIN_V_DIST 1.5`).
  - 4% have a three-way e/e̞/ɛ or o/o̞/ɔ contrast. Drow d725 is one, and firbolg d197 has 15 vowels including ä ɘ ɜ ø.
  - The chain-shift repair runs only after a merger veto (architecture §5).
- **Inventories are drawn segment by segment.**
  - The feature-economy bonus is too weak to make sounds come in series.
  - The result is the over-shoots in §5.3: any retroflex 75%, any long vowel 77%, implosives 29%.
  - It also gives lone series members, such as kʼ without pʼ or tʼ, and labialisation on the wrong places. nʷ is in 14%,
    lʷ in 12% and ŋʷ in 13%, but kʷ in only 2% of living human lects. PHOIBLE has kʷ at 12.5% and nʷ/lʷ at about 1%.
- **The click system:**
  - at most 6 accompaniments;
  - no root-initial restriction;
  - no click-vowel constraints.
- **Small inventories are not built from basic sounds** (§4.2).
- **The audio layer.** It reads IPA only (no stress, no syllable boundaries). Piper replaces non-English sounds with
  English ones (audio.md: ʁ > ɹ, x > h, retroflexes > alveolars). eSpeak drops pharyngealisation and velarisation and
  renders ejectives as stop + ʔ and implosives as plain stops. The voice offset per people is good, but every lect of a
  people sounds the same apart from its segments.

### 5.3 Exists but wrongly calibrated (living human-voiced lects, n = 321)

| Feature | Live share (a24559) | Real reference | Cause found in code |
|---|---|---|---|
| **Labial-velar stops k͡p ɡ͡b** | **0%** | PHOIBLE 14%; WALS 19A ≈ 8% | `phoible_pool` drops multi-letter rows (`inventory.py:221-225`) |
| Prenasalised stops ᵐb ⁿd ᵑɡ | 3% (almost all clicks) | PHOIBLE 11% each | same |
| **Tone count among tonal lects** | 2: 1%, 3: 1%, 4: 20%, **5: 78%**; nothing above 5 | WALS 13A ≈ 60% two-tone; PHOIBLE 2: 28%, 3: 35%, 4: 20%, 5: 10%, 6+: 7% | Fusion turns level pairs into contour tonemes (`inventory.py:86`, `lect.py:939-946`); `_TONE_SETS` caps at 5 (`:480`) |
| Tonal share | 31% (all lects 38%) | WALS 13A ≈ 42% | fine |
| **Any retroflex** | **75%** (protos 68%) | ≈ 20% (UPSID; from memory) | Segment-by-segment draw: ʈ 15%, ɳ 14%, ɭ 13%, ɻ 12% … drawn almost independently |
| **Any long vowel** | **77%** (protos 74%) | ≈ 35–45% (PHOIBLE iː alone 32%) | Same, plus identical-vowel fusion makes long vowels |
| Implosives | 29% | WALS 7A ≈ 13% | Same; ɓ 20% vs PHOIBLE 11% |
| Ejectives | 24% | WALS 7A ≈ 17% | Same |
| No glottalised consonants | 56% | WALS 7A ≈ 72% | Same |
| Uvulars | 36% (ʁ 32%, q 0.3%) | WALS 6A ≈ 17%; PHOIBLE q 7.6%, χ 7.7%, ʁ 3.7% | r > ʁ (S148); round 5: ʁ 10% of humans; q and χ still rare |
| Palatalised / alveolo-palatal (ȶ ȵ ȴ ʲ) | 42% | no firm reference; members 2–14% each | Same draw effect |
| Labialised sonorants nʷ lʷ ŋʷ | 12–14% each | PHOIBLE ≈ 1–5% | A sound change on sonorants (not traced); kʷ only 2% |
| Pharyngeals ħ ʕ | 0.6% | WALS 19A ≈ 3.7% | Low draw weight, and no source rules |
| Nasal vowels | 14% (protos 31%) | WALS 10A ≈ 26% | Lost over time; source not traced |
| Front rounded vowels | 13% | WALS 11A ≈ 7% | Umlaut-type rules (S135) and the draw |
| No laterals | 8% | WALS 8A ≈ 17% | Draw (l 70% PHOIBLE) plus no exit rules |
| Vowel qualities (WALS 2A bins) | 2–4: 11%, 5–6: 25%, 7+: 65% | 2–4: 16%, 5–6: 51%, 7+: 32% | Drift adds qualities, and nothing re-disperses them (§5.2) |
| Exactly /i e a o u/ | 4% | the commonest system, ≈ a fifth or more (Maddieson; from memory) | Same |
| ŋ word-initially (lects with ŋ) | 99.6% | WALS 9A ≈ 38% | No positional phonotactics |
| Geminate consonants | 1% (protos 18%) | ≈ 10%+ (Italian, Finnish, Arabic, Japanese, Hungarian, Dravidian …; from memory) | Lost, and never re-created as phonemes; CC sequences in 15% are not called geminates |
| Realised syllable type (WALS 12A) | simple 2%, moderate 88%, complex 10% | 13% / 56% / 31% | Cap of 2 (complex end); no template enforcement after change (simple end) |
| Stress "none" | 32% (protos 40%) | WALS 14A "no fixed stress" 56%, mostly *lexical or weight-sensitive*, not absent | Definition mismatch (`inventory.py:35` "folded"; `sketch.py:804` prints "Stress is not phonemic (no fixed stress)") |
| Allophones present | 27% of lects | ≈ 100% | Eight tests; §5.2 |
| Consonant inventory size | 11/17/21/24/37 | PHOIBLE 12/17/21/27/42 | good |
| Voicing contrast in stops | 71% | WALS 4A ≈ 61% | fine |
| θ/ð | 6% | WALS 19A ≈ 7% | good |
| Clicks | 3% of human lects | WALS 19A ≈ 1.6% | fine for n = 321 |

**The series problem, in plain words.** The engine picks a language's sounds one at a time, each about as often as it
appears in the world's languages. Real languages instead pick whole sets: either they have retroflexes (and then usually
t, n, l and r all in retroflex form) or they have none. Picking one at a time gets each single sound's share right but makes
"has at least one of the set" far too common. That is why three quarters of the human lects have a retroflex, three
quarters have a long vowel and a third have implosives, while their series are patchy. The fix is to draw the series first
(with its share among world languages), then fill it. That one change addresses six rows of the table.

### 5.4 Non-human voices against their profiles

These lects are judged against their own profiles, not against Earth. Living lects by people:

| People | Lects | What shows | Against the profile |
|---|---|---|---|
| Dragons | 118 | harsh voice in 99%; 1.7 labials a lect (humans 4.2); tonal 23% | The profile's growl and lipless mouth show. **The sub-bass, which the profile makes cheap (`sub_register 0.5`; "part of the signal carried below ~20 Hz"), is in 0 lects.** `_NONHUMAN_VARIANTS` (`inventory.py:335`) offers growl, purr and a second voice, but no register variant, and no rule creates one. The audio's ˯ effect is therefore never used by a dragon. |
| Kenku | 27 | second voice ᴖ in 56%; growl 81%; tonal 67% | Fits (syrinx, pitch ear). |
| Aarakocra | 25 | second voice 32%; tonal 80%; 1.9 labials | Fits. |
| Tabaxi | 11 | purr in 82%, growl 91% | Fits. |
| Leonin | 6 | growl 100%, purr 0% | Purr costs 3.0, so this is plausible. |
| Kobold, dragonborn, lizardfolk, tortle | 53, 55, 4, 7 | few labials, growl 43–100% | Fits (reptilian mouth). |

One cross-voice issue: **a people that shifts language keeps the lect's old voice.** Fire giant d196.2 descends from the
bronze dragon proto-language. Its speakers shifted 10 kyr ago, and it still has no labials, no back vowels and a growled
a‼ (fire giants show harsh voice in 73% of their lects).

- That is defensible as a fantasy outcome: speakers who learned a draconic language keep its sounds.
- But the speakers' own voice profile only steers future changes. It never nativises the inherited sounds.
- A real shift leaves the shifting people's accent on the language (substrate phonology). The mechanism exists
  (`profiles.hear_word`); it is just not run on shift. This is a judgement call for Daniel.

---

## 6. Ranked recommendations

Value is how much more real-*looking* (RL: what a reader sees in IPA and spelling) and real-*sounding* (RS: what the audio
gives) the output gets, rated H/M/L. Cost: S = under a day, a few functions and tests; M = a few days, new structures and
recalibration runs; L = a week or more, or an architecture change.

| # | Recommendation | RL | RS | Cost | When |
|---|---|---|---|---|---|
| 1 | **Fix the PHOIBLE pool.** Parse rows with `parse_segment` in `phoible_pool` (`inventory.py:221`), so k͡p ɡ͡b ŋ͡m ᵐb ⁿd ᵑɡ ⁿdʒ enter protos at PHOIBLE's rate. Keep diphthongs out explicitly, and resolve the "either-or" rows (t̪\|t) to one. Re-check the top-20 overlap. | H | M | S | Before merge |
| 2 | **Draw series, not segments.** First draw which series a lect has (retroflex, uvular, ejective, implosive, aspirated, palatalised, labialised dorsals, pharyngealised, long vowels, nasal vowels, geminates), using PHOIBLE's "any member" share, which is derivable from `phoible.csv` per inventory. Then fill places within each series by economy. Fixes six rows of §5.3, gives full voiced/aspirated/ejective grids (Georgian), length on every quality (Finnish, Hawaiian, Arabic) and an emphatic series (Arabic). | H | M | M | Before merge if possible; else first after |
| 3 | **Tone counts and tone structure.** (a) Fusion of two level tones stays a sequence on a long vowel, or the contour is not added to `tones`. Let `_TONE_SETS` reach 6–8. Recalibrate against PHOIBLE's tone counts. (b) Later: tonal phonotactics (privative H, OCP), word melodies, downstep, and sandhi as rules (unblock the tone rows in `rules.py:1018`). | H | H | (a) S, (b) M–L | (a) before merge |
| 4 | **Make stress visible and audible.** Write ˈ into each form's displayed IPA from the lect's stress (and ˌ for secondary). Pass it to `/api/speak`. Stop Piper defaulting to the first vowel (`speak.py:337`). Rename `none` to "free / lexical" and either draw lexical stress per word or keep a true "no stress" value for tone languages, and fix the sketch line (`sketch.py:804`). | M | H | S | Before merge |
| 5 | **Small inventories from the core.** Raise the frequency exponent as the target size falls (e.g. `A_FREQ` 1 → 2 below 15 C), so an 8-consonant lect is p t k m n-type, not dʒ ʁ ħ ʂ. Check with a "rare-segment share by size" test against PHOIBLE. | M | M | S | Before merge |
| 6 | **Dragon sub-bass.** Add a register variant to `_NONHUMAN_VARIANTS` (`inventory.py:335`) for profiles with a finite `sub_register` cost, so the dragon profile's main claim appears in the lects and the ˯ audio effect is used. | M (fantasy) | M | S | Before merge |
| 7 | **Phonotactics that stay alive.** After each sound change, re-derive the realised template (max onset and coda, coda class, onset requirement) for the output and the sketch. Add per-segment positional limits (initial ŋ by WALS 9A, clicks mostly root-initial, h and ʔ by position) to `legal` and `draw_word`. Optionally let `repair` push back on violating outputs: a "conspiracy" that makes CV lects stay CV. | H | M | M | First after merge |
| 8 | **Synchronic vowel harmony.** When `harmony.back` (or a new rounding or ATR harmony) fires, set an inventory property such as `harmony = {"axis": "back", "neutral": [i, e]}`. Then `draw_word`, `repair`, compounds, loans and gram attachment (`sentences.join`, `grammar._attach`) obey it, with affix allomorphs chosen by the stem. Unblock S132–S134 as allomorph rules. Add an ATR axis to the percept space. | H | M | M | First after merge |
| 9 | **Richer, stress-aware allophony.** New tests: aspiration in stressed onsets, flapping, affrication before high vowels, vowel reduction in unstressed syllables, high-vowel devoicing, emphasis backing, l-darkening by position. Show phonemic /…/ and phonetic […] side by side in the sketch, and speak the phonetic form. | M | H | M | Later |
| 10 | **Length and gemination as contrasts.** Find why geminates vanish (18% → 1%): degemination rules with no source, and `_initial_geminate` repairs. Treat a CC of one consonant as a geminate in the phoneme table and the spelling. Pair long vowels across the system (part of #2). | M | M | S–M | Later |
| 11 | **Boundary morphophonology.** Voicing assimilation and epenthesis at affix boundaries (English -s/-ɪz), vowel elision with tone stability (Yoruba), consonant gradation, compound voicing (rendaku), and coronal assimilation of clitics. Put them as rules in `sentences.join` and the paradigm builder, drawn per lect from a small table. | M | M | M | Later |
| 12 | **Larger clusters.** For "complex" lects, allow onsets and codas of 3–4 with s + stop + liquid, Georgian-type stop + stop (harmonic) onsets as an areal option, and syllabic sonorants as nuclei. Raise `MAX_ONSET`/`MAX_CODA` per lect rather than globally. | M | M | M | Later |
| 13 | **Re-disperse vowels after change.** A dispersion steer in sound change (dispreferring outputs that crowd an existing quality), and a drift toward the commonest 5-vowel system. Fixes 35% of lects being under the floor and the WALS 2A skew. | M | M | S–M | Later |
| 14 | **Syllable weight, moras and pitch accent.** A weight function (CVV, CVC heavy by lect), weight-sensitive stress (Arabic, Latin), and a "pitch accent" prosody value: one accented mora per word or none. Japanese and Swedish-type word tones become possible. | M | H | L | Later |
| 15 | **Clicks done properly.** Root-initial placement, more accompaniments (uvular contours, delayed aspiration), vowel phonation and pharyngealised vowels, a root canon. | L–M | L | S–M | Later |
| 16 | **Accent after language shift.** On a shift, run the shifting people's `hear_word` over the lexicon as a substrate pass, so lects nativise to their new speakers' voice. This is a judgement call: should a fire giant lect keep the dragons' lipless sounds? It goes to Daniel. | M | M | S | Later (needs decision) |
| 17 | **Root-and-pattern morphology.** Consonantal roots with vowel templates, as a grammar and lexicon type. This is shared with grammar Phase C item 15. | M | L | L | Later |
| 18 | **Audio fidelity.** Per-lect voice choice (eSpeak's tables for languages with uvulars, pharyngeals and retroflexes, e.g. 'ar', 'hi', 'fi'; Piper only for English-like lects); pass syllable boundaries and stress; downdrift tied to the tone system. | L | H | M | Later |

**Before the first merge**, items 1, 3a, 4, 5 and 6 are all S. They remove a silent data bug (1), the most visible
calibration error in tone (3a), a property the pages state but never show or play (4), the oddest small inventories (5),
and the main unrealised claim of the dragon profile (6). Item 2 is the largest single gain in realism. It is M, but it
replaces mechanism rather than adding it, so it could go in before the merge if a lane is free.

---

## 7. Caveats

- Run a24559 is from 11-04. Round 5 changed ɹ, ʁ, ɫ, ɦ and ʐ shares (calibration.md). The other rows should be unchanged,
  but no newer run exists to confirm it.
- WALS and UPSID figures are from memory and rounded (1A, 2A, 4A, 6A, 7A, 8A, 9A, 10A, 11A, 12A, 13A, 14A, 19A). Check
  them before quoting.
- The PHOIBLE comparisons use segment strings. Coding differences (t̠ʃ vs tʃ, n̪ vs n, the dental "either-or" rows) blur
  a few rows, which is why I avoided absolute "missing p t k m n" claims.
- The realised WALS 12A classes use my own classifier over the lexicon:
  - simple: under 2% of words have initial clusters, under 5% end in a consonant, and no medial run is longer than 1;
  - complex: over 1% of words have 3-C onsets, over 3% have 2-C codas, or over 5% of medial runs are 3 or more;
  - moderate: everything else.
- The harmony index is the adjacent-vowel front/back agreement against independence, over non-central vowels of mid
  height or higher. It is a coarse measure.
- I filed no inbox drafts, because the brief was read-only. The 18 items above are written so the coordinator can turn
  them into drafts.
