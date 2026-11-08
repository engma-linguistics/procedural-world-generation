# Lexicon, semantics and word-formation review: eight real languages against the generator

Branch `lang-design` at 2ab724ea. This was a read-only review: nothing in the repo was changed. Code paths are relative to
the worktree. It is the sister of `docs/review/language/grammar-gaps.md` and uses the same coverage scale.

**Sources of the figures.**
- **Live figures** come from the 627 living lects of run a24559, read read-only from `runs/a24559/languages.json`.
- **a24559 predates round 5.** Its lexicons have about 370 concepts. The current list has 745: 570 core rows in
  `concepts.tsv`, including the 339 WOLD rows, plus the extras. Kin by birth order and marriage, COUSIN, TWENTY, HUNDRED,
  THOUSAND, most of the cooking vocabulary, and the religion, house and clothing fields are therefore absent from the
  live figures. Where it matters, I say so.
- **Synthetic figures** test the mechanisms on the **current** code. They come from a scratchpad simulation, `lx/sim.py`:
  12 seeds, two proto-lexicons each, one lect stepping 360 generations with the other as its contact. They show which
  replacement source each kind of word gets.
- **WOLD borrowing scores** come from `data/language/raw/wold/Haspelmath-2009-1460.tsv`, column `BORROWING_SCORE`. The
  repo already holds this file, and the code never reads it.
- **Real-language facts** are from my own knowledge unless marked. Figures from memory are marked "≈".

All the scripts are in the scratchpad `lx/` folder: `tally*.py` read the run, `sim.py` runs the current code, and `wold.py`
and `corr.py` read the WOLD file.

## How to read "coverage"

The scale is the same as in the grammar review.
- **Full:** the mechanism exists, and the output shows it.
- **Partial:** the mechanism exists, but it is thinner than the real feature, or it is accidental.
- **Label only:** the page claims the feature, but nothing builds it.
- **None:** there is no mechanism at all.

---

## 1. Summary table

| Language | Distinctive lexical feature | Coverage | Note |
|---|---|---|---|
| **English** | Eskimo-type kinship (lineal vs collateral, sex-neutral *cousin*) | partial | the concepts are English-shaped already; nothing chooses a system |
| | 11 basic colours (B&K stage VII) | partial | every proto starts with the same 7 colour words |
| | Decimal numerals; *eleven/twelve* 'one/two left' | partial | 6–9 are mostly quinary compounds; 11–19 do not exist; the sketch says "decimal" |
| | Loan layers: Norse (core), French (food, law), Latin/Greek (learned) | partial | loans arrive one word at a time from any contact, with no prestige, domain or layer |
| | Animal/meat split (*cow/beef*, *pig/pork*) | none | |
| | Relative frame of reference (left/right) | partial | LEFT, RIGHT and the cardinal points exist; no frame is chosen |
| **Mandarin** | Disyllabic compounding as the main renewal path | full | 274 recipes, generic + specific (`SELF`), longer words after mergers (Nettle) |
| | Descriptive (Sudanese-type) kin: *bófù / shūshu / jiùjiu*, *táng-* vs *biǎo-* cousins | none | there are no FB/MB/FZ/MZ concepts |
| | Five flavours plus *là* 'hot' and *má* 'numbing'; dozens of cooking verbs | partial | 4 tastes and about 8 cooking verbs; no pungent, numbing or savoury |
| | Calques instead of loans (*diànnǎo* 'electric brain') | none | there are no lexical calques; `history.calque` copies typology only |
| | Naming taboo for rulers (*bìhuì*) | none in language | `taboo_defs.ruler_name` exists in the culture layer, and the lexicon never reads it |
| **Japanese** | Three strata (wago, kango, gairaigo) with register doublets (*yama/san*) | none | a loan replaces the old word; it never sits beside it |
| | Two numeral sets (*hitotsu…* / *ichi…*) | none | one word per numeral |
| | Mimetics (giongo/gitaigo), including food textures (*sakusaku*, *mochimochi*) | none | there is no ideophone class |
| | Honorific and humble vocabulary (*taberu / meshiagaru / itadaku*) | none | there are no registers |
| | *ao* grue, later split by *midori* | partial | GREEN~BLUE arises as a CLICS shift (50 lects), never as a stage that later splits |
| **Yoruba** | Ideophones (with tone) | none | |
| | Vigesimal-subtractive numerals (15 = 20 − 5) | none | |
| | Derivation by nominal prefixes (*oní-* 'owner of', *olù-*, *à-*, *ì-*) | partial | 8 affix meanings, one form each; no 'owner of' |
| | Sibling terms by relative age, not sex (*ẹ̀gbọ́n / àbúrò*) | partial | OLDER/YOUNGER SIBLING exist (round 5), but the contrast damping fights the sex merger |
| | Stage II–III colour system (*dúdú*, *funfun*, *pupa*) | none | no lect can have fewer than 5 distinct colour words |
| **Hungarian** | A large derivational suffix set (*-ság*, *-ás*, *-ó*, *-s*, *-talan*, *-ít*, *-gat*, *-hat*, *-né* …) | partial | 8 meanings; no abstract noun, privative, collective, female, ordinal or inchoative |
| | Old Turkic loans for farming and herding (*búza* 'wheat', *ökör* 'ox', *borjú* 'calf') | partial | crops and herds travel with their names (food routes), which is good; herding terms do not |
| | Two basic reds (*piros / vörös*) | none | |
| | Relative-age siblings (*bátya / öcs / néne / húg*) | partial | round 5 concepts; the sex × age grid is incomplete (OLDER/YOUNGER BROTHER, but no sister pair) |
| **Hawaiian** | Hawaiian-type (generational) kinship: *makua kāne* = father and uncles; cousins = siblings | partial (accidental) | FATHER=UNCLE in 20 lects and MOTHER=AUNT in 16, but **both in only 1**; no system |
| | Sibling terms by sex *of the speaker* (*kaikunāne* 'brother of a female') | none | |
| | Counting by fours (*kāuna* 4, *kanahā* 40, *lau* 400) | none | |
| | Small inventory, long words, much reduplication | full / none | word length follows the syllable space (`lexicon.py:664-686`); no lexical reduplication |
| | Staple–relish split (*ʻai* 'staple food' vs *iʻa* 'fish, relish') | none | |
| **Dyirbal** | Jalnguy, the mother-in-law register (same grammar, a smaller and more general vocabulary) | none | `taboo_defs.motherinlaw` and `inlaw_words` exist; the language makes nothing of them |
| | Taboo replacement of words that sound like the names of the dead | partial | taboo is 5% of replacements, for animals and danger words only, and is not tied to the culture's taboos |
| | Few numerals (1, 2, 3, many) | none | every lect has 1–10 (and now 20, 100, 1000) |
| **Pirahã** | No exact numerals (*hói / hoí / baágiso*) | none | |
| | No basic colour terms (descriptive phrases; Everett's claim, debated) | none | |
| | Riverine absolute directions (upriver / downriver / inland) | partial | UPSTREAM and DOWNSTREAM exist as nouns; there is no frame choice |
| | Pronouns borrowed from Nheengatu (Thomason & Everett 2005) | over-covered | the generator borrows pronouns in ~15% of lects, which is Pirahã-level rarity made common |

---

## 2. Why these eight

The brief fixed English. I picked the others so that each lexical axis has at least one strong case, and so that each
language tests a different part of `lexicon.py`.

- **English:** the baseline. Its concept list *is* the generator's concept list (Swadesh, Leipzig-Jakarta and WOLD are
  English-glossed), so English also shows what the generator takes for granted. It also has the clearest loan layers.
- **Mandarin:** compounding as the normal renewal path, descriptive kinship, a rich food and taste lexicon, calquing
  rather than borrowing, and a naming taboo. I chose it over Turkish because Turkish's Arabic and Persian layers are
  covered by English and Japanese, while Mandarin's kin terms and flavour words are not covered elsewhere.
- **Japanese:** stratified loans that keep their native doublets, two numeral sets, honorific vocabulary, and the
  world's best-known food mimetics. It is the main test case for registers and sound symbolism.
- **Yoruba:** ideophones, vigesimal-subtractive numerals, prefixal noun derivation, sibling terms by relative age, and a
  small colour system. It takes the place of Swahili: Swahili's noun-class derivation and Arabic layer are close to what
  Yoruba and English already test.
- **Hungarian:** a rich and productive derivational system (the brief's "Hungarian or Finnish"), and an agricultural and
  herding loan layer from Turkic. That layer is the closest real case to the engine's food routes.
- **Hawaiian:** the type case of generational kinship, a very small inventory (it tests word length), counting by fours,
  and the Oceanic staple–relish split. I chose it over Warlpiri because Hawaiian's kinship type is the one the
  generator's English-shaped concepts can show only by accident.
- **Dyirbal:** the avoidance register (Jalnguy) and taboo replacement. Here the culture layer already has the rules
  (`planet/lineages/taboo_defs.py:95-108`) and the language does not use them.
- **Pirahã:** the lower limit: no exact numbers, no colour terms, and a riverine frame. It also covers the "absolute
  directions" slot. Guugu Yimithirr's cardinal frame comes up under the cross-cutting gaps.

Crow and Omaha kinship do not belong to any of the eight. They come up under §5.2, because the culture layer already
draws the triggers that would justify them: clan exogamy and one-sided cousin marriage.

---

## 3. What the lexicon has, in brief (checked in code)

- **Concepts: 745 in all.**
  - 570 core rows in `planet/language/data/concepts.tsv`: Leipzig-Jakarta, Swadesh 207, and 339 WOLD rows from round 5.
  - The extras in `lexicon.py:288-361`: landscape, 8 directions, 8 kin terms, SIX–TEN, social words, BLUE and BROWN,
    SOUR and SALTY, 6 cooking verbs, 6 food nouns, 31 derived nouns, and the god domains.
  - From the world tables: crops from `crop_defs` (36), herd animals from `animal_defs` (6), fuels (9) and goods (8).
  - Every lect of a run gets the same list, apart from crops and animals the run lacks (`lexicon.py:483`).
- **Word-making sources** (`lexicon.py:72 SOURCES`): derive 0.36, compound 0.22, borrow 0.12, shift 0.10, renew 0.06,
  taboo 0.05 and coin 0.03.
  - **Derivation is table-driven.** `derivations.tsv` has 296 rows and only 8 affix meanings
    (`lexicon.py:154 AFFIX_MEANINGS`): little, place, agent, thing, do, like, cause and intens. Each lect has one form
    per meaning (`:689 _draw_affixes`), all prefixes or all suffixes at 85%.
  - **Compounds come only from recipes.** `compounds.tsv` has 274 rows.
  - **Shifts** follow CLICS3 edges or the 66 `shift` rows.
  - **Proto-lexicons are built by derivation only** (`:704-792`, rows of `_rows_by_target`). A compound recipe, such as
    SIX = FIVE + ONE, can fire only on a later replacement.
- **Contrast sets** (`lexicon.py:125-150`, round 5): kin sex pairs, pronouns, numerals, deixis and the paired directions.
  A shift or colexification that would merge two members is damped to 0.1.
- **Taboo** (`lexicon.py:1530 taboo_word`): 'the brown one' style paraphrases, for concepts flagged `taboo`. These are
  all of `Animals`, plus `_TABOO_CORE` (`:271`, 12 concepts). For every other concept the 0.05 goes to derivation
  (`:1914`).
- **Borrowing on replacement** (`lexicon.py:1831-1873 _replace_word`):
  - The donor is any contact lect that has the concept. It is picked uniformly (`:1846`). There is no prestige, domain or
    contact-kind weighting.
  - When a word cannot be derived, compounded or shifted, it falls back to a loan with chance `BORROW_FALLBACK` 0.35
    (`:1812`).
- **Food routes** (`history.py:658 food_step`): a crop or herd animal arriving from a donor deme brings the donor's word.
  This is the engine's one domain-specific borrowing mechanism, and it works well (crops are 55% loans live).
- **Elaboration by niche** (`lexicon.py:1652 ELABORATIONS`): 6 niches and 22 splits, for example MILK > fresh/soured,
  cattle > CALF/BULL, FISH > sea/river and SNOW > falling/lying. `history.py:913 niche_for` maps only herder, coast,
  farmer and hunter, so **the `mountain` and `cold` splits can never fire**. `niche_weights_from` (`lexicon.py:1676`),
  which would map them, is called nowhere.
- **Not anywhere in `planet/language/`:** kinship-system typology; colour stages; numeral systems (the grammar's
  `numeral_base` is label-only, grammar-gaps §5.2); frames of reference; registers or honorifics; ideophones or sound
  symbolism; lexical reduplication; lexical calques; loan strata or doublets. My grep for kinship, Berlin, vigesimal,
  ideophone, symbolism, honorific and frame found nothing.

---

## 4. Per-language sections

### 4.1 English

**What makes its lexicon distinctive:**
- **Kinship:** Eskimo-type. Lineal kin are kept apart from collateral kin (*father* ≠ *uncle*), *cousin* is
  sex-neutral, and in-laws are marked by *-in-law*.
- **Colour:** 11 basic terms, Berlin & Kay stage VII.
- **Numerals:** decimal. *Eleven* and *twelve* are opaque 'one left' and 'two left', 13–19 add *-teen*, and *score*
  survives.
- **Space:** a mainly relative frame of reference.
- **Loan layers by domain:** Norse in the core (*they*, *sky*, *egg*, *take*); Norman French in law, rank and the
  table, hence the animal/meat split (*cow/beef*, *pig/pork*, *sheep/mutton*); Latin and Greek in the learned register.
  About half the general vocabulary is borrowed, but the Swadesh core is still about 90% native (≈).
- **Word-formation:** productive compounding and derivation (*-er*, *-ness*, *-less*, *un-*, *-y*).
- **Phonaesthemes:** *gl-* 'light', *sn-* 'nose', *-ump*.
- **Food:** a cooking-verb set that is largely French (*boil*, *roast*, *fry*, *stew*, *braise*, *simmer*); *hot*
  colexified for temperature and pungency; *umami* is a 20th-century loan.

**Coverage:**
- **Kinship: partial, by default.** The concepts *are* English: MOTHER, FATHER, UNCLE, AUNT, COUSIN, NEPHEW, NIECE,
  -IN-LAW (OF MAN). An English-type system is what a lect gets when nothing merges. But that is the starting point,
  not a choice the generator makes.
- **Colour: partial.** Every proto has BLACK, WHITE, RED, YELLOW, GREEN, BLUE and BROWN, the 7 terms of stage VI–VII.
  Live, 479 of 627 lects (76%) still have all 7 distinct, 138 have 6, and 10 have 5. None has fewer.
- **Numerals: partial, and inconsistent.**
  - Live, SIX–TEN were last remade as compounds in 62–64% of lects: FIVE+ONE, FIVE+TWO, FIVE+THREE or FOUR+TWO,
    FIVE+FOUR or TEN+ONE, and HAND+TWO for ten.
  - But only 61 lects (10%) have all four of 6–9 as five-plus. The common patterns are mixtures like "6 = 5+1,
    7 = 5+2, 8 = an opaque root, 9 = 5+4" (61 lects) and "5.55".
  - There are no teens. In a24559 TWENTY, HUNDRED and THOUSAND are absent from every lect. In the current list they are
    simple roots with no recipe (`compounds.tsv` has none).
  - The sketch then prints "Counting base: decimal" (drow sketch, line 438) above quinary compounds and "ten < 'hand'".
- **Loan layers: partial.**
  - A loan is one word at a time, from a uniformly picked contact (`lexicon.py:1846`).
  - The donor's prestige plays no part. `history.PRESTIGE_CAP` and `KIND_WEIGHT` drive language shift only.
  - Domain plays no part either: borrowability is not read anywhere (§5.3).
  - A Norman-style layer, cultural words from one prestige donor over one period, cannot form, and neither can doublets.
- **Animal/meat split: none.** There is no MEAT (OF X) concept and no elaboration for it.
- **Derivation: partial.** *-er* is 'agent', *-y* is 'like' and causative is 'cause'. *-ness*, *-less* and *un-* have no
  meaning slot.
- **Food and taste: partial.**
  - SWEET, SOUR, BITTER and SALTY are present.
  - The cooking verbs are COOK, BOIL, ROAST, ROAST OR FRY, BAKE, SMOKE (FOOD), FERMENT, SALT (FOOD) and KNEAD.
  - ROAST (`lexicon.py:329`) and ROAST OR FRY (`concepts.tsv` row 583) are two near-duplicate concepts.
  - There is no pungent/hot word, no TASTE verb, and no TASTY.

**Could a generated lexicon look like English?** Its core and its kin terms, yes. Its history, no: there is no layered
loan vocabulary, no learned register, no 11–19, and no meat names.

### 4.2 Mandarin Chinese

**What makes its lexicon distinctive:**
- **Compounding:** most words are disyllabic compounds: *huǒchē* 'fire-cart' = train, *fùmǔ* 'father-mother' =
  parents.
- **Kinship:** descriptive (Sudanese-type), with separate terms for father's older and younger brother (*bófù*,
  *shūshu*), mother's brother (*jiùjiu*), father's sister (*gūgu*), mother's sister (*yí*), and patrilateral versus
  other cousins (*táng-* vs *biǎo-*). Siblings are by age and sex (*gēge*, *dìdi*, *jiějie*, *mèimei*).
- **Numerals:** decimal, with a unit at 10⁴ (*wàn*), and classifiers.
- **Loans:** few. Buddhist Sanskrit is the main old layer. Modern concepts are mostly calqued (*diànnǎo* 'electric
  brain').
- **Food:** the five flavours (*suān*, *tián*, *kǔ*, *là*, *xián*), plus *má* 'numbing' and *xiān* 'savoury, fresh'.
  A large cooking-verb set: *chǎo*, *zhēng*, *dùn*, *zhǔ*, *kǎo*, *zhá*, *lǔ*, *hóngshāo* and more.
- **Taboo:** emperors' names were avoided (*bìhuì*), and so were homophones of 'four' (*sì* ~ *sǐ* 'die').

**Coverage:**
- **Compounding: full.** This is the lexicon's strongest part.
  - 274 recipes, sourced to Urban 2012 and Brown 1999.
  - Generic + specific renewal (`SELF`: Thai *plaa*-X, English *rein-deer*).
  - Head order follows the typology (`history.head_first_of`).
  - Homophones made by mergers are renewed by longer, built words (`lexicon.py:1811 LONGER_RENEWAL`, after Nettle 1998).
  - PARENTS = FATHER + MOTHER is a recipe.
- **Descriptive kinship: none.** UNCLE and AUNT are single concepts.
  - Their recipes are 'little father' and 'little mother', with Swahili *baba mdogo* and *mama mdogo* cited
    (`compounds.tsv`, `derivations.tsv`). Those Swahili words mean *father's younger brother* and *mother's younger
    sister*, so the recipe narrows UNCLE to one of its four or more senses without the concept knowing it.
  - CLICS3, already in `clics_edges.tsv`, carries FATHER'S BROTHER, MOTHER'S BROTHER, FATHER'S SISTER and MOTHER'S SISTER
    (UNCLE ~ FATHER'S BROTHER in 27 families). The data is there; the concepts are not.
- **Food and taste: partial.**
  - 4 of the 5 flavours. No pungent (*là*), numbing, savoury or TASTY. SWEET ~ TASTY (9 families) and FRAGRANT ~ SWEET
    (8) are in CLICS, but neither concept is on the list.
  - About 8 cooking verbs, against Mandarin's 20 or more in daily use.
  - No STEAM (as a cooking verb), STEW or STIR-FRY.
- **Calques: none.** `history.py:930 calque` copies one or two *typology* features in a language shift. There is no
  loan translation of a donor's compound.
- **Naming taboo: none in the language.**
  - The culture layer draws `ruler_name` ("like-sounding words are changed", `taboo_defs.py:97`) and `dead_soundalike`
    (`:96`). The lexicon never reads them.
  - Its taboo source is animals and danger words only.

**Could a generated lexicon look like Mandarin?** In its word-building, yes; this is where the engine is closest. Its
kin terms and flavour words, no.

### 4.3 Japanese

**What makes its lexicon distinctive:**
- **Three strata:** native wago, Sino-Japanese kango (about half of a dictionary's headwords ≈), and modern gairaigo.
  They sort by register: *yama* versus *-san* 'mountain', and *hajimeru* versus *kaishi suru* 'begin'.
- **Two numeral sets:** native *hitotsu…tō* for counting things up to ten, and Sino-Japanese *ichi, ni, san* for
  everything else.
- **Mimetics:** thousands of giongo and gitaigo. Food texture talk relies on them: *sakusaku* 'crisp', *mochimochi*
  'springy-chewy', *shakishaki* 'crunchy-fresh', *torotoro* 'melting'.
- **Honorific and humble verbs:** 'eat' is *taberu*, honorific *meshiagaru*, humble *itadaku*. Kin terms are humble
  for one's own family and honorific for another's (*haha* versus *okāsan*).
- **Colour:** *ao* once covered green and blue; *midori* took green later.
- **Kinship:** siblings by age and sex (*ani*, *otōto*, *ane*, *imōto*).
- **Coinage:** *umami* was coined in 1908 from *umai* 'tasty'.

**Coverage:**
- **Strata and doublets: none.** A loan *replaces* the native word (`lexicon.py:1846`; `lex.set(new)` in `step`). Two
  words for one concept, split by register, cannot exist in the `Lexicon` data model: `words` is one Word per concept.
- **Two numeral sets: none.** It is the same one-word-per-concept limit.
- **Mimetics: none.** No ideophone class, no reduplication in word formation, and no sound–meaning bias in
  `inventory.draw_word`.
- **Honorific vocabulary: none.** Grammar-gaps Phase D queues politeness for pronouns and verbs. Lexical suppletion of
  the *meshiagaru* kind needs a register slot, which the data model lacks.
- **ao / midori: partial.** GREEN ~ BLUE is the commonest colour colexification live (50 lects, all by CLICS shift, the
  edge seen in 46 families). But it runs backwards: the lects start with two words and *merge* them. Japanese, and the
  B&K sequence generally, *split* a grue term and fill the new slot from an object word, as *midori* did from 'sprout,
  greenery'. The derivation rows for that already exist (`derivations.tsv`: LEAF/GRASS 'like' > GREEN, SKY 'like' > BLUE).
- **Siblings by age: partial.** OLDER BROTHER, YOUNGER BROTHER, OLDER SIBLING and YOUNGER SIBLING are round-5 concepts.
  There is no OLDER/YOUNGER SISTER. Every lect has the full set, so none *lacks* the age distinction.

**Could a generated lexicon look like Japanese?** No. Everything distinctive about it needs more than one word per
concept, or a sound-symbolic class.

### 4.4 Yoruba

**What makes its lexicon distinctive:**
- **Ideophones:** very many. They are often marked by tone and vowel quality for size and intensity (*gbàdàgbàdà* 'big
  and flat').
- **Numerals:** vigesimal with subtraction. 15 is *mẹ́ẹ̀ẹ́dógún*, '5 less than 20'. 16–19 subtract from 20, 25–29 from
  30, and the tens are built on 20.
- **Derivation:** nominal prefixes build agents and abstracts from verb phrases (*oní-* 'owner of': *oníṣòwò*
  'trader'; *a-*, *ì-*, *olù-*). Personal names are whole clauses.
- **Kinship:** sibling terms by relative age with no sex distinction (*ẹ̀gbọ́n* 'older sibling', *àbúrò* 'younger
  sibling').
- **Colour:** a small basic set, *dúdú* 'black', *funfun* 'white' and *pupa* 'red', with other hues as phrases (*àwọ̀
  ewé* 'leaf colour'). Stage II–III.
- **Food:** a staple-heavy vocabulary around pounded yam, cassava and maize (*iyán*, *èbà*, *àmàlà*, *gún* 'pound').
- **Loans:** an Arabic layer in religion, arrived through Hausa.

**Coverage:**
- **Ideophones: none.**
- **Vigesimal or subtractive numerals: none.**
  - NINE = TEN+ONE carries a "subtractive" note ('one from ten': Latin *un-de-viginti*). But the recipe is head TEN +
    modifier ONE, which the engine joins like any other compound, so nothing marks the subtraction.
  - There is no route to 20 as a base.
- **Prefixal derivation: partial.**
  - 'agent' and 'thing' derive from verbs and nouns.
  - 'owner of' and 'having X' are folded into 'like' (`derivations.tsv` 'like' rows), which mixes "X-like" with "having
    X". Those are different affixes in most languages: English *-y* versus *-ed*/*-ful*; Hungarian *-s* versus *-i*.
  - There is no phrase-to-word derivation (no 'one who sells goods').
- **Relative-age siblings without sex: partial.**
  - The age concepts exist.
  - BROTHER ~ SISTER is a contrast set, damped to 0.1 (`lexicon.py:137`). A shared form is also *renewed* as if it were
    an accidental homophone (`_renewal_boost`, `:1764`).
  - So the Yoruba (and Malay *kakak*/*adik*) type, where sex is not lexicalised for siblings at all, is actively pushed
    out. The comment cites CLICS3 for BROTHER ~ SISTER in 29 families. A system-level choice would fit those languages
    better than a damping.
- **Small colour system: none.** At least 5 distinct colour words everywhere, live.

**Could a generated lexicon look like Yoruba?** No. Its numerals, ideophones, colours and sibling system are all out of
reach.

### 4.5 Hungarian

**What makes its lexicon distinctive:**
- **Derivational suffixes:** dozens, freely stacked:
  - nouns: *-ság/-ség* abstract, *-ás/-és* action;
  - adjectives: *-ó/-ő* present participle and agent, *-s* 'having', *-i* 'of a place', *-talan/-telen* privative;
  - verbs: *-ít* causative/factitive, *-ul/-ül* inchoative, *-gat/-get* frequentative, *-hat/-het* potential;
  - kin and diminutive: *-né* 'wife of', *-ka/-ke* diminutive.
  - *Ehetetlen* 'inedible' is *eszik* 'eat' + *-het* potential + *-etlen* privative.
- **Loan layers:** an Old (Bulgar-)Turkic layer in farming and herding (*búza* 'wheat', *árpa* 'barley', *alma*
  'apple', *ökör* 'ox', *borjú* 'calf', *bor* 'wine'), then Slavic, German and Latin.
- **Colour:** two basic reds, *piros* and *vörös*.
- **Kinship:** sibling terms by age and sex (*bátya*, *öcs*, *néne*, *húg*).

**Coverage:**
- **Derivational richness: partial and capped.**
  - There are 8 meanings, and each lect has one form per meaning.
  - `AFFIX_CAP` 0.08 (`lexicon.py:902`) stops any affix on more than 8% of words.
  - `MAX_AFFIXES` is 2 and `MAX_MORPHEMES` 3 (`:161-162`).
  - These caps are sensible against accretion, but they are the same for every lect. Hungarian and Mandarin get the
    same derivational budget, so the "derivation vs compounding" axis is not a property of a language.
  - Missing meanings: abstract or quality noun, action noun, privative, female or 'wife of', collective, ordinal
    (FIRST and SECOND are concepts with no recipe), inchoative, potential, 'of a place', and augmentative.
  - Live, the affixes are often homophonous after sound change (the first live lect: 'place' = 'agent' = /a/,
    'thing' = 'do' = /i/). Real systems tolerate this, but it adds to the thinness.
- **Turkic farm loans: partial, and good where it exists.**
  - Crops and herd animals arriving with a donor bring its word (`history.py:658`).
  - In a24559, 55% of crop words are loans; that is the right signal.
  - What is missing: the *practice* words that travel with a crop or herd (CALF, BULL, PASTURE, PLOUGH, YOKE, CHEESE,
    WINE). The elaborations make CALF and BULL locally, by compounding, never by loan.
- **Two reds: none.**
- **Age-and-sex siblings: partial.** The grid lacks OLDER SISTER and YOUNGER SISTER.

**Could a generated lexicon look like Hungarian?** Its loan *route* for crops, yes. Its derivational density, no.

### 4.6 Hawaiian

**What makes its lexicon distinctive:**
- **Kinship:** the type case of generational kinship. *Makua kāne* is father and every male of his generation, and
  *makua hine* is mother and the women of hers. Cousins are called by sibling terms.
- **Siblings:** named by relative age to a same-sex sibling (*kaikuaʻana*, *kaikaina*) and by sex *relative to the
  speaker*: *kaikunāne* 'brother of a female', *kaikuahine* 'sister of a male'.
- **Sound shape:** 8 consonants and 5 vowels, so words are long. Reduplication is common, colour terms included
  (*ʻulaʻula* 'red', *melemele* 'yellow', *ʻōmaʻomaʻo* 'green').
- **Traditional counting:** in fours, *kāuna* 4, *kanahā* 40, *lau* 400, *mano* 4000.
- **Food:** the Oceanic split between *ʻai* 'staple (poi, taro)' and *iʻa* 'fish, flesh, relish'. Taro has many
  cultivar names.
- **Taboo:** the *kapu* system, including name avoidance for chiefs.

**Coverage:**
- **Generational kinship: partial, and only by accident.**
  - Live, FATHER = UNCLE in 20 lects and MOTHER = AUNT in 16. **Only 1 lect has both.**
  - The merges come from independent CLICS shifts, not from a system, so the output is incoherent: a "father = uncle"
    lect keeps a separate aunt word.
  - COUSIN = SIBLING cannot happen in a24559 (COUSIN is new). In the current code it can only happen by a CLICS shift.
- **Speaker-relative sex: none.** Concepts carry no "of a man / of a woman" variants, apart from the four -IN-LAW
  (OF MAN) rows. Their (OF WOMAN) twins are absent, though CLICS has FATHER-IN-LAW (OF MAN) ~ (OF WOMAN) in 41 families.
- **Small inventory, long words: full.** `length_scale` (`lexicon.py:673`) lengthens roots when the syllable space is
  small (Nettle 1995), and coinages lengthen after mergers.
- **Reduplication in the lexicon: none.**
- **Counting by fours: none.**
- **Staple–relish: none.** There is FOOD, but no STAPLE versus RELISH or SIDE DISH.
  - This split is one of the most culinary-relevant contrasts in ethnography: Oceanic *ʻai/iʻa*, Bantu *ugali* versus
    *mboga*, Chinese *fàn* versus *cài*.
  - The cuisine sheet already computes a `staple` (`cuisine.py:278`).

**Could a generated lexicon look like Hawaiian?** Its word shape, yes. Its kin system, no, except in one lect in 627,
by chance.

### 4.7 Dyirbal

**What makes its lexicon distinctive:**
- **Jalnguy:** an avoidance register used within earshot of a taboo relative (a mother-in-law, or a cross-cousin of
  the opposite sex). It has the same grammar and phonology, but nearly every content word is different, and there are
  fewer of them. One Jalnguy verb often covers several everyday (Guwal) verbs (Dixon 1972, ≈ one Jalnguy word per
  three or four Guwal words).
  - Jalnguy words come from neighbouring languages' everyday words, from sound-shifted native words, and from
    generic-plus-modifier phrases.
- **Taboo replacement:** across Australia, words that sound like a dead person's name are replaced for a time. Dixon
  argues this makes lexicostatistic dating unreliable there.
- **Numerals:** few: 1, 2, 3 and 'many'.

**Coverage:**
- **Avoidance register: none in the language. The culture layer already draws it.**
  - `taboo_defs.py:103` defines `motherinlaw`, "a man may not look at or speak to his mother-in-law".
  - `:98` defines `inlaw_words`, "a wife avoids words that share a syllable with her parents-in-law's names". That is
    the Bantu *hlonipha* type.
  - `cuisine.py:47` already uses `motherinlaw` for "who eats together". The lexicon never reads either taboo.
- **Taboo replacement: partial, and decoupled.**
  - In the replacement draw, taboo is 0.05, and only for `c.taboo` concepts (`lexicon.py:440`, `:271`). That is a
    hunting or danger taboo, as with the bear in IE.
  - Live, 1,424 taboo steps sit in the ancestries of living words, over 45 concepts. 355 of 627 lects have a current
    taboo word.
  - But the rate is the same in a culture with `dead_soundalike` as in one without. A culture-driven name taboo would
    hit *any* word that sounds like a name, so it should raise replacement across the lexicon, not only for animals.
- **Few numerals: none.**

**Could a generated lexicon look like Dyirbal?** No. Its two defining lexical facts are drawn in the culture layer one
package away, and nothing carries them over.

### 4.8 Pirahã

**What makes its lexicon distinctive:**
- **Numbers:** no exact number words. *Hói* means 'small amount', *hoí* 'larger amount', and *baágiso* 'many' (Everett
  2005; Frank et al. 2008).
- **Colour:** no basic colour terms. Colours are described by phrases. This is Everett's claim, and it is debated.
- **Kinship:** a minimal set.
- **Space:** riverine absolute directions: upriver, downriver, and into the forest.
- **Pronouns:** borrowed from Nheengatu (Thomason & Everett 2005). This is one of the very few known cases of a borrowed
  first-person pronoun.
- **Speech modes:** whistled and hummed speech.

**Coverage:**
- **No numerals: none.** Every lect has ONE–TEN, and the current list adds TWENTY, HUNDRED and THOUSAND, whatever its
  people's population or way of life. Restricted systems are a real WALS 131A type (≈ 10% of languages).
- **No colour terms: none.**
- **Riverine frame: partial.** UPSTREAM and DOWNSTREAM exist as concepts (`lexicon.py:299`), with recipes 'river head'
  and 'river mouth'. Nothing makes them the *primary* frame. The exonym builder (`names.py:736 direction`) always uses
  NORTH, SOUTH, EAST and WEST.
- **Borrowed pronouns: over-covered.** Live, I is borrowed in 15% of lects, THOU in 16% and WE in 12%. WOLD's borrowing
  scores are I 0.03, THOU 0.04 and WE 0.01. What is famous in Pirahã because it is rare, the generator does several
  times more often than the WOLD sample (§5.3).

**Could a generated lexicon look like Pirahã?** No. The engine has no "less": every lect has every concept.

---

## 5. Cross-cutting picture

### 5.1 Missing entirely

1. **Kinship-system typology.** There is no choice of Hawaiian, Eskimo, Iroquois (bifurcate merging), Sudanese
   (descriptive), Crow or Omaha. The concepts are English's, the CLICS edges that would carry other systems (FB, MB, FZ
   and MZ, parallel and cross cousins) are left out, and merges are independent per pair.
2. **Colour stages (Berlin & Kay).** Every proto starts with 7 terms and can only lose distinctions, by shift. The
   real history runs the other way: composites split, and the new terms come from object words or loans.
3. **Numeral systems.**
   - No base is chosen. The grammar's `numeral_base` is label-only (grammar-gaps §5.2).
   - There are no teens or tens, no vigesimal or quaternary systems, no subtraction, and no restricted systems.
   - 6–9 are remade one item at a time, so a lect ends up with a patchwork.
4. **Frames of reference.** None of absolute (cardinal, riverine, uphill/downhill, seaward/landward), relative or
   intrinsic is chosen. The concepts exist, but no lect prefers one frame.
5. **Registers.** No avoidance (Jalnguy, *hlonipha*), honorific (Japanese, Javanese *krama*) or learned register. The
   data model is one word per concept per lect.
6. **Ideophones and sound symbolism.**
   - No ideophone class and no lexical reduplication.
   - No nursery-word bias: MOTHER and FATHER with *m/n* and *p/t/b* (Murdock 1959; Jakobson 1960). This is the
     strongest sound–meaning pattern in the world's lexicons, and the engine draws these two words like any others.
   - None of the sound–meaning associations of Blasi et al. 2016 (PNAS 113:10818), such as *i* for 'small', nasals for
     'nose' and *r* for 'round', which hold across about 6,000 word lists.
7. **Loan strata, doublets and calques.** A loan always replaces. No donor is preferred for prestige. Technology and
   faith bring no learned words. There are no loan translations.
8. **Speaker-relative and generational kin terms.** There are no OF WOMAN variants, no sex-of-speaker sibling terms, and
   no relative-age sister terms.
9. **The culture-to-lexicon link.** The culture layer draws speech taboos (`dead_name`, `dead_soundalike`,
   `ruler_name`, `inlaw_words`), avoidance (`motherinlaw`, `fatherinlaw`), cuisine (staple, dairy, cheese, fermentation,
   fuel cooking) and ways of life. The lexicon reads only the ways of life (four niches) and the crop and herd arrivals.

### 5.2 Modelled too thinly

- **Kinship coherence.**
  - Live, sibling merges (BROTHER = SISTER, 114 lects in a24559) and WIFE = WOMAN (96) are plausible.
  - Bifurcate and generational merges are isolated: F=FB-type in 20 lects and M=MZ-type in 16, with only 1 lect having
    both. Real systems are coherent: a language that calls the father's brother 'father' (bifurcate merging) also calls
    his children 'sibling'.
  - Round 5's contrast damping (`lexicon.py:125-150`) cuts the sibling merges, which is right for incoherent noise. But
    it also blocks the real relative-age-only type.
  - Crow and Omaha skewing needs descent, and the culture layer already has the triggers: `clan_exogamy`,
    `cousin_one_side` and `totem_marry` (`taboo_defs.py:100-102, 87`). CLICS's FATHER-IN-LAW ~ MOTHER'S BROTHER (13
    families) is the Dravidian cross-cousin-marriage signature, and it is sitting unused in `clics_edges.tsv`.
- **Derivational inventory.**
  - 8 meanings, one form each, and the same caps for every lect.
  - No per-lect "derivational richness" axis, so Hungarian-type and Mandarin-type lexicons cannot differ.
  - 'like' carries both "X-like" and "having X".
- **Food and taste vocabulary** (§5.4).
- **Taboo.**
  - The taboo source is fixed at 0.05, on animals and danger words. It ignores the culture's taboos.
  - The paraphrase is always quality + 'agent'/'thing' from 13 qualities (`lexicon.py:797 _QUALITY`). Real taboo
    replacement also borrows from neighbours (Jalnguy), distorts the old form (Australian, IE *bear*-type metathesis),
    and uses kin-term euphemism ('grandfather' for the bear or tiger).
- **Elaboration.**
  - 22 splits in 6 niches. Two niches (`mountain`, `cold`) are unreachable (`history.py:913` maps four).
  - No elaboration follows tech or cuisine (cheese known → cheese words; rice staple → COOKED RICE ~ RICE, which CLICS
    attests in 7 families).
  - Nothing follows the herd beyond CALF and BULL. The Nuer-type cattle colour and horn vocabulary, which is the classic
    lexical-elaboration case, is out of reach.
- **The basic lexicon's shape.** Every lect has the same 745 concepts. There is no "less": no restricted numerals, no
  missing colour terms, no absent BLUE. There is also no "more" beyond 22 niche splits.

### 5.3 Exists but wrongly calibrated

**Borrowing runs against real borrowability.**

- **The overall measure.** Over the 273 meanings shared by a24559's lexicons and WOLD:
  - Spearman's ρ between the generator's live share of current words that are loans and WOLD's `BORROWING_SCORE` is
    **−0.13**.
  - The means agree (0.156 against 0.151), but the *ordering* is slightly inverted.

| Meaning | Live loan share (a24559) | WOLD borrowing score |
|---|---|---|
| WE / I / THOU | 0.12 / 0.15 / 0.16 | 0.01 / 0.03 / 0.04 |
| ONE / TWO / THREE / FOUR | 0.36 / 0.39 / 0.35 / 0.35 | 0.13 / 0.23 / 0.22 / 0.21 |
| YEAR / HOUSE | 0.43 / 0.45 | 0.19 / 0.11 |
| FIRE / WATER | 0.07 / 0.10 | 0.04 / 0.09 |
| (current-code sim) food things: MEAT, SOUP, FLOUR, BUTTER, BREAD, BEER, POT, BOWL | 0.13 of replacements | SOUP 0.53, BUTTER 0.49, BREAD 0.48, BEER 0.68, POT 0.33 |
| (current-code sim) house and clothing: ROOF, DOOR, WINDOW, SHOE, CHAIR, PILLOW | 0.16 of replacements | DOOR 0.23, SHOE 0.45; WOLD field "the house" 37%, "clothing" 39% |

- **Cause** (`lexicon.py:1831-1873`):
  - A word with no derivation row, no compound recipe and no shift edge falls through to a loan with
    `BORROW_FALLBACK` 0.35. With a contact present, that is nearly the only way it can change.
  - Closed classes are exactly those words: pronouns, low numerals, and words like YEAR. Contrast damping makes their
    shifts rarer still (round 5).
  - Cultural nouns, by contrast, have recipes (SOUP = WATER + MEAT, BUTTER = FAT + MILK), so they are mostly *built*.
  - The result is that **the least borrowable items are borrowed most, and the most borrowable are built at home.**
- **The current code does the same.** The synthetic run (`lx/sim.py`) gives these shares of replacements that are loans:

| Group | Loan share of replacements |
|---|---|
| low numerals | 73% |
| pronouns | 36% |
| religion | 40% |
| house and clothing | 16% |
| food things | 13% |
| colours | 16% |

- **WOLD's per-field figures** (Tadmor 2009; secondary reproduction, check before quoting): religion 41.2%, clothing
  38.6%, the house 37.2%, law 34.3%, social and political 31.0%; sense perception 11%, spatial relations 14%, the body
  14.2%; 24.2% overall.
- **The live figures by field are flat.** Kinship 18%, the body 16%, sense perception 12%, and Quantity 27%, the
  highest core field. Only crops (55%, from the route mechanism) and the single HOUSE concept stand out.
- **The fix data is already in the repo.** `data/language/raw/wold/Haspelmath-2009-1460.tsv` has `BORROWING_SCORE`
  for all 1,460 meanings, and `build_reference_tables.py` already reads this file for the concept list. It simply drops
  that column.

**Colour colexifications partly violate B&K.**
- Composites of the attested kinds appear: GREEN~BLUE 50 lects, RED~YELLOW 36, YELLOW~GREEN 25, BLACK~BLUE 10.
- So do rarer or unattested ones: YELLOW~BLUE 10, WHITE~YELLOW 10, RED~BLUE 3. These come from CLICS edges of 6 families
  or fewer, often by chained shifts.
- The 50 grue lects all keep a distinct BROWN. That is the reverse of the B&K order, where blue comes before brown.

**Numerals.**
- Live, five-plus 6–9 (quinary-decimal) is the commonest pattern for 6–9, in about 60% of lects.
- WALS 131A (≈): 125 of 196 languages decimal, 22 hybrid vigesimal-decimal, 20 pure vigesimal, 20 restricted, and only
  a handful with a 5-based or other base.
- The compound recipes, the only replacement path for numerals, are mostly quinary, and they are drawn per item.

**Diminutive renewal is very visible in the core.** In the drow sketch (`sketches/d725-drow.md:337-350`), fish, tree,
bone, mouth and many are all 'X + little' renewals with the same affix. `RENEW_CAP` 0.02 (`lexicon.py:176`) applies to
the whole lexicon, not to the core 100. Romance does this (*oreille*, *soleil*, *abeille*), but five in a 45-word sample
reads as a tic. Recheck this on the next run.

**Small data errors.**
- `compounds.tsv` row 217 glosses Hungarian *nagybátya* as "'big brother'". It means 'uncle', literally 'big
  older-brother'.
- ROAST (`lexicon.py:329`, CLICS ROAST (SOMETHING)) and ROAST OR FRY (`concepts.tsv` row 583) duplicate one meaning.
- `Concept.base` (`lexicon.py:243`), which `_CORE_BASE` (`:278`), `_CROP`, `_ANIMAL`, `_FUEL`, `_GOOD` and `_EXTRA`
  fill, is **read nowhere**. Its docstring says "related concepts a new word is built from when CLICS gives none", but
  only `derivations.tsv` and `compounds.tsv` rows are used. Either wire it in or delete it.
- `niche_weights_from` (`lexicon.py:1676`) is unused, and the `mountain` and `cold` elaborations are unreachable.
- `names.py:9`: E9 'the free' needs a FREE concept the lexicon lacks. This is known; it is noted in the module.

### 5.4 Food and taste vocabulary, against the culinary end goal

**What exists.**
- **Food acts (current list):** EAT, DRINK, CHEW, SUCK, GRIND, KNEAD, COOK, BOIL, ROAST, ROAST OR FRY, BAKE,
  SMOKE (FOOD), FERMENT and SALT (FOOD).
- **Food things:** FOOD, MEAT, MILK, BUTTER, EGG, HONEY, FRUIT, BREAD, BEER, SOUP, FLOUR, SALT and BEVERAGE.
- **Vessels and tools:** POT, BOWL, JUG and MORTAR.
- **Food states:** RAW and COOKED.
- **Tastes:** SWEET, SOUR, BITTER and SALTY.
- **From the world tables:** 36 crops, 6 herds and 9 fuels, plus the MILK, CALF and BULL elaborations.
- About 35 concepts in all, plus the crops. The route mechanism for crop names is a real strength: each word carries
  its hop list.

**What the cuisine sheet knows and the lexicon cannot say** (`planet/lineages/cuisine.py`):
- cheese, soured or fermented milk (kumis, kefir), wine, cider, palm wine, sorghum or millet beer, spirits (distilling),
  infusions and cacao drinks (`:36-40`, `:313-341`);
- fuel-specific cooking: ember baking, griddles, all-day braises, smoke-flavouring (`FUEL_COOK`, `:51`);
- who eats together, and meal taboos (`:41`);
- what outsiders get wrong.

The sheet writes all of this in English. No line of it can be glossed in the people's own words.

**Missing concepts, by the culinary-dnd spine** (fuel, staples, techniques, drink, implements, etiquette):
- **Staple and meal:** STAPLE versus RELISH or SIDE DISH (the Oceanic, Bantu and Chinese split), PORRIDGE or GRUEL,
  DOUGH, MEAL, FEAST, BREAKFAST, HUNGER and THIRST. CLICS has FAMINE ~ HUNGER in 19 families.
- **Techniques:** STEW or SIMMER, STEAM, FRY as distinct from ROAST, DRY or CURE, PICKLE, POUND (it is a base in
  `derivations.tsv` but not a concept), SKIM, CHURN, CURDLE, BREW, DISTIL, LEAVEN and SOAK.
- **Products:** CHEESE (WOLD 0.66), WINE (0.74), OIL (FOOD), VINEGAR, YOGURT or SOUR MILK (elaboration only), BLOOD
  (as food), FAT (as food), SPICE and PEPPER (0.66).
- **Taste and smell:** TASTE (verb and noun; TASTE ~ TRY is in 16 families), TASTY, PUNGENT or HOT (spicy), SAVOURY,
  ASTRINGENT, BLAND, RICH or FATTY, FRAGRANT, STINKING (ROTTEN ~ STINKING in 15 families), and texture words (crisp,
  chewy, slimy). The texture words are where ideophones would earn their keep.
- **Implements:** OVEN, HEARTH (present, as a god domain), GRIDDLE, SPIT or SKEWER, SPOON, LADLE, SIEVE and
  QUERN (GRIND covers the act).
- **Colexifications already in `clics_edges.tsv`, unusable because a member concept is missing:** BITTER ~ SOUR (22),
  BITTER ~ SALTY (12), SALTY ~ SOUR (12) (these three *are* usable), RAW ~ UNRIPE (27), COOKED ~ RIPE (23),
  BAKE ~ ROAST OR FRY (17), SWEET ~ TASTY (9), FRAGRANT ~ SWEET (8), BOIL ~ COOK (13) and COOKED RICE ~ RICE (7).

**Elaboration is the right tool, but it is keyed to the wrong inputs.**
- It is keyed to four niche weights. It should also key to what the cuisine sheet computes:
  - a dairy herd plus cheese known → CHEESE, CURD, WHEY and churn words;
  - a grain staple → its porridge, bread or beer, named from the grain word;
  - a fuel → the cooking verbs that fuel favours.
- Real languages elaborate exactly where their cuisine is: Mongolian dairy vocabulary, Japanese rice (*ine*, *kome*,
  *gohan*), Nuer cattle.

---

## 6. Ranked recommendations

**Value** is how much more real-looking the output gets, and how much it serves the culinary goal (H/M/L). **Cost**
follows the grammar review:
- **S:** under a day; a few functions and tests.
- **M:** a few days; new data plus mechanism.
- **L:** a week or more, or a change to the data model.

| # | Recommendation | Value | Cost | When |
|---|---|---|---|---|
| 1 | **Borrowability by meaning.** Read WOLD's `BORROWING_SCORE` (already downloaded; add it as a `concepts.tsv` column in `build_reference_tables.py`). Scale the borrow source and `BORROW_FALLBACK` by it. Make the fallback for contrast-set members (pronouns, numerals) "keep the old word". Measure Spearman ρ against WOLD on the next run (now −0.13). | H | S | Before merge |
| 2 | **Food, taste and cooking concepts tied to the cuisine sheet.** Add the §5.4 concepts with recipes, and the CLICS edges that come with them. Key elaboration to techtree and cuisine facts (dairy and cheese, fermentation, grain staple, fuel). Add a staple–relish split. Optionally let the cuisine sheet print the people's word beside each English line. | H (end goal) | M | First after merge (concepts and recipes alone are S) |
| 3 | **A numeral system per proto.** Choose a base (decimal, vigesimal or hybrid, a quinary-decimal sub-pattern, quaternary, restricted), weighted from WALS 131A. Build 6–9, 11–19, the tens, 20, 100 and 1000 *consistently* by recipe (adding, multiplying, sometimes subtracting). Let a restricted system skip numbers above 3 for small forager peoples. This makes the sketch's "counting base" label true. | H | S–M | Before merge (the label is already printed) |
| 4 | **A kinship system per proto.** Choose Hawaiian, Eskimo, Iroquois, Sudanese, Crow or Omaha, weighted by descent. Use `clan_exogamy` and `cousin_one_side` from the taboo draw where present: unilineal descent leans Iroquois, Crow or Omaha, and cross-cousin marriage leans Dravidian. Add the concepts the systems need: FB, MB, FZ, MZ; parallel and cross cousin; OLDER/YOUNGER SISTER; and the (OF WOMAN) in-laws (the CLICS rows exist). Build kin words by *merging* concepts per system (one word for F and FB). Replace the per-pair contrast damping for kin with the system's own contrasts. Show a kin table in the sketch. | H | M | Later (first) |
| 5 | **Colour by Berlin & Kay stage.** Draw a proto stage (II–VII) and start with its composites (light/warm, dark/cool, grue, yellow-green). Over time, split a composite with a new word from the existing 'like' rows (LEAF > green, SKY > blue, ASH > grey) or from a loan. Drop the shifts that make RED~BLUE and YELLOW~BLUE. Keep BROWN after BLUE. | M–H | S–M | Before merge if cheap |
| 6 | **Culture-driven taboo and avoidance.** Scale the taboo source by the culture's speech taboos (`dead_soundalike`, `ruler_name`: any concept, not just animals; Dixon's Australian turnover). Widen the paraphrase sources: loans from neighbours, form distortion, kin-term euphemism. Add a second, smaller **avoidance lexicon** for cultures with `motherinlaw` or `inlaw_words`, built Jalnguy-style from generic words, neighbours' words and paraphrase. This needs #11's data model for a second word per concept, or it can be a separate table. | M–H | M | Later |
| 7 | **A richer, per-lect derivational inventory.** Add meanings: abstract or quality ('-ness'), action noun, privative, 'having/owner of' (split from 'like'), female, collective, augmentative, ordinal, inchoative and 'of a place' (the last also feeds demonyms in `names.py`). Give each lect a derivational-richness draw that scales `AFFIX_CAP` and the derive/compound split, so Hungarian-like and Mandarin-like lexicons differ. | M | M | Later |
| 8 | **Sound symbolism.** A nursery-word bias for MOTHER and FATHER (and grandparent terms): nasal and labial or dental onsets, reduplicable, re-coinable. Mild Blasi et al. 2016 biases in `draw_word` for SMALL, NOSE, TONGUE, ROUND and similar. Cheap, and very visible in a core-100 table. | M | S | Before merge |
| 9 | **An ideophone class.** Reduplicated, phonotactically marked words for sounds, textures, motion and light, made by lects whose typology leans that way (Yoruba, Japanese, Korean). Use them for food textures in the glossed recipe text (grammar-gaps Phase D). | M | M | Later |
| 10 | **Frames of reference.** Per lect: absolute (cardinal, riverine, uphill/downhill, seaward/landward, chosen from the people's landscape), relative or intrinsic. It decides which direction words are frequent and stable, and which ones `names.py` uses for exonyms. Add SEAWARD, LANDWARD, UPHILL and DOWNHILL. | M | S–M | Later |
| 11 | **Loan strata and doublets.** Allow a second word per concept with a register tag (native/learned/polite). Weight donors by prestige and contact kind (`history.KIND_WEIGHT`, `PRESTIGE_CAP`). Bring learned or cultural loans with technology and faith spread (writing, metal, temples). Add calques: copy the donor's compound recipe with native parts. This is the data-model change that #6's avoidance register and Japanese-style numeral sets also need. | H | L | Later |
| 12 | **Tidy-ups.** Fix the *nagybátya* gloss; merge ROAST into ROAST OR FRY; wire in or delete `Concept.base`; route `mountain` and `cold` into `niche_for` (or delete them and `niche_weights_from`); add a recipe for TWENTY, HUNDRED and THOUSAND (part of #3). | L | S | Before merge |
| 13 | **Herd and crop practice words travel with the route.** When a crop or herd arrives, borrow a small bundle with it: CALF, MILK (SOURED), PLOUGH, YOKE and CHEESE for herds; the bread or beer word for grains. This is the Hungarian–Turkic and English–French pattern, and it extends the route mechanism already in `history.food_step`. | M–H | S–M | With #2 |
| 14 | **Lexicon size by way of life.** Let lects *lack* concepts. Small forager peoples with a restricted numeral system have no HUNDRED. A stage-II colour lect has no BLUE. A people with no kings has no KING. The sketch shows the gap as a phrase. | M | S (once #3 and #5 exist) | Later |

**Before the first merge**, items 1, 3 (the base and teens), 5 (stage start), 8 and 12 are all S or S–M:
- Item 1 removes the clearest calibration error: inverted borrowability.
- Item 3 makes a printed label true.
- Items 5 and 8 change the look of every core table at little cost.

Item 2 is the highest-value item for the culinary goal. Its concept-and-recipe half is S, and its link to the cuisine
sheet is M. Items 4 and 11 are the two large ones. They should be scheduled in that order, because #11's data model
also unlocks #6.

---

## 7. Caveats

- The live figures come from a24559, which predates round 5. It has no WOLD concepts and the older
  `BORROW_FALLBACK` 0.5. The synthetic run on the current code shows the borrowability inversion survives, but it is a
  two-lect toy, not a world.
- WOLD's `BORROWING_SCORE` is a graded likelihood averaged over 41 languages, not a share of lects. The comparison is
  about rank order, which is why I report Spearman ρ.
- Tadmor's per-field percentages come from a secondary reproduction, and WALS 131A from memory (≈). Check both before
  quoting.
- Statements about real languages are from my general knowledge (Dixon 1972 for Dyirbal; Everett 2005 and Frank et al.
  2008 for Pirahã; Berlin & Kay 1969 and Kay et al. 2009 for colour). Check exact forms before they go on a public page.

Sources checked during this review:
- [Tadmor field figures, reproduced (Linguistik Online)](https://bop.unibe.ch/linguistik-online/article/download/1373/2319)
- [World Loanword Database note (Language Hat)](https://languagehat.com/world-loanword-database/)
