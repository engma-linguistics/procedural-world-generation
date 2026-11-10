# Proposal: question-word paradigms, and conquest and trade borrowing (2026-11-10)

Two questions from Daniel, answered from the literature, from the code at `main` 70ad3788, and from read-only measurements
on the stored run `runs/a24559/languages.json` (620 living lects, 320 protos). Nothing in the model was changed. The
measurement scripts were throwaway and are not committed; every number below names what it counts.

Part 1 asks whether the English *wh-* set (one stem across person, thing, place and time) is common, and what the engine
should do about it. Part 2 asks whether the engine has a "Norman conquest": prestige vocabulary from rulers, cow/beef
splits, and, after Daniel's addition, food doublets in general and the trade layer (Swahili's Arabic numerals and
commerce words).

---

## Part 1. Shared stems in question words: correlative paradigms

### In plain words

Yes, it is common. English *who, what, where, when, which, why, how* all come from one Indo-European question stem,
*\*kʷi-/\*kʷo-*. Latin *qu-*, Slavic *k-/č-* and Sanskrit *k-* come from the same stem. Many unrelated languages do the
same thing: Japanese *do-* (*dore, doko, dō, dono*), Turkish *n-* (*ne, nere, nasıl, neden*), Hungarian *mi-* (*mi, mikor,
miért*). Very often the words for "this" and "that" are built the same way, so the language has a small grid: one stem
for the question, one for "here" and one for "there", crossed with person, thing, place, time and manner. English
*where/there/here* and *when/then* are what is left of that grid.

It is not a noun-class system. A noun class is an agreement category that every noun belongs to. This grid is a small
derivational pattern: a handful of endings, each from an ordinary word such as "place", "time" or "way". Swahili does
link the two, because its "which" word agrees in class, and its place and manner question words are class forms.

The engine already builds *where*, *when* and *how* from *what* in about half of today's languages, but you cannot see
it. Only 16% of living languages have three question words that start the same way, against 3 to 7% for five random
words. Three things hide the link:
- the derivations happen at random times;
- the frequent words wear down one by one;
- *where* and *when* use the same "place" ending, so they often come out identical and one gets replaced.

The proposal is a "correlative table" system, like the existing number, colour and kin systems. Each proto draws question
and pointing stems and a set of category endings. The cells are built from them, wear down and get renewed as a set. The
table is shown on the language page.

### 1.1 Findings: Indo-European

**The interrogative stem.** PIE had *\*kʷi-* (animate and indefinite: Latin *quis*, Greek *tís*, Hittite *kuiš*) and
*\*kʷo-* (Latin *quod*, Sanskrit *kás*, Gothic *ƕas*), plus a *\*kʷu-* locative stem (Sanskrit *kúha*, Latin
*ali-cubi*). The stem is initial and the category marks follow it:
- Gothic *ƕas* 'who', *ƕa* 'what', *ƕar* 'where', *ƕan* 'when', *ƕaiwa* 'how';
- Old English *hwā, hwæt, hwǣr, hwanne, hwȳ* (an instrumental 'by what'), *hū*, and *hwilc* < *\*hwa-līk* 'what-shaped';
- Latin *quis, quid, quando, qualis, quantus, ubi* (< *\*kʷu-bhi*, initial lost; compare *ali-cubi* 'somewhere');
- Sanskrit *kás, kím, kva/kútra, kadā́, katham, kati*.

The reflexes differ by sound law, not by system:
- Greek labiovelars gave *t-* before front vowels (*tís*) and *p-* before back ones (*poû* 'where', *póte* 'when',
  *pôs* 'how'). Greek therefore shows two "stems" that are one etymon.
- Slavic gives *k-* (*kъto, kъde, kogda, kako*) beside palatalised *č-* (*čьto*).

**The parallel deictic sets.** PIE *\*so-/\*to-* (the "that" demonstrative) gave English *the, that, there, then,
thence, thither, thus*. PIE *\*ḱi-* ('this') gave *here, hither, hence* (and *he*, *him*). The correlative table that
results is:

| category | interrogative | distal / anaphoric | proximal |
|---|---|---|---|
| place (at) | where | there | here |
| place (to) | whither | thither | hither |
| place (from) | whence | thence | hence |
| time | when | then | (now: a separate root) |
| manner | how | thus | (so) |
| reason | why | (therefore) | — |

**How productive the tables are today.** In English they are eroded:
- the *-ther* and *-nce* rows are archaic, replaced by *where to* and *where from*;
- *how* and *who* lost the /w/ in speech (*who* /huː/) and keep it only in spelling;
- *why* survives as a frozen instrumental.

German keeps the system alive and regular. *Wo/da/hier* combine with *-hin/-her* (*wohin, dahin, hierher*) and with
prepositions (*womit, damit, hiermit*). *Warum* < *wār-umbe* 'about what' is a renewal of the reason cell. French
shows erosion and renewal side by side:
- inherited *qui, quoi, quand*;
- *où* < *ubi*, which lost the onset;
- *comment* (< *quomodo* + *-ment*), *pourquoi* 'for what' and *combien* (< *comme bien*) are renewals by periphrasis.

Spanish *dónde* < *de + unde* is a reinforcement of the place cell. The engine already has the machinery for this kind of
reinforcement (`relation=reinforce` in `data/derivations.tsv`).

### 1.2 Findings: typology

**How common is a shared stem?**
- Ultan (1978) surveyed 79 languages. He found that interrogative words tend to share a common element, and that
  'where', 'when' and 'how' are typically derived where any are.
- Cysouw (2004, "Interrogative words: an exercise in lexical typology", workshop handout; summarised on the MPI-EVA
  page *Typology of content interrogatives*) sets up four core categories: person, thing, place and selection ('which').
  In a majority of languages each of the four is a synchronically unanalysable lexeme. Formal sharing is concentrated
  in the other categories (time, manner, reason, quantity), which are mostly built from the core four.
- Idiatov (2007, *A typology of non-selective interrogative pronominals*, PhD, Antwerp) shows that a distinct *who* and
  *what* is very nearly universal.
- Diessel (2003, "The relationship between demonstratives and interrogatives", *Studies in Language* 27(3): 635–655)
  sampled about 100 languages. Demonstratives and interrogatives cut across the same word classes and encode the same
  features: person, thing, place, direction, manner, time and amount. They are often built with the same category
  formatives. Diessel (1999, *Demonstratives*, Benjamins) gives the grammaticalisation side.

Together these give a realistic expectation:
- *who* and *what* are separate words almost everywhere, often unrelated in form;
- *where* is an independent root in many languages;
- the time, manner, reason and quantity cells are usually built on *what*, *which* or *where*;
- languages with a fully visible stem-plus-formative grid (Japanese, Turkish, Hungarian, Gothic) are common but not the
  majority.

I found no published share of "languages with three or more question words sharing an onset". Decision 1.2 proposes
setting that band from a sample instead of inventing one.

**Indefinites built from interrogatives.** Haspelmath (1997, *Indefinite Pronouns*, OUP) builds the implicational map of
indefinite functions:
- specific known, specific unknown;
- irrealis non-specific;
- question, conditional;
- indirect negation, comparative;
- direct negation;
- free choice.

Each indefinite series covers a contiguous stretch of the map. WALS 46A (Haspelmath, 326 languages) counts the
indefinite types:

| type | languages |
|---|---|
| interrogative-based | 194 |
| generic-noun-based | 85 |
| mixed | 23 |
| special | 22 |
| existential construction | 2 |

Interrogative-based indefinites dominate North America, Australia and most of Eurasia. Generic-noun-based ones dominate
Africa, New Guinea and the Pacific (an areal pattern largely independent of family). English is mixed: *somewhere,
anyhow* are interrogative-based, while *someone, something* are generic-noun-based.

**Examples.**
- **Japanese** has the textbook grid. The stems are *ko-* (near the speaker), *so-* (near the hearer), *a-* (far) and
  *do-* (question). The formatives are *-re* (thing), *-ko* (place), *-no* (adnominal), *-nna* (kind) and *-ō/-ū*
  (manner): *kore/sore/are/dore*, *koko/soko/asoko/doko*, *kō/sō/ā/dō*. *Dare* 'who', *nani* 'what', *itsu* 'when' and
  *naze* 'why' stand outside the *do-* set. Indefinites add *-ka* (*dareka, dokoka*). Universal and negative-polarity
  forms add *-mo* (*daremo*), and free-choice forms add *-demo*.
- **Korean** has *nugu* 'who', *mwŏ(t)* 'what', *ŏdi* 'where', *ŏnje* 'when', *ŏttŏk'e* 'how', *wae* 'why', *ŏlma* 'how
  much' and *ŏnŭ* 'which'. Several begin with *ŏ-*. Demonstratives *i/kŭ/chŏ* take *-gŏt* (thing) and pair with
  *yŏgi/kŏgi/chŏgi* (place). Bare interrogatives double as indefinites, distinguished by intonation.
- **Mandarin** has *shéi* 'who' and *shénme* 'what'. *Nǎ* 'which' builds *nǎr/nǎlǐ* 'where', parallel to
  *zhèr/nàr* 'here/there'. *Zěnme* 'how' is parallel to *zhème/nàme* 'so'. *Wèishénme* 'why' is literally 'for what'.
  Bare interrogatives serve as indefinites (*shéi* 'anyone').
- **Turkish** has two stems, *k-* (*kim* 'who', *kaç* 'how many') and *n-* (*ne* 'what', *nere-* 'where', *nasıl* 'how',
  *neden/niçin* 'why' = 'what-ABL', 'what-for'). *Ne zaman* 'when' is literally 'what time'. *Nere-de* matches
  *bura-da/şura-da/ora-da* (here/there): a live correlative.
- **Finnish** has *ku-* (*kuka* 'who', *kuinka* 'how', *kumpi* 'which of two') and *mi-* (*mikä* 'what', *missä/mistä/
  mihin* 'where/whence/whither', *milloin* 'when', *miksi* 'why'). The place and reason cells are case forms of *mi-*,
  so local case does the work of a place formative.
- **Hungarian** has *ki* 'who', *mi* 'what', *mikor* 'when', *miért* 'why' and *mennyi* 'how much'. *Hol/hová/honnan*
  is the place set. Its correlates are *ekkor/akkor* 'then', *itt/ott* and *ide/oda*. Indefinites use *vala-*
  (*valaki, valahol*), negatives *se-* (*senki*) and universals *minden-*: a complete Haspelmath grid.
- **Swahili**:
  - *nani* 'who', *nini* 'what', *lini* 'when', *wapi* 'where', *kwa nini* 'why' ('for what');
  - *-pi* 'which' agrees in class: *yupi, kipi, lipi, zipi*;
  - *-ngapi* 'how many' agrees as well;
  - *vipi* 'how' is the class 8 form of *-pi*, and class 8 *vi-* also makes manner adverbs (*vizuri* 'well');
  - the locative classes 16–18 (*pa-, ku-, mu-*) give *papi/kupi/mupi* 'at which place' and the demonstratives
    *hapa/huku/humu* 'here' and *pale/kule/mle* 'there'.
- **Quechua** (Southern): *pi* 'who', *ima* 'what', *may* 'where' (*may-pi* 'where at', *may-manta* 'from where'),
  *imayna* 'how', *ima-rayku* 'why' ('because of what'), *hayk'aq* 'when' and *mayqin* 'which'. Indefinites and negatives
  add *-pas* (*mana pi-pas* 'nobody').
- **Tagalog** has *sino* 'who', *ano* 'what', *saan* 'where', *kailan* 'when', *paano* 'how' (*pa-* + *ano*), *bakit*
  'why', *ilan* 'how many', *alin* 'which'. *Gaano* 'how (much)' matches the demonstrative manner set
  *ganito/ganyan/ganoon* 'like this/that'. The place deictics are *dito/diyan/doon*.
- **Warlpiri** (Pama-Nyungan, Australia) has *ngana* 'who/someone', *nyiya* 'what/something', *nyarrpara*
  'where/somewhere', *nyangurla* 'when' and *nyarrpa* 'how'. Most begin with *ny-*, and each doubles as an indefinite,
  the common Australian pattern (Mushin 1995, "Epistememes in Australian languages", *Australian Journal of
  Linguistics* 15).

**Is it "noun class-like"?** Not in the technical sense. Noun classes (genders) are an agreement system: every noun is
assigned to one, and the class shows on other words (Corbett 1991). A correlative table has neither property. It is a
small, closed derivational paradigm: a few stems (interrogative, proximal, distal, sometimes indefinite) crossed with a
few ontological categories. Most of the categories come from grammaticalised nouns or case markers, for example:
- 'what person' > 'who';
- 'what place' > 'where';
- 'what time' > 'when' (Turkish *ne zaman*);
- 'what-like' > 'how' / 'which' (English *which* < *hwa-līk*);
- 'for what' > 'why' (French *pourquoi*, Mandarin *wèishénme*).

Daniel's intuition does land in two places:
- The categories are ontological (person, thing, place, time, manner, kind, amount), like the semantic core of many
  noun-class systems. In Bantu the two overlap directly: classes 16–18 are locative classes, class 8 makes manner
  adverbs, and *-pi* 'which' takes the class prefixes. So Swahili's place and manner question words are class forms of
  one interrogative stem.
- Japanese, Turkish and Hungarian show the reverse: the category marks are case suffixes or bound nouns rather than
  class prefixes.

The accurate name is "correlative (pro-form) paradigm". In Bantu it uses the noun-class prefixes as its category marks.

*Reference note.* The brief cited "Mackenzie's correlative tables". I could not locate a precise publication under that
name. The correlative table as an organising device is Zamenhof's (the Esperanto *tabelvortoj*, 1887). Classical
grammars of Sanskrit give the same table (*ya-/ta-/ka-* relative/demonstrative/interrogative). Daniel, if you have the
Mackenzie reference, I will add it.

### 1.3 What the engine does now

**Concepts.**
- `lexicon._WH` = WHO, WHAT, WHERE, WHEN, HOW, plus HOW MUCH as an ordinary FUNC concept.
- The deictics are THIS, THAT and HERE, THERE, plus NOW.
- There is no WHY, WHICH, THEN, THUS, HOW MANY, or indefinite pronouns (someone, nothing).
- All the WH and deictic concepts are in `_CLOSED` (`lexicon.py:156-157`).

**How they are made.**
- **Proto** (`proto_lexicon`, `lexicon.py:887`): each concept is a fresh root, unless a `derivations.tsv` row lets it be
  built from another proto concept. That happens with probability `PROTO_DERIVE[freq_class]`. The WH words are frequency
  class 1, so the probability is 0.15. The rows are:
  - `place WHAT WHERE` (2), `place WHAT WHEN` (1) and `like WHAT HOW` (1);
  - `place THIS HERE` (3) and `place THAT THERE` (3).
- **History** (`lexicon.step`): a replaced word draws from SOURCES, with derivation at 0.36. So WHERE, WHEN and HOW are
  rebuilt on the current WHAT at any later date, using the lect's single 'place' or 'like' affix (`_draw_affixes`).
- **Reinforcement** (`relation=reinforce|repair`): THIS+HERE, THAT+THERE and WHO+PERSON renew the cells.
  `core_repair` (`lexicon.py:2309`) renews one member when two cells of a core set fall together. It uses, in order, a
  reinforcement row, a loan, a derivation, and only then a fresh root.
- **Grammar.** `grammar.py:491` uses WHO/WHAT as the source of WH-INTERROGATIVE grams. X73 'what' > polar question
  particle. The sketch lists the question words in its "Questions" topic (`sentences.py:2351`).

**Measured on a24559** (living lects, n = 620; "onset" = the segments before the first vowel):

| measure | value |
|---|---|
| ≥3 of WHO/WHAT/WHERE/WHEN/HOW share one etymological root | **47.9%** (of these, WHAT is the shared root in 217 of 297) |
| ≥2 share one root | 83.1% |
| WHAT-rooted: WHERE / WHEN / HOW / HOW MUCH | 48.7% / 47.6% / 44.7% / 35.3% |
| WHO built on WHAT / on PERSON | 4.5% / 28.4% |
| those WHAT-rooted cells first derived at a proto / later in history | 87 / 786 |
| ≥3 of the five share a non-empty onset | **15.5%** |
| same, for random 5-sets of core words (3 draws) | 3.2–6.8% |
| same, for random 5-sets of other function words (3 draws) | 3.4–6.0% |
| WHERE, WHEN, HOW: how many are WHAT-rooted *and* still contain WHAT's current form | 0: 54.7%, 1: 26.9%, 2: 14.0%, 3: 4.4% |
| HERE built on THIS / THERE on THAT | 75.2% / 67.3% |
| ≥2 of WHERE/HERE/THERE built with the lect's 'place' affix (all 3) | 75.2% (39.5%) |
| THIS and THAT share a non-empty onset | 6.9% |
| current loans: WHO / WHAT / WHERE / WHEN / HOW | 10.6 / 8.5 / 11.6 / 14.0 / 14.7% (WOLD scores 0.3–5%) |

How to read these numbers:
- **The etymological paradigm exists but is invisible.** Almost half the living lects have three question words on the
  WHAT root. Only 4% have all three of WHERE/WHEN/HOW still visibly containing WHAT. A visible shared onset in three or
  more question words runs at about 3× chance (15.5% against roughly 5%). In English the link is etymologically older
  but formally visible, because the stem is initial, the formatives are final, and analogy kept the set together.
- **Why invisible, part 1: independent timing.** 90% of the derivations happen after the proto (786 against 87). Each
  cell is rebuilt separately, on whatever WHAT then sounds like, so the cells carry different stem shapes.
- **Why invisible, part 2: per-word wear.** The frequent-word wear (PW-1570) acts word by word. In d0, WHAT *eɖi* > *i*
  and WHERE *ʔueɖi* > *u*: the shared stem is gone from both.
- **Why invisible, part 3: one 'place' affix for two cells.** WHERE and WHEN both use the lect's single 'place' affix
  on WHAT. In 257 of 620 living lects both were built that way at some point, and built on the same WHAT form they are
  homophones at birth. The living WH words carry 89–97 repair steps each (WHERE 95, WHEN 89, HOW 97) and 78 for WHO.
  This also explains why WH loans run at 9–15% against WOLD's 0.3–5%: 63 of 72 WHERE loans and 81 of 91 HOW loans are
  `contact (paradigm repair)`.
- **The WHO reinforcement is mis-shaped.** The row `repair PERSON WHO` says "'what person' (Latin *quis homo*)", but
  `core_repair` calls `compound(head=k, modifier=m)`. That builds *old-WHO + PERSON* ('who-person'), not
  *WHAT + PERSON*. It is a real reinforcement type but not the one the row cites.
- **Emergent correlatives already happen.** In 39.5% of lects, WHERE, HERE and THERE were all built with the same
  'place' affix at some point. That is a real *where/here/there* pattern, arrived at by accident, and erosion then
  removes it.

### 1.4 Proposal: a correlative system in `lexsys`

Model it like the numeral, colour and kin systems (`lexsys.set_numerals`, `system_word`): a stored system that owns
how its cells are built and renewed.

**1. Proto draw** (`lexsys.set_correlatives`, in `proto_lexicon` after the kin system):
- **Stems.** One interrogative stem Q (the WHAT root) and an optional second interrogative stem Q2 for WHO (Turkish
  *k-/n-*, Finnish *ku-/mi-*, Hungarian *ki/mi*). Proximal and distal deictic stems D1 and D2 (the THIS and THAT roots).
  An optional selective stem S, 'which', which can serve as the base for place and manner (Mandarin *nǎ-*).
- **Cells.** The categories are person, thing, place, time, manner, reason and quantity. The type per cell is drawn
  from weights set from Ultan, Cysouw and Diessel:
  - person and thing are mostly independent roots;
  - place is an independent root about half the time;
  - time, manner, reason and quantity are mostly built.
- **Formatives.** One per built category, each with a recorded source taken from new rows in `derivations.tsv` with a
  `relation` per category. The sources are grammaticalisation paths in Heine & Kuteva (2002) and Kuteva et al. (2019):
  - PLACE: a place noun or a locative case;
  - TIME: TIME/DAY or a temporal case;
  - MANNER: 'like/way';
  - REASON: 'for/because' (BECAUSE is a concept already) or a causal case;
  - QUANTITY: 'much/many'.

  This gives WHEN a time formative of its own, which removes the WHERE = WHEN collision at the source.
- **Shared formatives across rows.** The same formative builds the interrogative and both deictic rows: WHERE = Q+place,
  HERE = D1+place, THERE = D2+place. A lect with a case system can use its locative case gram as the place formative
  (the Finnish *mi-ssä* pattern), read from `grams`.
- **Stem position.** Following the lect's affix order (`affixes[..].suffix`; 61% suffixing in a24559), so suffixing
  lects get the English and Japanese look of a shared initial stem.

**2. Erosion and renewal.**
- **Sound change** applies to the cells as to any word.
- **Analogical levelling** is new. After each step, if a built cell's stem portion no longer matches the current
  stem but differs by at most one segment, then with probability `LEVEL_P` per generation it is re-levelled to the
  stem. This is the paradigm-internal analogy that kept English *wh-* together (Kuryłowicz's and Mańczak's tendencies:
  the basic form remodels the derived). It does not apply to independent roots.
- **Opacity.** Once a cell's formative has worn to nothing or merged, the cell is recorded as opaque, as *how* and *why*
  are in English. Opaque cells are renewed only by the normal hazard.
- **Renewal.** A cell that comes up for replacement is rebuilt by the system's recipe on the *current* stem and
  formative (French *pourquoi*, *comment*), or reinforced (Spanish *dónde* < *de + unde*), or renewed by a new
  periphrasis that becomes its formative (Turkish *ne zaman*). This replaces the general SOURCES draw for these cells,
  as `system_word` does for composite numerals.
- **Paradigm repair.** `core_repair` still guards the set. Its WHO row becomes WHAT+PERSON as the data row intends.
- **Loans.** Interrogative cells keep the closed-class rule, and their loan share should fall towards WOLD once the
  collisions stop.

**3. Indefinites.** The system draws an indefinite strategy per lect from Haspelmath's types:
- interrogative-based: the bare interrogative (Mandarin, Warlpiri) or interrogative + marker (Japanese *-ka*, Hungarian
  *vala-*);
- generic-noun-based ('some person', 'some thing');
- mixed.

The draw is weighted by the WALS 46A counts. A second series covers negation and free choice, as a contiguous stretch
of the semantic map. The marker comes from a grammaticalisation source: 'or', 'some', 'one', 'also/even' (Japanese
*-mo*), 'want' (free choice). These are system cells (someone, something, somewhere, nobody, nothing, anywhere), not
concepts, so the concept list stays unchanged. `grammar.py` can then use the negative series as the NEG source it
already allows (NOTHING > NEG is G068).

**4. New concepts.** WHY, WHICH and THEN (and optionally HOW MANY). They are frequent in texts and needed for a
believable table. WHY = 'for what' and THEN = D2+time.

**5. Language page.** The grammar sketch "Questions" topic gets a correlative table (rows = categories; columns =
question / near / far / some- / no-). Built cells are shown with their morpheme split. Each cell gets a one-word note:
"built", "worn (opaque)", "renewed 3 kyr ago from 'for what'". The existing sentence examples stay. The proto page shows
the drawn grid, and daughters show how it eroded. That makes the family resemblance visible, which is the point.

**6. Check.** Add a row to `checks.py`: the share of living lects with ≥3 interrogative cells sharing a visible stem, in
a band (decision 1.2). Also add WH loan share ≤ about 6%.

### 1.5 Effort, risks, cost

- **Effort: M** (about 2 lane-days).
  - `lexsys.py` system: about 300–400 lines.
  - `derivations.tsv`: about 25 new formative rows with sources.
  - Three concepts.
  - Sketch table in `sentences.py`/viewer.
  - Tests and one check.
  - A language pass on a24559 to measure (owner-authorised compute; this lane did none).
  - Indefinites add **S–M** on top.
- **Changes.** Golden outputs and every lexicon (new concepts shift the RNG streams). Cognate scores move slightly,
  because more of the core is built from shared stems. WH loan share drops. Function words get longer where cells are
  built: PW-1570 drew them short, and a built cell may be 2–3 syllables. The analogical levelling keeps that in check;
  the median function-word length needs watching.
- **Risks.**
  - Over-regularity: too many tidy Japanese-style grids. The per-cell type weights and the erosion are the brake.
  - Interaction with `core_repair` and the homophone boost.
  - Proto RNG drift across all runs (harmless under the no-backward-compatibility rule).
- **Realism against cost.** The visible payoff is large for a linguist reader: a page that shows *where/there/here*
  families across a family tree. The machinery mostly reuses the lexsys pattern. The cheapest real gain is two
  one-line data fixes, a TIME formative row and a WHAT+PERSON head (option A below). Those alone remove most WH
  homophone repairs and loans, but they do not create visible paradigms.

### 1.6 Decisions for Daniel

**D1.1 Scope.**
- (A) Data fixes only: a 'time' formative for WHEN, WHO = WHAT+PERSON, and a matching 'reason' row. **S.**
- (B) The correlative system with interrogative and deictic rows, levelling and the page table. **M.**
- (C) B plus the indefinite and negative series on Haspelmath's map. **M–L.**

*Lean: B now, with C as the follow-up ticket.* A is worth doing even if B waits.

**D1.2 Calibration.** How many living lects should show a visible shared interrogative stem (≥3 cells)?
- (A) No bar; show it only.
- (B) A band set from a 40–50-language sample the lane compiles from reference grammars (WALS sample languages), before
  tuning.
- (C) A band you set by judgement now (for example 30–60%).

*Lean: B.* The literature gives categories, not a share, and you are better placed than any of us to judge (C) if you
prefer.

**D1.3 New concepts.**
- (A) WHY, WHICH, THEN.
- (B) A plus HOW MANY, THUS and the indefinites as concepts.
- (C) None; system cells only.

*Lean: A.* The indefinites live as system cells, so the concept list stays a vocabulary list.

---

## Part 2. Conquest and trade borrowing: prestige layers, food doublets, numerals

### In plain words

The engine borrows words, and it borrows the right *kinds* of words more often in general: temple words more than body
words. What it does not do is change *which* words get borrowed according to *who* the neighbours are. A conquering
elite, a trading partner and a next-door village all hand over the same mix. So there is no Norman layer of law and
cuisine words, and no Swahili layer of Arabic market and number words. Separately, every meaning has exactly one word,
so the native word cannot survive beside the loan with a different job (cow beside beef). Also, the concept list has no
"beef", "pork" or "mutton", and only two law words.

The food picture today is the reverse of English. Farm-side words are borrowed more than kitchen-side ones:
- pig is a loan in 57% of languages, meat in 25%;
- wheat in 76%, flour in 32%.

This is partly realistic: crops really do travel with their names along trade routes. But no conquest ever pushes the
kitchen vocabulary.

The proposal has three parts:
1. Each contact kind gets a field profile: rulers give law, faith, war and cuisine; traders give market, money, measure
   and big-number words; a substrate keeps landscape, plants and animals.
2. A doublet step: when a loan arrives while the native word survives, the two can split the meaning (the animal versus
   its meat, the ingredient versus the dish) or the register (everyday versus formal).
3. The pages say where words came from: "came in with the conquerors".

### 2.1 Findings: typology

**Kinds of contact and what they leave.** Thomason & Kaufman (1988, *Language Contact, Creolization, and Genetic
Linguistics*) separate two routes:
- **Borrowing.** Speakers keep their language and take words from another. Content and non-basic vocabulary come first,
  structure only under intense, long contact (their borrowing scale, stages 1–5).
- **Shift-induced interference.** A population learns a new language imperfectly. It brings phonology and syntax, and
  few words.

The three labels follow from this:
- **Superstrate.** The language of a dominant group that later shifts, or that the dominated borrow from: Frankish in
  French (*guerre* < *\*werra*, *garder*, *blanc*); French in English.
- **Substrate.** The language of a shifting, dominated group. It leaves toponyms, local flora and fauna, and local
  cultural terms: Celtic river names in England (*Avon, Thames*), Pre-Greek *-nthos/-ssos* names and plant words
  (*hyákinthos, terébinthos*).
- **Adstrate.** A neighbour of comparable standing. It can reach basic vocabulary when the languages are close and the
  bilingualism is intimate: Norse in English (*they, egg, sky, skin, take*).

**Which fields borrow.** The Loanword Typology project (Haspelmath & Tadmor 2009, *Loanwords in the World's Languages*;
Tadmor 2009: 64, field table as reproduced by later work) gives the share of borrowed words per field, averaged over 41
languages:

| field | borrowed share |
|---|---|
| religion and belief | 41.2% |
| clothing and grooming | 38.6% |
| the house | 37.2% |
| law | 34.3% |
| social and political relations | 31.0% |
| the body | about 14% |

Sense perception, spatial relations and kinship are lowest as well. These are averages over contact *types*. In
individual languages the profile follows the donor's role.

**English.** WOLD (Grant 2009) puts English at about 41% borrowed meanings, against a mean of about 24%. Baugh & Cable
(*A History of the English Language*, 5th ed. 2002, ch. 7) list the French domains: government and administration, the
church, law, army and navy, fashion, food and social life, art, learning and medicine. The three-layer register
stratification has three tiers: Germanic everyday, French formal, Latin learned. It shows in the triplets:
- *ask / question / interrogate*;
- *kingly / royal / regal*;
- *rise / mount / ascend*;
- *fear / terror / trepidation*.

**The cow/beef pattern.**

| native (the animal) | French loan (the meat) |
|---|---|
| cow, ox | beef < OF *boef* 'ox' |
| swine, pig | pork < *porc* 'pig' |
| sheep | mutton < *moton* 'ram, sheep' |
| calf | veal < *veel* 'calf' |
| deer | venison < *venesoun* 'hunted game' |

The donor words meant the *animal*. The meat sense is a specialisation inside English. It was slow:
- *beef* still meant the live ox into the 17th century (plural *beeves*);
- the observation is usually traced to John Wallis (*Grammatica linguae Anglicanae*, 1653) and popularised by Scott's
  *Ivanhoe* (1819);
- Durkin (2014, *Borrowed Words*) cautions that the specialisation postdates the Conquest by centuries.

So the mechanism is "a loan for an existing meaning enters as a doublet, then the pair differentiates", not instant
replacement.

Comparable cases:
- Japanese *niku* 'meat' is a Sino-Japanese loan that displaced native *shishi*. The meats are Sino or hybrid
  compounds: *gyūniku* 'beef' beside native *ushi* 'cow', *butaniku*.
- Thai *rachasap*, the royal register, takes Khmer, Pali and Sanskrit words for everyday meanings.
- In Indic, the *tatsama/tadbhava* doublets are learned Sanskrit forms beside inherited ones.

The global default is different. Most languages say "cow-meat" with a compound (German *Rindfleisch*, Korean *sogogi*,
Mandarin *niúròu*). A specialised meat noun is the special case, and conquest is one way to get it.

**The ingredient against what is made from it.** This tracks technology diffusion more than conquest. The made thing is
often borrowed *with the technique*:
- Germanic took Latin *vīnum* (*wine, Wein*) and *cāseus* (*cheese, Käse*), and *coquina* (*kitchen*);
- Early Latin trade gave Germanic *caupō* 'trader' > *kaufen*, *cheap*; *mercātus* > *Markt*; *monēta* > *Münze,
  mint*; *pondō* > *Pfund, pound*;
- Germanic *\*kaupa-* went on into Finnic (Finnish *kauppa* 'trade, shop').

Crop names spread as Wanderwörter: *sugar* < Arabic *sukkar* < Sanskrit *śarkarā*; *rice*; *tea/chai*. So in real data
the raw side *also* borrows heavily when the crop itself is new. The conquest pattern (prepared side borrowed, farm side
kept) and the diffusion pattern (both sides borrowed with the new thing) coexist.

**Trade layers: numerals and commerce.**

*Swahili*, checked against Wiktionary etymologies:
- **Numerals.** *moja, mbili, tatu, nne, tano, nane, kumi* are Bantu. *sita* 6, *saba* 7 and *tisa* 9 are Arabic
  (*sitta, sabʕa, tisʕa*); Bantu *kenda* 9 survives beside *tisa*. The tens from 20 (*ishirini … tisini*) are Arabic, as
  are *mia* 100 and *elfu* 1000. *laki* 100,000 is Hindustani *lākh* (< Sanskrit *lakṣa*); *milioni* is English.
- **Commerce and law:**

  | word | meaning | source |
  |---|---|---|
  | *bei* | price | Arabic *bayʕ* 'sale' |
  | *biashara* | trade | Arabic *bāʕa* 'sell' + *šarā* 'buy' (per Wiktionary; a Persian source has also been proposed) |
  | *soko* | market | Arabic *sūq* |
  | *duka* | shop | Arabic *dukkān*, probably back-formed from *\*dukani* read as *duka* + locative *-ni* |
  | *hesabu* | account, arithmetic | Arabic *ḥisāb* |
  | *faida* | profit | Arabic *fāʔida* |
  | *deni* | debt | Arabic *dayn* |
  | *sheria* | law | Arabic *šarīʕa* |
  | *serikali* | government | Omani Arabic *sörkār* < Persian *sarkār*, so Persian, not Arabic |
  | *bandari* | port | Persian *bandar* |
  | *pesa* | money | Hindustani *paisā*, so Indic |

  The layer is a trade and coastal-city layer (Indian Ocean commerce, Omani rule on the coast), not one source language.

*Malay* has a Sanskrit layer from the Indianised kingdoms and an Arabic layer with Islam:
- Sanskrit: *harga* 'price' < *argha*; *niaga* 'trade' < *vāṇija*; *bahasa* < *bhāṣā*;
- Arabic: law, religion and time (*hukum, waktu*).

*Japanese and Korean* have two full numeral sets:
- Japanese native *hito-, futa-, mi- … tō* (to 10 only) beside Sino-Japanese *ichi, ni, san*;
- Korean native *hana, tul, set* (to 99) beside Sino-Korean *il, i, sam*;
- the Sino sets own money, dates, measures and all large numbers, which is the trade and administrative domain.

*Thai*: most numerals from 3 up (*sǎam, sìi, hâa, hòk, cèt, pɛ̀ɛt, kâaw, sìp*) are early Chinese loans.

*Hausa*: an Arabic layer in religion, law and writing (*alƙali* 'judge' < *al-qāḍī*, *alƙalami* 'pen' < *al-qalam*).

The generalisation is that trade brings commerce, measure and money words. It brings numerals above some threshold
first (hundreds, thousands, the units used in reckoning). Low numerals follow only under long, intense commercial
bilingualism (Swahili 6–9, Thai, Japanese and Korean).

### 2.2 What the engine does now

**Mechanism** (verified in code):
- **Loans replace; they never add.** A word is replaced with the frequency-class hazard. If a contact lect has the
  concept, the replacement source draws "borrow" with weight `LOAN_MAX × intensity × loan_factor(k, intensity)`
  (`lexicon.py:2240`). `loan_factor` depends only on the meaning's WOLD score and the summed intensity.
- **The donor** is drawn by its pull (`history.loan_weights`, `history.py:433`): `LOAN_CONTACT × contact ×
  prestige ratio / PRESTIGE_CAP`, plus the deme's bilingual share in the donor. Same-deme speech pulls at
  `MINORITY_PULL`. Prestige does steer *how much* flows downhill, but not *what*.
- **Contact kind** (`elite, takeover, swamp, city, trade` in `inputs.Trigger`, `history.KIND_WEIGHT`) enters only
  `shift_step`, as the shift rate. It never reaches `loan_weights` or `step`.
- **On a shift**, `substrate_transfer` keeps the old lect's local words (landscape, local plants and animals, names;
  `local_concepts`) with a chance of 0.1–0.3 each, whoever is shifting. For a `swamp` trigger the *newcomers* shift to
  the locals' speech (`inputs.py:661`). Even then they "keep" their own words for the local landscape, which is the
  substrate profile applied to a superstrate.
- **Specialised channels:**
  - food routes carry crop names (`with the oil seeds …`);
  - `tech_step` carries BREAD, BEER, CHEESE, WINE and others with the technique (`TECH_LOAN` 0.7);
  - faiths carry sacred words as learned loans (`faiths.learned_step`).
- **One word per concept** (`Lexicon.get/set`). The only doublets are the faiths' `systems.learned` register and the
  avoidance register (`lexsys`), stored beside the lexicon, not in it.
- **Numerals are not closed to borrowing.** `closed_class` only blocks the *fallback* loan (`lexicon.py:2092`). The
  "borrow" source and `core_repair` loans still reach them.

**Measured on a24559** (living lects; "loan" = the word's latest word-making step is `borrow:`, as in the WOLD check):

*Loans by donor relation and field group.* "Prestige" = law, social and political, social, religion, warfare.
"Nature" = animals, crops, agriculture, physical world, landscape. "Goods" = house, clothing, technology, trade goods.

| donor relation | loans | prestige | food | nature | goods | other |
|---|---|---|---|---|---|---|
| other deme (all contact) | 134,397 | ×1.19 | ×0.84 | ×1.01 | ×1.22 | ×0.96 |
| same deme, minority ← dominant (the conquered speech) | 5,218 | ×1.10 | ×0.87 | ×0.91 | ×1.22 | ×1.00 |
| same deme, dominant ← minority | 3,168 | ×1.13 | ×0.87 | ×0.90 | ×1.19 | ×1.00 |
| substrate (kept on shift) | 1,121 | 0 | 0 | ×5.49 | ×0.33 | ×0.04 |
| learned (liturgy) | 461 | all | — | — | — | — |

(×n = the group's share of these loans over its share of all words.) The three contact rows are the same profile: the
conquered speech borrows from its rulers exactly as from any neighbour. The substrate and learned channels do have
profiles.

*Field rates against Tadmor (2009).* The engine is 30% borrowed overall. Religion is highest (55.9%), then clothing
(44.8%), and the order at the top is plausible. The range is compressed, though:
- body 30.5% against Tadmor's ~14%;
- spatial relations 38.7%;
- kinship 20.9%.

The engine also counts loans between close relatives as loans, which WOLD mostly cannot detect.

*Prestige vocabulary on the list.* The concept list has 2 Law concepts (STEAL, THIEF), 9 social and political, 6
religion, and no JUDGE, LAW, COURT, TAX, PRICE, MONEY, DEBT, WEIGH, MEASURE. There are no species-meat concepts
(beef, pork, mutton).

*Food pairs* (living lects that have both words; "derived" = the prepared word's etymology runs through the raw word's
root):

| raw / prepared | lects | colexified | derived | raw loan | prepared loan |
|---|---|---|---|---|---|
| cattle / MEAT | 620 | 0 | 0 | 17.6% | 24.7% |
| PIG / MEAT | 620 | 0.2% | 0 | **57.3%** | 24.7% |
| SHEEP / MEAT | 620 | 0 | 0 | 44.7% | 24.7% |
| wheat / FLOUR | 271 | 0 | 0 | **76.4%** | 31.7% |
| wheat / BREAD | 224 | 0 | 0 | 72.3% | 42.9% |
| GRAIN / FLOUR | 620 | 0 | 43.1% | 46.0% | 24.4% |
| FLOUR / BREAD | 490 | 1.8% | 11.0% | 28.0% | 35.1% |
| GRAIN / BEER | 491 | 0 | 0 | 53.8% | 32.2% |
| MILK / CHEESE | 341 | 0 | 28.2% | 54.5% | 45.7% |
| MILK / BUTTER | 620 | 0 | 22.7% | 48.9% | 34.0% |
| vine / WINE | 134 | 0 | 0 | 66.4% | 56.0% |
| HONEY / MEAD | 486 | 14.8% | 37.7% | 40.1% | 34.0% |
| FISH / FISH SAUCE | 423 | 0.5% | 92.0% | 25.5% | 23.2% |

Three readings:
- The prepared side is often *built from* the raw side: fish sauce from fish, flour and porridge from grain (43–44%),
  mead from honey, cheese from milk. That is good and realistic.
- With no species meats there is nothing to split, so the cow/beef case cannot even be posed.
- The farm side borrows *more* than the kitchen side in every pair. That comes from WOLD scores (PIG 0.30, MEAT 0.13)
  and the crop routes. It is the diffusion pattern, and no conquest pattern exists to offset it.

*Commerce and numerals* (current loan share; WOLD score in brackets):

| word | loan share | WOLD score |
|---|---|---|
| BUY | 33% | 0.15 |
| SELL | 31% | 0.17 |
| MARKET | 32% | 0.67 |
| PAY | 52% | 0.30 |
| LEND | 36% | 0.08 |
| MERCHANT | 28% | 0.33 |
| TRADE OR BARTER | 52% | 0.26 |
| COUNT | 60% | 0.23 |
| RICH | 76% | 0.28 |
| POOR | 76% | 0.45 |
| ONE–TEN | 11–28% | 0.13–0.29 |
| HUNDRED | 39% | 0.42 |
| THOUSAND | 61% | 0.58 |
| ELEVEN–FORTY | 2–4%, nearly all `contact (paradigm repair)` | — |

Commerce loans come from ordinary contact, not from trade partners: no channel distinguishes them. MARKET is
*under*-borrowed relative to its score. RICH and POOR are far over, which needs its own look. Numerals do borrow, and
the gradient (thousand > hundred > units) is right, but nothing ties numeral loans to trade.

*Checks.*
- `loans follow borrowability (WOLD)`: rho 0.407 (bar ≥ 0.3).
- Pronoun loans 0.076 (cap 0.08). The cap is nearly binding, and any profile change must not push it over.
- Shifts on a24559 by trigger kind: takeover 87, swamp 44, trade 5, elite 1.

### 2.3 Proposal

**P1. Contact-kind field profiles.** Carry the trigger kind into the donor pull.
- `loan_weights` returns `{donor: (pull, kind)}`:
  - `elite` or `takeover` when a live trigger has that donor's deme as ruler;
  - `city` for a mixed city;
  - `trade` for a trade trigger or a food or tech route partner;
  - `swamp` (newcomers absorbed);
  - `neighbour` otherwise;
  - `bilingual` for same-deme speech.
- In `step`, the borrow weight becomes `LOAN_MAX × intensity × loan_factor(k) × m(kind, field(k))`. The donor for k is
  drawn by `pull × m(kind, field(k))`, so the ruler supplies the law word and the trade partner the market word.
- Each profile is normalised so its mean over the concept list is 1. Overall loan volume is unchanged; only its
  distribution moves.

Starting multipliers (set from Tadmor's field spread and Baugh & Cable's French domains):

| kind | raised (×2–3) | lowered (×0.5) |
|---|---|---|
| elite / takeover (superstrate) | law, social and political, religion, warfare, clothing, the house, prepared food and cuisine (BREAD, CHEESE, WINE, SOUP, FEAST, the new meat concepts) | body, kinship, sense perception, motion, basic verbs, nature |
| trade | commerce (BUY, SELL, MARKET, PAY, LEND, MERCHANT, and new PRICE, MONEY, DEBT, WEIGH, MEASURE), trade goods and metals, crops, spices, drinks; numerals HUNDRED and up ×3, low numerals ×1 (raised to ×2 for SIX–NINE only past a long, high-intensity trade link, the Swahili and Thai case) | body, kinship |
| city | crafts, house, clothing, food | — |
| neighbour / swamp / bilingual (adstrate) | — | flat (×1) |

Substrate on shift: keep `substrate_transfer` for the conquered shifting to the rulers' speech. When the *newcomers*
shift (a `swamp` trigger: Franks in Gaul, Normans in England), keep the elite profile's fields instead of
`local_concepts`. Those are the superstrate words (war, rule, cuisine, dress).

Closed class: the multiplier is 1 for pronouns, WH words and deictics, so the pronoun cap is untouched.

**P2. Doublets: meaning split and register split.** When a loan is drawn for concept k under an elite or takeover pull,
and the native word is not itself up for loss, the loan enters as a doublet with probability `DOUBLET_P[kind]` instead
of replacing the native word. It then resolves one of two ways:

- **Meaning split** (the cow/beef type), where k has a *split child* in a new `splits.tsv` table:
  - animal → its meat: cattle → `meat:cattle`, pig → `meat:pig`, caprine → `meat:caprine`, fowl → `meat:fowl`, deer →
    `meat:deer`;
  - ingredient → product: MILK → CHEESE/BUTTER, GRAIN/wheat → FLOUR/BREAD, vine → WINE, HONEY → MEAD.

  The loan, which is the *donor's word for k*, takes the child concept. The native word keeps k. This is exactly the
  English mechanism: OF *boef* 'ox' becomes English *beef* 'ox meat'. The child's etymology says "borrowed for
  'cattle', narrowed to its meat".

  For lects without a split, the new meat concepts are built the global-default way: a compound of the animal + MEAT
  (Rindfleisch, sogogi, niúròu), a `compounds.tsv` recipe. Most lects then have *cow-meat*, and conquered ones may have
  a *beef*. The split also fires through `tech_step` when the dish arrives with a technique (cheese, wine), reproducing
  the Germanic Latin layer.
- **Register split** (ask / question): no split child. Both words are kept, the loan in a `systems.registers.high`
  table like the faiths' `learned` register (same shape: `{concept: [ipa, "doublet" | "synonym", donor, kyr]}`). The
  sketch shows the pair. Over time a doublet either specialises (a small hazard moves it to a split child if one exists)
  or one member dies (by the normal hazard). Doublets are not permanent.

The lexicon stays one word per concept. Doublets live as sibling concepts (split children) or in a register table, so
`Lexicon.get`, families and cognate scoring are untouched.

**P3. New concepts** (needed for P1 and P2 to show):
- the five meat concepts;
- commerce: PRICE, MONEY, DEBT, WEIGH or MEASURE, PROFIT;
- prestige: LAW, JUDGE, TAX, COURT (or ASSEMBLY), NOBLE.

That is about 15 concepts. WOLD scores exist for most of them (Haspelmath-2009-1460 list), and the rest fall back
through `Concept.base`.

**P4. Pages.**
- Each loan's etymology line names its channel: "came in with the [ruling people] (elite rule, 4.2 kyr ago)", "from
  the traders of [deme] (trade)", "kept from the old speech (substrate)".
- A per-language "layers" table: rows = donor languages; columns = channel, period, number of words, and the top
  fields with three sample words each. This is the Norman/Norse/Latin summary a linguist expects.
- A "doublets" list: *native / loan — sense of each* (cow / beef). Food pairs come first, since they feed the culinary
  pages.

### 2.4 Effort, risks, cost

- **Effort.**
  - P1: **M**. Plumbing the trigger kind into `loan_weights`, the field multiplier table, the swamp-direction substrate
    fix and tests.
  - P2: **M**. The splits table, the doublet draw, the register table and the sketch.
  - P3: **S**. Data plus golden refresh.
  - P4: **S–M** (viewer).
  - Total about 3–4 lane-days, plus one language pass to measure.
- **Interaction with the checks.**
  - *WOLD rho* (0.407): profiles are mean-normalised and raise the fields WOLD already ranks high. Expect rho to hold
    or rise, though per-meaning shares become less uniform across lects. Re-measure.
  - *Pronoun cap* (0.076 of 0.08): untouched by the closed-class multiplier of 1. Still near-binding, so watch it.
  - *WH loans*: unaffected here, and fixed by Part 1.
  - A new check is worth adding: the elite-donor loan field profile should differ from the neighbour profile (prestige
    share ×≥1.5 of baseline). Also: in lects under elite rule for ≥2 kyr, at least some meat or product splits.
- **Risks.**
  - Trigger kinds are skewed (takeover 87, elite 1 on a24559), so "elite" in practice means takeover. Fine, but the
    elite profile must be on takeover too.
  - Doublets add words that the sentences and names code does not expect. Keeping them as sibling concepts avoids
    that.
  - Food routes already dominate crop loans. The trade profile must not push crop loans further (wheat is already 76%).
    Cap the trade multiplier on crops at ×1.
- **Realism against cost.** P1 is the core realism gain and is cheap relative to its effect, because every conquered
  language then reads differently from a neighbour-influenced one. P2 is the payoff for the culinary pages (beef, pork,
  cheese words with histories). It is worth doing, but it depends on P3's concepts. Without P3 neither shows, so P3 is
  not optional.

### 2.5 Decisions for Daniel

**D2.1 Profiles.**
- (A) Field profiles by contact kind (P1), mean-normalised.
- (B) A, plus the swamp-direction superstrate fix on shift.
- (C) Leave borrowing kind-blind.

*Lean: B.* The fix is small, and without it newcomers who shift keep "local landscape" words they never had.

**D2.2 Doublets.**
- (A) Meaning split only (animal/meat, ingredient/product) through a splits table.
- (B) A plus the register split (a high-register table like `learned`).
- (C) None; keep one word per concept.

*Lean: B.* Food splits first, because they serve the culinary pages. The register table reuses the faiths' shape.

**D2.3 Numerals under trade.**
- (A) Trade raises HUNDRED and up only.
- (B) A, plus SIX–NINE after long, intense trade (the Swahili and Thai case) and a second numeral set kept as a register
  when a whole series is borrowed (the Japanese and Korean case).
- (C) Leave numerals as they are; they already borrow at WOLD-like rates.

*Lean: A now, B as a follow-up.* The double numeral sets are striking but need the register machinery from D2.2 B
first.

---

## Sources

- Baugh, A. C. & T. Cable. 2002. *A History of the English Language*, 5th ed. Routledge. Ch. 7.
- Corbett, G. 1991. *Gender*. Cambridge University Press.
- Cysouw, M. 2004. *Interrogative words: an exercise in lexical typology*. Workshop handout; see MPI-EVA, *Typology of
  content interrogatives* (https://www.eva.mpg.de/linguistics/past-research-resources/typological-surveys/typology-of-content-interrogatives/).
- Diessel, H. 1999. *Demonstratives: Form, Function and Grammaticalization*. Benjamins (TSL 42).
- Diessel, H. 2003. The relationship between demonstratives and interrogatives. *Studies in Language* 27(3): 635–655.
- Durkin, P. 2014. *Borrowed Words: A History of Loanwords in English*. Oxford University Press.
- Grant, A. 2009. Loanwords in British English. In Haspelmath & Tadmor (eds.), *Loanwords in the World's Languages*.
- Haspelmath, M. 1997. *Indefinite Pronouns*. Oxford University Press.
- Haspelmath, M. 2013. Indefinite pronouns. WALS Online, ch. 46 (https://wals.info/chapter/46).
- Haspelmath, M. & U. Tadmor (eds.). 2009. *Loanwords in the World's Languages: A Comparative Handbook*. De Gruyter.
- Heine, B. & T. Kuteva. 2002. *World Lexicon of Grammaticalization*. CUP. Kuteva et al. 2019, 2nd ed.
- Idiatov, D. 2007. *A typology of non-selective interrogative pronominals*. PhD thesis, University of Antwerp.
- Mushin, I. 1995. Epistememes in Australian languages. *Australian Journal of Linguistics* 15(1): 1–31.
- Tadmor, U. 2009. Loanwords in the world's languages: findings and results. In Haspelmath & Tadmor (eds.), 55–75.
- Thomason, S. G. & T. Kaufman. 1988. *Language Contact, Creolization, and Genetic Linguistics*. University of
  California Press.
- Ultan, R. 1978. Some general characteristics of interrogative systems. In J. Greenberg (ed.), *Universals of Human
  Language* 4: 211–248. Stanford University Press.
- Wiktionary, Swahili entries *bei, biashara, duka, serikali, soko* and Appendix:Swahili numbers (consulted
  2026-11-10).

Language examples not attributed above are standard reference-grammar facts. The Tadmor field percentages are quoted
from a secondary reproduction of his table and should be checked against the book before they become calibration
targets.
