# Grammar coverage review: eight real languages against the generator

Branch `lang-design` at ab4d0c24. This was a read-only review: nothing was changed. Code paths below are relative to the
worktree. "Live" figures are from the 627 living lects of run a24559, tallied read-only from `runs/a24559/languages.json`.
The scripts are in the scratchpad `gg/` folder. Real-language figures are Grambank marginals as the code stores them
(`grammar.py:283 _FB_GB`). WALS figures are from memory and approximate. They are marked "≈".

**Run a24559 predates round 5's vocabulary.** Its lexicons had no GET, BECOME, FINISH, WANT or NOTHING. Round 5 added
them (`concepts.tsv` rows 694, 1990, 1766, 1784, 687; commit 9fe20b10). So some paths that were dead in a24559 can fire
now: passive from GET/BECOME, perfect from FINISH, future from WANT. I could not measure what they do, because no newer
run exists. Where this matters, I say so.

## How to read "coverage"

- **full**: a typology value exists, a gram or construction realises it, and the sample sentences or notes show it.
- **partial**: something exists, but it is thinner than the real feature, rarely realised, or only a label.
- **label only**: the typology draws a value and the sketch prints it, but nothing in the output carries it out. It is
  worse than none, because the page claims something it never shows.
- **none**: no typology value, no gram function and no sentence builder.

---

## 1. Summary table

| Language | Distinctive feature | Coverage | Note |
|---|---|---|---|
| **English** | SVO, prepositions, NG/GN mix | full | WALS crosstabs; free adpositions from IN/AT |
| | Definite and indefinite articles (from THAT, ONE) | full | X15, G050 |
| | Past, perfect (*have*), future (*will* < want), progressive (*be at*) | full | G006, G004 (WANT now in the lexicon), G008 |
| | Subject agreement only in 3SG (-s) | full (by accident) | partial paradigms are the norm in the output |
| | *be* passive | none in practice | PASS 0% live, no passive sentence |
| | Subject–auxiliary inversion, do-support in questions | none | polar_question has no inversion value |
| | Pronoun case (I/me), wh-fronting, *that* relatives | partial / full / full | no pronoun case |
| **Mandarin** | Isolating, few or no affixes | full | median lect has 1 bound gram |
| | Lexical tone | full (phonology) | 38% tonal |
| | Numeral classifiers | partial | after numerals only, not after demonstratives (*zhè-ge*) |
| | Aspect particles *le*, *guo*, *zhe*, *zài* | partial | PERF and PROG exist; G016 experiential is unmapped |
| | Serial verbs, resultative compounds | label only | `serial_verbs` is never built into a sentence |
| | Topic–comment | none | |
| | RelN and GN with *de* | full | RelN linker = free GEN (`sentences.py:847`) |
| | Sentence-final particles (*ma*, *ne*, *ba*) | partial | only the question particle, and that is the word IF, not a tracked gram |
| | *bǎ* object marking (< 'take') | partial | G030 TAKE > ACC exists, but the object does not move before the verb |
| **Swahili** | 15–18 noun classes in sg/pl pairs | partial | at most 5 class grams in any lect, 9 groups; plural is a separate PL, not a class switch |
| | Alliterative concord (adjectives, demonstratives, verb) | none | class markers sit on the noun only |
| | Verb template SM-TAM-OM-root-EXT-FV | partial | SM (person, not class) and TAM prefixes yes; OM, relative and FV no |
| | Object marker | none | no object-agreement function at all |
| | Verb extensions: applicative, causative, passive, reciprocal, stative | partial | CAUS yes (11% bound), PASS 0%, the rest none |
| | Locative suffix -ni / locative classes | partial | LOC case yes; locative classes no |
| | Asymmetric negation (*ha-* plus negative TAM forms) | partial | NEG prefix yes; no negative-only paradigm |
| **Mohawk** | Polysynthesis: 6–10 affixes per verb | partial (rare) | 6% of lects have ≥6 bound verb affixes |
| | Agent/patient pronominal prefixes (transitive portmanteaus) | none | no object agreement, no portmanteaus |
| | Noun incorporation | none | |
| | Inclusive/exclusive, dual in verbs | none | clusivity 0% live; dual only on nouns |
| | Head-marking, no case | partial | "no case" yes; head-marking only as subject agreement |
| | Aspect suffixes (punctual, habitual, stative) and modal prefixes | partial | aspect yes, mood none |
| | Pragmatic (free) word order | partial | `free` is drawn (13%) but rendered as fixed SOV/SVO |
| **Basque** | Ergative case (-k), zero absolutive | none in practice | ERG 0% live; erg-abs lects show no marker |
| | 12+ cases, local genitive (-ko) | partial | `case: many` 7%; ABL/ALL/INS/COM rarely recruited |
| | Polypersonal auxiliary (ERG, ABS, DAT agreement) | none | no auxiliary host, no object or indirect-object agreement |
| | Definite suffix -a | full | `definite_article: post` |
| | SOV, postpositions, RelN | full | |
| | Preverbal focus position | none | |
| **Latin** | Fusional (cumulative) case+number endings | partial | case and number stack as separate affixes; only sound change blurs them, on 4 exemplars |
| | Five declensions, four conjugations | none | no inflection classes across the lexicon |
| | Three genders with agreement | partial | gender is a noun affix only; nothing agrees |
| | Synthetic passive (-r) | none in practice | PASS 0% |
| | Subjunctive, imperative | none | no mood functions besides evidentials |
| | Perfect stems by ablaut or reduplication | partial | an affix that erodes to nothing can leave a changed stem (`grammar.py:1992`), on exemplars only |
| | Free order (pragmatic), SOV tendency, no articles | partial | free order is rendered fixed |
| **Quechua** (Cuzco) | Agglutinative suffix chains, SOV, case suffixes | partial | possible but uncommon; 36 SOV lects have `case: many` |
| | Three-way evidentials (-mi, -si, -chá) as second-position enclitics | partial | DIR 4%, REP 20%, no conjectural; they attach to the verb, not to the focused word |
| | Object agreement and person portmanteaus (-wa-, -yki) | none | |
| | Inclusive -nchik vs exclusive -yku | none | |
| | Switch-reference (-spa / -qti) | none | no clause chaining at all |
| | Possessor suffixes on the noun (*wasi-y*) | none | possession is dependent-marked or unmarked only |
| | Nominalised relative clauses (-q, -sqa, -na) | none | relative = THAT relativiser, gap or correlative |
| | Topic -qa, polar/negative -chu | none / partial | Q clitic from IF only |
| **Tagalog** | Symmetrical voice (AV -um-, PV -in, LV -an, CV i-) with an *ang* pivot | none | |
| | Infixation (-um-, -in-) | none | grams attach only before or after |
| | Aspect by CV reduplication (*kakain*) | label only | `verb_reduplication` 72% "yes", never built |
| | Verb-initial order | full | VSO/VOS 5% of lects (WALS ≈ 9%) |
| | Phrase-marking particles *ang/ng/sa* | partial | free case words before the NP are possible |
| | Linker *na/-ng* | partial | only the GEN-as-linker trick for RelN |
| | Second-position pronoun clitics | none | clitics attach to their host only |
| | *tayo/kami* clusivity, plural word *mga* | none / full | free PL word, yes |

---

## 2. Why these five

The brief fixed English, Mandarin and Swahili. I picked the other five so that every major axis is covered by at least one
language, and so that each one tests a different part of the engine.

- **Mohawk** (Iroquoian): polysynthesis, head-marking, noun incorporation, agent/patient pronominal prefixes, discourse-driven
  order. It tests whether the engine can build a word-sentence and mark the object on the verb.
- **Basque** (isolate): ergative case and polypersonal agreement in an auxiliary. It tests the alignment layer, which the
  typology draws but the grams may not realise. I chose it over Dyirbal because Basque also has a large case system,
  definite suffixes and a periphrastic verb, which together make it a fuller test. Dyirbal's split ergativity and four
  classes come up under the cross-cutting gaps.
- **Latin**: a fusional case language. It tests cumulative exponence, inflection classes, gender agreement, the
  synthetic passive and mood. I chose it over Russian because Latin's passive and subjunctive are inflectional; Russian's
  aspect pairs are mostly derivational prefixes, which overlap less with what the engine models.
- **Quechua** (Southern/Cuzco): an agglutinative suffixing language with three-way evidentials. It also covers
  switch-reference, clusivity, object agreement, possessor suffixes and nominalised relatives, so it does double duty for
  the "switch-reference" slot. Turkish would test less: its evidential is two-way, and it has no clusivity or object
  agreement.
- **Tagalog** (Austronesian): verb-initial order, a symmetrical voice system, infixes, reduplication for aspect, linkers and
  second-position clitics. It tests morphology that is not a prefix or suffix, and a voice system that is not a passive.

Mandarin already covers the "classifiers" and "highly analytic" slots.

---

## 3. What the engine has, in brief (checked in code)

- **39 typology features** (`grammar.py:527 FEATURES`), each drawn conditional on the ones before it (`:656 _draw_feature`).
  Word order uses WALS crosstabs; the rest use Grambank marginals with lifts.
- **36 gram functions plus noun classes** (`grammar.py:85 FUNCS`): PL DU, DEF INDEF, 9 cases, DIM AGENT PLACE,
  PAST RECPST FUT, PERF PROG IPFV HAB, EVID.DIR EVID.REP, NEG, CAUS PASS REFL, and subject person 1SG–3PL.
  Affixes stack in a fixed order (`:125 SLOT_ORDER`), each before or after its host (`:985 _side`). **No infixes,
  circumfixes, reduplication, mutation or tone as exponents. No functions for the object, the possessor, mood, questions,
  the copula, relativisers, complementisers, topic or focus, applicatives, reciprocals or antipassives.**
- **Grams are recruited along paths** (`data/grammaticalization_paths.tsv`, 72 rows; plus 18 built-ins at `grammar.py:349`).
  A path counts only if `_TARGET_MAP` (`:321`) maps its target, so these rows are dropped: G007 obligation, G016
  experiential, G020 permission, G021 attempt, G023 complementiser, G034 hortative, G035 apprehensive, G053 3rd person
  pronoun, G055 relativiser, G056 copula, G057 focus, G060 middle > passive, G062 nominaliser, and the comparative rows
  G047/G048.
- **Ten sample sentences** (`sentences.py:885`). Copula, question particle and relativiser are faked from lexical words
  (`:817`, `:685`, `:847`). Free word order is rendered as SOV or SVO.
- **Paradigms** are 4 nouns and 4 verbs per lect (`grammar.py:1366 _cell_keys`). Process morphology (a changed stem with
  no affix left) can survive only in these cells (`:1992 _check_lost`).
- **Label-only typology.** `serial_verbs`, `verb_reduplication`, `numeral_base`, `comparative` and `clusivity` are read by
  nothing in `sentences.py` or `lexicon.py`. Only `tools/language/sketch.py:551-568` reads them, and it prints them as facts.
  `passive` and `object_agreement` are read only to set the shown value.

---

## 4. Per-language sections

### 4.1 English

**What makes it distinctive:** SVO with prepositions. Mostly analytic, with a little inflection left: plural -s,
possessive ='s, past -ed, 3SG -s and -ing. Definite and indefinite articles. A large set of auxiliaries: perfect *have*,
progressive *be*, future *will*, passive *be*, and *do*-support. Wh-fronting. Subject–auxiliary inversion in questions.
Case survives only in pronouns. No pro-drop.

**Coverage:**
- **Word order, prepositions and articles: full.** The WALS crosstabs handle SVO→prepositions/NG. DEF from THAT (X15) and
  INDEF from ONE (G050) are exactly the English histories.
- **TAM: good, after round 5.** PERF < HOLD (G006, aliased from HAVE: `grammar.py:338`) and PROG < AT (G008) worked
  before. FUT < WANT (G004) only became possible once WANT entered the lexicon. Past from YESTERDAY (X14) is unlike
  English's dental suffix, but it is a reasonable source.
- **Agreement: right by accident.** English has a single 3SG marker. The engine's agreement is nearly always partial:
  216 of the 627 lects have exactly one bound person marker, and only 1 has all six (my tally). That fits English,
  but it is wrong as a general rule (see §5.3).
- **Passive: none in practice.** PASS was live in 0 lects. In a24559 the only sources (G032 SUFFER/RECEIVE/GET, G033
  BECOME) were missing from every lexicon. GET and BECOME are in the lexicon now, so this may change. Even so, no
  sentence uses PASS.
- **Polar questions by inversion: none.** `polar_question` has four values (intonation, initial or final particle, verb
  morphology), but no "inversion" value. English would be drawn as "intonation".
- **Pronoun case: none.** Pronouns are single forms.

**Could a generated language look like English?** Yes, broadly. An SVO lect with prepositions, two articles, a plural
clitic, a past suffix and HOLD-perfect/AT-progressive auxiliaries is well within range. What gives it away: no passive,
and no question inversion.

### 4.2 Mandarin Chinese

**What makes it distinctive:** isolating morphology. Lexical tone. Numeral classifiers, required after numerals and
demonstratives. Aspect, not tense: perfective *le*, experiential *guo*, durative *zhe*, progressive *zài*. Serial verbs and
resultative compounds (*dǎ-pò* 'hit-break'). Topic–comment structure. RelN and GN with the linker *de*. Sentence-final
particles (*ma*, *ne*, *ba*, *le*). Wh-in-situ. *bǎ* object fronting. Copula *shì* (< demonstrative 'this').

**Coverage:**
- **Analytic shape: full.** The engine skews analytic. 36% of lects have no bound gram, and the median is 1.
- **Tone: full**, from the sound system.
- **Classifiers: partial.** Free CLASS grams from generic nouns follow numerals (`sentences.py:441 _classifier`). That is
  a good mechanism (G066 is the real source). But a classifier is never used with a demonstrative, which Mandarin
  requires. Share: 18% of lects, against Grambank GB057's 24%.
- **Aspect: partial.** PROG < AT (G008) matches *zài*. PERF < FINISH (G013) matches *le* < *liǎo*; FINISH has only been in
  the lexicon since round 5. G016 PASS/CROSS > experiential (*guo*) is dropped because `_TARGET_MAP` has no entry for it.
  There is no durative.
- **Serial verbs: label only.** `serial_verbs: yes` is drawn for 50% of lects and the sketch prints "serial verbs"
  (`tools/language/sketch.py:551`), but no sentence has two verbs. The GIVE > DAT (X18) and TAKE > ACC (G030) paths do
  start from serial verbs, but the serial stage itself is never shown.
- **Topic–comment: none.**
- **de-linker relatives: full.** A free or clitic GEN is used as the RelN linker (`sentences.py:847`). That is a neat
  Mandarin-like touch.
- **Copula: full in spirit.** The copula is the word for HE OR SHE OR IT, else THAT (`sentences.py:817`), as the
  *shì* history (G056) has it. But it is not tracked as a gram, so it never erodes or binds.
- **Final particles: partial.** Only Q, and it is the IF word, not a gram (`sentences.py:685`).
- **bǎ: partial.** G030 TAKE/HOLD > ACC exists, but an ACC gram is placed as an adposition on the object wherever the
  object stands. The object never moves before the verb.

**Could a generated language look like Mandarin?** Partly. 8 lects in a24559 are SVO, tonal, have classifiers and at most
one bound gram. What gives them away: no serial-verb or resultative sentence, no topic-fronting, and no classifier after
a demonstrative.

### 4.3 Swahili

**What makes it distinctive:** about 15–18 noun classes in singular/plural pairs (m-tu / wa-tu). Alliterative concord on
adjectives, demonstratives, possessives and the verb. An agglutinative verb template: SM-(NEG)-TAM-(REL)-(OM)-root-
(extensions)-final vowel. Object markers. Verb extensions: applicative -i/e-, causative -ish-, passive -w-, reciprocal -an-,
stative -ik-. TAM prefixes from verbs: -ta- < *-taka* 'want', -me- < *-isha* 'finish', -li- < 'be'. Negation by *ha-* and
separate negative TAM forms. SVO, with N-Adj, N-Dem, N-Gen and N-Num order. Locative classes and the -ni locative suffix.

**Coverage:**
- **Noun classes: partial.** This is a strong part of the engine. Class markers grow from classifier nouns into prefixes
  or suffixes (`grammar.py:1606 add_class`, groups at `:128`), as in Bantu. But:
  - Number is a separate PL gram. Real Bantu plural is a switch to a paired class (1/2, 3/4 …).
  - No lect has more than 5 class grams. 6% have 3 or more, and only 2 lects have 5 bound.
  - **Nothing agrees.** The class marker appears only on the noun (`sentences.py:376`). Concord is what defines a noun
    class system, so without it this is a classifier prefix, not gender.
- **Subject marker: partial.** Prefixal person agreement is possible: in VO lects the "agr" side rule gives `pre`
  (`grammar.py:985`). But it marks person only, never class.
- **TAM prefixes: good.** In VO lects TAM grams land as prefixes (`_side` "aux" rule). WANT > FUT and FINISH > PERF follow
  the real Swahili sources, now that both words are in the lexicon.
- **Object marker: none.** There is no function for it (`realised_value` returns "none" for object agreement,
  `grammar.py:1174`).
- **Extensions: partial.** CAUS < GIVE/MAKE (bound in 11%). PASS: 0% live. Applicative, reciprocal and stative: none.
  G026 lists "applicative" as an endpoint, but its target is mapped to DAT.
- **Negation: partial.** A NEG prefix, yes. Negative-only TAM forms, no.
- **Orders and LOC: full.**

**Could a generated language look like Swahili?** On the surface, briefly. 15 lects in a24559 are SVO with noun classes
and prefixal agreement. Any connected text gives them away: no concord, no object marker, and no applicative or passive
suffixes on the verb.

### 4.4 Mohawk

**What makes it distinctive:** polysynthesis. A single verb often holds pronominal prefix + root + aspect suffix, plus
modal, dualic, repetitive or cislocative prefixes. About 58 pronominal prefixes encode agent and patient together
(*kon-* 'I→you'). Noun incorporation. Head-marking throughout, with no case. Inclusive/exclusive and a dual. Gender
(masculine, feminine-indefinite, zoic) only in the pronominal prefixes. Few true adjectives; stative verbs fill that role.
Discourse-driven word order.

**Coverage:**
- **Long verbs: partial (rare).** Only 37 of 627 lects (6%) have 6 or more bound verb affixes. Reaching that many depends
  on long recruitment chains with a low adult-learner share.
- **Agent/patient prefixes: none.** There is no object person function. Person markers are separate single-cell grams,
  never portmanteaus.
- **Noun incorporation: none.** No function or sentence for it. (The lexicon's compounding exists, but it is noun-noun.)
- **Clusivity: none.** It shows 0% because `_clusive` (`grammar.py:1129`) wants two lexicon concepts, "WE (INCLUSIVE)" and
  "WE (EXCLUSIVE)", and `concepts.tsv` has neither, only WE (row 1212). So it can never be "yes".
- **Dual: partial.** DU exists only on nouns (2% live). There is no verb or pronoun dual.
- **Gender in verb prefixes: none.**
- **Adjectives as stative verbs: full.** `adjective_verb_like` is rendered (`sentences.py:1115`).
- **Free order: partial.** It is drawn, but rendered as SOV or SVO with a note.
- **Aspect suffixes: partial** (PERF, HAB, PROG). Modal prefixes: none.

**Could a generated language look like Mohawk?** No. The defining features (agent and patient on the verb, incorporation,
clusivity) are absent. The best the engine can do is a verb with subject-person and several TAM affixes, which looks more
like Turkish than like Iroquoian.

### 4.5 Basque

**What makes it distinctive:** ergative–absolutive case (ergative -k, absolutive zero, dative -i). Around 12–15 cases,
including the local genitive -ko and benefactive -entzat. Most verbs are a participle plus an auxiliary (*izan*/*ukan*), and
the auxiliary agrees with the ergative, absolutive and dative arguments at once. A definite article suffix -a that fuses
with case and number. SOV, with postpositions and case suffixes. RelN with -en. A preverbal focus slot. Pro-drop.

**Coverage:**
- **Ergativity: none in practice. This is the most serious single finding.**
  - The typology draws erg-abs for 6% of living lects and split for 8%, but **no living lect has an ERG gram** (my
    tally: 39 erg-abs lects and 49 split lects, all with no ERG and no ACC).
  - Why: the only path to ERG is the built-in X17, INS > ERG (`grammar.py:367`). It is a gram-to-gram path, so it needs a
    live INS, and INS is live in only 2% of lects. No lexical path leads to ERG.
  - The recruitment pull cannot rescue it. `_unrealised` (`grammar.py:1269-1283`) asks only whether a function's *first*
    feature is already marked, and the first feature of both ERG and ACC is `case`. So a lect with any LOC or GEN marker is
    never pulled toward ERG or ACC.
  - The pages then say "the typology leans ergative, but no case marker shows it" (as the drow sketch does for nom-acc).
    That is honest, but it means every ergative lect is shown as neutral.
  - Sentences mark ERG only when the lect is `erg-abs` (`sentences.py:558`). A split lect gets ACC only, and no split is
    conditioned by person or by tense and aspect.
- **Many cases: partial.** `case: many` covers 7% of lects. ABL, ALL, INS and COM are wanted only for `many`, and the
  pull only fires when *no* case gram is live, for the same `feats[0]` reason. So a rich case system grows only by the
  ordinary recruitment draw. INS is live in 2%, COM in 12%, and ABL and ALL in 0%.
- **Polypersonal auxiliary: none.** There is no object or indirect-object agreement. There is also no notion of an
  auxiliary as the host for agreement: person grams always attach to the lexical verb (`sentences.py:509 verb`).
- **Definite suffix, SOV, postpositions, RelN: full.**
- **Focus position: none.**

**Could a generated language look like Basque?** Its word order and noun phrase, yes: an SOV lect with postpositions,
a definite suffix and a few case suffixes. Its alignment and verb, no.

### 4.6 Latin

**What makes it distinctive:** fusional morphology. Case and number share one ending (-ōrum = genitive plural), across five
declension classes. Three genders, with agreement on adjectives and pronouns. Verbs fuse person, number, tense, aspect,
mood and voice, across four conjugations, with a synthetic passive (-r) and a subjunctive. Perfect stems are formed by
ablaut, reduplication or -v-/-s- (*fēc-ī*, *cecid-ī*). No articles. Fairly free, SOV-leaning order. Pro-drop.

**Coverage:**
- **Case–number fusion: partial.** Number and case are separate grams in fixed slots (`grammar.py:125`). Sound change
  running over the exemplar cells, with the N×case pairs at `:1366`, can blur the boundary and produce irregular cells.
  That is a real diachronic mechanism, but only on 4 nouns. There is no portmanteau ending: no single morph that means
  "GEN.PL".
  - The merger rule (`:1992 _check_lost`) *deletes* the rarer of two same-slot grams that sound change made identical. Real
    syncretism keeps both categories and lets them share a form.
- **Declension and conjugation classes: none.** Every noun takes the same affix. Variation comes only from sound change
  on the exemplars.
- **Gender: partial.** Sex gender (9% of lects) shows as a marker on the noun, from MAN/WOMAN. Nothing agrees with it, so
  the reader sees a masculine prefix, which is not what Latin gender is.
- **Passive: none in practice** (see English).
- **Subjunctive and imperative: none.** The only mood-slot functions are the two evidentials (`grammar.py:85`).
- **Perfect stems: partial.** When an affix erodes to nothing but leaves a changed stem, the gram survives as "fused"
  (`:1992`). That models umlaut or ablaut stem marking, but again only on exemplars; other nouns and verbs in the sentences
  get the bare stem.

**Could a generated language look like Latin?** Only a little. About 20 lects have 5 or more bound noun affixes, and
their paradigms look agglutinative-turned-irregular, not fusional. No agreement, no inflection classes, no mood.

### 4.7 Quechua (Southern / Cuzco)

**What makes it distinctive:** an agglutinative suffix chain on nouns and verbs. Case suffixes: -ta accusative, -pa
genitive, -man allative/dative, -manta ablative, -wan comitative/instrumental, -pi locative, -kama 'up to', -paq
benefactive. Evidential enclitics, -mi direct, -si reported and -chá conjectural, on the focused constituent in second
position. Object agreement and person portmanteaus (-wa- 1st person object; -yki 'I→you'). Inclusive -nchik and exclusive
-yku. Switch-reference: -spa (same subject), -qti (different subject). Possessor suffixes (wasi-y 'my house').
Nominalised relative clauses (-q, -sqa, -na). Topic -qa, question/negative -chu. Derivational verb suffixes: -chi
causative, -ku middle, -naku reciprocal, -pu benefactive.

**Coverage:**
- **Agglutinative SOV with case suffixes: partial.** It is possible: OV puts aux-type grams after the verb, and case
  suffixes come from postpositions (G049). But it is uncommon: 19 lects in a24559 are SOV with case, an evidential and
  suffixal agreement.
- **Evidentials: partial.**
  - Two values: REP (20% live) from SAY (G024), and DIR (4% live) from SEE (G022).
  - No conjectural or inferential.
  - EVID.DIR is wanted only when the typology says `direct+indirect`. The pull skips it once a REP gram exists, for the
    `feats[0]` reason.
  - Evidentials always attach to the verb. Quechua's sit in second position, on the focused constituent.
- **Object agreement, portmanteaus: none.**
- **Clusivity: none.**
- **Switch-reference: none.** No sentence has two clauses besides the relative.
- **Possessor suffixes: none.** Possession is either GEN on the possessor or bare juxtaposition (`sentences.py:376`, the
  `poss` branch). Head-marked possession (WALS 24A ≈ a third of languages) cannot arise.
- **Nominalised relatives: none.** RelN is a finite verb with no relativiser (`sentences.py:847`).
- **Topic marker: none.**
- **Q/NEG clitic -chu: partial.** `verb_morph` puts a clitic from IF on the verb (`sentences.py:690`).
- **Derivational verb suffixes: partial.** CAUS and REFL exist. Reciprocal and benefactive (an applicative) do not.

**Could a generated language look like Quechua?** At the level of "SOV, suffixing, case, a reportative": yes, in a minority
of lects. Its most recognisable traits (-nchik/-yku, the object and person portmanteaus, -spa/-qti, wasi-y) are all
missing.

### 4.8 Tagalog

**What makes it distinctive:** a symmetrical voice system. The verb's voice affix picks which argument is the pivot,
marked *ang*: actor voice -um-, patient voice -in, locative -an, conveyance i-. Infixes (-um-, -in-). Aspect, not tense,
built from infix plus CV reduplication (*kumain* 'ate', *kumakain* 'eats', *kakain* 'will eat'). Verb-initial order.
Phrase-marking proclitics *ang*/*ng*/*sa*. Linkers *na*/-ng between modifiers and heads. Second-position pronoun and
adverb clitics. Inclusive *tayo* vs exclusive *kami*. Plural word *mga*. Existential possession (*may*).

**Coverage:**
- **Voice system: none.** PASS is the only voice function, and it is a demotional passive. It is also 0% live.
- **Infixation: none.** Grams attach before or after (`grammar.py:241 _attach`).
- **Reduplication for aspect: label only.** `verb_reduplication` is "yes" for 72% of lects and is never built.
- **Verb-initial: full.** 33 lects (5%) are VSO or VOS.
- **ang/ng/sa: partial.** Free case words that precede the NP are possible: prepositional, with `adp` side `pre`.
  Nothing makes one of them a pivot marker.
- **Linkers: partial.** Only the GEN-as-RelN-linker case.
- **Second-position clitics: none.**
- **Clusivity: none.**
- **Plural word: full.** A free PL < ALL/MANY (G064), placed before the noun.
- **Existential possession: partial.** "Locational" or "with" possession is drawn and rendered (`sentences.py:765`).

**Could a generated language look like Tagalog?** A VSO lect with proclitic case words and a free plural word, yes. A
Tagalog-type voice system, no; nothing in the engine approaches it.

---

## 5. Cross-cutting picture

### 5.1 Missing entirely (no typology value, no function, no construction)

1. **Object agreement.** The feature is drawn, but there is no gram function (`grammar.py:1174`). This blocks Mohawk,
   Swahili, Basque and Quechua. Real shares: GB093 34% (suffix), GB094 22% (prefix).
2. **Agreement of anything with a noun's class or gender.** No concord on adjectives, demonstratives or verbs. The
   `gender` feature is realised as a noun affix only.
3. **Possessor marking on the possessed noun.** Head-marked possession, as in my-house. Common in Uralic, Turkic,
   Quechuan, Austronesian and much of the Americas and New Guinea.
4. **Mood.** Imperative, subjunctive/irrealis, optative, hortative and apprehensive. G007, G020, G034 and G035 are in the
   path table but unmapped. There is no imperative sentence, though a bare-stem imperative costs nothing.
5. **Voice beyond the passive.** Applicative (G026 names it but maps it to DAT), antipassive, reciprocal, middle (G060 is
   unmapped), and Austronesian symmetrical voice.
6. **Clause linkage.** Switch-reference, converbs and clause chaining, complement clauses (G023 SAY > complementiser is
   unmapped), coordination. The only subordinate clause is the relative.
7. **Information structure.** Topic markers and topic-fronting, focus particles and positions (G057 is unmapped).
8. **Non-concatenative exponence outside exemplar paradigms.** Infixes, reduplication, initial mutation (Celtic), and
   grammatical tone. Mutation and umlaut *can* arise inside exemplar cells (`grammar.py:1992`), but they never reach the
   sentences.
9. **Noun incorporation.**
10. **Inflection classes** (declensions and conjugations), and **portmanteau morphs** (cumulative exponence).
11. **Second-position (Wackernagel) clitics.**
12. **Pronoun case** (I/me), and **pronominal dual or inclusive**.
13. **Polar-question inversion** (Germanic V1 questions) as a `polar_question` value.

### 5.2 Modelled too thinly

- **Constructions that are faked, not tracked.**
  - The question particle is the IF word. The copula is HE/THAT. The relativiser is THAT.
  - None of them is a gram, so none can erode, bind or renew. A Turkish -mI clitic or a Mandarin *ma* cannot arise
    historically.
  - The pages are honest about this (`sentences.py:685`, `:817`, `:847`).
- **Label-only typology.**
  - The sketch prints these as properties of the language (`tools/language/sketch.py:551-568`): `serial_verbs`
    50% yes, `verb_reduplication` 72% yes, `numeral_base`, `comparative`.
  - Nothing builds them. The numerals table even says "Counting base: decimal" above ten unrelated numeral words.
  - A linguist reading a sketch will notice "serial verbs" with no serial verb in it.
- **Person agreement is cell by cell.**
  - Each person form is its own gram, recruited separately from its pronoun (X06–X11).
  - Result: 216 lects have one bound person marker, 89 have two, and 1 has all six.
  - Real agreement systems arise when the whole pronoun series cliticises together, so partial paradigms like this are
    unusual outside English-like erosion.
  - "Verb agreement: suffix 31%, prefix 26%" therefore mostly means "a 3SG marker".
- **Free word order is rendered as fixed order.** `sentences.py:549`, with a note.
- **Only 4 nouns and 4 verbs carry paradigms.** Irregularity, fusion and stem alternation live only there. Every other
  word in a sentence is regular concatenation.
- **The noun-class inventory is small.** At most 5 class grams, in 1% of lects; 3 or more in 9%. Bantu-scale systems
  (10+) cannot arise.
- **Classifiers appear only after numerals**, never after demonstratives or quantifiers.
- **Evidentials have two values.** No inferential or conjectural, and no second-position placement.
- **There is no ditransitive sentence.** DAT, INS, ABL and ALL appear only in the notes (`sentences.py:932`), never in a
  sample sentence.

### 5.3 Exists but wrongly calibrated

| Feature | Live share (a24559) | Real reference | Cause found in code |
|---|---|---|---|
| Passive | 0% | GB147 42% bound; GB302 10.5% periphrastic | In a24559 no lexicon had GET, BECOME, SUFFER or RECEIVE (all dead paths). G060 REFL > MIDDLE > PASSIVE is unmapped (`_TARGET_MAP`, `grammar.py:321`), even though REFL is live in 28% of lects. Round 5 added GET and BECOME; **unmeasured since**. |
| Object agreement | 0% | GB093 34%, GB094 22% | No function exists. |
| Clusivity | 0% | GB028 52.5% | Needs lexicon concepts that `concepts.tsv` lacks (`grammar.py:1066`). |
| **Ergative case** | **0% have an ERG gram** (typology claims erg-abs 6% + split 8%) | GB409 22%; WALS 98A ≈ 17% ergative on full NPs | Only path is gram-to-gram INS > ERG (X17); INS is live in 2%. `_unrealised` pulls by `feats[0]` only (`grammar.py:1283`), so any live case gram blocks the alignment pull. |
| Accusative case | 9% have ACC | GB408 44%; WALS 98A ≈ 28% nom-acc | Same pull bug; sources only G030 TAKE/HOLD and G045 ALL > ACC. |
| Dual | 2% (0% bound) | GB043 7.7% | DU's first feature is `number`, so once PL is live the pull never fires for DU. |
| Rich case (ABL/ALL/INS/COM) | ABL 0%, ALL 0%, INS 2%, COM 12% | WALS 49A ≈ 25% of languages have 6+ cases | Same `feats[0]` block; ABL and ALL have no lexical paths (only the G017 ARRIVE > allative row, and the ablative appears only as a source). |
| Direct evidential | 4% | GB322 15% (of all languages) | Same block once REP is live. |
| Verb inflectional synthesis | 63% of lects have 0–1 bound verb affixes; 46% have none | WALS 22A ≈ under 5% of languages with 0–1 verb categories | Low RECRUIT/FUSE relative to 20 kyr with a median adult-learner share of 0.54. The comment at `grammar.py:46` gives median 5–12 live grams. This is a deliberate model choice, but the outcome is far more isolating than the world's languages. |
| Adjective–noun order | NA 85% | WALS 87A ≈ 64% NA, 27% AN | Already flagged on the reference page. |
| Gender: sex | 9%, realised as a noun affix | GB051 18% (but defined by agreement) | A definition mismatch: no concord. |
| Verb agreement | shown 59% | GB089 41% / GB090 42% | The share is fine, but the paradigms are nearly always partial (§5.2). |

**The `_unrealised` bug, in plain words.** The engine is meant to nudge a language toward the markers its typology asks
for. It checks "is this category already marked?" using only the *first* category a marker belongs to. ACC and ERG belong
first to "case", DU to "number", EVID.DIR to "evidentiality" and ABL to "case". So a language with any case marker never
gets nudged toward an accusative or ergative one. A language with a plural never gets nudged toward a dual. A language
with a reportative never gets nudged toward a direct evidential. The fix is to check each function's own sub-feature:
alignment for ACC/ERG, `sg-du-pl` for DU, `direct+indirect` for EVID.DIR, `many` for the rich cases. It is a small
change. (`grammar.py:1269-1286`.)

---

## 6. Ranked recommendations

Value is "how much more real-looking the output gets" (H/M/L). Cost: S = under a day, a few functions and tests;
M = a few days, new functions plus sentence work; L = a week or more, or an architecture change. **Before merge** means
cheap and fixing something the pages already claim. **Later** means new capability.

| # | Recommendation | Value | Cost | When |
|---|---|---|---|---|
| 1 | **Fix the alignment and sub-feature pull** (`_unrealised` keyed by function, not `feats[0]`). Add lexical and gram paths to ERG: ABL/LOC/GEN > ERG and an agentive 'by' source (Kuteva et al. 2019 list ablative, locative and genitive sources). Mark ERG in `split` lects by a person or TAM split in `clause()`. Also fixes dual, rich case and the direct evidential. | H | S | Before merge |
| 2 | **Clusivity.** When the typology draws `clusivity: yes`, split WE into two lexicon entries: inclusive by a WE+YOU compound (as Tok Pisin *yumi*), exclusive as old WE. Or add the two concepts to `concepts.tsv`. Show it in the pronoun table. | M | S | Before merge |
| 3 | **Stop label-only claims.** Either build `serial_verbs`, `verb_reduplication` and `numeral_base`, or drop them from the sketch's "Other features" line (`tools/language/sketch.py:551-568`). Cheapest builds: a serial sentence 'take the knife, cut the meat'; a CV-copy on the verb for habitual or plural action; numerals 11–20 built from 10 (or 20 from PERSON, vigesimal). | M | S | Before merge |
| 4 | **Passive.** Map G060 (REFL > middle > passive) in `_TARGET_MAP`. Check the post-round-5 PASS share on the next run (GET and BECOME are new). Add a passive sentence ('the dog was seen'). | M | S | Before merge |
| 5 | **Ditransitive and imperative sentences.** 'The man gives the child a fish' shows DAT or serial GIVE, and later object agreement and applicatives. 'Eat!' as a bare stem (or a mood gram later) shows the commonest clause type, now absent. | M | S | Before merge |
| 6 | **Whole-paradigm person agreement.** When a person gram binds, give the other pronouns in that series a strongly raised chance to cliticise, so full or near-full paradigms dominate. | H | S–M | Before merge if cheap; else first after |
| 7 | **Object agreement.** O-person functions (1SG.O …) recruited from object pronouns (the same Givón path), side from `object_agreement`, read in `realised_value`, and rendered in a 'he sees me' sentence. Opens Mohawk, Swahili OM, Basque and Quechua -wa-. Portmanteau A+O cells can follow from fusion. | H | M | Later (first) |
| 8 | **Concord.** Class or gender markers copied onto adjectives, demonstratives and the verb's subject slot (Bantu alliterative concord; IE gender agreement on adjectives and articles). Without it, `gender` should not be called gender. | H | M | Later (first) |
| 9 | **Head-marked possession.** Possessor person affixes on the possessed noun (from pronouns), its own typology feature (GB430/431), used in the 'my mother' sentence. | H | M | Later |
| 10 | **Constructions as grams: Q particle, copula, relativiser, complementiser, topic, focus.** Map G055, G056, G057 and G023 and add the functions, so they erode and bind like the rest. Q and COP are the most visible. | M | M | Later |
| 11 | **Morphological richness calibration.** Measure inflectional synthesis per lect against WALS 22A, and decide with Daniel whether an L2 median of 0.54 over 20 kyr should leave 46% of lects with no bound verb affix. This is a judgement call, so it should go to Daniel as a needs-decision ticket. | H | S to measure, M to tune (runs) | Later (needs decision) |
| 12 | **Mood grams** (imperative, irrealis/subjunctive, hortative, apprehensive) from the already-written paths G007, G020, G034, G035. | M | M | Later |
| 13 | **Inflection classes and portmanteaus.** Assign nouns and verbs to classes by stem shape or gender, so one function gets several allomorphs. Let two fused same-word grams merge into one cumulative morph, and keep syncretic categories instead of deleting the rarer (`grammar.py:1992`). | H for fusional looks | L | Later |
| 14 | **Applicative, reciprocal, antipassive.** GIVE > applicative (G026's real endpoint), REFL > reciprocal (G059). | M | M | Later |
| 15 | **Process morphology in sentences.** Infixes, reduplication, and mutation or umlaut stem marks applied to every word, not only exemplars. | M | M–L | Later |
| 16 | **Second-position clitics and topic-fronting**, so a free order is not shown as fixed. | M | M | Later |
| 17 | **Switch-reference and clause chaining** (needs a two-clause sentence and same/different-subject markers from AND or converbs). | L–M | M–L | Later |
| 18 | **Noun incorporation** (object noun compounded into the verb in highly synthetic, head-marking lects). | L–M | M | Later |
| 19 | **Austronesian voice system** (voice affixes choosing a pivot marked by a phrase particle). | M (for one type) | L | Later |

**Before the first merge**, items 1–5 are all S cost, and about half of item 6 can be too:
- 1 removes a silent failure, ergative typologies with no ergative anywhere.
- 2 and 4 remove two of the three known 0% shares.
- 3 stops the sketches asserting things they never show.
- 5 adds the two most basic missing clause types.

Item 7 (object agreement) is the single largest gain in real-looking output, but it is a new layer and belongs after the
merge, with concord (8) next.

---

## 7. Caveats

- The live shares come from a24559, which predates the round 5 vocabulary. Passive, perfect-from-FINISH and
  future-from-WANT shares may already have moved.
- The WALS figures (22A, 24A, 49A, 87A, 98A) are from memory and rounded. Check them before quoting.
- "Full" coverage means the mechanism exists and is shown. It does not mean the share matches real languages.

## Queue (Daniel, 2026-11-07: "no particular hurry to merge, queue all of that work here")

All 19 ranked items are queued on lang-design, plus degrammaticalization (a rare one-step climb for clitics/affixes,
Norde 2009). Three phases, one lane at a time on grammar.py to avoid conflicts:

- **Phase A (small, things the pages already claim):** 1 `_unrealised` per-function fix + ergative sources + split
  ergativity; 2 inclusive/exclusive WE; 3 build serial verbs, reduplication, numeral base (or drop the labels);
  4 passive (G060 mapping); 5 give + imperative sentences; 6 person paradigm recruited as a set; 11 measure synthesis
  vs WALS 22A (decision for Daniel after the measure); degrammaticalization.
- **Phase B (agreement and markers):** 7 object agreement; 8 concord (class/gender on adjectives, demonstratives,
  verb); 9 possessor marking on the possessed noun; 10 question particle, copula, relativiser, complementiser,
  topic/focus as real grams; 12 mood from the written paths.
- **Phase C (morphology types):** 13 inflection classes and cumulative exponence (keep merged categories);
  14 applicative, reciprocal, antipassive; 15 infixes, reduplication, stem change across the lexicon; 16 second-position
  clitics and topic fronting; 17 switch-reference; 18 noun incorporation; 19 Austronesian-style voice.

### Phase D (coordinator's picks, Daniel 11-07 night: "what would *you* want to work on?")
Against Wikipedia's grammatical-category list, after A-C:
- **Deixis distance:** 2- vs 3-way demonstratives (this/that/yon), distance-marked by the lexicon and pages. Cheap and very visible.
- **Politeness and honorifics:** T-V pronoun splits (a plural or 3rd-person pronoun used politely), honorific verb forms in
  status-heavy cultures; link them to the peoples' social data where it exists.
- **Species leanings in grammar,** the way kenku lean tonal: a small per-people bias table (e.g. long-lived peoples toward
  evidentials and conservative morphology). Owner-flavoured, so propose the table rather than invent lore.
- **Tense remoteness** (Bantu-style graded pasts and futures), **aspect variety** (inceptive, completive, iterative), and
  **mirativity** beside the evidentials.
- **Comparison and degree** as real constructions (the exceed, locational and particle comparatives the typology draws).
- **Obviation and animacy hierarchies** (proximate/obviative third persons; hierarchy-driven agreement), with Phase B's
  object agreement.
- **A glossed short text per demo language** (a few connected sentences: a small story or a recipe, in keeping with
  the culinary end-goal), not just isolated sentences.
- **A last-pass "reviewing linguist" agent** reads the regenerated sketches cold and lists what looks fake.

### Texts (Daniel, 11-07 night)
- Every glossed text shows four lines: book spelling (romanized), IPA, gloss and English.
- **A Schleicher-style fable.** One fixed short English fable, in the spirit of Schleicher's "The Sheep and the Horses",
  rendered in each proto-language and in its daughters. Like Schleicher's, it shows the same text through sound
  change and grammar change: the proto version and 2–4 descendants side by side, each with audio.
- **An origin myth from the faith data.** For a people whose culture has gods (`planet/lineages/gods.py`, `taboos.py`,
  merged from main 11-07), a short creation or origin myth built from that faith's gods and taboos, told in the people's
  language and glossed. If the faith data is too thin for that, say so rather than inventing lore.

### Phase A progress (branch `lang-gram-a`, 2026-11-08)

- [x] 1 `_unrealised` per function (`PULL_GROUP`), ergative from ABL/LOC/GEN/INS and agentive 'near, with', DAT > ACC,
  lexical ABL/ALL/INS sources, split ergativity by person or aspect (`Grammar.processes["split"]`); alignment shown as
  neutral when no ACC/ERG marker lives. ACC 10% > 40% of lects, ERG 0% > 15%, DU 5% > 10%, ABL 0% > 10%, ALL 5% > 9%.
- [x] 2 inclusive/exclusive 'we' (WE (INCLUSIVE) from we + you, I + you or a root; sketch pronoun table): 0% > 54%.
- [x] 3 reduplication (a process with its own verb paradigm cell: 74% of lects) and counting base (20, 100, 6-9 built
  at proto time; sketch numerals table shows 20 and 100). Serial verbs and 11-19 counting phrases: sentences (task 8).
- [x] 4 passive: G060 mapped; GET/BECOME already give 45% (before and after; WALS 107A about 44%).
- [x] 6 person paradigm as a set: one-of-six paradigms 60% > 12% of agreeing lects.
- [x] degrammaticalization (`DEGRAM`), logged as events.
- [x] 11 synthesis measured vs WALS 22A: in `for-daniel.md` as a decision.
- [x] 5 and task 8: give, imperative, passive, serial-verb, reduplication, split-ergative and inclusive sentences, with notes (Commands, Pronouns, Voice, Reduplication, Serial verbs, Giving, Numerals; Case names the split).
