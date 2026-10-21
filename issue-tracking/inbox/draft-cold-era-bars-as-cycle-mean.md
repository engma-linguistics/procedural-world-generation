---
title: "Cold-era health bars: state them as cycle means and add the cycle's glacial and interglacial bounds to tools/sealevel.py"
type: task
status: todo
parent: null
subsystem: infra
effort: xs
impact: low
found_by: pw462
blocked_by: []
relates: [PW-462, PW-438, PW-452, PW-461]
refs: [tools/health.py, tools/sealevel.py, docs/review/audit/ice-framing-deep-dive.md]
---

## Description
The run's cold-era bars (`tools/health.py` `sea_ice_m` >= -250 "PW-240 goal -150 typical / -250 worst",
`sea_ice_below_150` <= 10%; the pw449 10-seed check: worst era >= -450 m and <= 2% of time below -430 m;
~70% of seeds passing) were set on whatever the run's ice was. Today's rule makes that the edge of the cycle
(interglacial on moderately cold moments, near-glacial on deep ones; PW-462 deep dive). Once the run's ice is
the cycle mean (draft-run-ice-cycle-mean.md):
- Keep the numbers, change their meaning to "cycle mean", and say so in the reference text. Earth's
  Pleistocene mean in the run's terms (all land ice) is about -65 (today's sheets) - 50 (mean glacial excess)
  = ~-115 m, its glacial maxima ~-185 m: under the -150 "typical" mean, and an icehouse twice Earth's still
  passes -430.
- Add to `tools/sealevel.py` and the health table the cycle's bounds per sample (the persistent ice's and the
  cold phase's sea level, which the new rule computes anyway), with an informational (not gating) line for
  the worst glacial maximum, so a seed whose mean passes but whose glacials reach -700 m is visible.
- The ~70% seed bar stays the owner's.
- [ ] reference texts updated; bounds printed
