---
id: PW-351
title: earth_check and the scorecard should carry the moisture budget's headline numbers (basin E-P-R, poleward transport, rain efficiency)
type: task
status: done
parent: PW-013
milestone: null
subsystem: infra
effort: s
impact: low
found_by: moisture-budget
blocked_by: []
relates: [PW-015, PW-016]
refs: [tools/moisture_budget.py, tools/earth_check.py, tools/scorecard.py, docs/proposals/moisture_transport.md]
created: 2026-10-16
updated: 2026-10-16
---

## Description
PW-014 put the diagnosis in its own tool, tools/moisture_budget.py (~10 s at L6). It reruns the rain kernel in an instrumented copy, which tests/test_moisture_budget.py keeps bit-identical to climate._rain. earth_check doesn't print any of it, so PW-015's step acceptance (docs/proposals/moisture_transport.md §8) would need a separate run every time.

Add a short block to earth_check's report and JSON, with the same keys in the scorecard row's Earth entry:
- Atlantic, Pacific and Indian E-P-R (Sv) and the Atlantic-minus-Pacific per-area difference;
- northward transport at 40S and 50N;
- sea P at 50-60S;
- the median and worst rain efficiency (P/PW)/obs over the probe regions;
- the L6 kernel's mass residue.

Make it a call into moisture_budget.analyse (no second copy of the code). Mind earth_check's runtime: the probe takes ~5 s at L6.
- [ ] earth_check prints the block; the scorecard stores it

## Updates
- 2026-10-16: Status in-progress -> done. Done (2d3b8c4): moisture headlines in earth_check (and --json R['moisture']) and the scorecard's Earth entry; +5.8 s per earth_check. Coordinator: headline names the literature E-P-R range next to NCEP-GPCP E-P (not like for like).
- 2026-10-16: Status todo -> in-progress. Agent started.
- 2026-10-16: Created from inbox draft draft-earth-check-moisture-headlines.md (found by moisture-budget).
