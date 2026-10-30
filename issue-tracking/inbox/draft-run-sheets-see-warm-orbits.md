---
title: "The run's ice sheets never feel the warm orbital phases that end real ice ages, so they outlast the climate that made them"
type: task
status: needs-decision
parent: null
milestone: null
subsystem: climate
effort: l
impact: high
found_by: lane67
blocked_by: []
relates: [PW-470, PW-464, PW-471, PW-1091, PW-1115, PW-434]
refs: [planet/tectonics/earth.py, planet/icemass.py, tools/ice_probe.py, planet/timezoom/cycle.py]
---

## Description
In plain words. Real ice ages end because every ~100,000 years the planet's orbit gives the northern summers
extra sunshine, and the big sheets melt away within about 10,000 years. The long-run simulation can't step through
those orbits. Instead it grows each ice sheet to the size it would have under the average of all the orbits. A
sheet that has grown huge keeps itself cold: it is high, bright and makes its own cold air. Under average sunshine
it never gets the strong summer that would start it melting. So once the run makes a big sheet, the sheet stays
far longer than the climate that made it, and the world can stay "frozen over" (40%+ of its land under ice) while
its temperature is back near Earth's.

Evidence (lane 67, 2026-10-30):
- Earth on main, the ice rule walked down and back up in dT (tools/ice_probe.py --stair, 4 climate updates a
  step). Land under ice, going down: 10.0% at 0, 14.9% at -4, 20.5% at -6, 27.6% at -8. Coming back up: 26.8% at
  -4, 23.1% at -2, 15.3% at 0. Real Earth went from about 25% of land at the Last Glacial Maximum to about 11%
  today, with about 6 C of warming (orbits helping).
- With the sheets' own cold air turned off (probe only), the gap between the two legs shrinks by 20-50%. Most of
  the rest is the sheet's height keeping its own surface cold.
- Generated worlds (coasts judge, D arm, L6): seed 957317 held 36-41% of its land under ice from dT -5 up to
  dT +3.75 for ~60 Myr. It only let go when CO2 reached ~5500 ppm and the planet overshot to +10 C.

The physics idea. Let a sheet's height count toward keeping itself only where the sheet would survive the warm
phase of its own orbital cycle, the same cycle the time zoom already scripts (PW-471, cycle.py). In the warm
phase the margins would retreat, and a sheet that can only live at the cycle's cold end would shrink to what it
holds through the warm one. This is the "run ice as a cycle average" work (PW-464) in the parked ice-age epic
(PW-470).

Options:
- A. Build it now as a v1 soundness fix. It is the root of the persistence, but it is v2-scale work (effort l),
  and it touches the parked epic.
- B. Keep it parked in PW-470. For v1, fix the measured surface-climate cause first (PW-1115, Greenland too cold
  in every season), which may narrow the gap, and use the Earth staircase's up-leg as the plausibility check.
- C. Do both: B first, then A if the frozen-over rate on main stays well above the ~70% pass bar's tolerance.

Lean: B, then judge. Option A changes how every run's ice behaves, so it needs the owner.
- [ ] Owner: A, B or C
