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
