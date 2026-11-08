# Language reference data

Reference tables for the language-generation engine, gathered 2026-11-03. The derived tables live in `planet/language/data/` and are small enough to commit (about 500 KB together). The raw downloads are in `data/language/raw/<source>/`, which is git-ignored and sits in the owner's data dir. Two scripts rebuild everything:

- `uv run python -I tools/language/build_reference_tables.py` reads the downloads and writes the seven tables derived from data, in about 3 s.
- `uv run python -I tools/language/knowledge_tables.py` writes the two tables I wrote from knowledge (no download behind them).

Every TSV starts with `#` comment lines giving the source, version, licence, script and derivation notes, then one header row. Loaders must skip lines that start with `#` (for example `pandas.read_csv(sep="\t", comment="#")`, or `csv` after filtering).

The network worked and every source downloaded. Only the two tables flagged below came from knowledge.

| Table | Rows | From |
|---|---|---|
| `phoible_segments.tsv` | 649 | download |
| `phoible_inventory_sizes.tsv` | 224 | download |
| `grambank_features.tsv` | 398 (195 features) | download |
| `grambank_correlations.tsv` | 388 (45 feature pairs) | download |
| `wals_wordorder.tsv` | 207 | download |
| `clics_edges.tsv` | 4228 | download |
| `concepts.tsv` | 579 | download (3 classes from knowledge; the WOLD pick by hand) |
| `grammaticalization_paths.tsv` | 72 | **knowledge** |
| `sound_changes.tsv` | 214 | **knowledge** |

## PHOIBLE: `phoible_segments.tsv`, `phoible_inventory_sizes.tsv`

- **Opened:** https://raw.githubusercontent.com/phoible/dev/master/data/phoible.csv (repo `phoible/dev`, commit 5f82b9c3, 2026-09-24). This is PHOIBLE 2.0 plus later fixes from the dev branch, not the frozen 2.0 Zenodo release. Counts can differ from published 2.0 figures by a few inventories.
- **Licence:** CC-BY-SA 3.0. The derived tables are share-alike too, so anything that ships them has to carry the same licence and attribution (Moran & McCloy eds. 2019).
- **Derived:**
  - **Deduplication:** 3020 inventories became one per Glottocode, keeping the lowest InventoryID (the first listed). That leaves n = 2175. One inventory without a Glottocode was dropped.
  - **Frequency:** the fraction of those 2175 inventories that contain the segment. Marginal phonemes count as present.
  - **Tail:** segments in fewer than 0.2% of inventories (fewer than 5) are left out. That is 1925 segments (1241 consonants, 657 vowels, 27 tones), 2825 occurrences in total, and the header records it as the "other" bucket.
  - **Features:** the 37 PHOIBLE feature columns, copied verbatim from each segment's first occurrence.
  - **Sizes:** distinct phonemes per inventory, split into consonants, vowels, tones and total. For each the table gives a count per size plus mean, median, quartiles, minimum and maximum.
- **Caveats:**
  - PHOIBLE vowels are distinct vowel phonemes, so long and nasal vowels count separately: the median is 9, mean 10.1. That is not WALS 2A's vowel-quality count (median about 5). Consonants: median 21, mean 23.7. Total: median 32.
  - "First inventory per Glottocode" is arbitrary. Each source in PHOIBLE (SPA, UPSID, AA, ...) has its own analysis style.
  - Frequencies are raw over languages, not family-balanced.

## Grambank: `grambank_features.tsv`, `grambank_correlations.tsv`

- **Opened:** https://raw.githubusercontent.com/grambank/grambank/v1.0.3/cldf/ (`parameters.csv`, `codes.csv`, `languages.csv`, `values.csv`). Grambank v1.0.3 is the latest tag and the same dataset as v1.0 with fixes (Zenodo doi:10.5281/zenodo.7740139).
- **Licence:** CC-BY 4.0 (Skirgård et al. 2023, *Science Advances* 9).
- **Derived, features:**
  - **Languages:** 2467 languoids became 2426, one per `Language_level_ID`, preferring the "language" row over dialects. Family rows were dropped.
  - **Columns:** for every feature and value, the short name (from `Grambank_ID_desc`), the question, the value coding, `n_coded` (`?` excluded), `n_unknown`, the count and the raw frequency.
  - **`freq_family_weighted`:** each top-level family, with each isolate counted as its own family, gets total weight 1, split over its coded languages. Use this column for genealogically balanced draws. It moves some features a lot: verb-final order is 0.43 raw but 0.67 family-weighted.
- **Derived, correlations:**
  - **Features:** 52 structural features: word order, adpositions, possessor-noun, adjective-noun, relative clauses, articles, case, alignment, gender, classifiers, number, TAM, argument indexing, affixation and incorporation.
  - **Pair filter:** for each pair coded together in at least 100 languages, I computed Cramér's V and kept pairs with V ≥ 0.40. That is 45 of 1326 pairs. Rerun with `--gb-vmin 0.3` to get about 100 pairs and about 940 rows.
  - **Rows:** each kept pair appears in both directions with the full conditional distribution P(f2=v2 | f1=v1), plus the marginal and the lift. A generator can therefore draw feature by feature.
  - **What the strongest pairs show:**
    - The Dryer harmonies: prepositions against verb-final order (V 0.70), postpositions with verb-final order (0.61), possessor-noun order with prepositions (0.57), and relative clause before the noun with verb-final order (0.49).
    - Agreement families: adjective gender with demonstrative gender (0.76).
    - Case with accusative alignment.
- **Caveats:**
  - Correlations use raw language counts, not family-balanced, so Austronesian and Atlantic-Congo inflate some pairs.
  - Some kept pairs are near-definitional, for example S-prefix with A-prefix, or the three verb-position features with each other.
  - Adjective-noun order (GB193) correlates only weakly with OV/VO, as Dryer 1992 found, so it falls under the cut. That is a real result, not a bug.

## WALS: `wals_wordorder.tsv`

- **Opened:** https://raw.githubusercontent.com/cldf-datasets/wals/master/cldf/ (commit 81298aa2, 2026-09-28; WALS Online v2020.x).
- **Licence:** CC-BY 4.0 (Dryer & Haspelmath eds. 2013).
- **Derived:**
  - **Value frequencies** for 81A, 85A, 86A, 87A, 88A and 90A (`table=freq`). Example: 81A has n = 1376, with SOV at 0.41 and SVO at 0.35.
  - **Cross-tabs** of 81A against each of the other five (`table=crosstab`), with `fraction` = P(value2 | 81A value). The brief asked for 85A and 86A; the other three are only about 150 extra rows, so I included them.
  - **Spot check:** SOV gives postpositions 0.92; SVO, VSO and VOS give prepositions 0.82 to 0.91.
- **Caveat:** counts are raw over languages. Dryer's published figures balance by genus.

## CLICS3: `clics_edges.tsv`

- **Opened:** https://github.com/clics/clics3/raw/master/clics3-network.gml.zip (repo `clics/clics3`, commit 19b4051f, 2023-05-10). I extracted it to `data/language/raw/clics3/extract/graphs/network-3-families.gml` and parsed it with a small line-based GML reader in the build script (no networkx).
- **Licence:** CC-BY 4.0 (Rzymski, Tresoldi et al. 2020, *Scientific Data* 7:13).
- **Derived:** every edge with FamilyWeight ≥ 3. The published network is already cut at 3 families, so all 4228 edges over 2919 concepts are kept. Each edge gives both Concepticon ids and glosses, the family, language and word weights, and both semantic fields, sorted by family count. The top edges are TREE–WOOD (59 families), MONTH–MOON (57), CLAW–FINGERNAIL (55) and FOOT–LEG (52).
- **Caveats:**
  - CLICS3 is the 2020 release. CLICS4 (2024, more datasets) exists but I did not use it.
  - Some edges join two Concepticon variants of one idea (KNIFE with KNIFE (FOR EATING)). A generator may want to treat these as near-synonyms rather than colexifications.

## Concept lists: `concepts.tsv`

- **Opened:** https://raw.githubusercontent.com/concepticon/concepticon-data/master/concepticondata/ (commit 1d53585c, 2026-11-03): `concepticon.tsv`, and in `conceptlists/` the files `Tadmor-2009-100`, `Swadesh-1952-200`, `Swadesh-1955-100`, `Pagel-2007-200`, `Holman-2008-100` and `Holman-2008-40`.
- **Licence:** CC-BY 4.0 (Concepticon). The list values come from the cited papers.
- **Derived:**
  - **Lists:** 240 concepts, the union of Leipzig-Jakarta 100 and "Swadesh 207". Concepticon has no 207 list, so I built it as Swadesh 1952 (200) ∪ Swadesh 1955 (100) by Concepticon id. That union is the source of the familiar 207 list, but it maps to 213 ids, because a few English glosses split into two Concepticon concepts.
  - **Columns:** list membership, Leipzig-Jakarta rank, Pagel et al. 2007 Indo-European replacement rate and English frequency, and ASJP stability rank and score (Holman et al. 2008).
  - **`stability_class`:** 1 is most stable, 5 fastest. It is derived, not published: the quintile of the Pagel rate where available (200 concepts). Otherwise it is the quintile of Holman stability, otherwise the quintile of the Leipzig-Jakarta rank.
  - **From knowledge:** 3 concepts (BERRY, MALE PERSON, HOT OR WARM) have none of those values. I gave them classes from knowledge, marked `stability_class_source=knowledge`.
- **Caveat:** the Pagel rates are Indo-European only. Holman's ASJP ranks are global but cover only 100 items, so classes from the two sources are not strictly comparable.
- **WOLD extension (2026-11-07, round 5):** 339 more meanings from the WOLD 1460 list (Haspelmath & Tadmor 2009, Concepticon `Haspelmath-2009-1460.tsv`, raw copy in `data/language/raw/wold/`), picked by hand in `build_reference_tables.WOLD_EXTENSION`: motion and everyday verbs, exchange, qualities, kin by birth order and marriage, numbers to a thousand, body, nature and time, animals and food, house and tools. They are marked `lists=WOLD1460`; `stability_class` is 3, 4 or 5 by tercile of WOLD's own rank (`stability_class_source=wold_rank_tercile`), and a new `pos` column carries WOLD's part of speech (blank for the core rows, whose part of speech `lexicon.py` sets; numerals are nouns like ONE). The core 240 rows are unchanged. Word-building recipes for the new meanings were added by hand to `derivations.tsv` (~95 rows) and `compounds.tsv` (~60 rows).

## Grammaticalization paths: `grammaticalization_paths.tsv` (from knowledge)

- **Source:** written from my general knowledge of the paths catalogued in Heine & Kuteva's *World Lexicon of Grammaticalization* (2002; 2nd ed. 2019), Bybee, Perkins & Pagliuca 1994, and Hopper & Traugott 2003. **Nothing was extracted from the book.** The file header says so.
- **Content:** 72 paths, among them:
  - motion to future (GO, COME), WANT > FUTURE, HAVE > PERFECT, FINISH > PERFECTIVE;
  - SAY > COMPLEMENTIZER, GIVE > BENEFACTIVE/CAUSATIVE, TAKE > OBJECT MARKER;
  - body part > spatial adposition (BACK, FACE, HEAD, BELLY, BUTTOCKS, SIDE);
  - ONE > INDEFINITE, DEMONSTRATIVE > DEFINITE > NOUN MARKER, DEMONSTRATIVE > PRONOUN > AGREEMENT;
  - COPULA > FOCUS, BODY > REFLEXIVE > MIDDLE > PASSIVE, CHILD > DIMINUTIVE, Jespersen's cycle, and others.
- **Columns:** source, target, intermediate stages, typical fusion endpoint, frequency class (very common / common / attested), and one real example.
- **Caveats:**
  - Frequency classes are my judgement, not counts.
  - Examples are textbook cases, romanized, with tones and diacritics dropped. A few (K'iche' chuxe', Tibetan -thong, the Croft negative-existential cycle) are cited from memory, so check them before quoting them anywhere public.

## Sound changes: `sound_changes.tsv` (from knowledge)

- **Source:** written from my knowledge of standard historical phonology (Campbell; Hock 1991; Blevins 2004; Kümmel 2007). The Index Diachronica (https://chridd.nfshost.com/diachronica/, a hobbyist compilation) was **inspiration only**. I did not open it this session and copied nothing from it.
- **Content:** 185 context-conditioned changes in 23 families. They cover every area the brief listed:
  - lenition chains, intervocalic voicing, spirantization, fortition;
  - palatalization, nasal-place and voicing assimilation, final devoicing, final consonant loss, cluster simplification;
  - vowel reduction, apocope and syncope, umlaut and harmony, nasalization and nasal loss;
  - rhotacism, debuccalization, h-loss, glottalization;
  - tonogenesis from onset voicing and from coda ʔ and h;
  - Grimm, the High German shift, the Great Vowel Shift, the Northern Cities Shift;
  - metathesis, epenthesis, θ > f, ɸ > f, w > v, l-vocalization, uvular > pharyngeal/glottal, click loss;
  - gemination and degemination, prenasalization, labialization.
- **Columns:** id, family, rule, cause, articulators_or_axes_needed, naturalness, example.
  - **Rule:** compact notation, defined in the header.
  - **Cause:** one of seven words.
  - **Articulators or axes:** from a fixed list, which the script validates. They let a people without lips, or without pitch perception, skip changes that need them.
  - **Naturalness:** 1 to 5.
  - **Example:** one real-language case.
- **Caveats:**
  - Naturalness and cause are judgement.
  - A few rows are rare, and their examples are flagged as weak in the row itself (χ > ħ is marked "example not verified"; the Cʔ > Cʼ ejective row).
  - The Vietnamese tonogenesis rows name the coda sources (Haudricourt 1954) but deliberately not which tone came from which coda, because I was not sure of that mapping.
  - Some rows are paradigm or prosodic processes (analogy, Meeussen's rule, pitch accent) rather than segmental changes. They are included because the brief's cause list asks for them.

## Raw downloads (in `data/language/raw/`, git-ignored)

`phoible/phoible.csv` (26 MB); `grambank/*.csv` (52 MB); `wals/*.csv` (5 MB); `clics3/clics3-network.gml.zip` (12 MB) plus `clics3/extract/graphs/network-3-families.gml` (71 MB); `concepticon/*.tsv` (0.5 MB). Each source has its own directory. All of it was read only as CSV, TSV or GML text by `python -I`.
