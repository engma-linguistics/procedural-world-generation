---
id: PW-576
title: "The thermostat's weakness is its bookkeeping, not erosion: the saturating weathering law (PW-574 A) doesn't help; fix it with the CO2 stock and a fixed start reference instead"
type: task
status: in-progress
parent: PW-470
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: base-climate-laneB
blocked_by: []
relates: [PW-574, PW-558, PW-559, PW-564, PW-572, PW-561]
refs: [planet/tectonics/earth.py, tools/ice_diag.py, docs/review/base-climate/thermostat.md]
created: 2026-10-22
updated: 2026-10-22
---

## Description
PW-574's option A (a smooth saturating weathering law) was chosen on the review's hypothesis that erosion swamps the
sink's temperature factor. Stage 0 of lane B measured the sink's parts, and the hypothesis doesn't hold. The setup:
- `ice_diag --summary` now splits the sink and instruments the gain on the random drift. The drift knows nothing of
  geography; the review's regression on dT mixed the gain with the thermostat's own answer to geography.
- 10 L6 1 Gyr seeds, after 300 Myr. The full tables are in `docs/review/base-climate/thermostat.md`.

What was measured:
- **The erosion supply rises with warmth** (+0.018 per C median): a wetter world erodes more. It doesn't swamp the
  temperature factor.
- **The sink's own answer is 0.047 per C (fb ~0.35 C/C).**
  - A controlled re-run of one climate call at dT − 4 gives a temperature factor of 0.050 per C.
  - The eroding ground (|lat| ~20°, 1–1.4 km up) warms ~0.65 × dT.
  - So the written 0.09 per C (fb ~0.7) was never reachable: the latitude curve moves the low latitudes about
    0.5–0.7 × dT.
- **The bookkeeping halves it.**
  - The 10 Myr smoothing of the rates loses ~20%.
  - The baselines relearn over 300–1000 Myr, which loses ~30%: they take up a long cold era's deficit.
  - The CO2 term answers at only **+0.13 C/C median** (2/10 in 0.4–0.9).
- **The CO2 term does push against drift-made dT on 9/10 seeds.** Its raw correlation with dT is positive on 8/10,
  because it follows the tectonic source, which causes the warmth. Earth's record has the same positive correlation.
- **Attempt 1 of option A** (W = c (1 − exp(−e/c)), c ∝ runoff × exp(0.09 ΔT) × plants, C 1e-4):
  - the median CO2 answer is unchanged (+0.14);
  - N1–N4 fall from 4/10 to 2/10, with longer deep eras;
  - the raw correlation is negative on 0/10.

  Saturated ground no longer answers temperature. It can't fix the bookkeeping, so further attempts were not made.

Options:
- **A (as decided): keep working the saturating law.** It can't reach the bar, for the reasons above.
- **B: the CO2 stock with a fixed start reference (PW-558 A + PW-559 B together).**
  - dC/dt = source − k × sink(T) × exp(WEATHER_CO2 × C).
  - k is set once from the planet's own start balance, the outgassing against the weathering over the first ~100 Myr.
    That is also where the set point comes from (PW-559 B).
  - No relearning baselines and no extra smoothing. A cold era's deficit stays, and CO2 piles up under the ice, which
    is A3b and the snowball exits.
  - Expected steady-state answer: the sink's own ~0.35–0.5 C/C, with a weaker brake on short spells (the stock's
    time constant).
  - The tectonic source's long trends would then drift the climate (no baseline to forget them). The source would
    need its own planet-relative reference, for example the mantle heat's decay.
- **C: B, plus the bar re-read.**
  - Judge "the CO2 term runs against dT" on the drift (9/10 already), not on the raw correlation, which a fair
    tectonic forcing makes positive.
  - Treat ~0.35–0.5 C/C as close enough, if B's sweep lands there, rather than tuning WEATHER_K up to reach 0.7.

Lean: **C**. It fixes the mechanism that's actually wrong (the baselines' forgetting) with the stock that PW-558 already
plans. It keeps option A out, since it makes cold eras longer.

The bar change in C is the owner's call:
- the measure moves from the raw correlation to the drift;
- "close enough" becomes the sink's own answer, ~0.35–0.5 C/C, instead of the written 0.7.
- [ ] owner picks A, B or C
- [ ] if B or C: lane B builds the stock and the start reference, then measures the 10 seeds with `ice_diag --summary`

## Updates
- 2026-10-22: Owner 2026-10-22: mature start + option (a) 'set once' (no relief term); keep the 300 Myr warm-up; simulate's default run becomes 1 Gyr.
- 2026-10-22: 2026-10-22 attempts 1-3 done (branch worktree-agent-adf7ab7eab37416aa). Owner: first give planets a mature start (relief and anything else that spins up), then compare attempt 1 (set once) against attempt 3 (relief term) on it; owner sees both before anything merges. If the mature start doesn't help appreciably, take attempt 3.
- 2026-10-22: Status needs-decision -> in-progress. Owner 2026-10-22: option C. Build CO2 as a stock (PW-558) with a fixed reference set once from the planet's own start balance (PW-559 B); judge 'runs against dT' against the drift; accept ~0.35-0.5 C/C as close enough rather than tuning sensitivity to 0.7.
- 2026-10-22: Created from inbox draft draft-thermostat-cause-is-bookkeeping.md (found by base-climate-laneB).
