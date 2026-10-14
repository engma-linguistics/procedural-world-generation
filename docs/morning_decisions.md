# Judgement calls for the morning (2026-10-14)

Collected overnight. Each item: the question, the options, and what was done in the meantime (if anything).

## 1. Which viewer layers should draw lakes?
Lakes now show on the run globe (demo run **8dc2f2**: open it, elevation layer, t≈180–360). They are drawn only on **elevation** and **biome**, because on the climate (Köppen) and rainfall layers the map's own blues and greens get confused with lake colours.
- **A (current):** lakes on elevation and biome only.
- **B:** lakes on every layer with a dark outline so they stand out.
- **C:** a "Lakes" overlay toggle, like Rivers, that works on any layer.

My lean is C.
