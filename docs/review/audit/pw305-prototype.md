# PW-305 prototype: a mixed-layer depth for land showers (option E1)

Prototype on branch pw305-e1-mixed-layer (commit e104331, based on main 4e5f259), **not merged**: the owner chose option A for PW-305 (2026-10-15) and folded the dry-interior problem into PW-013. Kept as input for PW-013. PW-266's fresh-water books are kept as they are.

## The physical argument
The kernel's vapour `q` is the column's water, counted in units of the sea air near the surface. Over the sea, `src_q = rh × qs(sst)` is a surface humidity, and the water lives within the vapour's ~2 km scale height. The shower trigger compares the ground air's moist static energy, `mse_t + LQ·q`, with the energy of the air aloft. That treats the column's water as if it were all in the ground air.

On hot, dry land the ground spends its energy heating the air instead of evaporating water. Dry convection then mixes the ground air through a layer that grows with that heat. Once the layer is deeper than the vapour's scale height, the same column water is spread thinner: the ground air that would feed a shower holds only `VAPOUR_H / h` of it. The rest is carried off aloft, where the large-scale rain can still take it.

So the change is:
- the shower trigger sees `LQ · share · q`, with `share = min(1, VAPOUR_H / h)`;
- `h` is the depth of a mixed layer that grows into stable air (Tennekes 1973, encroachment): `h² = 2 · (the day's sensible heat) / (ρ c_p γ)`;
- the sensible heat is `PET − AET` from the kernel's own Budyko numbers, with PET standing for the available energy.

Nothing else changes. The large-scale rain, the supersaturation rain-out, the transport and the evaporation stay as they were, so the water books are untouched. Wet land (sensible heat below ~1250 mm/yr) and the sea get `share = 1`, so their outputs are bit-identical.

The constants are physical, not fitted:
- `VAPOUR_H` = 2000 m, the scale height of water vapour;
- `γ` = 3.3 °C/km, the standard atmosphere's potential-temperature gradient (g/c_p − 6.5);
- `ρ c_p` = 1206 J/m³/°C, the heat capacity of air.

`clouds()` uses the same share for its cumulus, so the cloud diagnostic sees the same instability as the rain.

Code: `planet/climate.py`, `_mixed_layer_share` and `_rain` (`bl_share`), with the share passed to `clouds()` through the season dicts.

## Earth (earth_check L6)
| | pre-PW-266 | main (after-audit) | **E1 prototype** | E1 with steady-state depth (rejected) | observed |
|---|---|---|---|---|---|
| Köppen group / exact (%) | 71.8 / 38.9 | 71.2 / 33.0 | **71.6 / 34.3** | 71.6 / 32.8 | |
| B share of land, excl. Antarctica (%) | 28.9 | 20.3 | **21.9** | 31.7 | 30.1 (Kottek) |
| land P mean / median (mm) | 840 / 515 | 1008 / 737 | **999 / 719** | 924 / 604 | 791 / 546 (GPCC) |
| point score exact / group / miss | 33 / 27 / 18 | 29 / 34 / 15 | 29 / 33 / 16 | 30 / 28 / 20 | |
| Sahara | 205 | 328 | **294** | 218 | 35 |
| Sahel | 1679 | 2007 | 2015 | 2116 | 593 |
| Arabia | 329 | 391 | 390 | 396 | 95 |
| Australia interior | 463 | 837 | **720** | 573 | 291 |
| Gobi/Mongolia | 303 | 582 | 587 | 596 | 157 |
| Great Plains | 264 | 640 | 634 | 320 | 550 |
| W Siberia | 271 | 557 | 558 | 563 | 503 |
| Pampas | 438 | 706 | 673 | 332 | 943 |
| Amazon | 2613 | 2719 | 2723 | 2736 | 2335 |
| SE China | 833 | 1134 | 1088 | **472** | 1462 |
| SE USA | 994 | 1346 | 1347 | **518** | 1328 |
| E Australia | 916 | 1186 | 1136 | **485** | 743 |
| cloud: Sahara / Arabia / Australia int. (%) | 20 / 30 / 34 | 25 / 37 / 44 | 22 / 36 / 39 | 20 / 35 / 34 | targets 10–20 / 10–25 / 20–35 |
| fresh-water mean taken off (m/yr) | | +0.0040 | +0.0041 | +0.0000 | |

## The rejected variant
The deeper variant replaces the one-day encroachment with a steady state: the layer is as deep as it takes for clear-sky radiative cooling (1.5 °C/day) to remove the day's sensible heat. That gives realistic desert depths (Sahara ~5–6 km, Australia ~4 km, a wet forest <2 km) and brings the B share back: 30.2–32.9% for 1–2 °C/day. But it dries out the hot humid-subtropical summers: SE China, SE USA, E Australia and the Pampas fall to 30–40% of their rain.

The model's summers there are 4–6 °C too warm (Tw: SE China 29.3 against 24.5; SE USA 29.6 against 25.3; Pampas 30.3 against 25.1). That gives a high PET and a large `PET − AET`. A deeper layer means fewer showers, which means drier ground and a deeper layer still: a runaway. Obs C → model B rises to 43% of C. Exact agreement doesn't improve.

A mixed layer driven by PET in absolute terms isn't safe until those warm summers are fixed. The one-day form only acts above ~1250 mm/yr of sensible heat, and it never makes a region worse.

## What E1 does and doesn't reach
- **Helped:** the hottest, driest summers. Sahara July share 0.86, Australia's January 0.93.
- **Not reached: the Gobi and the Sahel.** Their extra rain doesn't come from a deep dry layer.
  - In the Gobi summer the model's ground keeps evaporating (AET 694 of PET 1085), so the share stays at 1. The shower trigger is easy there: the plateau's air is only 7 °C short of the reference aloft, which follows the latitude's cool sea.
  - The Sahel's surplus is the wet season of its monsoon (4000 mm/yr in the July half).
  - Both are filed as drafts.
- **Not deep enough:** single-day encroachment into a standard atmosphere gives at most ~2.6 km. Real desert layers grow into the near-neutral residual layer of earlier days, which is why the steady state matches observations better. So E1 is a lower bound on the effect.

## Generated planets (health --quick, 8 L6 seeds, 500 Myr, 8 workers × 1 thread)
Both sweeps were run in scratch copies: main 4e5f259 unchanged, and this branch.

| (mean of the per-seed medians, range) | main | E1 prototype |
|---|---|---|
| dry_pct (Köppen B, % of land; envelope 12–45, Earth ~30) | 31.1 (28.0–34.5) | 28.5 (24.0–34.3) |
| inland_pct (envelope 8–30) | 5.9 (4.3–7.6) | 5.3 (3.4–9.8) |
| temp (°C) | 15.0 (12.8–16.8) | 14.9 (12.8–16.6) |
| trees_pct / npp | 26.8 / 322 | 27.4 / 307 |
| ice_pct | 0.6 | 1.1 |
| fresh-water residue warnings (> 2 cm/yr, all frames) | 267, median 2.8, max −6.1 cm/yr | 191, median 2.7, max −4.2 cm/yr |
| determinism re-run (seed 1, 100 Myr) | | bit-identical |

On generated planets the change is lost in run-to-run chaos. Any change to the climate sends a 500 Myr run onto a different tectonic path, and the per-seed dry shares move both ways: seed 1 went 33.7 → 24.0, seed 3199 28.2 → 34.3. The mean fell 2.6 points, inside the seeds' spread. `inland_pct` is still below its 8% envelope on 7 of 8 seeds, as on main (PW-054). The prototype doesn't make generated planets drier on the whole: their deserts seldom reach the ~1250 mm/yr of sensible heat that a deep layer needs.

## Water books
The change only alters when showers fire. The rain-out of the vapour still comes out of the same column, and the evaporation is still the water balance's AET, so the books stay as PW-266 left them:
- Earth: the fresh-water mean taken off is +0.0041 m/yr, against +0.0040 on main.
- Generated runs: fewer and smaller residue warnings than on main (the residue is PW-304's transport leak).

## Tests
- `uv run pytest -q`: 245 passed.
- Goldens regenerated (`tests/golden/climate_L4.json`, `sim_L4_s1_60myr.json`): the outputs changed on purpose.
- `tests/test_health.py::test_measure_frame` failed on the new trajectory by 0.01 of its 0.1-point tolerance. The cause: 2 L4 cells of oceanic crust count as land in the run's stats (bed > 0), but the trench offset puts their frame elevation below the sea. The test now names that case as well as grounded ice on pressed beds; filed as a draft.

## Also on this branch: PW-294 (output-neutral)
- `climate.ice_cooling()` and `TUNE['ice_cooling']` are removed.
- icemass has its own `ICE_COOL = 2.0` °C. TZParams' `albedo_share` becomes `ice_cool` (default `ICE_COOL`), and the docstrings are fixed.
- The old product was `10.0 * 0.2 == 2.0` exactly in floating point, so the outputs are bit-identical.

## Recommendation
Merge E1 as a small, sound step, or keep option A. It recovers about a fifth of PW-266's damage on Earth (exact 33.0 → 34.3%, B share 20.3 → 21.9%) with no regional regressions and the books closed.

The larger fix, a desert-deep layer, waits on the humid subtropics' warm summers (draft `draft-pw305-steady-mixed-layer-runaway.md`). The Gobi and the Sahel need their own fixes (draft `draft-gobi-sahel-wet-not-dry-layer.md`).
