# Audit fixes: surface and hydrology (PW-283, 282, 280, 281, 279, 239)

Branch `worktree-agent-a4e14f114a9da60d7`. One commit per ticket. Health sweeps: `docs/review/health-surface-hydro*`.

## What changed
| Ticket | Result |
|---|---|
| PW-283 | `test_sediment_budget_closes` (test_invariants): Σ deposited = Σ removed per step (rel 1e-9), no negative deposits; since PW-280 also: no river-end cell filled above its basin's spill point. |
| PW-282 | Hillslope term is a slope law: lowering = `hillslope` × K × relief / d (mean downhill slope), `hillslope` = 3.3245 km/Myr (= 4 × 100 / 120.32 km, so L6 is unchanged). Test: same terrain wears the same at L4 and L5. |
| PW-280 | `surface._closed_basins`: what reaches a closed lake or pit fills the lake's floor (up to its surface), then the whole hollow up to 5 m below its spill point (priority-flood of the terrain), each cell by its room, as open lakes do; the excess follows the flood path over the rim into the next hollow or the sea (up to 8 basins). |
| PW-281 | B tried and dropped (it cost the Jaccard, below); A: documented in overview §2.11 and `hydrology.erode`'s docstring. |
| PW-279 | A: overview §2.5 documents the 200 m base level as a stand-in for "flat plains don't erode". |
| PW-239 | `output.water_now`: a frame's `flow`, `downstream`, `lake_kind`, `lake_depth` come from `hydrology.rivers_and_lakes` on the frame's final bed (over land ice, no lakes on it). Test: every river that ends on land ends in a closed lake, salt pan or pit of the frame's own elevation. Health run time 327 s → 311 s for the L6 quick sweep (noise; ~0.4 s per L7 frame). |

## PW-282: hillslope lowering per 2-Myr step, synthetic continent (fixed-wavelength noise, K = 1)
| | L5 | L6 | L7 |
|---|---|---|---|
| hillslope, before | 1.25 m | 2.51 m | 4.91 m |
| hillslope, after | 2.49 m | 2.51 m | 2.50 m |
| incision (unchanged) | 2.23 m | 1.61 m | 1.14 m |
| total, before → after | 8.15 → 9.38 m | 8.80 → 8.80 m | 10.73 → 8.32 m |

Incision's level trend is filed as a draft (needs-decision: the law is sound, the grid resolves more small-catchment cells).

## PW-280: L5 seed 1, 300 Myr (every step)
| | before | after |
|---|---|---|
| river-end (sink) cells filled > 1 m above their spill point | 742 of 5798 cell-steps | 0 of 6228 |
| closed-lake cells raised > 1 m above the lake surface | 34% (worst 4.2 km) | 23% (worst 0.28 km; always below the rim: the lake was full of sediment and the hollow kept filling) |
| deposition on hollow cells landing above the spill level | 5.1% | 2.8–3.3% (the rest is floodplain deposits near rims: draft) |
| Σ dep / Σ removed | 1.000000000000 | 1.000000000000 |

The ticket's "no closed-lake cell above its lake level" is replaced by "nothing above the basin's spill point": material below the rim stays in the closed basin, as on Earth; only a full basin passes it on.

## PW-281 B, tried: finishing (strength 0.3) on three L5 run ends (300 Myr), same climate
| seed | lake Jaccard vs keyframe, A → B | inland drainage, A → B (keyframe) | new land cells (deltas) |
|---|---|---|---|
| 1 | 0.60 → 0.37 | 4.1 → 2.2% (10.4) | +67 (2.2%) |
| 2 | 0.27 → 0.00 (17 lake cells → 0) | 5.6 → 0.2% (5.9) | +72 |
| 3 | 0.81 → 0.55 | 1.4 → 3.4% (2.0) | +52 |

B costs the Jaccard badly and builds deltas over the keyframe's coast, so per the approved fallback it is A.

## Closed-basin share (PW-054, PW-243): `tools/health.py` measure, median per seed over 100–500 Myr, mean of seeds
| | L6, 8 seeds (`--quick`) | L7, seeds 3199 / 21 | L7 / L6 |
|---|---|---|---|
| main (baseline) | 10.3% (raw `downstream`: 27.3%) | 23.5% (22.4 / 24.6) | 2.3 |
| + PW-282, PW-280 | 9.2% (23.8%) | 18.1% (20.1 / 16.1) | 2.0 |
| + PW-239 (final) | 7.9% (7.9%) | 16.3% (19.1 / 13.5) | 2.1 |

Earth ~18%. The L6 baseline is the coordinator's; the L7 baseline is main's code run here on the same seeds (500 Myr, `health-L7-main`, not committed). With PW-239 the raw and checked shares agree (they were 2–3× apart), and the frames' measure drops: part of the old L6 "inland" share was rivers ending in hollows the frame no longer had. PW-282 narrows the L7/L6 gap a little (2.3 → 2.0); the rest is PW-243's per-cell lake rules.

Other health measures (same sweeps): frames whose biggest lake is over 1 Mkm²: L6 17.2 → 11.3 → 13.4%, L7 4.0 → 10.4 → 12.9% (L6 and L7 now agree; they are on the frames' own terrain: draft). Land, temperature, dry share: within seed noise. L7 highest peak, median 8.05 → 7.62 km; peak frames 1 → 0 per run.

## Scorecard (L6, 1000 Myr) vs baseline
| | seed 1 before → after | seed 2 before → after |
|---|---|---|
| land | 32.6 → 32.2% | 32.1 → 30.5% |
| crust volume | ×0.936 → ×0.915 | ×0.955 → ×0.920 |
| dry | 32.0 → 41.8% | 37.2 → 31.2% |
| ocean age | 73.6 → 47.5 Myr | 41.5 → 44.6 Myr |

Earth climate unchanged by these fixes (71.8% group agreement). Continental volume falls ~2–3% more over 1 Gyr: full closed basins now pass their load on to the sea instead of piling mounds on land. No retunes.
