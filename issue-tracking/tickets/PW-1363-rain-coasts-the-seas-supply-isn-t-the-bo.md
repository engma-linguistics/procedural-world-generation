---
id: PW-1363
title: "Rain coasts: the seas' supply isn't the bottleneck (observed sea temperatures make the coasts drier); D40 A stopped, the next round is where the vapour rains (B: low-layer friction + ascent)"
type: task
status: todo
parent: PW-015
milestone: later
subsystem: climate
effort: l
impact: high
found_by: lane132
blocked_by: []
relates: [PW-1321, PW-1099, PW-1100, PW-026, PW-1279, PW-593]
refs: [docs/review/base-climate/rain-supply/round1.md, docs/review/base-climate/rain-supply/screens.md, docs/review/base-climate/rain-supply/marine-layer.patch, docs/review/base-climate/rain-supply/sstswap.py, docs/review/base-climate/rain-supply/swap.sh, docs/review/base-climate/rain-supply/ec.sh, docs/review/base-climate/rain-supply/summ.py, docs/review/base-climate/rain-inland/diagnosis.md, docs/review/base-climate/rain-inland/candidates.patch, tools/moisture_regions.py, tools/earth_check.py, "planet/climate.py::_rain", "planet/climate.py::sea_uptake", "planet/climate.py::_season_inputs", "planet/climate.py::monsoon_wind", "planet/climate.py::compute", "Fairall et al. 2003 J. Climate 16:571", "Stevens 2006 TCFD 20:279", "Chan & Wood 2013 JGR 118:12422"]
created: 2026-11-02
updated: 2026-11-03
---

## Description
In plain words: Daniel approved plan A (D40). It said the humid coasts (SE USA, the Pampas, Japan, SE China) are
dry because the seas next to them are too dry.
- Lane 132 built a low marine air layer under the column and tried it two ways. Both made the coasts drier and the
  interiors wetter: two strikes.
- Then it checked the premise directly, by giving the rain the observed sea air temperatures. The seas' vapour came
  close to observed (Gulf summer 31.6 -> 36.3 mm, obs 39). But the coasts still got drier (SE USA 720 -> 597 mm,
  obs 1329).
- Observed land temperatures didn't help the coasts either.
- So the coasts aren't short of vapour coming in. It passes through them: in summer, SE USA takes 3916 mm in through
  its south face and lets 4185 mm out through its north face.
- The fix belongs to where the air rains, not to how much the sea gives.

Screens (Earth L7 earth_check + L6 moisture_regions, round1.md section 2). Each figure is the model's rain as a
multiple of the observed:

| arm | humid coasts | interiors 40-60 N |
|---|---|---|
| main | 0.56 | 1.85 |
| marine layer | 0.46 | 2.03 |
| marine layer + showers | 0.36 | 2.06 |
| observed sea air, 15-50 N | 0.52 | 1.96 |
| observed land air | 0.53 | 1.90 |
| both | 0.48 | 2.01 |

Options:
- **A'. Stop supply work for the coasts** and run the placement round instead, judged together on Earth:
  - lane 120's land friction (fric_land 0.89), better applied to the low layer only;
  - PW-1100's convergence ascent;
  - PW-1099's inflow depth.
  The parked marine layer (marine-layer.patch) is the natural carrier for "the low layer" if the inflow is split by
  height. **Lean.**
- **B. Merge fric_land 0.89 alone** (the D40 fallback). Coasts +5-15%, B -0.8 points, interiors unchanged.
- **C. Park rain coasts** behind PW-1279 / D34, as lane 120 suggested.

- [ ] owner picks A', B or C

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: rain kernel is calibration polish and three strikes sends it to the back of the line (PW-1363)
- 2026-11-02: Status needs-decision -> todo. Coordinator 2026-11-02 (owner delegated prioritisation): parked at the back of the line after five failed rain arms; A' (where the vapour rains: low-layer friction, PW-1100, PW-1099) is the plan when it comes back. Not B alone.
- 2026-11-02: Created from inbox draft draft-rain-coasts-are-through-flow-not-supply.md (found by lane132).
