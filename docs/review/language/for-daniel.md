# For Daniel (set aside overnight, 2026-11-07 → 11-08)

Everything here has a working default in the code already. Nothing is blocked; change any of them in one place.

## Decisions (defaults taken)
1. **Synthesis level** (how affix-heavy languages are): the measurement against WALS 22A comes from grammar A. Default: unchanged until you rule.
2. **Species leanings in grammar** (like kenku → tone): the lane's guessed table, marked as guesses.
3. **Letters for non-human sounds** in book spellings (the purr vs trill rr): names lane's guess.
4. **Merger veto / homophony; spread of change rates between lects:** current settings kept.
5. **After a shift: how long minority speech lives, L2 share levels, how much dialect continuity:** current settings kept, with the reviews' numbers alongside.
6. **A shifting people keeps the old language's sounds, or reshapes them by its own voice:** current behaviour (keeps them) kept.

## Weirdness noticed
- **The demo page has glitches** (a full read before publishing found them). Merchants are glossed as things in two languages, a dual marker is described but missing from its example, one note quotes the wrong verb, and some agent jargon shows. None is in the data model's core. All are queued as the first item of grammar B in queue.md.
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
