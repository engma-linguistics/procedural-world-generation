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
  x a lognormal pull (sigma `SIZE_ANCHOR` 0.2 in ln n) toward the line's own proto count, clamped to [0.1, 2]. A context-free
  rule removes what it rewrites; a conditioned one is a split.
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
- **replacement**: each word's hazard = `BASE_REPLACE * rate_by_freq[freq_class]` per generation, calibrated so Swadesh-100
  retention is about 86% per millennium at human generation length (Pagel 2007 shape: frequent words 10x slower than rare).
  The replacement source is drawn: derive (40%), compound (25%), colexification shift from a CLICS neighbour (20%), borrow
  from a contact lect if one is in contact (10%), taboo (5%, animals and dangerous concepts only).
- **elaboration**: when a concept's weight in the deme's life passes a threshold (herder: milk words; coast: fish words;
  farmer: crop-stage words; from `inputs.md` niches), split it with a derived or compound word.
- **borrowing on arrival**: `borrow(word, from_lect, to_lect, kyr, route_note)` = `hear_word` + repair + an `EtymStep`
  `borrow:<lect>`; the result is a normal word thereafter.

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
  Hops chain by themselves; the etymology is the route.
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

## 10. Checks (`checks.py`)

Each returns `{"name", "value", "target", "pass", "note"}`:
1. proto inventory sizes and segment frequencies vs PHOIBLE (sizes within the interquartile range for 70% of protos; top-20
   segments overlap);
2. sister lects recognisable, distant not (blind cognate share: siblings > 0.5, cross-family < 0.15);
3. horizon between 6 and 10 kyr;
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

## 11. Output (`output.py`, `languages.json`)

```
{ "format": "procgen-languages/1", "run": "a24559", "seed": ..., "start_kyr": 20,
  "profiles": { <lineage id>: {source, modality, articulators, make_cost, hear, notes} },
  "lects": [ { "id", "deme", "people", "parent", "how" (proto|bud|shift|arrival), "substrate", "born_kyr", "died_kyr",
               "rate", "language", "family_true", "family_scholars",
               "inventory": {"consonants": [ipa], "vowels": [ipa], "tones": [...], "shapes": {...}},
               "typology": {...}, "grams": [{function, form_ipa, form_roman, level, side, source, born_kyr}],
               "paradigms": {"noun": {"lemma", "gloss", "cells": {"SG.NOM": {"ipa","roman"}, ...}}, "verb": {...}},
               "lexicon": { concept: {"ipa", "roman", "pos", "etym": [EtymStep...] } },   # full for living lects, core list only for dead
               "changes": [{kyr, rule, cause, origin_lect (null if own)}],
               "complexity": {...},
               "shares_history": [[kyr, {lect_id: share}]] } ],
  "names": { "peoples": { people: { "endonym": {ipa, roman, gloss, pattern, lect}, "glossonym": {...},
                                   "set": {land, people, person, language},
                                   "exonyms": [{by_people, by_lect, ipa, roman, gloss, pattern, basis, era_kyr, relay: [...]}] } },
             "demes": { deme_id: { "name": {...}, "places": [{kind, ipa, roman, gloss, lect, kyr, substrate_of}] } },
             "common": { "lect": id, "why": "...", "exonyms": {...} } },
  "shifts": [ {deme, kyr, from_lect, to_lect, trigger, ruler_deme, substrate_words: [concept...], accent: [[from_ipa, to_ipa]...]} ],
  "food_routes": [ {concept, origin_deme, hops: [{deme, lect, kyr, ipa, roman, from_deme, changes: [...]}]} ],
  "families": { "true": tree, "scholars": tree, "horizon_kyr": x },
  "checks": [ ... ],
  "romanization": "house/1" }
```

Keep the file under ~40 MB: full lexicons for living lects only; dead lects keep the core 100 plus names. The brief gets a
per-people summary; the workbench loads the whole file.

## 12. Romanization (`romanize.py`)

`data/romanization.tsv`: IPA -> house spelling, deterministic, ASCII first, digraphs next, diacritics last. Rulings: ŋ
`ng` (`n'g` where n+g meet), ʃ `sh`, tʃ `ch`, ʒ `zh`, dʒ `j`, θ `th`, ð `dh`, x `kh`, ɣ `gh`, **uvulars get their own spelling**:
q for q, `qh` for χ (as in several Caucasian romanizations), `gq` or `ġ` for ʁ (pick one, document the convention source),
ʔ `'`, long vowel doubled, tone as acute/grave, clicks `!` `|` `ǁ`, ejectives `'` after the letter, aspiration `h` only when
contrastive in that lect, ə `e` with a note or `ë` when it contrasts with e. Non-human percepts take the house symbol from
`symbols.tsv`. `romanize(ipa: str, lect: Lect | None) -> str` (the lect is needed for contrast-dependent choices).
Proper names capitalized; hyphen only where a digraph would mislead.

## 13. Workbench and brief

- `viewer/lineages.html` gains a **Languages** tab (own JS file `viewer/langtab.js` like `religiontab.js`): a people picker ->
  its languages, with the name stack and etymologies; a cognate table (rows: 15 core concepts; columns: the people's living
  lects plus one distant lect); one paradigm; the food word route as a hop list; the shift cases; a family tree (true, with
  the scholars' tree beside it and the horizon marked). IPA and house spelling side by side.
- `brief.py` gains a short language section per people: the headword (romanized endonym), the glossonym, two exonyms, three
  etymologies, and the food words with their route.

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
