# Lane A handoff (2026-10-22, second session, ~100 tool calls)

Lane A is base-climate stages 1–3 and then the checkpoint. **Stage 1 (PW-458) has not passed.** Attempts 1 and 2 of
3 are used.
- Attempt 1 was the factor separation plus the step-consistent uptake through sea ice.
- Attempt 2 was the bulk sea-air exchange, which subsumes the step-consistent uptake.

Committed on this branch: `tools/overturning_report.py` (PW-572, item 1) and this note. No model change is
committed.

## Uncommitted model edits in the worktree (experiments: finalise or revert)
- **`planet/climate.py`, `_rain_args` and `_rain`: the bulk sea-air exchange (attempt 2).**
  - The air over the sea now takes up `1 − exp(−open × wind × dt / sea_fetch_km)` of its deficit to `src_q` per
    step, where it used to fill instantly.
  - New TUNE keys: `sea_fetch_km` = 770 (a ~1 km boundary layer / C_E ~1.3e-3) and `sea_wind_min` = 3 m/s.
  - `tools/moisture_budget.py`'s probe follows it (`open_sea[k, i]`).
  - This changes outputs: the goldens would need refreshing.
- **`planet/ocean.py`, `overturning`: `x_ref_hemi`** (TUNE, default 0). Each hemisphere's polar sea sets its own
  deep-water reference, instead of one shared reference per connected ocean.

## Results

### Overturning (`tools/overturning_report.py --earth --world 119973 28442c 607540`)

| | Earth NH Sv (Nordic / Irminger / Labrador / Baffin) | Norway open in winter | Fenno Jan / Jul bias | worlds' NH / SH Sv |
|---|---|---|---|---|
| HEAD | 5.1 (0.1 / 1.3 / 1.1 / 2.6) | 0% | −18.5 / −5.3 | 16.3/16.9, 16.4/16.9, 15.6/14.6 |
| fetch 770 | 13.0 (5.9 / 2.6 / 1.8 / 2.4); SH 1.15 | 43% | −18.5 / −5.0 | 16.1/16.8, **0.0**/15.8, **0.05**/11.1 |
| fetch 770 + x_ref_hemi | 7.2 (0.3 / 2.8 / 1.8 / 2.5) | 0% | −18.5 / −5.4 | 16.1/16.6, 15.0/15.6, 15.1/6.8 |

- With the fetch, Earth reaches the bar's strength and puts 79% of its sinking in open seas. But Baffin still sinks
  2.4 Sv, and **two of the three generated worlds lose their northern overturning**.
  - The cause is the shared deep-water reference per connected ocean. It makes the hemispheres compete
    winner-take-all.
  - `x_ref_hemi` fixes the worlds, but on Earth the northern reference is then Baffin's water, so the Nordic Seas
    are gated out.
- **The crux on Earth is Baffin Bay's water.**
  - Without the overturning it is 35.2 psu (observed ~33.5), with a winter density of 1030.7 kg/m3. That is ~2 kg/m3
    above any other northern sea.
  - The causes are its evaporation (517 mm against 237 mm of rain), the export of its sea ice, and brine. There is
    also no Arctic water coming in: the Canadian Archipelago is closed at L5 and L6.
  - With the overturning, 76% of its surface water is the 36.6 psu inflow, arriving under the winter ice.
- **Fennoscandia's −18.5 C January doesn't move, even with the Norwegian Sea partly open.**
  - `_air_temps` counts a sea as open in winter only where `sst − sea_half > FREEZE` (`open_w`).
  - `sea_half` is 5.3–5.8 C at 62–75N, against ~2.5–3 C observed. So the Norwegian Sea's sea air is the land's winter
    air.
  - This is the older half of PW-458 ("the drift stops at 55N"), and it is the next thing to fix.

### The rain (earth_check, HEAD → fetch 770)

| measure | change | verdict |
|---|---|---|
| land mean P | 1138 → 1284 mm (GPCC 791) | worse |
| land P, 90th percentile | 2611 → 3795 | worse |
| log-rain correlation | 0.617 → 0.659 | better |
| Köppen arid (group B) share | 18.0 → 27.5% | better |
| Köppen group match | 71 → 70% | slightly worse |
| exact match | 31 → 34% | better |
| cities in the wrong group | 18 → 25 | worse |
| runoff / rain | 0.47 → 0.59 (Earth ~0.37) | worse |
| Sahara and Arabia | drop off the worst list | better |
| Sahel, East Africa, Gobi | wetter | worse |

So it is **not merge-ready**: the rain isn't "no worse overall". See the inbox draft
`draft-sea-evaporation-bulk-exchange.md`.

## Next steps (attempt 3, the last for stage 1)
1. Smaller seasonal swing where the overturning's deep inflow makes up the surface. The inflow is a layer hundreds of
   metres deep (moc_q0, moc_width), so its share should shrink `sea_half`, both in `ocean.solve`'s winter density and
   in `_air_temps`' `open_w`. This is the mechanism behind the frozen Norwegian Sea and Fennoscandia's −18 C.
2. Baffin: look for a planet-general mechanism.
   - Lean: the inflow can't make up the surface where its own winter would freeze, but **without** the ratchet that
     made the hard lid collapse (attempt 1). That means a continuous share, recomputed each iteration from the
     inflow's own route temperature, not a lid that only ever grows.
   - The deep-water reference per hemisphere (`x_ref_hemi`) is needed for the generated worlds either way.
3. The bulk exchange: either tune it toward "no worse" (the land is too wet, the 90th percentile too high), or
   park it as PW-015's and go back to HEAD's instant fill. It moved the overturning the most, but it also tipped the
   generated worlds.
4. Then the bars: `uv run pytest -q`, the goldens, earth_check, the scorecard.

Scratch scripts are in `/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/laneA/`:
- `capture.py`, `factor*.py`, `exp.py`, `earthmoc.py`;
- `head/`: HEAD's planet and tools, for the "before" runs;
- `ec/before.txt` and `ec/fetch770.txt`: the two earth_check outputs.
