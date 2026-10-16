# Icehouse depth (PW-364; with PW-365, PW-360 C, PW-338)

Run-physics lane, 2026-10-16. Branch `worktree-agent-af88781fac4d4cbc3` (main dcf6cba + the time zoom batch). Tools: `tools/ice_probe.py` (now `--level`), scratch probes that run the same ice rule on a traced run's own geography, and `tools/health.py --quick` (8 L6 seeds x 500 Myr, `--workers 8 --threads 1 --no-determinism`): `docs/review/health-ice-before/` (main), `health-ice-after/` (settled ice + PW-365), `health-ice-final/` (+ PW-360 C + PW-338).

## Short answer
- **The depth is a genuine geography, not a runaway.** The L5 envelope world (seed 1 + PW-338's patch) went through its icehouse with a continent drifting over each pole (land poleward of 60 deg: N 52 -> 90%, S 25 -> 87% over 264-360 Myr), standing ~1.1 km high (Earth's ice-free polar land: 0.37 km), on an old ocean (sea_tect -250 m), when the climate drift dipped to -4.7 C. On that fixed geography the ice rule's fixed point at dT -4 is **-576 m over 16% of the surface** (mean ~2.5 km: a Nye profile on sheets ~3x Antarctica's area), against Earth's -67 m at dT -6 (-168 m once the sea answers). The ice albedo adds at most -1.4 C (it levels off, as designed); CO2 *rose* as the ice covered the weathering land (-1.9 -> -0.2, the thermostat working). The steepest feedback is the sheets' carried air (PW-336): without it the same fixed point is -223 m / 9.0%. It holds land margins at ~52 deg, where the bare ground's summer is +14 C and the margin cell's own sheet air brings it to +10 C. Antarctica validates that air (margin summers within 1-3 C of NCEP; without it 5-12 C too warm), and no Earth sheet today has a land margin at 50 deg to test it. Not an error I can name.
- **"10% ice at 12.4 C for 60 Myr" was mostly a model error: lag.** The run made one ice pass per climate update. A pass moves a margin about one cell (its new margins' lower Nye surface melts next), so a sheet took ~20 updates (~80 Myr) to grow into a cold era or shrink out of one, where real sheets settle in 10-100 kyr. The 12.4 C ice was grown at 10.2 C (dT -4.3) and not yet melted. There is also real hysteresis: from the run's ice at dT +1.6 the rule settles at -163 m / 6.9%, from no ice at -32 m / 4.0% (a big sheet keeps itself cold).
- **Fixed (PW-364):** `earth.ice_sheets` repeats its pass under the step's climate until the iced cells repeat, each pass on the bed its ice presses down (glacial isostasy), the bare ground shifted by the lapse rate. Without the bed in the passes, climate and ice 2-cycled (-253 / -49 m on alternate updates). The rest of the climate (carried air, albedo, rain) follows at the next update, as CO2 does. Re-computing the climate within the step whenever margins moved was tried: +78% climates at L5, mostly for a few margin cells shuffling. Dropped.
- **Consequence: cold eras are deeper and shorter.** Seed 11's L6 cold era (same trajectory before and after; global 2.3-5 C, dT -9.5..-12) reaches -346 m where the lagged ice was still at -160 m and growing, and is back to -25 m at 280 Myr (was -63). In the after sweep one seed of eight crossed PW-240's -250 m (11: 14% of frames). In the final sweep (PW-338 re-rolls the histories) none does: deepest -219 m at 4.6 C. The depth follows dT and geography soundly. Narrowing the drift is the owner's call (draft).
- **PW-365 (one line, as the time zoom's `orbit_k`):** the run's cycle-averaged balance counted the open sea as fully absorbing land in the orbital mix. Earth probe at dT 0: **1.97% and falling -> 2.53% steady** (Antarctica 824 cells, Greenland 164: PW-313's ~3% nearly met). Cooling side unchanged. It is not why cold eras run deep.
- **PW-338:** with the settled ice, `tests/test_envelopes.py` passes with the patch, bands unchanged (arid 340-400 Myr: seed 1 23.0%, seed 2 25.7%). That is a chaotic re-roll (seed 1 no longer meets the polar continents), so the test's fragility stays: draft `draft-envelope-dry-window.md` (lean: average 100-400 Myr).
- **PW-360 C:** the overturning iterates past the spin-up's 4 iterations until the inflow share moves < 0.003. Earth north 10.0 -> 11.3 Sv (= 30 iterations), south 2.61 -> 2.51. Generated moments move <= 0.5 Sv (one southern site 19.9 -> 16.3 Sv). 10-22 iterations instead of 4: ~+0.1-0.15 s per climate (~+1 s per 260 Myr L6 run measured; large share of an L5 climate, ~3% at L7).

## 1. The envelope world's cold era (L5 seed 1 + PW-338 patch, pre-PW-364 code)
Global temperature terms (`earth.global_temperature`), C:

| Myr | dT | drift | CO2 | ice albedo | ice % | ice SL m | land >60N / >60S % |
|---|---|---|---|---|---|---|---|
| 264 | +1.0 | | | +0.6 | 1.8 | -13 | 48 / 5 |
| 296 | -2.0 | -2.2 | -1.6 | +0.2 | 2.9 | -22 | 53 / 30 |
| 308 | -4.3 | -4.7 | -0.7 | -0.5 | 5.7 | -83 | 56 / 45 |
| 320 | -3.1 | -1.1 | -0.3 | -1.1 | 8.2 | -189 | 62 / 59 |
| 344 | -1.3 | +1.5 | -0.3 | -1.4 | 10.7 | -293 | 81 / 78 |
| 356 | +1.6 | +4.4 | -0.2 | -1.4 | 10.8 | -298 | 90 / 87 |
| 392 | +2.6 | +2.8 | +0.6 | -0.4 | 3.7 | -63 | 52 / 93 |

(The sea at -516 m in the ticket is this -298 m of ice plus the old ocean's -218 m.) The polar land is drift, not exposed shelves: the land at the ice-free sea level matches within 1%. Hypsometry: polar land (|lat| > 55) mean 1.1 km, median 0.7 km (Earth's ice-free polar land 0.37 / 0.26).

Arid share (envelope test's metric), from the trace: not mainly the ice. By 384-400 Myr only ~38% of land lies below 35 deg and the young ocean floods the planet (land 33 -> 27%, land rain 960 -> 1250 mm); low-latitude land is 10-17% arid (49% at 264 Myr). Arid of land / of ice-free land: 344 Myr 9.6 / 14.2%, 400 Myr 4.2 / 4.8%.

## 2. The ice rule on that geography (fixed dT and sea level, from no ice; fixed point)
| (final code; env. 14 updates, Earth 10) | env. world @344 Myr, dT -4 | Earth L5, dT -6 (from today's ice) |
|---|---|---|
| all feedbacks | -576 m, 16.1% | -67 m, 4.4% |
| + sea level answers the ice | -628 m, 17.5% | **-168 m, 8.5%** (shelves glaciate; still growing) |
| + ice albedo in dT | -579 m | -65 m |
| no carried sheet air (PW-336) | **-223 m, 9.0%** | -61 m, 3.9% |
| sheet air x0.5 (diagnostic) | -307 m, 11.4% | -66 m |
| no leads (PW-308) | -558 m | -42 m |

On the same geography from no ice (final code): dT +1.6 -32 m, 0 -62 m, -1.3 -204 m (still growing), -4 -576 m. From the run's ice at dT +1.6: -163 m (the iced branch). So the response is steep on this geography, mostly through the carried air over continuous land (-576 vs -223 m without it). Earth's own curve is a weak yardstick. Its probe holds the sea fixed. With the sea answering, Earth reaches -168 m at dT -6 and is still growing, near the real LGM's ~-185 m in the model's terms (the model counts all land ice: today's ~65 m of SLE plus the LGM's 120). And its NH barely glaciates (dT -6: 680 non-polar cells; no Laurentide, PW-033). The PW-240 goal (-150 / -250 m) was stated against "Earth's LGM ~-120 m", which is the change from today, not the total.

## 3. The lag and its fix
One pass at a time on the run's ice at 356 Myr, dT +1.6, climate held: the sheet loses ~50 cells a pass (1055 -> 441 cells over 20 passes), then 2-3 margin cells flicker between two passes. Under the old map each pass was one climate update (4 Myr). From the run's ice at dT +3 the old map took ~20 updates to settle (-34 m / 3.7%).

`ice_sheets` now repeats `_ice_pass` until the iced set repeats (a fixed point or a 2-cycle), each pass on `bed + sink - ice_load(ice)`, the ground's temperatures by `-LAPSE x` that rise; `update_climate` passes `sim.ice_sink`. Passes per update on the L5 trajectory: 2 (57 updates), 3-5 (43), up to 9. Cost: L5 400 Myr 28 -> 30 s; L6 seed 11 0-260 Myr (a big icehouse) 66 -> 81 s (+23%, all of it ice: 3 -> 18 s). `ice_sheets` is 0.07 s a pass at L6, 0.26 at L7.

Earth probe, L6, 8 updates (sea level m / ice % after updates 1, 4, 8):

| dT | main | settled ice | + PW-365 (final) |
|---|---|---|---|
| 0 | -38 / -31 / -27 m; 2.41 / 2.20 / 1.97%, falling (Antarctica 726 cells) | -30 / -22 / -21; 1.67% steady (632) | -40 / -36 / -36; **2.53% steady** (824; Greenland 164) |
| -6 | -40 / -45 / -51, growing | -53 / -56 / -57 | -57 / -56 / -58 |
| -9 | -47 / -61 / -72, growing | -70 / -75 / -80 | -63 / -65 / -66 |
| -12 | -61 / -94 / -119, growing | -138 / -141 / -146 | -130 / -141 / -149 |

(The old map's dT 0 reaches ~1.9% after ~12 updates. Its "2.33% after 8" in the polar-bundle write-up was a transient.)

## 4. Health --quick (8 L6 seeds x 500 Myr, frames after 50 Myr)
Deepest ice sea level (Myr, global T); spells below -50 m (gaps <= 5 frames joined); % of frames below -150 / -250 m:

| seed | before (main) | after (settled ice + PW-365) | final (+ PW-360 C + PW-338) |
|---|---|---|---|
| 1 | -26 (500, 10.1 C); - | -125 (500, 8.5); 480-500 | -117 (500, 9.4); 492-500 |
| 2 | -285 (500, 3.2); 468-500 (T 3.0-8.8); 4.4 / 1.8 | -138 (500, 2.1); 472-500; 0 / 0 | -141 (500, 2.7); 480-500; 0 / 0 |
| 11 | -165 (196, 4.9); 172-284 (T 2.4-13.8); 7.1 / 0 | -352 (212, 6.5); 168-276 (T 2.3-14.1); 18.6 / 14.2 | -219 (192, 4.6); 168-232 (T 1.6-11.0), 364-452 (-109 m, T 8.5-14.3); 7.1 / 0 |
| 21 | -7 | -8 | -10 |
| 3199 | -12 | -36 | -67 (500, 10.5) |
| 42 | -103 (496, 10.5); 444-500 | -112 (464, 7.2); 428-500 | -82 (500, 10.7); 440-500 |
| 77 | -18 | -83 (452, 8.2); 296-320, 440-464 | -82 (460, 9.3); 3 short spells |
| 505 | -8 | -37 | -17 |
| coldest T range | 2.4-12.3 C | 2.1-12.5 C | 1.6-12.0 C |

Runs re-roll after a change, so compare the distributions. Seed 11 is a clean pair (same geography and dT to ~260 Myr; section 3's consequence). In the final sweep no frame is below -250 m and every seed's deepest ice sits in an era colder than 10.7 C; the deepest spells are LGM-cold or colder (1.6-9.4 C). Sim times: 279-286 s before, 352-513 after, 372-601 final, but the last two ran beside another agent's four ~200% processes. Measured alone (section 3), the settled ice costs +23% on the icehouse-heavy seed 11 and +7% on the L5 world.

## 5. earth_check
Final code (only PW-360 C reaches earth_check, which uses Earth's own ice): Koppen group 71% / exact 33% (unchanged), global T 14.5 C, P 998 mm, point check 29 exact / 34 group / 15 wrong (night baseline 28/34/16). Earth overturning north 11.3 Sv, south 2.5 (was 10.0 / 2.6).

## Left over (inbox drafts; ticket updates)
- `draft-envelope-dry-window.md` (needs-decision): the envelope test's single 60 Myr window is chaos-fragile; lean average 100-400 Myr.
- `draft-climate-drift-drives-cold-eras.md` (needs-decision): the drift (sd 3 C) makes the cold dips; PW-240's decision to narrow it was never applied. Lean: leave it, the owner's call.
- PW-366 updated: cold-era depth comes from extent; thicker sheets would deepen it further; reconcile with PW-015's margin snowfall.
