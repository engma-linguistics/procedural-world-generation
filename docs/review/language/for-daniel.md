# For Daniel (set aside overnight, 2026-11-07 → 11-08)

Everything here has a working default in the code already. Nothing is blocked; change any of them in one place.

## Decisions (defaults taken)
1. **Synthesis level** (how affix-heavy languages are). Grammar A measured it: 58% of our lects mark 0-1 verb categories with affixes, against about 3% in WALS 22A, so ours are far more isolating than real languages. Default: unchanged until grammar B adds mood and it's measured again. Then raise `FUSE` (0.012 to about 0.02) if it's still over about 25%. Details in the Grammar phase A section.
2. **Species leanings in grammar** (like kenku → tone): the lane's guessed table, marked as guesses.
3. **Letters for non-human sounds** in book spellings (the purr vs trill rr): names lane's guess.
4. **Merger veto / homophony; spread of change rates between lects:** current settings kept.
5. **After a shift: how long minority speech lives, L2 share levels, how much dialect continuity:** current settings kept, with the reviews' numbers alongside.
6. **A shifting people keeps the old language's sounds, or reshapes them by its own voice:** current behaviour (keeps them) kept.

## Weirdness noticed
- **The demo page has glitches** (a full read before publishing found them). Merchants are glossed as things in two languages, a dual marker is described but missing from its example, one note quotes the wrong verb, and some agent jargon shows. None is in the data model's core. All are queued as the first item of grammar B in queue.md.
- **Scholars' horizon jumped from about 11 to 16-18 thousand years** in both the grammar A and lexicon lanes' passes. Grammar A doesn't touch the words, so the measure may swing with any change to the random draws. The lexicon lane is checking that before it tunes anything.
- See each lane's section below for more.

## Demos waiting
- **Languages demo page** (10 languages, 255 audio clips, complexity tab): https://claude.ai/artifact/GQUxhWHnErqn3zx7MTaFUs (private). Live viewer: `uv run python -m planet langserve a24559 --host 0.0.0.0 --port 8790`.

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
