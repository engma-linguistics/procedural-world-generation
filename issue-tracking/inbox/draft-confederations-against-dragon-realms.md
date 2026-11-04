---
title: "Confederations: does a dragon realm next door count as the foreign power a people bands together against?"
type: task
status: needs-decision
parent: null
milestone: v3
subsystem: culture
effort: xs
impact: med
found_by: lane178
blocked_by: []
relates: [PW-785, PW-1449]
refs: ["planet/lineages/polities.py::_confederations", "planet/lineages/polities.py::CONFED_AGAINST", docs/review/culture/polities/round3.md, "docs/review/cultures-proposal/proposal.md#212-formation-growth-and-reach", "run 3c1caf", "run b4d502", "run a2b637"]
---

## Description
In plain words: lane 178 added confederations to the polities. A people with kings or law but no city can now band its villages
and camps into a state. It needs a city's worth of its own people (10,000) within a state's reach, and a foreign power next door
the century before (Turchin 2009's mirror empires). This is what gives the Seven Meals world a present-day antelope-kin empire and
fallen cervid-kin empires (PW-785).

The open question is which neighbours count as "a foreign power". Today a foreign state, empire or dragon realm counts
(`CONFED_AGAINST`). The proposal lists "dragon country" among this world's frontiers (proposal.md 2.1.2), and a dragon realm takes
tribute from its subjects.

What misleads if this is never decided: the default stays a judgement nobody signed off. Either the Seven Meals present-day empire
rests on it, or more land is ruled than history would suggest.

Numbers. The baseline is each run with no confederations:

| | no confederations | states, empires and dragon realms count (now) | states and empires only |
|---|---|---|---|
| 3c1caf: states and empires over the run | 663 | 1,223 | 1,021 |
| 3c1caf: antelope-kin empire standing at the present | no | **yes** (0.39 Mkm², founded 200 years ago) | no (their last: 1,300 years ago) |
| 3c1caf: polities over 1 Mkm² at the present | 25 | 30 | 26 |
| b4d502 (D&D): land ruled at the present | 26.8 Mkm² | 38.4 Mkm² | 32.0 Mkm² |
| b4d502: polities over 1 Mkm² at the present | 7 | 14 | 9 |

Options:
- **A. Keep the dragon realms (now).** Seven Meals gets its present-day antelope-kin empire. D&D worlds get more confederations
  near dragon country.
- **B. States and empires only** (Turchin's original). This is the more conservative choice. The antelope-kin empires all lie in
  the past on 3c1caf, so the present-day one would need an authored anchor (a back-fill).
- **C. Dragon realms count only for a people that is itself a dragon realm's subject** (it pays tribute). This is closer to "band
  together against the raider", but it is one more rule.

Lean: A. Dragons are sapient rulers taking tribute, the proposal already names dragon country as a frontier, and the extra land
mostly matters for PW-1449's reach, which owns that problem.
