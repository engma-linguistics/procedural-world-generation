# Languages from scratch: the overnight demo (lane report, 2026-11-04)

Branch `lang-design`, worktree `.claude/worktrees/lang-design`. Run **a24559** (dnd preset, world dba204). Everything below is
committed on the branch; nothing is merged. The viewer is `viewer/languages.html` (a "Languages" link sits in the peoples
workbench header). Start the server from the worktree (`uv run python -m planet serve`, or on another port if yours is
up) and pick a24559.

## Rule on these first

1. **The horizon measure.** An automatic comparative method on the output goes blind at **9.0 kyr** for human lects (9.6 for
   all), inside the 6-10 target, under a split-based measure with a strict cognate test (aligned distance plus recurring
   correspondences; a clade in the scholars' tree matching the true split at Jaccard >= 0.8). The first, per-pair measure
   read 11-13 kyr. Three choices inside the measure are judgement (the clade tolerance, the chance excess, and whether the
   "sisters recognisable" bar of 0.5 should apply to the strict share, which is 0.46, or the loose one, 0.54). Draft:
   `issue-tracking/inbox/draft-language-rates-and-horizon.md` (needs-decision). Details in §6 and `calibration.md`.
2. **Per-generation scaling at exponent 1** (your ruling) does what it says: aarakocra (5.8-year generations) change
   about five times faster per year than humans, kobolds (11.7) twice; aarakocra sister lects 5 kyr apart share almost no
   core roots, and their own horizon is 2-3 kyr. Elves (145-year generations) look like ~3 kyr of human change over 20 kyr;
   dragons (430) keep 85-88% of their proto core words. Keep it, or soften it (0.7) for the very-short-generation peoples?
   Numbers in §7.
3. **Voice profiles.** `docs/review/language/voice-profiles.md` holds the drafted numbers and the sources per species. Three
   choices you may want to overturn: humans can make harsh (growled) voice at a high cost (contrastive in !Xóõ and Bai)
   rather than never; birds keep a larynx (a valve, no phonation) and voice with the syrinx, so voicing rules apply to them;
   tortles hear front vowels poorly. Dragons' sub-bass register is dropped by every human-eared listener, as designed.
4. **Rivers are named by the people with the most heads on them** (square-root weighted), so dragons name a river now and
   then rather than most of them (they covered most cells at 20 kyr). Your call if you want more draconic hydronyms.
5. **Romanization for the book** is a lossy "book mode" (tones dropped, nasal vowels as plain vowel + n, one diacritic per
   word, ü/ö only where a lect contrasts them); the workbench shows the full spelling beside it. Uvulars: q, qh, ġ (ʁ, DIN
   31635), gq, nq. Endonyms came out like *Mïzhekheema* 'the real people' (humans), *Ïthe'ee* 'the river people' (kobolds).

## What works and what doesn't

**Works.** Every layer of the slice is real and runs end to end on a24559 in 15 minutes: 321 proto-languages, 1,249 lects
(633 living), 600 languages, 214 shifts, 98 food routes, all six checks pass (horizon 9.0 kyr for human lects), and two runs
of the same seed give the same file. Sound change looks like sound change: regular correspondences you can state between
sisters (d604 ɜ = d856 ə; *p, *ɡ > ʔ word-initially; voiced stops > breathy; finals lost; *a > ɨ), distant lects distant, a
shift case that reads like a textbook one (dragonborn under human rule: shares 0.23 then 0.53, 65 substrate words, an accent
m > v, n > ɹ, ɲ > ʒ because the old lect had no labials or nasals, a minority still speaking the old tongue), grammar with
attested paths (LOC < 'belly', PROG < 'at', 3PL < 'they', a negator worn ʃ > h > ʔ) and real alternations (a 3PL suffix that
lengthens the stem vowel), names through the grammar with patterns and relay mangling, food words with routes, and a viewer
that shows all of it with audio.

**Doesn't, yet.** (1) The lexicon is the weak layer: derivation meanings are often absurd (EAT + 'thing' = 'tree'), one 'thing'
prefix starts 12% of the words of the main human family and makes unrelated words look cognate, and etymology loops happen
(man > person > child > small in 2 kyr). (2) Tone is everywhere: 98% of living lects are tonal against 24% of protos, and ɨ
fills three of the four commonest vowel slots; living inventories grow past real languages (half end above PHOIBLE's upper
quartile; 513 of 633 lects spell two segments alike). (3) Half the shifts are re-shifts inside one family on the cooldown
clock. (4) Food-route hop tables and the receivers' own etymologies disagree in 28% of hops. (5) The per-generation ruling makes
aarakocra keep nothing of their proto core words. A final tidy-up round on (2), (3) and the derivation rules was running as
this report was written; §8 says what state it reached.

## 1. What was built (PW-1423 and PW-986, and most of PW-982)

`planet/language/` (14 modules, ~12k lines, 500+ tests, all not-slow):

| Layer | Module | What it does |
| --- | --- | --- |
| Sounds as heard | `percepts.py`, `data/symbols.tsv` | one percept space for every species (place, manner, voicing, larynx, phonation incl. harsh and purr, secondary, vowel height/back/round/nasal, length, tone, second source, register); 274 symbols: IPA, extIPA, VoQS and a few house symbols; injective rendering |
| Voice profiles (PW-1423) | `profiles.py`, `data/voice_profiles.toml`, `spec.py::voice` | make cost per percept class, hear resolution per axis, articulators, modality; inherited key by key along the lineage tree like `body`; human default from PHOIBLE frequencies; nativization = hear a word through a profile and an inventory |
| Inventories | `inventory.py` | PHOIBLE-weighted draws with feature economy and vowel dispersion, scaled by the species' make costs; sonority-sequenced syllable shapes; repair |
| Sound change | `rules.py`, `data/sound_changes.tsv` | 28 hand-written demo rules plus 150 parsed from the catalogue, each with its cause (coarticulation, effort, perception, prosody, tonogenesis, dispersion) and needs (articulators or hear axes); a species keeps the rules it can cause; Wedel-style functional-load veto; regular vs diffusing |
| Words | `lexicon.py`, `data/concepts.tsv`, `data/clics_edges.tsv` | ~330 concepts (Leipzig-Jakarta, Swadesh, food from the run's crops and animals, landscape, kin, numbers, god domains); frequency-dependent replacement (Pagel 2007 shape, 86%/kyr Swadesh retention at human generations); derivation, compounding along CLICS edges, colexification shifts, borrowing, taboo, substrate; every word carries its etymology |
| Grammar | `grammar.py`, `data/grambank_*.tsv`, `data/wals_wordorder.tsv`, `data/grammaticalization_paths.tsv` | 39 typology features drawn with their correlations and drifting at stability-class rates; grams recruited along Heine-Kuteva paths and moving free > clitic > affix > fused > lost; sound change runs on inflected exemplar cells so alternations arise; analogy levels; complexity measured, never stored; L2 share, population and isolation push the rates |
| The driver | `history.py`, `lect.py`, `inputs.py` | one lect per deme; proto-languages per connected component of same-people demes in contact at 20 kyr; budding copies; wave spread of fired rules over the contact record weighted by contact and prestige; language shift on elite rule, swamping, city mixing and trade, with substrate words, an accent and calqued features; food words borrowed hop by hop along the crop and animal spread; city koine; batched per 0.5-kyr frame, never per generation |
| Families | `families.py`, `checks.py` | true lect tree with shift edges; blind cognate shares; language clustering; the scholars' UPGMA tree and the horizon; the six checks |
| Names (PW-972) | `names.py` | endonym patterns E1-E12 and exonyms X1-X9 from the owner's taxonomy, built through each lect's grammar (class markers, compound order, locatives); relayed exonyms mangled hop by hop; hydronyms kept as substrate across shifts; the Common and its exonyms; scholars' names for dead families |
| Output | `output.py`, `run.py` | `runs/<id>/languages.json`; `planet languages RUN [--out] [--workers]`; a guarded hook in `output.save`; a placeholder export for the writing repo |
| Romanization | `romanize.py`, `data/romanization.tsv` | the house spelling (full and book modes) |
| Audio | `speak.py`, `data/ipa_to_speech.tsv`, `/api/speak`, `planet speak` | IPA to WAV: eSpeak NG baseline, Piper fed raw IPA; growl, purr, second voice, sub-bass and ultra registers and percussives as numpy effects; the voice profile sets pitch and pace. Samples in `docs/review/language/audio/`; research in `audio.md` |
| Viewer | `viewer/languages.html`, `viewer/lang*.js` | six tabs, below |
| Brief | `brief.py` | a "Names and words" section per people (headword, glossonym, exonyms, three etymologies, food words with routes) |

Reference data (`planet/language/data/`, sources and licences in `reference-data.md`): PHOIBLE 2.0+ (CC-BY-SA), Grambank 1.0.3,
WALS, CLICS3, Concepticon lists (Leipzig-Jakarta, Swadesh, Pagel 2007 rates, Holman). The sound-change and grammaticalization
tables are written from knowledge, not downloaded, and say so in their headers.

## 2. The viewer

Screenshots in `docs/review/language/screens/`.

- **Families**: the true lect tree on a 20-kyr axis (bud solid, shift dashed, arrival dotted, coloured by people) beside the
  scholars' tree, with the 6-10 kyr band and the measured horizon. `lang-families.png`
- **A language over time**: pick a lect, scrub 20 kyr: the consonant grid and vowel trapezoid animate (sounds that came flash
  green, sounds that went are struck out), the core words change in IPA and spelling, the grams sit on their ladder, the
  typology line, complexity over time, the change log with causes. Play buttons on words. `lang-time.png`, `lang-time-now.png`
- **Continuum and intelligibility**: a map of living lects with contact edges coloured by intelligibility at the scrubbed
  frame (green > 0.7, amber, red < 0.4), chain cards ("the middle understands both neighbours, the two ends do not"), when
  a chain broke, and a who-understands-whom heatmap. `lang-continuum.png`, `lang-continuum-chain.png`
- **Names and etymologies**: endonym, glossonym, the land/people/person/language set, exonyms by whom and why, each with its
  etymology chain; deme place and river names; what the Common calls them; scholars' names. `lang-names.png`
- **Food words and shifts**: each route hop by hop with the form at each hop; each shift case with trigger, substrate and
  accent. `lang-routes.png`, `lang-shifts.png`
- **Checks and voices**: the checks table and a voice card per species. `lang-checks.png`

Load is ~2 s for the 140 MB file; every tab draws under 0.2 s; scrubbing is 5-15 ms a frame.

## 3. Sample proto-inventories next to PHOIBLE

**PHOIBLE reference** (`phoible_inventory_sizes.tsv`, 2,175 inventories): consonants median 21 (IQR 17-27), vowels median 9
(IQR 6-12), tones median 0 (IQR 0-0).

| proto | speakers | C | consonants | V | vowels | tones, syllables |
| --- | --- | --- | --- | --- | --- | --- |
| p306 | human | 26 | p b ɓ f v m t d tʰ ts dz s z ʃ tʃ n r l ȶ ʈ j k ɡ ŋ w h | 10 | i e ɛ a ɔ o u ɨ aː ɔː | 5 tones; up to CCVC; stress penult |
| p255 | kobold | 21 | β tʰ d ts s n l ɻ tʃ dʒ j k kʰ ɡ x ɣ ŋ χ ʔ h hʲ | 10 | i iː e̞ ẽ̞ ə a aː ɑ o̞ u | no tone; up to CCVC |
| p222 | aarakocra | 24 | m b t d s z r r‼ l tɬ ɮ ȶ ʈ ɖ tʃ ɟʝ j k kʰ ɡ w ʔ h ʕ | 6 | i iːᴖ ɪ ɛ o u | 5 tones; up to CCVCC; stress final |

All three sit inside PHOIBLE's consonant IQR; the human and kobold vowel counts are at the upper end, the aarakocra one at the
lower. **Avian labials are scarce, as ruled:** p222 has only m and b (p306 has six: p b ɓ f v m); over all protos the median is
6 labials for humans, 3 for aarakocra, 2 for kobolds and dragons. **Second-source and harsh segments are there:** p222 has a
second-voice vowel (iːᴖ) and a harsh trill (r‼); 52% of aarakocra protos carry a ᴖ segment and 57% a harsh one. They fade:
among living aarakocra lects only 23% still have ᴖ and 35% a harsh segment (kobolds fall from 72% to 45% harsh; dragons stay at
99%). Humans and elves have none, as they should.

**Living inventories by species group** (quartiles q1 / median / q3):

| group | living lects | consonants | vowels | tones |
| --- | --- | --- | --- | --- |
| human | 105 | 24 / 28 / 35 | 11 / 13 / 15 | 4 / 4 / 5 |
| dragons (10 kinds) | 118 | 22 / 27 / 33 | 7 / 11 / 15 | 2 / 3 / 4 |
| elves (elf, drow, sea elf) | 27 | 15 / 24 / 34.5 | 8 / 9 / 10.5 | 3.5 / 4 / 4 |
| kobolds | 53 | 25 / 29 / 31 | 8 / 11 / 15 | 4 / 4 / 4 |
| aarakocra | 26 | 22 / 27 / 33 | 7 / 9.5 / 13 | 4 / 4 / 5 |

Protos start inside PHOIBLE's range (the check's 110 human-voiced protos: median 23 C, 8 V). After 20 kyr they have grown: **half
of all living lects are above PHOIBLE's upper quartile for consonants (51% over 27) and nearly half for vowels (46% over 12)**,
and 98% of living lects are tonal against 24% of protos (about 40% of the world's languages are tonal).

## 4. Cognates, etymologies, a food word's route, a shift, paradigms

**(a) Human family p306** (proto 20 kyr; 42 living lects, many of them spoken by halflings, orcs and aarakocra after shifts). Five
human lects of the d604 branch and one of the d561 branch. Split dates: d604-d856 1.5 kyr; d604-d702 12; d604-d691 13; d604-d666
15; d774 against all the others 19.

| concept | proto p306 | d604 | d856 | d666 | d691 | d702 | d774 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| WATER | pjo˨˦dzku˨ | ʔə˦h ‹'ë́h› L | ʔə̃˦h ‹'ë̃́h› L | ʔje˦i˧ʒ ‹'yéiž› L | ʔɨ˦a˨ ‹'ḯà› = | mo̞˧ɨ˨i˨ ‹moï̀ì› =+d | ɨ˨ɹa˨˦ɨː˨˦hɛ˨ =+d |
| FIRE | tja˦˨brɔ˧r | lɨː˨˦lɜ˨ɱa˨i˨ =+d~ | ə̃˦ʃɨ˨ə˨ʔ =+d~ | tʰĩ˦li˨ ‹thĩ́lì› N | lɨː˨˦ɹɔ˦ N+d | a˦˨ ‹â› N | ɛ˦ɲɨ˧ɨ˧ L~ |
| HAND | ȶɨ˧ | ŋu˧ ‹ngu› N | ŋo˧ ‹ngo› N | ȶɨ˦ ‹ťḯ› = | ȶɨ˧ ‹ťï› = | lɨː˨˦le˨i˦˨ N+d~ | ȶɨ˦ ‹ťḯ› = |
| EYE | daː˦˨p | dʱi˨˦ ‹dǐ› = | dʱĩ˨ʔ ‹dĩ̀'› = | mɛ˨lɨ˦ɨ˨v =~ | ʈɨ˦ɜ˨ɪ˨ N+d | lɨ˨˦li˨iː˦˨ʒe˧ =+d | lɨː˨˦nɨ˦˨ N+d |
| ONE | ŋa˧ | ʂɨ˦ɜ˦v ‹ṣḯë́v› N+d | ʂɨ˦ə˦f ‹ṣḯë́f› N+d | lɨ˨˦ɫi˨a˨ N+d | ŋɨ˨ ‹ngï̀› = | lɨ˨˦i˧ɨ˨ N+d | ɲɨ˨ ‹nyï̀› = |
| TWO | e˨ȶa˨ | lɨ˨˦ɫlɛː˨˦ N+d | laː˧ʔ ‹laa'› N+d~ | ɲi˨˦v ‹nyǐv› N | lɨː˨˦lɨ˨ =+d | lɨː˨˦lɨ̃˨ =+d | tʰɹa˨˦a˨˦u˨˦va˨ N |
| STONE | mo˨˦mɔː˨tʃ | lɨː˨˦mi˧ə˦ =+d~ | lɨː˨˦my˧ə̃˦ =+d~ | lɪ˦ʁĩ˦ N | tʰɛ˦ ‹tẹ́› L | hɨː˧la˧ɨ˦a˨ N+d | ŋu˦nna˨˦ N |
| TREE | mi˦so˦˨vʃa˧d | lɨː˨˦ləː˨ʔːi˨˦ =+d~ | lɨː˨˦lə˨ʔĩ˦ʔ =+d~ | lɨ˨˦ɫʼje˨ʈɨ˦ N+d~ | lɨ˨˦fɡla˨ɡaː˦ N+d | lɨː˧ʂaː˧ N+d | mɨ˦ɦɨː˨mɨ˨˦ =+d |
| NIGHT | ze˦˨m | lɨː˨˦ʈɜ˦dʱ =+d | lɨː˨˦ʈə˦dʱ =+d | ɨ˦ʔɨ˦ɨ˨v =+d | lɨː˨˦lɨ˨ʈ =+d | lɨ˨˦ɛ˦ɨ˨ N+d~ | lɨ˨ɹʒɨ˨˦ɨ˨˦ N+d |
| DOG | kɛ˦ru˨˦ | kxaː˦ʔi˨˦ L+d | kxaː˦ʔĩ˦ʔ L+d | ɲɨ˦˨f ‹nyï̂f› N | bʱɨː˨ɖɨː˦bʱɨ˨ =+d | ŋi˧ɨ˨ N+d | ɨ˧la˧mɨ˧ɛ˦ L+d |
| FISH | su˨˦me˨˦w | lɨ˨˦v ‹lï̌v› =+d | lɨ˨˦v ‹lï̌v› =+d | ʔɨ˦ ‹'ḯ› L | lɨ˨˦fma˨v N+d | mi˨˦i˨ ‹mǐì› = | ɨ̃˦ɫɨ˨ɨː˦hɨ˨ N+d |
| I | ŋa˨˦ɡ | lɨ˨˦ɫʃo˧laː˧ L+d | ɲ̟ĩ˦ʔ ‹ɲ̟ĩ́'› = | ɨ˦f ‹ḯf› =~ | kxhi˦ ‹kxhí› L | ɲ̟e˦ ‹ɲ̟é› = | lɨ˨˦ɨː˦ɹɨ˨ =+d |
| THOU | sɨ˧vɔ˦p | lɨ˨˦ɫdʱɜ˨ɨ˨ =+d | ĩ˦l ‹ĩ́l› L | ʔɨ˦f ‹'ḯf› = | lɨː˨˦dʱɨ˨ɨ˨ =+d | ɲi˨˦ ‹nyǐ› =~ | ŋu˨ɲ̟a˨˦u˨˦ŋɛ˦˨ N |
| WE | tʃɔ˦ | i˦ɫ ‹íll› L | ĩ˦ɫ ‹ĩ́ll› L | ʂi˨ɫi˨tʰ N | ɲi˨˦ ‹nyǐ› =~ | lɨ˨˦li˨ɛ˨ N+d | lɨ˨˦ɨː˦ɹɨ˨ =+d~ |
| EAT | be˧bwo˧ | ʃo˧laː˧dʱe˧ L | ʔɨ̃˦tʰɨ˦ə˦x =+d | ɓa˨ŋɨ˧ɨ˦ɨ̃˦ L | mɛ˨˦ɛ˨ʔɨ˦ N+d~ | ʁe˨˦ ‹ġě› N | ɨː˦mɨ˦˨ N+d |

Correspondences that can be stated. **d604 : d856** (1.5 kyr, 73 of 100 core roots shared): d604 ɜ = d856 ə (14 tokens: BREAST,
DIE, EAR, HEAD, DRINK, NIGHT ...); d604 v = d856 x or f (10: DIE, DRINK, EAR, MAN; HEAD, HEART, KILL); d604 ʒ = d856 ʃ and d604 ɦ
= d856 h (d856 devoices fricatives); d604 oral i, ə = d856 nasal ĩ, ə̃ / ɨ̃ (19 tokens); d604 word-final high-toned vowel = d856
vowel + ʔ (DOG kxaːʔi˨˦ : kxaːʔĩʔ, EYE, SEED, TREE). **From the proto:** *p and *ɡ > ʔ word-initially (WATER *pj- > ʔ in four
lects; I *ŋaɡ > ɲ̟ĩʔ); voiced stops become breathy (EYE *d > dʱ); final consonants go (*-p, *-d, *-m, *-r); *a > ɨ (ONE *ŋa > ŋɨ,
ɲɨ); *ȶ is the most stable consonant (HAND *ȶɨ unchanged in three lects after 13-19 kyr). Deeper pairs share little: d666 : d691
(13 kyr) 11 roots. **What a linguist would stop on:** a prefix lɨ˨˦- (the 'thing' derivation) has eaten the vocabulary: 12% of
all words in this family start with it, so TREE, NIGHT, STONE, FISH, TWO and THOU look alike across the family for a reason that
is not inheritance; d774 has one word for I and WE.

**(b) Dragonborn family p120** (proto 20 kyr; d148, d280, d308, d544 are first-generation daughters, d771 budded from d148 at 7.0
kyr). Kobolds would have made a weaker table: the largest kobold family (p255, 16 living lects) keeps a median 1% of its proto
core words, and 28% of living kobold lects keep none.

| concept | proto p120 | d148 | d771 | d280 | d308 | d544 |
| --- | --- | --- | --- | --- | --- | --- |
| WATER | ti | ʂi˨t.si˦˨ ‹ṣìtsî› N | i˦ɛ˨i˨ N+d | ʔɘ˦ca˨a˦i˦ɘ˦ N+d | ʔje˦ɛ˦ ‹'yéẹ́› N | ʒi˨ə˨ L+d |
| FIRE | tat | ɹa˦i˦ɛ˨i˨ɾ =+d | ɹi˦wa˨ɛ˨ɪ˦ɾ =+d | ʔɘ˦ɨ˨ɘ˦˨ =+d~ | tje˦ɛ˦ ‹tyéẹ́› = | ʃi˦ ‹shí› N |
| HAND | li‼ | ʔi˦ɛ˨ ‹'íẹ̀› =+d | le̞˦ɛ˦ɪ˦ʔ =+d | ʔɨ˦cʼɘ˦lɘ˨ =+d | tĩ˦i˦ħ N | hɨ˦ ‹hḯ› L |
| EYE | ruʔ | i˦ɛ˨˦ L+d | ʔe̞˨ʒɪ˨e̞˨ =+d | ʔi˦ʔɜ˦dʱ =+d~ | ɫje˦ʃɛ˨c =+d | ʔə˦ʒɨ˨ə˨ =+d |
| ONE | titi‼t | ha˦ɛ˦i˨˦ ‹háẹ́ǐ› = | ta˦a˦ɛ˦ɪ˦ʔ = | ʔɨ˦ ‹'ḯ› = | ɫje˨ɛ˦ʃ N+d | hɜ˦ ‹hë́› N |
| TWO | kĩkas | li˦ ‹lí› N | li˦ ‹lí› N | ʔɨ˦ca˨i˨i˦ N+d~ | ʔi˨je˦ɛ˨c N+d | ɨ˦ ‹ḯ› =+d |
| STONE | ki‼ta | ɛ˨i˨ɹ ‹ẹ̀ìr› =+d | le̞˦i˨ɛ˨ɪ˦ N+d | ʔɘ˦cɘ˨ɜ˦i˦ N+d | ʔɛ˦je˨ctɛ˦ N+d | ʔɨ˦əː˦ʃɨ˨ L+d |
| TREE | restse‼ | i˦dʱe˦˨qʰi˨˦ʈ N+d | ti˨txiː˨ɹ N~ | ʔɜ˦ɹɨ˨ʔi˦ɾ =+d | ɹiː˨χĩ˨ʃi˨ɛ˨ L+d~ | hɨ˦ʈʒi˦ =+d |
| NIGHT | χarhalk | qʰi˦ ‹qí› N~ | i˦e̞˨ N+d | ʔɜ˦i˦ɘ˦˨ =+d | ʔje˦ɫ ‹'yéll› =~ | ʔi˨ʒɨ˨ə˨ N+d |
| DOG | rik | ɛ˦i˦qʰ ‹ẹ́íq› N | ɪ˦qʰ ‹ị́qh› N | hħa˦i˨ɦɘ˦ʕɨ˨ɘ˨ʈ N+d | ʔɛ˦ɛ˨iː˨ʔɛ˦ N+d | hɨ˦ʒə˨i˨ =+d |
| FISH | kerk | ʔɛ˦i˦ʔa˦i˦ L+d | e̞˦i˨˦ ‹éǐ› =+d | ʔɨ˦ca˦ L+d | ʔi˦ ‹'í› = | ʔi˦ʒɨ˨ə˨ N+d |
| I | ʈik | i˦ʈi˨ ‹íṭì› =+d~ | ʈi˦dʱa˨a˦ɛ˦ɪ˦ɹ =~ | ʈi˦c ‹ṭíky› =~ | ʈje˦ ‹ṭyé› = | ʔʒi˦ə˨ =+d |
| THOU | ʃau | i˦ʔi˦ɾ L+d | ʈi˨i˨ =+d~ | ʔi˦ɘ˦˨ ‹'íë̂› = | ɫje˨ʂti˨˦ N | ɗɨ˨ ‹'dï̀› N |
| WE | ɖeːcrak | ʈi˦dʱa˨ɛ˦i˦ɹ = | ɹa˦ɛ˦ɪ˦ɹ =~ | ʈi˦c ‹ṭíky› = | ʔɛ˦ɛː˨ʔɛ˦ʃ L+d | ti˨˦ɹ ‹tǐr› N |
| EAT | χeː | ʔi˦ɾ ‹'ír› L | i‼˨i˦ ‹ìrhí› L+d | dʱɘ˨i˦˨ L | ʈɨ˦ =+d | ʈʒi˦ =+d |

Correspondences: proto final stops are lost everywhere (*-t, *-k: ONE, I, DOG); the harsh vowel *i‼ becomes a plain mid vowel
(ɛ, e̞, ɪ: HAND, ONE, STONE); *ʈ is kept in every lect (I: ʈi, ʈi˦c, ʈje); *t- gives h in d148 (ONE ha-), ʔ in d280, t in d771 and
d308; d308 breaks *i after coronals into je (ʈje, tje, ɫje); *k > c in d280 (I ʈic). d148 : d771 (7 kyr) share 18 roots, with
shared new coinages TWO li˦ (d148, 14.0 kyr) and DOG qʰiː (10.5 kyr); d280 : d308 (20 kyr) share 9. **Winces:** the descendants
of a harsh, consonant-heavy proto have become vowel strings (FIRE ɹa˦i˦ɛ˨i˨ɾ, ONE ta˦a˦ɛ˦ɪ˦ʔ, DOG ʔɛ˦ɛ˨iː˨ʔɛ˦); d280 has one
word ʈi˦c for both I and WE.

**(c) Four etymologies.**

1. **SMALL in d636.1 (halfling), 15 steps, two loans.** 20 kyr blue-dragon proto p19 *kucɾɔʎzi* 'husband' > 12.0 d39 *tʃiː˦ɾɑ˦zi˨*
   > 11.0 **borrowed by humans** (d561) *ʃeːɾadze* 'husband' > 10.0 *hiɾadzi* > 9.5 HUSBAND + 'thing' = *lɨ˨˦hiɾa* 'man' > 6.5
   MAN + CHILD = 'male person', then MALE PERSON + FATHER = *lɨ˨˦ɦa˦ʈe˧ʂ* 'man' > 5.5 MAN + PEOPLE = *lɛ˨˦hɛː˨mɛ˧dʱɪ˨* 'person' >
   5.0 into orcish d652.3 by shift *lɛ˨˦ɦmɛ˧dʱː* > 4.5 PERSON + MAN = 'child' > 4.0 CHILD + 'like' = *lɛ˨˦ɦmɛ˧ʔɪ˨* 'small' > 3.0
   *lɛː˨˦mɛ˧* > 1.0 **borrowed by halflings** (d636.1 from d841) > now *lɛ˧mɛ˧* ‹lẹmẹ›. 'Child-like' for 'small' is good; the
   man > male person > man > person > child loop in 2 kyr is not.
2. **Rice, by food route** (route `crop:rice`, "tamed here" at d710, human, 9.5 kyr, *ɨ˨xɜ˦ɨ˨*; 54 hops). The chain to the triton
   lect d767: 9.0 hill giant d26 *ɨ˨ɣɜ˨ɨ˨* (lenition: x > ɣ between vowels) > 7.5 copper dragon d71 *ʔɛ˨ɛ˨ɛ˨* > 5.5 orc d677
   *ʔɛ˧ɛ˧ɛ˧* (tones levelled) > 2.0 human d604 *ʔĩ˧ɨ̃˧* > 0.5 tortle d206 *ʔɨ˨ɜ˨* (nasality lost, ɨ̃ pushed to ɜ) > 0.0 triton
   d767 *ʔɨ˨ɜ˨* ‹'ï̀ë̀›. But the triton word's own etymology says something else: orcish d677 made it at 3.0 kyr as WATER +
   'little' (*ʔĩ˦ɨ̃˦ʔɨ̃˦*, from a brass-dragon word for water borrowed at 9.5 kyr) and that word travelled d677 > d604 > d206 > d767.
   The hop table splices two different words; in 28% of all hops the receiver's word shows no borrowing at all.
3. **A substrate survivor: 'horses' in d148.1** (deme 148, dragonborn now speaking a human language; see (d)). 20 kyr proto p120
   *sret.ʃsukqʰi‼k* > by 3.5 kyr in dragonborn d148, after 39 sound changes, *ʔa˦i˦i˨a˨i˨* > 2.0 kept through the shift as substrate
   *ʔa˨i˨i˨a˨i˨* (high tones heard as low: accent) > 1.5 *ʔa˦i˨i˨a˨i˨*. 'Cattle' in the same lect is a substrate word reused:
   d148 *e̞˦i˦ʔa˦i˦ɾ* 'animal' (BIRD + OLD) > substrate *e̞˨i˨ʔa˨i˨ɾ* > 1.5 ANIMAL + GREEN = *vi˨˦ʒʔa˨i˨ɾ* 'cattle'.
4. **A compound: SMITHING in d806 (human).** 5.5 kyr d562 coins *me˦nɲi˦ɲh* 'fire' > 3.0 d806 *mɜ˦ɜ˦ɲɜ˦˨ɜ˦* > 1.0 FIRE + STRIKE,
   both clipped, *mɨː˦ʔɜ˦mɜ˦ɜ˦* 'smithing' > now *mɨ˦ʔə˦mɜ˦ɜ˦* ‹mḯ'ë́më́ë́›. Also good: DAY = SUN + SKY in d570.1 from an elvish
   'sun'; SPIRIT = GOD + BREATHE in d605 (though d605 cycles spirit > god > spirit > god > spirit five times in 18 kyr).

**(d) One shift in full: deme 148 (dragonborn 4, the west of Trojanel) to human, 2.0 kyr ago.**
- **Trigger:** humans of deme 791 took 76 dragonborn sites, a town or city among them, about 2.2 kyr ago (`takeover`, strength
  1.0, held to now; source settlements.json holders). The dragonborn stayed under human rule.
- **Shares of the rulers' lect d791 among the dragonborn:** 2.5 kyr 0.23, **2.0 kyr 0.53: shift** (another human lect, d584, 0.05).
  After the shift the old dragonborn lect keeps 0.38 (1.5 kyr), 0.31, 0.25, **0.21 now**, and d584 rises to 0.14.
- **The old lect lives on:** d148 is alive, flagged `minority`.
- **Old d148 (dragonborn):** 24 C `ʔ tʃ h ɹ ʈ ɾ l ʒ kʼ dʱ x qʰ ɫ kx ʃ ʁ ʂ c t ɦ k s ɖʱ χ`, 8 V `i i‼ ɛ e̞ e‼ a ɘ̠ e`: no labials,
  no nasals. **New d148.1:** 26 C with f pf pʷ v bv ɱ ŋ ŋʷ ɲ̟, 16 V; the rulers' d791 has 28 and 14.
- **Core words, old / new / rulers' now:** WATER ʂi˨t.si˦˨ / hi˨xi˨x / pfə˨pfə˨ɲɨ˦ʃə˨ʃ; FIRE ɹa˦i˦ɛ˨i˨ɾ / ŋi˦fi˨ʒx / ŋɨ˦pfŋi˦ɣfə˨dʱ;
  HAND ʔi˦ɛ˨ / hɨ˦ / pfɨ˦; ONE ha˦ɛ˦i˨˦ / kxi˦ / ŋɛ˦pfi˨vʃe˨; I i˦ʈi˨ / kxɨ˦ / kxɨ˦; EAT ʔi˦ɾ / ʔi˦x / ʔy˦ʃ; NIGHT qʰi˦ / ʉ˦ / ʉ˦. The
  new lect took the rulers' words of 2.0 kyr ago (WATER was *ɲɨːʒəːʒ* then) and both have moved since; I, NIGHT still match.
- **Substrate kept:** 65 concepts: landscape (HILL, MOUNTAIN, RIVER, SEA, FORD, PASS, COAST, MARSH ...), wild and farm animals
  (DEER, WOLF, BEAR, horses, cattle, goats, fowl), FISH, BIRD, DOG, LOUSE, TREE, STONE, and three crops.
- **Accent (old sound for new):** m > v, n > ɹ, nʼ > ɹ, ɲ > ʒ, pf > f, ʍ > k, d > dʱ, ð > s, ø > e, y > i, ɨ > i, ə > e, u > ɘ̠.
  Sensible for speakers with no labials and no nasals: those heard as the nearest sound they have.
- **Calques from dragonborn:** no copula (rulers have one); polar question particle moved to the start.

**(e) Two paradigms from living lects** (`paradigms` per lect: nouns and verbs with cells, segmentation, irregular cells; history
from the snapshots' `grams`).

*d691 (human 49, family p306, VSO, ergative, no case).* Nouns: WATER ʔɨ˦a˨, LOC **la˨˦**-ʔɨ˦a˨; PERSON ɔ˨, LOC la˨˦-ɔ˨, CLASS:3
**u˦**-ɔ˨; TREE lɨ˨˦fɡla˨ɡaː˦, LOC la˨˦-lɨ˨˦fɡla˨ɡaː˦.

| verb | lemma | PROG | NEG | 3SG | 3PL | PROG.3PL |
| --- | --- | --- | --- | --- | --- | --- |
| GO | ʔɨ˦ɨ˨˦ | lɨ˨˦-ʔɨ˦ɨ˨˦ | ʔɛ˦-ʔɨ˦ɨ˨˦ | ʔɨ˦ɨ˨˦-ɲi˨˦ | ʔɨ˦ɨ˨˦-ʔɨ˦ | lɨ˨˦-ʔɨ˦ɨː˨˦-ʔɨ˦ (irregular) |
| EAT | mɛ˨˦ɛ˨ʔɨ˦ | lɨ˨˦-mɛ˨˦ɛ˨ʔɨ˦ | ʔɛ˦-mɛ˨˦ɛ˨ʔɨ˦ | mɛ˨˦ɛ˨ʔɨ˦-ɲi˨˦ | mɛ˨˦ɛ˨ʔɨː˦-ʔɨ˦ (irregular) | lɨ˨˦-mɛ˨˦ɛ˨ʔɨː˦-ʔɨ˦ |
| SEE | ʔɨ˦li˧ | lɨ˨˦-ʔɨ˦li˧ | ʔɛ˦-ʔɨ˦li˧ | ʔɨ˦li˧-ɲi˨˦ | ʔɨ˦li˧-ʔɨ˦ | lɨ˨˦-ʔɨ˦li˧-ʔɨ˦ |

The 3PL suffix lengthens a stem-final vowel before it (EAT, GIVE): a real, statable irregularity. Gram paths:
- LOC from BELLY: free *liː˨˦bʱɛ˨˦* (18.0) > clitic *la˨˦ɨ˨˦bʱɛ˨* (14.5) > affix *la˨˦* (10.5). A body part to a locative: attested.
- PROG from AT: free *li˨˦li˨* (16.0) > clitic (10.5) > affix *lɨ˨˦* (9.5). Locative to progressive: attested.
- 3PL from THEY: *u˦* (11.5) > clitic *ʔy˦* (10.0) > *ʔĩ˦* > *ʔɨ˦* > affix (2.5). 3SG from HE/SHE/IT: *ɲi˨˦* (2.5) > affix (0.5).
- NEG coined *ʃɔ˧* (10.5) > clitic (9.0) > *ha˧* > affix *hɛ˧* (6.5) > *ʔɛ˧* > fused *ʔe̞˦* (3.5) > *ʔɛ˦*: the erosion ʃ > h > ʔ again.
- PAST (*ɡa˨˦* 20 kyr > ... > *ʔɨ˦*) and FUT (*ʃɨ˦ʐi˨* 14.0 > *ʔɨ˦ʐ*) both wore down and died at 3.5 kyr, unrenewed.
- Defects: 3PL and CLASS:2 are both *ʔɨ˦*; PROG *lɨ˨˦-* is identical to the lexical 'thing' prefix in TREE.

*d726 (aarakocra 34, family p204; 68 cells, among the richest lects).* Nouns: WATER ʈi˦e˦˨ʊ˦˨, LOC **nɛ˨**-, DAT **ka˦**-;
PERSON o˦ʔa˦o˦ʔa˦; DOG mi˨ʔa˦i˦; TREE mi˦ʔa˦ʔa˦. Verbs are all prefixing:

| verb | lemma | PROG | PERF | NEG | 1PL | 3PL | CAUS |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GO | ŋa˦˨ɹɛ˦ny˨ | lẽ˨- | lɛ˦n- | i˦˨- | ta˦- | ɓy˨- | ka˦- |
| EAT | dʱlo˦˨ɹɛ˦ny˨ | lẽ˨- | lɛ˦n- | i˦˨- | ta˦- | ɓy˨- | ka˦- |
| GIVE | ka˦ɹɛ˦ny˨ | lẽ˨- | lɛ˦n- | i˦˨-**xa˨**ɹɛ˦ny˨ | ta˦- (PROG.1PL ta˦lẽ˨**a˦**ɹɛ˦ny˨) | ɓy˨- | ka˦- |

GIVE alternates k ~ x ~ ∅ after prefixes: real stem allomorphy. Gram paths: PROG from AT (6.0, clitic *lẽ˨to˨ɳ* > fused *lẽ˨* 0.5);
PERF from HOLD (1.0 *lɛ˦nɹɛ˦* > *lɛ˦n*); 3PL from THEY (*ɓo˨nni˦˨* 3.0 > *ɓy˨*), after an older 3PL *ʊ˦˨ɳe˦˨* died at 6.0; CAUS
from GIVE, renewed three times (11.0, 5.5, 1.5); DAT from GIVE (*ka˦*, homophonous with CAUS); DEF from THAT, renewed at 1.0;
3SG *kʷe˦ʔa˦* (7.0) > *ke˦* > *tʃe˦* > *ʃe˦* > *he˦* > *e˦*, then replaced by a free *sa˦* at 0.0. **Winces:** grammar churns (most
grams here are under 6 kyr old, several renewed two or three times); DAT = CAUS = *ka˦*, AGENT = PERSON = *o˦ʔa˦*; the nouns are
ʔa-strings (PERSON, DOG, TREE).

**(f) Names.**

| people | endonym | book spelling | gloss | pattern | made from |
| --- | --- | --- | --- | --- | --- |
| firbolg | ŋi˨le˦ ʔõ˦mo˨ | Ngile omo | the hunters | E8 way of life | ngile 'hunt' (coined 4 kyr ago) + particle omo |
| lizardfolk | ʔʉ˦ɣːi˦ʔʉ˦ʔi˨hi˨ | Ugghi'u'ihi | the snake people | E11 totem | ugghi 'people' + u'h 'snake' |
| tortle | ʔa˦ɲɨ˦ɛ˦la˨ | Anyïela | the old people (first on Simath) | E7 | ela'ïzhi 'people' + anyïï 'old' (ANCESTORS + 'like') |
| kobold | dʱə˨ɪ˦βa˨ɾi˨ | Dheivari | the river people | E4 | varie 'people' (borrowed from d408) + dhei'i 'river' |
| dwarf | ɬə˨ɪ˨lɾy˨ŋʔə˦ | Hleilrüng'e | the real people | E2 | hleilshïhliġi 'people' + rüng'ei 'real' |

| by -> of | exonym | book spelling | gloss | pattern | basis |
| --- | --- | --- | --- | --- | --- |
| orc -> triton | ɨ˦lə˨˦mɨː˧l | Ïlemiil | the enemies (raiders) | X5 | tritons settled among orcs on 20 cells in 2 kyr |
| green dragon -> hill giant | ɨ˦ʔə‼˦ŋxe˦ɗə˨ | Ï'erhngxe'de | the mutes | X3 | ï'erh 'mute' + class prefix |
| elf -> dragonborn | ʔĩ˦ɭi˦ɲi˦ʔĩ˦ɲi˦ʔo˦a˦ | Inḷinyi'inyi'oa | the strangers | X2 | oaha 'stranger' + people class |
| drow -> tortle | ʃi˦ʒi˨ɲi˨ŋi˨ɹi˦ | Shizhinyingiri | the beaked ones | X7 body | 'people' + 'bird' + 'mouth' |
| aarakocra -> human | ʔɪ˨i˨ | Ii | their own name I izh, as aarakocra hear it | X1 | first met in deme 561 |

Place names, each with its chain:
- **River Engengif, 'the long river' (deme 677, orc; P2, substrate).** Halfling d416: *ə˦˨tʃ* 'far' (coined 12.5 kyr) > *ɜ˦˨f*
  > FAR + 'like' = *ə˦ŋɨ˨ɜ˦˨f* 'long' (8.5) > *ʔɜ˦ŋɜ˨ɜ˦˨f*; *a˨˦ŋi˨˦f* 'river' (4.5) > *ŋi˨˦f*; name *ʔɜ˦ŋɜ˨ŋi˨˦f* > kept by the orcs
  when deme 416 shifted, *ʔɛ˧ŋɛ˧ŋi˧f* (tones levelled to mid).
- **Peak Kxallïï, 'the black mountain' (deme 666, human).** p306 *ze˦˨m* 'night' (20 kyr) > *si˨* > *ɨ˦* > NIGHT + 'like' = *ɨ˦ɨ̃˦˨*
  'black' (5.0) > *ɨ˦ɨ˦˨*; *ɡɣã˧l* 'mountain' (coined 7.0) > *kxa˦ɫ*; name *kxa˦ɫɨ˦ɨ˦˨*. 'Night-like' for 'black' is good.
- **Lake Neðnitiʿnishwdhix, 'the stone lake' (deme 51, brass dragon; P2).** Kobold d239: *ɣri˦˨ɕsiː˦˨x* 'stone' (coined 0.5 kyr),
  *ɾɛ˨sri˦t̪s* 'river' (1.0) > RIVER + 'thing' = 'lake'; name *ɾɛ˨sɹi˦t̪ɣri˦˨ɕsiː˦˨x*, which the brass dragons heard as
  *nɛ˨ðni˨t̪i˨ʕni˨ʃʷði˨x* (13 segments). The name is dated 20 kyr, from words coined in the last 1 kyr.

## 5. Sound change over time in one lect

**d691 (human 49, the west of Ratal; p306 > d561 > d604 (19.0) > d691 (13.0)).** 332 sound changes in 20 kyr (16.6 per kyr): by
cause effort 96, coarticulation 76, dispersion 61, prosody 43, perception 34, tonogenesis 22. 278 own, 54 adopted by wave (26 from
d666, 13 from d375, the rest from 7 other lects). 93 rules fired more than once ('rare sounds merged' 24 times; h-loss, nasal place
assimilation 6 each). In order (`[dX]` = adopted from lect dX; "rare sounds merged" entries left out):

- 19.5 (d561): metathesis sk; pt > tt; r lost before C or finally with lengthening; long vowels shorten before CC; r > ɹ [d375]; n > ɲ before i, j [d375]; iː, uː > ai, au [d375]; s > ʃ before i [d381]; l > ɫ before C or finally [d381]; k, ɡ > tʃ, dʒ before front vowels [d381]; a > ɛ stressed open [d421]; z > r /V_V [d421]; w > b /#_ [d421]; j > dʒ /#_ [d432]; nasal place assimilation [d467]; b > β /V_V [d485]; k > tʃ before front vowels [d485]
- 19.0 (d604): a > ɛ stressed open; back harmony; final devoicing; h lost in codas with lengthening; kt > jt; degemination; s > z /V_V; k, ɡ > tʃ, dʒ [d375]; dz > z [d375]; low tone before voiceless stop + C [d375]; t > ʔ /V_V or finally [d580]
- 18.5: voiced stops > breathy; k > ʔ finally; p t k > ʔ finally; m lost finally; ɛ, ɔ > je, we stressed; n > ɲ before i, j; ts > s; k > h /V_V; VC > long V before C; w lost /#_ [d375]; aː > ɛː [d375]; k > tʃ [d375]; i˨ inserted between consonants [d375]; p lost /#_ or /V_V [d466]
- 18.0: s lost finally; s > h /#_, /V_V; tʃ > ʃ; t > θ /V_V; θ > s; fricatives voiced after unstressed vowels; t > tʃ before i; h lost; p t k > f θ x [d375]
- 17.5: x > h /#_; s > ʃ before i; i˨ added after final C; low tone after voiced obstruents; j inserted after i before V; umlaut; l > r after C
- 17.0: w lost before u, o; nasal place assimilation; χ, x > h; s > ʂ after r u k i (ruki); e > i before nasals; o > a unstressed; eː, oː > iː, uː; l > w before C or finally; raising before i; s > r /V_V; liquid metathesis; tone becomes phonemic
- 16.5: j > dʒ /#_; iː, uː > ai, au; k > ts before front vowels; intervocalic voicing; i˨ epenthesis; dʒ > ʒ; z > s; gemination after stressed short vowels; p t k > pf ts kx initially; m > n finally [d375]
- 16.0: CrV > CVr; w > v; i, u > j, w before vowels; o > o̞; e, o > i, u stressed; f > h; θ > t
- 15.5: k > ɡ /V_V; j > ʒ; l > ɫ before C or finally
- 15.0: ts > s; palatalization of k, ɡ; final C lost; tʃ > ʃ; nasalization before nasals; nasal vowels denasalize; n > ɲ before i; breaking; labialization before u, o; r > ʁ
- 14.5: stops voiced after nasals; h lost; b d ɡ > p t k; s > ʃ before i; w inserted after u; i > ɨ; long vowels shorten before CC; k > x after vowels; nasalization after h, ʔ; compensatory lengthening
- 14.0: u > o before C(C)a; o > a unstressed; aː > ɛː; t > ʔ; e, o > i, u unstressed; degemination; low tone before voiceless stop; final unstressed vowel lost; m lost finally
- 13.5: i˨ epenthesis (three rules); kʷ > k; regressive voicing; umlaut; eː, oː > iː, uː; low tone after voiced obstruents; iː, uː > ai, au; t > tʃ before i; ʃ > x; s > h; p t k > f θ x; f > h /#_ [d375]
- 11.5 (d691): w > ɡw /#_; n > ɲ; breaking; devoicing of b d ɡ; y > i; j > dʒ; χ, x > h; h lost; j insertion; l > ɫ [d666]; k > tʃ [d666]; p t k > pf ts kx [d666]; ʔ lost in codas [d666]
- 11.0: final C lost; tʃ > ʃ; intervocalic voicing; ts > θ; compensatory lengthening; iː, uː > əɪ, əʊ; tone phonemic; e > i before nasals [d666]
- 10.5: j > ʒ; nasal place assimilation; dʒ > ʒ; umlaut; o > a unstressed; low tone after voiced obstruents; i, u > j, w before V; syncope [d666]; e, o > i, u stressed [d666]
- 10.0: u > y; ʔ inserted before initial vowels; nasalization; θ > t; fricative voicing [d666]; voicing assimilation [d666]; p t k > f θ x [d666]; ŋ > n finally [d666]
- 9.5: VCjV > VjCV; denasalization; a > ɛ; e, o > i, u unstressed; w > v [d604]; θ > s, s > z, f > h, z > r, r > ɹ [all d666]
- 9.0: ɔ > ɑ; final devoicing; long vowels shorten; ts > s; s > ʃ before i; low tone [d666]; l > r after C [d666]; prothetic i˨ [d666]; ʃ > x [d666]; CrV > CVr [d666]; CCC simplified [d666]; r lost with lengthening [d666]; iː > ai [d666]
- 8.5: y > i; h lost; nasalization after h, ʔ; χ, x > h; breaking [d666]; f > h [d666]
- 8.0: voiced stops > breathy; lengthening of stressed vowels before CV
- 7.5: s > h before C or finally; nasal place assimilation; gemination; e > i before nasals; j > ʒ; intervocalic voicing; n > ɲ; regressive voicing; h lost in codas; degemination; s > h /#_, /V_V
- 7.0: iː, uː > əɪ, əʊ; tone phonemic
- 6.5: compensatory lengthening; umlaut; e, o > i, u unstressed; final unstressed vowel lost; m > n, ŋ > n finally; labialization; o > a unstressed; a > ɛ; fricative voicing; eː, oː > iː, uː
- 6.0: long vowels shorten; w > ɡw /#_; l > w; n > ŋ finally; nasal lost after nasal vowel; u > y; denasalization
- 5.5: h lost; w > v; ʔ inserted before initial vowels
- 5.0: z > s; low tone before voiceless stop; l > r after C; voiced stops > breathy; r > ɹ; prothetic i˨; ruki; y > i
- 4.5: nasal place assimilation; stressed-vowel lengthening; low tone after voiced obstruents
- 4.0: s > r /V_V; iː, uː > ai, au; ə > ɜ; s > h; f > h; e, o > i, u stressed; r > ʁ
- 3.5: gemination; final devoicing; degemination; ŋ > n finally; ɛ > e̞; devoicing before voiceless; Cʔ > ejective
- 3.0: l > w; ʔ lost in codas; ʃ > x; x > h /#_; x > f finally
- 2.5: m > n finally; o > a unstressed; breaking; k > ʔ finally; aː > ɛː; h lost; w > v; e > i before nasals; w after u; k > ts before front vowels; long vowels shorten before CC
- 2.0: eː, oː > iː, uː; stops voiced after nasals; a > ɛ; k > tʃ after i; k > x after vowels; e, o > i, u unstressed
- 1.5: CCC simplified; umlaut; x lost before C with lengthening; p t k > f θ x; m lost finally; regressive voicing; long vowels shorten; nasal place assimilation; n > ŋ finally [d604]
- 1.0: compensatory lengthening; low tone after voiced obstruents; nasalization; f > h (twice); nasal lost after nasal vowel; intervocalic voicing; w lost before u; iː, uː > əɪ, əʊ; tone phonemic (high default); h lost in codas [d604]
- 0.5: low tone before voiceless stop; ɣ lost /V_V; χ, x > h; stressed-vowel lengthening
- 0.0: e, o > i, u stressed

Inventory of the line at four moments:

| kyr | lect | C | consonants | V | vowels |
| --- | --- | --- | --- | --- | --- |
| 20 | p306/d561 | 26 | p b ɓ f v m t d tʰ ts dz s z ʃ tʃ n r l ȶ ʈ j k ɡ ŋ w h | 10 | i e ɛ a ɔ o u ɨ aː ɔː |
| 10 | d691 | 26 | ʔ ʃ t dʱ ɲ ʈ tʰ n l m f ʂ ȶ ŋ ɓ bʱ w j kx ɖ ts ɲ̟ ŋʷ ŋ͡m ʒ ɱ | 15 | ɨ i a y ɛ ɨ̃ ɛː ĩ ɔː o̞ ã ɔ o e aː |
| 5 | d691 | 32 | ʔ ʒ dʱ ɲ tʰ l ʈ ɦ ŋ m v ȶ ɡɣ ɖʱ ɓ n f ʐ ɹ ɡʱ ʂ kx ȡʱ s lʷ bʱ ɓ̥ ɲ̟ ɳ ŋʷ ŋ͡m ʒʷ | 9 | ɨ e i ə ɪ a ɛ o ɔ |
| 0 | d691 | 36 | ʔ l tʰ ʐ dʱ m ʈ f ɡ v ʂ n kx h ɓ ŋ ȶ ɲ bʱ ɖ ɹ w s ʁ ɳ ɱ ts dz ɡɣ z ʃ ŋ͡m ʒ k tʃ ȡ | 15 | ɨ i ɨː iː ɛ a u ɜ ɪ aː ɔː e ɔ o ə |

Read as a linguist: each change is a real, attested type and the sequence has natural chains (s > h > ∅; p t k > f θ x > h;
voiced stops > breathy > tone). Too much of it, though: 16 changes per kyr, the same handful recurring (h-loss six times, a > ɛ
four), and the inventory ends with ŋ͡m, ɓ̥ (a voiceless implosive) and both ɖ and ȡ, at 36 C against PHOIBLE's 21.

**d726 (aarakocra 34, the north of Sothasor; p204 > d292 > d726 (9.5)), in brief.** 389 changes (19.5 per kyr; generation 5.8
years): effort 148, coarticulation 93, dispersion 67, perception 34, tonogenesis 25, prosody 22. Only **10 adopted** (all from
d180): aarakocra change on their own. 71 rules repeat (merges 21, s > h 7, h-loss 7). The first step (19.5) alone has 27 changes;
at 10.0 and again at 1.0 the lect applies n > ŋ and ŋ > n finally in the same step; at 5.0 t > θ and θ > t. Inventory: 20 kyr
19 C (with kʷ tʼ ɻ) / 12 V (with iːᴖ); 10 kyr 28 C (ɓ ħ ʕ ɳ ʂ bʱ dʱ gained) / 13 V, the second voice gone; 5 kyr 26 / 14; now
25 C `ʔ l ɹ n ɾ ɻ k ɓ ʈ dʱ p t ŋ ʂ ɲ ʃ ħ m b tʃ ɣ x s h ɳ` / 13 V `ɛ a y ə ɪ i e o ʊ ɨ aː ẽ ɒ`. Labials p b m ɓ only.

## 6. The checks, as measured

| check | measured | target | pass |
| --- | --- | --- | --- |
| proto inventories vs PHOIBLE | 110 human-voiced protos: median 23 C, 8 V; 51% inside the C IQR, 54% inside the V IQR, 23% both; top-20 segment overlap 19 | medians inside the IQR (C 17-27, V 6-12); 35-75% inside per measure; top-20 overlap >= 10 | yes |
| sisters recognisable, distant not | blind cognate share: sisters parted <= 2 kyr 0.541 (182 pairs); different families 0.003 (197,692 pairs); chance floor 0.013 | sisters > 0.5, different families < 0.15 | yes |
| scholars' horizon (human lects) | **9.0 kyr** (all lects 9.6; old per-pair measure 9.0, all 12.0) | 6-10 kyr | yes |
| language shift happened | 214 shifts; 104 of 633 living lects speak outside their deme's descent | > 0 | yes |
| long generations change less | humans 15.2 rules/kyr, long-lived peoples 4.5 (ratio 3.35) | long-lived < a third of humans | yes |
| hubs simpler, isolated richer | complexity: hubs 1.47 (208 lects), isolated 3.35 (61) | hubs < isolated | yes |

**Horizon: share of true splits the scholars' tree recovers, by age (2-kyr windows, human lects).**

| split age kyr | 0-2 | 1-3 | 2-4 | 3-5 | 4-6 | 5-7 | 6-8 | 7-9 | 8-10 | 9-11 | 10-12 | 11-13 | 12-14 | 14-22 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| splits | 10 | 13 | 9 | 10 | 14 | 13 | 11 | 11 | 6 | 2 | 2 | 1 | 3 | 3-8 each |
| recovered | 0.90 | 0.92 | 1.00 | 0.70 | 0.57 | 1.00* | 0.75* | 0.64 | 0.50 | 0.50 | 0.50 | 0 | 0 | 0 |
| mean cognate share | 0.55 | 0.40 | 0.30 | 0.15 | 0.11 | 0.11 | 0.09 | 0.05 | 0.04 | 0.03 | 0.03 | 0.003 | 0.006 | <= 0.014 |

\* scored on the big splits only (3 and 4 of them); counting all splits these bins give 0.69 and 0.82. The 9.0 reading rests on
bins of 6, 2 and 2 splits, so it would move by a kyr or two on another seed.

**Shares, three ways:** sisters parted <= 2 kyr: loose 0.541, strict (aligned distance under the threshold and recurring
correspondences) 0.462, true (same root in the etymologies) 0.572. Different families: loose 0.003, strict 0.000, true 0.0003.

**Intelligibility now** (`intelligibility.now`, 951 pairs):

| pair | pairs | 10th / median / 90th pct | share > 0.7 | share < 0.4 |
| --- | --- | --- | --- | --- |
| sisters parted <= 2 kyr | 182 | 0.24 / 0.42 / 0.71 | 0.11 | 0.46 |
| parted 2-5 kyr | 288 | 0.07 / 0.16 / 0.36 | 0.01 | 0.93 |
| parted 5-10 kyr | 362 | 0.06 / 0.12 / 0.26 | 0 | 0.99 |
| parted > 10 kyr | 114 | 0.06 / 0.08 / 0.17 | 0 | 1.00 |
| different families | 5 | 0.06 / 0.08 / 0.09 | 0 | 1.00 |

Sisters parted under 2 kyr are only half intelligible (median 0.42); by 2-5 kyr
they do not. **Continua found by the pass: 2.** Family p269: human d177.2 – gnome d470.2 – gnome d765.1 (links 0.66, 0.56; ends
0.48), the west of Simath; family p300: halfling d543.3 – elf d550.2 – human d570.2 (0.53, 0.56; ends 0.36), the south of Ratal.
Both are shifted peoples speaking one family's lects. The viewer's in-browser search finds more chains at earlier frames.

## 7. Species

| group | lects (living) | generation yr | rules per kyr (median, q1-q3) | inherited core share (median; living with 0) | mean word length (segments) | homophone share | inventory C+V | shifts as speakers / rulers | ʔ-initial core words |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| human | 136 (105) | 28 | 15.6 (10.8-18.6) | 0.10; 0% | 4.84 | 0.092 | 42 | 26 / 124 | 19% |
| dragons | 131 (118) | 430 | 3.9 (3.2-4.7) | **0.77**; 0% | 4.72 | **0.144** | 38 | 2 / 18 | 7% |
| elves | 36 (27) | 145 | 6.0 (4.1-8.6) | 0.46; 0% | 4.97 | 0.113 | 33 | 4 / 12 | 12% |
| kobolds | 100 (53) | 12 | 19.6 (16.6-23.5) | 0.01; **28%** | 4.90 | 0.099 | 41 | 18 / 4 | 19% |
| aarakocra | 50 (26) | 6 | **22.6** (16.1-28.8) | **0.00; 65%** | 5.32 | 0.106 | 39 | 20 / 0 | 12% |
| dragonborn | 97 (56) | 25 | 15.7 (14.2-16.9) | 0.08; 2% | 4.88 | 0.081 | 42 | 24 / 3 | 21% |
| all others | 378 (248) | 30 | 14.7 (8.9-19.0) | 0.11; 0% | 4.73 | 0.096 | 42 | 120 / 53 | 21% |

("Rules per kyr" counts every change on the lect's line of descent over 20 kyr, wave-adopted ones included: dragons adopt 61% of
theirs, aarakocra 12%.)

- **Human:** the reference. One core word in ten survives 20 kyr, roughly what glottochronology would predict; sound change is fast.
- **Aarakocra: not mush in sound, amnesiac in words.** Their inventories are normal (39 segments, few labials, 12% ʔ-initial
  against 19% for humans), but at 23 changes per kyr and a 6-year generation 65% of living lects keep no proto core word at all,
  so no family is visible after a few kyr. Some lexicons do turn into ʔa-strings (d726 PERSON o˦ʔa˦o˦ʔa˦, TREE mi˦ʔa˦ʔa˦).
- **Elves: conservative, as wanted.** A third of the human rate and 46% of the core kept after 20 kyr.
- **Dragons: very conservative, perhaps too much.** 77% of the core kept, but the highest homophone share (14%) and most of their
  changes come from neighbours by wave. Almost never shift.
- **Kobolds: as fast as aarakocra** (20 changes per kyr, 12-year generation): families barely visible (median 1% core kept).
- **Dragonborn: human-like** in speed and retention; a quarter of their 97 lects arose by shifting to human or other rulers.

## 8. What is still wrong (honest list)

Measured over the 633 living lects (218,045 words):

- **Largest living inventories** (C + V): human d721, d843 and dragonborn d363 at 45 + 20 = 65; human d465 45 + 19; green dragon
  d91 45 + 17. d843: `ʔ m l h d̪ ŋ ɲ kʷʰ ɹ l̪ ɢʷ n̪ n qʷ t̪ tsʰ ɫ ɡʼ ʈʂʰ dʱ xʷ nʷ pʰ bʰ ʐ l̪ʷ ȵ ŋʷ ɡʰ bʱ ɬ d̪ʷ kʰ s kʼ ɮʷ t̪ʷ ɲʷ sʷ f ʂ z ɮ ɡʷʰ lʷ`
  + 20 vowels (8 nasal). d363 has ɓ and ɓ̥, n‼ and r‼, and 20 vowels with a‼ and i‼. PHOIBLE's upper quartile is 27 + 12.
- **Words over 12 segments:** 116 (0.05%); the longest are 16 segments, all CHILD (DESCENDANT) in elves and drow
  (d835 ʃi˦ɲi˨ʒi˦ŋʷi˨bʱi˦bʱi˦vi˨ɲi˨).
- **Brace segments `{`:** none (in words, inventories or grams). **Empty forms:** none in lexicons; 50 fused grams have a zero
  form (zero marking, acceptable).
- **Duplicate spellings:** in 513 of 633 lects two inventory segments get the same letter (ɜ and ə both ‹ë›, ɹ and ɾ both ‹r›,
  a, ä, ɐ all ‹a›); 546 pairs of different words share one spelling, in 217 lects.
- **Shifts per deme:** up to 6 (deme 168: hobgoblins of deme 289 rule it from 19 kyr, and it "shifts" at 19, 16, 13, 10, 7, 4).
  103 of the 214 shifts are a deme moving to another lect of the same true family, and the gap between a deme's shifts is
  never below, and has a median of, exactly 3.0 kyr: the cooldown sets the pace.
- **Koine levelling:** 237 entries. Example: d468.2 (halfling) THIS ɲɨ˧ʃi˧i˧, "borrowed from d844, koine levelling in city 1136".
- **Food routes:** 20 of 98 start at a taming site ("tamed here"), 22 "inherited by the donor", 56 "first known here". In 28% of
  hops the receiver's present word shows no borrowing (see rice in SAMPLES c2).
- **ʔ-initial words:** 15.6% of all words, 17.1% of core words (down from a third in the earlier run).
- **Top 12 segments (token share):** ʔ 6.9%, i˨ 4.4, ɨ˦ 4.2, ɨ˨ 3.7, i˦ 3.4, l 2.9, n 2.7, ɲ 2.7, m 2.5, ŋ 2.4, a˦ 2.2, ə˨ 2.2. ɨ is
  three of the top four vowels (i > ɨ "dispersion" fires everywhere); world languages favour a, i, u.
- **Tone everywhere:** 98% of living lects are tonal against 24% of protos and about 40% of real languages.
- **Same-step reversals:** in 1,315 lect-steps a change and its inverse fire together (n > ŋ and ŋ > n finally 656 times, s ~ z
  348, t ~ θ 220, d ~ ð 152).
- **Seen in the samples:** derivations with no sense behind them (EAT + 'thing' = 'tree', TREE + 'agent' = 'fire', WATER + 'agent'
  = 'river', SALT + 'agent' = 'sea', LOUSE + 'thing' = 'this', EAR + 'thing' = 'fish'); 39% of living core words go back to a
  coinage from nothing; I = WE in d774 and d280; homophonous grams (DAT = CAUS, 3PL = CLASS:2); dragonborn words as vowel strings;
  half the place names (169 of 343) are dated before the words they are built from were coined; one people uses the same
  exonym for different peoples 168 times (aarakocra call elves and dragonborn both Ehilanfï, 'the people of the east'); halflings
  and humans share the endonym I izh because the halflings' lect is a human one; proto forms such as *sret.ʃsukqʰi‼k* are still
  not possible words.

**Fix first, in order:**
1. **Tone and ɨ everywhere.** Tonogenesis and the i > ɨ push fire in almost every lect, so all species converge on the same
   tonal, ɨ-heavy sound. Make them conditional and rarer.
2. **Re-shifts on a 3-kyr clock.** Half the shifts are a deme re-adopting its rulers' family every 3.0 kyr; each one recopies the
   lexicon. A deme that already speaks the rulers' family should level (koine) rather than shift.
3. **Derivation semantics.** 'thing', 'agent' and 'like' produce absurd meanings and, in p306, a lɨ˨˦- prefix on 12% of words that
   fakes cognates. Restrict each affix to plausible source-target meaning pairs.
4. **Inventory growth and spelling.** Half the living lects end above PHOIBLE's upper quartile (to 65 segments), and 513 lects
   spell two segments alike; tie inventory growth to losses and give each contrast its own letter.
5. **Bookkeeping that contradicts itself:** food-route hops that splice different words, names dated before their words, a change
   and its inverse in one step, exonyms reused across peoples. Each is small, but a reader sees all of them.

## 9. Judgement calls the lane made (beyond the five above)

- **Proto-languages at 20 kyr**: one per connected component of same-people demes in contact at the start frame
  (320 components on a24559), so continua start as continua; isolated demes get their own; arrivals (elves, gnomes, tritons)
  get a fresh proto-language at their first deme because `demes.json` gives them a wrong deme parent.
- **One lect per deme, always**; a "language" is a cluster of lects measured afterwards (blind cognate share > 0.7).
- **Shift triggers** are derived, not stored: incursions located through `demes_all`, settlement holder changes aggregated
  per ruler/ruled deme, mixed cities, long trade contact. Elite rule needs the ruler to out-prestige the ruled (population,
  cities, writing, law); the other way round is swamping. A deme may shift only to a different language and not within
  3 kyr of its last shift.
- **Rates are calibrated by the horizon check**, with the tension described above. Final constants in `calibration.md`.
- **Inventories are capped** at 1.5x the proto count (45 consonants, 20 vowel qualities); rules that would add a new
  segment are drawn at 0.3 weight; a rule fires at most twice in a lect's life and not twice within 3 kyr.
- **Only nouns compound**; verbs replace by derivation, shift or a fresh root. Compounds take a head from the concept's own
  domain and a modifier from a CLICS neighbour.
- **The check "proto inventories vs PHOIBLE"** was redefined: medians inside PHOIBLE's interquartile range and 35-75% of
  protos inside it on each measure, since a PHOIBLE-like draw puts half of them inside by definition.
- **Hydrids, templates and overlays** (half-elves, tieflings, genasi, aasimar) have no demes in the run, so no lects.
- **Writing hand-off**: `output.export_writing` gives IPA, morpheme breaks and glosses per word; nothing about scripts.

## 10. Tickets

Updates for the coordinator to put on the board after merging:

- **PW-1423** (done for the demo): percept space, profile schema in the lineage spec (`voice`, inherited like `body`),
  human profile from PHOIBLE, inheritance tested, the demo runs on it, non-human profiles drafted with sources
  (`voice-profiles.md`) for Daniel to react to. Open: the variant-share draft (`draft-language-nonhuman-variant-share.md`).
- **PW-986** (the demo stands; the owner rules): all slice items built; checks 5 of 6 pass; the horizon check and the rates
  need the ruling above; the brief section renders but `brief.build` crashes on a24559 on current code before reaching it
  (the stored tree no longer parses under PW-1275: "tortle: density and band_km2 are no longer given"), so the brief could
  only be checked on a synthetic run - a main-branch issue, not the lane's.
- **PW-982**: the full catalogue (178 rules after dedup), the lexicon processes and the grammar ladder are in; what is
  left of it is quality (the defects list) rather than scope.
- **PW-972**: name stacks filled with word forms; 6% of exonym rows are plain 'foreigners' (the bar was a third).
- **PW-984**: food routes are in the output and the brief (172 routes on a24559); the donor-form issue in §8.
- **PW-985**: sociolinguistic pressure acts on the gram rates; the "hubs simpler, isolated richer" check passes on this run.
- **Drafts** (3): `draft-language-rates-and-horizon.md` (needs-decision), `draft-languages-json-size-and-cost.md`,
  `draft-language-nonhuman-variant-share.md`. Folded into this write-up instead of drafts: the two knowledge tables deserve a
  spot-check of their examples (`reference-data.md` lists the doubtful rows); koine has fired only on synthetic data;
  `brief.build` on a24559.

## 11. How to run it

- `uv run python -m planet languages a24559 --out DIR --workers 12` (15 min; writes `DIR/a24559/languages.json`); without
  `--out` it writes into the run and adds `meta.languages` to run.json.
- `uv run python -m planet speak "kalima" --people human --out k.wav`
- Tests: `uv run pytest -q tests/test_language_*.py tests/test_languages_viewer.py` (the not-slow suite: 1483 passed, 1 skipped; language tests 507).
