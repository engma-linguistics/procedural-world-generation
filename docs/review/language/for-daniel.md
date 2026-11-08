# For Daniel: choices and leftovers from the language lanes

Short and plain. Each choice is one constant or table row; change it there.

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

## Leftovers
- Names are not run through each language's own sound-change history; old names are approximated (see
  architecture.md section 13b).
- The language pages (sketch.py) are Markdown, so the names there have no play buttons; the viewer's Names tab has them.
  The finish lane's demo page could add them with its `play()` helper.
- E11 confederation and X6 dynasty/state names need polity or state data that does not reach the language pass yet.
  X9, P1, P3, P5-P7, glossonym drift, name length by tradition, river/peak tautologies, orthographic profiles: not started.
- Bilabial click ʘ is still spelled `px`.
