# PW-015 handoff (2026-10-16): continue option A

Branch `worktree-agent-adc23e25e68fd8311`; main merged at db3795b.
- Full write-up: `docs/review/audit/pw015-rain.md`. §9 covers stage 1 alone and the stage-2 revision; §10 is
  the option A design.
- Proposal: `docs/proposals/moisture_transport.md`.

## Branch layout (oldest first)
| commit | what |
|---|---|
| 1af9a9b | **Stage 1.** Rain kernel in physical time; conservative finite-volume transport (`_faces`, `face_winds`, `_transport`; float32 shares, [cell, season]); 20 days from a half-saturated start. The moisture_budget probe is bit-identical; earth_check gains the log-rain corr and the PW-019 ratio. |
| ecffcb9 | **Stage 2.** Storm eddies (`storm_eddies`, storm_k 1.3e6 x B, saturation-gradient closure as a velocity); bulk sea evaporation against q_s(SST) through a 2 km column (c_e 1.2e-3, 5 m/s gust); **PW-358** Penman lake evaporation (`open_water_evap`) for `lake_evap`. |
| 16daace, a1941ae | Write-up, drafts, overview §2.6, goldens. |
| 326e482 | **Stage-2 revision.** `rain_phases`: phase 1 (10 days) gives the ground's AET/PET; phase 2 (14 days, warm: carries the vapour and the running rain means `ema`) lets the vapour ride `v_belts + s (v - v_belts)`. s = 1 at sea; on a land low, max(0.53, wetness); on a land high, 0.53. Zoom tests reworded (flat floodplains; treeline against the forest belt). |
| 8f9de88, 947ef82 | Follow-up write-up (§9); goldens for 326e482. |
| e26422b | **WIP option A** (below). Not measured on Earth. |

## Key numbers (Earth; GPCC/Kottek observed)
| | main L6 | stage 1 L6 | stage 2 L6 | 326e482 L6 / L7 | obs |
|---|---|---|---|---|---|
| Koppen group / exact % | 71.0 / 32.7 | 70.6 / 30.9 | 70.3 / 35.1 | 72.2 / 36.2 (71.4 / 35.6) | |
| arid share % | 20.3 (L7 24.5) | 18.0 (L7 17.9) | 29.3 | 31.0 / 31.4 | 30.1 |
| land P mm | 993 (L7 784) | 1138 (L7 1152) | 1200 | 1153 / 1152 | 791 |
| SE USA / Pampas | 1343 / 703 | 1156 / 681 | 277 / 217 | 757 / 237 | 1328 / 943 |
| India / Tibet | 711 / 76 | 723 / 70 | 642 / 39 | 551 / 12 | 1109 / 296 |
| log-rain corr | 0.601 | 0.617 | 0.667 | 0.685 | |

- **Generated planets** (health --quick, mean of per-seed medians), main / stage 1 / stage 2 / 326e482:
  - arid share 29.3 / 27.8 / 36.1 / 37.8%
  - NPP 334 / 321 / 277 / 304
  - deepest icehouse ice sea level -228 / -217 / -216 / **-491** m
- **L7 climate update:** main 2.2 s, stage 1 3.6, 326e482 3.5.
- **Ice probe dT 0 / -6:** main 2.54% / -58 m; 326e482 3.20% / -149 m.

## Tried and dropped
- **Stage 3, the humid-column shower gate** (Bretherton exp(15.6 r)): dries SE USA and SE China further, since
  their summers run 4-6 C warm in the first-pass temperatures (PW-352).
- **The air-mass trigger reference:** not tried (decision 3 makes it conditional on PW-352).
- **An eddy closure on the actual vapour gradient:** small gain, wets the Gobi.
- **A uniform 0.53 share of the land-sea wind:** kills the monsoons.
- **Removing PW-016's spin-up rule:** it is already inert on Earth. Not removed, since the Atlantic's E-P-R is
  +0.20 Sv (< 0.25).
- **The coordinator's decisions:** stage 1 does not merge alone (it regresses Earth at L7); stage 2 does not
  merge as is.

## Root causes established
1. **The cold half's offshore winds.** In the cold half the vapour rode the continents' shallow cold outflow
   offshore on all subtropical east coasts. Fixed in 326e482.
2. **Winter coasts still dry** (SE USA Oct-Mar PW 4.6 vs NCEP 17.4 mm):
   - the model's winter wind there is offshore westerly/north-westerly;
   - it has no winter oceanic subtropical highs, hence no southerly return flow;
   - the saturation-gradient eddies give only 0.3-1.2 m/s onshore.
3. **The one-layer column under the bulk formula:**
   - The subtropical sea columns sit at q/qs 0.5-0.6, so their own rain is low (20-40 deg sea P 300-450 vs
     700-1160).
   - So land takes too much of the fixed global mean (land P 1153 vs 791; land 50-60N 1175 vs 584).
   - The ITCZ evaporates too little (its convergent column is near saturation).
4. **The east coasts' summer warmth** (+4.6..+6 C) is in the first-pass air temperatures, not the evaporative
   split (PW-352 draft).

## Option A as built in e26422b
Design in pw015-rain.md §10.
- **`_rain` is two-layer.**
  - Boundary layer m_b (the lowest `bl_m` = 1000 m: w_b = 1 - exp(-1000/2000) = 0.39 of a uniform column) and
    free troposphere m_f; humidities q_b = m_b / w_b, q_f = m_f / (1 - w_b).
  - Sea bulk flux into the BL against q_b; land evaporation into the BL.
  - Entrainment x = dt·`bl_entrain`(5 mm/s)/2000·(q_b - q_f).
  - Per-layer oversaturation and large-scale rain on each layer's own humidity; showers triggered by q_b,
    applied to both layers.
  - At one humidity in both layers it reduces to the one-layer kernel.
  - Returns (r, r_ls, up, q_b, m_b, m_f, ema).
- **`_rain_args(grid, elev, seasons_b, seasons_f, ...)`** builds the two transports at a shared dt
  (`_transport` takes an optional dt).
- **`rain_phases`:**
  - The BL rides `v_surf`: the climate's surface wind v_jul/v_jan, polar drift included.
  - The FT rides `v_belts + deep (v - v_belts)`: deep = 1 at sea, the wetness on land lows, 0 on land highs.
    Phase 1 has the FT on v.
  - `compute` puts v_surf, v_belts and low into the season inputs.
  - SHALLOW_S is gone (the layer is the shallowness).
- **Done:** an L4 smoke test runs (`climate.compute`).
- **Untested:**
  - Earth numbers.
  - The two-layer probe in tools/moisture_budget.py (spliced, never run).
  - `tests/test_rain_transport.py::test_no_rain_from_a_dry_column`: it indexes args `a[-2]` as m0, now
    `a[-3]`/`a[-2]` are m_b/m_f and it unpacks 6 outputs; fix to 7.
  - test_moisture_budget, the goldens, cost.
- **Next steps:**
  1. Fix those tests and run them.
  2. earth_check L6 and L7, and the box diagnostic for the winter coasts. Test the coordinator's claim that the
     BL on the surface wind carries winter Gulf/Pampas vapour inland. My expectation: not with the current
     surface wind (see root cause 2), but the subtropical sea columns should moisten.
  3. Then up to ~3 nudge rounds on `bl_m` (0.5-1.5 km) and `bl_entrain` (3-8 mm/s) only.

## Success bar (coordinator, verbatim)
- Earth at L6 and L7:
  - Köppen group and exact both at or above main.
  - Arid share within 5 points of 30.1.
  - Land rain within 20% of 791 mm at both levels.
  - SE USA and Pampas each at least 60% of observed annual rain.
  - India not drier than main.
  - Vapour books still close.
- Generated planets (health --quick):
  - Arid share 25–35%.
  - Icehouse ice sea level no deeper than −250 m on every seed.
  - NPP at least 300.
- L7 climate update at most 2× main's 2.2 s.

If you meet the bar: report back for merge with health before/after, earth_check and scorecard, and regenerated goldens.

If you can't meet it: stop, report the closest result and what is still missing. PW-015 then parks with the branch kept, and the run lane moves on to PW-380.

## Commands (from the worktree; `mkdir -p data && ln -s /data/personal/repos/procedural-world-generation/data/earth data/earth` first)
- **earth_check:**
  ```
  NUMBA_NUM_THREADS=8 PYTHONPATH=. uv run python tools/earth_check.py --level 6 --json ec_L6.json
  NUMBA_NUM_THREADS=8 PYTHONPATH=. uv run python tools/earth_check.py --level 7 --json ec_L7.json
  ```
  It includes the moisture headlines.
- **Moisture budget:** `NUMBA_NUM_THREADS=8 PYTHONPATH=. uv run python tools/moisture_budget.py --level 6`. It
  has the per-region table, the zonal E-P and the residence.
- **Ice probe:** `NUMBA_NUM_THREADS=8 PYTHONPATH=. uv run python tools/ice_probe.py 0 -6 --regions`
- **Health:** `PYTHONPATH=. uv run python tools/health.py --quick --workers 8 --threads 1 --no-determinism --out <worktree>/docs/review/health-rain-<tag>`
  (~15-20 min; it deletes its L6 runs).
- **Scorecard:** `PYTHONPATH=. uv run python tools/scorecard.py --jobs 3 --threads 2` (~22 min; appends to
  docs/scorecard.jsonl).
- **veg_check:** `tools/earth_world.py --level 6`, then `tools/veg_check.py` (soil_check, coastal_check
  likewise). Delete `worlds/ runs/ grids/` afterwards.
- **Timing:** time `climate.compute(grid, elev, 0, 23.4, ice)` on `earth_data.earth_on_grid(build_grid(7))`,
  the second call after a warm-up. Main's is 2.2 s on the Threadripper at 8 numba threads.
- **Tests:**
  ```
  uv run pytest -q
  uv run pytest tests/test_golden.py --update-golden
  ```
  Regenerate the goldens (climate_L4, sim_L4_s1_60myr) whenever the outputs change.
- **Health sweeps:** `docs/review/health-rain-before/` (main b8872f2), `health-rain-s1/` (1af9a9b),
  `health-rain-after/` (ecffcb9), `health-rain-s2b/` (326e482).

## Open inbox drafts on the branch
- east-coast-summers-first-pass (PW-352)
- subtropics-dry-after-bulk-evaporation (needs-decision; option A chosen)
- zoom-lakes-penman
- rain-warm-start-in-runs
- pw016-spin-up-status
- moisture-budget-l7-drainage
- pw304-land-books-residue
- pw300-after-pw358

## Update (2026-10-16, second agent): option A measured; misses the bar, PW-015 parks
- Fixed `test_no_rain_from_a_dry_column` (both layers dry, 7 outputs). The two-layer moisture_budget probe runs:
  books -0.10 / +0.01% (L6), -0.15 / +0.06% (L7).
- **Boundary-layer storm eddies** (`storm_k_bl` 1.3e6, `storm_eddies` with `q_eddy`): down the gradient of the
  first phase's boundary-layer vapour, as a velocity.
  - The winter SE USA gets +1.07 m/s onshore, but q_b/qs only rises 0.23 -> 0.29 and its Oct-Mar rain stays ~20.
  - The Gobi's extra rain comes in **summer** (B 0.70; winter B 1.08, the same as the SE USA). It is not the free
    troposphere: the flux is in the boundary layer only. Storminess in continental interiors is the cause
    (draft winter-coast-eddy-flux).
- **Large-scale rain gated by q_b in both layers:** land P -60, Atlantic E-P-R 0.16 -> 0.01 Sv. Reverted.
- **bl_m 0.5-1.5 km, bl_entrain 3-8 mm/s:** land P stays 1173-1207. Kept bl_m 500 m (SE USA best).

| Earth (GPCC) | main L6 | 326e482 L6 | A r0 (1 km) L6 | A final L6 / L7 | bar |
|---|---|---|---|---|---|
| Koppen group / exact | 71.0 / 32.7 | 72.2 / 36.2 | 71.1 / 36.0 | 71.0 / 35.8 ; 70.1 / 35.1 | >= main |
| arid % (30.1) | 20.3 | 31.0 | 31.3 | 32.2 ; 32.6 | 25.1-35.1 |
| land P (791) | 993 | 1153 | 1192 | 1177 ; 1178 | <= 949 |
| SE USA (1328) | 1343 | 757 | 596 | 791 ; 896 | >= 797 |
| Pampas (943) | 703 | 237 | 205 | 226 ; 228 | >= 566 |
| India (main 711) | 711 | 551 | 576 | 555 ; 537 | >= 711 |
| Gobi (157) / Tibet (296) | 582 / 76 | 196 / 12 | 349 / 13 | 345 / 12 ; 301 / 11 | |

- **Ice probe dT 0 / -6:** 3.77% / -187 m (main 2.54% / -58; 326e482 3.20% / -149).
- **L7 climate update:** 5.1 s on this machine (2.3x main's 2.2 s).
- **Health --quick** (docs/review/health-rain-optA/; mean of per-seed medians): arid 41.2% (main 29.3, 326e482 37.8), NPP 275 (334 / 304), deepest icehouse ice sea level -258 m (seed 1; main -228, 326e482 -491). This misses all three generated-planet bars.
- **What is missing:** the land/sea split. Subtropical sea q_b/qs is only 0.62-0.64 and sea P 20-30N ~290
  (GPCP 714). Land P/PW runs ~2x observed and rises inland. The showers rain both layers whatever the free
  troposphere's humidity, and the stage-3 gate on that waits on PW-352. The winter coasts need frontal lifting
  and winter subtropical highs (PW-026), not more transport.
- `tests/test_health.py::test_frame_rivers_end_in_its_own_hollows` fails with these outputs (t=240, cell 2082).
  Not investigated, since PW-015 parks.
