# For Daniel: decisions, oddities and demos set aside

## Grammar phase A (branch lang-gram-a, 2026-11-07)

Reasonable defaults taken while you were away. Each lives in one constant in `planet/language/grammar.py`.

- **Split ergativity kind**: by person (pronouns accusative, nouns ergative) 60%, by aspect (ergative in the perfective
  or past) 40%. `SPLIT_KIND`.
- **Inclusive 'we' source**: 'we + you' compound 45%, 'I + you' 15%, a root of its own 40%. Plain WE stays as the
  exclusive. `INCLUSIVE_FROM`.
- **Reduplication meaning and shape**: iterative 45%, intensive 20%, continuous 35%; CV copy 65% (prefixed 3 in 4),
  whole stem 35%. `REDUP`, `REDUP_SHAPE`.
- **Counting base words** at proto time: decimal 20 = 'two ten'; vigesimal 100 = 'five twenty' (20 = 'one person' half
  the time); 'other' read as quinary-decimal, 6-9 = 'five one' ... 'five four'. `NUMERAL_WORDS`.
- **Person paradigm**: each other pronoun joins a binding person marker with 60-85% (3SG lowest); gap fill 0.004 per
  generation. `PERSON_JOIN`, `PERSON_FILL`.
- **Degrammaticalization**: 1/50 of the fusion hazard, x3 for NP-edge markers, x3 for the last survivor of a lost
  paradigm. `DEGRAM`, `DEGRAM_EDGE`, `DEGRAM_ORPHAN`.
- **Alignment shown as neutral when no accusative or ergative marker exists** (before, the aim showed through: 16% of
  lects claimed ergativity with no ergative anywhere). This is WALS 98A's reading (flagging). Head-marked ergativity
  (Mayan-style, on the verb) is not modelled, so it cannot be claimed.

**Measured** (living lects of a24559, scratch pass, before = same code base without phase A, same vocabulary):
accusative gram 10% > 40% of lects (49% of lects with case; Grambank GB408 44%); ergative 0% > 15% (17% of case
lects; GB409 22%); dual 5% > 10% (GB043 7.7%); ablative 0% > 10%; allative 5% > 9%; witnessed evidential 5% > 13%;
inclusive 'we' 0% > 54% (GB028 52.5%); verbal reduplication built in 74% (GB158 73%); one-of-six person paradigms
60% > 12% of agreeing lects; shown alignment neutral 52% (WALS 98A about 52%).

**Decision: verb synthesis (WALS 22A), measured, not tuned.** Bound verb categories per living lect (tense, aspect,
mood/evidential, negation, voice/valence, person; affix or fused):

| categories | 0-1 | 2-3 | 4-5 | 6-7 | 8+ |
| --- | --- | --- | --- | --- | --- |
| our lects (after phase A) | 59% | 28% | 12% | 1% | 0% |
| WALS 22A (145 languages, from memory, about) | 3% | 17% | 36% | 21% | 23% |

Our languages are far more isolating than the world's. Cause: fusion is slow against 20 kyr with a median adult-learner
share of 0.54 (`FUSE`, `social_factors`), and the categories list is short (no object agreement or mood yet: phase B
adds some). My recommendation: wait for phase B (object agreement, mood) and re-measure; if 0-1 is still above ~25%,
raise `FUSE` from 0.012 toward 0.02 and check the L2 exponent on fusion ((1 - l2)^2), rather than adding categories by
hand. Your call.

**Odd or worth a look:**
- Passive is already 45% of lects before and after (GET and BECOME from round 5 feed it; G060 adds a few). The brief
  said 20-40%; WALS 107A has about 44% with a passive, so I left it.
- 77% of ergatives come from the agentive 'near, with' path (X22), because a lexical source is always at hand while the
  gram sources (instrumental, ablative, locative) need a live gram. Plausible but lopsided; lower X22's weight if you
  want more case-syncretic ergatives.
- No genitive gram ever arises (0%): no lexical source in the vocabulary (G067 needs BELONG). Phase B item.
- Degrammaticalization fires about 1.6 times per lect over 20 kyr in the isolated harness (61% of lects have at least
  one), mostly articles, accusatives and plurals. At the asked 1/50 rate, but probably more than real (Norde collects a
  few dozen cases). `DEGRAM` is one constant.
- Split ergativity is shown in 7% of lects (6% by person, 1% by aspect); aspect needs a live perfect or past.
- The lexicon's own compound recipes build 6-9 as 'five + one' ... and 10 as 'hand + two' in lects whose counting base
  is decimal (seen in d21). Quinary-built digits in a decimal system are real (many languages), but it ignores the base
  feature; the recipes in data/compounds.tsv could be gated on `numeral_base` later.
