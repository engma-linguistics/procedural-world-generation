# Plan for rounds 1 and 2 (2026-10-13), as written

*Moved from `docs/plan_next.md` on 2026-10-14. Historical: items 1–6 and the Round 2 queue are done (item 6 is in `glacial_timezoom.md`). What is still open is on the board (`issue-tracking/`).*

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
  - **Server** (~~`planet/__main__.py` Handler~~; done: it lives in `planet/server.py` + `planet/api.py`): add `POST /api/zoom` with JSON `{run, t}` or `{world}`, plus `{lat, lon, size_km, res_km}`.
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


# Round 2 (started 2026-10-13): status and queue, as of 2026-10-14

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
  The salinity budget must include:
  - **river runoff** entering each basin at its river mouths (it freshens basins like the Arctic);
  - **moisture carried by the wind** from one basin to another (part of why the Atlantic is saltier than the Pacific);
  - **sea ice:** brine is rejected where it forms, and fresh water is released where it melts;
  - **ice-sheet meltwater.** In the main run this is small, since ice is near equilibrium at each climate update. In the glacial time zoom it matters a lot: meltwater pulses (Heinrich events, Younger Dryas) can weaken or shut down the overturning. So the time zoom should feed its ice melt into the same salinity term.
  (User request 2026-10-13.)
- **An Earth reference in the viewer:** our climate model on real Earth terrain next to the observed data.

**Queue (in order, as files free up):**
1. After `water` merges:
   - **Climate kernels in parallel** (bit-identical) and climate updated at every keyframe (`climate_every` = 4), so the viewer's climate isn't stale. The speedup pays for the extra cost.
   - **Then overturning circulation** in `climate.py`. **Done on branch `ocean`, merged** (`planet/ocean.py`; see Known issues → Overturning).
2. After `water` merges: **split `tectonics.py`** into kernels, crust, events and earth-system modules (output-neutral via the goldens), and drop compatibility code (`ocean_ref_age`, …). **Then the supercontinent B′** on the split code.
3. After `timezoom` and `highlights` merge:
   - `planet/store.py` (one reader/writer for runs, zooms and timezooms);
   - one file per layer, so the viewer loads only what it draws;
   - checkpoints every ~100 Myr;
   - `server.py`;
   - world files reference the shared grid.
4. **Earth reference world** in the viewer (model vs observed).
5. **Highlights, round 2** (the user wants all of these; "big ole waterfalls" most). **Done on branch `hl2`** except the fastest plate (skipped); see Known issues → Highlights.
   - waterfalls and knickpoints: big drops along big rivers; refine the height and location in the zoom raster (pixel-scale drops);
   - grand canyons (deep incision on high ground);
   - salt flats and closed basins (from `lake_kind`);
   - coral coasts;
   - rain shadows;
   - plateaus;
   - the most varied 1000 km square;
   - fastest plate, low priority, only if something visible goes with it (e.g. a collision in progress).
5b. **Real waterfalls in the zoom.** **Done on branch `falls`** (see `zoom.knickpoints()`). Where the coarse river drops steeply (big drop and discharge, the `waterfall` highlight), keep a knickpoint: a resistant-rock lip with a plunge pool and a gorge cut back upstream, instead of grading the reach smooth. Fix the lake-outlet cliff at the same time. The user wants big waterfalls most.
5c. **Lakes on the run globe.** *(Done: runs store `lake_depth` and `lake_kind` per frame.)* ~~Runs store no lake layer,~~ Runs stored no lake layer, so a 390,000 km² lake (a89254 @ 1592) shows only as a dip. The simulation already computes lake levels and kinds each step (`surface.erode` → `hydrology.lakes`), so keep them and store `lake_depth` and `lake_kind` per frame. Then draw lakes in the run viewer like worlds do. Do it after `store` and `mantle` merge.
6. **Regenerate the six showcase worlds** with the new code, then delete the old ones.

