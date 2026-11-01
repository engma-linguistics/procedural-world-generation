# Arc CO2: what the code does, and why candidate A changes nothing (lane 100e, PW-950)

## In plain words

The plan was to make volcanic-arc CO2 follow the sinking plates (convergence rate times trench length) instead of
the continents' volume thermostat. The code already does that, and has since PW-741 (commit `04b9fff5`). The
thermostat's boost never reaches the CO2 source. Lane 100d's diagnosis read the thermostat's arc growth (the crust
budget's `arc`) next to the total CO2 source and took the one for a driver of the other. A trace of the source's
parts shows that they don't move together. So A isn't built. Nothing here needs a source, because no relation is
added or changed.

## What the code does now

- `crust.arc_growth` returns two fields. `growth` is the crust the arcs add: `arc_growth x heat x convergence` at
  every trench edge, times the volume thermostat's gain on continental overriding cells. `nominal` is the same
  without the gain: the melt the slab makes.
- `Simulation._physics` passes `nominal` (as `outgas`) to `earth.global_temperature`. There the source is
  `new floor + 20 x sum(outgas) + plumes`. So the arc part is the mantle heat times the sum, over the trench edges
  subducting this step, of their convergence (clipped to 0-15). That is convergence rate times trench length,
  spread over the arc belt behind the trench (1.6 L5 cells, with the forearc gap).
- Two details differ from a strict per-edge sum. Edges that share an overriding cell count once, at their largest
  convergence (`np.maximum.at`). And the belt is cut where it meets another arc's belt (`spread`: each cell takes
  its nearest source). Both scale with trench length, and neither involves the thermostat.

## The trace (tracediag.py now logs the source's parts and the slab; L6, seeds 1 and 3)

Arc part = `20 x sum(outgas) / scale^2`, the mean per step. Thermostat arc growth = the crust budget's `arc`, in
km x L5 cells. Main against `neck_km=200 rise=1 slope_k=1000`:

| seed 1 | arc CO2 part, 0-300 Myr | arc CO2 part, 600-1000 | thermostat arc growth, 0-300 | thermostat arc growth, 600-1000 |
|---|---|---|---|---|
| main | 2253 | 2640 | 10 937 | 28 787 |
| creep | 2287 (+1.5%) | 2287 (-13%) | 14 816 (+35%) | 38 663 (+34%) |

| seed 3 | | | | |
|---|---|---|---|---|
| main | 2185 | 2711 | 10 177 | 21 692 |
| creep | 2191 (+0.3%) | 2328 (-14%) | 11 761 (+16%) | 49 158 (+127%) |

The thermostat's growth rises by a third or more with the creep. The arc CO2 doesn't move with it during the
reference years (0-300 Myr), and late in the run it falls while the growth rises. The late fall is in the slab:
convergence x trench length, `conv_sum` in the trace. With the sea-level fix on (code2), seed 3's `conv_sum` was
2688 (0-300 Myr) and 2507 (600-1000) without the creep, and 2509 and 2239 with it. Over 600-1000 Myr the trench
length rises (more trench edges), while the mean convergence falls (5.3 to 4.4-4.7).

## So what does cool the creep's worlds?

The source's reference is learnt from the run's own source over the first 300 Myr (`REF_FREEZE`). After that the CO2
follows late slab flux against early slab flux. Any change that alters the plate history moves that ratio (in these
screens, by -14% to +22% between arms on the same seed). That is PW-1158's question (the source running low late in
some runs), not a bookkeeping link to the thermostat. The arms here differ in both directions, so a two-seed screen
can't say whether the creep lowers late convergence systematically. Only the paired judge can.
