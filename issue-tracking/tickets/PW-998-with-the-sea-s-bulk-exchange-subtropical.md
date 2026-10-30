---
id: PW-998
title: "With the sea's bulk exchange, subtropical east coasts and winter-rain coasts dry out (SE USA 482 vs 1328 mm, Pampas 294 vs 943, Japan 524 vs 1672, E Australia 488 vs 743): the instant refill had masked their winds"
type: task
status: done
parent: PW-013
milestone: v1
subsystem: climate
effort: l
impact: med
found_by: lane25
blocked_by: []
relates: [PW-015, PW-026, PW-352]
refs: [planet/climate.py, tools/earth_check.py, tools/moisture_budget.py, docs/review/base-climate/deserts/README.md]
created: 2026-10-29
updated: 2026-10-30
---

## Description
Lane 25 (PW-015) replaced the rain kernel's instant refill of the sea's air with a bulk exchange
(`climate.sea_uptake`, commit 5840dcc6). Earth improved overall (Koppen B 20 -> 27%, log-rain corr 0.648 -> 0.691,
exact 34 -> 36%), but coasts whose rain came from air that had crossed only a little sea lost a lot (Earth L6 earth_check,
main -> branch, GPCC):

| region | main | branch | GPCC |
|---|---|---|---|
| SE USA | 1109 | 482 | 1328 |
| Pampas | 548 | 294 | 943 |
| Japan | 1153 | 524 | 1672 |
| E Australia | 1055 | 488 | 743 |
| Mediterranean | 607 | 383 | 551 |
| Mexico N | 237 | 114 | 482 |
| India | 696 | 588 | 1109 |

Before, any strip of sea refilled the air at once, so these coasts were wet for the wrong reason. Their real moisture
comes with winds the model lacks: the winter subtropical highs' return flow and the cyclones that bring Gulf, South
Atlantic and Kuroshio air onshore (PW-026, the 2026-10-16 handoff's root cause 2: SE USA Oct-Mar PW 4.6 vs NCEP 17.4 mm).
Japan's winter (the NW monsoon over the Sea of Japan) should be wet under a bulk exchange; check whether its summer
southerlies or its winter fetch is what dried.

What to try: per region and half-year with `tools/moisture_budget.py` (kernel terms, wind), find which half lost the rain
and from where the vapour comes; then fix the winds (PW-026), not the sea's exchange.
- [ ] SE USA and Pampas each at least 60% of GPCC's annual rain without undoing the bulk exchange

## Updates
- 2026-10-30: Status todo -> done. Merged 53807d76: coast package done; Earth headlines all improve, polar land dry bias fixed. Acceptance line (SE USA/Pampas >=60% of GPCC; now 48%/42%) moved to PW-026, PW-1094 and PW-1097, the wind tickets.
- 2026-10-30: Lane 28 diagnosis of the coasts judge's icebox rise (no new sims; A = db7a178a vs D = e0158fa2 records, and two shared states solved with each round's frozen code). The package grows more land ice at the SAME global temperature, from the first 30 Myr: in 36/36 draws sea_ice -19 -> -35 m, snow_land +40%, sheets' net accumulation +35%, dT only -0.14 C; over 300-990 Myr dT is unchanged (+0.09) while sea_ice is -39 m and ice_frac +0.014, so the extra iceboxes are mostly the sea-level icebox flag tripping on more ice. Cause: round 3's poleward eddy drift. On seed 957317 at 12 Myr and seed 53669 at 300 Myr, D gives +30-75% precipitation poleward of 60 deg (e.g. 70N 139 -> 205, 80N 118 -> 171, 70S 335 -> 439 mm/yr) and +15-20% at 40-60 deg; the bare ground's warm month moves only -0.2 to -0.5 C; rounds 1-2 add little (B/C within ~1 m of A's ice, D +4.5 to +11 m on the same state). So hypotheses (b)/(d) (more polar snow, more accumulation), not the cold domes (c) and not CO2 (a). Open: is the extra polar precipitation too much against GPCC (Greenland, Antarctica, Siberia, Canada)? Held until the Earth cache is rebuilt (GPCC upstream outage); no drift tuning before then (coordinator 10-30).
- 2026-10-29: Coasts paired judge finished (A = db7a178a main vs D = e0158fa2 coasts, 36 L6 pairs, pre-speed cadence): passes 27/36 vs 27/36; iceboxes 8 vs 21; end T -2.8 C [-4.4, -0.9]; arid -2.8 pts, hot desert -2.8 (both moved, intended direction). Do not merge until the icebox rise is explained; likely interacts with PW-1050 (ice-climate loop one step per update).
- 2026-10-29: Lane 26b. Round 1 (shallow cold domes, 261343c5) awaits its paired judge. Round 2 (storm-lifted humidity gate, c9b4990e) is committed: Earth L6 SE USA 525 -> 601 mm (45% of GPCC), Pampas 291 -> 330 (35%), winter SE USA 153 -> 288, NE USA 174 -> 313, corr 0.707, exact 37.9, B 25.6 (lost mostly wrong-B land, bflip.py). Both rounds are vapour-limited: 60% isn't reachable without the return flow's vapour and the Pampas jet (coasts README, round 2 note).
- 2026-10-29: Lane 26 diagnosis (docs/review/base-climate/coasts/README.md): the winter half is lost (SE USA Oct-Mar 93 vs 1334 mm, PW 3.7 vs 17.5) because the model blows offshore where NCEP has the subtropical highs' onshore return flow; Japan rains its vapour at 0.3-0.4x; the Pampas lacks the Andes low-level jet. No single probed mechanism reaches 60% with B >= 26 (best combination SE USA 58%, Pampas 42%, B 23.7); plan choice in draft-subtropical-coasts-mechanism-choice.md.
- 2026-10-29: Created from inbox draft draft-subtropical-coasts-dry-after-bulk-evap.md (found by lane25).
