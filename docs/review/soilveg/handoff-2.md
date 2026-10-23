# Soils-and-vegetation lane 2: handoff 2 (2026-10-23)

Branch `worktree-agent-a87b74fb9caca1b42`, based on main 22d3152; work commit 12e8922. Retired at ~100 tool calls.

## Done (commit 12e8922; pytest 595 passed; no golden change; simulate outputs unchanged)
- **PW-347 crown fire.** `vegetation.CROWN_FIRE` (0.08) x fire season x cover of TeNE + BoNE (`CROWN`) is added
  to `globfirm` in `_step`, times ignition. `equilibrium(crown=)` / `model(crown=)`, default on; the simulation's
  climate step (`tectonics/earth.py`) passes `crown=False` so runs don't change. Turning it on in runs is for the
  serial run-physics lane: it changes `simulate` outputs (the `test_highlights` sliced-world test caught that).
  Earth 490f1c, observed climate: boreal rotation / median 294 / 382 -> 218 / 286 yr (GFED 170-216); savanna
  3.82 -> 3.80, grassland 1.32 -> 1.32 Mkm2/yr; forest >= 60% trees 46.2 -> 43.7 Mkm2. CROWN_FIRE sweep: 0.06 ->
  230 yr, 0.08 -> 218, 0.10 -> 207. A dry-spell term (rain days at random, (1-f)^k) was tried and dropped: the
  rain/PET ratio term already counts boreal months 30-50% dry, so it moved boreal fire only to 240 yr.
- **PW-329 weathering profile.** `soils.R_SAP` 0.02, `D_SAP` 10 m: saprolite D = D_SAP ln(R/E), R = R_SAP x leaching
  (m/yr) x warmth; under glaciation/lava limited to R x time since. `age_w` = (D + h)/E (capped like the soil's age)
  drives W and the climate memory; the soil age `age` (h/E) still drives lime (CALCIC_YR), peat. New outputs of
  `_mineral`: `age_w`, `saprolite`. Earth: groups unchanged; Ferralsols 9.9 -> 15.2% of land (needs-decision draft).
  Not measured: the memory effect on a run world (the old 0.01 W shift was on run a1d3b9 at 380 Myr).
- **PW-330** salt soils only in the cell holding the salt lake or pan (`salt_near` no longer adds neighbours);
  blown sand (deflated/dry sandy, and its 1 m loose depth) only on slope < `SAND_SLOPE` 3 m/km. Agreement 45.0%
  unchanged; desert 21.6 -> 17.9% (SoilGrids 14.6), young 12.2 -> 14.6% (21.9), salt 5.0 -> 1.0% (1.1).
- Drafts: draft-veg-crown-fire-followups, draft-soil-ferralsol-acrisol-split (needs-decision),
  draft-soil-agreement-remaining (needs-decision), draft-soil-zoom-salt-pixels.

## Diagnostics (observed climate, L6 Earth)
- SoilGrids Ferralsols vs Acrisols: model W median 6.28 / 6.35, saprolite 11 / 12 m, slope 1.5 / 1.5 m/km: no signal.
- Caliche hits by mi: 0.1-0.2 55%, 0.2-0.3 41%, 0.3-0.35 36%; by age 2e4-5e4 28%, 1e5-3e5 59%; misses spread over
  Luvisols, Cambisols, Leptosols, Regosols.
- Frozen soils on SoilGrids Cambisols (3.3 Mkm2): slope bins don't separate them from SoilGrids Cryosols.
- Scripts (scratchpad scripts/): sv_soildiag.py (model type x WRB tables, KEYS env for fields), sv_calcdiag.py
  <type id> (rock/age/mi/slope bins), sv_saltdiag.py, sv_crown_sweep.sh, sv_firemap.py (unfinished: fire return vs GFED).

## Not done
- **PW-624**: the zoom viewer's 2D ramp path already paints sea (`water === 1`) with the sea ramp before the game
  ramps (viewer/zoom.html ~1230), so the "sea in travel/sightline colours" item may already be fixed or be in another
  view (3D or legend); needs a screenshot on zoom 4f54cb (scratch store) to confirm. Roughness reconciliation
  (world relief/1500 vs zoom Tobler slope) not started.
- **PW-525** not started.
- Screenshot of fire return (sv_firemap.py: `VC.run` returns the vegetation dict, fire return is `v["sm"]["fire_return"]`;
  `earth_gfed(grid)` returns the burned fraction array).
