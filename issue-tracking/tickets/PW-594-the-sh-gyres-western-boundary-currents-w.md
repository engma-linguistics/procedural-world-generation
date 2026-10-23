---
id: PW-594
title: "The SH gyres' western boundary currents warm their coasts 3-5 C too far south: Tasman SST 19.3 (NCEP air 15.2), Agulhas +1.3, Tasmania warmest +6.0"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: ocean
effort: m
impact: med
found_by: base-climate-laneA13
blocked_by: []
relates: [PW-589, PW-017]
refs: [planet/climate.py, docs/review/base-climate/laneA13/bands_fold.txt]
created: 2026-10-22
updated: 2026-10-23
---

## Description
After PW-589 (lane A13), the SH's open sea is ~0.3–0.6 C cooler and its band means are close (+0.3 to +1.7 at
15–60S). But the near-land rows at 35–45S stay +1.6 to +2.1 C, and that is the gyres' anomaly (`sea_surface`,
`raw0 − t_eq`), not the overturning:
- Tasman 35–45S, 150–165E: t_eq 14.6, gyre **+5.0**, SST 19.3 against NCEP's annual air 15.2;
- Agulhas 30–40S: gyre +3.1;
- off Patagonia: gyre +1.3. On Earth the Falklands current makes this sea cold.
- Tasmania's warmest month is still +6.0 C, most of it the Tasman's air.

On Earth the East Australian Current and the Agulhas leave the coast at ~31–38S. South of that the westerlies'
northward Ekman drift and the circumpolar current's cold flank set the sea. The model's boundary currents carry the
subtropics' warmth (reach `relax_km` × speed / `cur_ref`) all the way to 45S.

What to check: where the gyre streamfunction closes against the circumpolar band (`currents`, `_circumpolar`); and
whether the westerlies' equatorward Ekman transport (cold water north) is missing from `sea_surface`.
- [ ] Tasman / Agulhas near-land SST within 2 C, without cooling the SH subtropics' east coasts' summers below NCEP

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Lane A17 (branch worktree-agent-a6b65c5df0ddd0d62, 7b41cea, waits on PW-623 with PW-596): islands longer N-S than two boundary-current widths now wall the gyres (New Zealand, Luzon, Sulawesi); Tasman SST 19.3 -> 18.5, bar not met; remainder PW-625.
- 2026-10-22: Created from inbox draft draft-sh-western-boundary-currents-too-warm.md (found by base-climate-laneA13).
