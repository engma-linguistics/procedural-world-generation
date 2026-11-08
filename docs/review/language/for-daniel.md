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
- **Languages demo page** (version 3, 11-08: grammar C, 10 languages, 308 audio clips, complexity tab; a full read's remaining slips are listed in demo-read-3.md and are grammar D's first item): https://claude.ai/artifact/GQUxhWHnErqn3zx7MTaFUs (private). Live viewer: `uv run python -m planet langserve a24559 --host 0.0.0.0 --port 8790`.

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
- New rule S218: the labialized coronals tʷ dʷ nʷ sʷ zʷ lʷ rʷ lose their labialization. nʷ had a source (S068, labialization before a lost rounded vowel) and no way out, so it built up to 10.5% of lects; PHOIBLE has 1.2%. It is now at 1.7%.
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


## Grammar phase C (branch lang-gram-c, 2026-11-08)

### Fixes from the read of phase B's demo
Each fixed where it arose:
- **Object-agreement examples on 'go'** ("he goes us"): the examples now take a transitive verb (see, eat, hit, hold).
- **One verb, two stems** (kenku oː˧l vs u˦toː˧) and **plural stems that are not the noun** (gnome li-tej-nep for tuj):
  a stored paradigm cell whose stem part is not today's stem has unreliable morph boundaries after thousands of years
  of sound change. Such a cell is now shown as one unsegmented word with a fused gloss (tejnep 'dog.PL.M', as English
  mice 'mouse.PL'), and the regular cells keep their breaks.
- **Reduplication examples that were not copies** (red dragon kaː-ʔu‼iː, gnome nu-nep): reduplication is productive, so
  the page now always copies today's stem rather than reading the stored, worn cell.
- **"marked by the genitive a clitic"** now reads "the genitive marker, a clitic ..."; **"Dat is"** is DAT again (the
  note's first letter is raised, the rest left alone).
- **Numerals 30 'ten three' vs 11 'ten one'**: where multiplication puts the base first (numeral after the noun), the
  page joins addition with the lect's 'and' (11 'ten and one'), and every numeral example says its arithmetic
  ('ten three' = 3 × 10). The lexicon's own numeral words (lexsys, the lexicon lane's) are unchanged.
- **Imperative with an object marker while the note said "no person marker"**: the note says "no subject or tense
  marker" and adds "the verb still marks its object" where it does.
- **Trudgill's "small, isolated societies" for 309,717 speakers**: that cause now also needs a population in the lower
  half; an isolated but large community gets its own wording.
- **Ancestry lines**: a deme's earlier language is "older speech of human 20" when the deme appears again later, and a
  language shift is spelled out ("language shift: its speakers, fire giants, took up bronze dragon 8's language"); a step
  where the people changed without a recorded shift says so too.
- **Classifiers**: a system whose class markers have all worn away no longer prints an empty list; a free classifier
  is described as "a separate word after the numeral", matching the examples; the masculine class is described as
  "men, and by default most other nouns" (fish in the 'masculine' class read as "men and male things").
- **Felt word families**: a two-sound root is heard only at a word's edge, a longer root needs three of its sounds; when
  the root's own word is gone, a member must share three sounds (or its first two) with another member.
- **Jargon**: no "of run a24559", "the window read", "the file does not keep them per frame" or "language d674" left.
  The non-IPA mark key now also sits in each complexity card whose forms use a mark (the kenku ᴖ was first seen there).

### Engine and pages: what phase C added, with the defaults I chose
Each default is one constant in `planet/language/grammar.py`.
- **Concord.** While a class marker is bound (clitic or tighter), class agreement spreads to demonstratives, adjectives
  and the verb, one at a time (weights 1.0 / 0.7 / 0.5, Corbett's Agreement Hierarchy), at `CONCORD_GROW` 0.02 per
  generation; each target goes again at 0.0005. The verb's agreement is Bantu-style: the subject's class marker stands
  in the third-person slot. The copied marker has the noun marker's form (alliterative concord); real systems often
  have separate agreement forms, which this does not model.
- **Constructions as grams.** Question particle from 'if, whether' (Russian li) or a negator (Mandarin ma); copula from
  a demonstrative (G056), a third-person pronoun (Hebrew hu) or a posture verb (Spanish estar); relativizer from a
  demonstrative or 'who, what' (G055, G058); complementizer from 'say' (G023) or the relativizer; topic from 'if,
  when' (Haiman 1978) or a demonstrative; focus split off the copula (G057). Polar question and copula are now read
  from the grams, as case and number already were. A free or clitic question marker counts as a particle, a bound one
  as verbal morphology.
- **Copies, not reanalyses.** Copula > focus, reflexive > reciprocal and > antipassive, comitative > applicative and >
  same-subject, locative > different-subject, relativizer > complementizer leave the source gram in place (`COPY_PATHS`).
- **Inflection classes.** A bound number, case, tense, aspect or person marker gets a second form at 0.0006 per
  generation, taken from another source word of the same function (or a fresh small morph); 20-50% of words take it,
  chosen arbitrarily but fixed per word (a stable hash, never Python's). Levelling removes it at 0.0004.
- **Portmanteaus.** Two bound neighbours (number + case, tense or aspect + person) on the same side fuse into one
  ending at 0.0008 per generation; the two keep living alone. Syncretic markers (same slot, same form) are now kept half
  the time instead of always losing the rarer.
- **Stem change across the lexicon.** When a fused marker is worn to nothing but its cells still differ from the stem,
  its vowel changes become a rule: the pages apply it to any word in that category (dog\PL). It is applied where a
  word is inflected; the lexicon lane's files are untouched.
- **Infixes** only from vowel-initial verb prefixes (Yu 2007), at 0.003 per generation: rare by construction.
- **Second-position clitics**: 0.0015 per generation while the lect has a verbal clitic, x3 under free word order.
- **Noun incorporation** in head-marking lects (a bound object marker and 3+ bound verb categories), at 0.003.
- **Switch-reference** grams are wanted only in OV lects; **Austronesian voice** only in verb-initial ones, the patient
  voice from the passive, the actor voice from 'do' (my guess: the source of Austronesian *-um- is not known), the pivot
  marked by the old article (Tagalog ang), glossed PIV.
- **Antipassive** is wanted only in ergative or split lects (WALS 108A).
- **Complexity score**: free clause particles (a question word, a free copula) are left out of the mean binding level,
  so the new grams do not lower it.

### Measured
Isolated harness (300 human protos, ~20 kyr; before = lang-design 3d239669) and the full pass of a24559 (622 living
lects; before = phase B's final pass). Shares are of lects with the gram at all / bound (affix or fused).

| | harness before | harness after | full pass before | full pass after | reference |
| --- | --- | --- | --- | --- | --- |
| question gram (Q) | 0% | 62% / 26% | 0% | 49% / 9% | WALS 116A: about 60% particle, 17% verbal |
| polar question shown: intonation only | 43% | 38% | 42% | 51% | WALS 116A: about 14% |
| polar question shown: verb morphology | 10% | 26% | 6% | 9% | about 17% |
| copula gram (COP) / copula shown | 0% / 56% | 69% / 69% | 0% / 62% | 56% / 56% | GB117 57% |
| relativizer (REL) | 0% | 36% | 0% | 22% | (no single figure) |
| complementizer / topic / focus | 0% | 29% / 21% / 9% | 0% | 12% / 6% / 8% | |
| concord (any target) | 0% | 33% (70% of gender lects) | 0% | 20% (51% of gender lects) | gender is defined by agreement in Grambank |
| applicative / reciprocal / antipassive | 0% | 12% / 16% / 1% | 0% | 9% / 7% / 0% | WALS 109A ~45% applicative; 108A ~25% antipassive |
| switch-reference (SS or DS) | 0% | 13% | 0% | 3% | (Americas, New Guinea, Australia) |
| actor / patient voice | 0% | 2% / 1% | 0% | 1% / 1% | rare (Philippine type) |
| inflection classes | 0% | 27% | 0% | 9% | |
| portmanteau endings | 0% | 13% | 0% | 3% | |
| stem change across the lexicon | 0% | 5% | 0% | 8% | |
| infix | 0% | 1% | 0% | 0% | rare |
| second-position clitics | 0% | 17% | 0% | 10% | |
| noun incorporation | 0% | 9% | 0% | 4% | |
| verb synthesis, WALS 22A bins 0-1 / 2-3 / 4-5 / 6-7 / 8+ | 25 / 37 / 24 / 13 / 0% | 24 / 43 / 21 / 12 / 0% | 55 / 26 / 15 / 4 / 0% | 55 / 28 / 14 / 3 / 0% | about 3 / 17 / 36 / 21 / 23% |

Full-pass checks: all pass except the scholars' horizon (human lects), which reads **19.0 kyr** this pass (phase B's
read 11.0, phase A's 16.0); another lane is on it, and this branch changes no sound or lexicon code. "Typology agrees
with the live grams" is ok with polar question and copula now realised. 2062 s at 10 workers on a loaded machine.

**Synthesis (your decision, not tuned).** Still 55% of living lects in the 0-1 bin against WALS's about 3%. Phase C adds
categories (valence, voice, switch-reference) but in the full pass they are mostly free words, as phase B found: the
lever is still `FUSE` and the L2 exponent on fusion. I did not touch FUSE.

### Odd or worth a look
- **Intonation-only questions are 51% of the full pass** (WALS about 14%). The aims ask for a particle in about 58%
  of lects, but the pull is slowed by the adult-learner share and a free particle is often abandoned. Raising the
  pull for Q alone, or letting the lexical 'if' stand in when no gram lives (as before), would close it; I left it.
- **Antipassive is near 0%**: its only source is a live reflexive in an ergative lect. WALS 108A has about a quarter
  of languages with one. A lexical source would help, but I found none I could cite.
- **Concord copies the class marker's own form** onto adjectives and the verb (alliterative). Separate agreement forms
  (Swahili a- vs m-) are not modelled.
- **Gender is still shown without concord** in about half of gender lects (Grambank's definition requires agreement).
  Should `gender` read 'none' until concord reaches at least the demonstrative? Your call; it would cut the gender
  share by about half.
- **Infixes are vanishingly rare** (vowel-initial verb prefixes are rare, since recruitment keeps a word's onset).
- **The actor-voice source 'do, make' is my guess.**

## Faiths & contact pass 3 (lang-lexcon, 2026-11-08)

**What changed, in plain words**
- **Gods have names, and the names are words.** Each culture's up to four most important gods (the high god first) get a name in the language of the people who hold them, made from that language's own words: a bare domain word used as a name ('Sea'), a kin title ('sky-father', 'mountain-grandmother'), a rank title ('lord of the sky', 'chief of the river'), an agent noun ('the one who stands'), or a kenning ('roof of the world', 'the water-road'). The name is a lexicon entry (`name:god:<key>`, part of speech NAME), so it goes through every sound change the lect goes through, is inherited by daughters (sisters keep cognate names when the faith is older than their split), survives a shift as substrate, and is borrowed by converts from the people who converted them. The faith readout comes from gods.json; a24559's stored copy is older than faiths, so the pass re-derives it in memory (read-only, ~2 min).
- **Names get replaced by epithets** (the Germanic bear, 'the brown one'): a name has a half-life of 12 thousand years against a new epithet; avoidance titles ('the lord', 'the holy one', 'the old one') join the patterns there. The old name is in the new word's history.
- **Liturgical languages.** When a faith's holders learn temples (the techtree), the liturgy freezes the speech of the faith's seat at that moment: a copy of the lect that never changes again (`lit<faith>`). It holds a small sacred vocabulary (god, spirit, soul, holy, pray, sacrifice, demon, priest, temple, plus death, peace, true, song, sing, hear, give, we, light, feast) and the god names as they were. Three formulas are built from it with the grammar of that frozen stage: an invocation ('The lord, hear us!'), a praise ('Holy is the lord.') and a petition ('The sky-father gives rain.').
- **Learned loans.** Holders take sacred words back from their liturgy at a slow rate, as English took learned Latin beside its own words. Where the lect still has its own word the loan sits beside it as a doublet or synonym in a `learned` register; the sketches show it.
- **PRIEST and TEMPLE** are new concepts (with temples in the techtree): 'god-person', 'god-house', 'one who prays', 'place of praying'.
- **Segment borrowing.** Under heavy contact (intensity above 0.5) a loan can keep a consonant the receiver lacks, and the sound joins the receiver's inventory (as English kept /ʒ/ from French). At most 4 per line. Logged in each lexicon's `systems.seg_loans`.
- **River and lake tautologies.** A water name kept from a substrate language can get the new language's own word for river or lake added ('Avon river' type), when the two words differ.
- **The faith endonym (E10)** now uses the lect's own name for its high god ('the people of Mawidu (the sky god)').
- Output: languages.json has a new `faiths` block (holders, gods and their names per lect with glosses and when each was coined, the liturgy's words and formulas). The sketches have a "Gods and liturgy" section.

**Defaults taken (your call when you are back)**
1. **Four gods per culture** (`faiths.GODS_PER_CULTURE`), ranked high god first, then by devotion.
2. **Name half-life 12 kyr** (`NAME_HALF_KYR`). At 6 kyr, 72% of all names had been replaced by an epithet and 'the lord' was everywhere. Real god names can last 5-6 thousand years (Dyaus / Zeus / Jupiter), and many were replaced by titles (Baal 'lord', Adonai), so anything from 6 to 15 is defensible.
3. **The liturgy freezes at temples.** Liturgies are therefore up to ~6.6 thousand years old in a24559 (temples come early in its techtree). Real liturgical languages are 1.5-4 thousand years old (Latin, Sanskrit, Ge'ez, Church Slavonic). Freezing at writing instead would make them younger; there is no writing in the techtree that I could use.
4. **Learned loan rate** `LEARNED_RATE` 0.0025 per generation per sacred meaning.
5. **Kin titles give a god a sex** ('sky-father', 'earth-mother') that gods.json does not have; I drew it 50/50 (grandmother/grandfather the same). If a god should be sexless the kin patterns can be dropped.
6. **Separate families name a shared god independently at the start** (frame 0): when two unrelated peoples hold one faith from the beginning, each names its gods from its own words, so their names are calques ('sky-father' in both), not loans. Converts later borrow the name.
7. **Segment borrowing** `SEG_BORROW_MIN` 0.5, `SEG_BORROW_K` 0.15, `SEG_BORROW_MAX` 4. Consonants only.
8. **Petition gifts** per domain (`faiths.GIFT`): sea gives fish, sky and storm rain, mountain water, herd milk, war and smithing spears, death and ancestors peace. Mine, not from the data.

**Changed in the sound lane's files (flagged)**
- `history.take_segments` adds the borrowed consonant to the lect's `base_segs` and calls `lect._sync_inventory`. One call into lect.py; no change to lect.py itself.

**Odd output noticed**
- Many sister lects replace a name by the same kind of epithet ('the lord', 'roof of the world'), so a faith's god can be 'the lord' in four languages with four unrelated forms. This is plausible (Baal) but repetitive; it was much worse at the 6 kyr half-life.
- Faith names from gods.json read "the sky faith of first halflings of …" (the culture label). Not mine to change.
- gods.json has no myths, no god sex and no relations between gods beyond parent; I did not invent any. The kennings are chosen by domain from a small fixed table.
- Some god names wear down to one vowel ('A', 'I', 'Ì') after 15-20 thousand years of sound change. Plausible for a short word, odd for a god.
- A god whose domain has no word of its own borrows a neighbouring domain's word: a desert spirit is 'chief of the fire', a sun spirit 'lord of the sky'.
- **Segment borrowing is frequent.** In the final pass 205 of 618 living lects carry a borrowed-segment log and 142 sit at the cap of 4 (the log is inherited, so daughters of a heavy-contact lect share it); 266 of the 697 logged consonants are still in today's inventories, the rest were lost to sound change or folded away as rare. The areal inventory signal went from -0.004 to +0.003 (near minus far), so the effect on that check is still small. If this reads as too much, lower `SEG_BORROW_K` (0.15) or raise `SEG_BORROW_MIN` (0.5).

**Horizon (both readings, a24559, 8 workers).** p4 (god names and liturgy, half-life 6): window 12.0 kyr, logistic 13.2. p5 (everything here): window **4.3**, logistic **11.0**. The previous lexicon pass (p3): window 4.5, logistic 13.7. The check fails as it did before this lane, now on the low side of 6-10 (the window read is the noisy one; see item 7 of pass 2).

**Not done (task 4 leftovers)**
- River names through each lect's own sound-change history (they would need `name:river` words injected into the lexicons, like the gods).
- Peaks get no tautologies: peak names have no substrate path.
- X9 and the P-pattern names (P1, P3, P5-P7) not started.

## Grammar phase D and texts (branch lang-gram-d, 2026-11-08)

### Fixes from demo read 3
All fixed where they arose, the mechanical ones with tests (`test_third_read_fixes`, `test_demo_page_third_read_fixes`,
`test_sentence_spelling_is_the_book_spelling`).
- **Imperative and serial verbs drop case**: the imperative, the hortative and serial verbs now run the same flagging as
  any clause, so the object keeps its accusative and a transitive serial verb's subject its ergative.
- **Reduplication glide** (i-ji, u-wuk): a reduplicant now joins its base with no glide (u-ulo), as the rule text says.
- **Storm giant 'dog' with two stem shapes**: a stored cell is now used for the innermost markers it covers and any
  outer marker is added outside it, so the plural and the singular share one stem.
- **Trudgill wording**: "small" needs under 20,000 speakers and "few adult learners" an L2 share under 0.15; other
  communities get their own wording.
- **Felt families** ('middle' tahe̞/dahe̞, ilai/ilami-): I left them. They pass the phase C rule (three shared sounds or
  the first two) and look like real doublets. **Odd glosses** "seals (good)" now read "seals (trade good)".
- **Dangling comma in card names**: the card heading now names the region from the deme's name.
- **"1 families"**: number agreement.
- **Antipassive note** mentions the ergative only where an ergative exists.
- **Copula note vs sentence**: possession and predication go through one copula phrase, so a bound copula attaches in
  the sentence too; markers that share a conditioning context are told apart ("after a front or central vowel" / "after
  a back or rounded vowel").
- **Negation clitic after the verb**: the note now describes second-position clitics as such; "typology calls it" is gone.
- **Stranded ACC after wh-fronting**: the whole object noun phrase moves, case marker included.
- **"Fused" vs "suffix"**: a fused marker is described as "a suffix that fuses with some stems", and the forms list says
  "merged with the stem in X 'go.1SG'" where it has merged.
- **Storm giant word shapes**: the stem-vowel person is described in its own sentence ("the subject (2SG) is shown by
  the stem's vowel", with an example verb) and is no longer listed under "no marker yet"; portmanteaus get an example.
- **Kobold**: the possession note mentions head marking on the possessed noun; identical forms are named as such
  ("1PL.OBJ and 1SG.OBJ are both n"); a second (inflection-class) form now gets its own example.
- **Jargon**: "no question gram is tracked" is gone; "(no LOC gram)" now reads "(there is no locative case)".
- **PROG vs IPFV**: different English ("is going" vs "goes (ongoing or repeated)").
- **Spelling**: sentences now use the same book spelling as the Words table (one shared `orthography()`).
- **Minor**: ancestors are no longer listed as closest living relatives; populations in millions show two decimals;
  a form changed by sound change since an event is marked "reshaped by sound change"; a free person marker beside a
  full pronoun reads "short unstressed pronoun ... beside the full pronoun X".
- **Picker**: a new "newer features" demo slot prefers a language that shows applicatives, reciprocals, voice, infixes,
  incorporation, focus or concord, and the elvish, dwarvish and ergative picks prefer these on ties.

### Texts
- Every glossed text has four lines: book spelling, IPA, gloss, English.
- **The fable** (`planet/language/texts.py`): "The Bird and the Fish", six sentences, written for this (not a copy of
  Schleicher's), using only Swadesh-100 words so every proto-language can tell it:
  A bird sat in a tree. / The bird saw a fish in the water. / The bird said: "Come! I will give you a good seed." /
  The fish said: "I do not eat seeds. You will eat me." / The fish did not come. / The bird ate the seed.
  It is shown for a proto-language and two to four daughters from different branches (intelligibility to each other at
  most 0.5), side by side with audio, in its own demo tab ("A fable"), and in each sketch (the lect's version and its
  proto's).
- **A recipe** per demo language, as commands ("How to cook X": take, grind or cut, put in the pot, cook on the fire,
  eat with salt, it is good). X is the people's first crop from the food data, else its first herd animal, else fish.
- **The faith myth** (`texts.myth`, built after merging the faiths lane): "What the gods hold", told only from the
  data: each of up to three gods holds its first domain ('Oanga holds the fire'), the high god gives its domain's gift
  ('... gives us rain', faiths.GIFT), each divine food taboo becomes 'X holds the wild swine. We do not eat wild swine.'
  (taboos.json, the god matched by label; targets with no word, like eels, are left out), and it ends with the
  invocation ('X, hear us!'). gods.json has no creation story, sex or divine kinship (its `parent` is the god's descent
  across cultures), so none is told. Shown on the demo page and in the sketches beside the recipe.
- **Faith names**: the run names a founding culture "first tortles of the south of Simath" (planet/lineages/cultures.py
  line 430) and its faith "the sea faith of first tortles of ...". The language pages now print "the sea faith of the
  earliest tortles of ..." (`sketch.faith_label`); the cause is in the lineages code, not mine, and changing it would
  rename the stored cultures of every run.

### Phase D: what I added, with the defaults I chose
Each default is one constant in `planet/language/grammar.py`.
- **Distance in demonstratives** (DIST, X64): 'that' plus the first syllable of 'there' or 'far' (that-there > yon;
  Diessel 1999), only where the lect has 'this'. Kept like a question particle (`KEEP` 0.25).
- **Remote past** (REMPST, X65, from 'long', 'old', 'before': my guess at a source) beside a past tense; graded pasts are
  kept at `KEEP` 0.4.
- **Aspect**: completive from 'finish' (X66), inceptive from 'begin' (X67), iterative from 'return' or 'turn around'
  (X68).
- **Mirative** split off the perfect (X69) or the reportative (X70) (DeLancey 1997; Aikhenvald 2012).
- **Politeness**: polite address arises with population (`POLITE_MAKE` 0.002 x how large the community is; the peoples'
  data has no rank or class field, so size is the only social figure I could use). It takes the plural 'you' (70%) or
  the third person (30%) (WALS 45A); it is lost at 0.001 in small communities. An honorific verb marker (HON, from
  'king' or 'master', X71) is wanted only where polite address exists.
- **Comparison** follows the typology's own `comparative` aim (Grambank: exceed / locational / other); "other" splits
  into the particle type (likelier in VO lects) and the conjoined type. The exceed verb is 'climb' or 'jump' (a guess).
- **Differential object marking**: the accusative marks only animate objects, at 0.0015 per generation (x4 when the
  accusative came from a dative, as Spanish a and Hindi ko did), generalising at 0.0006.
- **Obviation** (OBV, from 'that' or 'other', X72: a guess, the Algonquian source is unknown) only where the verb
  marks both subject and object.
- **Polar questions**: the aims' pull toward a question particle is 3x the ordinary pressure, a wanted free particle is
  abandoned at a quarter of the usual rate, and 'what' is a new source (X73, Polish czy).
- New sentences: distance, remote past, aspect, mirative, polite request, comparison, obviation; new notes:
  Demonstratives, Polite address, Comparison, Obviation, and DOM in the Case note.

### Measured
Isolated harness (300 human protos, ~20 kyr, `sim.py` from phase C) and the final full pass of a24559 (after merging
the faiths lane: 612 living lects; "before" = phase C's final pass, 622 living lects).

| | harness before | harness after | full pass before | full pass after | reference |
| --- | --- | --- | --- | --- | --- |
| polar question: intonation only | 39% | 32% | 51% | 36% | WALS 116A: about 14% |
| question gram (Q), any | 61% | 68% | 49% | 64% | about 60% particle + 17% verbal |
| far demonstrative (3-way distance) | 0% | 31% | 0% | 16% | WALS 41A: 3-way about 37% |
| graded past, of lects with a past | 9% | 20% | (not measured) | 11% | WALS 66A: about 30% |
| completive / inceptive / iterative | 0% | 22% / 8% / 10% | 0% | 8% / 6% / 6% | (no single figure) |
| mirative | 0% | 8% | 0% | 6% | WALS 77/78 area: rare as a gram |
| polite address (plural / third person) | 0% | 14% / 5% | 0% | 16% / 14% | WALS 45A: 24% binary + 10% more |
| honorific verb marker | 0% | 2% | 0% | 1% | rare (Japanese, Korean, Tibetan) |
| comparison: locational / exceed / particle / conjoined | none | 20 / 31 / 24 / 25% | none | 18 / 34 / 20 / 28% | WALS 121A: 47 / 20 / 13 / 20% |
| DOM, of lects with an accusative | 0% | 17% | 0% | 8% | common in accusative languages (Bossong) |
| obviative | 0% | 3% | 0% | 1% | rare (Algonquian, Kutenai) |

Scholars' horizon (human lects), not chased: window reading 12.0 kyr, logistic `human_logistic` 13.3 kyr (the
pre-merge pass of this branch read 17.0 / 14.7: the window reading swings, as noted before); still FAIL on the window
reading. Other checks all ok as before.

### Odd output
- **Far demonstrative worn back into 'that'** (red dragon on the demo: 'that' tɛ˨˦ɨ˨ and the far one tɛ˨˦ɨ˨): the
  reinforcing syllable eroded away, so the two distances now sound alike. Real systems do merge this way; the page
  reports it as it stands rather than hiding it.
- **Full pass vs harness**: far demonstratives (16% vs 31%) and graded pasts (11% vs 20%) are half as common in the
  full pass as in the isolated harness; contact and adult learners strip optional free words. Below WALS on both; I
  did not chase it further.
- **Comparison shares**: locational is 18% (WALS 121A 47%) and exceed 34% (20%), because the construction now follows
  the typology's Grambank-drawn `comparative` aim; that draw (GB265/GB266) was there before phase D. Changing it is a
  one-line prior change if you want WALS shares.
- **Recipes on crops**: "How to cook cane" and "How to cook alliums": the staple is the people's first crop, whatever
  it is; a cane recipe that says "grind it with a stone" is plausible but odd.
- **Proto fables without a locative**: a proto-language with no case or adposition says 'bird tree sit-PST' for "A bird
  sat in a tree"; that is honest, not missing.
- **Polite note** says "It grew in a large society, where rank is marked in speech": the only social figure the model
  uses is population, so "rank" is my gloss, not data.

### Species leanings (a proposal, not applied)
Per-people multipliers on existing rates, the way kenku lean tonal. All are suggestions for you to accept, change or
drop; none is in the code. Only traits the lineage data already holds are used (lifespan, generation length, body).

| people (by a trait the lineage data holds) | lean | multiplier | why |
| --- | --- | --- | --- |
| long generations (elves, dragons) | evidentials and mirative kept | EVID/MIR recruitment x1.5, loss x0.5 | flavour: long memories and witnessed events |
| long generations (elves, dragons) | conservative morphology | erosion and fusion x0.7 | long generations already change less per kyr; this would add to it |
| voice profile with a wide pitch range (kenku, already tonal) | reduplication | REDUP x1.5 | flavour: sound-copying |
| short generations (goblin-kin, kobolds) | faster grammaticalization | recruitment x1.2 | already happens per kyr through generation length |
| everyone else | none | x1 | the baseline |

My own view: the rows are flavour on top of mechanisms that already exist (generation length, population size). I
would apply at most the first, and only if you want elves and dragons to feel different in their grammar.

## Polish lane (lang-polish, 2026-11-08)

Fixes for every item of `demo-read-4.md`, at the cause where there was one. Numbers and the full pass: see the end of
this section (filled in after the pass).

**Defaults taken**
1. **Paradigm repair, not a veto** (`lexicon.core_repair`). Sound change may still merge two pronoun cells, two numerals,
   two question words or this/that, but the very next lexicon step renews the more marked one: plural before singular,
   3rd before 2nd before 1st person, a composite numeral before a simple one, WHO before WHAT, far before near. The
   renewal tries, in order: the counting recipe, a reinforcement ('we others' as Spanish nosotros, 'you all',
   'that one' for he/they as French il, 'ten tens' for 100 as Gothic taihuntaihund, 'what person' for who), a loan
   from a contact language (English they), a derivation, and only last a new word of unknown origin. Left open on
   purpose: thou = you (English) and he = she (Finnish hän). I chose an immediate repair rather than a sound-change
   veto because the veto lives in the sound lane's rules.py and because real paradigms do merge and then repair.
2. **T-V only with a distinct polite form.** Polite address is not created where the polite form ('you all' or 'they')
   sounds like plain 'you', and it is lost (the English way) if they later fall together.
3. **Numerals:** an addend stands on the other side of the base from a multiplier, so 12 and 20 never meet (they did
   in 83 of 612 living lects: an NNum lect said 'ten two' for both). The numerals note now quotes the lect's own
   number words and its counting system's recipes, so it agrees with the word lists.
4. **One faith, one pantheon.** A faith's gods are its founding (seat) culture's, topped up with the gods most holders
   share; every holder names exactly those. The myth's food taboos are the faith's own, most characteristic first, so
   two faiths with swine and carrion-bird taboos lead with different ones. Gods, their names and spirits are persons
   for noun classes. God names are spelled in the book register (no tone marks).
5. **The fable** now uses an ancestor last spoken 3-6 kyr ago with 2-4 daughters (nearest age when none fits), and the
   page says how long ago it was spoken.
6. **Book spellings:** the letter-separating guard inside a word is now a middle dot (irh·ll), as Catalan l·l, so it
   does not read as an affix break; a word that would be spelled null / none / undefined at its end is re-spelled
   (nulh).
7. **Notes from the forms:** a stored paradigm cell whose stem differs from the dictionary form is now segmented from
   the forms (stem + marker, ∅ for a marker with no sound, or the stem's changed shape with a note) instead of being
   shown unsegmented and called 'merged with the stem'; 'the verb carries the subject's 3SG marker' is dropped where
   subject concord replaced it; a far demonstrative that sounds like 'that' or 'this' is not shown as a third distance,
   and the 'reinforced by a place word' clause appears only while the form still shows it; split alignment with only one
   of ACC / ERG live says so; the remote past note reads 'graded, from nearer to further back' or names the perfect;
   a class used as the default for nouns outside the other classes says so; verb clitics in a second-position language
   are described as second position; a bound copula goes on the edge of the predicate phrase; the invocation marks its
   object once; recipes say 'them' for a plural food and use the lect's own 'at' / 'in'; word-family cards count
   distinct words (uncle = father's brother = mother's brother is one word).

**Weirdness left (for you)**
- Class fallback: a noun whose group has no class takes the abstract, tools, plant or animal class (the first the
  lect has), so a dog can take the 'tools' classifier. The note now says that class is the default; whether animals
  should rather fall to the person or a general class is your call.
- A god name can sound like a grammatical marker (Moow); not vetoed.
- The kobold 'belly' family shows a human proto-form: the word is a loan, and the card does not yet say so.
- Event lines in the history quote a gram's form when it was made (Aliy'unun 2SG.POSS ŋɨ̞n then, ŋɨ̞ŋ now); not yet
  marked as 'then'.
- Instrument 'with' (a free word WITH) and comitative 'with' (the COM case) are different markers in one language;
  correct, but the page does not explain it.
- The dwarf vowel ä missing from the chart is in the sound lane's inventory files; not touched.

**Measured** (full pass of a24559 at commit c5a5c885, 8 workers, 1463 s, scratch output `scratchpad/polish/pass1/`;
before = the grammar D pass the demo read 4 page came from; living lects 612 -> 624, the draws moved):

| measure | before | after |
| --- | --- | --- |
| living lects with two core pronoun cells alike (I = WE, THOU = HE ...) | 156 (25.5%) | 1 (0.2%) |
| living lects with two numerals alike (restricted hundred = thousand aside) | 339 (55.4%) | 5 (0.8%) |
| living lects with two question words alike | 150 (24.5%) | 1 (0.2%) |
| plural T-V where 'thou' = 'you' | 39 of 187 | 0 of 156 |
| faith gods not named by every holder | 89 | 8 (a name coinage failed) |
| faiths with their own food taboos in the record | 0 | 81 of 107 (first: swine 54, carrion birds 21, others 6) |
| horizon, human, window / logistic | 12.0 / 13.3 kyr | 13.5 / 10.8 kyr (summary line 14.0) |
| pronoun loans (WOLD check) | 0.049 | 0.069 (repairs by loan, as English they) |
| sisters strict / cross-family | 0.593 / 0.0005 | 0.605 / 0.0005 |

All 14 checks as before: 13 pass; the horizon check still fails (target 6-10 kyr). The horizon moves 1-2 kyr between
passes on its own (bootstrap noise, calibration.md), so neither reading is a regression I can pin on the repair.
Demo: `scratchpad/polish/languages-demo.html` (12 languages, 8.4 MB) and `languages-demo-stripped.html`. The fable now
uses the triton proto-language, last spoken about 6,000 years ago, with 4 daughters ('bird' betʰi > bitʰi, biɾ, pini).
