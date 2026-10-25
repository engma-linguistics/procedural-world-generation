# Coupling audit (2026-10-25)

This audit looks for places where two systems disagree about the same quantity. Typically one module estimates, proxies or stands in for something another module now computes itself, or the same effect is counted twice. It does not repeat the [assumptions audit](../assumptions-audit/README.md), which checked the model against reality.

It covers main at d89f602 plus the unmerged climate branch **v1-finish-12** (the `agent-a509febb63d5ebd7d` worktree; its old `worktree-agent-a509...` branch has no commits beyond main). Everything was read only, and no simulations were run. The data are in [findings.json](findings.json), with one inbox draft per finding (`issue-tracking/inbox/draft-*.md`, `found_by: coupling-audit`).

## Findings, ranked for the Earth-like v1 finish

| # | Sev | Finding | One side | Other side | Measured | Physics lane |
|---|---|---|---|---|---|---|
| C1 | **high** | The weathering sink counts CO2 twice on planted ground. It applies GEOCARB's FERT law to an NPP that the plants already grew at the run's CO2. | earth.py (branch) `co2_law` L121-125 | `plant_factor` L209-212, fed by `update_vegetation` L482-491 at `pco2(sim.co2)` | NPP rises 1.19x per CO2 doubling. That adds about 0.11 to the sink's log-slope on top of FERT's 0.2, about 55% too strong. NPP is below 500 on 84-93% of vegetated land. | **first** |
| C2 | med | Plume and hotspot magma is modelled but never outgasses. The resized drift (0.8 C) now stands only for burial and ocean chemistry. | earth.py (branch) L310, the source is ridges plus arcs | simulation.py `_physics` (hotspots, cap_plumes); params.py `climate_drift` comment | Code read only; nothing outgasses. In the literature, plume degassing is about the size of ridge degassing (Marty & Tolstikhin 1998). | **second** (needs-decision) |
| C3 | med | Weathering's runoff factor follows the global-mean rain law (3%/C). The land runoff the climate computes is not used. | earth.py (branch) L227, `climate_coef` L108-111 | climate.py L2278-2298; `sim.runoff` | Ice-free land rain grows 0.5-2.3%/C (4 L6 runs), against 3%/C. That makes `climate_coef` 5-17% too strong. | **third** |
| C4 | med | The time zoom treats the run's moment as the interglacial peak and only ever cools from it. So the run erodes, weathers and sets sea level at interglacial conditions through whole icehouse eras. | timezoom/cycle.py, forcing.py L88-94 | earth.py `global_temperature`/`ice_sheets`; overview 2.8 ("swings around" the run) | 8 L7 zooms: mean I 0.44-0.57, mean dTg -1.3 to -6.2 C, mean sea level -5 to -205 m. The zoom start equals its keyframe exactly. | ice-age epic (needs-decision; v1 needs a doc fix) |
| C5 | low-med | The glacier bed rule ("slides if the warm month is above -8 C") dates from the bare-ground frame. Since PW-277 it reads the ice surface. The time zoom uses a sliding rule instead. | earth.py `erode` k_mult (line predates PW-277) | earth.py `update_climate`, `ice_surface` overwrite; timezoom params | 16-47% of iced cells count as wet-based (10-35% of ice over 1 km) in 4 runs | - |
| C10 | low-med | On the branch, zooms name cloud forest from the light's shade. Runs and worlds pass the sky's cover. | branch zoom_vegetation.py, no `sky=` | branch world.py and earth.py pass `sky=` | Tropical highland cells at cover >= 0.65 drop 34% (6909cb) and 25% (2a7385) | land with the v1-finish-12 merge |
| C6 | low | The time zoom adds a vegetation-albedo cooling on top of `glacial_cool`, which is sized on Earth's whole LGM cooling and so already includes vegetation. | timezoom/params.py glacial_cool | timezoom/plants.py `measure` | The vegetation term is -0.09 to -0.61 C, 3-7% of peak cooling | - |
| C7 | low | Reefs test the air temperature against `reef_temp`, which is documented as SST. | earth.py `reefs`, volcanism.py L393 | params.py reef_temp; climate sst; coastal.py | Air is 1.5-2.0 C below SST over shallows, which gives 4-16% fewer reef cells (4 worlds) | - |
| C8 | low | The ice-albedo term counts from real Earth's ice share (3.1%), not the model's own Earth ice at dT = 0 (2.53%). The ice share is a cell count, not area-weighted. | earth.py EARTH_ICE | tools/ice_probe.py (overview 2.8) | +0.23 C | fourth (tidy-up) |
| C9 | low | Light, PET, the ice balance and the orbital anomalies all use today's S0. The run's star is 8-15% fainter early, or moved by the star thermostat. | orbit.py S0, climate.py S0_MJ | earth.py `star_forcing`, `star_control` | PAR and PET are 8% too high at the start of a 1 Gyr run. Exact at the run's end on the branch. | - |
| C11 | low | Zoom glaciers read the tilt from `params.tectonics.tilt`; plants and climate read `params.tilt`. | zoom.py:1900, zoom_fine_forms.py:76 | zoom_vegetation.py:289, zoom.py:3352 | Only bites on generated or Earth worlds with a non-default tilt | - |
| C12 | low | The zoom's `loess` layer is overwritten by the soils' world loess, not the glacial loess the terrain was built with. | zoom.py:3320 | zoom.py:3325 `**veg_l` (zoom_vegetation.py:265) | Code read | - |
| C13 | low | Snowpack is computed two ways (months vs icemass PDD), and permafrost three ways. A dead helper and a stale `ICE_DDF` comment remain. | climate.py `months` | icemass.py; soils, vegetation.flooded, hydrology | Not measured | - |
| C14 | low (dormant) | `finish.orbit_dt` under `orbit_resp=seasons` gives the climate bed + 2x ice. | finish.py orbit_dt | climate.compute `surf = elev + ice` | Code read; the default `run` path is unaffected | - |

### For the physics lane (climate and carbon)

Take these in order: **C1**, then **C2**, then **C3**. All three change the carbon thermostat's strength or its inputs, so re-measure the PW-865 bar once after them rather than three times. C1 is likely the largest: CO2's equilibrium swing for a given source/sink imbalance is about a third smaller than the literature laws intend. That bears directly on the faint-star compensation and the end-CO2 diagnosis. C8 is a one-line follow-up for the same pass. C10 is not physics, but it should land with the v1-finish-12 merge.

None of the 14 findings is fixed on v1-finish-12. C1 exists on main too, as X^0.4 plus the NPP plant factor. C3 and C10 were introduced on the branch (v1-finish-11 and v1-finish-12).

## Method

1. I ran a fast-forward to main and read the wiki index, overview sections 2.5-2.8, the assumptions audit (to avoid repeating it) and decisions.md (for rulings).
2. I read the core coupling code myself: `earth.py` (carbon, temperature, erosion and climate update order), `climate.compute`'s temperature, rain and shade, `params.py`, and the time zoom's forcing, cycle and plants on v1-finish-12. Three Explore sweeps covered the rest of `planet/`: the time zoom against the run, the world and zoom against the run, and surface, hydrology, soils, vegetation and the downstream consumers. That gave about 60 candidates. I verified every finding kept here against the code myself.
3. Each candidate got a small offline check on existing data (read only, a few minutes of CPU in all). The scripts are in the session scratchpad and are not committed:
   - land rain versus dT across keyframes of runs 0ceebf, 172922, 343058 and 2b0b65;
   - wet-based ice share and lakes under ice, from the keyframes of four runs;
   - soils' Fu runoff against the climate's, and air temperature against SST over shallows, in four worlds;
   - the time zoom's index, dTg, vegetation term and sea level, in eight L7 zooms, plus whether each zoom starts at its keyframe;
   - the run's vegetation variant on world 6909cb at 350 and 700 ppm (branch code), for C1;
   - sky cover against shade on tropical highlands, for C10.
4. Before writing anything up, I tried to refute each candidate. I dropped it if it was a documented, deliberate approximation that no newer mechanism contradicts, if the data showed the two sides agree within a crude model's tolerance, or if the earlier audit or an owner ruling already covers it.

## Rejected

| Candidate | Why dropped |
|---|---|
| Weathering's temperature factor uses the cell's own temperature against 15 C | The references are learnt with the same per-cell law, so the absolute frame cancels. |
| Global ice albedo and local ice-surface cooling both count the ice | They are different effects (planetary albedo vs surface energy), and dT = 0 includes both. |
| Rain counted twice in stream power (rain factor x sqrt(flow)) | Documented and calibrated (PW-055); a standard approximation. |
| Run hydrology makes lakes under ice | 0 lake cells under ice across 171 keyframes of 4 runs. |
| Soils' own Fu water balance | Within 6-12% of the climate's runoff (0.89-0.94x in total). Consistent. |
| Run plants are the cheap variant (no soils, no crown fire) | Documented; crown fire is already on the assumptions audit's list. |
| Keyframe warm start from tree cover vs a slice's true fractions | tree_cover is 0.89x the tree cover fractions; a warm start that the equilibrium resolves. |
| Time zoom snowfall kernel at 7%/C vs the climate's 3%/C | Local vs global laws, both defensible; reset to the full climate every 10 kyr. |
| Circular reference orbit vs a climate calibrated on today's | Consistent between run and zoom; a calibration nuance. |
| `temp_response` duplicates `climate.temperature`'s shape | It is the identical polynomial. |
| Carbonate, coal and sediment erosion counted as silicate weathering | Assumptions audit finding 14. |
| The glacial index stands in for CO2 and ice albedo | Owner-ruled kludge (PW-471, under PW-470). |
| Run vs zoom sea-level-from-ice laws | The zoom reports changes from a shared start; they differ only for marine ice. Low, and belongs to the ice-age epic. |
| Köppen and plants see the pre-update sea level | About 10 m per step. |
| The zoom re-derives the run's state at its start | Six zooms checked; they start exactly at the keyframe. |
| `orbit_resp` run vs seasons (3x different) | The default `run` is shared; tracked in PW-555. |
| The four known findings (star frame, frozen balance, plants' sunshine, drift double count) | Fixed on v1-finish-12; C10 is the sunshine fix's leftover. |

## Not assessed (left for a follow-up sweep)

The sweeps raised these, but I did not verify or measure them, so they have no drafts:

- sea ice is computed three ways (climate `open_share`, `coast.sea_ice_share`, humanuse harbours);
- lineages subtract ice from "elevation" in every frame type, which is right only for time zooms (`crop_defs.py:55`, `animal_defs.py:35`, `history.py:84`);
- the soils' own erosion rate vs the run's denudation;
- the BQART sediment load vs the routed load;
- coal swamps (run vs resources), dunes and deserts (five rules), and laterite (resources vs soils' weathering stage);
- humanuse's Holdridge PET in zooms;
- the world climate runs on textured terrain but keeps the run's ice;
- the world's rain starts cold while the run's is warm-started;
- run keyframes define July/January differently from worlds, and the keyframe jet comes from a different temperature stage;
- slope effects may be counted twice in the zoom's PET, and the diffuse light share is fixed;
- the zoom builds `fractions()` on the raw world, not the land view;
- zoom glaciers interpolate the seasons differently from zoom plants;
- the finished world's `orbit_dt` uses a different bright mask from the time zoom's.
