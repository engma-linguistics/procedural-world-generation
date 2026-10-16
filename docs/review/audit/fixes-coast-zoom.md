# Audit fixes: coast and zoom synthesis (2026-10-15)

Fix agent for the [coast-zoom audit](coast-zoom.md): PW-269, PW-273, PW-271, PW-270, PW-272, PW-268, one commit each (plus one for the shared U_TRADE/U_STORM refit). No run, climate or golden output changes (the coast layers and zooms are world-level; goldens unchanged).

**Measurement notes.** `tools/coast_check.py` can't run on this machine as is: building `data/earth/L6.npz` needs the Köppen file, whose server resets the connection (draft `draft-earth-data-koppen-download.md`; the coordinator's baseline `earth_check.txt` is that traceback). coast_check was run through a scratch wrapper that builds only the elevation/ice half of `earth_data._build` (same terrain, same model climate, nothing cached). "Before" is main's code. Zooms: an L7 seed-3199 400 Myr run of this branch (world at `--at auto` = 360 Myr), plus the audit's world 592f2a read from the main checkout; 2000 km at 4 km/px, `zoom.build(..., seed 1, 15 iterations)`, in memory.

## Waves and tides (coast_check, Earth L6)

| | main | after PW-270 | + PW-272 | + refit (final) |
|---|---|---|---|---|
| waves in range / within 2× (of 33) | 13 / 28 | 14 / 24 | 11 / 23 | 4 / 24 |
| open-ocean coasts (18): rms log error, bias | 0.61, −0.17 | 0.87, −0.63 | 0.61, −0.30 | **0.53, +0.03** |
| enclosed seas (11): rms log error, bias | 0.82, +0.20 | 0.72, −0.20 | 1.27, +1.11 | 1.56, +1.44 |
| tides in range / within 2× (of 26) | 16 / 24 | | | 12 / 22 (PW-273) |

- **PW-270** grows the sea under four Weibull speeds instead of 1.43 × U: the right moment per regime. Ray cost ~2.5× (Earth L6 wave_power 2.7 → ~5–6 s).
- **PW-272** `LAND_SLOW, L_RECOVER` 0.5, 1200 km → 0.3, 50 km (physical; the approved lean A).
- **Refit (a re-centring both tickets name):** `U_TRADE, U_STORM` 6.5, 6.0 → 7.0, 7.0 m/s, least squares of log(model / middle of the observed range) over the 18 open-ocean rows only (6×6 grid; flat valley along U_TRADE + U_STORM ≈ 14). The count "in range" fell because many rows now sit just outside their ranges; the open-ocean error is the lowest of the four columns. The enclosed seas are 3–5× too strong (Baltic 30 kW/m against 1–6): the 1200 km recovery had been hiding that their winds are the open sea's. Draft `draft-coast-enclosed-sea-winds.md` (relates PW-075).
- **PW-273** (no clamp; λ from the shelf's mean depth along the path; W from the coastline to the interpolated shelf break): the macrotidal shelves that sat at the clamp's peak fall (Patagonia 5.2 → 2.2 m, Yellow Sea 2.3 → 1.4, Khambhat 7.8 → 4.2, St Malo 6.5 → 3.3). Draft `draft-tides-macrotidal-shelves-off-resonance.md`.

## Deltas (PW-269)

`plain_radius_km` = 70 km × (Q / 1000)^0.35 × (0.8 + 0.6 sf), cap 350 km (was 22 km × ..., cap 300): Nile 110–140 km, Mississippi 210–265, G-B 275–350 at sf 0.5–1, within 30% of the docstring's sizes (test). Real inputs (audit's table): G-B tide 0.79–0.86, Mekong 0.70–0.79, Fly 0.89–0.93, Mississippi river 0.79–0.85, São Francisco wave 0.70–0.76.

| world 9970c1 (L7), 55 mouths ≥ 1500 m³/s | river | wave | tide | mixed |
|---|---|---|---|---|
| old radius | 30 | 21 | 0 | 4 |
| new radius | 17 | 14 | 13 | 11 |

Biggest mouth (47,400 m³/s), 1000 km zoom at 2 km: plain 112 → 349 km, land below 10 m 17,300 → 106,600 km², 1 → 4 mouths (PW-061's "fans are small"). The demo zooms 00975d / f81832 / ce4b72 no longer exist (Mac outputs). Follow-ons in the zoom, because plains this size reach far: the prodelta and the mean-correction damping act only over the shelf (with the bigger plains and no such limit, a 300 km prodelta filled the trench off 592f2a's coast: its sea cells came out +1009 m, its trenches +4323 m), tidal flats keep the prodelta's hard floor, and a delta's mouths are counted along its own channels (a 1.6 R disc took in a neighbouring river 460 km away). `test_delta_types_differ`'s zoom is 800 km at 5 km/px (300 km couldn't hold the plain); thresholds unchanged. `tools/coast_check.py`'s delta rows still use sf = 0 (the lower end of the radius).

## Zoom lakes (PW-271)

A coarse lake in the zoom loses open water's net evaporation over its area before passing its water on. Synthetic lake under a 1400 mm/yr sky: zoom outflow / coarse outflow 1.40 → 0.87 (the zoom sees ~90% of the catchment), and outflow = inflow − evaporation (test).

## Zoom cell means (PW-268)

Land cells away from the coast, bias / RMS (m), 2000 km at 4 km/px:

| zoom | before | after |
|---|---|---|
| 592f2a (−9.35, −161.39): main (the audit's numbers) | −86 / 234 | **−13 / 157** |
| ... its trench cells (< −6000 m) | 2–4 km shallow (audit) | +309 / 624 |
| ... its sea interior | +415 / 912 (audit) | +30 / 278 |
| 9970c1 tropical mountains (−15.69, 127.51) | −1 / 195 | +8 / 206 |
| 9970c1 mid-latitude hills (−48.19, −165.19) | −10 / 77 | +5 / 54 |
| 9970c1 glaciated plateau (−48.48, 60.12) | −27 / 489 | +131 / 236 |
| ... its trench cells / sea interior | +636 / 160 (rms) | +76 / 22 (rms) |

Changes: the landscape pass fits C to box means of the target before the valleys were cut (mass-neutral carving); creep's loss goes back on the hillslopes; the detail's mean correction runs 12 passes instead of 2. Stats `inland_cell_mean_bias_m`, `inland_cell_mean_rms_error_m`, with a test on the synthetic lake zoom (|bias| < 20, RMS < 120).

The bias meets the ticket's ±20 m on three zooms; the RMS < 120 m on 592f2a doesn't (157). What is left is the stream-power pass's own C fit, which settles 100–200 m off the box means it is fitted to even at 30 iterations; on the glaciated plateau it overshoots +100 m, which the carving deficit used to cancel, so that zoom's bias got worse. Scaling the relief above the drainage per cell fixed the RMS (37–115 m) but changed the landform classes' character in their tests, so it was dropped. Draft `draft-zoom-landscape-fit-offset.md`. Build time is unchanged within the noise (9–11 s per zoom at load 20–35).
