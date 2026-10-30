---
title: "Run ice sheets have no flow: a sheet's margins can't be resupplied from its interior, so Earth's Greenland halves under the warm-orbit rule"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: lane75
blocked_by: []
relates: [PW-1142, PW-464, PW-1115]
refs: [planet/tectonics/earth.py, planet/icemass.py]
---

## Description
In plain words. To stop worlds freezing over, the run now makes an ice sheet prove it can survive the warmest
part of each ice-age cycle (PW-1142, the "kitchen sink"). It works: no frozen-over worlds on the screen. But it
shrinks Earth's Greenland from 165 map cells to about 68. The reason is that the model's ice sheets don't flow.
A real sheet's edges melt hard in a warm spell, but ice keeps flowing out from the thick middle to replace it,
and the edges grow back when the cold returns. In the model each patch of ice has to survive on its own, so the
edges vanish and can't come back. Restoring Greenland should come from adding flow, not from loosening the
warm-orbit rule. Owner: is a minimal flow scheme worth doing for v1?

Evidence (lane 75, Earth L6 staircase from real ice, Greenland iced cells at dT 0):
- main 165; kitchen sink (lapse + warm persistence + bare absorb) 67-68; seasonal lapse alone 150.
- A time-weighted test that thins each cell by its warm-phase extra melt over a quarter precession cycle
  (5.75 kyr) gives 83, and a full warm-then-cold cycle gives 85. So the weighting isn't the problem; the missing
  resupply is (scratch l75/optionC.patch, l75/stair.py, l75/grthin.py).
- Per cell at dT 0: the interior thins only 30-80 m (NEEM: 400 +- 250 m over the Eemian, NEEM community 2013,
  Nature 493: 489). The margins thin 1.4-7 km (warm-state excess 0.24-1.2 m/yr). 96 of 133 cells survive, and
  the time-mean pass can only rebuild ~83 from that seed. Main's 165 are held by the old ice's own height.
- Caveat: Greenland really is fragile. Schaefer et al. 2016 (Nature 540: 252) find it was nearly ice-free for
  extended Pleistocene spells. So ~68 cells isn't absurd, just smaller than today's.
- Earth's present land ice under the kitchen sink is 8.6% (real 10.7%), still plausible. Antarctica is
  unchanged (792-802 cells, interior and summer as main).

Options:
- Minimal draw-down (effort m, ~1-2 days): in the warm-phase test, count each sheet's mass budget as a whole.
  The sheet loses the summed extra melt x the phase length, spread as a lowering of its Nye surface, and its
  margin retreats only by the volume-equivalent. That's derived from the existing profile with no new constant.
- Shallow-ice flow (effort l): a real SIA diffusion step on the run's sheets. It costs run time (PW-464's 2x
  budget) and touches every ice test.
- Accept for v1 and move it to v2.
- [ ] Owner: draw-down for v1, SIA later, or accept
