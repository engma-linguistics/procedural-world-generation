---
id: PW-1402
title: Source ranges for the ladder numbers that have none (forager level, rich-land half point, irrigation)
type: task
status: todo
parent: null
milestone: v2
subsystem: peoples
effort: s
impact: low
found_by: lane 145
blocked_by: []
relates: [PW-1383, PW-1275]
refs: [planet/lineages/ranges.py, planet/lineages/ladder.py, docs/review/peoples/ranges/round1.md, docs/review/peoples/density-ladder/ladder.md, docs/review/peoples/density-ladder/binford_by_npp.py, docs/review/peoples/density-ladder/rich-foragers.md]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: the "draw numbers from their published ranges" setting (PW-1383) can only draw what a source gives a range for. Three
of the numbers that matter most have none, so they stay fixed even with the setting on:

- **The forager level (0.036 per km2 at NPP 330).** Binford's spans are across all land qualities. At one land quality the scatter
  around the fit (r 0.55) is not written down. `binford_by_npp.py` has the D-PLACE data: the residual spread of log10 density around
  the fit (say its middle half) would be a sourced range for this number. Today only the fit's slope (1.26-1.28) is drawn, which moves
  almost nothing.
- **RICH_HALF (3).** A judgement on the Calusa case (richness 7-16); no range for the constant itself.
- **Irrigation steps (30 ... 240 per watered km2).** One "hypothetical" series (Butzer 1976 Table 4); other figures are other places.

Source the first (cheap, data in hand); the other two only if a paper turns up. Then add the ranges to ranges.py (RANGES, and take the
name out of FIXED) and a ladder.py entry in Ladder.v.

## Updates
- 2026-11-03: Created from inbox draft draft-ranges-source-the-fixed-ones.md (found by lane 145).
