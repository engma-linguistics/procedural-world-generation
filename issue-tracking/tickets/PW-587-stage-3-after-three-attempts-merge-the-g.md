---
id: PW-587
title: "Stage 3 after three attempts: merge the green candidate without the fetch, or redesign the fetch first?"
type: task
status: done
parent: PW-470
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: base-climate-laneA11
blocked_by: []
relates: [PW-352, PW-457, PW-573, PW-581, PW-580, PW-570]
refs: [docs/review/base-climate/stages.md, docs/review/base-climate/laneA11/stage3_attempt3_candidate.diff]
created: 2026-10-22
updated: 2026-10-22
---

## Description
Attempt 3's candidate (`laneA11/stage3_attempt3_candidate.diff`, not on the branch) passes the whole suite except
the goldens (565 passed). It has four parts:
- the summer reach per time (PW-581 part 1);
- the mountain rule (PW-581 part 2);
- the energy split, re-referenced to the model's own potential evaporation (`ef_ref` 0.61 = Earth's ice-free land
  20–60 summer AET/PET without the split). This replaces attempt 2's Priestley–Taylor share, which warmed cold lands
  and lost `test_cold_moment_has_sheets` once the fetch was gone (0.51% against 1%);
- the humidity floor fix (`draft-humidity-floor-under-humid-min.md`).

There is no fetch (`draft-stage3-fetch-moves-l4-glacial-ice-poleward.md`).

Earth L6 against main (`laneA11/stage3_probe_attempt3.txt`):

| measure | main | candidate |
|---|---|---|
| rain r | 0.622 | 0.626 |
| Köppen group | 70.5 | 70.4 |
| Fennoscandia warmest month | −5.2 | −3.6 |
| Alaska warmest month | −2.8 | +0.6 |
| W Europe | +0.4 | −0.2 |
| Canadian Rockies coldest month | −7.7 | −6.8 |
| NH continentality rows | | all within 1.4 |
| Keewatin | −0.4 | +3.9 |
| Iceland | +0.5 | +2.0 |
| SH coastal range | 14.3 | 14.7 |
| NZ | +2.3 | +2.9 |
| Tasmania | +6.9 | +8.5 |
| Chile mid | +2.2 | +3.6 |
| obs E → model D | 6% | 26% |

Stage 3's main targets (humid summers within 2.5 C, SH coastal range within 1.3×) are not met. Humid summers move
0–2 C toward observed and the SH range not at all. The endings test passes (36 / −0.2).

Options:
- A: merge the candidate as stage 3's sound parts (PW-581 done, PW-352 / PW-457 in the energy-split form) and keep
  PW-573 open for a fetch redesign. It's mixed rather than clearly better (polar summers warmer, SH small lands worse).
- B: hold stage 3 until the fetch is redesigned (scale on the land's width, built from the arriving sea air), then
  land all of it together.
- C: drop stage 3 for v1. The base climate stays at PW-579.

Lean: B. A doesn't clearly improve things overall under the owner's principle, and the fetch is what stage 3 was for
(PW-573). The fetch redesign is one more focused attempt, with the toggles and diagnostics in `laneA11/tools/`.

## Updates
- 2026-10-22: Status in-progress -> done. 2026-10-22 stage 3 merged (lane A12): summer fetch from the arriving sea air on distance scales (fetch_km 1000, fetch_h 3500), per-time reach, PET-referenced energy split, mountain rule, humidity floor. Humid summers +5-6 -> +2-4 C; SH coastal range 1.29x (pass); dry-region summer rain down; r 0.620. W Europe / Fennoscandia summers worse via too-cold near-land NH SST (new ticket). Merged under the owner's principle.
- 2026-10-22: Status needs-decision -> in-progress. Coordinator 2026-10-22: option B. Redesign the fetch to build from the arriving sea air on a land-width scale, then land stage 3 together; fix PW-586 alongside.
- 2026-10-22: Created from inbox draft draft-stage3-after-three-attempts.md (found by base-climate-laneA11).
