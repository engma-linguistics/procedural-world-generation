# Names and spelling review: real naming traditions and romanizations against the generator

Branch `lang-design` at 9e51ac2e. This was a read-only review: nothing in the repo was changed. Code paths below are
relative to the worktree. "Live" figures are from run a24559, tallied read-only from `runs/a24559/languages.json`
(627 living lects, 37 peoples, 235,255 lexicon entries, 2,305 names: endonyms, exonyms and places). The scripts are in
the scratchpad `ns/` folder. Full spellings are the ones stored in the run. Book spellings were **recomputed with the
current `romanize.py`** from each word's stored IPA and the lect's segment set, so they show today's rules, not the
4 November ones. The owner's taxonomy is "Ethnonyms: A Taxonomy for Culture Generation" (Claude Doc
7b3b1078-…, rev 7). Facts about real traditions are from general knowledge. They are marked "≈" where they are
approximate or contested.

Sister review: `docs/review/language/grammar-gaps.md`. The coverage scale is the same:

- **full**: the mechanism exists and the output shows it;
- **partial**: something exists, but it is thinner than the real thing or rarely realised;
- **label only**: the output claims it, but nothing carries it out;
- **none**: nothing.

---

## 1. Summary table

| Tradition / system | Distinctive feature | Coverage | Note |
|---|---|---|---|
| **Personal names (all traditions)** | Given names, bynames, family names | **none** | No personal-name generator exists. The only person-like name is E5's ancestor, a random meaningless 2-syllable draw (`names.py:499-502`) |
| **Icelandic patronymics** | Father's name in the genitive + *-son/-dóttir* | none | Every piece is in place: GEN grams, SON and DAUGHTER in all 627 lexicons, compounding. Nothing joins them |
| **Chinese surname + given name** | Small closed surname pool, family name first, 1–2-syllable given names chosen for meaning | none | No name order, no surname pool, no meaning-chosen given names |
| **Arabic ism/nasab/kunya/laqab/nisba** | A name chain: *ibn* X *ibn* Y, *Abu* Z, an epithet, a place adjective (*al-Baghdādī*) | none (the hooks exist) | The lexicon's 'like' affix is a ready nisba (`names.py:805`, used only for scholars' names) |
| **Malagasy long names** | Whole descriptive phrases as names, with noble/honorific prefixes | none | Names are capped at 4 syllables × the length scale (`names.py:42`, `:145-154`) |
| **Yoruba meaningful names** | Clause names about the birth (*Babatunde* 'father has returned'), theophoric names, praise names | none | `sentences.py` could build clause names, and GOD is in every lexicon. Nothing uses them for names |
| **Germanic dithematic names** | Two themes from a closed pool (*Wil-helm*), recombined in families, later made opaque by sound change | none | This is the best fit for the engine: themes are lexicon words, and sound change would make them opaque, as *Wilhelm* became *Bill* |
| **Place names: rivers** | Old substrate hydronyms survive (*Avon* 'river'); tautologies (*River Avon*) | **partial (good)** | Named by the first lect on the river, kept as substrate by newcomers: 291 of 1,237 places (24%). No tautologies |
| **Place names: settlements** | Generic + specific (*-ton*, *-by*, *-grad*, *Kraków* 'Krak's') | **none** | No town names at all. TOWN, VILLAGE, FORD, HILL and VALLEY are in all 627 lexicons |
| **Place names: land, sea, peak, lake** | Land named after its people (*England*); landscape words | full / partial | 'Land of the X' from the people set. Modifiers come from a fixed list of 6–9 adjectives (`names.py:63-64`) |
| **Ethnonyms: endonyms** | E1–E12 patterns | partial | 9 of 12 patterns fire. **The code's pattern numbers do not match the owner's taxonomy** (§4.8) |
| **Ethnonyms: exonyms** | X1–X9 patterns | partial | 7 of 9 fire. X4 relay 0 rows; X6 has no code path. The code's X6 and X9 mean different things from the doc's |
| **Name-change processes** | P1–P8 | partial | Only P2 (substrate) fires, plus a scholars' name filed as "P8". P1 conquest, P3 adopted exonym, P5 renaming, P6 name > word and P7 split are absent |
| **Glossonyms** | Language name can differ from the people's name (*Euskara*/*Euskaldunak*, *nešili*/*Hatti*) | partial | A noun-class 'manner' prefix (Bantu *Lu-ganda*) or a 'speech of' compound. Never a separate root |
| **Scholars' names** | Type sites, artefacts, reconstructions | partial | One recipe: river or landmass + the Common's 'like' suffix. All 56 families end in *-ba* |
| **Romanization: one lect's consistency** | Same sound, same letters across the lexicon | full (workbench) / **partial (book)** | Book mode's "one diacritic per word" and "one doubled vowel per word" rules spell one phoneme two ways in one lect |
| **Romanization: related languages** | Shared conventions by descent | full, by uniformity | Sister cognates with the same IPA differ in spelling in 2.4% of cases (book 1.3%). But every one of the 265 families uses the same house system |
| **Tone** | pinyin marks / numbers, Yoruba accents, Hmong letters | full (workbench) / none (book) | Book drops tone. In the 237 tonal lects, 3,810 sets of words become homographs that differ only in tone |
| **Aspiration** | Wade–Giles ' vs pinyin b/p | partial | Written as *h*. One aspirate anywhere flips *sh th kh ch* to *š þ x č* across the whole lect |
| **Allophones** | Hepburn (phonetic) vs Kunrei (phonemic) | Hepburn-like | Surface sounds are spelled, so lenited [ɣ] of /k/ is *gh* |
| **Clicks** | Zulu *c q x*; Khoisan ǀ ǃ ǁ ǂ | partial | ASCII `| || !` plus Unicode ǂ. A long click comes out as `|:` |
| **Ejectives, implosives, glottal stop** | Americanist *t'*, Hausa *'b*, Hawaiian ʻokina | full but overloaded | One apostrophe serves three jobs. A hyphen disambiguates (*t-'a* vs *t'a*) |
| **Non-human sounds** | none in reality | full but noisy | 26% of names carry *rh/rr/wh/mh*. 2,720 words pile up as *rrrh*, *rhrh* or *rhrr*. Purr *rr* = trill *rr* |
| **IPA leaking into spelling** | an orthography uses letters, not phonetic diacritics | partial | 12.2% of full spellings (415 lects) carry IPA marks (t̪, ï̠, e̞o) |
| **Orthographic depth** (English, French, Irish) | spelling frozen while sound changes | none | Every spelling is a fresh transcription of today's sound |

---

## 2. Why these traditions

I picked one tradition for each way that a culture builds a personal name, plus the place and people names the engine
already makes.

- **Icelandic patronymics.** The name is grammar: a genitive plus a kin noun, re-derived every generation. It tests
  whether the existing GEN gram and kin words can make a name. It is the cheapest tradition to build.
- **Chinese surname + given name.** A fixed, inherited surname from a small pool, a meaningful given name, and name
  order. It tests whether the engine has name order and any notion of an inherited surname.
- **Arabic name chain** (ism, nasab, kunya, laqab, nisba). Five slots, each from a different source: kinship, offspring,
  epithet, place. It is the richest "name as record" system, and it tests whether a name can reuse places and
  derivations.
- **Malagasy long names.** Names and place names are whole descriptive phrases (*Andrianampoinimerina* ≈ 'the prince in
  the heart of Imerina'; *Antananarivo* ≈ 'city of the thousand'). It tests the length cap and phrase-building.
- **Yoruba meaningful names.** Clause names about the birth, theophoric names (*Oluwaseun* 'God has done it') and
  praise names. It tests whether a name can come from a sentence and from a faith.
- **Germanic dithematic names.** Two themes from a closed pool (*wil* 'will' + *helm* 'helmet'), recombined in a family,
  with alliteration or a shared theme (Anglo-Saxon *Æthel-red*, *Æthel-stan*). It is the closest fit to the engine's
  strength, because names become opaque through sound change.
- **Place names.** Three real layers:
  - English *-ton* (OE *tūn* 'enclosure, farmstead'), *-by* (ON *býr* 'farm') and *-ford*: generics that erode into
    suffixes;
  - Slavic *-grad*/*-gorod* 'enclosure, town' and the possessive *-ov/-ów* (*Kraków*);
  - Celtic river names that survive as a substrate (*Avon* < Brittonic *abona* 'river'), and tautologies made when
    newcomers no longer understand the old name (*River Avon*; *Pendle Hill* = hill + hill).
- **Ethnonyms, glossonyms, exonyms.** The owner's E/X/P taxonomy, already the basis of `names.py`.

---

## 3. What the engine has, in brief (checked in code)

- **`planet/language/names.py`** (959 lines) builds four things:
  - **endonyms** by pattern (`:437 endonym_pattern`, `:473 endonym_in`);
  - **exonyms** from reputation rows (`:665 exonym`);
  - **places**: river, lake, sea, peak and land (`:621 places`). Rivers and lakes are named by the first lect on them;
    a later unrelated or shifted lect keeps the name as heard, which is substrate (`:554 water_name`);
  - **the Common's exonyms** and **scholars' names** for dead families (`:798`).
- Forms come from the lect's own words through its grammar:
  - `grammar.people_set` (`grammar.py:2182`) makes person/people/land/language from one root, through a noun class
    (Buganda/Baganda/Muganda/Luganda) or through AGENT/PL/PLACE grams;
  - otherwise PEOPLE heads a compound in the lect's head order.
- `place_name` (`grammar.py:2225`) adds a LOC or PLACE gram.
- **There is no personal-name generator anywhere**, in `planet/language/` or `planet/lineages/`. PW-911 (named
  individuals) is filed for later. `planet/names.py` names landmasses with a hard-coded, English-looking syllable
  generator (`planet/names.py:14-30`: onsets like *br th sh kh*). Those names (*Simath*, *Treram*) then appear inside
  the language output ("first on Simath", "the Simathba languages").
- **`planet/language/romanize.py`** (509 lines, "house/2") has two registers.
  - **Full** (workbench, `roman` in the lexicon): one spelling per segment. It is contrast-dependent: è only when the lect
    also has e; š when the lect writes aspiration, and so on (`:165 contrasts_of`). It marks tone (Yoruba-style) and
    marks non-human sounds with trailing ASCII digraphs (`:263-264`, `:425-429`).
  - **Book** (`roman` in names): lossy, by design (`:16-25`):
    - no tone;
    - a nasal vowel is written as vowel + *n*;
    - only the first long vowel of a word is doubled (`:486-488`);
    - at most one letter with a diacritic per word, the first; later ones are stripped (`:338 _book_cap`).
- **`data/romanization.tsv`**: 136 base rows, each citing the convention it follows (ISO 15919, Czech, Polish,
  Hungarian, Hepburn, Albanian, Korean RR, Vietnamese, Zulu, Hausa, DIN 31635, Semitist).
- **The speller sees surface segments.** `output.Speller` (`output.py:25-28`) and `names._segs` (`names.py:107`) use
  `lect.segments()` (`lect.py:482`), every segment of every word. Allophones are therefore spelled, and they can change
  the contrast set.

---

## 4. Per-tradition sections

### 4.1 Icelandic patronymics

**What makes it distinctive:** no surname. A child is *Jón-s-son* or *Jón-s-dóttir*: the father's name in the
genitive plus 'son' or 'daughter', re-derived every generation (matronymics are allowed). The phone book is sorted by
given name. The name is transparent grammar, not an inherited label.

**Coverage: none.** But every ingredient is live:
- SON and DAUGHTER are in all 627 lexicons;
- GEN grams exist (free, clitic or suffix);
- `grammar.compound` follows the lect's head order.

A patronymic is `compound(SON, gen(father_name))`, or `father_name + GEN + SON` where GEN is bound.

**Could a generated people's names feel like it?** Not today. With a personal-name layer it is the easiest tradition to
get right, and it would show off each lect's own GEN marker: a free GEN gives *Son-of Jon*, Gaelic *mac*-style; a suffixed
one gives *Jonsson*-style.

### 4.2 Chinese surname + given name

**What makes it distinctive:**
- **A small, closed, old surname pool.** ≈100 surnames cover most of the population, and *Wang*, *Li* and *Zhang* alone
  cover ≈20%. Surnames are mostly single syllables from old clan, state or place names.
- **Family name first.** Hungarian, Japanese and Korean do the same, so this is not tied to head-finality in any strict
  way.
- **Given names of one or two syllables, picked for meaning** (virtues, nature, hopes). A **generation name** is shared
  by siblings or cousins.

**Coverage: none.** There is no name order, no surname inventory and no meaning-chosen given name.
- What the engine could reuse: the river and land names it already makes (surnames from places), the people set
  (surnames from clans), and the typology's head order as a weak prior on name order.
- The "closed pool, inherited and frozen" property is the interesting part. A surname should be **coined once and then
  carried down the lect tree with sound change**, as a lexicon entry is. Old surnames then become opaque. That is what
  makes *Smith* feel like a surname rather than a job.

**Could it feel like it?** Not today.

### 4.3 Arabic name chain

**What makes it distinctive:** several named slots.
- **ism**: given name.
- **nasab**: the chain *ibn/bint* X *ibn* Y.
- **kunya**: *Abu*/*Umm* + eldest child, 'father/mother of'.
- **laqab**: an epithet, often honorific or theophoric (*Ṣalāḥ al-Dīn* 'righteousness of the faith').
- **nisba**: an adjective of origin, tribe or trade (*al-Baghdādī*, *al-Qurashī*).

In real use one or two slots carry the name, and which ones depends on context. Clan names *Banu X* ('sons of X') also
show up as ethnonyms (taxonomy E5).

**Coverage: none, but the hooks exist.**
- **Nisba:** the lexicon already derives a 'like' adjective (`lexicon.affixes["like"]`). It is used only for scholars'
  family names (`names.py:805-820`).
- **Nasab:** SON + GEN, as in §4.1.
- **Kunya:** FATHER/MOTHER + a child's name.
- **Laqab:** an epithet compound from GOD, STRONG or a virtue word.
- **Banu X as an ethnonym:** E5 does exist (`names.py:499`), but its ancestor is a random 2-syllable draw with no
  meaning and no later life. It is never a personal name that also shows up elsewhere in the people's history.

**Could it feel like it?** Not today. If built, it would be the most "historical-record" naming style and would use the
deme and place data the run already has.

### 4.4 Malagasy long names

**What makes it distinctive:** names, especially royal names and place names, are whole descriptive phrases, often of
7–10 syllables, and they carry prefixes: *Andriana-* 'noble', *Ra-* honorific, *Ra-* plus a clause. A person can take a
new name on a life event or at death (a posthumous name). Place names are phrases too.

**Coverage: none, and blocked by a cap.**
- `MAX_SYLL = 4` (`names.py:42`), scaled by the lexicon's `length_scale`, clips every ethnonym and place-name root.
- Parts are clipped to 2 syllables before joining (`:145-174`).
- That is the right default for a reader, but it makes the Malagasy type impossible.

**Could it feel like it?** No. The fix is to make the caps a property of the naming tradition, not a global constant.

### 4.5 Yoruba meaningful names

**What makes it distinctive:**
- **Circumstance names:** *Babatunde* ≈ 'father has returned' (a boy born after a grandfather's death); *Ige*, born feet
  first.
- **Theophoric names:** *Olu-*, *Ogun-*, *Ṣango-* + a clause, as in *Oluwaseun* 'God has done it'.
- **Praise names** (*oríkì*).
- Every name is a transparent clause in the language. Naming is a ceremony.

**Coverage: none.**
- `sentences.py` already builds glossed clauses from the lect's own grammar, and GOD and SPIRIT are in every lexicon.
- The faiths work merged into `lang-design` (9e51ac2e) gives named gods.
- A "clause name" is a short sentence (S + V, or 'God gave') compressed by the existing joiner.

**Could it feel like it?** Not today. Of all the traditions this would show the grammar best, because each name is a
mini sentence in the lect.

### 4.6 Germanic dithematic names

**What makes it distinctive:**
- A closed pool of a few dozen **themes** (*wil* 'will', *helm* 'helmet', *sige* 'victory', *frid* 'peace', *gar* 'spear',
  *beraht* 'bright', *ric* 'ruler'), each with a fixed slot (first or second element).
- Themes combine freely, without regard to meaning (*Frið-gar* 'peace-spear').
- Families share a theme or alliterate (Æthel-red, Æthel-stan, Æthel-wulf).
- Over centuries sound change makes the names opaque: *Wilhelm* > *William* > *Bill*; *Hrōþberht* > *Robert*. The same
  type runs through Slavic (*Vladi-mir*, *Bogu-slav*), Greek (*Themisto-kles*), Celtic and Sanskrit, so it is very old.

**Coverage: none.** But this is the tradition that best fits the engine:
- the themes are lexicon words with etymologies;
- the pool is a frozen sub-lexicon carried down the lect tree;
- the existing sound-change pass would make old names opaque while the words they came from move on or are replaced.

A name's `etym` chain could then say "*Wilam*, from *wil* 'will' + *halm* 'helmet', 6 kyr ago". That is the same
Pokorny-style trace the engine already makes for words.

**Could it feel like it?** Not today. If built, it would feel more real than any other tradition, because the
opaqueness is earned and not faked.

### 4.7 Place names

**What makes it distinctive:**
- **Layers.** River names are the oldest layer, and they often mean just 'water' or 'river'. Settlement names are
  younger and built as generic + specific: *-ton*, *-by*, *-ham*, *-ford*, *-grad*, *-burg*. Field and street names are
  younger still.
- **Generics erode into suffixes.**
- **Possessive place names** (*Kraków* 'Krak's (town)').
- **Tautologies** when newcomers add their own generic to an opaque old one (*Pendle Hill*, *River Avon*).

**Coverage:**
- **Rivers and lakes: partial, and good.**
  - The first lect on the water names it, by a population-weighted draw (`names.py:506-538`).
  - An inheriting lect carries the word forward; an unrelated or shifted one keeps it as heard, which is substrate
    (`:554-594`). 291 of 1,237 places (24%) are substrate names.
  - "The river" is the commonest river gloss (113): 30% of river names are a bare RIVER or WATER word (`:546`). That
    matches the real *Avon*/*Don*/*Ouse* pattern.
  - **Missing: the tautology step.** A substrate river name never takes the newcomers' own RIVER word, so there is no
    *River Avon*.
- **Settlements: none.**
  - There is no town name of any kind, although the run has settlements and mixed cities (`names.py:781`).
  - TOWN, VILLAGE, HOUSE, FORD, HILL, VALLEY and FIELD (438 lects) are in the lexicons.
  - The generic-to-suffix erosion would come free from the gram machinery: a TOWN gram on the ladder, as G-paths make
    PLACE from nouns.
- **Land: full.** 'The land of the X' comes from the people set (573 land names). It is like *England* and *Scotland*.
  But 263 of the 573 are 'the land of the real people', because the endonym pattern repeats.
- **Sea, peak: partial.** HEAD + one modifier from a fixed list (`:63-64`: BLACK, WHITE, RED, BIG, LONG, COLD, STONE, GOOD,
  OLD). Real oronyms and hydronyms also come from animals, plants, gods, people and events.
- **Landmasses: outside the language engine.** The names are English-looking syllable strings (`planet/names.py:14-30`).
  No lect says them. Even E7 ("the old people, first on Simath") and the scholars' fallback quote them.

**Could it feel like it?** The river layer, yes: substrate hydronyms are the most convincing names in the output. The
settlement layer, no, because it does not exist.

### 4.8 Ethnonyms, glossonyms, exonyms (the owner's taxonomy)

**What makes it distinctive:**
- A people has a **name stack**: endonym, glossonym, one exonym per neighbour, and a scholars' name if it is extinct.
- Each layer follows a different logic. Names are layered over time by processes P1–P8: conquest, substrate, adoption,
  renaming, splitting.

**Coverage: partial. The mechanisms are good, but the labels drift from the owner's taxonomy.**

**The pattern codes do not match the doc.** `names.py:46-53` uses the same codes as the owner's taxonomy with different
meanings. Anyone who reads `pattern: "E4"` in `languages.json` against the doc gets the wrong pattern.

| Code | Owner's doc (rev 7) | `names.py:46-53` |
|---|---|---|
| E4 | free, noble, high status | 'the river people' (the doc's E6) |
| E6 | land, river or landscape | named after their river (fits E6) |
| E7 | position: border, middle, direction | 'the old people', first settlers (closest to E2 *Lenni-Lenape* 'original people') |
| E9 | physical trait or custom | 'the free' (the doc's E4; marked as needing a FREE concept the lexicon lacks) |
| E10 | faith or covenant | 'described by body' (the doc's E9) |
| E11 | confederation or alliance | 'totem animal' (not in the doc) |
| E12 | adopted exonym, reclaimed insult | 'the many' (closest to the doc's E11, *Alemanni* 'all men') |
| X6 | dynasty or state | 'after a trade good' (no code path) |
| X9 | misattributed origin | 'by land' (cave, mountain, sea, river people: the doc's X7 "dwelling as observed") |
| P5 | rejection and renaming | relay mangling (the doc's X4 relay) |
| P8 | parallel names by audience | scholars' name (unnumbered in the doc) |

**What fires** (a24559):
- Endonyms: E2 12, E1 11, E4 (code) 6, E5 2, E8 2, E3/E7/E10/E11 (code) 1 each.
- Exonyms (1,031): X1 392, X8 209, X9 (code) 179, X7 126, X2 64, X5 37, X3 24.

**Coverage notes:**
- **Never fire:**
  - X4 relay: 0 rows. The path needs `borrowed_from` on a reputation row, and a24559 has none.
  - X6 dynasty: no code path. States now exist in main.
  - X9 misattributed origin.
  - The doc's E4 free (no FREE concept), E10 faith (faiths now exist), E11 confederation (polities now exist) and E12/P3
    adopted exonym.
- **Processes:**
  - Only P2 (substrate on places) is real.
  - P1 (the conquerors' name spreads to the land) is absent, although `shifts` with a ruler deme are in the run.
  - P5 renaming, P6 ethnonym > ordinary word (*slave*, *vandal*) and P7 one root split by borrowing (*Deutsch*/*Dutch*)
    are also absent.
- **Glossonym: partial.** It uses a 'manner' noun class if the lect has one (Bantu *Lu-*), else a 'speech of' compound
  (`grammar.py:2220-2221`). The doc's "glossonym drift" (*nešili* vs *Hatti*), a language name from a different root, never
  happens.
- **The X1 relay is good.** "Their own name *Ṭimungti-i*, as aarakocra ears hear it" gives *Tinotii*. Brass dragons hear
  it as *Hi*. That is the doc's "a good stress test for your language generator" carried out, including *Sioux*-style
  truncation (by repair, not by a deliberate clip).
- **Scholars' names: partial.**
  - One recipe: river or landmass + the Common's 'like' suffix. All 56 dead-family names in a24559 end in *-ba*
    (*the Alingiaba languages*, *the Simathba II languages*).
  - The doc's other bases are not used: type site, artefact, burial, a legend or text, a reconstruction (*Bantu* from
    'person').

**Could a generated people's names feel like a real stack?** The endonym-plus-exonyms stack, yes: it is the most
convincing part of the names output. The time depth (P1, P3, P5, P6), no.

---

## 5. Romanization

### 5.1 What real systems do with the hard parts

| Problem | Real solutions | House/2 does |
|---|---|---|
| **Tone** | pinyin: diacritics (*mā má mǎ mà*) or numbers (*ma1*), usually dropped in running English. Yoruba: acute high, grave low, mid unmarked. Hmong RPA: a final letter per tone (*-b -j -v -s -g -m*, none for mid). Many Bantu orthographies mark only high tone, or none | Full: Yoruba-style on every vowel (`romanize.py:114`). Book: none. In the 237 tonal lects (38%), 3,810 sets of words are book homographs that differ only in tone |
| **Aspiration** | Wade–Giles: apostrophe (*p'*, *ch'*), so *Peking* is misread. pinyin and Korean RR: voiced letters for unaspirated stops where voice does not contrast (*b/p*, *d/t*). Indology: *h* (*kh*, *bh*) | *h* after the letter (`:416`). Any aspirate in the lect turns `"aspiration"` on (`:170`). *sh th kh ch qh dh gh zh* then switch lect-wide to *š þ x č x̣ ð ğ ž*. One contrast changes the whole look of the language |
| **Phonetic or phonemic** | Hepburn: phonetic for readers (*shi*, *chi*, *tsu*). Kunrei: phonemic, consistent per morpheme (*si*, *ti*, *tu*). Spanish writes *b d g* for [β ð ɣ] | Phonetic. The speller sees `lect.segments()` (surface), so an intervocalic allophone [ɣ] of /k/ is written *gh*. 171 lects record allophones (intervocalic 209, nasal vowel 36, final devoicing 29, nasal place 14, palatal 4). In 9 lects an allophone changes the contrast set itself |
| **Digraphs or diacritics** | Polish: digraphs *sz cz rz* plus acute *ś ć ź ń*. Czech: háček *š č ž ř*. English: *sh ch*. Every real orthography follows one model | A patchwork. Digraphs *sh ch zh kh* (English and Arabic transliteration), acute *ś ź ć* (Polish), caron *ť ď ň ľ* (Czech and Slovak), dot below *ṭ ḍ ṇ ṣ* (ISO 15919), *ġ ḥ ʿ* (DIN 31635), *ơ* (Vietnamese), *å æ* (Scandinavian), *ů* (house), *eu eo* (Korean RR). Each choice is sourced. Together they are no one's orthography. 36% of full spellings have two or more letters with diacritics |
| **Doubled letters** | Welsh: *ll* = [ɬ], *dd* = [ð], *rh* = [r̥], *w y* vowels. Finnish and Hungarian: doubling = length | Doubling = length, consistently, except where *ll* or *hh* is taken (`:261`, then *l·l*). *rh* = growl. That is a lucky echo of Welsh voiceless *rh* |
| **Glottal stop** | Hawaiian ʻokina (U+02BB, a letter, written even word-initially: *ʻŌlelo*). Ignored where it is predictable (German) | ASCII `'` (`romanization.tsv:46`). The same sign marks ejectives after a letter (*t'*) and implosives before one (*'b*). The hyphen keeps them apart (*t'a* ejective, *t-'a* t + ʔ; *a'ba* implosive, *a'-ba* ʔ + b). Book drops a word-initial `'` (`:490-491`) |
| **Length** | Hawaiian kahakō macron (*ā*). Finnish doubling. Japanese Hepburn macron | Full: doubled. Book: only the first long vowel of a word is doubled. Later ones are written short (`:486-488`) |
| **Clicks** | Zulu and Xhosa: *c q x* (dental, alveolar, lateral), with *gc nq xh* for the accompaniments. Khoekhoe and Juǀʼhoan: Unicode letters ǀ ǃ ǁ ǂ. Older ethnography: ASCII *!Kung* | ASCII `|`, `||`, `!` with Unicode `ǂ` (`romanization.tsv:129-133`). A long click is `|:` (the colon fallback in `_double_first`, `:274-280`). `title_name` gives *!Xu* (`:502`), the old anglophone convention |
| **"Fantasy" spellings** | Apostrophes as decoration (*Drizz't*), *y* for *i*, silent *h* | Apostrophes are always a real sound (ʔ, ejective, implosive): 6.3% of book words, 7% of names. *y* is always /j/. Non-human marks are the house's own fantasy layer (§5.4) |

### 5.2 Real examples from a24559

Endonyms. Book spelling, then the full spelling, then the IPA:

| people | book | full | IPA | what it shows |
|---|---|---|---|---|
| human | Ṭimungti-i | Ṭi̠mungṭi̠î | ʈi̠˧mu˧ŋʈi̠˧i˦˨ | Book cap: the second ʈ becomes plain *t*. The hyphen marks hiatus. The full form leaks IPA ̠ |
| kenku | Sü yüi | Sǘ yüî | sy˦ jy˧i˦˨ | Tone dropped in book. A two-word name is capitalised once |
| goliath | Aewaeu | Æwǽû | æ˧wæ˦u˦˨ | Book *ae* for æ makes a vowel string hard to parse |
| red dragon | Terhrrrhi | T̪èrhrrrhí | t̪e‼˨r‼i˦ | Growl after a trill gives *rrrh* |
| white dragon | Kurirhsirhlirhk | (same) | kuɾi‼si‼li‼k | Three growl marks in one word |
| blue dragon | T'lyontaarh'a | T'lyònt̪aarh'a | tʼʎɔnt̪a‼ːʔa | Ejective *t'* and ʔ *'* in one word |
| drow (in one lect) | Ne !a!'epx'e | | | Two clicks, an ejective ʘ and an apostrophe |
| bugbear | Leudhida | Lë̠udhida | lɘ̠uðida | IPA ̠ on a house letter in full mode |
| orc | Ṭeu'beb | Ṭèu'bẹ̌b | ʈɯ˨ɓɛ˨˦b | *eu* = ɯ (Korean RR) next to implosive *'b*. A reader sees *Teu-beb* |

Places and scholars' names:
- *Herhsherh-hurhli-irhnyrhirh*, 'the land of the fishers' (white dragon).
- *Ludshirhrrrhe*, 'the white river'.
- *!Aňemafe*, 'the stone mountain' (drow).
- *Lodźazhisi*, 'the red lake' (Polish *dź* beside English *zh*).
- *the Simathba II languages*: an English-looking landmass name + the Common's suffix + a Roman numeral.

Probes run on the current code (`ns/a4.py`):

| IPA | full | book | note |
|---|---|---|---|
| ǀːa (lect has ǀ ǁ) | `|:a` | `|:a` | a colon in a name |
| ǀǀa | `|-|a` | `|-|a` | told apart from ǁ only by a hyphen |
| ãa | ãa | **ana** | same as /ana/ |
| ʈaʈa / taʈa | ṭaṭa / taṭa | **ṭata** / taṭa | one sound, two spellings by position |
| ʃisʰi (aspirating lect) | šishi | **shishi** | ʃ and sʰ merge in book |
| ħiːħeiɖ (from the run) | ḥiirhḥeiḍ | **ḥiirhheid** | the second ħ becomes *h*, merging with /h/ |
| a˦ma˨ | ámà | ama | tone gone |

### 5.3 Does one language keep its conventions across its lexicon?

- **Full mode: yes.** A segment's spelling depends only on the lect's contrast set, so it is the same in every word.
  Exceptions:
  - hyphens, which follow the neighbours (3,420 book words, 1.5%);
  - the surface-allophone issue (§5.1).
- **Book mode: no, by design.** Two word-level rules spell one phoneme differently by position:
  - **One diacritic letter per word** (`_book_cap`, `:338`). In a sample of up to 400 words per lect, at least 1,914
    words spell a repeated phoneme two ways (*ṭata*, *ṣunasu*, *ġoiiġu*). Across lects the cap also merges contrasts:
    ʂ with s, ħ with h, ʈ with t.
  - **One doubled long vowel per word** (`:486-488`). A long-vowel root is spelled long in one word and short in a
    compound where an earlier long vowel came first.
- **Book homographs: 6,266 sets of distinct IPA forms share one book spelling** (about 10 per lect). 3,810 of them
  differ only in tone. The other 2,456 come from the cap, the length rule, nasal vowels and the documented merges.
- No real orthography spells a phoneme by its position in the word. A reader who learns that *ṭ* is retroflex in
  *Ṭimung* will read *t* in *Ṭimungti-i* as a different sound. The intent is good: fewer diacritics per word for a reader
  who must say the name. The mechanism is wrong. A real orthography gets the same effect by choosing, **once per
  language**, which contrasts carry a diacritic and which fold to a digraph or merge (§6).

### 5.4 Clicks, tones, ejectives and non-human sounds

- **Clicks** (1.5% of protos by design; 14 of 2,305 names).
  - ASCII `|` and `!` read as punctuation in a book. `||` is a lateral click but looks like two dental clicks (only a
    hyphen separates them). `ǂ` is Unicode while the others are ASCII.
  - The two real models:
    - **Bantu** *c q x* plus *gc nq xh* for the accompaniments. It suits a lect with a small click set, as in Zulu, which
      borrowed clicks.
    - **Khoisan** ǀ ǃ ǁ ǂ as real letters (U+01C0–01C3, not the ASCII look-alikes), with digraphs for the accompaniments
      (*ǃh*, *ǃʼ*, *ǃg*).
  - The house has no c and no x in most lects. It uses q for uvulars, and x only as an aspiration-mode alternative, so the
    Bantu letters would usually be free.
- **Tones.** Full mode is coherent Yoruba practice:
  - acute high, grave low, mid unmarked, caron rising, circumflex falling;
  - in a tonal lect the marked vowels switch from grave to dot below (*ẹ ọ*) so that a grave never means two things.
    That is a thoughtful touch.
  - Book drops tone entirely, as most English books drop pinyin tones. That is fine for a reader, but it makes 3,810
    homograph sets. A middle way: mark only high tone in book mode (as many African orthographies do), or none in names
    and some in glossaries.
- **Ejectives and glottals.**
  - One apostrophe for three roles is unusual but workable, because the position after vs before a letter decides and a
    hyphen settles the rest.
  - The risk is the reading load: *T'lyontaarh'a*. Americanist and Caucasian practice use the apostrophe for ejectives
    and a separate sign for ʔ (ʔ itself, or ʻ).
  - The ʻokina (U+02BB) is free and is a letter, so `title_name` and word-break logic treat it right.
- **Non-human sounds.**
  - A readable ASCII mark trails the letter: growl *rh*, purr *rr*, second voice *wh*, sub-bass *mh*, ultra *ih*. That
    keeps names sayable, and it is a good idea.
  - But:
    - 26% of all names and 17% of all lexicon words carry the marks;
    - 2,720 words pile them up (*rrrh*, *rhrh*, *rhrr*);
    - purr *rr* equals the trill *rr* (`romanization.tsv:59`), told apart only by a hyphen (*a-rr* vs *arr*);
    - ultra *ih* reads as i + h.
  - The book cap does not cover them, so a dragon name can carry three marks while a human name may keep only one
    diacritic.
- **IPA leakage into the full spelling.**
  - 28,606 full spellings (12.2%, in 415 lects) carry an IPA diacritic: minus below ̠ 16,772, bridge ̪ 11,108, down tack
    ̞ 6,054, plus ̟ 1,525.
  - It comes from the "shifted vowel keeps its mark" rule (`:248-254`) and the dental bridge (`:233`).
  - The book drops them. The workbench orthography does not, so it is half transcription and half spelling. ISO 15919
    already has an answer for the dental/alveolar pair (plain *t* for dental, *ṯ* for alveolar, as in Malayalam).

### 5.5 Do related languages share conventions?

**Yes, by uniformity rather than by history.**
- Across 10,117 sister-lect cognate pairs with identical IPA, 2.4% are spelled differently in full mode and 1.3% in book
  mode. The cause is always a contrast one sister has and the other lacks: *hh/h*, *d̪/d*, *è/e*.
- Across the 265 true families, ʃ has two spellings (*sh/š*) in 3 of 155 families, ɛ (*è/e*) in 5 of 115, and β
  (*bh/v*) in 8 of 48.

But all 265 families use the same house system, so an elvish and a kobold language look like dialects of one
orthography. In reality:
- related languages often share conventions because they share a writing history (Polish *sz* vs Czech *š* for one
  Slavic sound);
- unrelated ones differ for the same reason.

The house system can't show that, because there is one convention for the whole planet.

This is the right choice for a **scholarly transcription**, which is what linguists do. It is the wrong one if book
spellings are meant to give each people a recognisable look. Both can coexist (§6).

---

## 6. Cross-cutting gaps

### 6.1 Missing entirely

1. **Personal names.** No given names, bynames, surnames, patronymics, epithets, theophoric or clause names, and no name
   order. Every tradition in §4.1–4.6 is "none". This is the largest gap: names of people are what a reader meets most,
   and what an adventure or a cookbook needs (PW-911, and the culinary end goal: who cooks, who the dish is named for).
2. **Settlement names.** None, although the lexicons hold TOWN, VILLAGE, FORD, HILL, VALLEY and HOUSE.
3. **Names as lexicon entries that age.** Names are re-made from today's words at output time (endonyms, places), except
   river and lake names, which do have a substrate history. A real name is coined once and then evolves. It goes opaque
   while its source word moves on or is replaced (*Wilhelm*, *-ton*, *Avon*). The engine's best feature, etymology
   through sound change, is barely used for names.
4. **Orthographic traditions.** One house system for every language. There is no per-family profile, no inheritance of
   spelling habits, and no spelling reform.
5. **Orthographic depth.** Spellings never lag behind sound change (English, French, Irish, Tibetan). Every spelling is
   a fresh transcription.
6. **Name-change processes over time.** P1 conquerors' name, P3/E12 adopted exonym, P5 renaming, P6 ethnonym > word, P7
   split by borrowing, and glossonym drift.
7. **Tautological and hybrid place names** (*River Avon*, *Pendle Hill*).

### 6.2 Modelled too thinly

- **Ethnonym pattern codes** no longer match the owner's taxonomy (§4.8). Several patterns the doc lists are missing
  (E4 free, E10 faith, E11 confederation, X6 dynasty, X9 misattribution), although the run now has faiths and polities.
- **Place modifiers** come from a 6–9-word list, so the glosses repeat: 'the old river' 48, 'the old mountain' 40, 'the
  black mountain' 36.
- **Scholars' names** follow one recipe and one suffix.
- **Landmass names** come from an English-looking generator outside the language engine (`planet/names.py:14-30`), so a
  landmass name never sounds like the peoples on it.
- **Multi-word names** capitalise only the first word (`names.py:128-129`): *Hili kangrhighirh*, *Opa'i e*. Real practice
  capitalises each element (*Kel Tamasheq*, *Banu Hashim*) or hyphenates a clitic particle (*al-*). 14% of names are
  multi-word, and many end in a one-letter particle (*Opa'i e*, *E iva*).

### 6.3 Exists, but the rule is wrong for a reader or a linguist

| Issue | Measure (a24559, current code) | Cause in code |
|---|---|---|
| Book spells one phoneme two ways in one lect | ≥1,914 words in the sample; ʂ/s, ħ/h, ʈ/t merged | `_book_cap` (`romanize.py:338`); one doubled vowel (`:486-488`) |
| Book homographs | 6,266 sets (3,810 tone-only) | no tone in book; cap; nasal vowel = V + *n* (*ãa* = *ana*) |
| One aspirate flips the whole lect's fricative spellings | 1 contrast name decides *sh/š*, *th/þ*, *kh/x* | `contrasts_of` (`:170-171`) |
| Allophones spelled; allophones change the contrast set | 171 lects with allophones; 9 contrast sets changed | Speller uses surface `lect.segments()` (`output.py:26`, `names.py:107`, `lect.py:482`) |
| IPA marks in the full orthography | 12.2% of full spellings | `:233`, `:248-254`, `:255` (the IPA fallback) |
| Non-human mark pile-ups and a purr/trill clash | 2,720 words; *rr* = both | `_NH_PHONATION` (`:263`); `romanization.tsv:59` |
| Long click | `|:` | `_double_first` falls back to `:` (`:280`) |
| Mixed source conventions inside one lect | 36% of full spellings have 2+ diacritic letters from several traditions | `romanization.tsv`: each row picks its own source |
| ř for the approximant ɹ | Czech ř is a raised trill, the opposite of an approximant | `romanization.tsv:111` (book uses *r*, so this is a workbench-only issue) |

---

## 7. Ranked recommendations

**Status (names & spelling lane, 2026-11-08; architecture.md sections 12, 13b; commits on `lang-names`):**
- [x] 1 codes realigned with the doc (rev 7); the generator's label is the new `variant` field
- [x] 2 one book spelling per phoneme per lect (`book_folds`, budget 2); every long vowel doubled
- [x] 3 phonemes, not allophones (`romanize.Orthography`)
- [x] 4 no IPA marks in full spellings (test over the whole percept space)
- [x] 5 non-human marks: once per run in book, rrh for a growled r, purr `vr` (letters are Daniel's call: `NH_MARKS`)
- [x] 6 clicks as ǀ ǁ ǃ ǂ, long click doubled (no Bantu c q x option yet)
- [x] 7 pinyin b/p for aspiration-only lects
- [x] 8 personal names v0: traditions inherited down the tree (dithematic, phrase, single; patronymic, matronymic,
  epithet, clan); 3 old + 3 new given names and 2 bynames per living lect with etymologies (`personal.py`)
- [~] 9 names age: old names carry the lect's reflexes of their themes, a replaced theme stays as a fossil, and old names
  wear down; not yet replayed through each lect's own sound changes
- [x] 10 settlement names (generic + specific, generic worn to a suffix, Kraków-style genitive founders)
- [x] 11 tautologies for substrate settlement names (not yet for rivers and peaks)
- [ ] 12, 13 orthographic profiles and depth; [ ] 14 name length by tradition; [ ] 16, 18, 19, 20
- [~] 15 E4 'masters' and E10 faith now fire; E11 confederation and X6 dynasty wait for polity/state data in the run;
  X9, P1, P3, P5-P7 not started
- [x] 17 multi-word names capitalized, short particles hyphenated

Value is how much more real-looking or readable the names and spellings get (H/M/L). Cost: S = under a day; M = a few
days; L = a week or more, or an architecture change. **Before merge** means cheap, fixing something the pages already
claim or show. **Later** means new capability.

| # | Recommendation | Value | Cost | When |
|---|---|---|---|---|
| 1 | **Realign the pattern codes with the owner's taxonomy** (`names.py:46-53`, and the `pattern` fields in `languages.json` and the sketches). Use the doc's numbers. File the code's extras ('totem animal', 'after a trade good', 'by land') as new codes or under their nearest doc pattern (E9, X7). Call the scholars' name `scholarly`, not P8, and the relay X4, not P5. | H (correctness) | S | Before merge |
| 2 | **One spelling per phoneme per lect in book mode.** Replace the per-word diacritic cap and the once-per-word doubled vowel with a **per-lect** budget. Rank the lect's marked letters by functional load. Keep the top one or two as diacritics. Fold the rest once, for the whole lexicon (ʈ = *t* everywhere if it folds), and record the fold on the orthography line. Write length the same way in every word (doubled, or a macron counted in the budget). | H | S | Before merge |
| 3 | **Spell phonemes, not allophones.** Build the speller's segment set and contrasts from the phonemic inventory (`inventory.consonants/vowels`, not `lect.segments()`), and spell an allophone with its phoneme's letters (Kunrei, Spanish *b d g*). The IPA keeps the phonetics. | M–H | S | Before merge |
| 4 | **Stop IPA marks leaking into the full spelling.** Fold a shifted vowel to its house letter unless it contrasts with the unshifted one. Use ISO 15919's *t/ṯ* pair for dental vs alveolar instead of the bridge. Give the IPA fallback (`:255`) a test that fails on any IPA-only character in a spelling. | M | S | Before merge |
| 5 | **Non-human marks: cap and disambiguate.** In book mode, write a non-human mark at most once per syllable, or once per word on the stressed syllable, as the diacritic cap does. Give purr a spelling that is not the trill's *rr*. Check the *rrrh* class with a test. The choice of letters is a taste call: offer Daniel two or three options as a `needs-decision`. | M | S | Before merge (decision) |
| 6 | **Clicks as letters.** Use ǀ ǃ ǁ ǂ (U+01C0–01C3), not ASCII `| ! ||`, fix the long click (`|:`), and keep `title_name`'s *!Xu* rule. Optionally give Bantu-style *c q x* to lects whose clicks are few or borrowed, which links to #10. | M | S | Before merge |
| 7 | **The pinyin trick for aspiration.** When a lect contrasts aspiration but not voicing, write the plain stops *b d g* and the aspirates *p t k*, as pinyin and Korean RR do. The fricative digraphs then stay *sh th kh*, and one contrast no longer flips the lect's whole look. | M | S | Before merge |
| 8 | **Personal names v0: naming traditions.** Draw a naming tradition per proto, inherited and drifting along the lect tree like typology: name order; given-name source (dithematic themes / clause names / single meaningful words); byname (patronymic from GEN + SON/DAUGHTER, nisba from the 'like' affix, kunya, epithet, clan *Banu X*); family name (none, or a frozen surname pool from places and clans); length cap (#14). Make 10–20 sample names per people for the brief and the sketch. | H | M | Later (first) |
| 9 | **Names as aging lexicon entries.** Coin dithematic themes, surnames, settlement generics and landmass names once, store them with `etym`, and run them through sound change with the words. Old names then go opaque, as *Wilhelm* did, and a name's history shows in the workbench trace. Rivers already do half of this. | H | M | Later (with 8) |
| 10 | **Settlement names.** Generic (TOWN, VILLAGE, HOUSE, FORD, HILL, FIELD) + specific (founder's name from #8, people, river, a feature), in head order. The generic can grammaticalize into a place suffix (*-ton*, *-by*, *-grad*). Possessive names come from GEN (*Kraków*). Name the run's settlements and mixed cities. | H | S–M | Later (first) |
| 11 | **Tautological substrate names.** When a lect inherits a substrate river or peak name, sometimes compound it with its own RIVER or MOUNTAIN word (*River Avon*, *Pendle Hill*). Raise the chance when the old name's head word is no longer recognisable. | M | S | Before merge if cheap |
| 12 | **Orthographic profiles per family (romanization only, not scripts).** Separate the scholarly house transcription (keep it as the workbench spelling) from a per-language **book profile** drawn at the proto and inherited, with occasional reforms. The profile chooses: digraphs or diacritics; ʃ as *sh/sz/š/x/sch*; /j/ as *y/j*; length as double or macron; ejectives as ' or dot; tone as none, high-only, full or RPA letters; clicks as Bantu or Khoisan letters. Related languages then share a look and unrelated ones differ. Keep the merges and MERGES list as the engine's guarantee. Check the boundary with Daniel's writing-systems project first: this is choosing Latin letters, not designing a script. | H | M–L | Later |
| 13 | **Orthographic depth.** Freeze a lect's book spelling at a "standardisation" date (a polity's founding, or the Common's spread). Later spellings follow sound change only through the frozen forms, giving *knight*-type silent letters and French-type endings, labelled as historical spelling. | M (very distinctive) | M | Later (after 12) |
| 14 | **Name length by tradition.** Move `MAX_SYLL` and the part clip (`names.py:42`, `:145-154`) into the naming tradition, so a Malagasy-type people can have 8–10-syllable names and a Chinese-type people 1–2-syllable ones. | M | S | Later (with 8) |
| 15 | **The missing taxonomy patterns and processes.** E4 free (add FREE), E10 faith (from faiths), E11 confederation (from polities), X6 dynasty or state (from states), X9 misattributed origin (a neighbour's name for the wrong people), P1 conquerors' name (the `shifts` with a ruler deme), P3/E12 adopted exonym, P6 ethnonym > word, P7 split by borrowing. Find out why X4 relay never fires (no `borrowed_from` in a24559). | M | M | Later |
| 16 | **Glossonym drift.** Sometimes name the language from a different root: a place (Hittite *nešili* 'of Neša'), 'our speech', or a manner adverb (*Euskara*). | L–M | S | Later |
| 17 | **Book capitalisation and particles.** Capitalise each content word of a multi-word name. Attach a one-syllable people particle with a hyphen or close it up, as *al-*, *Kel*, *Banu* do, so there is no *Opa'i e*. | L–M | S | Before merge |
| 18 | **Landmass names from the languages.** When languages exist, name each landmass in the lect of its first settlers (taxonomy E7, P2) or in the Common, falling back to `planet/names.py`. Daniel's own names (PW-867) must still win. | M | S–M | Later |
| 19 | **Scholars' names with more bases.** Type site (a place name from #10), a reconstructed word ('person', as *Bantu*), a two-extremes compound for big families (*Indo-European*), and *Proto-*. | L | S | Later |
| 20 | **Dish and food names** (the culinary end goal). Eponyms (a cook or ruler from #8), toponyms through the nisba or 'like' affix ('the Ratal-ish stew'), and exonyms for foreign dishes along `food_routes`. | M (for PW-692) | M | Later |

**Before the first merge**, items 1–7 and 17 are each S:
- 1 fixes a silent mislabelling of every name's pattern against Daniel's own doc;
- 2 and 3 make one language spell one phoneme one way, which is the basic contract of any orthography;
- 4–7 remove the visible oddities: IPA marks, *rrrh*, `|:`, and the lect-wide *š* flip.

Personal names (8–10, 14) are the largest gain in real-looking output. They are new capability, so they come after the
merge. Name ageing (9) is what will make them feel real rather than random.

---

## 8. Caveats

- Full spellings come from the run (4 November code). Book spellings were recomputed with today's code, so the two can
  differ where `romanization.tsv` changed after 11-04.
- a24559 predates round 5 (coda dark-ɫ and other allophones, the WOLD vocabulary). The allophone count (171 lects) is a
  floor. Once dark ɫ allophones exist, the surface speller would write *ll* for coda /l/ in lects with clear /l/. A
  Welsh reader would take that as [ɬ].
- The "≥1,914 words" book-cap figure is from the first 400 words of each lect only.
- Real-world figures are from general knowledge. The Chinese surname share (≈20% for the top three) and name lengths
  are approximate. Some etymologies are contested: *Avon* < *abona* is standard; *Torpenhow Hill* is often cited but
  partly folk etymology, so I used *Pendle Hill* instead. Per the doc's own note, the taxonomy's etymologies are not
  source-checked.
- I did not read Daniel's writing-systems repo (out of scope by instruction). Recommendation 12 is about Latin
  romanization only.
