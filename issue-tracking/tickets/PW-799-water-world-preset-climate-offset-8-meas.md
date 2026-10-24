---
id: PW-799
title: Water-world preset climate_offset +8 (measured at L6, 2/2 pass) needs its L7 check before it lands, or is dropped if the reference-freeze fix lands
type: task
status: blocked
parent: null
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: v2-climate-1
blocked_by: [PW-798]
relates: [PW-790]
refs: [planet/make.py, tests/test_make.py, README.md, docs/coordination.md, docs/review/base-climate/v2-climate-1/]
created: 2026-10-24
updated: 2026-10-24
---

## Description
v2-climate-1 measured the water-world preset (seed 13, continental_start 0.1, heat_start 2, star 0.45) at L6 over
2 Gyr. The offset draws were +4 / +4.001, +6 / +6.001 and +8 / +8.001.
- +4 and +6 are icebox after 1 Gyr.
- +8 passes in every window: icehouse 22% / 3.3% over 300-2000, dT medians +4.7 / +6.2, max 11.8.

The L7 runs (+6, +8) were stopped at about 200 Myr for the owner's benchmark, so there is no L7 number. L7 runs
1-2 C warmer than L6 at 2 Gyr (v1-finish-8), so +8 may lean ice-free there.

Options:
- A. Run 1-2 L7 draws at +7 and +8 over 2 Gyr, then set the preset. That touches five places: `planet/make.py`
  PRESETS, `tests/test_make.py:22`, `README.md:91`, `docs/coordination.md:57`, and the blurb.
- B. Hold: fix the reference freeze (draft-co2-ref-freeze-emerging-land) first, which should make the offset
  unnecessary.

Lean: B, under the no-temporary-fixes rule. Take A only if B is far off.

## Updates
- 2026-10-24: Status needs-decision -> blocked. Held behind PW-798; drop if the reference fix lets the water world run at offset ~0.
- 2026-10-24: Created from inbox draft draft-water-world-offset-l7-check.md (found by v2-climate-1).
