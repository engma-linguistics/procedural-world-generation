# For Daniel (set aside overnight, 2026-11-07 → 11-08)

Everything here has a working default in the code already. Nothing is blocked; change any of them in one place.

## Decisions (defaults taken)
1. **Synthesis level** (how affix-heavy languages are). Grammar A measured it: 58% of our lects mark 0-1 verb categories with affixes, against about 3% in WALS 22A, so ours are far more isolating than real languages. Default: unchanged until grammar B adds mood and it's measured again. Then raise `FUSE` (0.012 to about 0.02) if it's still over about 25%. Details in the Grammar phase A section.
2. **Species leanings in grammar** (like kenku → tone): the lane's guessed table, marked as guesses.
3. **Letters for non-human sounds** in book spellings (the purr vs trill rr): names lane's guess.
4. **Merger veto / homophony; spread of change rates between lects:** current settings kept.
5. **After a shift: how long minority speech lives, L2 share levels, how much dialect continuity:** current settings kept, with the reviews' numbers alongside.
6. **A shifting people keeps the old language's sounds, or reshapes them by its own voice:** current behaviour (keeps them) kept.
7. **How to read the scholars' horizon** (the one check still failing). The current reading swings between 4.5 and 17.6 thousand years on the same code with different seeds. Recommendation: use the logistic fit (about 13 on current code, steadier) as the check's value, and decide whether 6-10 stays the target. Details and decisions 8-12 (fresh roots, kinship weights, name-taboo rates, avoidance registers, areal rate) are in the Lexicon & contact section.

## Weirdness noticed
- **The demo page has glitches** (a full read before publishing found them). Merchants are glossed as things in two languages, a dual marker is described but missing from its example, one note quotes the wrong verb, and some agent jargon shows. None is in the data model's core. All are queued as the first item of grammar B in queue.md.
- **Scholars' horizon: mostly noise in the measure, and your call on how to read it.** The same code read 10.7 or 17.6 thousand years depending only on the random seed. The lexicon lane traced it (see its section, decision 7).
- See each lane's section below for more.

## Demos waiting
- **Languages demo page** (version 2, 11-08 morning: grammar B, 10 languages, 294 audio clips, complexity tab; a full read found a few remaining slips, now with grammar C): https://claude.ai/artifact/GQUxhWHnErqn3zx7MTaFUs (private). Live viewer: `uv run python -m planet langserve a24559 --host 0.0.0.0 --port 8790`.

## Finish lane (lang-finish, 2026-11-07)

**Decisions taken by default**
- **Rounding harmony.** Only high vowels copy the root's rounding, as in Turkish (göz-ün, but göz-ler, not *göz-lör). A non-high vowel takes the root's backness. After an unrounded root it may lose its rounding, but it never gains it. Before this, a > ɒ made ɒ a living vowel in a fifth of all lects.
  - Change it in `planet/language/rules.py` `_produce` (the `first_vowel` branch).
- **New ways out of ɖ.**
  - S215: ɖ > ɽ between vowels (Hindi-Urdu ghoṛā).
  - S216: ɽ > ɾ (Eastern Bengali).
  - S217: ɖ > r at the start of a word (Romani rom < ḍomba).
  - These live in `tools/language/knowledge_tables.py`.
- **Non-human voices now feel ease drag from their own species' make costs.** Before, they had none, so u > y and l > ɫ ran unchecked in kenku, aarakocra, kobold and dragonborn lects. Their voice profiles do not favour y or ɫ.
  - The steepness is `EASE_K`, the same for every voice, in `planet/language/lect.py`.
- **u‼ is a non-human sound.** The two-voiced (harsh) u‼ is now treated as non-human, so the overuse check skips it.
- **p is left as it is.** It is rare across all lects because beaked and lipless mouths find labials dear: aarakocra labial cost 5, reptilian 4. Human lects have p in about 0.7 (PHOIBLE 0.85). I did not force it.
- **Measure for "Languages getting more and less complex".** I used `grammar.complexity`: bound functions + mean gram level + 4 × allomorphy share + 0.5 × bound class markers. It comes from the 0.5 kyr snapshots, joined through the parent chain.
  - The window is the last 0.5–3 kyr. A change of at least 1.0 points counts as "clear".
  - These are `CX_WINDOW` and `CX_CLEAR` in `tools/language/demo_page.py`.
- **Piper speech threads are capped at 8 by default.** Set `PIPER_THREADS` to change it.

**Your call when you are back**
- About 22% of word meanings share a form with another meaning on a 700-meaning list. Almost all of it is polysemy attested in CLICS. Is that acceptable? This is also in the inbox draft on realism leftovers.

**Odd output noticed**
- **Grams that are lost outright.** A whole function such as NEG, PAST or PL sometimes drops out with nothing to replace it. For example, the goliath lect d152 loses NEG about 1.5 kyr ago. Real languages renew negation rather than lose it. The hobgoblin lect d641 ends with a complexity score of 0.38, almost no grammar left. Worth a look: maybe loss should need a renewal path for the core functions.
- **One sentence set for all.** All 617 living lects get the same English sentences ("The woman sees the dog.", "My older brother catches three fish."). Only the tense sentence varies (build / carve). That is good for comparing lects, but dull to read through. A per-lect pick is easy if you prefer it.
- **A click spelt "|" in names.** Elvish click names such as "Pxeyag|he" broke the markdown tables in the sketches. They are now escaped in tables only. The romanization itself is unchanged.
- **The pass is not faster.** It still takes about 21 minutes. The file is much smaller: 36 MB main, 126 MB in three files, against 241 MB in one.

## Sound lane (lang-sound, 2026-11-08)

**Decisions taken by default**
- **Series-based inventory draw.** A proto first draws which series it has (labial-velar, prenasal, retroflex, aspirated, ejective, implosive, uvular, labialized, long vowels, nasal vowels and so on). Each series is drawn with PHOIBLE's share among inventories of the same size, so a 12-consonant language almost never has ejectives. Then about 3/4 of PHOIBLE's mean member count for that series is filled, and the free picks follow.
  - Table: `planet/language/data/phoible_series.tsv` (built by `tools/language/build_reference_tables.py`).
  - Knobs: `SERIES_FILL` 0.75, `SERIES_BOOST_MAX` 12, `SERIES_FLOOR` 0.002 in `planet/language/inventory.py`.
- **Tonemes.** A contour found only on long vowels counts as two level tones, not a toneme (`lect.tonemes`). Tone sets go up to 7.
- **Dragon sub-bass.** Dragon vowels can carry a sub-bass register. Its make cost is `sub_register = 0.5` for the chromatic and metallic dragon profiles in `planet/language/data/voice_profiles.toml`. Most dragon protos now have at least one sub-bass vowel (about 9 in 10 in proto draws). Raise the cost if you want it rarer.
- **Stress.** IPA in sketches and pages carries ˈ. Speech (`/api/speak?stress=`) puts the stress on the right syllable. Stress is the lect's pattern (initial, penult, final), not stored per word yet.
- **Sound-change catalogue** (a helper did this on my branch):
  - 14 of the 21 refused rows now parse. 7 stay refused with a reason: S106 haplology (needs two identical syllables), S132 and S133 suffix harmony (handled by the harmony machinery, not the catalogue), S170 and S172 (pitch accent and tone loss, which are not segment rewrites), S183 and S184 (analogy, which is not sound change).
  - `X` means any segment (long-distance dissimilation `r > l / _X*r`, Grassmann).
  - ATR harmony S134 is approximated on height (ɪ ʊ ɛ ɔ > i u e o in a word with i u e o). This is said in the row.
- **Line drift.** Each proto line draws a lognormal liking per rule family (σ 0.7) and per row (σ 1.0). Daughters keep it, with a small jitter at budding (σ 0.2). Named laws (Grimm, Verner, Grassmann, the Great Vowel Shift and similar) fire at most once per line. Other rows wait 4 kyr before re-firing (was 3).
  - Knobs: `LINE_FAMILY_SIGMA`, `LINE_ROW_SIGMA`, `LINE_BUD_SIGMA`, `ONE_OFF_IDS`, `ONE_OFF_MAX`, `REFIRE_KYR` in `planet/language/lect.py`. Chain shifts count half (`history.RULE_WEIGHT["family:chain_shift"]`).
  - Effect in the helper's harness: rows found in at least 80% of lects 45 → 19; Grimm fires in about a quarter of lines, the whole Great Vowel Shift in 29%.
- **Chain shifts are one staged event in drag order.** "a > b > c" now means a > b, then b > c. Grimm S177 (after sonorants too), High German S178, the Great Vowel Shift S179 (top down), Northern Cities S182.
- **New common rows S218-S225.** t > k; k > ʔ; ŋ > n; secondary palatalization before front vowels; aː > ɔː; ɪ ʊ > i u; t k > s before i; k > tʃ before a. S174 diphthongizes only in stressed open syllables.
- **The synchronic rule layer** (new `planet/language/phonology.py`; architecture.md 5b):
  - Each lect keeps an ordered list of live rules, inherited by daughters. Rules come from its allophones (phonetic level) and its conditioned sound changes.
  - A new sound change starts as a phrase-level rule. It narrows to the word level after `PHRASE_KYR` 1 kyr and to the stem level after `WORD_KYR` 3 kyr. This is Bermúdez-Otero's life cycle.
  - A rule dies when it is old (lognormal life around `LIFE_KYR` 6 kyr), when it is opaque (more than `OPAQUE_MAX` 20% of the words it should touch break it), or when it is crowded out (more than `MAX_LIVE` 8 rules).
  - 70% of tonal lines (`SANDHI_SHARE`) draw one tone-sandhi rule: Meeussen's rule, a Mandarin-type low-low rule, high spread, or contour simplification.
  - Rules apply to new words, derivations, compounds, loans and names (`inventory.realize`). In sentences they apply at morpheme joins (word level) and across word joins (phrase level).
  - Sketches have a "Phonological rules" section, and the viewer's time tab shows "Phonological rules today". Both use plain notation (e.g. "/t/ → [ɾ] / V_V") with a worked example from the lect's own words where one exists.

**Your call when you are back**
- **Rule death.** Is a 6 kyr median life and 8 live rules at most a sensible picture? Real languages keep some rules for very long (Celtic mutations, Sanskrit sandhi). I took the life-cycle reading: most rules end as stem-level or lexicalized.
- **Dragon sub-bass.** About 9 in 10 dragon lines have it. Should it be rarer, or a hallmark of every dragon tongue?

**Odd output noticed**
- **Two checks fail on a24559 with the sound lane** (pass D, `planet languages a24559` into scratch, never into runs/). Before this lane: the horizon at 10.7 kyr already failed, and the overuse check passed.
  - **Scholars' horizon (human lects): 12 kyr** (target 6-10; base 10.7). The rule rate is 11.2 per kyr against 14.6 at base. Line drift, the once-a-line named laws and the 4 kyr re-fire wait all mean fewer changes fire.
    - I raised `rules.PICK_REDRAWS` from 8 to 16. That took the horizon from 17 to 12.
    - `LANG_RATE_SCALE=7` alone only went from 17 to 13.5, so I left `RATE_SCALE` at 5.
    - The horizon is thinly resolved: 3-6 splits per bin past 10 kyr. It read 9, 11 and 13 on base code in earlier rounds.
  - **Overused segments: ɑ 26% (PHOIBLE 7%), lʲ 17% (2%), ɤ 13%, ä 12%, ɘ 10%.** The vowels come from the proto draw. With the series draw, a proto without a long-vowel or nasal-vowel series fills all its vowel slots with distinct qualities, so rarer qualities enter. In human proto draws ɑ is 0.18 against 0.10 on base code. History then spreads them through big families.
    - The fix I would try next: draw the vowel count after the vowel series, or let the free vowel picks take a long or nasal partner of a chosen quality even without the series, as PHOIBLE's counts include those.
    - lʲ is mostly one big family (16 living lects from proto p286) plus S221.
  - Fixed on the way:
    - prenasal stops: 43% of living lects → 27% (S142 weight 3 → 1);
    - tʷ and lʷ: no longer overused (S068 weight 2 → 1);
    - S221 (secondary palatalization) now fires before i only, at weight 1.
- **Five-tone systems are still the commonest** among tonal living lects (53%; base 85%). Protos are fine: tone counts 2-5 are 28/31/23/18%. History adds contour tones on short vowels (tonogenesis rows), and nothing merges tones back. This is "tone evolution", task 4, not done.
- **Line preferences are keyed by proto id** (`hiatus_key`), so two runs with the same proto ids share them. That is harmless within a run.
- **Paradigm cells don't run the live rules.** Grammar paradigm cells (`grammar.py`, grammar A's file) don't apply them yet. Only new coinages, derivations, compounds, loans, names (`realize`) and sentences do.
- **Viewer speech uses the selected lect's stress** pattern. Per-word stress is not stored.

## Names & spelling lane (2026-11-08)

### Choices made for you (reasonable guesses)
1. **Purr is spelled `vr`** (was `rr`, the same as the trill). Growl stays `rh`, second voice `wh`, sub-bass `mh`, ultra
   `ih`. One table: `romanize.NH_MARKS`.
2. **Book mode keeps 2 diacritic letters per language** (the commonest by word count); others fold to plain letters in
   every word. A fold that merges nothing (ṭ when there is no t) always happens. `romanize.BOOK_DIACRITIC_BUDGET`.
3. **A dental beside its alveolar is t̮ d̮ n̮ l̮** (breve below) in the workbench spelling, since ḻ already means ɻ.
   Book drops it. `romanize._DENTAL`.
4. **A vowel with a small shift** (ɨ̠, e̞) is written as its plain letter; only if the language also has the unshifted vowel
   does it get a breve (raised/advanced) or macron below (lowered/retracted). `romanize._SHIFT_MARK`.
5. **Pinyin b/p** only when the language has no voiced stops and its aspirates are all voiceless stops/affricates
   (labial to velar). A language with voiced stops too (Hindi-like) keeps `ph th kh`.
6. **Clicks are the letters ǀ ǁ ǃ ǂ.** No Bantu `c q x` option yet.
7. **Multi-word names**: every word capitalized; a one- or two-letter particle joins with a hyphen (*Opa'i-e*, *E-Iva*).
8. **Pattern codes now match your taxonomy doc.** The generator's own labels live in a new `variant` field. My mapping:
   'old people, first settlers' -> E2 ('original people', as Lenni-Lenape); 'totem animal' -> E9 (custom); 'the many' ->
   E11 (Alemanni 'all men'); 'cave/mountain/sea people' exonyms -> X7 (dwelling as observed); scholars' name ->
   `scholarly`; relay -> X4. E4 'free/noble' uses MASTER (no FREE concept), for a people that ruled another in a shift.

9. **Naming traditions** (`personal.py`): given names dithematic 50% / sentence names 25% / one-word names 25%; bynames
   patronymic 35% / clan 30% / epithet 25% / matronymic 10%; a language changes one part of its parent's tradition 12% of
   the time. Theme pools, phrase list, epithets and clan words are short tables at the top of the file.
10. **Old names were coined about 4 kyr ago** in each language's line (`OLD_NAME_KYR`), so sister languages share them in
    different shapes; they wear down to two syllables with a chance up to 60% (`OPAQUE_CAP`, `OPAQUE_KYR` 8 kyr).
11. **Town names**: 3 per deme, largest first; a generic is worn to one syllable after 3 kyr (`SUFFIX_KYR`); a town kept
    from another people gets the newcomers' own generic added 25% of the time (`SUBSTRATE_TAUTOLOGY`).
12. **E10 faith names** fire rarely (weight 0.15 + 0.6 x the high god's individuation; `names.FAITH_W`).

### Worth a look
- About two thirds of the towns a24559's demes hold were founded by another people, so most town names are substrate
  names. That follows the settlement history; tell me if it looks too high.
- No living a24559 language has a genitive marker, so patronymics are compounds ('Lifingi-son'), not *Jónsson*-type
  genitives. They switch to the genitive automatically once the grammar gives one.

### Leftovers
- Names are not run through each language's own sound-change history; old names are approximated (see
  architecture.md section 13b).
- The language pages (sketch.py) are Markdown, so the names there have no play buttons; the viewer's Names tab has them.
  The finish lane's demo page could add them with its `play()` helper.
- E11 confederation and X6 dynasty/state names need polity or state data that does not reach the language pass yet.
  X9, P1, P3, P5-P7, glossonym drift, name length by tradition, river/peak tautologies, orthographic profiles: not started.
- Bilabial click ʘ is still spelled `px`.


## Grammar phase A (branch lang-gram-a, 2026-11-07)

Reasonable defaults taken while you were away. Each lives in one constant in `planet/language/grammar.py`.

- **Split ergativity kind**: by person (pronouns accusative, nouns ergative) 60%, by aspect (ergative in the perfective
  or past) 40%. `SPLIT_KIND`.
- **Inclusive 'we' source**: 'we + you' compound 45%, 'I + you' 15%, a root of its own 40%. Plain WE stays as the
  exclusive. `INCLUSIVE_FROM`.
- **Reduplication meaning and shape**: iterative 45%, intensive 20%, continuous 35%; CV copy 65% (prefixed 3 in 4),
  whole stem 35%. `REDUP`, `REDUP_SHAPE`.
- **Counting base words** at proto time: decimal 20 = 'two ten'; vigesimal 100 = 'five twenty' (20 = 'one person' half
  the time); 'other' read as quinary-decimal, 6-9 = 'five one' ... 'five four'. `NUMERAL_WORDS`.
- **Person paradigm**: each other pronoun joins a binding person marker with 60-85% (3SG lowest); gap fill 0.004 per
  generation. `PERSON_JOIN`, `PERSON_FILL`.
- **Degrammaticalization**: 1/50 of the fusion hazard, x3 for NP-edge markers, x3 for the last survivor of a lost
  paradigm. `DEGRAM`, `DEGRAM_EDGE`, `DEGRAM_ORPHAN`.
- **Alignment shown as neutral when no accusative or ergative marker exists** (before, the aim showed through: 16% of
  lects claimed ergativity with no ergative anywhere). This is WALS 98A's reading (flagging). Head-marked ergativity
  (Mayan-style, on the verb) is not modelled, so it cannot be claimed.

**Measured** (living lects of a24559, scratch pass, before = same code base without phase A, same vocabulary):
accusative gram 10% > 40% of lects (49% of lects with case; Grambank GB408 44%); ergative 0% > 15% (17% of case
lects; GB409 22%); dual 5% > 10% (GB043 7.7%); ablative 0% > 10%; allative 5% > 9%; witnessed evidential 5% > 13%;
inclusive 'we' 0% > 54% (GB028 52.5%); verbal reduplication built in 74% (GB158 73%); one-of-six person paradigms
60% > 12% of agreeing lects; shown alignment neutral 52% (WALS 98A about 52%).

**Decision: verb synthesis (WALS 22A), measured, not tuned.** Bound verb categories per living lect (tense, aspect,
mood/evidential, negation, voice/valence, person; affix or fused):

| categories | 0-1 | 2-3 | 4-5 | 6-7 | 8+ |
| --- | --- | --- | --- | --- | --- |
| our lects (after phase A) | 59% | 28% | 12% | 1% | 0% |
| WALS 22A (145 languages, from memory, about) | 3% | 17% | 36% | 21% | 23% |

Our languages are far more isolating than the world's. Cause: fusion is slow against 20 kyr with a median adult-learner
share of 0.54 (`FUSE`, `social_factors`), and the categories list is short (no object agreement or mood yet: phase B
adds some). My recommendation: wait for phase B (object agreement, mood) and re-measure; if 0-1 is still above ~25%,
raise `FUSE` from 0.012 toward 0.02 and check the L2 exponent on fusion ((1 - l2)^2), rather than adding categories by
hand. Your call.

**Odd or worth a look:**
- Passive is already 45% of lects before and after (GET and BECOME from round 5 feed it; G060 adds a few). The brief
  said 20-40%; WALS 107A has about 44% with a passive, so I left it.
- 77% of ergatives come from the agentive 'near, with' path (X22), because a lexical source is always at hand while the
  gram sources (instrumental, ablative, locative) need a live gram. Plausible but lopsided; lower X22's weight if you
  want more case-syncretic ergatives.
- No genitive gram ever arises (0%): no lexical source in the vocabulary (G067 needs BELONG). Phase B item.
- Degrammaticalization fires about 1.6 times per lect over 20 kyr in the isolated harness (61% of lects have at least
  one), mostly articles, accusatives and plurals. At the asked 1/50 rate, but probably more than real (Norde collects a
  few dozen cases). `DEGRAM` is one constant.
- Split ergativity is shown in 7% of lects (6% by person, 1% by aspect); aspect needs a live perfect or past.
- The lexicon's own compound recipes build 6-9 as 'five + one' ... and 10 as 'hand + two' in lects whose counting base
  is decimal (seen in d21). Quinary-built digits in a decimal system are real (many languages), but it ignores the base
  feature; the recipes in data/compounds.tsv could be gated on `numeral_base` later.
- Sample sentences (task 8): every lect's imperative is the bare stem, because no mood gram exists yet (phase B's mood
  item will vary it). The 1PL agreement marker came from the old 'we', so in a lect with clusivity it sits beside the
  inclusive pronoun unchanged ('u fish muh-eat'): plausible (many languages have one 1PL agreement), but clusive
  agreement is not modelled. The give sentence uses the dative only when a DAT gram lives; otherwise a serial or a
  double object, never a locative or allative recipient (a reasonable default; Basque/Latin-type dative-as-allative
  syncretism is not shown).
- Demo candidates: d191 (split ergativity by person, VSO: 'see-3SG ERG-man DEF ACC-1SG'), d10 (inclusive/exclusive),
  d1 (whole-stem continuous reduplication), d2 (serial 'take ... come'), from the scratch pass, not the shipped run.


## Grammar phase B (branch lang-gram-b, 2026-11-08)

### Demo-page bugs fixed (the full read of the 11-08 demo)
Each was fixed where it arose, with a test where the fix is mechanical:
- **Merchants glossed as things.** Role and trade nouns (merchant, soldier, teacher, thief, king, servant and so on)
  had no semantic field that says 'person', so they took the 'abstract' class. They are people now.
- **Class numbers with gaps and twins** (tabaxi: no class 1, two class 3s). The engine gave a new class the number
  "count + 1", so after a class was lost the next one took a number still in use. It now takes the next unused number,
  and the pages number classes 1..n.
- **The dual named in prose but missing from the examples.** The page showed only two examples per note. It now shows
  up to four, and the Number note has a 'two dogs' example with the dual.
- **The correlative note quoted 'sings' for a 'dance' sentence**, and **the 'have' note said dog for a boat sentence.**
  Both now quote their own sentence.
- **Classifier examples without the classifier.** A free classifier is now shown after a numeral ('two CLF dogs'),
  and a free class marker in a bound system stands beside its noun. The example noun is not the marker's own source
  noun when another will do.
- **Prose forms that differ from the examples** (cloud giant PST iŋ vs in=, human e̞˧ʔ vs =je̞˧ʔ). The joining rules
  change a marker next to its neighbour. The note now names both: "(e̞˧ʔ; je̞˧ʔ after a vowel; from …)", "(iŋ; in
  before a stop)", or "where it has merged with the stem" for a stored word form.
- **ᴖ in IPA.** It is not a leak: it is the house mark for a second simultaneous voice (the avian syrinx), from
  `symbols.tsv`. In this pass only aarakocra and kenku lects have it. The kobold case would have been an old root
  reconstructed from an avian ancestor. Each language section now has a key for any non-IPA mark it shows (‼ ᵣ ᴖ ˯
  ˰ ʞ).
- **'Felt' word families whose members do not share the root.** The lexicon keeps a felt root on a word after its
  form has drifted away (aarakocra 'knee' wja˦ under 'head' le˧). The pages now list a felt family member only if the
  root can still be heard in it. The lexicon's own `roots` field is the lexicon lane's (lexicon.py), so its data are
  unchanged.
- **A language listed as its own ancestor** (a split that kept its deme carries the same name). Such stages are now
  folded into one. **The sea elves were "an elvish language" while descended from a gnome proto.** The elvish and
  dwarvish picks now need the people's own proto-language.
- **The relatives line dropped percentages.** The file keeps intelligibility only from 5% up, so a missing value
  now reads "under 5% understood".
- **Mixed gram labels** (PAST/PST, PERF/PRF, EVID.REP/REP): the complexity tab now uses the gloss labels too.
  **"Likely cause." with a lowercase sentence** is capitalized. **Tool and agent jargon** is gone from the pages
  ("(sketch.py)", "the lane picked…", bare "G055"/"G056", `cx`, the file-name footer). Path ids stay in the code.

### Engine: what phase B added, with the defaults I chose
- **Mood grams.** Four new functions, from the written paths and a few built-in ones:
  - IMP (imperative);
  - HORT ('let us': G034 'let, leave'; 'come, go'; 'give' as Russian *davai*);
  - OBLG ('must': G007 'have', read as HOLD);
  - APPR ('lest': G035 'fear').
  - The imperative's own sources are my guess, since the catalogue has none: an attention word 'look!, come!' (X29),
    or a hortative widened to commands (X30). Most languages use the bare stem (WALS 70A), and the bare stem stays
    the default.
  - None of these has a typology feature, so they come with the ordinary recruitment draw, with no pull.
- **Object agreement** (1SG.O … 3PL.O, glossed 1SG.OBJ). It comes from the object pronouns (Givón). One lead path
  (3rd person 'him/her' > 3SG.O). The rest of the series binds with it as a set, like subject agreement (`SERIES`,
  `PERSON_JOIN`). The `object_agreement` aim pulls it. Its side follows the aim (prefix/suffix), and
  `realised_value('object_agreement')` now reads the live grams.
- **The genitive has sources now.**
  - Ablative > genitive (X31, Latin *de* > French *de*).
  - A demonstrative linker (X32, Albanian, Persian ezafe).
  - A case language is pulled toward a genitive of its own (`PULL_GROUP['GEN']`).
  - Patronymics will switch to the genitive automatically where one exists (names lane).
- **The inclusive 'we' in agreement.** A 1PL.INCL marker joins a binding subject series when the lexicon has an
  inclusive 'we' (join chance 0.7, `PERSON_JOIN['INCL']`). The old 1PL marker is then the exclusive.
- **Possessor marking on the possessed noun** (1SG.POSS …, slot after number and before case, as Turkish
  *ev-ler-im-de*). The lead path is 'I' > 1SG.POSS (X39), and the series binds as a set. Its side follows the
  genitive order. There is no typology feature for it, so the ordinary draw brings it.
- **'Set' paths** (frequency class `set`, weight 0). These paths are never drawn on their own; only a series' set
  binding uses them. Without them, twelve more pronoun paths would dilute the draw for every other target.
- **Sentences.**
  - The imperative takes IMP where it lives.
  - New 'Let us eat the fish!' (hortative) and 'The woman sees you.' (object agreement).
  - Every transitive clause puts the object's marker on the verb when it is bound.
  - The 'we (you and I)' sentence uses 1PL.INCL.
  - Possessed nouns carry the possessor marker, and the possessor pronoun is dropped in pro-drop lects.
  - New notes: Object agreement, Possessor marking. Mood markers go under "Mood and evidentiality", and the Commands
    note names the imperative marker.

### Measured (isolated-lect harness, 300 human protos, ~20 kyr, before = lang-design 7f10e12f)
| | before | after | reference |
| --- | --- | --- | --- |
| genitive gram (any / bound) | 0% / 0% | 63% / 27% | (no single figure; most case languages mark the possessor) |
| object agreement shown | 0% | 51% (suffix 34%, prefix 18%) | GB093 34% suffix, GB094 22% prefix |
| object markers bound, of lects with any | n/a | median 3 of 6 | n/a |
| possessor markers (clitic or tighter) | 0% | 19% of lects | GB430/431: roughly a quarter to a third |
| inclusive subject marker (any) | 0% | 32% of lects (of 57% with an inclusive 'we') | n/a |
| IMP / HORT / OBLG / APPR (any) | 0% | 17% / 39% / 30% / 19% | WALS 70A: 78% have a dedicated imperative (this counts the bare stem against a marked indicative, too) |
| verb synthesis 0-1 bound categories (WALS 22A bins, harness) | 37% | 25% | about 3% |

**Full pass** (a24559, 620 living lects; before = phase A's final pass on the same base, after = this branch):
- genitive gram 0% > 56% (14% bound);
- object agreement shown 0% > 35% (suffix 19%, prefix 16%; Grambank 34% and 22%);
- possessor markers (clitic or tighter) 0% > 8% of lects;
- inclusive subject marker 0% > 17%;
- IMP 11%, HORT 26%, OBLG 16%, APPR 8%;
- verb synthesis, WALS 22A bins: 0-1 categories 58% > 55%, 2-3 28% > 26%, 4-5 13% > 15%, 6-7 1% > 4%, 8+ 0%
  (WALS about 3 / 17 / 36 / 21 / 23%).

The full pass moves much less than the harness. Most living lects carry a high adult-learner share, and new grams
stay free words there.

Checks:
- all pass except the scholars' horizon, which reads 11.0 kyr for human lects (phase A's pass: 16.0). Another lane is
  on it. This branch changes no sound or lexicon code, so the move is run-to-run variation plus the grammar's effect
  on intelligibility.
- "Typology agrees with the live grams" is ok.

**Synthesis (your decision, not tuned).** Mood and object agreement add bound verb categories. The harness's 0-1
bin falls from 37% to 25%, but the full pass only from 58% to 55%, against WALS's 3%. So adding categories does not
close the gap: the grams exist but stay free.

Phase A's advice stands: the lever is `FUSE` (0.012 → about 0.02) and the L2 exponent on fusion ((1 - l2)^2). I did
not touch FUSE.

### Odd or worth a look
- The genitive is now common (63% of harness lects, about half of them still a free word, an adposition). That
  follows from the pull. Lower or remove `PULL_GROUP['GEN']` if you want fewer.
- HORT (39%) outnumbers IMP (17%). This is plausible, since many languages have a 'let's' particle and a bare-stem
  imperative, but it rests on my guessed IMP sources.
- Possessor marking has no aim behind it, so its share is set by the draw alone.

### Demo page
- The regenerated demo (not published; the coordinator publishes it) uses this branch's pass of a24559 with the
  sentences and notes rewritten by today's sentences.py (`demo_page.py --re-enrich`, new).
- After the pass I fixed two small note slips:
  - an inalienable note said "no marker" beside a possessor marker;
  - 'I' was written as 'i' in "from 'i'".

### Not done (left for the next grammar lane)
- **Concord** (item 8): class or gender markers copied onto adjectives, demonstratives and the verb.
- **Constructions as grams** (item 10): Q, COP, REL, COMP, FOC. These are still lexical stand-ins, and the notes
  say so in plain words now.

Both are queued in grammar-gaps.md (phase B progress).

## Lexicon & contact lane (lang-lexcon, 2026-11-08)

**What changed, in plain words**
- **Loans follow the contact and the meaning.** Each neighbour pulls on a lect's words by contact × prestige slope, plus the share of the deme already shifting toward it. The sum is the contact intensity. Loans are about 5% of replacements under casual contact and up to about half just before a shift. Each meaning's chance of being borrowed is scaled by its WOLD borrowed score, steeply under light contact and gently under heavy contact (Thomason & Kaufman's scale). Pronouns, numerals, deixis and question words never fall back to a loan; they keep their old word.
- **Numerals are systems.** Each lect counts in one system read from its grammar's counting-base label: decimal (some with 6–9 as five-plus), vigesimal or vigesimal-below-a-hundred, a five-based system, or a restricted one (1–3, then 'two two', 'one hand', 'one person', 'many'). Teens and tens (ELEVEN, TWELVE, FIFTEEN, THIRTY, FORTY) are new concepts, always built by the system. A composite numeral is re-formed from its current parts when its word is renewed.
- **Colour terms by Berlin & Kay stage.** A proto starts at a drawn stage (I–VI) with composite categories as one word. A composite splits over time in the B&K order; the new word comes from an object word ('grass-like', 'sky-like', 'earth-like') or a loan from a neighbour that has the term. Colour words no longer merge by CLICS shifts.
- **Kinship systems.** Each proto draws one of Hawaiian, Eskimo, Iroquois, Sudanese, Crow or Omaha; its kin share words accordingly. New concepts: FATHER'S BROTHER, MOTHER'S BROTHER, FATHER'S SISTER, MOTHER'S SISTER, PARALLEL COUSIN, CROSS COUSIN. Systems drift slowly to a neighbouring type. Descriptive (Sudanese) terms are compounds ('mother-brother', Swedish morbror).
- **Nursery words and sound symbolism.** MOTHER mostly with a nasal and an open vowel (mama, nana), FATHER mostly with a labial or dental stop (papa, tata). Mild Blasi et al. 2016 links (NOSE n, TONGUE l, SMALL i, ROUND r ...).
- **Substrate after a shift** keeps 10–30% of the local words (drawn per shift) plus all names, not all of them. The accent replaces 80% of the missing sounds (was 50%), and the stress system carries over. Calques come only from features shift interference is known to move (word order, aspect, evidentials, articles ...), never gender or case.
- **Areal diffusion.** A lect copies a typology feature from a contact lect now and then, weighted toward the areal features (articles, future, evidentials, classifiers, polar questions, order). The log is in each lect's `systems.areal`.
- **Words that come with a technology.** Bread, beer, cheese, wine, mead, spirits, vinegar, oven, quern, sugar, steaming, pickling, yeast, griddle, fish sauce, porridge, dough and curd appear when the people knows the technology (the techtree). Learned from a neighbour, the word mostly comes with it (a Wanderwort). BREAD and BEER had no way into any lexicon before. Taste words (TASTE, TASTY, FRAGRANT, STINKING, PUNGENT, BE HUNGRY, MEAL, FEAST) are new proto concepts.
- Tidy-ups: ROAST merged into ROAST OR FRY; the nagybátya gloss fixed; `Concept.base` now feeds borrowability; mountain and cold elaborations reachable (deme elevation, latitude); the unused `niche_weights_from` removed.

**Defaults taken (your call when you are back)**
1. **Loan levels.** LOAN_CONTACT 0.1, LOAN_MAX 1.0, the steepness of the borrowability curve (gamma 1.5 → 0.5). Change in `history.py` / `lexicon.py` (top of the borrowability section).
2. **Numeral system weights inside the grammar labels.** "other" is 60% restricted, 40% five-based; restricted becomes five-based in a people past 20,000 speakers. The grammar's label distribution itself (about 28% "other" in the final run) is grammar A's; WALS has about 10% restricted.
3. **Proto colour stages** (weights in `lexsys.STAGE_WEIGHTS`) and the split rate `COLOUR_SPLIT`. Tuned by eye, not to the World Color Survey.
4. **Kinship weights** are Murdock's Ethnographic Atlas shares from memory (≈). Crow and Omaha are shown only on the cross cousin (one concept), not on the full skewing. The culture's descent and clan exogamy do not yet steer the draw.
5. **Areal rate** AREAL_K 0.0015 per generation × contact × prestige slope.
6. **Two test thresholds moved** (lexicon tests): the homophone share's one-run maximum 0.24 → 0.25, and the proto core-vs-all derivation margin 0.05 → 0.04. Both are diluted by the new system concepts, explained in the tests.

**Weirdness noticed**
- Hawaiian-type lects call cousins by the BROTHER word only; there is one word per sibling sex, and the sex split of cousins is not modelled.
- A colour or kin category changes its word only when its focus (WHITE, GREEN, FATHER ...) is renewed; a hit on a non-focus member is kept.

### Pass 2 (lang-lexcon, 2026-11-08)

**Your call when you are back**
7. **How to read the scholars' horizon.** The check takes the first two 2-kyr windows in a row where fewer than half of the true splits are recovered. Past 10 kyr each window holds only 3-6 splits and recovery hovers near one half, so one split more or less moves the reading by about 6 kyr: the same code reads 10.7 or 17.6 on two seeds, and a bootstrap of the shipped run spans 9.7-16.7. A logistic fit of "recovered" against split age, with every split counted once, stays put (17.9 and 17.1 on those two seeds). It is now reported beside the old reading as `human_logistic`; it does not decide pass or fail yet. My recommendation: make the logistic reading the check's value. The other option is a median over three pass seeds, which costs about 1.5 hours of compute per measurement.
   - On the logistic reading the human horizon was about 13.5 thousand years before this lane, about 17.5 after pass 1, and **12.8 now**. The 6-10 target was never met on a robust reading; the shipped 10.7 was a lucky draw.
8. **Fresh roots for meanings nothing can renew** (`lexicon.KEEP_COIN`, `KEEP_COIN_FREQ`). Round 5 let a replacement that no source could make keep the old word. Frequent meanings with no derivation, compound or semantic shift (EGG, STAR, LEAF, SLEEP, FISH) were therefore renewed only by loans. With little contact they never changed: 83-92% of them kept the proto word for 12 thousand years. Such a draw now takes a fresh root (a word of unknown origin) for frequency classes 1-2. Pronouns, numerals, deixis and question words still keep their word.
   - Fresh roots are 4.6% of replacements in the full pass, up from 2.9%.
   - The Swadesh rate is held by `KEEP_COMPENSATION` 1.08 → 1.0. The full pass replaced 16% of the human core per thousand years at the old value.
   - The coinage test bound moved from 6% to 8% (reason in the test).
9. **Kinship follows the culture's marriage rules** (`lexsys.KIN_PULL`). Clan exogamy weights Iroquois, Crow and Omaha by 2. Cross-cousin marriage weights Iroquois by 3 and Crow and Omaha by 1.5. A culture with neither weights Hawaiian and Eskimo by 1.5. A disfavoured system changes up to 3 times faster. These weights are my reading of Murdock 1949, not fitted.
   - a24559's stored taboos.json predates the kinship and speech rules, so the pass re-derives it in memory (read-only) with the lineages code.
10. **Name taboos speed word loss** (`lexsys.SPEECH_TABOO_X`): +30% on the open-class replacement rate for "words like a dead person's name" and +20% for the ruler's name. Dixon describes the effect in Australia as large but gives no rate, so these numbers are guesses.
11. **Avoidance registers.** Where the culture has the mother-in-law or in-law word rules, the living lect gets a second word for 20 everyday meanings. Half are a neighbour's word, as Dyirbal Jalnguy often is; the rest are paraphrases ('the black one') or derivations. They are built for today only: they are not inherited and have no sound-change history. They appear in the sketches under "Avoidance words".
12. **Areal rate ×10** (`AREAL_K` 0.0015 → 0.015). See the pass-2 numbers in calibration.md for whether the near/far signal appears.

**Changed in the sound lane's files (minimal, flagged)**
- New rule S218 (now S226: the sound lane already used S218-S225): the labialized coronals tʷ dʷ nʷ sʷ zʷ lʷ rʷ lose their labialization. nʷ had a source (S068, labialization before a lost rounded vowel) and no way out, so it built up to 10.5% of lects; PHOIBLE has 1.2%. It is now at 1.7%.
  - I did not check one attested case. The rule rests on labialization being commonest on velars and uvulars (Ladefoged & Maddieson 1996).
- Backness harmony in `rules._produce`: a front e going back now opens to ɑ, as in Turkish -ler/-lar and Hungarian -nek/-nak. Before, it became ɤ, and a rounded o after an unrounded back root also unrounded to ɤ. ɤ reached 11.7% of lects on one seed (PHOIBLE 2.2%) and is now at 1.0%. Central ə and ɐ are neutral.
- `lect.py` passes two more context values to `lexicon.step`: `kin_weights` and `speech_taboo`.

**Odd output noticed**
- The overused-segment check also swings with the seed: one seed failed on nʷ, the other on ɤ. Both are fixed at the cause.
- The counting base now drives the numeral words directly. Grammar A's proto numerals and the lexicon's numeral systems used to build twenty and the rest separately, and the lexicon's overwrote grammar A's. A decimal lect no longer renews six as 'five one' (`lexsys.recipe_fits`).
- The sentence lane's numeral note still builds 11/15/30/40 as phrases even where the lect has its own word for ELEVEN or THIRTY.

**Not done**
- Liturgical language and god names from gods.json (contact-gaps rec. 5).
- Segment borrowing at high contact intensity (contact-gaps 3d).
- Polities: they need a polities document in the run.
