# Contact, sociolinguistics and variation: eight real situations against the generator

Branch `lang-design` at 2ab724ea. This was a read-only review: nothing was changed. Code paths are relative to the
worktree. "Live" figures are from run a24559's 573 living dominant lects (plus 54 living minority lects), tallied
read-only from `runs/a24559/languages.json`. The scripts are in the scratchpad folder `reviews/cg/`. Figures for real
languages are from memory unless a source is named. WOLD figures (Haspelmath & Tadmor 2009) are rounded and marked "≈".

**Run a24559 predates several changes.** It was written on 11-04. Since then, `BORROW_FALLBACK` went from 0.5 to 0.35
(`lexicon.py:1812`), `kin_close` and the shift caps changed, and round 5 added vocabulary such as KING, MERCHANT and
WHEEL. Where a live figure may have moved, I say so.

## How to read "coverage"

The scale is the one the grammar review uses (`grammar-gaps.md`):
- **full**: the mechanism exists, it is driven by the world, and the output shows it.
- **partial**: the mechanism exists but is thinner than the real thing, or it is mis-calibrated.
- **label only**: the output names it, but nothing produces it.
- **none**: no mechanism at all.

---

## 1. Summary table

| Situation | Distinctive mechanism | Coverage | Note |
|---|---|---|---|
| **English** (Norse, Norman French) | Loans scale with contact intensity: Norse reached basic words and pronouns (*they*, *egg*, *take*); French brought a register-stratified layer (*cow/beef*, *ask/question/interrogate*) | partial | Loans exist (17% of the median lexicon), but at a flat rate. Lexical loans ignore intensity and prestige (§5.1). |
| | Phonemes come in with loans (/v z ʒ/ split off as phonemes) | none | Every loan is nativised by `hear_word` (`lexicon.py:1624`). |
| | Simplification under adult L2 contact (Norse and Danelaw koine: loss of gender and case) | partial | `grammar.social_factors` strips bound grams by l2² (`grammar.py:1735`). The L2 proxy is high almost everywhere (median 0.53). |
| | Prestige register (learned French and Latin vocabulary) | none | There is no register and no learned-loan channel. |
| **Balkan Sprachbund** | Grammar converges across four families: postposed article, loss of the infinitive, future from WANT, clitic doubling, a schwa | none | Typology drift re-draws values from global marginals (`grammar.py:804`). Cross-family neighbours are no more alike than distant pairs (0.545 vs 0.544 agreement). |
| | Areal phonology | partial | 27% of living sound changes arrive by the wave, 75% of those across families. Yet cross-family neighbours' inventories are no more alike than distant ones' (Jaccard 0.285 vs 0.288). |
| **Irish and Manx → English; Celtic and Indian English substrates** | Shift within 3–5 generations once tipped; language death; substrate in phonology and syntax, few words | partial | Shift, minority speech and its death, accent and calques all exist (`history.py:529-656`). But each shift keeps 64 words, including the same 14 Swadesh-100 words every time (DOG, TREE, BIRD, LOUSE …). Bilingualism lasts a median 3 kyr before the shift and 3 kyr after it. |
| **Tok Pisin** | A pidgin forms in a many-language labour or trade setting, then creolises: one lexifier, substrate grammar, analytic TMA | none | Lects have one parent. A mixed city either levels (koine) or shifts. |
| **Michif / Media Lengua** | A mixed language, with grammar from one source and lexicon from the other, made by a new identity | none | Shift is all-or-nothing: `ruler.copy()` plus local words. |
| **Swahili** | A lingua franca carried by trade and caravans; L2 speakers outnumber L1; L2 varieties drop concord; heavy Arabic loans from trade and faith | label only | "The Common" is the lect holding the most mixed cities (`names.py:778`), a naming device. The "trade" trigger is co-residence (`inputs.py:700`). No trade routes, no vehicular variety. |
| **Arabic** (diglossia, liturgy, continuum) | H (Classical, Qur'anic) is frozen by a faith over L dialects; learned loans from H; a continuum with unintelligible ends | none / partial | No faith wiring, no register, no frozen standard. Continua are detected (`families.py:208`) but rare: 5 chains, all of length 3. 510 of 587 "languages" have one lect. |
| | (Latin and Sanskrit as liturgical and prestige languages: doublets, *tatsama/tadbhava*) | none | `gods.json` (faiths, conversion) is not read by the language pass. |
| **Vaupés** (linguistic exogamy) | Marriage must cross language lines; everyone speaks 4–5 languages; purism keeps the vocabularies apart while grammar converges (Tariana took Tukanoan evidentials) | none | Minority speech per deme is the only multilingualism. No purism, no structural borrowing. `taboos.py:185` draws clan exogamy as a readout only. |
| (Japanese honorifics, Javanese speech levels) | Grammaticalised social register | none | Already queued as Phase D "politeness and honorifics" (`grammar-gaps.md` Phase D). Cross-referenced in §5.5. |
| (Wave model vs tree model) | Both at once | full (mechanism) | Budding builds the tree; rules spread by wave, gated by prestige and generation length (`history.py:266-292`). The outcome check is missing (§5.2). |

---

## 2. Why these eight

I wanted each situation to test a different lever of the engine, and together to cover the Thomason & Kaufman (1988)
outcome space: borrowing, shift with interference, convergence, and the three "new language" outcomes (pidgin, creole,
mixed language).

- **English**: borrowing at two intensities from two donors, register stratification, phonemes imported by loans, and
  L2 simplification, all in one well-documented case. It tests the borrowing channel and the L2 channel together.
- **Balkan Sprachbund**: convergence with no single dominant donor and with grammar more than words. It tests whether
  typology and grams diffuse, or only sound rules.
- **Irish and Manx**: shift and death with dates (Manx's last native speaker died in 1974), plus the substrate those
  shifts leave in Hiberno-English (the *after*-perfect, habitual *do be*, dental stops). I folded in the Indian English
  substrate (retroflex /t d/, syllable timing) because it is the same mechanism with different input. It tests
  `shift`, `accent`, `calque` and the minority speech.
- **Tok Pisin**: the pidgin-to-creole path. Nothing in the engine can produce it yet, and the world's mixed cities are
  the obvious place it could arise. I picked it over Haitian or Sranan because its substrate (Tolai) and its
  grammaticalised TMA (*bai* < *by and by*, *bin*, *save*) are well described.
- **Michif and Media Lengua**: mixed languages. They test whether lect parentage can be anything but a tree. I paired
  them because they split differently: Michif by part of speech (Cree verbs, French noun phrases), Media Lengua by
  layer (Quechua grammar, about 90% relexified from Spanish).
- **Swahili**: a lingua franca whose spread followed trade and states, not population. It tests the trade, polity and
  faith wiring (Arabic loans came with both trade and Islam).
- **Arabic**: diglossia, a liturgical H frozen by a faith, and a continuum, all in one language. Latin, Sanskrit and Pali
  come in here as further liturgical cases, and Dutch–German as a further continuum. It tests faith wiring, registers,
  and the line between dialect and language.
- **Vaupés**: the counter-case. Contact is intense and lifelong, yet the vocabularies stay apart by ideology while the
  grammar converges. It tests whether attitudes and marriage rules (both modelled in `planet/lineages/`) could gate
  borrowing.

I left Japanese honorifics out of the eight because the grammar review's Phase D already queues them. They come back
in §5.5, where the polities and taboos data could drive them.

---

## 3. What the engine has, in brief (checked in code)

- **One lect per deme** (`history.py:130 add`). It buds as a copy when a deme splits (`:193 birth`). A shifted deme's
  old lect lives on as **minority speech** until its share falls under `MINORITY_MIN` 0.1 (`:62`, `:564-573`).
- **Wave** (`history.py:266-292`). Each sound rule that fires in a lect is offered to every contact lect with
  p = tanh(WAVE_K · contact · prestige ratio / 2) × min(1, giver gen / receiver gen). It is damped by ease, size and tone
  hearing (`:286-290`). Contact = (shared cells + half the border edges) / the smaller deme (`inputs.py:366`).
  Prestige = population × (1 + 0.5 · {cities, writing, law}) × (1 + 0.05 · towns + 0.5 · cities)
  (`inputs.py:438-445`). Architecture §8 specifies a ruler bonus; the code has none.
- **Lexical borrowing** happens only when a word is replaced. "borrow" is 12% of the source weights (`lexicon.py:72`),
  plus a fallback of 0.35 when nothing else can build the word (`:1812`, `:1841`). The donor is drawn **uniformly** from
  the contact lects that have the concept (`:1846`). A contact lect is any lect with contact ≥ 0.1, plus the other speech
  of the same deme (`history.py:241-247`). Contact intensity, prestige, bilingual share and the concept's borrowability
  play no part. Architecture §8 says "lexical borrowing uses the same contact weights"; the code does not.
- **Food routes** (`history.py:658-731`). A crop or animal arriving from a donor deme brings the donor's word, so the
  etymology traces the route. This is the one channel tied to a real cultural flow.
- **Shift** (`history.py:529-619`). Triggers come from the stored history (`inputs.py:554-731`): elite (incursions),
  takeover (settlement holders), swamp, city and "trade". Each pushes a share up by SHIFT_K · kind · strength ·
  √prestige · presence per generation. At a share of 0.5 the deme takes a copy of the ruler's lect and keeps three things
  from the old one:
  - substrate words for every concept in the fields "Animals" and "Agriculture and vegetation", plus 9 landscape words
    and names (`lexicon.py:272-273`, `:1962-1990`);
  - an accent, in which each sound the old lect lacked is replaced by the nearest old sound with chance 0.5
    (`history.py:621-656`);
  - 1–2 typology features copied at random from the old grammar (`history.py:930-946`).
- **Koine** in mixed cities (`history.py:385-476`). Sounds most heads cannot make are replaced. A same-language
  minority levels toward the majority lect: wave at p = 1, and core words borrowed at 0.1 per interval.
- **Adult L2.** `inputs.l2_share` (`inputs.py:402-418`) is other peoples' presence on the deme's cells × 0.6, plus the
  heads in the mixed cities it holds, clipped at 0.7. It raises gram loss and stripping (`grammar.py:1735-1747`, strip
  × l2²) and typology drift. A re-drawn morphological feature goes to its simplest value with chance l2/2
  (`grammar.py:820-829`, `SIMPLE_VALUE` `:561`). It does not touch the lexicon or the sound rules.
- **Dialect vs language.** A language is a scholars' UPGMA cluster at a blind core share of 0.7 (`families.py:25`,
  analyse). Intelligibility is symmetric: cognate share × form distance × a word-order and case penalty
  (`families.py:159-197`). Continua are detected and reported (`families.py:208-250`).
- **Not read by the language pass at all:** `gods.json` (faiths, conversion, gods), polities (`polities.py`, a century-step
  readout), attitudes (tolerance, aggression), taboos (including the speech taboos `taboo_defs.py:94-99`), the techtree's
  `from` field (who passed a technology on), and cultures, which are used only for names (`names.py:395`).

---

## 4. Per-situation sections

### 4.1 English after Norse and Norman French

**What makes it distinctive.**
- **Two layers of loans, at two intensities.** Norse reached basic vocabulary, and even pronouns (*they, them, their*),
  *are*, *egg*, *sky*, *take*, *die*. Danish and English were close relatives, and the speakers lived side by side and
  intermarried in the Danelaw. That is stage 3–4 of Thomason & Kaufman's scale.
- **The French layer is stratified by register.** It is cultural, administrative and learned vocabulary (*beef*,
  *judge*, *question*), with Latin doublets above it (*interrogate*). That is stage 2–3, under elite dominance.
- **The lexicon ends up very mixed.** WOLD puts English at ≈41% borrowed meanings; the WOLD mean is ≈24%.
- **Loans brought phonemes.** French loans helped make /v/–/f/, /z/–/s/ and /ʒ/ contrastive.
- **The grammar simplified.** Gender and most case inflection were lost in late Old and early Middle English. The
  usual explanation is Norse–English adult bilingualism and koineisation in the Danelaw (Trudgill 2011; McWhorter 2002).

**Does the engine model it?**
- **Borrowing: partial, and flat.** Loans are 17% of the median living lexicon (p10 5%, p90 22%, max 28%). They do not
  correlate with L2 share (r = −0.07) or isolation (r = 0.06). No lect can reach English's 41%, and no isolated lect
  falls to Mandarin's ≈1%. The donor is uniform among contacts, so a ruling elite gives no more words than a small
  neighbour (`lexicon.py:1846`).
- **Borrowability: wrongly shaped.** Core-100 words are borrowed as often as the rest (median 17% of core vs 17% of all
  words). Live loan rates per concept: I 15%, WE 11%, YOU 11%, NOT 17%, but TWO 39% and ONE 36%. WOLD and the
  Leipzig–Jakarta list put pronouns and *not* among the least-borrowed meanings, at a few percent.

  The numerals are high because they cannot be derived or compounded. Their replacements fall through to the
  borrowing fallback (`lexicon.py:1841`). That fallback was 0.5 when a24559 ran and is 0.35 now.

  Cultural words are right. Crops reach 40–68% (rye 67%, foxtail millet 68%) through the food routes, which is the one
  channel that behaves like stage-1 cultural borrowing.
- **No register stratification.** There is one word per concept (`Lexicon.get`), so *cow/beef* doublets cannot exist,
  and no learned layer either.
- **Phonemes never arrive with loans.** `borrow` runs `hear_word` and `repair` on every loan (`lexicon.py:1624-1646`).
- **L2 simplification: partial.** The mechanism is right in direction (`grammar.py:1743-1747`). But the proxy puts 55% of
  living demes at an l2 of 0.5 or more, and 10% at the 0.7 ceiling, so the simplification is close to universal rather
  than special to Danelaw-type contact (§5.3).

### 4.2 Balkan Sprachbund

**What makes it distinctive.** Greek, Albanian, Balkan Romance and South Slavic come from four branches but share:
- a postposed definite article (Romanian *-ul*, Bulgarian *-ta*, Albanian *-i*);
- loss of the infinitive, replaced by finite subjunctive clauses (*da*, *să*, *na*, *të*);
- a future from WANT (Greek *θα* < *θέλω να*, Bulgarian *šte*, Albanian *do*);
- object clitic doubling;
- a merged dative and genitive;
- a stressed schwa in some of them.

The mechanism is long, multi-directional adult and child bilingualism with no single dominant donor. Grammar converges
more than the lexicon. This is Trudgill's (2011) other branch of contact: **long-term co-territorial bilingualism tends
to add or copy categories, not shed them.**

**Does the engine model it?**
- **Grammar: none.** `grammar.drift` re-draws a flipped feature conditional on the lect's own other features, from global
  marginals (`grammar.py:820-835`). Neighbours never enter. Grams are recruited from the lect's own lexicon along
  grammaticalisation paths; no gram, gram function or construction is ever copied from a neighbour. The only grammar
  that crosses lects is the 1–2 calqued features at a shift (`history.py:930`).

  The live check (scratchpad `cg/areal.py`) compares typology agreement over 40 features. For cross-family lect pairs
  under 500 km apart it is 0.545 (n = 567); for those over 3,000 km apart it is 0.544 (n = 150,394). There is no areal
  signal at all. Same-family pairs are 0.755 near and 0.734 far, which is inheritance. One caveat: deme positions are
  the `lat`/`lon` in `demes.json`, which may be the deme's founding place rather than its present centroid.
- **Phonology: partial.** The wave is lively: 27% of the sound changes in living lects arrived by contact, and 75% of
  those came from another family. That is a real Wave-model mechanism. But consonant and vowel inventory Jaccard for
  cross-family pairs is 0.285 near and 0.288 far, so the outcomes do not converge.

  The likely reason is that a rule is adopted, not a sound. "p > f" taken up by a lect that has a different /p/
  distribution gives a parallel change, not a shared inventory. Real areal phonology (clicks spreading into Nguni,
  retroflexes across South Asia, Balkan schwa) mostly travels as **segments**: through loans that keep their sounds, and
  through bilinguals mapping one system onto another. The engine blocks both (§4.1, phonemes never arrive with loans).
- **The future from WANT** is now possible as an inherited path, since round 5 added WANT. But it is never
  contact-induced. A neighbour having FUT < WANT does not raise the chance of the same path.

### 4.3 Irish and Manx → English; Celtic and Indian English substrates

**What makes it distinctive.**
- **Shift is fast once tipped.** Fishman's three-generation pattern applies. Irish went from majority speech around 1800
  to about 14% by 1900 (famine, emigration, schooling, the Church's use of English). Manx went from a community language
  in the 18th century to its last native speaker in 1974.
- **Interference is mostly phonological and syntactic, with few words** (Thomason & Kaufman's "shift without much
  borrowing"). Hiberno-English has the *after*-perfect (*I'm after eating*), habitual *do be*, it-clefts, echo answers
  instead of yes/no, and dental stops for /θ ð/. Celtic left English only a handful of words (*brock*, *crag*, *tor*,
  *combe*) but many river and place names (*Avon*, *Thames*, *Dover*). Indian English shows the same mechanism with
  other input: retroflex /t d/, syllable timing, invariant *isn't it?*, and progressive forms of stative verbs.
- **Before the shift, the receding language borrows heavily from the target.** Irish took many English loans; Manx
  took more.

**Does the engine model it? Partial: the mechanism is there, but its calibration is off.**
- **Shift: present and well wired.** There are 159 shifts in a24559: takeover 99, swamp 49, trade 7, elite 1. Each is
  logged with its trigger and source. The old lect stays as minority speech, decays, and ends as "shifted" (97 of 159).
- **Too much lexicon is kept.** The median shift keeps **64 words**, 18% of the new lexicon. It always includes the
  same **14 Swadesh-100 items**: BARK, BIRD, CLAW, DOG, EARTH, FISH, LEAF, LOUSE, MOUNTAIN, ROOT, SAND, SEED, STONE,
  TREE.

  The cause is `local_concepts`, which keeps whole semantic fields ("Animals", "Agriculture and vegetation") plus fixed
  landscape words (`lexicon.py:272-273`, `:1962`). It is deterministic, so every shift looks the same, and the amount
  is closer to a mixed language than to a substrate. Place and river names, the real substrate signature, are handled
  in the names layer, which is the right place.
- **Too little phonology and syntax.** The accent replaces only half the sounds the old lect lacked (`ACCENT_P` 0.5),
  with a median of 9 substitutions. Prosody (stress, tone, syllable timing) is never carried over. The calques are any
  1–2 differing typology features at random. In this run the commonest were polar_question, comparative, case, future,
  definite_article and gender. Real shift interference favours phonology, word order, aspect and evidential or
  discourse categories, and it does not favour adding gender or case.
- **The timing is slow.** Median bilingualism before the shift is 3.0 kyr (85 generations; p10 0.5, p90 9 kyr). Median
  survival of the old speech after the shift is a further 3.0 kyr (p90 4.5). SHIFT_DECAY 0.01 per generation
  (`history.py:47`) gives a half-life of about 70 generations.

  Real shifts that tip complete in a few generations, and stable bilingualism lasting millennia is the exception
  (Arvanitika, Sorbian). The 0.5-kyr frame step limits resolution, but the hazard itself is about 10× too slow.
  Whether the world wants long-lived minority speech is a judgement call for Daniel.
- **No extra borrowing during the bilingual years.** The receding lect's loan rate is the flat 12% of replacements
  whatever its share in the ruler's lect (`l.shares`, which the code already tracks).

### 4.4 Tok Pisin: pidgin to creole

**What makes it distinctive.**
- **Where it formed.** Plantation and labour-trade settings (Samoa, Queensland, then New Guinea) put many languages
  together, with no common one and one socially dominant lexifier (English). That gives a reduced, stabilised pidgin.
- **What the pidgin looks like.** A small lexicon with multifunctional words and circumlocution (*gras bilong het*
  'hair'), no inflection, substrate grammar (Tolai): *-im* transitive, *yumi*/*mipela* clusivity, a predicate marker *i*.
- **How it expanded.** It grew as a lingua franca and nativised (creolised) in town families from the mid-20th century,
  with grammaticalised TMA (*bai* < *by and by* FUT, *bin* PST, *save* HAB) and faster speech that made clitics of words.

**Does the engine model it? None.**
- Every lect has one parent: a bud, a shift copy, or a new proto (`history.py:138-213`). A mixed city does one of two
  things. If the lects are one language it levels them (`koine_level`, `:438`). If not, it raises a shift pressure
  toward the holder (`_city_triggers`, `inputs.py:641`).
- Nothing detects "many lects, no shared language, no majority". Nothing builds a reduced variety. Nothing gives a lect
  a lexifier and a substrate at once.
- The pieces a pidgin needs mostly exist:
  - `SIMPLE_VALUE` for the typology (`grammar.py:561`);
  - grammaticalisation paths for FUT/PERF/PROG from lexical words;
  - `hear_word` for substrate phonology;
  - core-list truncation for the reduced lexicon;
  - the clusivity compound queued in Phase A (*yumi*).

  What is missing is the event and a lect with two parents.

### 4.5 Michif and Media Lengua: mixed languages

**What makes it distinctive.** A mixed language comes from a new group identity in a bilingual community, not from
gradual borrowing (Bakker 1997; Matras 2009).
- **Michif.** The Métis were born of French fur traders and Cree and Ojibwe women. Michif has Cree verbs with all their
  polysynthetic morphology, and French noun phrases with articles, gender and adjectives.
- **Media Lengua.** Ecuador. It has Quechua morphosyntax and about 90% of its roots relexified from Spanish.
- **The split follows a fault line**: noun versus verb, or grammar versus lexicon. Neither source is "the" parent.

**Does the engine model it? None.**
- Shift is all-or-nothing: the deme takes `ruler.copy()` and keeps only the local words (`history.py:590-608`). Because
  that word list is large (§4.3), a shifted lect already looks slightly "mixed". But that comes from calibration, not
  from a mechanism, and it always takes the same field.
- The world does produce the trigger. `cultures.py` makes new cultures from `split_adapted` demes and from merges, and
  demes are cross-people (demes_all, mixed cells). There is also a crossing model (`planet/lineages/crossing.py`), which
  matters most for the half-elves and half-orcs who have no lects at all (architecture §8: "peoples with no demes …
  get no lects tonight").

  A **mixed-descent people is the natural home of a mixed language**: half-elves speaking an elvish grammar with a
  human lexicon is exactly the Michif pattern.

### 4.6 Swahili: lingua franca

**What makes it distinctive.**
- **Origins.** A Sabaki Bantu coastal language of trading towns, with heavy Arabic loans (≈20–30% of the general
  lexicon in older counts) from centuries of Indian Ocean trade and from Islam.
- **The spread followed trade and states, not population.** It went inland with 19th-century caravan routes, then
  through German and British administration and Tanzanian nation-building. L2 speakers (tens of millions) far outnumber
  L1 speakers.
- **Its L2 and upcountry varieties simplify** (Shaba Swahili, Kiswahili cha Kongo): noun-class concord is reduced and
  the TAM system is regularised. This is the vehicular-language pattern.

**Does the engine model it? Label only.**
- "**The Common**" (`names.py:778-796`) is the lect holding the most mixed-city heads, or else the one with the most
  contacts. In a24559 it is a gnome lect that holds 2 mixed cities. It names the scholars' families and gives exonyms,
  and nothing in the history acts on it.
- The "**trade**" trigger (`inputs.py:700-731`) is 3 kyr of shared cells (a co-residence share ≥ 0.25), and it pushes
  a *shift* at weight 0.08 (`history.py:49`). It produced 7 shifts. It is not trade along routes, and it makes nobody
  bilingual without shifting.
- Settlements store no trade links (`inputs.md:219`: "No … trade links"). The polities readout has reach and roads but
  is not read here.
- There is no L2-only variety, so a language cannot be L1 for some demes and a simplified vehicular for others.

### 4.7 Arabic: diglossia, liturgy and continuum (with Latin, Sanskrit, Dutch–German)

**What makes it distinctive.**
- **Diglossia** (Ferguson 1959). Every community has two varieties. H (Classical or Modern Standard Arabic) is fixed by
  the Qur'an, learned in school, and used for liturgy, writing and formal speech. L (the dialects) is everyone's mother
  tongue.
- **H feeds L.** Learned loans and doublets flow from H into L. Latin did the same for Romance (*fragile/frêle*,
  *hospital/hôtel*), and Sanskrit for the Indo-Aryan languages (*tatsama* vs *tadbhava*).
- **Under H, the L varieties form a continuum** from Morocco to Iraq, with unintelligible ends. Dutch–Low German–High
  German is a continuum without a shared H; standardisation along state borders cut it.
- **A liturgical language spreads with conversion**, and it keeps a dead stage alive for millennia: Latin, Church
  Slavonic, Ge'ez, Pali, Avestan.

**Does the engine model it?**
- **Diglossia, H and L registers: none.** There is no register layer. There is one word per concept per lect.
- **Liturgy: none.** `gods.json` has faiths, founding, inheritance, schism, conversion by neighbours, missionaries and
  rulers (`gods.py:24-41`). None of it reaches the language pass. Gods have no names yet: "Names wait for PW-986"
  (`gods.py:22`), and PW-986 is this language engine. Prestige counts `writing` but not faith (`inputs.py:438`).
- **Continua: partial.** The detector exists and is reasonable: a chain of adjacent intelligibility above 0.5 whose ends
  fall below 0.5 (`families.py:208`). The live output, though, is almost no dialect structure:
  - 573 living dominant lects make 587 "languages" (minority lects included);
  - 510 languages have one lect;
  - one language has 7 lects;
  - there are 5 continua, all chains of 3.

  So the demes of one people stop being mutually intelligible fast. Two things keep real dialects of one language
  together: continuous dialect contact, and lexical diffusion between neighbours, which runs far faster between dialects
  than between languages. Here, same-family neighbours share sound rules by wave, but the lexicon only shares through
  the flat 12% loans. The koine levelling (which borrows core words) runs only in mixed cities (11 events).

  Intelligibility is symmetric (`families.py:171-197`), so asymmetric comprehension (Danish/Swedish, a standard
  understood by its dialect speakers but not the reverse) cannot appear.
- **Tree and wave together: full as a mechanism.** The budding tree and the wave are both there, and the wave is
  prestige-weighted and generation-scaled. The weakness is the outcome: no measured areal or continuum structure, and no
  check that would catch its absence (§5.2).

### 4.8 Vaupés: linguistic exogamy

**What makes it distinctive.**
- **Who marries whom.** Among the Eastern Tukanoan peoples of the Vaupés, you must marry someone of another "father
  language" group. A household is multilingual, a child grows up with 3–5 languages, and the father's language is the
  identity marker (Sorensen 1967; Jackson 1983).
- **Words are kept apart.** A strong ideology rejects mixing, and lexical loans are few (Aikhenvald 2002; Epps).
- **Grammar converges a great deal.** Tariana (Arawak) took Tukanoan-type evidentials and other categories through
  calquing.

This is the clearest case that **attitudes gate borrowing type**: words are blocked, structure flows.

**Does the engine model it? None.**
- Multilingualism exists only as one deme's dominant lect plus its shifted-away minority speech. There is no stable,
  symmetric multilingualism between demes.
- There is no purism and no structural borrowing (§4.2).
- The world has the inputs:
  - `taboos.py:185` draws `clan_exogamy` (EA015's share) and `taboo_defs.py:94-105` has kinship and speech taboos;
  - `attitudes.py` gives each culture a tolerance value from 0 to 1.

  But both are readouts that nothing in `planet/language/` reads.

---

## 5. Cross-cutting picture

### 5.1 Missing entirely

1. **Contact-intensity borrowing (the Thomason & Kaufman scale).** Loans are a fixed share of replacements. Three things
   are missing:
   - the amount does not rise with contact, the bilingual share or the donor's prestige;
   - the type does not climb the scale (cultural words, then function words, then basic words and affixes, then
     structure);
   - the donor choice is uniform (`lexicon.py:1846`), which contradicts architecture §8.
2. **Borrowability by meaning.** No per-concept factor. WOLD's borrowed scores per meaning are exactly this, and the
   concept list is already built partly from WOLD (Leipzig–Jakarta, `concepts.tsv` header).
3. **Structural borrowing.** No gram, affix or construction is copied between lects. Typology features are never pulled
   toward neighbours. Only the calque at a shift crosses lects.
4. **Phoneme borrowing.** No segment ever enters a lect through a loan.
5. **New-language outcomes.** There are no pidgins, no creoles and no mixed languages. Lects have one parent, so the
   true tree cannot hold a network node.
6. **Registers.** There is no H/L diglossia, no learned layer, no honorifics, and no avoidance speech (Dyirbal
   *Jalnguy*, in-law registers). The speech-taboo rows that could drive avoidance speech exist in `taboo_defs.py:94-99`.
7. **Liturgical and prestige languages tied to faiths.** None (§4.7).
8. **Vehicular languages.** No L2-only variety, and no lingua franca beyond the label (§4.6).
9. **Variation below the deme.** No social dialects, no city vs country, and no dialects inside one deme's lect. This
   is acceptable at the world's grain, but it is why §4.7's continua must come from between demes.

### 5.2 Modelled too thinly

1. **Areal outcome.** The wave is busy: 27% of sound changes, 75% of them cross-family. But neither inventories nor
   typology show any areal signal (§4.2). `checks.py` has no areal check, so this was invisible. The check in this
   review (cross-family agreement near vs far) should become one.
2. **Shift interference.** The calques are random features. The accent replaces half the missing sounds, and prosody
   never transfers.
3. **L2 effects.** The L2 effect touches only grammar, and only in the simplifying direction. Long-term child
   bilingualism, the Balkan and Vaupés kind, which copies categories, is missing. The L2 proxy also has no direction:
   other peoples living on my cells are assumed to learn *my* lect, whatever the prestige. When the prestige runs the
   other way, it is *my* people who become L2 speakers of *theirs*.
4. **Dialect continua.** Same-family neighbours share sound rules but barely share words, so dialects drift apart into
   languages. The result is 510 single-lect languages and 5 three-lect continua.
5. **Trade.** "Trade" means co-residence (`inputs.py:700`), at a shift weight of 0.08. No routes, and no bilingualism
   short of a shift.
6. **The Common.** It is a naming choice with no history behind it.

### 5.3 Exists but wrongly calibrated

| What | Engine (a24559) | Real-world reference | Note |
|---|---|---|---|
| Loan share per lect | median 17%, p10 5%, p90 22%, max 28%; r(l2) = −0.07 | WOLD ≈1% (Mandarin) to ≈60% (Selice Romani), mean ≈24% | Too narrow and unrelated to contact. |
| Core-100 loans | median 17% (= all words) | Leipzig–Jakarta items are by construction the least-borrowed, mostly under 10% | No borrowability gradient. |
| Pronoun loans | I 15%, WE 11%, YOU 11% | a few percent (English *they* is the famous exception) | |
| Numeral loans | TWO 39%, ONE 36% | Numerals are fairly borrowable (Thai, Japanese, Swahili *sita*/*saba*/*tisa*), but not at 4 in 10 | An artefact of the fallback chain: no derive or compound route for numerals. BORROW_FALLBACK fell from 0.5 to 0.35 since this run. |
| Substrate words per shift | 64 (18% of the lexicon), always the same 14 core words | a handful of words plus toponyms (Celtic in English) | Deterministic fields (`lexicon.py:272`). |
| Bilingualism before a shift | median 3.0 kyr (85 gen) | 3–5 generations once tipped (Irish, Manx); centuries for slow cases (Coptic) | SHIFT_K 0.015 (`history.py:46`) |
| Old speech after a shift | median 3.0 kyr | about 1–3 generations to the last speakers | SHIFT_DECAY 0.01 (`history.py:47`) |
| L2 share | median 0.53; 55% of demes ≥ 0.5; 10% at the 0.7 cap | Most small speech communities are bilingual, but L1-dominant | `L2_SHARED` 0.6 and `L2_MAX` 0.7 (`inputs.py:41-42`). Simplification is near universal. |
| Ruler prestige bonus | absent in code | architecture §8 specifies one | A doc/code mismatch. |

### 5.4 How the world's systems are wired into language

| System (`planet/lineages/`) | Read by language? | How | What it could drive |
|---|---|---|---|
| Demes, presence, contact (`demes.py`, presence table) | yes | lects, budding, wave, borrowing donors, L2, isolation | (already central) |
| Incursions (`contacts.py`) | yes | elite and swamp shift triggers (`inputs.py:583`) | direction and intensity of borrowing |
| Settlements (`settlements.py`) | yes | takeovers, mixed cities (koine, city trigger, L2 bonus), prestige | a city lect as a standard; pidgin sites |
| Crop and animal spread | yes | food routes: loans carried with each hop | (works well: 40–68% crop loans) |
| Techtree | partly | prestige from cities, writing and law (`inputs.py:43`) | **tech loanwords along `known[p][t][2]` = `from`**, like food routes (iron, wheel, writing, kingship words) |
| Cultures (`cultures.py`) | names only | ethnonyms and exonyms (`names.py:395`) | mixed-language identity (a new culture from a merge); culture-level dialect boundaries |
| Reputation (`reputation.py`) | names only | exonym valence | feared or despised donors lent fewer loans, or loans with pejoration |
| **Faiths and gods** (`gods.py`) | **no** | — | liturgical lects, religious vocabulary along conversions, god names (`gods.py:22` waits on PW-986), the prestige of temple faiths |
| **Polities** (`polities.py`) | **no** | — | elite rule triggers from real rule; a ruler prestige bonus; administrative lingua francas; capital standards; borders as isoglosses |
| **Attitudes** (`attitudes.py`) | **no** | — | tolerance → purism (fewer loans, more calques: Vaupés, Icelandic); a forced shift under intolerant rulers |
| **Taboos** (`taboos.py`, `taboo_defs.py`) | **no** | the lexicon's "taboo" source is keyed to the concept class (`lexicon.py:1530`), not to the culture's taboos | speech taboos (dead_soundalike, ruler_name, inlaw_words) → faster lexical replacement (as in Australia and Polynesia), avoidance registers; clan exogamy → multilingual households |
| Invasions you schedule (`invasions.py`) | no (only through polities) | — | follows once polities are wired |
| Crossing / mixed peoples (`crossing.py`) | no | half-elves, half-orcs and others have no lects | mixed languages |

**Order of the passes.** Polities and gods are readouts derived after the peoples run. The language pass already reads
`cultures.json` and `settlements.json`. Reading `gods.json` and a polities document is the same kind of dependency, but
a run must have them derived before `planet languages` runs. In a24559, `gods.json` exists and polities does not.

### 5.5 Notes on the situations I did not pick

- **Japanese honorifics and Javanese speech levels** are queued in Phase D of the grammar review. Two inputs are already
  in the world: `polities.py` (kingship, states) and the taboo kinds `rank`, `sumptuary` and `caste`
  (`taboo_defs.py:54-56`, `:67-69`). These should gate them, so that honorific registers appear in stratified, kingship-holding
  cultures and not at random.
- **Latin and Sanskrit** are covered by §4.7's liturgical design. The *tatsama*/*tadbhava* doublets fall out of it if
  learned loans may coexist with the inherited word as a register pair.

---

## 6. Ranked recommendations

Value is "how much more real-looking the languages and their histories get" (H/M/L). Cost: S = under a day; M = a few
days, a new mechanism plus a run; L = a week or more, or an architecture change. The **Re-cal** column marks items that
move the retention or horizon calibration and need a calibration run afterwards (`calibration.md`).

| # | Recommendation | Value | Cost | Re-cal |
|---|---|---|---|---|
| 1 | **Borrowing by intensity and borrowability.** (a) Weight the donor by contact × prestige ratio, and add the receiver's share in that donor's lect (`l.shares`) during bilingual years, instead of a uniform draw (`lexicon.py:1846`). (b) Make the loan share of replacements rise with that intensity: about 5% for casual contact, up to about 50% in the last generations before a shift. (c) Add a per-concept borrowability factor from WOLD's borrowed scores (CLDF `wold`, CC-BY) to `concepts.tsv`, so that pronouns, *not* and body parts sit low and cultural words high. (d) Give numerals a non-loan fallback (a compound like 'hand' > FIVE, or keeping the old word) so TWO stops being a loan 39% of the time. This fixes §4.1 and §5.3's top rows, and the doc/code mismatch with architecture §8. | H | S–M | yes |
| 2 | **Calibrate the substrate.** Keep each local word with a chance (say 0.1–0.3), drawn per shift; always keep names and toponyms. Raise ACCENT_P toward 1, and carry over the stress or tone system. Draw calques from shift-prone features (word order, aspect and perfect, evidentiality, polar_question, the case–adposition side) and not from ones that add gender or case. | H | S | small |
| 3 | **An areal check, then areal grammar and sounds.** (a) Add the near-vs-far cross-family agreement (this review's `cg/areal.py`) to `checks.py`, for typology and inventories. (b) In `drift`, draw a re-drawn feature from contact neighbours' values, with a chance ∝ contact × bilingual share. (c) Let a neighbour's realised gram path (FUT < WANT, DEF < THAT postposed) raise PRESSURE and path weights for the same path. (d) Let loans keep a donor segment at high intensity (stage ≥ 2), so sounds diffuse as sounds. Together these give Balkan-type convergence and real phonological areas. | H | M | yes |
| 4 | **Wire polities.** Use the polities readout for elite-rule triggers: a ruling culture's state over subject cultures' demes, with a strength from the share ruled. Add the ruler prestige bonus that architecture §8 specifies. Give empires an administrative lect (the capital's) that pushes L2 shares and loans across the realm, and level same-language lects inside one polity toward the capital (a standard). Needs a polities doc before `planet languages`. | H | M | yes |
| 5 | **Wire faiths: liturgical lects and god names.** When a faith is founded, freeze its founding culture's lect as the liturgical lect (a snapshot that no longer changes). Converts borrow religious vocabulary (GOD, SPIRIT, PRIEST, TEMPLE, PRAY, the god names) from it, as *learned* loans that may sit beside the inherited word (doublets). A temple faith's liturgical lect adds prestige. This also gives `gods.py`'s beings their names, which wait on PW-986. | H | M | no |
| 6 | **Tech loanwords along the techtree.** `known[p][t] = [kyr, how, from]` names the donor people. Run the food-route machinery for tech concepts (iron, wheel, cart, writing, king, merchant): the Wanderwort channel. | M | S | no |
| 7 | **Speech taboos and purism.** (a) Cultures with `dead_soundalike`, `ruler_name` or `inlaw_words` (`taboo_defs.py:95-99`) get a raised replacement hazard on high-frequency nouns, and a share of those taboo replacements are loans or paraphrases. Australian and Polynesian lexicostatistics show this effect (Dixon 1980). (b) A culture's tolerance (`attitudes.py`) scales its loan share; low tolerance turns would-be loans into calques (a compound on the donor's recipe). | M | S | small |
| 8 | **Shift timing.** Accelerate the shift once the share passes about 0.3 (the tipping point), and make the old speech decay over a few generations unless a stable-bilingualism condition holds (an isolated enclave, or high cohesion). This is a needs-decision question for Daniel: how long minority speech should live in this world. | M | S | small |
| 9 | **The two L2 regimes and their direction.** Split the L2 input into short-term adult L2 (simplifying; the present path) and long-term co-territorial child bilingualism (copying categories: feeds #3c). Make the proxy depend on direction: other peoples count as L2 learners of my lect only if mine has the higher prestige; otherwise they raise my bilingual share in theirs. Revisit `L2_SHARED`/`L2_MAX` with Daniel (median 0.53 now). | M | S–M | yes |
| 10 | **Dialect continua.** Let same-language contact lects borrow core words at an intensity-weighted rate (the koine-level mechanism, outside cities). Then measure continua and single-lect languages against a target set with Daniel. Consider asymmetric intelligibility: phonological distance weighted by the listener's inventory. | M–H | M | yes (horizon) |
| 11 | **Vehicular languages.** When a lect is used across many contacts, mixed cities, trade or a polity, fork an L2 variety with a strong strip, regular paradigms and no concord. Mixed-city and trade shifts then go to it. "The Common" becomes the largest vehicular lect. | M–H | M | no |
| 12 | **Diglossia (H/L).** Once `writing` is known, a people's prestige lect gets a frozen written standard. Learned loans from H into L form doublets with the inherited words, and the sketch shows the two registers. This shares machinery with #5. | M | M | no |
| 13 | **Mixed languages.** For a culture born of a merge or a mixed-descent people (`crossing.py`; the peoples that now have no lects), build a lect with two parents: verbs and grams from one, nouns from the other (Michif), or grammar from one and lexicon from the other (Media Lengua). This needs `parents` as a list in the true tree. | M | M | no |
| 14 | **Pidgins and creoles.** In a mixed city or a mine with three or more mutually unintelligible lects and no majority (where koine fails), form a pidgin. Lexifier: the holder's core list, reduced. Typology: `SIMPLE_VALUE`. TMA: particles from paths (FUT < 'later', PERF < FINISH, PROG < STAY). Substrate: the labourers' majority. If it lasts a generation as a deme's main speech, it creolises (`how="creole"`, two parents). | M | L | no |
| 15 | **Honorifics** (Phase D), gated by kingship, `rank` or `caste` taboos and state polities, not drawn at random. | M | M | no |
| 16 | **Exogamous multilingualism** (Vaupés): `clan_exogamy` plus small neighbouring demes of one culture area give stable multi-lect repertoires with purism (#7b) and structural convergence (#3). A flavour case. | L–M | M | no |

**Small and mostly self-contained:** items 1, 2, 6 and 7a. Each is S or S–M and fixes a visible mis-calibration or opens a
cheap channel the world already supplies. Item 1 changes the retention calibration, so it needs a calibration run. Item
3a (the areal check) is S on its own and should go in with them, so that items 3b–d can be judged.

**The largest gains in realism** are items 3, 4 and 5. They tie the languages to the world's history: areas, empires
and faiths. They are what would make a reader see "the language of the old empire" or "the temple tongue" in the
output.

**Needs Daniel:** item 8 (how long minority speech lives), item 9 (the L2 levels), and item 10 (how much dialect
continuity at deme grain is wanted). These are judgement calls and should be needs-decision tickets.

---

## 7. Caveats

- a24559 predates the 11-07 changes (`BORROW_FALLBACK` 0.35, the shift caps, round 5's vocabulary). The numeral loan
  rate and the shift counts may have moved.
- Deme positions for the areal test are `demes.json` `lat`/`lon`, which may be founding places. A re-test with
  present-day centroids from `layers/demes_all.bin` would settle it. I expect the same null, because the near and far
  values match to the third decimal.
- WOLD percentages and the dates for Irish and Manx are from memory and rounded. Check them before quoting.
- The tally counts a word as a loan when its latest word-formation step is `borrow:` (sound changes skipped). A loan
  later reshaped by a derivation counts as a derivation.
