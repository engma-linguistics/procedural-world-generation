# Next round of work: plan

*Written 2026-10-13, from the user's notes after viewing the six v1 worlds. ~~Nothing below is implemented yet.~~ (Done 2026-10-14: items 1–6 are all implemented; see Round 2 below. The plans are kept as written.)*

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

## Backlog (user notes, 2026-10-14)
- **Delta types.** Real deltas differ by what dominates (Galloway's classification):
  - **river-dominated:** the Mississippi's bird's-foot, a few long distributaries reaching out into calm deep water;
  - **wave-dominated:** the Nile and São Francisco, a smooth arc-shaped coast with beach ridges;
  - **tide-dominated:** the Ganges–Brahmaputra and Mekong, many funnel-shaped channels and islands (the Sundarbans).

  ~~The model has no waves or tides.~~ (Done: `planet/coast.py` has `wave_power`, `tide_range` and Galloway delta types in the zoom.) Wave energy could come from the winds and fetch (open water the wind blows over). Tidal range could come roughly from shelf width and basin shape. Then pick the delta shape in the zoom per type. Medium effort.
- **Giant open lakes:** outlet incision should drain them down over time; today they stay at their spill level. a89254 has a 390,000 km² open lake, larger than any open lake on Earth (Superior is 82,000 km²; only the closed Caspian is bigger).
- **Vegetation, and eventually a "satellite view"** of the globe and zooms. Not yet.
- **Zoom 3D view:** a simple low-poly three.js heightmap mesh with a water plane and rivers, in the existing viewer. No Unity or game-engine side project. The goal is to "see a big ole waterfall".
- **Finer zooms:** 100–250 m pixels for small areas, if the zoom pass holds up at that scale.
- **A level-7 showcase run** (~60 km cells, 164k cells; roughly 4–8× the cost of level 6, so ~15–30 min per Gyr), once B′ and the ocean work land. It doubles as a resolution-dependence check, since everything was calibrated at levels 5–6. **Level 8** (~30 km, 655k cells; maybe 1–2+ h per Gyr, plate arrays ~1.5 GB) only after a short trial. Neither resolves waterfalls; those come from the zoom.

## Known issues to come back to (collected from the agents' reports, 2026-10-13)

**Glacial time zoom** (`planet/timezoom.py`)
- **No real 100-kyr sawtooth.** Ice shrinks back 20–50 m at insolation peaks, but the trend ratchets upward. Terminations need mechanisms that aren't modelled yet: a CO₂ rise independent of the ice, proglacial lakes, dust darkening the ice, and the overturning/meltwater coupling (below).
- **Generated worlds glaciate too hard.** At dT 0 they reach about −400 m, roughly 3× Earth's last glacial maximum. The global temperature hits the floor set by the CO₂ and albedo feedback caps. Related: **the main run's ice rule** (`precip > 25 mm/yr`, an equilibrium extent) leaves cold polar deserts bare that an ice sheet would cover. Revisit it in the main model.
- **Earth on our model's climate:** only −52 m at 150 kyr. Labrador and Baffin summers are ~5 °C too warm (no Laurentide inception). Tibet, Karakoram and the Altiplano grow ice caps, and Cordillera and Alaska ice is too big. **On the observed baseline:** no Fennoscandian ice.
- **Eemian-like start:** +24 m in the first 10 kyr (real: +6–9 m). `insol_k` above 0.3 melts most of Antarctica.
- **Start anchor:** the fixed per-cell cooling that keeps the starting ice stable persists after that ice is gone. It's a calibration crutch.
- **Smaller issues:** small accumulation jumps at each 10 kyr climate refresh; the ablation zone (where ice melts) is about one 110 km cell wide.
- **Not done:** glacial erosion, proglacial lakes. (The meltwater link to ocean salinity is in, branch `ocean`, merged: each full climate gets the net ice loss since the last one as `melt`, and the overturning carries on from the last one's state. Over Earth's first 150 kyr it is only ~0.03 Sv, too small to matter.)

**Climate**
- **Norway too cold:** partly fixed by the overturning (branch `ocean`, merged). The Norwegian coast's sea surface went from 0.9 to ~5–6 °C (observed ~7.5), and Scandinavia's coldest month from −26.5 to −22.3 °C (NCEP −8.2). W European winters barely moved (−4.3 → −4.2 °C against 0.6 observed). Even a sea 8 °C warmer all over the NE Atlantic only brings them to −3 °C, so the rest is in the air-temperature model (how far the sea's air reaches inland in winter), not the ocean.
- **Overturning circulation** (`planet/ocean.py`, branch `ocean`, merged):
  - **Earth:** ~11 Sv sinking in the Nordic, Irminger and Labrador seas (observed AMOC ~17 Sv) and none in the North Pacific. The Antarctic margin makes only ~2.5 Sv (AABW ~10–20 Sv): the Weddell and Ross seas are too fresh (~34.0 psu against 34.4–34.6). Their winter brine is weak, and there's no shelf/polynya ice factory.
  - **Labrador Sea is too warm** (~7 °C sea surface against ~3.5 °C): the inflow feeds it along the Labrador coast. SW Greenland and Iceland now get summers just above 10 °C, so ET becomes D there (Reykjavik's coldest month went from −29.6 to −12.9 °C, observed −0.6 °C).
  - **The North Atlantic's on-state is found by a spin-up rule,** not by history. With no earlier state, every polar sea that is nearly dense enough starts sinking, and the drho threshold tightens over the iterations. Without that start, the model's own salinity leaves the Nordic seas too fresh to sink: its rain model has no Atlantic/Pacific evaporation contrast to speak of. Hosing ~1 Sv into the North Atlantic shuts it down. Once the hosing stops it recovers within 2–3 climate updates, so it has no lasting off-state.
  - **Its warmth adds to the 50–70°N ocean band** (`moc_zonal` = 0): that band's sea is now ~2–4 °C warmer than before. The Köppen score preferred this (70.69% against 70.50% with half of it taken off the band).
  - **Cost:** about +0.15–0.2 s per climate.compute at level 6 (0.48 → ~0.65 s unloaded). The overturning is solved on the level-5 grid, but the sea surface and the air temperatures are carried a second time on the full grid.
- **Gulf Stream and Kuroshio separate from the coast too far north** (a Stommel-model limit), so the Oyashio region is too warm.
- **Rain is patchy cell to cell on flat ground:** neighbouring cells differ by a median 1.5× near the hothouse lake. Diagonal streaks in rain maps predate the gyre work.
- **Older Earth errors:** Sahel and East Africa too wet; Indian and Chinese monsoons too dry; Siberia, Alaska, Quebec and NE China winters 5–10 °C off.
- **Visible in the Earth world's temperature difference view (8e052d):**
  - The East Antarctic interior is about 10 °C too warm.
  - NE Canada, Labrador and Greenland's margins are too warm; this also blocks Laurentide ice inception in the time zoom.
  - The Andes and the Tibetan margin are speckled.
- **The jet stream is broad and zonal,** with modest meanders.
- ~~**The run viewer's climate is up to 4 Myr stale** (`climate_every` = 8 vs keyframes every 4). The fix is queued with the parallel climate kernels.~~ Done: `climate_every` = 4, matching the keyframes.

**Rivers, lakes, sediment** (see `docs/review/rivers_lakes_deltas.md`; `water` and `zoomwater` address most)
- **No evaporation:** discharges are 2–5× too high and there are no closed lakes. (`water`)
- **Sediment piles reach 33 km** (Earth max about 20–22 km). (`water`)
- **Drainage switches outlet in one step when a rift opens.** (`water`, optional)
- ~~**Zoom lakes are sinks:** the water level is wrong and the floor is a flat 42 m; there are no deltas or distributaries. (`zoomwater`)~~ Done (`zoomwater`): lakes pass water on at their outlet, sit at the world's `lake_level` with a bed from the coarse fill depth, and big mouths get delta plains and distributaries.
- **Evaporation is merged (`water`); what's left:**
  - **Drainage memory** is not implemented. Old channels would have to move with the plates; the physical damping is rift-flank uplift, which is a tectonics change.
  - **Generated worlds have almost no closed basins after ~150 Myr** (0–2% of land drains inland, against 21% on Earth's terrain). Sediment and erosion fill every hollow, and the tectonics makes no new interior basins (foreland or intermontane basins, rift-flank highs).
  - ~~**Sediment is treated as crust-density rock in the isostasy,** so filling deep water takes ~5× its depth in sediment (Earth ~3×). About 400 cells sit at the 18 km metamorphic cap.~~ **The user chose (2026-10-13) to give sediment its own lower density,** compacting with depth. Done (with B′, `mantle` merge): `isostasy.sediment_density`, 2.1 → 2.6 g/cm³; basin fill now ~3× the water depth, and 0–103 cells at the cap instead of 76–664 (L6 seed 1, see `docs/proposals/supercontinent_cycle.md`).
  - **The 20 m "unresolved channel" threshold** for coarse hollows is a judgement call.
  - **Discharge misses come from the rain model:** the Yangtze ends in a lake, and the Lena, Mekong and Ganges are too small (dry China, Siberia and Indian monsoon). The Nile is 19× too big (Sahel too wet). With observed rain, magnitudes are about right.
  - **The Orinoco gauge picks up the Amazon,** a coarse-routing artifact.
- **Zoom lakes and deltas are merged (`zoomwater`); what's left:**
  - ~~The lake outlet river drops about 140 m within a few km (a cliff waterfall).~~ Fixed (`falls`): the ground below an open lake's outlet steps down at most 2 m/km (rapids), out to the first designed fall.
  - The zoom sees only part of a big lake's catchment (45k of 125k m³/s). ~~River water entering at the zoom's edge can drain straight back out through the edge.~~ (Done: the edge next to an inflow is land, not an outlet; `zoom.py`.)
  - Delta fans are small, and their branches run straight (only 8 possible step directions). There are no distributaries when the fine-scale river reaches the sea away from the coarse mouth.
  - A small lake fragment sometimes has no outlet and acts as a sink.
  - The real `lake_level`/`lake_kind`/runoff layers from `water` are untested in the zoom (only the fallback was exercised).
- **Fjords aren't carved in the zoom:** fjord coasts are only detected.

**Crust and continents**
- Continental area overshoots to about 45% (target 40%).
- Ocean plate boundaries are ragged.

- **Too few plates after the mantle merge:** seed 1 drops to 2–3 plates around 500–700 Myr at both L6 and L7. Showcases end with 4 (2b59b1, 9219ac); Earth has ~7 major plus ~8 minor. Rifting may need to split big plates more readily, or plate absorption is too eager (41–61 absorbed vs 52–69 rifts per run). See `docs/review/overnight_runs.md`.

- **Supercontinent cycle (`mantle`, merged):** all 4 L6 seeds reassemble above 25% at least twice in 2 Gyr, but cycles are uneven (seed 1 is quiet from 590 to 1930 Myr) and mostly 400–870 Myr apart. Showcase run 6d9dcf (seed 2).
- **Land runs high** (median 34–36%, up to ~40% when assembled), and crust volume drifts +2–5% mid-run: assembled continents have fewer subducting margins, and the volume thermostat only partly compensates.
- **Plate count** median 6–7 with c8a06d2 (before: 8–10), dipping to 2–3 about 10–20% of the time. The cause is fewer plate births since the fixed heat and big-plate rift rules were removed.
- **Single-sample ~12–13 km elevation spikes** seen once with B′ and once with the breakup fix alone. Not investigated.
- **Sediment compaction isn't remembered** after uplift.
- **Name clash:** `planet.tectonics.isostasy` resolves to the function, not the module.

- **Oceans get older after the `l7jumps` fix:** margin subduction now breaks off one basin (6000 km of the oldest passive margin) instead of the plate's whole ocean. Mean ocean age is 83 Myr at L6 against 70 before. In stagnant 2–3-plate phases the L7 mean reaches 140–185 Myr, and the ocean-basin term of sea level sits on its −250 m clip. (To be precise: only that term, half the change in mean ocean depth measured against a ~300 Myr running baseline of itself, is clipped to ±250 m; the hot-mantle term and the ice term are added after the clip, so sea level itself can go beyond −250 m.)
- **L7 continents are ~2 km thinner and ~300 m lower than at L6** (median crust 33 vs 35 km), so twice as much land sits within 100 m of sea level and land is ~2× as sensitive to sea level. Cause not found; check erosion and thermostat scaling with resolution.

- **Fast sea-level swings remain after the l7jumps fix,** rarer: L7 fe7144 40→30% land at ~1140 Myr then back to 34% by 1172; L6 796a25 37→30% at 1320. Probably any big plate reorganisation renewing ocean floor quickly, plus low L7 continents. Consider limiting how fast mean ocean depth can change (ridge volume responds over ~10s of Myr) or checking the thermostat. See `docs/review/overnight_runs.md`.

**Highlights**
- ~~Several highest peaks sit under ice caps~~: an iced peak now ranks lower and the highest ice-free peak is added (`hl2`).
- ~~Earth-like A's longest river crosses a cold, dry polar continent~~: thin rivers over barren land rank lower (`hl2`); it's still listed.
- The hothouse wine country has 41 °C summers (Köppen-correct, not appealing).
- ~~Pre-made zooms need re-making after `zoomwater` lands~~: re-made for a434c5 and cec38b (`hl2`).
- ~~**No big waterfalls in the zoom except at lake outlets.**~~ Fixed on `falls`: steep coarse reaches keep falls (lip, gorge, plunge pool, cascades). Notes from before the fix: The landscape pass grades every river (slope ~ Q^-0.5), and coarse rivers are carved along a smooth, linearly interpolated floor, so a coarse steep reach (e.g. 315 m over 220 km at 61,000 m³/s) becomes a smooth valley; pixel-scale falls on rivers are tens of metres. The one big kind, a lake outlet (105 m at 102,000 m³/s in a434c5's big lake, zoom cc9dcf; 153 m at 45,700 m³/s in 42bc11), comes from the zoom cutting the outlet river's floor 12–45% below the coarse ground: the "cliff waterfall" known issue under zoom lakes. The coarse world itself is flat there (lake 284 m, next cells 284 and 275 m). Real falls would need the zoom to keep a knickpoint where the coarse river drops steeply (e.g. a hard-rock lip), a zoom model change.
- **Worlds sliced before `water` (a434c5, cec38b) have no lake_kind and no closed basins**, so salt lakes, salt pans and inland basins don't appear; exposed evaporite beds on dry land stand in as "salt flats".
- **Canyons are weak at 110 km cells:** the Earth world finds the Kura valley and the Siang below the Tsangpo gorge, not the Grand Canyon. Rain shadows find the Himalaya, SE Tibet and the Atacama/Altiplano edge, not the Sierra Nevada. Plateaus find Tibet, Wyoming and the Altiplano (3rd). The Earth world's salt lake is in Hungary (the model climate leaves the Pannonian basin closed); the Caspian is below sea level, so it's the landlocked sea.

- **Zoom falls (`falls`) are big for such big rivers:** 141 m at 60,000 m³/s is ~85 GW, about 70× Niagara, because coarse worlds drop big rivers 500–700 m over a few hundred km.
- **The escarpment shows only as the fall and gorge**, not as stepped country. The 1-px gorge is hidden under the preview's wide river line.
- **A designed step is lost** if the zoom's river carries under 30% of the coarse discharge or the reach leaves the region (a 256 m step on a 1,215 m³/s stream in 58ed13). `waterfalls()` keeps falls ≥15 km apart, so close cascades go unlisted.
- **Small uphill steps on delta trunks** (path frozen early), from before `falls`.
- **No glacial hanging valleys.** The lake-outlet cone can raise low ground up to 150 km around an outlet.
- **Big zoom rivers are now less deeply incised** (they keep at least their valley floor), so canyons are shallower than before `falls`.

- **Falls are scaled down to fit under the coarse ground (`falls2`):** median fit 0.34; only 2 of 47 reaches keep full height. Big rivers now show ~50–150 m falls, and only steep mountain fronts keep 250–550 m. Full heights would need the land itself to step up into a plateau above each fall.
- **Some stretches still run perched above the land beside them** where the zoom's land is lower than the coarse ground (f99af0's upper reach, 200–400 m): an embankment look.
- **Some cascade steps still realise ~0 m,** and there are rare hanging joins where a river joins a falls reach mid-course (1b3609: 102 m at 1,210 m³/s).
- **Coarse zooms (2–4 km pixels) still report steep reaches as drops,** and small streams (<400 m³/s) show 100–200 m drops on steep slopes.

**Coast: waves, tides, delta types** (`planet/coast.py`, branch `deltas`)
- **Southern Hemisphere westerly coasts get ~half their observed wave power;** the N Atlantic and NE Pacific get ~1.5× too much. The storm tracks come mostly from land–sea contrast, so they are weak over the Southern Ocean.
- **Wave power is ~2× too high in the Med, Baltic and Black Sea,** and India's west coast is too low (no monsoon swell). Faint straight streaks appear in the lee of islands (16 ray directions).
- **Tides:** Fundy is too small (2.4 m; the funnel is under the cell size), the Caribbean too big (1.0 m), Arctic shelves too big (no sea-ice damping), and there are no amphidromic points.
- **No Earth delta comes out tide-dominated:** the model gives the Ganges 3,700 m³/s (real ~40,000), and its mouth's tide is too small.
- **The fine river can reach the coast ~100 km from the coarse mouth,** so the delta form and the river don't always line up.
- **Not done:** spits deflected by longshore drift, mangroves, visible beach ridges in the preview, and a dendritic eroded tidal-channel network (it's noise-based now).
- **Cost:** ~1.2 s per level-6 world.

**Viewer / Earth world** (from the viewer2 report)
- The Earth world `8e052d` has about 7% of its land as lakes (no erosion, every pit fills). Re-run `tools/earth_world.py` after `water` merges and delete the old one.
- The Earth world can't be zoomed (no rock layers).
- The cold-era timeline tint is stripy where temperature flickers from frame to frame (kept unsmoothed).
- Time zooms made from the button run away too: f87163 reaches −520 m with ice 7.4 km thick. This is the "generated worlds glaciate too hard" issue above.

- **Run lakes vs sliced worlds (`lakes`):** closed lakes on flat basins disagree a lot (t=180 in demo run 8dc2f2: 1 shared wet cell of 88 vs 18), because the world adds ±180 m texture, its own erosion and a fresh climate. Open lakes agree roughly; the world's are smaller and about half as deep.
- **Giant shallow lakes in runs** (up to ~2.3M km²): outlets don't cut down (see outlet incision in Backlog).
- **Closed lakes on flat basins look speckled** on the run globe.
- **Lakes are drawn only on the elevation and biome layers**, and run hover shows lake info only when elevation is loaded. Contrast: salt-lake teal is near some biome greens, and fresh blue is near shallow sea. `lake_depth` is stored in whole metres, so shallow lakes read "~0 m".

- **Sliced worlds don't store wind, current or jet layers** (only runs and the Earth world do), so those overlays never appear on generated worlds (found by the overview agent).
- **No `equator_temp`/`pole_temp` knobs exist** (the README claimed them; fixed in f45525c). `climate.compute` derives them from dT and tilt. Add real knobs if wanted.

**Infrastructure**
- **Parallel numba kernels aren't safe for concurrent calls from several Python threads** (climate and `kernels.locate`). The API runs one job at a time; keep it that way, or add a lock.
- `NUMBA_NUM_THREADS=4` is often faster under load on this 4P+4E-core Mac. Parallel launches cost about 40–57 µs each.
- `api.Jobs` state is in memory only and is lost on server restart.
- ~~The zoom request can't choose seed, iterations or resolution (always 500 px).~~ Partly done: `POST /api/zoom` accepts `seed` and `res_km` (default `size_km`/500); it still can't choose `iterations` (always the default 15).
- The Earth-score metric has three definitions (B5 in the code review). Unify them after the climate work settles.
- **Checkpoints are big (`store`):** about 23 MB each at level 6 (≈229 MB per 1 Gyr run, about as much as the layers). Saving only live plates' slots would shrink them.
- **Old outputs still show in dropdowns** until deleted. Every pre-`store` run, world and zoom fails to open (all were scheduled for deletion and regeneration).
- **Replay falls back to t=0 when the code changed** (the source hash differs), so slices of older runs take minutes, or fail with ReplayMismatch unless `--force`.

## Overnight state (2026-10-14 00:10): for the coordinator after context compaction

**User asleep.** Cleared for ONE level-8 run (save it for last; kick off no later than 05:00) and up to 8 level-7 runs, plus any level-6 runs. The user reviews in the morning. Commit locally only.

**Agents in flight**, each in its own worktree `.claude/worktrees/<branch>` with symlinked `data runs worlds zooms grids`. When one reports: merge its branch into main, run `uv run pytest`, fix conflicts, regenerate goldens if outputs legitimately changed (`uv run pytest tests/test_golden.py --update-golden`), add its "remaining issues" to Known issues, and restart the server if server code changed.

| Branch | What it's doing |
|---|---|
| `mantle` | Breakup fix plus B′ mantle field, hotspots tied to warm mantle, lighter sediment density. Will make a 2 Gyr level-6 showcase run. |
| `store` | `planet/store.py`, one file per layer (viewer loads lazily), consistent layer names, worlds referencing the shared grid, checkpoints via `Simulation.state()`/`load_state`/`from_state`, `planet/server.py`. Existing outputs may need regenerating after this. |
| `ocean` | Overturning circulation (salinity from E−P, runoff, sea ice, a meltwater hook for timezoom) and its heat transport ("mild Norway"). |
| `falls` | Knickpoint waterfalls in the zoom (resistant lip, plunge pool, gorge retreat) and the fix for the lake-outlet cliff. |

The viewer server (`planet serve --no-open`, port 8765) was started by the coordinator. Restart it after server changes:
`pkill -f "planet serve --no-open"; nohup uv run python -m planet serve --no-open > $CLAUDE_JOB_DIR/tmp/serve.log 2>&1 &`

**Level-7 timing:** ~1.8 s/Myr under load (≈30 min/Gyr), 0.9 GB RSS. Land went 29→22% in the first 20 Myr at level 7, so check resolution dependence. **Level 8 estimate:** ~2 h/Gyr, ~3.5 GB RAM. Frames are large (level 8 ≈ 17 MB/frame), so use `--every 10` or more.

**Overnight plan after merges:**
1. **Lakes on the run globe** (queue 5c).
2. **Regenerate the six showcase worlds** at level 6 with the new code, delete the old ones (keep the Earth world `59a918`, re-made with `tools/earth_world.py`), recompute highlights, and pre-make zooms (`planet highlights <run> --at T --zoom 6`).
3. **Level-7 runs:** first an Earth-like ~1–2 Gyr run to check resolution dependence against level 6 (land, dry share, ocean age, landmasses; supercontinent cycle), then showcases. Up to 8.
4. **Level-8 run** last, started by 05:00. Earth-like, `--every 10`, ~1–1.5 Gyr.
5. **Morning report** for the user: what merged, the run ids with what to look at, highlights/zooms to open, and open decisions.

**Showcase recipes** (the old v1 runs were deleted at the `store` merge, since no old output can be read any more). All are level 6, `--every 4`, with default params except:

| Old run | Name | seed | Myr | `--set` | Old worlds (t) |
|---|---|---|---|---|---|
| ed7401 | Earth-like A | 11 | 1000 | — | 400 (cec38b), 576 |
| 68929f | Earth-like B | 12 | 1500 | — | 432 |
| a89254 | Water world, land emerges | 13 | 2000 | `continental_start=0.1 heat_start=2` | 1396, 1500, 1592 (giant lake), 1960 |
| f2d397 | Land-heavy | 14 | 1000 | `continental_fraction=0.6` | 864 |
| 7c716b | Cold world | 15 | 1000 | `tilt=15 climate_offset=-6` | 288 |
| d05a1e | Hothouse | 16 | 1000 | `tilt=45 climate_offset=5` | 432, 460 (a434c5) |

Same seeds won't give the same geography under the new physics, so pick world times afresh.

**Update 00:20:**
- `store` is merged (1c93acf); the server has been restarted.
- The `lakes` agent is doing step 1.
- The other agents were told to merge main before reporting.
- Old outputs get deleted once `falls` reports, since it tests on a434c5 and cec38b.
- The user (at bedtime) asked for two documents, both written by subagents only **after all other overnight work is done**:
  - `docs/morning_decisions.md`: judgement calls for the user to give feedback on. Collect them through the night.
  - `docs/overview.md`: an overview of what the project is and how each subsystem works. At most ~5 pages of text; pictures and diagrams are welcome.

**Update 01:45:**
- **Merged:** lakes, falls, ocean, deltas, and mantle at cbe40ce (the mantle agent is still finishing docs, a scorecard and a showcase).
- **Old outputs deleted.**
- **Running:**
  - L7 seed 1, 1500 Myr (`--every 5 --checkpoint-every 250`);
  - a serial script re-making the L6 seed-1 comparison plus the six showcases (`$CLAUDE_JOB_DIR/tmp/runs/showcase.sh`, logs alongside).
- **Next:** slice worlds, highlights and zooms from the showcases; the L8 run by 03:00–05:00; more L7 showcases.

**Update 03:20:**
- **Mantle:** merged at cbe40ce before the long runs. The agent is still adding plate-size-scaled stress rifting (more plates), so tonight's runs predate that.
- **L8:** run 15b1b0 started at 01:50 (seed 1, 1200 Myr, `--every 10`). It took 85 min to reach 300 Myr under load, so expect it around 07:00–08:00.
- **L7 done:** 1beb32 (seed 1, resolution check), 0e4c66 (seed 11, world eeaf33), f3f4ac (seed 16 hothouse, world 2c6e80).
- **L7 running:** eef4a2 (seed 13 water world, 1500 Myr) and seed 12.
- **L6 showcases done** (worlds and zooms made): 2b59b1, 60a706, 9219ac, 2552cf, 482ff7, f397a9.
- **Agent `falls2`** is investigating undesigned "drop" falls of up to ~1 km in zooms.

**Update 05:25:**
- **Merged:** mantle tip (c8a06d2: rift stress scaled by plate size), falls2 (designed falls the river bypassed) and l7jumps (margin subduction breaks off one basin). All 76 zooms were rebuilt after falls2.
- **Running on the final code:**
  - L7 verification runs, seeds 1 and 13, 1500 Myr;
  - the six L6 showcases re-made, then worlds, highlights and zooms (`showcase2.sh`, then `post2.sh`).
- **Once those finish:** delete the older L6 showcase runs (2b59b1, 60a706, 9219ac, 2552cf, 482ff7, f397a9) with their worlds and zooms. Keep the L7 runs from tonight (pre-fix, but informative).
- **L8 15b1b0** (pre-fix code) is due ~05:50.
