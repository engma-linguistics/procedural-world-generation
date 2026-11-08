# Language engine: architecture and contracts (lane, 2026-11-03)

This is the build contract for `planet/language/`. The design doc ("Languages from scratch: design",
https://claude.ai/artifact/58m5qxKajjfn6TkTqq3EL2) says *what*; this says *how*, precisely enough that several builders can
work in parallel and meet in the middle. `inputs.md` (next to this file) describes the stored data we read. Where this doc
and a builder's judgement disagree, build the better thing and say so in your report.

Everything is deterministic per seed: every draw goes through a `numpy.random.Generator` or `random.Random` seeded from the
run seed plus a stable string (`seed_for(run_seed, "lect", lect_id)`), never the global RNG.

## 1. Package layout

| Module | Owns | Depends on |
| --- | --- | --- |
| `percepts.py` | the percept space, `Segment`, distance, the IPA/extIPA/house symbol table (`data/symbols.tsv`) | - |
| `profiles.py` | `VoiceProfile`, the human default from PHOIBLE, non-human profiles (`data/voice_profiles.toml`), inheritance along the lineage tree, nativization (hear a segment through a profile + inventory) | percepts |
| `romanize.py` | IPA string -> house spelling (`data/romanization.tsv`) | percepts |
| `inventory.py` | proto-inventory draw (PHOIBLE-weighted, feature economy, dispersion, make cost), phonotactics (sonority), word-shape draw | percepts, profiles |
| `rules.py` | `Rule` (percept-class rewrite with environment, cause, needs, weight), the catalogue (`data/sound_changes.tsv` + hand-written demo set), rule application to a word, functional-load veto | percepts, profiles |
| `lexicon.py` | concept list (`data/concepts.tsv` + food/landscape/kin/gods), `Word` with etymology, replacement by frequency, derivation, compounding, colexification shift (`data/clics_edges.tsv`), borrowing with nativization, taboo, substrate | inventory, profiles |
| `grammar.py` | typology features with correlations (`data/grambank_*.tsv`, `data/wals_wordorder.tsv`), grams on the ladder (`data/grammaticalization_paths.tsv`), paradigm exemplars, name building (class prefixes, compound order, locatives) | lexicon, rules |
| `lect.py` | `Lect`: one speech variety; holds inventory, phonotactics, lexicon, grammar, rule history, rate; `copy()`; per-generation `step()` | inventory, rules, lexicon, grammar |
| `history.py` | the driver: reads the run (demes, contacts, takeovers, settlements, crop spread), walks time from `START_KYR` to now, runs steps, tree + wave spread, shift and substrate, borrowing along routes | lect, inputs |
| `names.py` | name stacks per people and deme (ethnonym patterns E/X/P), place and river names, glossonyms, the Common and its exonyms | lexicon, grammar, romanize |
| `families.py` | the true lect tree, language clustering (dialect vs language), the scholars' tree by an automatic comparative method, the horizon measurement | lect |
| `checks.py` | every check in the design doc, each returning a number and a verdict | families, lect |
| `output.py` | `languages.json` writer, the placeholder export for the writing repo, the brief and workbench feeds | all |
| `run.py` | `planet languages RUN [--seed]` CLI, wired like `planet demes` | output |

`planet/language/data/` holds the derived reference tables (see `reference-data.md`). `data/language/raw/` (git-ignored) holds
downloads.

## 2. Segments: the percept space (`percepts.py`)

A `Segment` is an immutable record of axis values. Axes are the same for every species; a species that lacks an axis never
sets it. Values are small integers on ordinal scales so distance is meaningful; the symbol table maps IPA <-> axis values.

```python
@dataclass(frozen=True, slots=True)
class Segment:
    kind: str            # "C" | "V" | "T" (tone letter, only when a lect has tone)
    # consonants (as heard)
    place: int = 0       # 0 labial(grave) 1 dental 2 alveolar(acute) 3 postalveolar 4 palatal 5 velar(compact) 6 uvular 7 pharyngeal 8 glottal
    manner: int = 0      # 0 stop 1 affricate 2 fricative 3 nasal 4 approximant 5 lateral 6 trill 7 tap 8 click 9 percussive
    voice: int = 0       # 0 voiceless 1 voiced
    larynx: int = 0      # 0 plain 1 aspirated 2 ejective 3 implosive  (airstream/VOT as heard)
    phonation: int = 0   # 0 modal 1 breathy 2 creaky 3 harsh(growl) 4 purr
    secondary: int = 0   # 0 none 1 labialized 2 palatalized 3 velarized 4 pharyngealized
    sibilant: int = 0    # 0 no 1 yes (fricative/affricate spectral centre high: s-like vs θ/f-like)
    # vowels (as heard)
    height: int = 0      # 0 low .. 6 high  (F1 inverse)
    back: int = 0        # 0 front .. 4 back (F2)
    round: int = 0       # 0 unrounded 1 rounded (F2/F3 lowering)
    nasal: int = 0       # 0 oral 1 nasal
    # shared
    length: int = 0      # 0 short 1 long (geminate for C)
    tone: int = 0        # 0 none 1 low 2 mid 3 high 4 rising 5 falling   (on V; "T" kind for a standalone tone letter)
    source2: int = 0     # 0 none 1 second simultaneous source (syrinx)  - non-human
    register: int = 0    # 0 human range, -1 sub-bass, +1 ultra  - non-human pitch register
```

Functions:

- `AXES`: ordered tuple of axis names; `AXIS_RANGE[axis] -> (lo, hi)`.
- `from_ipa(s: str) -> list[Segment]` and `to_ipa(seg) -> str` via `data/symbols.tsv` (columns: `symbol`, then one column per
  axis, then `source` = ipa | extipa | house, `note`). Multi-character IPA (tʃ, kʷ, aː, ã) parses by longest match; unknown
  segments get the nearest symbol and `to_ipa` falls back to a house symbol. Diacritics ː ʰ ʼ ʷ ʲ ˠ ˤ ̃  are handled as
  modifiers in the parser, not as table rows.
- `distance(a, b, weights=None) -> float`: weighted L1 over axes, with a large penalty for kind mismatch. `weights` is a
  dict axis -> float from a profile's hear resolution (0 means the listener does not hear that axis at all).
- `natural_class(**bounds) -> Callable[[Segment], bool]` and the class notation used by rules: `C`, `V`, `N` (nasal), `P`
  (stop), `F` (fricative), `S` (sibilant), `L` (liquid), `G` (glide), `[+voice]`, `[place=0..1]`, `#` (word edge), `_`.
- `Word = tuple[Segment, ...]`; `word_ipa(word)`; `syllabify(word, sonority) -> list[Syllable]`.

Sonority scale (for syllabification and shapes): V 10 > G 8 > L 7 > N 6 > F(voiced) 5 > F 4 > affricate 3 > P(voiced) 2 > P 1.

## 3. Voice profiles (`profiles.py`)

```python
@dataclass
class VoiceProfile:
    id: str                              # lineage id it was resolved for
    source: str                          # "human_default" | "data_file" | "spec"
    modality: str = "spoken"             # spoken | signed (reserved)
    articulators: frozenset[str] = ...   # lips, teeth, tongue_tip, tongue_body, velum, larynx, pharynx, syrinx, beak
    make_cost: dict[str, float]          # keyed by a *percept class key* (see below) -> multiplier on the human cost; inf = impossible
    hear: dict[str, float]               # axis -> resolution multiplier (1 human; 0 unheard; 2 twice as fine)
    register: int = 0                    # pitch register offset
    notes: list[str]                     # plain-words lines for the workbench and voice-profiles.md
```

**Human cost per segment** is derived from PHOIBLE: `cost(seg) = -log(freq_in_inventories(seg))` for attested segments
(clamped to [0.1, 8]); a segment PHOIBLE never shows gets 8; a non-human percept (source2, register != 0, phonation harsh/purr,
percussive) gets `inf` for humans. Store the per-segment human cost in the `Inventory` draw, not in the profile.

**Percept class keys** for `make_cost` are a small closed vocabulary so a TOML can say what it means:
`labial` (place 0), `dental`, `alveolar`, `postalveolar`, `palatal`, `velar`, `uvular`, `pharyngeal`, `glottal`, `stop`,
`fricative`, `affricate`, `nasal`, `approximant`, `lateral`, `trill`, `tap`, `click`, `percussive`, `voiced`, `aspirated`,
`ejective`, `implosive`, `breathy`, `creaky`, `harsh`, `purr`, `labialized`, `palatalized`, `round_vowel`, `nasal_vowel`,
`front_vowel`, `back_vowel`, `high_vowel`, `low_vowel`, `tone`, `long`, `source2`, `sub_register`, `ultra_register`.
`species_cost(profile, seg) = human_cost(seg) * prod(make_cost[k] for k in keys_of(seg))`; `inf` wins.

**Inheritance**: `resolve_profile(lineage_id, tree) -> VoiceProfile` walks parents (first parent) and merges key by key:
`data/voice_profiles.toml` gives tables keyed by lineage id (stems and kinds, as in `dnd.toml`), and a lineage's own `voice`
table in the spec (new key, parsed by `spec.parse_voice`, inherited like `body`) overrides. Anything unresolved is the human
default. Every profile records `source` so the workbench can say "human default (not yet profiled)".

**Nativization** (`hear_word(word, listener_profile, listener_inventory) -> Word`): each segment maps to the nearest segment
in the listener's inventory by `distance` under the listener's `hear` weights; a segment whose nearest is farther than
`DROP_DISTANCE` (or on an axis the listener hears at 0) is dropped; then the phonotactic repair (epenthesis or deletion) of
`inventory.repair`. This is the one operation used for loanwords, substrate accent and cross-species borrowing.

## 4. Inventories and words (`inventory.py`)

```python
@dataclass
class Inventory:
    consonants: list[Segment]; vowels: list[Segment]; tones: list[int]   # tones: [] or e.g. [1,3] (low, high)
    shapes: dict[str, float]          # syllable templates by weight: "CV" 0.6, "CVC" 0.3, "CCV" 0.1 ... (max onset/coda sizes)
    onset_ok, coda_ok: callables or small tables over natural classes (sonority-sequenced)
    stress: str                       # "initial" | "final" | "penult" | "none"
    cost: dict[Segment, float]        # species cost per segment at draw time
```

Draw (`draw_inventory(rng, profile, size_hint=None)`): sample total consonant and vowel counts from PHOIBLE's size
distribution (`phoible_inventory_sizes.tsv`), then pick segments with probability `freq ** a / (1 + cost)` with feature
economy (prefer segments that reuse already-chosen places and manners: Clements) and vowel dispersion (reject a vowel closer
than `MIN_V_DIST` to an existing one until the system is full). Tone: with the PHOIBLE share of tonal languages, scaled by
the profile's `tone` cost and `hear["tone"]`. Shapes: draw from a small distribution of canonical syllable types (CV only;
CV(C); (C)(C)V(C); (C)(C)V(C)(C)), with onset and coda clusters allowed only if sonority rises into the nucleus.
**Clicks** (2026-11-04): a human-voiced proto (`profiles.human_voiced`) drawing at least `CLICK_MIN_C` (28) consonants gets
a click system with the probability that makes `CLICK_SHARE` (1.5%, PHOIBLE's share of click inventories) of all protos
click languages: 3-5 places (ǀ ǃ ǁ, + ǂ, + ʘ) x as many accompaniments (plain, voiced, nasal, aspirated, glottalized,
breathy) as fill `CLICK_PART` (45%) of the consonants, lexical commonness `CLICK_LEX_FREQ`. They are the main source of the
long consonant tail, as in PHOIBLE (Nama, Zulu, !Xóõ).

`draw_word(rng, inv, syllables=None) -> Word`, `repair(word, inv) -> Word` (make a word fit the phonotactics with the
cheapest edit: epenthesis of the inventory's commonest high vowel, cluster simplification, coda deletion).
`legal` also rejects two vowels of one quality side by side (a long vowel), a run of three vowels and a word-initial
geminate (2026-11-04, hiatus round); `repair` resolves them first (`_resolve_vowels`: fusion, long when the lect has that
long vowel; a high vowel in the run to its glide when the lect has j or w; else V1 elision), so coinages, compounds,
derivations and loans come out without them.

**Phonemes and allophones** (2026-11-04). `observed(inv, forms)` lists only phonemes in `consonants` / `vowels`;
`inv.allophones` maps each allophone to `(phoneme or None, test)`. `phonemic(forms, segs)` is the standard test
(complementary distribution with a commoner close sound, from the lect's own word forms; Hayes 2009 ch. 2): x is an
allophone of p when x and p differ in one feature group, p has >= 3 tokens and more than x, every token of x stands in the
test's environment and no token of p does, and no other allophone of p shares an environment with x. Tests
(`ALLO_TESTS`): nasal place assimilation (before a consonant of its place), palatalization (before front vowels and j),
intervocalic lenition (voicing or stop/fricative), final (voicing), initial (aspiration), vowel nasalization (before a
nasal), coda liquids (dark ɫ beside l and approximant ɹ beside the trill or tap, only before a consonant or word-finally;
round 5), and an inserted glottal onset (ʔ only before a word-initial vowel or in hiatus, with no vowel-initial word or hiatus
left without it; phoneme None). `legal` accepts allophones; `draw_word` and `repair` draw and fix with phonemes and then
`realize` the allophones (p becomes x in x's environment; ʔ inserted), so coinages and loans keep the pattern. Checks,
the size steer, snapshots (`al`) and the output (`inventory.allophones`) use the phonemic inventory; sound-change rules see
the surface forms.

## 5. Sound change (`rules.py`)

```python
@dataclass(frozen=True)
class Rule:
    id: str                 # "lenition.intervocalic_voicing"
    target: Pattern         # natural-class predicate over Segment, e.g. P & [-voice]
    change: Change          # axis -> new value (or delete, or insert)
    env: Env                # left and right context as class predicates, with "#" and optional "V_V" style sugar
    cause: str              # coarticulation | effort | perception | prosody | tonogenesis | dispersion | analogy
    needs: frozenset[str]   # articulators or hear axes the cause depends on: {"lips"}, {"velum"}, {"pitch_ear"}, ...
    weight: float           # naturalness x attested frequency, 1..5
    scope: str = "regular"  # regular | diffusing  (diffusing hits words by frequency over several generations)
```

- `catalogue(profile) -> list[Rule]`: all rules whose `needs` the profile has, with `weight` scaled by the species' make
  cost of the *output* (a rule producing a costly percept is downweighted; one removing a costly percept is upweighted).
- Per lect (`lect.rule_factor`, cached per segment set, 2026-11-04): x `NEW_SEG_WEIGHT` (0.3) when the rule brings in a
  segment the lect lacks; the **ease drag** for human voices, x `exp(EASE_K (cost_in - cost_out))` with PHOIBLE's
  `-ln share` as the cost, i.e. (share_out / share_in) ** 0.5, clamped to [0.25, 3] (light: drift still happens; a deletion
  makes nothing, an insertion is neutral; non-human voices get only their own make costs, through `cost_factor`, never
  PHOIBLE); and the **size steer**: (PHOIBLE size prior at the count the rule leaves / at the count now) ** `SIZE_K` (0.5)
  x a lognormal pull (sigma `SIZE_ANCHOR` 0.12 in ln n) toward the line's own proto count, clamped to [0.02, 3]
  (2026-11-04, was 0.2 and [0.1, 2]); the counts are the phonemes (allophones aside). A context-free rule removes what it
  rewrites; a conditioned one is a split; an assimilation (`[αplace]`) counts each output it could make from the lect's
  consonants (`lect.touched_by`). Wave adoption is damped by the same size steer (`lect.size_factor`) and the ease drag.
- The **stop steer** (human voices, 2026-11-04, word families round): s = oral stops over supralaryngeal consonant tokens in
  the lect's most frequent words (`load_forms`; ʔ, h and pharyngeals left out), binned in ln(s / `STOP_NORM` 0.33) steps of
  0.1 (part of the cache key); a rule's weight x exp(-`STOP_K` (2) x d x ln(s / 0.33)), d the mean change in stop-ness over
  the segments it rewrites (-1 stop to non-stop or deleted, +1 non-stop to stop), clamped to [0.1, 4]. Below the norm a
  lenition of stops is drawn less and a fortition or devoicing to stops more; above it the reverse. It replaced the refill
  that fresh coinages used to give (`lexicon.SOURCES` coin 0.15 -> 0.03); the ease drag's wave factor carries it too.
- The **keep steer** (human voices, 2026-11-04, sinks round): a rule that would leave no token of a near-universal phoneme
  (PHOIBLE share >= `KEEP_SHARE` 0.7: p t k m n l j w i u a) in the lect's frequent words (`load_forms`), when it had some,
  is weighted `KEEP_FACTOR` (0.25); a rule that only thins it (conditioned, some tokens survive) is untouched
  (`lect.keep_part`, tried only on forms holding such a phoneme, stopping at the first survivor). It is part of the cached
  weights and of the wave's ease factor. Catalogue sinks (one-way paths into ʔ, ɲ, ʋ) were balanced in the same round with
  conditioned creators and attested exits (calibration.md "Sinks round"); twins of a change drawn under two ids are listed
  in `rules.SAME_AS` and drawn once.
- **Hiatus** (2026-11-04, hiatus round; calibration.md "Hiatus round"). Two driver-side repairs, after Casali 1997, 2011
  (hiatus is resolved fast and nearly everywhere). (1) `lect.normalize` (run on every rule output and every fold) fuses two
  vowels of one quality into one (`inventory.fuse_vowels`: long when the lect has a long vowel, short when not; two level
  tones fuse to a contour) and simplifies a word-initial geminate. (2) `Lect.apply_rule`: a change that leaves more hiatus
  in the lexicon than before it (`inventory.hiatus_in`: adjacent vowels that are not a falling diphthong, a non-high vowel
  + a short high one) is followed by up to `HIATUS_REPAIRS` (3) firings of the catalogue's hiatus family (S125-S127,
  S205-S207: hiatus glides, V1 elision, glide formation, Attic contraction, Portuguese j-epenthesis), each the candidate
  with the highest weight x line preference (`hiatus_pref`: a lognormal, sigma `HIATUS_SPREAD` 1, keyed by the line's
  proto, `Lect.hiatus_key`, so daughters keep their parent's strategy) among those that reduce the hiatus of the words that
  have it and do not put most changed words back. Repairs are recorded changes, outside the re-fire memory.
- `apply(rule, word) -> Word`, left to right, regular, on a tuple of Segments; `applies(rule, inv) -> bool` (the lect has
  a target segment).
- `pick_rule(rng, lect) -> Rule | None`: weighted by `weight`, then vetoed by functional load: estimate the mergers the rule
  causes over the lect's lexicon (how many minimal pairs collapse, `functional_load(rule, lexicon) -> float`); veto with
  probability rising with that load (Wedel). Chain-shift repair: after a merger-vetoed vowel rule, offer a dispersion rule that
  moves the crowded vowel instead.
- The demo set: ~25 hand-written rules in `DEMO_RULES` covering lenition (p>f>h>0, intervocalic voicing, spirantization),
  final devoicing, final vowel loss, unstressed vowel reduction and syncope, nasal place assimilation, palatalization before
  front vowels, nasalization + nasal loss, s>h, h>0, θ>f, cluster simplification, vowel harmony (one rule), umlaut, rhotacism,
  tonogenesis from coda loss, a chain shift step, metathesis of CC, and epenthesis. The full catalogue is loaded from
  `data/sound_changes.tsv` by a parser of the compact notation; parse failures are logged and skipped, not fatal.
- Rules run on *inflected forms* too: the lect hands `apply` every stored form (stems, paradigm exemplar forms, gram forms,
  names).

## 6. Words and etymologies (`lexicon.py`)

```python
@dataclass
class Word:
    concept: str                 # Concepticon-style gloss: "WATER", "RIVER", "crop:barley", "god:storm", "kin:mother"
    form: Word_                  # tuple[Segment,...]
    pos: str                     # N | V | A | FUNC | NAME
    freq_class: int              # 1 (most frequent, slowest to replace) .. 5
    etym: list[EtymStep]         # oldest first
    born_kyr: float
    roots: tuple[str, ...]       # root ids the word is built on, main root first (2026-11-04, see "Root families" below)
    etym_roots: tuple[str, ...]  # the historian's roots (owner 11-07): set when the word is made, never re-read; carried
                                 # through sound change, shifts and loans (a loan keeps the donor's); `etym_roots(w)`
@dataclass
class EtymStep:
    kyr: float; lect: str; process: str   # proto | sound_change:<rule id> | replace | derive:<affix> | compound:<a>+<b> | shift:<from concept> | borrow:<lect> | taboo | substrate:<lect> | analogy | nativize
    form: str                             # IPA at that step
    gloss: str                            # meaning at that step
    note: str = ""
```

Concept list (`concepts()`): Leipzig-Jakarta + Swadesh from `data/concepts.tsv`; food concepts from `crop_defs`,
`animal_defs`, `fuels`, cooking acts (`cook`, `boil`, `roast`, `smoke`, `ferment`, `grind`, `salt`), tastes (`sweet`,
`bitter`, `sour`, `salty`); landscape (`river`, `lake`, `sea`, `mountain`, `hill`, `forest`, `marsh`, `plain`, `coast`,
`island`, `spring`, `ford`, `pass`), directions (`north`.. and `upstream`/`downstream`, `sunrise`/`sunset`), kin (12),
numbers 1-10, `people`, `person`, `real`, `speak`, `mute`, `stranger`, `enemy`, `friend`, `old`, `new`, `big`, `small`,
`black`, `white`, `red`, and the god domains from `gods.py`. A few hundred in all.

Per-generation lexical events on a lect (`lexicon.step(rng, lect, gen_rate)`):
- **replacement**: each word's hazard = `BASE_REPLACE * RATE_BY_FREQ[freq_class]` per generation, calibrated so Swadesh-100
  retention is 86% per millennium at human generation length (Pagel 2007 shape: frequent words `FREQ_SPREAD` = 4x slower
  than rare, "several times"; it was 10x until 2026-11-04, with `history.REPLACE_SCALE` 1.25, now 1.0).
  The replacement source is drawn from `SOURCES` (2026-11-04): derive along the table 0.36, compound 0.22, renew 0.12,
  colexification shift from a CLICS neighbour 0.10, borrow from a contact lect 0.12 (only when one has the word), taboo
  0.05 (animals and dangerous concepts only), a fresh root 0.03. A source that cannot make a word falls back to the next
  plausible one: derive, compound, shift, renew, a loan (`BORROW_FALLBACK` 0.5 when a contact lect has the word), and
  only then a fresh root (the weaker 4-family shift fallback was dropped 2026-11-04, compounds and shifts round). `Lexicon.counts` tallies the
  sources used (lineage totals, in `stats.replacements`).
- **derivation is table-driven** (`data/derivations.tsv`, 2026-11-04): rows `relation, base, target, weight, example`,
  relation = the affix meaning: agent 'one who' (HUNT > HUNTER), thing 'instrument / result / object' (CUT > KNIFE,
  CARRY > BURDEN), place (SLEEP > BED, DIG > GRAVE), little (RIVER > STREAM, CHILD > BABY), like (BLOOD > RED), do (SALT >
  SALT (FOOD), FIRE > BURN), cause (DIE > KILL), plus `reinforce` rows for function words (THIS + HERE > 'this', NOT + ONE >
  'not': compounds of a function word with itself and its reinforcer). ~200 rows, written from knowledge after Buck 1949,
  Urban 2012, Koch 2008, Pokorny / LIV2 and Heine & Kuteva 2002 (sources in the header); CLICS3's family count for a pair
  is added to its weight at load. `affix_fits(meaning, target, base)` is true only for a table pair. Two renewals stand
  beside the table: a noun, quality or natural thing replaced by its own diminutive (`RENEW_LITTLE`: Latin auricula >
  oreille, vetulus > vieux) and a verb by its frequentative or preverb form (`RENEW_INTENS`, the eighth affix 'intens':
  cantare < canere, comedere > comer); a renewal is bleached at once (it starts a new simple root for stacking) and is
  outside `AFFIX_CAP`.
- **stacking and re-analysis**: `word_layers(lex, w, kyr) -> (affixes, morphemes)` counts the derivations and compounds
  still felt as such, walking back from the latest step; it stops at a proto root, a coinage, a loan, a shift, a taboo or
  substrate step, a renewal, a derivation or compound older than `OPAQUE_KYR` (3), or a derivation whose base word has
  been replaced since (its root differs). A derivation needs the base at < `MAX_AFFIXES` (2) affixes and < `MAX_MORPHEMES`
  (3) morphemes; a compound of two parts may hold MAX_MORPHEMES in all. So a lexicalised word (burden, no longer bear +
  -th) is a simple root again and may take new affixes, and nothing accretes past two live affixes. `AFFIX_CAP` (0.08)
  limits each affix to that share of the words whose outermost formation step it is (`affix_share`).
- **compounds come only from recipes** (2026-11-04, compounds and shifts round): `data/compounds.tsv` (~200 rows: target,
  head, modifier, weight, example; sources in its header: Urban 2012, Brown 1976/1999, Witkowski & Brown, Buck 1949, WOLD,
  the Southeast Asian generic + specific compounds; CLICS3 counts of (target, head) and (target, modifier) added at load).
  The head is the category the target is a kind or part of: SKIN + TREE = bark, HAIR + BIRD = feather, EYE + DAY = sun,
  EYE + WATER = spring, CHILD + WOMAN = girl, MOTHER + BIG = grandmother, FIVE + ONE = six, DOG + BIG = horse; modifier
  `SELF` is the target's own word (a generic + specific renewal, Thai plaa-X, rein-deer: it carries the old word's chain
  and root). The ELABORATIONS table is the recipe of the elaborated concepts (MILK + SOUR); function words are reinforced
  along derivations.tsv's 'reinforce' rows, never twice with the same reinforcer while it is felt. A concept with no
  recipe (EGG, FLOWER, TREE, verbs, qualities) never compounds; its replacement comes from the other sources.
- **semantic shifts** (same round): along a CLICS3 colexification of >= `SHIFT_MIN_FAMILIES` (5) families,
  `SHIFT_MIN_CORE` (6) for the Swadesh-100 and frequency classes 1-2, between concepts of one semantic field
  (concepts.tsv, else CLICS3's field for the gloss) and part of speech; or along an attested pathway of derivations.tsv's
  `shift` rows (42: TREE > WOOD, SKIN > BARK, SKY > GOD, BREATH > SPIRIT, SEE > KNOW, HAND > FIVE, and grammaticalization
  BELLY > IN, WITH > AND, ONE > SOME; Buck, Wilkins 1996, Sweetser 1990, Heine & Kuteva 2002). A word shifted within
  `SHIFT_CHAIN_KYR` (3) is not taken again (`shift_candidates`, `shift_fits`). DOG ~ MOON, EGG ~ NAME, SEED ~ EYE,
  TREE ~ FIRE are no longer paths. `RENEW_LITTLE` also covers tools, plants and kin (couteau < cultellus, abuelo <
  aviolus).
- **elaboration**: when a concept's weight in the deme's life passes a threshold (herder: milk words; coast: fish words;
  farmer: crop-stage words; from `inputs.md` niches), split it with a derived or compound word.
- **borrowing on arrival**: `borrow(word, from_lect, to_lect, kyr, route_note)` = `hear_word` + repair + an `EtymStep`
  `borrow:<lect>`; the result is a normal word thereafter.

**Root families** (2026-11-04). A proto-lexicon grows from a root stock: every concept with a table row whose base is
on the proto's list is built from it with `PROTO_DERIVE[freq class]` (1: 0.15, 2: 0.3, 3: 0.55, 4: 0.7, 5: 0.75;
`PROTO_DERIVE_DERIVED` 0.95 for the derived vocabulary, domain "derived": HUNTER, FIGHTER, GUEST, HERDER, FISHER, SMITH,
ELDER, BABY, GIRL, BOY, KNIFE, AXE, NEEDLE, SPEAR, CUP, BURDEN, SEAT, BED, CAMP, GRAVE, STREAM, POND, PEBBLE, TWIG, PUPPY,
CHICK, SONG, DREAM, BREATH, GIFT, HEAT), in passes so a base may itself be derived (up to MAX_AFFIXES); the rest are simple
roots. About 22% of a proto's words are derived (11% of the core 100: core Swadesh items are mostly simple roots), so a
root such as FIRE has BURN, COOK, HEARTH, HOT, RED among its words. Every word carries `roots`, the roots a speaker still feels (`felt_roots`, re-read
after every `step` by `refresh_roots`; 2026-11-04, compounds and shifts round): a transparent derivation or taboo
paraphrase has its base's roots, a transparent compound its head's then its modifier's (a part replaced since is not
felt), a renewal keeps the word's own. A word is a root of its own from the step a speaker no longer analyses: a proto
root, a coinage, a derivation or compound older than OPAQUE_KYR, a shift away from the old meaning, a loan, a substrate
word. Ids: `"<proto lect>:<CONCEPT>"` for a word of the proto (made at its date), else `"<lect>:<CONCEPT>@<kyr>"` of that
step; `root_step(w)` finds the step (output.py's root table points there). Daughters inherit the families while they are
felt: a proto derivation is its own root once older than 3 kyr, so living lects' families are their recent derivations
and compounds on inherited roots.
The chain itself records the root too: a derived word's chain begins with its base's chain, so its first step is the
root's (proto, coin) step.

**Word length follows the syllable space** (2026-11-04). `syllable_space(inv)` is the effective number of distinct
syllables the inventory and its templates allow (perplexity over templates: onsets x vowels x tones x codas legal under the
phonotactics; ~35 for a 6 C / 5 V CV-only language, ~1100 for 25 C / 8 V (C)V(C), ~10^5 for 40 C / 12 V complex).
`length_scale(inv) = (LN_SIGMA_REF / ln sigma) ** LENGTH_EXP`, LN_SIGMA_REF = 7.7 (median human proto), LENGTH_EXP = 0.7,
clipped to [0.7, 2.0]. Root syllables (`_n_syll_for`, 1-3 by frequency class, frequent words shorter) are multiplied by it
(stochastic rounding, so the mean scales exactly); `limits(inv)` scales MAX_SYLL 3, MAX_SYLL_COMPOUND 4 and MAX_SEG 12 up
with it (never down), and derivation and compound clipping keep more of their parts. Source: Nettle 1995 (Linguistics 33:
359) and 1998 (J. Quant. Ling. 5:240): stems are shorter the larger the inventory, combined fit X = 17.87 S^-0.31 segments
(r = 0.82), a coding-efficiency trade-off (Kohler's synergetic model); the exponent 0.7 damps the pure coding law
(length ~ 1 / ln sigma) to Nettle's slope (a Rotokas-sized CV language ~1.6-1.8x the syllables of a 25 C (C)V(C) one).
Over time the scale is re-measured on the lect's current inventory at every `lexicon.step`: after mergers shrink it,
coinages are longer, derivation and compounding get `max(1, scale)` times their source weight (shift 1/scale), and a
homophone being renewed weights derivation and compounding by LONGER_RENEWAL = 2 (Nettle 1998's mechanism: mergers make
homophones, speakers answer with longer words, aujourd'hui < hui). `stats` reports `core_mean_syllables`,
`core_mean_segments`, `syllable_space` and `length_scale`.

## 7. Grammar (`grammar.py`)

Two layers.

**Typology** (`Typology` = dict feature -> value): draw at proto time from `grambank_features.tsv` value frequencies in a
fixed order so conditional draws use `grambank_correlations.tsv` (basic word order first, then adposition order, genitive,
adjective, relative clause, case, number, gender/class, alignment, TAM categories, polarity, question marking). Drift per
generation: each feature has a flip hazard from its stability class (word order and adposition order very stable; adjective
order and definite-article presence fickle), and a flip re-draws conditionally on the current word order. Keep ~40 features
in the demo.
Calibrated rates (2026-11-04; `grammar.STABILITY`, per generation: very stable 2e-4, stable 5e-4, medium 1e-3, fickle
2.5e-3, very fickle 4e-3, x (1 + adult-L2 share), x the lect's own `rate` as for sound change): over 20 kyr at human
generations a lect keeps its proto's value for ~85% (very stable), ~75-80% (stable), ~65% (medium), ~50-60% (fickle) of
features; 145-yr generations keep ~90%. A word-order harmony feature whose value the current basic order disfavours
flips up to 1 + DISHARMONY (9) times faster, so OV with postpositions and VO with prepositions re-assert themselves after
a word-order change. Sources for the ranking and the size of the spread: Dediu 2011, Dediu & Cysouw 2013, Greenhill et al.
2017, Dunn et al. 2011. `lect.grammar_step` runs it (`grammar.step(..., drift_typology=True, rate=lect.rate)`); before
this round nothing called the drift and typology only changed by calques on shift.

**One system** (2026-11-04, "Typology and grams round" in calibration.md). The drift above moves `Grammar.aims`, what the
community's syntax leans toward; `Grammar.typology` (what output, pages and checks read) is the aims with every feature
a gram realises read from the live grams (`grammar.realise`, `REALISED`): number (PL, DU), definite and indefinite article
(DEF side, INDEF), case (any of GEN LOC ABL ALL DAT ACC ERG INS COM; 'many' with 4+ or an ABL/ALL/INS/COM), alignment
(ACC/ERG fix it), past/future/perfective/progressive/habitual, evidentiality, negation (side of the main NEG), verb
agreement (person grams at clitic or tighter), causative and passive (bound at affix level), diminutive, agent noun,
gender and numeral classifiers (the class system: free classifiers, or gender once a class marker binds), clusivity
(two distinct 'we' forms in the lexicon; none yet, so 'no'), object agreement ('none': no gram marks it). Adposition
order stays an order feature but must agree with the side of the free and clitic case markers. The aims steer the
ladder: `_wanted` and `_side` read them; each category the aims mark and no live gram realises gets a recruitment pull
(`PRESSURE` 0.03 per generation, restricted to that category's paths); a bound gram the aims no longer want erodes
(`UNWANTED_LOSS`); an unwanted gram that binds anyway makes the aim follow it (`_adopt`). After an order change free
grams (level 0) move to the new side, bound ones stay; a NEG left on the old side lets a reinforcer be recruited on the
new one (Jespersen). Writes into `g.typology` from outside (calques on shift) become aims (`grammar.Shown`).
`grammar.clashes(g, lexicon)` lists contradictions; `checks.typology_consistency` counts living lects with any.

**Grammar phase A (2026-11-07, branch `lang-gram-a`; `grammar-gaps.md` Queue).**
- *The pull is per function* (`PULL_GROUP`, `pull_group`, `_unrealised`): an accusative or ergative answers the
  alignment, a dual the 'sg-du-pl' number, an oblique case (ABL ALL INS COM) 'case: many', a witnessed evidential
  'direct+indirect'; every other function answers its first feature with the rest of that feature's functions. Before,
  any case gram blocked the pull toward ACC/ERG, a plural blocked DU and a reportative blocked EVID.DIR.
- *More sources* (built-in paths X19-X26): ABL, LOC and GEN > ERG (gram reanalysis, Kuteva et al. 2019), an agentive
  'near, with' (English *by*) > ERG, DAT > ACC (differential object marking), 'leave, come' > ABL, 'go' > ALL, 'take,
  hold' > INS. G060 (reflexive > middle > passive) is mapped, so a REFL gram can become the passive; GET and BECOME
  (round 5 vocabulary) feed G032/G033.
- *Split ergativity* (`_split`, `Grammar.processes["split"]`): a lect with both a live ACC and a live ERG divides them
  by person (pronouns accusative, nouns ergative; 60%) or by aspect (ergative in the PERF or PAST clause, accusative
  elsewhere; only when it has one). Dropped when either case goes; logged as events.
- *Clusivity* (`_clusivity`, `INCLUSIVE_FROM`): when the aims say yes and the lexicon has one 'we', the lexicon gets
  WE (INCLUSIVE) from WE + THOU (45%), I + THOU (15%) or a root of its own (40%); plain WE is then the exclusive. At
  proto time at once; later at the PRESSURE rate; when the aims say no it goes at `CLUSIVE_LOSS` (a third of the time
  the inclusive becomes the only 'we'). `realised_value('clusivity')` reads the lexicon, as before. WE (INCLUSIVE) is in
  the pronoun contrast set (lexicon.py `_PRONOUNS`).
- *Verbal reduplication* (`_redup`, `REDUP`, `REDUP_SHAPE`, `reduplicant`): a process, not a gram: one meaning per lect
  (ITER iterative/pluractional 45%, INTS intensive 20%, CONT continuous 35%), a CV copy (65%; prefixed 3 times in 4)
  or the whole stem. The verb exemplars carry its cell (key `(ITER,)` etc.), so sound change wears the copy down with
  the word. `verb_reduplication` is now a realised feature (yes iff the process exists).
- *Counting base* (`_numerals`, `NUMERAL_WORDS`): at proto time a decimal lexicon builds TWENTY as 'two ten', a
  vigesimal one HUNDRED as 'five twenty' (and TWENTY as 'one person' half the time), the 'other' base 6-9 as 'five one'
  ... 'five four' (Comrie, WALS 131A). Multiplication follows the numeral's noun order, addition puts the larger first.
- *Person agreement as a set* (`PERSON_JOIN`, `_person_set`, `_person_fill`): when a person gram binds (reaches clitic),
  each other member of the series binds with it from its own pronoun (0.6-0.85 each; a zero 3SG is the commonest gap);
  `PERSON_FILL` (0.004 per generation) fills a remaining gap by analogy, at the paradigm's side and median level.
- *Degrammaticalization* (`DEGRAM` 1/50 of the hazard of the step undone, x3 `DEGRAM_EDGE` for NP-hosted markers, x3
  `DEGRAM_ORPHAN` when the marker is the last bound one of a slot that lost others; Norde 2009): a clitic or affix
  climbs one level; a grammar event.
- `Grammar.processes` is copied to daughters and kept in `to_json`/`from_json`.

**Grammar phase B (2026-11-08, branch `lang-gram-b`; `grammar-gaps.md` Queue).**
- *Mood* (`MOOD_FNS`: IMP, HORT, OBLG, APPR; slot 'mood'): G007 > OBLG, G034 > HORT, G035 > APPR mapped; built in
  'come, go' > HORT (X27), 'give' > HORT (X28), 'look!, come!' > IMP (X29, a guess), HORT > IMP (X30). No typology
  feature: the ordinary draw only.
- *Person series* (`SERIES`: S = the six subject persons + 1PL.INCL; O = 1SG.O ... 3PL.O on the verb, side rule 'oagr'
  from `object_agreement`; P = 1SG.POSS ... 3PL.POSS on the noun, slot 'poss' after number, side rule 'gen' from the
  genitive order). `_person_set` binds a series as a set when one member reaches clitic; `_person_fill` fills each
  series' gaps. One lead path per series (X33 'he' > 3SG.O, X39 'I' > 1SG.POSS); the other members' paths have the
  frequency class `set` (weight 0: never drawn alone). `object_agreement` is realised from the O grams and pulled by
  its aim. 1PL.INCL (X45) joins only when the lexicon has WE (INCLUSIVE).
- *Genitive sources*: ABL > GEN (X31), THAT/THIS > GEN linker (X32); `PULL_GROUP['GEN']` pulls a case lect toward one.
- *Class numbers* are never reused (`add_class` takes 1 + the highest CLASS number ever used); pages number classes
  1..n (`sentences.View.cl_num`). Role and trade nouns (MERCHANT, SOLDIER ...) are in the person group (`_PERSONS`).
- *Sentences*: `object_marker` on every transitive verb; `subject_marker` (1PL.INCL); possessor markers on possessed
  nouns (`noun_phrase`); `s_imperative` with IMP; `s_hortative`, `s_object`; notes Object agreement, Possessor marking,
  mood markers; `_shown_forms` makes a note name the joined shape of a marker its examples show.

**Grammar phase C (2026-11-08, branch `lang-gram-c`; `grammar-gaps.md` Queue).**
- *Constructions as grams* (slot 'clause', outermost): Q (X46 'if', X47 negator), COP (G056, X48 'he/she/it', X49
  posture verb), REL (G055, G058 'who, what'), COMP (G023 'say', X50 REL > COMP), TOP (X51 'if, when', X52
  demonstrative), FOC (G057 COP > FOC). `polar_question` and `copula` are realised features now (a free or clitic Q by
  its side, a bound one 'verb_morph'; COP live = yes), pulled by their aims; REL is wanted unless RelN; COMP, TOP, FOC
  come with the ordinary draw. Side rules 'q', 'rel', 'comp'. `COPY_PATHS`: a gram path whose source keeps its function
  (COP > FOC, REFL > RECP, COM > APPL ...): the new gram splits off with the source's form.
- *Valence, switch-reference, voice*: APPL (X53 'give', X54 COM), RECP (X55 REFL, X56 'other'), ANTIP (X57 REFL; wanted
  only in ergative/split lects), SS/DS (X58-X61; wanted only in OV lects), PV (X62 PASS > PV, reanalysis) and AV (X63
  'do', a guess; both wanted only in verb-initial lects).
- *Processes* (`Grammar.processes`, deep-copied to daughters): `concord` (sorted subset of dem/adj/verb, `_concord`,
  `CONCORD_GROW` while a class marker is bound at clitic+); `iclass` ({fn: {salt, share}}, `_iclass`: a bound marker gets a
  second form `Gram.alt` for a lexically arbitrary class, `iclass_member` = crc32 of concept and salt; levelled at
  `ICLASS_LEVEL`); portmanteau grams `A+B` (`_cumulate`, level fused, built into cells as one part, lost with either part);
  `stem_change` ({fn: [[v, v'], ...]}, recorded by `_stem_change` when a fused marker with no form still shows in its
  cells); `infix` ({fn}, `_infix`: a vowel-initial verb prefix goes after the stem's onset; cells carry two stem parts);
  `second` (`_second`: verbal clitics after the clause's first word); `incorp` (`_incorp`). Syncretic same-slot grams
  are kept half the time (before: the rarer always lost).
- *Sentences*: concord on adjective, demonstrative and the verb's third-person slot (`_verb_concord`); `cop_phrase`;
  Q, COP and REL grams before the lexical stand-ins (kept as fallbacks for older files); new `s_complement`, `s_topic`,
  `s_focus`, `s_applicative`, `s_reciprocal`, `s_antipassive`, `s_chain`, `s_incorp`, `s_voice` (two sentences, pivot
  marked by the article glossed PIV); infixes shown as k<um>ain / <PST>eat, stem changes as stem\PL, portmanteaus as one
  morph PL.GEN (`_portmanteaus`), second-position clitics moved in `clause`. A stored cell whose stem piece is not today's
  stem is shown unsegmented; reduplication is always a fresh copy of today's stem. Notes: Concord, Valence, Voice and
  pivot, Linking clauses, Topic and focus, Word shapes. Gram records carry `alt_ipa` for a second class form.
- `complexity`: free clause particles are left out of `mean_level`; new counts `portmanteaus`, `inflection_classes`.

**Grams** (`Gram`): `function` (PL, DU, DEF, INDEF, GEN, LOC, ABL, DAT, ACC, ERG, PAST, PERF, FUT, PROG, HAB, NEG, 1SG..3PL,
CLASS:n, ...), `form` (segments, may be empty when lost), `host` (N | V | NP | VP), `side` (pre | post, from typology),
`level` (0 free, 1 clitic, 2 affix, 3 fused, 4 lost), `source` (the lexical word and the path id), `born_kyr`, `history`.
Per-generation (`grammar.step`):
- **recruit**: with hazard `RECRUIT` x sociolinguistic factor, draw a path from `grammaticalization_paths.tsv` whose source
  concept the lexicon has and whose target function has no live gram; the gram starts at level 0 with the source word's form
  (and the source word stays a word: `go` keeps meaning go).
- **fuse**: hazard to move down one level rises with the gram's frequency and age, falls with the lect's adult-L2 share
  (PW-985). At level >= 2 the gram's form is attached to the paradigm exemplars (so sound change erodes it in place).
- **lose**: when the form is empty or its contrast collapsed (functional load), level 4; a periphrasis is recruited later by
  the normal recruit draw (the cycle).
- **analogy**: with a small hazard, level an alternation in an exemplar paradigm back to the stem form.
Start low: a proto-language starts with 1-3 grams, all at level 0-1, mostly PL/NEG/PAST, and recruits over time.

**Paradigm exemplars**: 4 nouns and 4 verbs per lect (drawn from high-frequency concepts) carry explicit inflected forms:
`forms[(function tuple)] -> Word_`. Sound change runs over them; `paradigm_table(lect)` renders them.

**Names through grammar**: `people_name(root, lect)` returns the land / people / person / language set using CLASS grams or
PL and a derivational pattern; `compound(a, b, lect)` orders by the head-direction feature; `place_name(base, lect, loc=True)`
adds the locative gram at its level.

**Measured complexity** (`complexity(lect) -> dict`): obligatory categories count, mean fusion level, allomorphy count from
the exemplars. Never stored as an input.

**Phase D (2026-11-08)**: far demonstrative DIST (X64), remote past REMPST (X65), completive/inceptive/iterative
(X66-X68), mirative (X69-X70, copies), honorific HON (X71), obviative OBV (X72), 'what' > Q (X73). Processes
`_polite` (`processes["polite"]` = {kind: plural|third, concept}; `aims["politeness"]`), `_compare`
(`processes["compare"]` follows the `comparative` aim) and `_dom` (`processes["dom"]`: ACC on animates only).
`PULL_BOOST` / `KEEP` give per-function multipliers on the aims' pull and on abandonment. Texts (fable, recipe, the
faith-myth hook) live in `texts.py`.

## 7b. Grammar notes and sample sentences (`sentences.py`, round 5)

A pass over one living lect's **json record** (not the engine objects), so it runs in `output.document` and equally on an
older languages.json (`tools/language/sketch.py` fills the fields when a file lacks them). It draws nothing: every form is a
word or gram the lect has, every order a typology feature.

- `View(lj)`: the typology, the live grams (one per function, as `Grammar.gram` picks: a bound one first, then the
  youngest), the paradigm cells, the noun classes (`classes`, see below; rebuilt from the CLASS grams' sources for older
  files), the lexicon and the inventory.
- **Words** (`Word`): a stem plus grams. A gram at level 0 is its own word beside its host (side from the gram); level 1 a
  clitic (`=`); level 2-3 an affix (`-`). Affixes stack inner-first by `grammar.SLOT_ORDER`, clitics outside them. Noun
  phrase grams (articles, case: host NP) go on the phrase's edge word on their side (an affix stays on the noun); free
  ones stand at that edge. A word whose bound grams make a stored paradigm cell takes the cell (the engine's own form with
  its alternations).
- **Joining** (`join`): at a morpheme or clitic boundary only, V+V takes a glide the lect has (j after front unrounded, w
  after rounded or back, else ʔ); a nasal before a stop or affricate takes the stop's place if the lect has that nasal.
- **Phrases**: Dem Num Adj N, each modifier on its side by its order feature (mixed/other: by head direction), mirrored
  after the noun (Greenberg's Universal 20); the possessor outermost (GN/NG), with the GEN gram unless the noun is kin and
  the lect has `alienability` yes; numeral classifiers (free CLASS grams) after the numeral; a free plural word is dropped
  after a numeral, an affix stays.
- **Clauses**: S, O and the verb complex by `word_order` (free: SOV or SVO by head direction, and the note says so); an
  oblique before the verb in OV lects, after the object in VO; ACC on the object (nom-acc) or ERG on the transitive subject
  (erg-abs) only when the gram exists; the subject's person gram on the verb when bound, and the subject pronoun dropped
  then if `pro_drop` is yes; TAM grams; NEG bound on the verb, or a free negator (the NEG gram's form, else NOT) placed by
  `negation` (clause-initial and clause-final ones move to the edge).
- **Constructions the engine tracks no gram for** (lexical sources from grammaticalization_paths.tsv): the polar question
  particle is the word for IF (as Russian *li* is both 'whether' and the question particle; `verb_morph`: its first syllable
  as a clitic on the verb); the copula (`copula` yes) is the word for HE OR SHE OR IT, else THAT (G056); relative clauses:
  NRel with THAT as relativizer (G055), RelN with the clause before the noun and no relativizer (or a free/clitic GEN as a
  linker, as Mandarin *de*), 'other' as a correlative with WHO ... THAT; predicative possession: 'have' by HAVE, else HOLD
  (glossed 'have'); 'locational' by LOC (or AT/IN) plus the copula; 'other' (Grambank marks neither) by 'with' (COM or WITH),
  the conjunctional type: the lane's pick.
- **Sentences** (`SENTENCES`, each skipped when a slot has none of its candidate concepts): a transitive clause; an
  intransitive with an adjective and a locative; the first TAM gram the lect has (PAST, RECPST, PERF, FUT, PROG, IPFV, HAB;
  none: unmarked, and the note says time is left to context); a yes/no question to 'you'; a 'what' question (fronted or in
  place by `wh_in_situ`); a negation with 'I'; 'my mother has a dog' (kin possession plus predicative possession); 'my
  brother sees two birds' (kin, numeral, plural); 'that man is a hunter' (demonstrative, copula); 'I know the woman who
  sings' (relative clause). Candidate lists name concepts the core lane is adding (HAVE, kin:mother ...) first where they
  fit, so new vocabulary is picked up without code changes.
- **Glossing**: Leipzig abbreviations (`ABBR`; PST.RCT, DIR, REP, AGT, CL*n*, CLF, ANIM, INAN are not in the Leipzig
  list and the pages explain them); lexical glosses lowercase with '.' joining a multi-word meaning; noun classes as M/F/N
  for sex genders, ANIM/INAN for animacy, CL*n* otherwise (and CL*n* whenever the noun's own class is missing and the
  engine falls back on another).

- **Grammar phase A sentences** (2026-11-08): 'the woman gives the child a fish' (`s_give`: DAT case or adposition if
  the lect has a DAT gram, else serial 'take X give R' if `serial_verbs` yes, else a double object); an imperative
  (`s_imperative`: the bare stem, no subject; no mood gram exists); a passive where a PASS gram lives (`s_passive`);
  serial 'take X come' = bring (`s_serial`, `serial_verbs` yes; one subject, the first verb carries the person marker;
  OV puts each object before its verb); reduplication (`s_redup`, from `processes.redup`: the copy made by
  `grammar.reduplicant`, glossed ITER/INTS/CONT; an exemplar verb takes its stored cell); split ergativity by person
  (`s_split`: 'the man sees me', ERG on the noun doer, ACC on the pronoun object; `flagging` decides ERG/ACC for every
  clause, so an aspect split shows ERG in the tense sentence when its TAM is PERF or PAST and ACC in the transitive one);
  inclusive 'we' (`s_clusive`, glosses 1PL.INCL and 1PL.EXCL). Notes added: Commands, Pronouns, Voice, Reduplication,
  Serial verbs, Giving (two objects), Numerals (`numeral_phrase`: decimal 11 'ten one', 30 'three ten' or 'ten three'
  by the numeral's noun order; vigesimal 30 'twenty ten', 40 'two twenty'), and the Case note names the split. The lect
  record carries `processes` (`{split?, redup?}`, only when non-empty). About +2.6 KB per living lect.

Output, per living lect (`enrich`): `sentences: [{id, en, w: [[form, gloss]...], ipa, roman, q?, note?}]` (`ipa`: the whole
sentence after joining, words separated by spaces, for `/api/speak?sentence=1`; `q`: 1 on a yes/no question) and
`grammar_notes: [{topic, text, ex: [[form line, gloss line, English]]}]` (Number, Case, Gender and noun classes, Tense and
aspect, Mood and evidentiality, Person agreement, Negation, Questions, Possession, Relative clauses, Copula). About 4 KB a
lect. `grammar_json` also stores the noun class system, `classes: {kind, classes: [[k, group, "CLASS:k"]]}`, so a reader
can tell which class a noun takes (`sentences.class_of`, the same rule as `grammar._class_for`).

`grammar.semantic_group` now puts kin terms and people nouns that concepts.tsv has no field for (BROTHER, FATHER, SON,
HUNTER, CHIEF ...; `_PERSONS`) in the person group; before, they fell into 'abstract' and took the abstract class.

## 8. Lects and the driver (`lect.py`, `history.py`)

**One lect per deme** at every time. A lect is a speech variety; a *language* is a cluster of lects (section 9). This keeps
tree and wave simple:
- **Tree**: when a deme buds (`demes.json` events `split_*`), the child deme's lect is `parent_lect.copy()` with a new id and
  `how="bud"`.
- **Wave**: when a rule fires in lect X at step t, it is offered to every lect Y whose contact with X at that frame is above
  `CONTACT_MIN`; Y adopts it with probability `p = sigmoid(contact_strength * prestige(X)/prestige(Y))` scaled by
  `WAVE_K`, only if `applies(rule, Y)`. Prestige = deme population (cells) x a ruler bonus when X's deme rules Y's. Lexical
  borrowing uses the same contact weights.
- **Proto-languages at START_KYR (20)**: among demes alive at the start frame, build the same-people contact graph with
  contact above `PROTO_LINK`; each connected component gets one proto-language (one draw), and every deme in it gets a copy
  of it (so a continuum starts as a continuum). Demes born after the start inherit by budding. Peoples whose first deme is
  born after the start get a proto-language at that birth (arrivals: elves, tritons, genasi) - record `how="arrival"`.
- **Steps**: for each frame interval [t0, t1] (kyr) and each living lect, `n = round((t0 - t1) * 1000 / generation_yr)`
  generations, each generation: `k_rules ~ Poisson(RATE_RULE * lect.rate)`, `lexicon.step`, `grammar.step`. `lect.rate` is
  drawn once per lect around 1 (lognormal sigma 0.3) and inherited with a small re-draw at budding. Exponent 1: no
  softening. Calibrate `RATE_RULE` by the horizon check (section 10), not by hand.
- **Shift**: triggers come from the stored history (see `inputs.md` for exact fields): substrate takeovers, conquests and
  rule (ruler deme R over ruled deme D), swamping (a deme fused into another, or a deme whose cells are mostly another
  people's), city mixing (settlements with several peoples). While a trigger holds, D's share of R's lect rises per
  generation by `SHIFT_K * prestige_ratio * rulers_per_head`; when it passes 0.5 the deme **shifts**: its lect becomes
  `R_lect.copy()` with `how="shift"`, `substrate=old_lect_id`, and the substrate transfer runs: local-concept words
  (landscape, local plants and animals, place and river names) are kept from the old lect; the new inventory is heard
  through the old profile+inventory for an accent (`hear_word` over the whole lexicon with a mild weight, so only the
  segments the old lect lacked are substituted); one or two typology features are calqued from the old lect. The shares
  during the bilingual years are stored on the deme record for the workbench.
- **Food routes**: for each crop or animal arrival at deme D from deme S at kyr t (from the spread history), if D's lexicon
  lacks the concept, `borrow` S's word with the route note; if S's lect also lacks it, S coins it first (derive or compound).
  Hops chain by themselves; the etymology is the route. One source of truth (2026-11-04): a hop's route is read from the
  donor word's own etymology (the latest route event in its chain, through renewed loans; `route_key_of`), and each hop in
  the output says whether the receiver's word still holds it (`now`: kept | replaced | lost, `by`: the step that replaced
  it, from the receiver's etymology; `history.hop_status`).
- **Death**: a deme's end ends its lect (`died_kyr`); names it gave to places stay in the place table.

**Batch per frame interval, never loop per generation.** The last 20 kyr is 41 frames at 0.5 kyr (`inputs.md` §0); 452
demes are alive at 20 kyr, 573 now; generations per interval range from ~1 (dragons, 430 yr) to ~86 (aarakocra, 5.8 yr),
~378,000 deme-generations in all. So for each interval and lect: `n = Δt / generation_yr` (fractional is fine),
`k_rules ~ Poisson(n * RATE_RULE * lect.rate)`, per-word replacement `~ Bernoulli(1 - (1 - h_word)^n)` vectorized over the
lexicon, gram events likewise `Poisson(n * hazard)`. Apply the drawn events in sequence inside the interval. Rules apply
only when drawn; words are tuples.

**Mapping the stored history to engine events** (all from `inputs.md`; nothing at deme level is stored, so derive):
- *Deme population* per frame: cells from `layers/demes_all.bin` × presence share × cell area × the people's density
  (`meta.lineages[].demography.density`); good enough for prestige and swamping.
- *Prestige* of a deme: population, plus a bonus when its people knows `cities`, `writing`, `law` at that time
  (`meta.techtree.known[people][tech] = [kyr_ago, how, from]`), plus the towns and cities on its cells (settlements.json
  sites by `cell` and frame).
- *Elite rule* triggers: (a) `meta.contacts.incursions` of kind `displacement` and `settled_among`: locate the `by` deme and
  the `over` deme at that `lat/lon` and frame through demes_all; if the `by` deme's prestige exceeds the `over` deme's, the
  `over` deme is under elite rule by `by` from `ago_kyr` for `span_kyr` + a tail; otherwise it is *swamping* in the other
  direction (a small newcomer among a large host shifts to the host); (b) settlement `holders` changes: a site changing hands
  to a new people is a local takeover for the deme holding that cell; count takeovers per (ruler deme, ruled deme) per frame
  and treat ≥ 2 sites or a city as rule. Record every trigger with its source so the workbench can show "why".
- *City mixing*: cities whose `who` has 2+ peoples (61 of 94 in a24559): the demes present in that city's cell form a
  contact edge with high weight and a raised adult-L2 share for the city-holding deme's lect (feeds PW-985 rates).
- *Trade languages*: pairs in contact for a long time (`pairs[].frames`) with high `shared` raise the larger lect's L2
  share in the smaller deme; shift only after `TRADE_SHIFT_KYR` of continuous contact.
- *Adult-L2 share* of a deme (PW-985 input): `shared` cells with other-people demes / own cells, plus the city mixing above.
- *Crop and animal arrival per deme*: first frame where any of the deme's cells has the crop bit set in `layers/crop_known`
  (uint64, bit = stock `bit`) / `animal_known`; donor = the co-present or bordering deme (pairs, then the cell graph) that
  had it the frame before; origin demes from `meta.crops.stocks[id].tamed` (lat/lon, frame).
- *Rivers*: build river ids once from the world's `downstream` and `flow` layers (`planet/highlights.py::_river_course`,
  `_basin_cells`): a river = the cells draining to one mouth with flow above a floor; a deme "lives on" the rivers crossing
  its cells. Lakes from connected `lake` cells. Name the largest river and lake per deme and the landmass part.
- *Arrivals' deme parents are wrong* (gnomes, elves, tritons): when a lineage's `origin == "arrival"`, its first demes get a
  fresh proto-language (`how="arrival"`), never the deme parent's lect.
- *Peoples with no demes* (half-elves, half-orcs, genasi, tieflings, aasimar) get no lects tonight; say so in the output.

Complexity budget: keep the whole pass under ~10 minutes on a24559 single-threaded; if it needs more, parallelize over
independent lects within an interval with `planet.parallel`, never across intervals (wave spread couples them).

## 9. Languages, families and the scholars' tree (`families.py`)

- `cognate_share(a, b, concepts)`: share of concepts whose forms are "recognisably cognate": normalized edit distance over
  percept vectors below a threshold **or** a shared etymology root (truth). Report both the truth and the blind measure.
- **Dialect vs language**: lects cluster into a language when pairwise blind cognate share on the core list > `LANG_SHARE`
  (start 0.7) and phonological distance is small; a language is named by its largest deme's glossonym.
- **True tree**: the lect parent links (bud and shift), with shift edges marked.
- **Scholars' tree**: distance matrix of blind cognate shares over the living lects, UPGMA; a link is "reconstructable" when
  the share is above chance (`CHANCE_SHARE`, measured by shuffling); the horizon is the oldest true split that the scholars'
  tree still recovers. This is the 6-10 kyr check, and the calibration target for `RATE_RULE` and `BASE_REPLACE`.
- **Split horizon** (`horizon`, calibration.md): splits recovered by a scholars' clade (Jaccard >= 0.8) under the strict
  cognate test, in 2-kyr windows stepped 1 kyr; the horizon is the start of the first **two consecutive** scored windows
  (>= 3 splits; a sparser window widens by 0.5 kyr per side up to 1 kyr first, `recovery_curve`, `widened_kyr`) under
  half recovered (`horizon_read`; `censored` when it never happens, a lower bound), with a smoothed read
  (split-weighted moving average over 3 windows) and the former single-window read beside it. `groups` runs the measure
  per people group (checks: human, long-lived = generation >= 60 yr, dwarves, elves, dragons).

## 10. Checks (`checks.py`)

Each returns `{"name", "value", "target", "pass", "note"}`:
1. proto inventory sizes and segment frequencies vs PHOIBLE (sizes within the interquartile range for 70% of protos; top-20
   segments overlap);
2. sister lects recognisable, distant not (STRICT cognate share, owner 11-04: siblings > 0.5, cross-family < 0.15);
3. horizon between 6 and 10 kyr for human lects, and the long-lived peoples' longer (or censored: still recovered as far
   back as their splits go);
4. at least a few living lects differ in family from their deme's descent (shift count > 0);
5. long-generation species' lects changed measurably less (rules applied per kyr vs humans);
6. empire and trade-hub lects simpler, isolated small lects richer (measured complexity by category; across seeds later).
7. living human-voiced lects' inventory sizes vs PHOIBLE (`living_sizes`): p5/q1/median/q3/p95 of consonant and vowel
   counts beside PHOIBLE's (12/17/21/27/42 C, 3/6/9/12/22 V); pass when the medians are within 3 C / 2 V, the quartiles
   within 4 C / 3 V, and the share above PHOIBLE's p95 is 0.3-15% for consonants (a rare tail exists) and under 15% for
   vowels;
8. living human-voiced lects' segment frequencies vs PHOIBLE (`living_segments`): top-20 overlap >= 12; p t k m n i a u each
   in at least half PHOIBLE's share of languages; no monoculture (no segment in over half the lects and over 2.5x PHOIBLE's
   share: ʒ, ɹ, the breathy stops). The segments in over half the lects outside PHOIBLE's top 12 are listed, not judged
   (PHOIBLE itself has e, ŋ, b, o, ɡ, h in over half its languages).
9. overused segments over every living lect (`living_overuse`, round 5): no segment in over 10% of living lects and over
   3x PHOIBLE's share; a lect does not count a segment its own voice profile favours (make_cost product below 1 over the
   segment's keys) or a sound humans cannot make. Catches what check 8 cannot see (it reads human-voiced lects only).

## 11. Output (`output.py`, `languages.json`)

```
{ "format": "procgen-languages/1" (in memory; on disk /2, below), "run": "a24559", "seed": ..., "start_kyr": 20,
  "profiles": { <lineage id>: {source, modality, articulators, make_cost, hear, notes} },
  "lects": [ { "id", "deme", "people", "parent", "how" (proto|bud|shift|arrival), "substrate", "born_kyr", "died_kyr",
               "rate", "language", "family_true", "family_scholars",
               "inventory": {"consonants": [ipa], "vowels": [ipa], "tones": [...], "shapes": {...},
                             "allophones": [{"ipa", "of" (phoneme ipa | null), "test", "where"}]},
               "typology": {...}, "grams": [{function, form_ipa, form_roman, level, side, source, born_kyr}],
               "classes": {kind, classes: [[k, group, "CLASS:k"]]},                       # when the lect has noun classes
               "sentences": [{id, en, w: [[form, gloss]], ipa, roman, q, note}],          # living lects (section 7b)
               "grammar_notes": [{topic, text, ex: [[form, gloss, English]]}],             # living lects (section 7b)
               "paradigms": {"noun": {"lemma", "gloss", "cells": {"SG.NOM": {"ipa","roman"}, ...}}, "verb": {...}},
               "lexicon": { concept: {"ipa", "roman", "pos", "freq", "etym": <node id>, "roots": [root id, ...],
                                         "etym_roots": [root id, ...]} },   # etym_roots: round 5, 2026-11-07   # full for living lects, core list only for dead
               "changes": [{kyr, rule, cause, origin_lect (null if own)}],
               "complexity": {...},
               "shares_history": [[kyr, {lect_id: share}]] } ],
  "names": { "peoples": { people: { "endonym": {ipa, roman, gloss, pattern, lect}, "glossonym": {...},
                                   "set": {land, people, person, language},
                                   "exonyms": [{by_people, by_lect, ipa, roman, gloss, pattern, basis, era_kyr, relay: [...]}] } },
             "demes": { deme_id: { "name": {...}, "places": [{kind, ipa, roman, gloss, lect, kyr, substrate_of}] } },
             "common": { "lect": id, "why": "...", "exonyms": {...} } },
  "shifts": [ {deme, kyr, from_lect, to_lect, trigger, ruler_deme, substrate_words: [concept...], accent: [[from_ipa, to_ipa]...]} ],
  "food_routes": [ {concept, origin_deme, hops: [{deme, lect, kyr, ipa, roman, from_deme, changes: [...], now, by}]} ],
  "etym_nodes": [ [parent | -1, kyr, lect, process, ipa, gloss | 0(, note)] ],
  "roots": { root id (every id in any lexicon entry's roots or etym_roots): {"node": etym node of the root's first step (shared by its whole family) | null, "lect", "kyr",
                       "concept", "gloss", "ipa", "pos"} },   # every root a stored word names; a compound's modifier root
                                                             # met only as a modifier has node/kyr/ipa null
  "families": { "true": tree, "scholars": tree, "horizon_kyr": x },
  "checks": [ ... ],
  "romanization": "house/1" }
```

That is the doc **in memory** (format /1's shape), which every reader works on. **On disk** (procgen-languages/2, finish
lane 2026-11-07) `output.save` packs it into three files, and `output.load(path, sidecars=True | False | ("etym",))` /
`LangCore.expand(main, {etym, snapshots})` in viewer/langcore.js unpack them back to exactly that doc (`expand(*pack(doc))
== doc`; tests/test_language_format.py checks both expanders). A /1 file still loads as it is.

```
languages.json            the main file: everything above except etym_nodes, roots and the lects' snapshots, plus
  "format": "procgen-languages/2", "sidecars": {"etym": "-etym", "snapshots": "-snapshots"},
  "lect_ids": [lect id ...]                       # interned lect ids (lects, etymology nodes, roots)
  "concepts": [[concept, gloss, pos] ...]         # every concept of a lexicon or a root; pos is the default for a word
  lects[i]."lexicon": {"c": [concept index ...], "ipa": [...], "roman": [...], "freq": [...],
                       "pos": sparse {word index: pos} where it differs from the concept's, "x": sparse extra keys}
languages-etym.json
  "root_ids": {"lect": [lect index], "concept": [concept index], "kyr": [text after "@" | null], "odd": sparse {i: id}}
                                                  # root id i = f"{lect}:{concept}" (+ "@kyr"); ids that do not parse whole
  "processes": [process ...], "notes": [note ...] # interned
  "nodes": {"up": [i - parent, 0 = none], "kyr": [...], "lect": [lect index | -1 = the parent's],
            "process": [index], "ipa": [ipa | 0 = the parent's | 1 = the first word (lect, then lexicon order) whose
            etym is this node], "gloss": [gloss | 0 = the parent's], "note": sparse {i: note index}}
  "roots": {"node": [...], "lect": [lect index | -1 = the id's], "kyr": [kyr | 0 = its node's], "ipa": [ipa | 0 = its
            node's], "absent": [root index with no table entry], "other": sparse {i: {concept, gloss, pos} not the
            concept table's}}
  "lexicons": {lect id: {"etym": [node], "roots": [[root index]], "er": sparse {word index: [root index]} where
               etym_roots differs from roots, "no_er": [word index without etym_roots]}}
languages-snapshots.json  {"format", "lects": {lect id: snapshots (section 8's delta encoding, unchanged)}}
```

A sparse column is `{"i": [gaps between successive indices], "v": [values]}`. The main file alone carries everything the
brief, names and sentences need (`load(path, sidecars=False)` leaves the words' etym / roots / etym_roots out); the viewer
fetches the two sidecars beside it in parallel and expands. Sizes on a24559 (round 5 vocabulary, 712 words per living
lect): calibration.md "Final run".

Full lexicons for living lects only; dead lects keep the core 100 plus names, and past ~60 MB unpacked their snapshots are
thinned to every 4th (`output.thin_dead`). The brief gets a per-people summary; the workbench loads the whole file.

**A root's family** (for the viewer's word trace and a language-page generator): the words whose `roots[0]` is the root
id, in one lect or across a family (`family_true`); `roots[1:]` are a compound's other roots (list a compound under each
for a Pokorny-style entry). The root's proto form and meaning are `doc.roots[id]` (`ipa`, `gloss`, `lect`, `kyr`); a
word's path from it is its etymology chain (`etym_steps`), whose first step is the root's.

## 12. Romanization (`romanize.py`)

`data/romanization.tsv`: IPA -> house spelling, deterministic, ASCII first, digraphs next, diacritics last. Rulings: ŋ
`ng` (`n-g` where n+g meet), ʃ `sh`, tʃ `ch`, ʒ `zh`, dʒ `j`, θ `th`, ð `dh`, x `kh`, ɣ `gh`, **uvulars get their own spelling**:
q for q, `qh` for χ (as in several Caucasian romanizations), `gq` or `ġ` for ʁ, ʔ `'`, long vowel doubled, tone as acute/grave,
clicks as the letters ǀ ǁ ǃ ǂ (U+01C0-01C3, not ASCII `| || !`; a long click doubles, ǃǃ), ejectives `'` after the letter,
aspiration `h` only when contrastive in that lect, ə `e` with a note or `ë` when it contrasts with e. Non-human percepts take
ASCII marks (`NH_MARKS`: growl rh, purr vr, second voice wh, sub-bass mh, ultra ih; purr is no longer the trill's rr).
Proper names capitalized; a multi-word name capitalizes each word and joins a one- or two-letter particle with a hyphen
(`title_words`: *Opa'i-e*, *E-Iva*). The tap ɾ is r, the trill rr, the approximant ɹ ř (2026-11-04). Book mode spells the
IPA-kept affricates with their stop's letter (ɟʝ gy, cç ky; the table's `book` column) and ɹ as r.

**One lect, one orthography** (names lane, 2026-11-08; names-spelling-gaps.md recs 2-7). `Orthography(segments, allophones,
counts)` is a lect's spelling in both registers, used by `output.Speller`, `names.py` and the sketch:
- it is built from the lect's **phonemes**: an allophone is spelled as its phoneme (Kunrei, Spanish *b d g*), an inserted ʔ
  is not written; the IPA keeps the phonetics, and allophones no longer change the contrast set;
- **no IPA marks** in either register: a shifted vowel (ɨ̠ e̞ ɑ̟) is its base's letter unless the lect has both, then a Latin
  breve (raised/advanced) or macron below (lowered/retracted) ("shift"); a dental beside its alveolar takes a breve below
  (t̮ d̮ n̮ l̮; macron below is taken by ḻ = ɻ);
- **aspiration, pinyin-style**: a lect that contrasts aspiration only on voiceless stops/affricates and has no voiced stops
  writes the plain ones b d g j dz and the aspirates p t k ch ts ("pinyin"), so its fricatives stay sh th kh; only a lect with
  voiced stops too (Indic three-way) writes h and switches the fricatives to š þ x ("aspiration");
- **book diacritics planned once per lect** (`book_folds`): a diacritic letter whose ASCII fold merges none of the lect's
  phonemes is always folded; of the rest the `BOOK_DIACRITIC_BUDGET` (2) commonest by token count keep their marks and the
  others fold everywhere (`Orthography.lossy`, named on the sketch's orthography line); every long vowel is doubled. The
  per-word cap and the once-per-word doubled vowel are gone: a phoneme is spelled one way in every word of a lect;
- **non-human marks in book**: one per sound, written once after a run of sounds that carry it, and a growled r is rrh.

Measured on a24559 (627 living lects, 235,255 words, old code vs new on the same IPA): full spellings with an IPA mark 12.1%
-> 0; book words whose spelling depended on position 13,151 (+5,121 by vowel length) -> 0; ASCII click marks in full
spellings 618 -> 0; lects whose one aspirate flipped the fricatives 55 -> 46 (8 now pinyin); book homograph sets 6,266 ->
5,990 (tone-only sets dominate); book diacritic letters per word 0.25 -> 0.28 (two kept per lect, not one per word); 246 lects
fold at least one contrastive diacritic (486 folds).

## 13. Workbench and brief

- `viewer/lineages.html` gains a **Languages** tab (own JS file `viewer/langtab.js` like `religiontab.js`): a people picker ->
  its languages, with the name stack and etymologies; a cognate table (rows: 15 core concepts; columns: the people's living
  lects plus one distant lect); one paradigm; the food word route as a hop list; the shift cases; a family tree (true, with
  the scholars' tree beside it and the horizon marked). IPA and house spelling side by side.
- `brief.py` gains a short language section per people: the headword (romanized endonym), the glossonym, two exonyms, three
  etymologies, and the food words with their route.

### 13b. Personal and settlement names (`personal.py`, names lane 2026-11-08)

`names.personal[lect]` (every living lect): `{tradition: {given, byname, order, origin, changed?, themes?}, given: [{roman,
ipa, gloss, age: old|new, opaque, etym}], bynames: [{roman, ipa, gloss, kind, etym}]}`; `names.demes[d].settlements`: up to
three standing sites of the deme (settlements.json, sites in the deme's cells now, largest first): `{site, tier, pop, ipa,
roman, gloss, lect, named_by, kyr, substrate_of, pattern (P2 or null), tautology, plain}`.

- **Traditions** are drawn at each proto and inherited down the lect tree; each lect redraws one field with chance `DRIFT`
  (0.12). Given names: `dithematic` (closed pools of 8 + 6 theme concepts fixed where the tradition began), `phrase`
  (subject + verb in the lect's order, Yoruba-like), `single`. Bynames: `patronymic`/`matronymic` (parent's name + GEN gram
  + SON/DAUGHTER, fused when GEN is bound and the lect head-final; with no GEN, as on a24559, the kin word compounds with
  the parent's name), `epithet`, `clan` (family first or last).
- **Old names**: three per lect are coined in the tradition's origin lect and carried down: a theme whose root the lect
  still has (`etym_roots`) takes its reflex, a replaced one stays as the lect hears the old form (opaque), and an old name
  is clipped toward two syllables with a chance that grows with age (`OPAQUE_KYR`, `OPAQUE_CAP`). **Approximation**: names
  are not replayed through each lect's own rule history (the rule objects are not kept); the boundary sound changes a real
  compound name undergoes (Wilhelm > William) are therefore missing. Three new names per lect are coined from today's words.
- **Settlements**: a generic from the namer's words (FORD/BRIDGE on a river cell, else by tier: TOWN, MARKET, FENCE
  'enclosure', VILLAGE, HOUSE, FIELD, WALL), eroded to one syllable (a suffix) after `SUFFIX_KYR`; a specific (a founder's
  given name in the bound GEN, Kraków-style; else an adjective). A site founded by a people whose lect the current lect does
  not descend from keeps the founder lect's name as heard (P2), and with chance `SUBSTRATE_TAUTOLOGY` (only when the generic's
  root differs from the newcomers' own, so they no longer understand it) the newcomers add their own generic: a tautology
  (River Avon). On a24559 (final run): 1430 towns in 488 demes, 970 kept from another people (P2), 213 tautologies; 920 of
  1875 old given names opaque; 103 of 625 lects changed their tradition.
- **E10 faith endonyms** (`names.high_god`): a people whose main deme's culture has a living high god (gods.json,
  cultures.json beside the run) may call itself 'the people of the <domain> god' (weight `FAITH_W`, by the god's
  individuation). No polity or state data reaches the language pass yet, so E11 confederations and X6 dynasty exonyms are
  still missing.
- Shown in the viewer's Names tab (with play buttons) and on the sketch pages ("Names of people and places").

### 13c. Faiths: god names, liturgies, learned loans (`faiths.py`, faiths & contact pass 3, 2026-11-08)

- **Input.** `inputs.Run.gods_doc()`: the run's gods.json; one from before the faith records (procgen-gods/1, as
  a24559's) is re-derived in memory with `planet.lineages.gods.derive` (read-only, ~2 min). `faiths.Plan` reads it once
  before the history: each living deme's culture (cultures.json `deme_culture`), its faith (`faith_now`) and its first
  `GODS_PER_CULTURE` living beings (high god first, then devotion).
- **God names are lexicon words** `name:god:<key>` (pos NAME), key = the root of the being's `parent` chain. The line
  takes the god at its first `converted` copy up the chain (a conversion: the name is borrowed from a lect that has it,
  most in contact first), else at the root's birth (a coinage; older than 20 kyr: in the proto-language, so daughters
  inherit one word). The coinage (`coin_name`) is a kin or rank title on the domain word ('sky-father', 'lord of the
  sea'), an agent noun from the domain's verb ('the one who burns'), a kenning ('eye of the sky') or the domain word
  itself; never the same form as another god's name in the lect. Every step in the chain is an ordinary etymology step
  (`name:god`, gloss = the name's English). Sound change, inheritance and shift (NAME words always kept as substrate)
  act on it like on any word; `lexicon.step` skips NAME words; instead `faiths.step` renames a name by an epithet at
  `NAME_HALF_KYR` per reference generation (the old name avoided; the note keeps it). `lexicon.stats` and the
  borrowability check leave NAME words out.
- **Liturgy.** A faith whose seat people (the largest holder deme of its founding culture, else of any holder) knows
  `temples` gets a canon at min(founding, temples), older than `LIT_MIN_KYR`: the seat's ancestor lect then is copied
  (`lit<faith>`, `how="liturgy"`, never stepped, not in `lects`). From the canon on, the lects of the holders' ancestor
  demes take learned loans of the SACRED words from it (`LEARNED_RATE` per generation; step `borrow:lit<faith>`, note
  "learned, from the liturgy of ..."). At the end each living holder lect gets `systems.learned` {concept: [the
  liturgy's form as the lect hears it, doublet | synonym | only, the liturgy's form]}.
- **Document.** `faiths` {faith id: {name, core, how, parent, founded_kyr, peoples, holders: [lect], gods: [{key,
  domain, label, high, names: [[lect, ipa, roman, gloss, coined [kyr, lect]]], plain}], liturgy: {lect_from, deme, kyr,
  people, words {concept: [ipa, roman]}, gods {key: [ipa, roman, gloss]}, formulas: [sentence records as in 7b]}}}.
  Two names with the same `coined` are one word (cognates or a loan). The formulas (invocation, praise, petition) are
  built with sentences.py on the frozen lect. The sketch's "Gods and liturgy" section (`sketch.faith_section`) shows
  them.
- **New concepts** PRIEST and TEMPLE come with the `temples` technology (TECH_CONCEPT), with recipes 'god person',
  'god house', 'one who prays', 'place of prayer'.
- **E10 faith endonyms** use the god's own name when the lect has one ('the people of <name>').

### 13d. Segment borrowing (`lexicon.borrow`, contact-gaps 3d)

A contact loan under intensity above `SEG_BORROW_MIN` keeps each donor consonant the receiver lacks with chance
`SEG_BORROW_K` x (I - min) / (1 - min) when the receiver's voice hears and makes it, at most `SEG_BORROW_MAX` per line;
logged in `systems.seg_loans` [ipa, donor, kyr, concept]. The driver (`history.take_segments`) adds it to the line's
`base_segs` (so `cap_inventory`'s rare-unit fold leaves it) and re-reads the inventory (`lect._sync_inventory`).

## 14. Work split for tonight

| Builder | Deliverables | Starts |
| --- | --- | --- |
| A percepts + profiles + romanize | `percepts.py`, `data/symbols.tsv`, `profiles.py`, `data/voice_profiles.toml`, `spec.parse_voice` hook, `romanize.py`, `data/romanization.tsv`, tests, `voice-profiles.md` (sourced reasoning) | now |
| B rules | `rules.py`, `DEMO_RULES`, catalogue parser over `data/sound_changes.tsv`, functional load, tests | now (code against section 2; swap in A's module when it lands) |
| C inventory + lexicon | `inventory.py`, `lexicon.py`, concept list assembly, tests | now (same) |
| D grammar | `grammar.py`, typology draw and drift, grams, paradigms, names-through-grammar helpers, tests | now (same) |
| E driver + families + checks + output + CLI | `lect.py`, `history.py`, `families.py`, `checks.py`, `output.py`, `run.py`, tests on a24559 | now (scaffold on inputs.md; integrate as modules land) |
| F names + viewer + brief | `names.py`, `viewer/langtab.js`, brief section | after E's first `languages.json` |

Integration order: A -> B, C, D -> E -> F. Each builder writes not-slow tests under `tests/test_language_*.py` and reports
judgement calls in their report (not on the board; the lane writes the inbox drafts).
