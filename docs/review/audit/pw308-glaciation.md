# PW-308: why runs stopped glaciating after the audit fixes, and the fix

Branch `worktree-agent-afc1230cc5c7e0e54`, on main 4326d64. The fix is one commit (5e24aa9). Measurement tool: `tools/ice_probe.py`.

## Short answer
- **Cause: PW-266's sea-ice lid.** PW-266 rightly stopped the rain kernel's air from taking up water through sea ice as if it were open sea. But it made frozen months give the air nothing at all. In a cold era the pack ice spreads over the polar seas, so the polar continents' snow collapses as the planet cools: Earth L6 at dT -6 gets 18 mm/yr on Antarctica, against 92 at dT 0 (-80%). Ice cores give about -50% at the LGM. The sheets starve, so cold planets (global 3-6 C) only reach -20 to -50 m.
- Before the audit the error ran the other way. Sea ice was a full vapour source, so a colder planet got *more* polar snow (+33% on Antarctica for -6 C). That bandaid hid the missing process.
- **Missing process: leads and polynyas.** Winter pack ice is never a closed lid. The central Arctic is ~1-3% open water in winter, the Antarctic pack ~5-20%, plus coastal polynyas. The very cold, dry air over that open water takes up water fast. **Fix:** the air takes up water through a share `TUNE['leads'] = 0.1` of a frozen sea's surface, as well as through the open months (`open_y + leads x (1 - open_y)`). It adds no ice-growth term and leaves the ice rule unchanged.
- PW-276/277 (the ice changes), PW-264/278 (CO2) and PW-288 (sea level) don't explain the loss: on a fixed planet they change Earth's ice response by ~1 m. In runs, reverting any one change re-rolls the chaotic history.

## 1. Bisect in runs (3 L6 seeds, 1 Gyr, `--every 4`; each revert applied on main 4326d64)
Deepest sea level from ice (m) / share of keyframes below -50 m / the coldest global temperature (C).

| variant | seed 11 | seed 42 | seed 2 |
|---|---|---|---|
| main | -22 / 0% / 5.6 | -27 / 0% / 8.5 | -48 / 0% / 2.9 |
| revert PW-277 (one ice-surface climate) | -96 / 5.5% / 4.6 | -29 / 0% / 7.9 | -128 / 5.9% / 3.0 |
| revert PW-276 (sheet surface from the margins) | -36 / 0% / 5.8 | -61 / 2.5% / 9.4 | -225 / 12.2% / 4.0 |
| revert PW-264 (CO2 baselines over 1 Gyr) | -17 / 0% / 5.6 | -18 / 0% / 9.1 | -113 / 16% / 3.4 |
| revert PW-278 (WEATHER_K 0.09) | -26 / 0% / 5.6 | -12 / 0% / 9.8 | -111 / 9.7% / 3.6 |
| revert PW-288 (sea level from the starting floor, slab drag) | -167 / 6.7% / 2.6 | -40 / 0% / 8.9 | -243 / 11.8% / 2.0 |
| revert PW-265 (moc_zonal 1) | -18 / 0% / 6.2 | -38 / 0% / 7.5 | -90 / 7.6% / 2.9 |
| revert PW-266 (rain kernel recycles the water balance) | -150 / 5.5% / 4.8 | -56 / 2.1% / 8.4 | -152 / 11.8% / 3.1 |
| pre-audit sweep, for scale (docs/review/health/2026-10-15) | -384 | -128 | -223 |

(PW-275 only touches the time zoom, so it has no run of its own.) Every revert glaciates more than main on seed 2, and none is clearly decisive. Each change re-rolls the run's chaotic history: geography, CO2 and drift. Seed 42 now stays warm (≥ 7.5 C) in every variant. So the runs alone can't attribute the loss.

## 2. Attribution on a fixed planet (`tools/ice_probe.py`)
The probe runs the run's ice rule (`earth.ice_sheets` after `climate.compute`, glacial isostasy, 8 climate updates) on Earth's L6 bed at a fixed dT, starting from Earth's real ice. Sea level is fixed, and nothing is chaotic. The table gives the sea level from ice after the 8th update (m; ice share of the surface).

| variant | dT 0 | dT -6 | dT -9 |
|---|---|---|---|
| pre-audit main (019b97f) | -0.8 (0.2%) | -115 (6.6%), still growing | -161 (8.4%) |
| main | -0.4 (0.1%) | -7.5 (0.8%) | -17 (1.5%) |
| main, PW-277 reverted | -0.3 | -7.2 | |
| main, PW-276 reverted | -0.3 | -7.8 | |
| main, PW-276 + PW-277 reverted | -0.3 | -7.8 | |
| main, PW-265 reverted | -0.3 | -6.6 | |
| main, PW-266 reverted | -1.1 | -110 (6.5%) | |
| main, sea ice a full source again (diagnostic) | -1.0 | -117 (7.0%) | |
| **fix: leads 0.1** | -0.5 (0.1%) | **-44 (3.1%)**, steady | **-75 (5.2%)** |
| leads 0.1 as a floor, `max(open_y, 0.1)` (tried) | | -44 | -65 |

(The first probe pass pressed ETOPO's bed down twice. The rows above come from the corrected probe, except the PW-277 / PW-276 / PW-265 / PW-266 rows, which come from the first pass: within ~1 m of the corrected pass at dT 0 and -6.)

Only PW-266 matters on a fixed planet. Rain over the ice sheets at fixed dT (`climate.compute` on Earth's real ice, mm/yr):

| | Antarctica dT 0 / -6 / -9 | ratio -6/0 | Greenland dT 0 / -6 | ratio |
|---|---|---|---|---|
| sea ice a full source (pre-audit kernel, PW-266 reverted) | 118 / 176 | 1.49 | 239 / 355 | 1.49 |
| main (sea ice a lid) | 92 / 18 | 0.20 | 195 / 49 | 0.25 |
| leads 0.05 | 96 / 44 / 44 | 0.46 | 203 / 117 | 0.58 |
| **leads 0.1 (fix)** | 97 / 66 / 69 | 0.68 | 207 / 162 | 0.78 |
| leads 0.2 | 105 / 94 / 104 | 0.90 | 217 / 213 | 0.98 |

Observed: LGM accumulation on the East Antarctic plateau was ~50-60% of the Holocene's (EPICA Dome C, Vostok), and on central Greenland ~30% (GISP2, Cuffey & Clow 1997). Clausius-Clapeyron at the model's 0.06/C gives 0.70 for 6 C. With 0.1, Antarctica sits near Clausius-Clapeyron, a little wetter than the cores. Greenland comes out too wet against GISP2, but its LGM dryness also comes from the Laurentide's shadow and regional cooling well beyond 6 C. I took the middle of the observed winter-pack range rather than fitting the probe.

## 3. Mechanism
At a given dT, a sheet grows where snow outlasts the summer and its snow surplus pays for the melt of its ablation zone (`icemass.balance`, `earth.ablation_zone`). The run's dT already counts the ice-albedo feedback, so a cold era is where sheets should grow. In such an era the sea within ~1000-2000 km of the polar coasts freezes over in every month (`ocean.open_share` = 0). With the lid, the kernel's air crosses that belt with no source and keeps raining out (large-scale rain, `ls`). It reaches the continent with a fifth of its vapour, and snowfall falls ~5x faster than Clausius-Clapeyron. Accumulation falls below the melt of a growing margin, so the sheets shrink back to their high, cold cores. In a run, a cold era at global 3 C (seed 2) peaked at -48 m. The smaller ice extent then also weakens the albedo cooling (`ice_frac` in `global_temperature`), so cold eras end sooner.

Why the ice and CO2 changes aren't the cause: PW-277 changes the ice extent only through the softness factor, by ≤ 30% of the thickness. PW-276 thins ice over high beds inside a sheet. Both move the Earth probe by < 1 m. PW-264/278 change how cold eras arise, not how much ice a cold era makes. Coldest-era temperatures are about the same before and after (pre-audit sweep 1.0-10.9 C, post-audit 2.9-11.1 C), while the ice per degree of cooling fell ~5x.

### The coordinator's question: PW-288's high tectonic sea level
Since PW-288 the tectonic sea level sits around +140 m, which floods high-latitude lowlands. As a diagnostic only, I forced `sea_tect = 0` and ran seeds 11 / 42 / 2:

| | seed 11 | seed 42 | seed 2 |
|---|---|---|---|
| main | -22 | -27 | -48 |
| main, sea_tect = 0 | -38 | -17 | -98 (coldest 1.3 C) |
| fix (leads 0.1) | -322 | -16 | -125 |
| fix, sea_tect = 0 | -161 | -19 | -113 |

A sea at +140 m costs some ice: main with sea_tect = 0 gains on seed 2, which also got colder. But it isn't what stopped glaciation. Without the leads, a 0 m sea still leaves seeds 11 and 42 with no spell below -50 m. With the leads, the sea level makes no consistent difference, and the fixed-planet probe (sea level fixed) shows the whole loss. PW-293 (re-centring sea level) can go ahead independently.

## 4. Measurements with the fix
`tools/health.py --l6 1 2 11 21 3199 42 77 505 --l7 --myr 1000 --workers 8 --threads 2` (docs/review/pw308/health/; run on 4326d64 + the fix's working-tree edit, identical to 5e24aa9). Determinism re-run identical.

Deepest ice sea level (m) and icehouse spells (keyframes below -50 m, joined across gaps of ≤ 5 frames) per seed:

| seed | pre-audit (health/2026-10-15) | post-audit (after-audit-2026-10-15) | fix |
|---|---|---|---|
| 1 | -96, 4 spells | -23, 0 | -26, 0 |
| 2 | -223, 2 | -48, 0 | -125, 2 |
| 11 | -384, 2 | -22, 0 | -322, 1 |
| 21 | -131, 2 | -21, 0 | -82, 2 |
| 3199 | -205, 2 | -9, 0 | -56, 1 |
| 42 | -128, 2 | -27, 0 | -16, 0 |
| 77 | -231, 3 | -24, 0 | -63, 2 |
| 505 | -154, 2 | -18, 0 | -15, 0 |
| spells in all | 19 | 0 | 8 |
| coldest-era global T, range (C) | 1.0-10.9 | 2.9-11.1 | 3.2-11.5 |
| keyframes with ice SL < -150 m, worst seed | 11.3% (s11; s2 25.6% < -100) | 0 | 7.1% (s11) |

L6 means of the per-seed medians (pre / post / fix): temperature 14.7 / 15.2 / 15.2 C, ice share 1.7 / 0.7 / 0.8%, arid share of land 30.4 / 26.7 / 23.5%, tree cover 32.4 / 29.6 / 32.6%. The arid share fell ~3 points, but on Earth's own terrain the B share is unchanged (earth_check below). The drop is likely chaotic, plus cold eras being wetter at high latitude.

Five of eight seeds now have 1-2 icehouse spells per Gyr (Earth ~4), mostly -55 to -125 m. Seed 11's 180-264 Myr cold era reaches -322 m at global 3.2 C (the pre-audit sweep had -384 m on the same seed). That's deep but not runaway: it ends, and it stays under the 10% envelope for keyframes below -150 m. Seeds 1, 42 and 505 never get colder than 8.9-11.4 C, so they stay ice-light. The remaining gap to Earth (dT 0 holds no ice at all, see the draft below) is pre-existing.

**earth_check** (L6, against docs/review/after-audit-2026-10-15/earth_check.txt): Köppen group 71% / exact 33%, unchanged; global P 998 and global T 14.5 C, unchanged. Land rain 80-90 N 102 → 139 mm (GPCC 168), 70-80 N 226 → 247 (227), Greenland 218 → 229 (359), Antarctica 70-80 S 187 → 200 (GPCP 412). Rain elsewhere moves by < 3 mm.

**Earth time zoom** (`planet timezoom earth --kyr 150`, same machine): main lowest -17 m at 70 kyr (3 glacial events); fix -23 m at 82 kyr (2 events). The LGM was ~-120 m. Earth's time zoom never gets far from dT 0 (its global change stays within -0.9 C), so its sea ice is near today's, where the leads hardly matter. The weak Earth cycle is PW-033 (no Laurentide or Fennoscandian ice) and the dT-0 problem below, not this fix.

**scorecard** (seeds 1, 2 at 1000 Myr; not appended, to keep the branch mergeable): Earth group 71.3% / exact 33.0% / log-rain corr 0.61 (before 71.2 / 33.0 / 0.61). Seed 1: dry 27.3%, ice 0.7%. Seed 2: dry 16.4%, ice 1.6%.

## 5. Left over
- `draft-run-ice-cannot-hold-antarctica.md`: on Earth's real ice at dT 0, the run's ice rule decays to 0.1% of the surface in every version (pre-audit too). Antarctica's low cells have a +13 C bare-ground summer (PW-112) and too little snow. Icehouses need ~-5 C more than Earth does.
- The kernel takes up water through the year's open share in both half-years. A per-half-year share (open summers, frozen winters) would be more exact. It doesn't matter for cold eras, where both halves are frozen, so no ticket.
