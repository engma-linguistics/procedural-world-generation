---
id: PW-1538
title: "Decisions: language defaults to confirm, part 3 of 3: grammar, species leanings and the pages"
type: task
status: done
parent: PW-767
milestone: null
subsystem: culture
effort: s
impact: med
found_by: lang-design (grammar A-D, finish, polish lanes, 2026-11-07/08)
blocked_by: []
relates: [PW-982, PW-985]
refs: [docs/review/language/for-daniel.md, docs/review/language/grammar-gaps.md, docs/review/language/architecture.md, planet/language/grammar.py, "planet/language/grammar.py::polite_contrast", "planet/language/sentences.py::default_class", planet/language/sentences.py, planet/language/texts.py, tools/language/demo_page.py, "run a24559"]
created: 2026-11-08
updated: 2026-11-09
---

## Description
In plain words: the four grammar lanes and the polish lane chose many rates and sources by judgement. Each is one
constant in `planet/language/grammar.py` (or the page code). This ticket lists them for a yes or a change. If it is
never done, the guessed sources (where an imperative or an obviative comes from) and the guessed species table stand
unreviewed, and two questions that change what the pages claim (is it "gender" without agreement? which class does a
dog fall into?) stay open.

Synthesis (how affix-heavy languages are) is not here: it is being changed by its own lane (lang-synth, 11-08); see
the grammar-shares draft for a follow-up if it does not settle.

**Real calls**
- A. **Gender without concord.** About half of the lects shown with gender have no agreement anywhere (concord in 20% of
  all lects, 51% of gender lects). Grambank defines gender by agreement. Show `gender` as 'none' until concord reaches
  at least the demonstrative? Cuts the gender share by about half. Lean: yes, label it "noun classes (no agreement)"
  rather than none.
- B. **Class fallback.** A noun whose group has no class takes the first of abstract, tools, plant or animal the lect has,
  so a dog can take the 'tools' classifier (`sentences.default_class`; the note now says it is the default). Should
  animals fall to the person class or a general class instead? Lean: animate nouns fall to person/animate first.
- C. **Species leanings in grammar (a proposal, not in the code).** Long generations (elves, dragons): evidential and
  mirative recruitment x1.5 and loss x0.5; morphology erosion and fusion x0.7. Wide pitch range (kenku): reduplication
  x1.5. Short generations (kobolds, goblin-kin): recruitment x1.2. The lane's own view: apply at most the first row.
  Options: none / first row only / all.
- D. **Comparison shares follow the Grambank-drawn aim**: locational 18% (WALS 121A 47%), exceed 34% (20%), particle
  20%, conjoined 28%. Switch the prior to WALS shares (one line)? Lean: yes.
- E. **One sentence set for every lect** ("The woman sees the dog.", "My older brother catches three fish."). Good for
  comparing, dull to read. Keep, or pick per lect (by culture, food, landscape)? Lean: keep the core set, add one
  per-lect sentence.
- F. **Politeness rises with population only** (`POLITE_MAKE` 0.002 x community size); the page says "rank is marked in
  speech", but no rank data exists. Keep until polities give rank (see the polities draft)? Lean: keep, soften the
  page wording.

**Confirm or change (each one constant in `grammar.py` unless noted)**
| default | value |
| --- | --- |
| Split ergativity kind | person 60%, aspect 40% (`SPLIT_KIND`) |
| Inclusive 'we' source | 'we + you' 45%, 'I + you' 15%, own root 40% (`INCLUSIVE_FROM`) |
| Reduplication meaning / shape | iterative 45, intensive 20, continuous 35; CV copy 65% (prefixed 3 in 4) (`REDUP`, `REDUP_SHAPE`) |
| Counting base words at proto time | decimal 20 = 'two ten'; vigesimal 100 = 'five twenty' (`NUMERAL_WORDS`) |
| Person paradigm binds as a set | join 60-85%, fill 0.004 / generation (`PERSON_JOIN`, `PERSON_FILL`) |
| Degrammaticalization | 1/50 of fusion, x3 at NP edge, x3 last survivor (`DEGRAM`, `DEGRAM_EDGE`, `DEGRAM_ORPHAN`); ~1.6 per lect per 20 kyr, probably more than real |
| Ergative mostly from agentive 'near, with' (77% of ergatives) | X22 weight |
| Imperative sources (guess: attention word X29, hortative widened X30) | bare stem stays default |
| Genitive pulled in case languages (63% of harness lects) | `PULL_GROUP['GEN']` |
| Concord spreads dem 1.0 / adj 0.7 / verb 0.5, copies the noun marker's own form | `CONCORD_TARGETS`, `CONCORD_GROW` 0.02, `CONCORD_LOSS` 0.0005 |
| Actor voice from 'do, make' (source of Austronesian -um- unknown) | guess |
| Remote past from 'long, old, before'; exceed verb 'climb' or 'jump'; obviative from 'that, other' | guesses (X65, X72) |
| Question particle pull x3, abandoned at a quarter the usual rate | `PULL_BOOST`, `KEEP` |
| Differential object marking | 0.0015 / generation, x4 from a dative, generalising 0.0006 |
| T-V only where the polite form differs from plain 'you'; plural 70% / third person 30% | `polite_contrast` |
| Fable ancestor depth | 3-6 kyr, 2-4 daughters (`texts.FABLE_DEPTH_KYR`) |
| Complexity tab window / "clear" change | 0.5-3 kyr, 1.0 points (`demo_page.CX_WINDOW`, `CX_CLEAR`) |
| Complexity score | bound functions + mean gram level + 4 x allomorphy + 0.5 x bound class markers (`grammar.complexity`) |

- [ ] Daniel answers A-F
- [ ] Daniel confirms or changes the table rows (silence = keep)

## Updates
- 2026-11-09: Status todo -> done. All parts ruled by Daniel on the Language Desk 11-08 and built in the rulings lane and lanes 4-10. Closing at language wrap-up.
- 2026-11-09: C threshold follow-through merged dffed688: LONG_GEN_YR 140 so elves (144.9 yr) count as long-generation.
- 2026-11-08: Created from inbox draft draft-language-defaults-grammar-pages.md (found by lang-design (grammar A-D, finish, polish lanes, 2026-11-07/08)).
- 2026-11-08: RULING (owner, Language Desk 11-08): A label class marking without agreement 'noun class marking (no agreement)', gender only with agreement; B animate nouns fall to person/animate first; C all three species leanings (long generations, kenku reduplication, short generations), each one constant; D comparison prior to WALS 121A; E keep the core sentence set and add one per-language sentence; F keep politeness, soften the page wording. Table rows kept.
