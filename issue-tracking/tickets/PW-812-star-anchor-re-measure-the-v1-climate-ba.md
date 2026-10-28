---
id: PW-812
title: "Star anchor: re-measure the v1 climate bar and PW-806's showcase diagnosis on the anchored star; add an end-counted last-540-Myr window as a reported diagnostic"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: star-anchor-audit
blocked_by: []
relates: [PW-791, PW-806, PW-780, PW-202]
refs: [docs/review/base-climate/v1-finish-8/passrate2.py, docs/review/base-climate/v1-signoff/, tools/ice_criteria.py, docs/review/base-climate/star-anchor-audit/]
created: 2026-10-24
updated: 2026-10-25
---

## Description
Audit items 4 and 5 (docs/review/base-climate/star-anchor-audit/README.md).

These were all measured on the old from-start star:
- every v1 climate number: L6 13/18 strict, L7 7/8, the 2 Gyr 1500-2000 window 4/13, the never-ice tallies, and
  PW-789's "L7 runs warm late";
- PW-806's showcase diagnosis: slices at +4 to +5.4 C and pCO2 87-244 ppm.

The windows count forward from the start (300-1000, 300-500 / 600-1000, 1000-1500 / 1500-2000). The 1500-2000
window was there to catch the future-Sun drift. Under the anchor, a run's last ~540 Myr is the Phanerozoic analogue,
and Earth's icehouse share there is ~25-33%.

Do:
- Re-run the 18 L6 seed-draws and 8 L7 seed-draws (1 Gyr), plus the 2 Gyr L6 set, on the anchored code, with the
  bar and thresholds unchanged.
- Add an end-counted window (the last 540 Myr) to the pass-rate harness as a *reported* diagnostic. That is a
  harness change; thresholds still need the owner.
- PW-806: the offline Earth-climate tests (280 ppm keeps ~80% of its trees; warm wet tropics forested) are
  star-independent and stand. Re-measure the showcase criterion (L7 wet tropics > 2000 mm carry >= ~20% trees) only
  after the anchor. Don't tune plants against old-star slices.
- Remake the showcase (PW-202) after the anchor and PW-807.
- [ ] pass rates on the anchored star recorded in PW-791
- [ ] end-counted window reported
- [ ] PW-806's showcase check re-measured after the anchor

## Updates
- 2026-10-25: v1-finish-11: re-measured on the anchored balance (passrate_a/t/o25.txt), with the end-counted last 540 Myr and the owner's finish diagnostics (true mean vs pre-industrial -6..+3 C, land ice at the finish). docs/review/base-climate/v1-finish-11/README.md
- 2026-10-24: v1-finish-10: harness passrate3.py (strict bar, forward windows, end-counted last 540 Myr diagnostic, pCO2, true mean T, trees, wet-tropics trees, corr). Partial measurement only (L6 1 Gyr first waves): full Gough 0/6, 0.45 1/6, full Gough + thermostat see README. L7 and 2 Gyr not run: the anchored code fails at L6. docs/review/base-climate/v1-finish-10/README.md
- 2026-10-24: Created from inbox draft draft-remeasure-v1-bar-on-anchored-star.md (found by star-anchor-audit).
