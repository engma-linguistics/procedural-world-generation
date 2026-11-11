# How the languages work

*Last updated 2026-11-11. [Back to Languages](index.md).*

1. **Start.** 20,000 years ago, each group of connected local populations ("demes") of a people gets one proto-language. Peoples that arrive later get theirs when they arrive. A proto-language's sounds, word shapes and grammar are drawn from real-language statistics (PHOIBLE, WALS, Grambank). Each species' voice decides which sounds it can make and hear.
2. **Every half-millennium**, each living variety changes:
   - its sounds change, through a catalogue of about 245 sound changes, each with a physical cause;
   - words are replaced; frequent ones hold out longest;
   - new words are made by derivation and compounding, and meanings drift;
   - grammar wears down and renews (a "going to" becomes a future tense).
3. **Peoples split, so languages split.** Neighbours borrow words and sound changes from each other. What gets borrowed depends on the contact:
   - rulers give status words;
   - traders give goods words and big numbers;
   - conquest leaves cow ~ beef pairs.
4. **Peoples shift language** under rule or swamping, and keep an accent and some old words.
5. **At the end:**
   - Varieties are grouped into languages and families. A simulated comparative method builds a "scholars' tree" that can be wrong.
   - Names are built from each language's own words: peoples, places, rivers, gods and persons, plus the Common's English names.
   - Sentences, a fable, recipes and spellings are generated, and the checks run.

Everything is deterministic from the run seed.

---

## For agents

### Module map (`planet/language/`, ~29k lines)
| Module | Owns |
|---|---|
| `percepts.py` | `Segment` as heard (ordinal axes shared by all species), distance, symbol table `data/symbols.tsv` |
| `profiles.py` | species voice profiles (`data/voice_profiles.toml`), inherited along the lineage tree; nativization |
| `inventory.py` | proto inventory draw (PHOIBLE-weighted, feature economy), phonotactics, word shapes (`draw_word`, `retemplate`), word-initial priors |
| `rules.py` | `Rule`, catalogue from `data/sound_changes.tsv` (S001–S245), weighting, functional-load veto, re-fire cap |
| `phonology.py` | synchronic rule layer: live rules per lect, life cycle, application to new words and joins |
| `lexicon.py` | concepts (`data/concepts.tsv`, ~590 rows, 969 concepts incl. food/landscape/kin/gods), `Word` + `EtymStep` chain, replacement by frequency class, derivation, compounding, CLICS colexification shift, borrowing, taboo |
| `lexsys.py` | lexical systems built whole: numerals by base (WALS 131A), colour terms by Berlin & Kay stage, sound symbolism |
| `contact.py` | borrowing by contact kind (`elite`, `trade`, `conquest`, `flat`); field profiles; `TRADE_NUMERALS` |
| `grammar.py` | ~40 typology features drawn conditionally (WALS/Grambank), grams on grammaticalization paths, paradigms, complexity |
| `lect.py` | `Lect`: inventory + lexicon + grammar + rule history + rate; `step` per frame interval; `diffusion_reach` |
| `history.py` | the driver: protos, births (bud/arrival), steps, wave spread, shift + substrate, areal, koine, food routes; `RULE_WEIGHT` overrides |
| `inputs.py` | the engine's read of a stored peoples run (`Run`); derives contact/rule/trade that the run does not store at deme level |
| `families.py` | true tree, language clustering, scholars' tree (automatic comparative method), horizon, continua, intelligibility |
| `names.py` | name stacks (endonym/exonym/glossonym, ethnonym patterns E/X/P), place and river names, the Common |
| `placenames.py` | per-family naming habits (six templates), the Common's English renderings |
| `personal.py` | naming traditions, personal names, settlement names and founding (`founding`, `_founder_lect`, `_holders_chain`) |
| `faiths.py` | god names as lexicon entries, liturgical registers, learned loans (reads the run's `gods.json`) |
| `sentences.py` / `texts.py` | grammar notes, glossed sentences; the fable (Schleicher-style) and recipes; draw nothing |
| `romanize.py` | house spelling "house/2" and per-lect book spellings; slur guard `data/offensive_substrings.txt` |
| `speak.py` | IPA to WAV (eSpeak backend for demos) |
| `checks.py` | 17 checks, `run_all(result)` |
| `output.py` / `run.py` | `languages.json` + sidecars; CLI `planet languages` |

Viewer: `viewer/languages.html` + `lang*.js` (tabs: Families, A language over time, Continuum & intelligibility, Names & etymologies, Food words & shifts, Checks & voices, Grammar & sentences). Server `planet/langserve.py`. Detail: `docs/review/language/viewer.md`.

### Reference data (`planet/language/data/`, built by `tools/language/build_reference_tables.py`; provenance in `docs/review/language/reference-data.md`)
| Table | Source |
|---|---|
| `phoible_*.tsv` | PHOIBLE |
| `wals_wordorder.tsv` | WALS |
| `grambank_*.tsv` | Grambank |
| `clics_edges.tsv` | CLICS |
| `borrowability.tsv` | WOLD |
| `word_initial.tsv` | NorthEuraLex 0.9 (CC-BY 4.0) |
| `token_frequency.tsv` | token frequency priors; Eurasian sample, see PW-1648 |
| `grammaticalization_paths.tsv` | Kuteva et al.-style paths |
| `sound_changes.tsv` | the catalogue, hand-built with causes |
| `compounds.tsv`, `derivations.tsv`, `splits.tsv` | hand-built word-making tables |
| `romanization.tsv`, `symbols.tsv`, `ipa_to_speech.tsv` | hand-built symbol tables |

Raw downloads go in `data/language/raw/`, which is git-ignored and untrusted.

### Output (`runs/<id>/`)
`languages.json` top-level keys:
- `lects`: the full lexicon for living lects; the Swadesh-100 and names for dead ones;
- `names`, `shifts`, `food_routes`, `faiths`, `families`, `intelligibility`, `continua`, `fable_splits`, `checks`, `landscape`, `rules`, `profiles`, `timing` and `constants`.

Sidecars:
- `languages-etym.json`: full etymologies;
- `languages-snapshots.json`: 100 core concepts per frame.

`meta.languages` is written in place. Lect ids are stable from birth to now, and a Lect holds its *final* lexicon. Per-frame history lives only in snapshots (core concepts), and this is why place names are currently coined from present-day words (PW-1685).

### Mechanics worth knowing before changing anything
- **Batching.** Time steps in 0.5-kyr frames, 41 of them. The per-generation hazards are batched per interval (architecture §8), never looped.
- **Rule weights.** These come from the catalogue, times `history.RULE_WEIGHT` overrides (S148 0.3, S042, S073), times a re-fire cap. PW-1692 found the cap saturates for common rules; lane 17 is fixing that, and the overrides should then be removed.
- **Borrowing.** Loans follow WOLD borrowability, then a contact-kind multiplier (`contact.py`). Pronoun loans have a hard check cap of 0.08.
- **Phonotactic veto.** A sound change that would create a syllable the lect forbids is vetoed per draw (PW-1622). CV languages are protected by `retemplate`.
- **Determinism.** Every draw is seeded with `seed_for(run_seed, "lect", id)`, so `--workers` does not change the output (byte-identical).
- **Speed.** About 10–11 min at 8 workers. Most of it is `steps`, about 300 s of CPU, then `wave`. `planet make` runs the pass; `--no-languages` skips it.
- **Tests.** There are 24 `tests/test_language_*.py` files plus the viewer test, and goldens in `tests/golden/`. Lane worktrees show about 16 extra skips because of the data layout; the merged suite is the real count.
