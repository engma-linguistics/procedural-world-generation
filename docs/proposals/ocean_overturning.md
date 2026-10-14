# Ocean overturning circulation: spec and follow-up (2026-10-13/14)

*Moved from `docs/plan_next.md` (Round 2 user decisions) and `docs/morning_decisions.md` item 3 on 2026-10-14. Implemented as `planet/ocean.py` (branch `ocean`). The follow-up plan (moisture transport, then removing the spin-up rule) is epic PW-013 on the board (`uv run python issue-tracking/board.py tree PW-013`).*

## Original spec (user request, 2026-10-13)

**Overturning (deep) ocean circulation:** wanted, done physically. Density from SST and salinity, with salinity from evaporation minus precipitation, so it comes after `water`. Use a zonally averaged or box overturning per basin, with poleward heat transport following from it (the "mild Norway" fix).
  The salinity budget must include:
  - **river runoff** entering each basin at its river mouths (it freshens basins like the Arctic);
  - **moisture carried by the wind** from one basin to another (part of why the Atlantic is saltier than the Pacific);
  - **sea ice:** brine is rejected where it forms, and fresh water is released where it melts;
  - **ice-sheet meltwater.** In the main run this is small, since ice is near equilibrium at each climate update. In the glacial time zoom it matters a lot: meltwater pulses (Heinrich events, Younger Dryas) can weaken or shut down the overturning. So the time zoom should feed its ice melt into the same salinity term.
  (User request 2026-10-13.)

## What was built, and its conservative choices (morning decision 3, 2026-10-14)

The overturning circulation is merged (plots in `docs/review/ocean/`). On Earth it sinks in the Nordic and Labrador seas and not in the North Pacific. Norway's coastal sea temperature goes from 0.9 to ~5–6 °C, against ~7.5 °C observed. The agent chose these, all easy to revisit:
- **(a) Spin-up rule.** The North Atlantic "on" state comes from a spin-up rule, because the model's rain has almost no Atlantic–Pacific evaporation contrast. Without the rule, the Nordic seas stay too fresh to sink. The real fix is in the moisture transport (the rain model), which is a bigger job. **Is a spin-up rule acceptable as "nudging"?**
- **(b) Rain doesn't see the ocean's warming.** One extra temperature pass, no rain recompute.
- **(c) Time cost.** Compute costs +0.17 s per climate step (~35% more). A 1 Gyr level-6 run adds ~15 s.
- **(d) The rest of Western Europe's winter error is in the air model.** It is still ~4.8 °C too cold, because of how far sea air reaches inland in winter, not the ocean. That's a separate climate item if you want it.

**Owner (2026-10-14):** spin up its own plan: fix moisture transport first, then remove the spin-up rule and check the Atlantic turns on and the Pacific stays off by themselves. Use Earth as a test analogue, never chase 100% parity.

## Known behaviour at merge (from the `ocean` agent)

- **Earth:** ~11 Sv sinking in the Nordic, Irminger and Labrador seas (observed AMOC ~17 Sv) and none in the North Pacific. The Antarctic margin makes only ~2.5 Sv (AABW ~10–20 Sv): the Weddell and Ross seas are too fresh (~34.0 psu against 34.4–34.6). Their winter brine is weak, and there's no shelf/polynya ice factory.
- **Labrador Sea is too warm** (~7 °C sea surface against ~3.5 °C): the inflow feeds it along the Labrador coast. SW Greenland and Iceland now get summers just above 10 °C, so ET becomes D there (Reykjavik's coldest month went from −29.6 to −12.9 °C, observed −0.6 °C).
- **The North Atlantic's on-state is found by a spin-up rule,** not by history. With no earlier state, every polar sea that is nearly dense enough starts sinking, and the drho threshold tightens over the iterations. Without that start, the model's own salinity leaves the Nordic seas too fresh to sink: its rain model has no Atlantic/Pacific evaporation contrast to speak of. Hosing ~1 Sv into the North Atlantic shuts it down. Once the hosing stops it recovers within 2–3 climate updates, so it has no lasting off-state.
- **Its warmth adds to the 50–70°N ocean band** (`moc_zonal` = 0): that band's sea is now ~2–4 °C warmer than before. The Köppen score preferred this (70.69% against 70.50% with half of it taken off the band).
- **Cost:** about +0.15–0.2 s per climate.compute at level 6 (0.48 → ~0.65 s unloaded). The overturning is solved on the level-5 grid, but the sea surface and the air temperatures are carried a second time on the full grid.
