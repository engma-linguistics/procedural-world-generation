# Next round of work: plan

*Written 2026-10-13, from the user's notes after viewing the six v1 worlds. Nothing below is implemented yet.*

**Pending decision:** the supercontinent cycle is in `docs/proposals/supercontinent_cycle.md`. The user will hand that doc back and choose; the current recommendation is the breakup-size fix plus B′. It is not part of this plan.

**Working rules** (also in memory):
- Commit locally only, never push. Commit trailer:
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_014bStFKVi2t6nKqdEqA4N8F`
- Iterate at level 6; ~5 min per run is fine.
- Ask about genuine judgement calls; nudge systems rather than force them.
- Correct the user's wrong assumptions rather than building on them.
- Run `uv run pytest` (~30 s) before every commit that touches `planet/`. Run `uv run python tools/scorecard.py` (~6 min) after model changes, and `tools/earth_check.py` for climate changes.

Order: 1 → 6, small to large.

## 1. Viewer: left panel too tall (user's Mac can't fit it)
- **Problem:** the controls panel in `viewer/index.html` overflows the window.
- **Plan:**
  - Make each section collapsible: View, Colour by, Overlays, Relief/River sliders, Playback, "Why pentagons".
  - Use `<details>` or a click-to-toggle header, and remember the open/closed state in `localStorage`, wrapped in try/catch.
  - Give the panel `max-height: calc(100vh - 24px)` and `overflow-y: auto`.
  - Collapse the rarely used sections (cell outlines, pentagons, smooth colours, auto-rotate, the slider tray) by default.
- **Check:** headless Chrome screenshots at 1500×900 and 1280×720.

## 2. Viewer: tilt and axis indicator, "north up"
- **User's ask:** a small visual on the globe showing the axial tilt, plus a way to re-centre north–south.
- **Plan:**
  - Draw the spin axis as a thin line through the poles, extending past the surface, with N/S labels or small cones.
  - Optionally draw an equator ring and the two tropic circles, at ±tilt, from `run.meta.params.tilt` (default 23.4).
  - Show the tilt as a small inset: the axis drawn at the tilt angle against an "orbit plane" line, labelled e.g. "tilt 23.4°".
  - Add a **"North up"** button (and key `N`) that resets the camera so north points up the screen, keeping the current longitude.
- **Check:** screenshots with tilt 23.4 and 45 runs.

## 3. Regional zoom inside the viewer UI
- **User's ask:** integrate the zoom tool into the UI, maybe as a separate tab.
- **Plan:**
  - **Server** (`planet/__main__.py` Handler): add `POST /api/zoom` with JSON `{run, t}` or `{world}`, plus `{lat, lon, size_km, res_km}`.
    - For a run, slice it at `t` first. Cache by (run, t); `T.slice_world` replays from 0, which takes ~10–60 s at level 6.
    - Then call `zoom.zoom(...)` and return the zoom id.
    - Run it in a worker thread and report progress: either `GET /api/jobs/<id>` polling or a blocking request with a spinner. Keep it simple; one job at a time is fine.
  - **Main viewer:** when a cell is clicked (or shift-clicked), show a "Zoom into this region (1000 km)" button in the hover/info box. It calls the API and, when done, opens the zoom.
  - **Tabs:** a "Globe | Regional zoom" tab switch at the top. The zoom tab hosts `viewer/zoom.html`, as an iframe or by merging the page. The zoom page's list should show which world or run each zoom came from.
  - The server is the user's running `planet serve` on port 8765. Any server code change needs a restart; tell the user.
- **Tests:** an API-level test that calls the handler logic as a function, without a socket.

## 4. Ocean currents: real closed gyres (physics)
- **Problem the user saw:** the currents are mostly zonal arrows. There's no circulation carrying warm water poleward and back, so no closed gyres.
- **Diagnosis:** in `climate.currents`, the open ocean only gets the wind's east–west component. The poleward and equatorward return flows exist only in a ~250 km band along coasts, applied by rule.
- **Plan:** replace the rule with a wind-driven **streamfunction** per ocean basin (the Stommel model):
  - Solve `r ∇²ψ + β ∂ψ/∂x = curl(τ)` on ocean cells, where τ is the annual-mean wind stress (∝ wind vector), β is the change of the Coriolis effect with latitude (∝ cos lat), and r is bottom friction. Use ψ = 0 on coasts, solving each connected basin separately with an iterative relaxation on the grid (numba). Currents are the rotated gradient of ψ: `u = k̂ × ∇ψ`.
  - This gives closed subtropical and subpolar gyres shaped by real coastlines, western intensification (a Gulf-Stream-like narrow, fast current on each basin's west side), and the return flow across the basin.
  - Add a circumpolar current where an unbroken ocean ring exists at some latitude, since a periodic channel has no walls. Detect latitude bands that are all ocean and add zonal flow from the wind there.
  - Equatorial currents (zonal, from the trades) can stay as the wind's zonal push near the equator, where β-plane gyres degenerate.
  - Keep the heat transport (`sea_surface`, relaxed along currents) but feed it the new current field. Re-check SST anomalies: warm western boundary currents, cold eastern boundaries, a mild "Norway".
- **Check:** `tools/earth_check.py` (the Earth score must not drop below ~68% group agreement; the test floor is 66%), Earth current maps showing Gulf Stream, Kuroshio, Antarctic Circumpolar, plus generated worlds and the viewer overlay. Runtime budget: `compute` ≤ ~1.5 s at level 6.

## 5. Winds: upper-level jet stream, terrain steering
- **What the user saw:** winds are "fairly invariant", no jet stream emerges, they're barely affected by land shape or elevation.
- **Explained to the user:**
  - The overlay shows the *annual-mean surface* wind, which on Earth is also fairly zonal.
  - The jet stream lives at ~10 km altitude and can't appear in a surface-wind field.
  - The terrain-steering gap is real.
- **Plan:**
  - **Jet stream:** compute the upper-level wind from the *thermal wind* relation: its speed follows the north–south surface temperature gradient, strongest where that gradient is sharpest, i.e. the polar front. Per season, smoothed, with meanders where land–sea contrasts bend the temperature field.
    - Store it as `jet_jul` and `jet_jan` from `climate.compute`, and as run layers `jet_e` and `jet_n` (int8 ×50).
    - Add a "Jet stream (upper winds)" viewer overlay.
    - Use it to steer storm tracks in the rain model. Mid-latitude rain should follow the jet's latitude per season, replacing part of the fixed storm belt.
  - **Terrain steering of surface winds:** air flows around high ground rather than over it. Remove part of the wind component that runs up steep slopes into high terrain (above ~1.5 km), redirecting it along the contours, as a blocking/deflection term. The calibration agent tried "mountain blocking" and dropped it for no net gain, so re-try it after gyres and the jet, judged on the Earth score plus visuals (Tibet, Rockies, Andes).
  - Possibly also show seasonal winds (July/January) as a viewer toggle. The annual mean hides the monsoon reversals, and the user expected to see them. Needs `wind_jul` and `wind_jan` layers (int8) per frame.
- **Check:** Earth score not worse, visuals, runtime.

## 6. Glacial "time zoom": a short-timescale, whole-planet side simulation
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

## Also noted (smaller, later)
- The older runs from before the v1 changes are still in the viewer list; ask whether to delete them.
- Continental area overshoots (~45% vs the 40% target).
- Lakes are too many and too large; ocean plate boundaries are ragged.
- Earth climate errors: Sahel and East Africa too wet; Indian and Chinese monsoons too dry; winter temperatures off by 5–10 °C in Siberia, Alaska, Quebec and NE China.

---

# Round 2 (started 2026-10-13): status and queue

**Done and merged:** items 1–5 above. The viewer has the panel, tilt, zoom tab and jet overlay. The model has gyres, the jet stream and terrain winds. Also merged: the code-review "safe now" cleanup, golden tests and code-version stamps, keyframe worlds for the zoom API, and the plate-merge fix.

**Running (separate worktrees):**
- `timezoom`: item 6.
- `highlights`: points of interest, plus pre-made zooms.
- `water`: evaporation and runoff (Budyko), closed/salt lakes, `lake_level` world layer, sediment limits.
- `zoomwater`: zoom lakes pass water through, true lake level and bed, delta plains and distributaries.

**User decisions (2026-10-13):**
- **No backward compatibility.** Old runs, worlds and zooms can be deleted whenever a change breaks them. Don't keep code paths only so old runs replay.
- **Splitting big files and the review's refactors are approved.**
- **Supercontinent:** C's breakup fix plus **B′**: a mantle temperature field (slab graveyards and continental insulation), basal traction into `_forces`, and the stress trigger decides rifts, replacing the fixed heat and big-plate rules. Hotspots are tied to the warm mantle. The user does not need cycles to be guaranteed.
- **Overturning (deep) ocean circulation:** wanted, done physically. Density from SST and salinity, with salinity from evaporation minus precipitation, so it comes after `water`. Use a zonally averaged or box overturning per basin, with poleward heat transport following from it (the "mild Norway" fix).
- **An Earth reference in the viewer:** our climate model on real Earth terrain next to the observed data.

**Queue (in order, as files free up):**
1. After `water` merges:
   - **Climate kernels in parallel** (bit-identical) and climate updated at every keyframe (`climate_every` = 4), so the viewer's climate isn't stale. The speedup pays for the extra cost.
   - **Then overturning circulation** in `climate.py`.
2. After `water` merges: **split `tectonics.py`** into kernels, crust, events and earth-system modules (output-neutral via the goldens), and drop compatibility code (`ocean_ref_age`, …). **Then the supercontinent B′** on the split code.
3. After `timezoom` and `highlights` merge:
   - `planet/store.py` (one reader/writer for runs, zooms and timezooms);
   - one file per layer, so the viewer loads only what it draws;
   - checkpoints every ~100 Myr;
   - `server.py`;
   - world files reference the shared grid.
4. **Earth reference world** in the viewer (model vs observed).
5. **Regenerate the six showcase worlds** with the new code, then delete the old ones.
