---
name: language-finder
description: Use when Daniel asks to find, pick or compare languages in a run by sound or features, in loose words ("something like Sindarin", "Japanese-ish with strict CV", "the most English-like one", "where's my fantasy Hawaiian", "a harsh guttural dwarvish language", "anything with clicks and tones"). Turns the description into tools/language/find.py calls over runs/<run>/languages.json and presents the top candidates with sample words.
---

# Language finder

`tools/language/find.py` reads one run's `languages.json` (main file only, ~2-3 s on a24559, nothing cached or written) and
either filters the living lects by features or ranks them by likeness to a reference profile.

    uv run python tools/language/find.py runs/<run>/languages.json --like sindarin [--people elves] [--explain] [--top 8]
    uv run python tools/language/find.py runs/<run>/languages.json --where "syllables=CV" --where "consonants<=10" \
        --where "tones>=2" --order VSO --sort final_vowel_share
    uv run python tools/language/find.py --list-profiles        # profiles, their numbers and sources
    uv run python tools/language/find.py runs/<run>/languages.json --features   # every key with an example

- Reference run: a24559. Never write into `runs/`.
- `--where KEY OP VALUE` (OP `= != < <= > >= ~`; `a|b` alternatives; bare `KEY` = present, `!KEY` = absent). Filters
  combine with `--like`: filter first, then rank.
- `--people` takes plurals and groups: `elves` (elf, drow, sea elf), `dragons` (every kind), `giants`, `dwarves`.
- `--sort KEY` is descending, `KEY:asc` ascending; without `--like` or `--sort` hits come by speakers.
- Profiles: hawaiian japanese english finnish arabic mandarin georgian welsh sindarin quenya spanish swahili zulu
  turkish klingon black_speech. Data: `tools/language/data/reference_profiles.tsv` (features, sources) and
  `reference_words.tsv` (word lists for sound texture; English comes from `sketch.py`).

## Turning a description into calls

1. Pick a profile if the description names or implies a language, plus filters for any hard constraint he states
   ("strict CV" is a filter, "Japanese-ish" is a profile).
2. Run two or three variants: the profile alone; the profile with his constraint or people; a pure-filter run sorted on the
   feature he cares most about. Add `--explain` when the ranking looks odd.
3. Show Daniel the top 3-5 across the variants: id, endonym, people, place, the one-line summary and the sample words
   (spelling and IPA). He judges the sound by eye; say which variant found each.
4. Distance guide: under ~2 is a close match, 2-3.5 a fair one, above ~3.5 means nothing in the run is really like it.
   Say so plainly rather than oversell, and name what is missing (the `why:` line).

| Description word | Profile(s) | Filters |
| --- | --- | --- |
| Elvish, Tolkien-ish | sindarin, quenya | `--people elves` as a second variant |
| Sindarin-like, Welsh-ish, Celtic | sindarin, welsh | `interdental`, `lateral_obstruent`, `final_vowel_share<=0.4` |
| Quenya-like, Latinate, Finnish-ish | quenya, finnish, spanish | `final_vowel_share>=0.6`, `max_onset<=1` |
| Polynesian, Hawaiian, island | hawaiian | `syllables=CV`, `consonants<=12` |
| Japanese-ish, moraic | japanese | `syllables=CV\|CVC`, `final_vowel_share>=0.85`, `tones=0` |
| liquid, flowing, soft, melodic | quenya, hawaiian | `final_vowel_share>=0.6`, `cluster_share<=0.3`, `!ejectives`, `!uvular` |
| harsh, guttural, throaty | arabic, georgian, klingon | `uvular`, `pharyngeal`, `ejectives`, `final_vowel_share<=0.4` |
| orcish, dark, menacing | black_speech, klingon | `max_coda>=2`, `final_vowel_share<=0.4` |
| clipped, consonant-heavy, clusters | english, georgian | `syllables=CCVCC\|CVCC`, `cluster_share>=0.4`, `mean_syllables<=1.5` |
| English-like | english (same reference as `sketch.py --english-top`) | `stress=initial`, `word_order=SVO` |
| tonal, sing-song | mandarin | `tones>=2` (`tones>=4` for Chinese-like) |
| clicks, Bantu, southern African | zulu, swahili | `clicks`; `syllables=CV` |
| Semitic, desert | arabic | `pharyngeal`, `uvular`, `word_order=VSO` |
| Turkic, vowel harmony feel | turkish, finnish | `front_rounded`, `word_order=SOV`, `case=many` |
| nasal, French-ish | (none) | `nasal_vowels`, `front_rounded` |
| lisping, "th" | sindarin, english | `interdental` |
| long words / short words | (none) | `mean_syllables>=2.5` / `mean_syllables<=1.5` |
| tiny / huge sound system | (none) | `consonants<=10` / `consonants>=30` |
| verb-first | welsh, hawaiian, arabic | `--order VSO` (or `VOS`) |
| inhuman, draconic | (none) | `--people dragons`, `nonhuman>=1`; `nonhuman=0` for human-sounding |
| big, widely spoken | (none) | `--sort population` |

Other keys (see `--features`): `stress` (initial penult final weight none), `case` (none few many), `adposition`,
`alignment`, `synthesis` (0-3, mean grammatical-marker level: low = isolating), every typology field, `family`,
`language`, `people`, `place` (`place~Simath`). Series flags: clicks ejectives implosives retroflex uvular pharyngeal
labial_velar front_rounded nasal_vowels interdental aspirated long_vowels lateral_obstruent.

If a description keeps coming up with no good profile, add one: a row in `reference_profiles.tsv` (cite sources) and
~50 everyday words in `reference_words.tsv`, then `uv run pytest -q tests/test_language_find.py`.
