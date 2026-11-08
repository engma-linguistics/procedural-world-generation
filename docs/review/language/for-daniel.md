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
