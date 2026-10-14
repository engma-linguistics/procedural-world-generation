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
   - **Then overturning circulation** in `climate.py`.
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
5b. **Real waterfalls in the zoom.** Where the coarse river drops steeply (big drop and discharge, the `waterfall` highlight), keep a knickpoint: a resistant-rock lip with a plunge pool and a gorge cut back upstream, instead of grading the reach smooth. Fix the lake-outlet cliff at the same time. The user wants big waterfalls most.
5c. **Lakes on the run globe.** Runs store no lake layer, so a 390,000 km² lake (a89254 @ 1592) shows only as a dip. The simulation already computes lake levels and kinds each step (`surface.erode` → `hydrology.lakes`), so keep them and store `lake_depth` and `lake_kind` per frame. Then draw lakes in the run viewer like worlds do. Do it after `store` and `mantle` merge.
6. **Regenerate the six showcase worlds** with the new code, then delete the old ones.

## Backlog (user notes, 2026-10-14)
- **Delta types.** Real deltas differ by what dominates (Galloway's classification):
  - **river-dominated:** the Mississippi's bird's-foot, a few long distributaries reaching out into calm deep water;
  - **wave-dominated:** the Nile and São Francisco, a smooth arc-shaped coast with beach ridges;
  - **tide-dominated:** the Ganges–Brahmaputra and Mekong, many funnel-shaped channels and islands (the Sundarbans).

  The model has no waves or tides. Wave energy could come from the winds and fetch (open water the wind blows over). Tidal range could come roughly from shelf width and basin shape. Then pick the delta shape in the zoom per type. Medium effort.
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
- **Not done:** glacial erosion, proglacial lakes, and the meltwater link to ocean salinity (see overturning in Round 2).

**Climate**
- **Norway too cold:** its sea surface is about 1.3 °C against about 7.5 °C observed, and W European winters are about 4 °C too cold. Waiting on the overturning circulation.
- **Gulf Stream and Kuroshio separate from the coast too far north** (a Stommel-model limit), so the Oyashio region is too warm.
- **Rain is patchy cell to cell on flat ground:** neighbouring cells differ by a median 1.5× near the hothouse lake. Diagonal streaks in rain maps predate the gyre work.
- **Older Earth errors:** Sahel and East Africa too wet; Indian and Chinese monsoons too dry; Siberia, Alaska, Quebec and NE China winters 5–10 °C off.
- **Visible in the Earth world's temperature difference view (8e052d):**
  - The East Antarctic interior is about 10 °C too warm.
  - NE Canada, Labrador and Greenland's margins are too warm; this also blocks Laurentide ice inception in the time zoom.
  - The Andes and the Tibetan margin are speckled.
- **The jet stream is broad and zonal,** with modest meanders.
- **The run viewer's climate is up to 4 Myr stale** (`climate_every` = 8 vs keyframes every 4). The fix is queued with the parallel climate kernels.

**Rivers, lakes, sediment** (see `docs/review/rivers_lakes_deltas.md`; `water` and `zoomwater` address most)
- **No evaporation:** discharges are 2–5× too high and there are no closed lakes. (`water`)
- **Sediment piles reach 33 km** (Earth max about 20–22 km). (`water`)
- **Drainage switches outlet in one step when a rift opens.** (`water`, optional)
- **Zoom lakes are sinks:** the water level is wrong and the floor is a flat 42 m; there are no deltas or distributaries. (`zoomwater`)
- **Evaporation is merged (`water`); what's left:**
  - **Drainage memory** is not implemented. Old channels would have to move with the plates; the physical damping is rift-flank uplift, which is a tectonics change.
  - **Generated worlds have almost no closed basins after ~150 Myr** (0–2% of land drains inland, against 21% on Earth's terrain). Sediment and erosion fill every hollow, and the tectonics makes no new interior basins (foreland or intermontane basins, rift-flank highs).
  - **Sediment is treated as crust-density rock in the isostasy,** so filling deep water takes ~5× its depth in sediment (Earth ~3×). About 400 cells sit at the 18 km metamorphic cap. **The user chose (2026-10-13) to give sediment its own lower density,** compacting with depth. Do it after the tectonics split, alongside B′.
  - **The 20 m "unresolved channel" threshold** for coarse hollows is a judgement call.
  - **Discharge misses come from the rain model:** the Yangtze ends in a lake, and the Lena, Mekong and Ganges are too small (dry China, Siberia and Indian monsoon). The Nile is 19× too big (Sahel too wet). With observed rain, magnitudes are about right.
  - **The Orinoco gauge picks up the Amazon,** a coarse-routing artifact.
- **Zoom lakes and deltas are merged (`zoomwater`); what's left:**
  - The lake outlet river drops about 140 m within a few km (a cliff waterfall). The downstream river's profile is built up from the sea, well below the lake. It needs a floor on the outlet channel that steps down gradually downstream.
  - The zoom sees only part of a big lake's catchment (45k of 125k m³/s). River water entering at the zoom's edge can drain straight back out through the edge.
  - Delta fans are small, and their branches run straight (only 8 possible step directions). There are no distributaries when the fine-scale river reaches the sea away from the coarse mouth.
  - A small lake fragment sometimes has no outlet and acts as a sink.
  - The real `lake_level`/`lake_kind`/runoff layers from `water` are untested in the zoom (only the fallback was exercised).
- **Fjords aren't carved in the zoom:** fjord coasts are only detected.

**Crust and continents**
- Continental area overshoots to about 45% (target 40%).
- Ocean plate boundaries are ragged.

**Highlights**
- ~~Several highest peaks sit under ice caps~~: an iced peak now ranks lower and the highest ice-free peak is added (`hl2`).
- ~~Earth-like A's longest river crosses a cold, dry polar continent~~: thin rivers over barren land rank lower (`hl2`); it's still listed.
- The hothouse wine country has 41 °C summers (Köppen-correct, not appealing).
- ~~Pre-made zooms need re-making after `zoomwater` lands~~: re-made for a434c5 and cec38b (`hl2`).
- **No big waterfalls in the zoom except at lake outlets.** The landscape pass grades every river (slope ~ Q^-0.5), and coarse rivers are carved along a smooth, linearly interpolated floor, so a coarse steep reach (e.g. 315 m over 220 km at 61,000 m³/s) becomes a smooth valley; pixel-scale falls on rivers are tens of metres. The one big kind, a lake outlet (105 m at 102,000 m³/s in a434c5's big lake, zoom cc9dcf; 153 m at 45,700 m³/s in 42bc11), comes from the zoom cutting the outlet river's floor 12–45% below the coarse ground: the "cliff waterfall" known issue under zoom lakes. The coarse world itself is flat there (lake 284 m, next cells 284 and 275 m). Real falls would need the zoom to keep a knickpoint where the coarse river drops steeply (e.g. a hard-rock lip), a zoom model change.
- **Worlds sliced before `water` (a434c5, cec38b) have no lake_kind and no closed basins**, so salt lakes, salt pans and inland basins don't appear; exposed evaporite beds on dry land stand in as "salt flats".
- **Canyons are weak at 110 km cells:** the Earth world finds the Kura valley and the Siang below the Tsangpo gorge, not the Grand Canyon. Rain shadows find the Himalaya, SE Tibet and the Atacama/Altiplano edge, not the Sierra Nevada. Plateaus find Tibet, Wyoming and the Altiplano (3rd). The Earth world's salt lake is in Hungary (the model climate leaves the Pannonian basin closed); the Caspian is below sea level, so it's the landlocked sea.

**Viewer / Earth world** (from the viewer2 report)
- The Earth world `8e052d` has about 7% of its land as lakes (no erosion, every pit fills). Re-run `tools/earth_world.py` after `water` merges and delete the old one.
- The Earth world can't be zoomed (no rock layers).
- The cold-era timeline tint is stripy where temperature flickers from frame to frame (kept unsmoothed).
- Time zooms made from the button run away too: f87163 reaches −520 m with ice 7.4 km thick. This is the "generated worlds glaciate too hard" issue above.

**Infrastructure**
- **Parallel numba kernels aren't safe for concurrent calls from several Python threads** (climate and `kernels.locate`). The API runs one job at a time; keep it that way, or add a lock.
- `NUMBA_NUM_THREADS=4` is often faster under load on this 4P+4E-core Mac. Parallel launches cost about 40–57 µs each.
- `api.Jobs` state is in memory only and is lost on server restart.
- The zoom request can't choose seed, iterations or resolution (always 500 px).
- The Earth-score metric has three definitions (B5 in the code review). Unify them after the climate work settles.

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
