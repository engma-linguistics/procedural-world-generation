# Glacial time zoom: design spec (2026-10-13)

*Moved from `docs/plan_next.md` item 6 on 2026-10-14. Implemented as `planet/timezoom.py` (branch `timezoom`); kept as the design record. Open issues are on the board: `board.py list --subsystem timezoom`.*

**User's decisions:**
- Whole planet, not regional.
- **View-only:** results do not feed back into the main run.
- Driven by **orbital (Milankovitch) cycles**.

**Corrected premise, as told to the user:** early Earth *did* have ice ages (Pongola ~2.9 Ga, Huronian ~2.4–2.1 Ga, Snowball ~720–635 Ma). A hotter interior ≠ a hotter surface; the young Sun was dimmer. Ice ages come in "icehouse" eras, and the main run already produces warm and cold eras (`dT` from drift + CO₂ + ice–albedo). So there is no arbitrary entry point: the user picks any moment. In greenhouse eras the time zoom shows little ice; in icehouse eras, full cycles.

**Plan:**
- **Entry:** `uv run python -m planet timezoom <run> --at <Myr> [--kyr 1000] [--step 0.5]`, also a viewer button on a run frame (after item 3's API exists). Mark icehouse eras on the run timeline, e.g. tint the timeline where `ice_pct` or `dT` says the world is cold.
- **Frozen geology:** take the main run's state at that moment (replay to t): bedrock elevation, sea floor, rock. Plates move ~50 km per Myr, so ignore tectonics.
- **Time step:** 500 yr over ~1 Myr, i.e. 2000 steps. Keyframes every ~2 kyr.
- **Orbital forcing:** obliquity (41 kyr period, ±1.2° around the planet's tilt), precession (23 kyr) × eccentricity (100 and 400 kyr, 0–0.05). Compute summer insolation anomalies per latitude and convert them into seasonal temperature anomalies. Amplitudes are knobs, so other planets can differ; the user's tilt param is the mean.
- **Climate per step:**
  - Not a full `climate.compute` every step (~1 s each); recompute fully every ~10–20 kyr.
  - In between, perturb: temperatures shift by the orbital anomaly, the lapse rate over the current ice surface, the ice–albedo cooling already in `compute` (`ice_cooling`), and global CO₂ feedback (glacial CO₂ drop ≈ −2–3 °C).
  - Precipitation scales roughly ×exp(0.07·ΔT), with an elevation-desert effect on high ice domes.
- **Ice sheet dynamics:**
  - *Mass balance:* snow accumulation (precip where T < 0) minus melt (positive degree days from the warm season).
  - *Flow:* shallow-ice approximation, nonlinear diffusion of ice thickness with D ∝ H⁵|∇s|², explicit with sub-steps or implicit. This is the user's "out": ice spreads under its own weight.
  - *Isostasy:* bedrock sinks by ~0.3× the ice thickness, relaxing with ~3 kyr e-folding (the user's "down"). It rebounds after melt.
  - Ice that flows to the coast calves into the sea, so it can't extend far over deep water. Shelves are optional.
- **Sea level:** from total ice volume (Earth's last glacial maximum was ~−120 m). Coastlines and land bridges change.
- **Optional extras:** glacial erosion, proglacial lakes, permafrost.
- **Output:**
  - Run format (`runs/<id>/` with `kind: "timezoom"`, time in kyr) so the existing viewer plays it.
  - Layers: elevation (with ice), ice thickness, temperature, sea level per frame.
  - Viewer: label time as "kyr after <run> @ <Myr>".
- **Tests:** ice volume ≥ 0; sea level consistent with ice volume; with no orbital forcing and a warm era, ice stays ~zero; deterministic.
- **Calibration:** on the Earth geography from `tools/earth_data.py`, a ~150 kyr run at Earth's current orbit range should grow Laurentide/Fennoscandian-like ice in North America and Europe with ~−100 m sea level at the cold peaks. That's a good sanity target.
