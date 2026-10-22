---
title: "Adopt the whole-history ice-age criteria (recovery, icehouse share, depth floor, hot eras end; 300 Myr spin-up) in place of the LGM-anchored depth bar"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: climate
effort: xs
impact: high
found_by: ice-v2-stage0
blocked_by: []
relates: [PW-555, PW-434, PW-449]
refs: [docs/review/ice-v2-criteria.md, tools/ice_criteria.py, docs/review/ice-v2/checkpoint-0.md]
---

## Description
docs/review/ice-v2-criteria.md section 3. The old bar (worst era >= -450 m, <= 2% of the time below -430 m) is
anchored on the last glacial; Earth's own Cryogenian fails it. Proposed per-run bars, L6 default params, after a
300 Myr spin-up, on the ice term of sea level: N1 every deep (< -150 m) era ends within 150 Myr and every very deep
(< -430 m) one within 60 Myr; N2 never below -1000 m; N3 5-70% of the time in an icehouse (ice holding >= 20 m of sea level, not a share of the
land, which mountain ice keeps above 1%) and no icehouse > 300 Myr; main: old bar 8/10, new 5/10; N4 dT > +8 C for at most 150 Myr at a time; N5 (reported) low-latitude ice only
after high-latitude ice. >= 70% of seeds pass. The zoom bars (Earth cycles, PW-467 window mean, the probe's
recovery) stay. Options: A adopt as written; B adopt with different numbers (say which); C keep the old bar.
Lean: A; keep printing the old bar beside the new one until stage 3. tools/ice_criteria.py implements both, and
tools/health.py shows both columns.
