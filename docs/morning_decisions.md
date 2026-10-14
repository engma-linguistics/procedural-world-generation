# Judgement calls for the morning (2026-10-14)

Collected overnight. Each item: the question, the options, and what was done in the meantime (if anything).

## 1. Which viewer layers should draw lakes?
Lakes now show on the run globe (demo run **8dc2f2**: open it, elevation layer, t≈180–360). They are drawn only on **elevation** and **biome**, because on the climate (Köppen) and rainfall layers the map's own blues and greens get confused with lake colours.
- **A (current):** lakes on elevation and biome only.
- **B:** lakes on every layer with a dark outline so they stand out.
- **C:** a "Lakes" overlay toggle, like Rivers, that works on any layer.

My lean is C.

## 2. Zoom waterfalls are very powerful
Zoom waterfalls are merged (example pictures in `docs/review/falls/`). The biggest come out at 140–200 m on rivers carrying 20,000–60,000 m³/s, i.e. tens of Niagaras. Real rivers that big (the Congo, the Mekong) usually lose their drop in long rapids or cataracts, not single falls. The cause is upstream: the coarse world drops big rivers 500–700 m over a few hundred km.
- **A:** keep it. It's dramatic and physically consistent with the coarse terrain.
- **B:** spread the drop over more, smaller steps as discharge rises.
- **C:** fix it at the source with more coarse-scale river erosion, so big rivers grade down over geological time.

My lean is a little of B now, then C as part of the "outlet incision" backlog item.

**Update 04:00:** a follow-up fix (`falls2`) found that the biggest falls in tonight's zooms were glitches: the river ran on a raised ledge and then dropped off its side. Now that falls must fit under the coarse ground, they come out smaller. Big rivers mostly get 50–150 m (median scale 0.34 of the design), and only steep mountain fronts keep 250–550 m. So the "too powerful" worry has mostly gone away, perhaps too far: the question is now whether you want **taller** falls, which needs the zoom to build stepped plateau country above the escarpment.

## 3. The ocean overturning circulation's conservative choices
The overturning circulation is merged (plots in `docs/review/ocean/`). On Earth it sinks in the Nordic and Labrador seas and not in the North Pacific. Norway's coastal sea temperature goes from 0.9 to ~5–6 °C, against ~7.5 °C observed. The agent chose these, all easy to revisit:
- **(a) Spin-up rule.** The North Atlantic "on" state comes from a spin-up rule, because the model's rain has almost no Atlantic–Pacific evaporation contrast. Without the rule, the Nordic seas stay too fresh to sink. The real fix is in the moisture transport (the rain model), which is a bigger job. **Is a spin-up rule acceptable as "nudging"?**
- **(b) Rain doesn't see the ocean's warming.** One extra temperature pass, no rain recompute.
- **(c) Time cost.** Compute costs +0.17 s per climate step (~35% more). A 1 Gyr level-6 run adds ~15 s.
- **(d) The rest of Western Europe's winter error is in the air model.** It is still ~4.8 °C too cold, because of how far sea air reaches inland in winter, not the ocean. That's a separate climate item if you want it.

## 4. Delta types: fitted constants
Waves, tides and the Galloway delta types are merged. To see them:
- **Demo zooms:** river-dominated `00975d`, wave-dominated `f81832` (with a barrier lagoon), tide-dominated `ce4b72` (funnels and tidal flats).
- **New colour layers in the viewer:** "wave power" and "tide range".
- **Screenshots:** `docs/review/deltas/`.

The wave and tide formulas are physical (wind-sea growth with fetch, swell decay, shelf resonance, funnelling), but about ten constants were fitted on Earth by grid search. Wave power is within 2× at 25 of 30 coasts, and tides within 2× at 21 of 23 sites. Thresholds: lagoons appear above a wave weight of 0.3, fingers above a river weight of ~0.4, and anything without a weight of at least 0.5 is labelled "mixed". **Are fitted constants OK here?** They're the honest option at 110 km cells. The bigger miss is upstream: the model's Ganges is 10× too small, and Southern Ocean storms are too weak.

## 5. Supercontinent cycle: good enough?
Merged. Every level-6 seed now forms a supercontinent at least twice in 2 Gyr. Before, 3 of 4 never reassembled. Assemblies form over cold mantle and break up once the mantle under them warms. Showcase run **6d9dcf** (seed 2): over 25% of the surface at 0–508, 892–976, 1736–1772 and 1948–1988 Myr.

Shortfalls:
- **Uneven cycles:** some seeds go quiet for ~1 Gyr.
- **Long gaps:** assemblies are 400–870 Myr apart, against Earth's ~300–700 (Rodinia → Pangaea ~750).
- **High land:** 34–36%.
- **Few plates:** a median of 6–7, sometimes 2–3.

Options:
- **A:** accept it, and tune land and plate count later.
- **B:** spend another round on regularity: stronger insulation, shorter mantle memory.
- **C:** restore some plate births with a gentle "big hot plate splits" nudge tied to the mantle field.

My lean is C (the plate count is the most visible flaw), then A.

**Note:** tonight's L7/L8 runs predate the plate-size rifting fix (c8a06d2), merged at 04:20. The six L6 showcases do too.
