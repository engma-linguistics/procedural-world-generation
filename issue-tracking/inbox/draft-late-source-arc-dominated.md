---
title: "Late runs read cold because the CO2 source is ~92% arcs and its reference is learnt in the start's fast-plate years: rebalance the source or learn the reference later?"
type: task
status: needs-decision
parent: null
milestone: later
subsystem: tectonics
effort: m
impact: med
found_by: lane271
blocked_by: []
relates: [PW-1158, PW-969, PW-895, PW-830, PW-1224]
refs: ["planet/tectonics/earth.py::global_temperature", "planet/tectonics/earth.py::references", "planet/tectonics/earth.py::YARDSTICK", "planet/tectonics/crust.py::arc_growth", "planet/tectonics/events.py::strength", "planet/tectonics/diag.py::Recorder.temperature", tools/ice_diag.py, tools/yardstick.py, docs/review/v1-cut/co2-crash-diagnosis.md, docs/review/tectonics/margin/note-arc-co2.md, docs/overview.md, "Marty & Tolstikhin 1998 (ridge and arc C fluxes)", "Brune et al. 2017 (continental rift CO2)"]
---

## Description
In plain words: the planet's volcanic CO2 comes almost entirely (about 92%) from volcanic arcs, which in the model
scale with how fast plates sink and how long the trenches are. When continents crash together late in a run, trenches
close and plates slow, so the CO2 supply can fall 2-3 times within ~50 Myr, and the planet stays cold to the end
(PW-1158: one world at 0.57 of its usual supply over 850-1000 Myr). On Earth the supply is spread over several
sources that do not all switch off together: mid-ocean ridges (about as much as arcs), plumes, and the metamorphic and
rift degassing of continents. Should the model give ridges and continental degassing a larger, Earth-like share, so an
assembly cuts the supply less?

Lane 271's diagnosis of PW-1158 (cheap, before any sweep): candidate causes of the low late source.
1. Mantle heat cooling: ruled out. heat_start is 1.0, heat() is 1.000 throughout (co2-crash-diagnosis.md).
2. The drift: ~0.89x of the 0.57 (PW-1158's own numbers); a minor part.
3. A reference biased high by the made-up start (learnt 0-300 Myr, when stress rifts are 2-3x as frequent as later,
   overview.md sea-level notes): it shifts every run's late source down a little (control median ln src -0.08 over
   300-990), not the tail.
4. Slab flux: the arc term follows summed trench convergence (r 0.94) and trench length (0.89); ridges move with it
   (ln r 0.92) because both follow plate speed. In the crash world the late fall split ~equally between trench length
   and convergence rate, at sutures that welded the largest continent (co2-crash-diagnosis.md section 1).
5. The source's composition: arcs 91.8%, ridges 6.1%, plumes 2.0% (same note). Earth's are roughly ridges ~ arcs
   (Marty & Tolstikhin 1998), plus continental rifts (Brune et al. 2017). A source this arc-heavy has no part that
   keeps going when trenches close.
Measured (lane 271, L6 1 Gyr, tools/ice_diag.py --tect on the branch with PW-1637's true areas, diag fields
ridge_src / arc_src / plume_src; scratch runs, deleted after reading). Medians per 100 Myr; the source against its
reference, plate count, largest landmass % of the surface, mean plate speed cm/yr:

| seed | 200-300 | 400-500 | 600-700 | 700-800 | 800-900 | 900-1000 |
|---|---|---|---|---|---|---|
| 819014 src | 1.21 | 0.71 | 0.94 | 0.68 | 0.69 | 0.69 |
| 819014 plates / largest / speed | 12.5 / 25.2 / 4.65 | 14 / 11.5 / 4.00 | 17 / 11.3 / 3.51 | 13 / 20.4 / 2.75 | 13 / 13.5 / 3.08 | 15 / 16.5 / 3.19 |
| 1 src | 1.31 | 0.77 | 0.96 | 0.83 | 0.93 | 0.96 |
| 1 plates / largest / speed | 16.5 / 25.4 / 4.40 | 18 / 25.3 / 3.81 | 17 / 12.6 / 3.64 | 14.5 / 10.2 / 3.33 | 14 / 11.3 / 3.67 | 16 / 12.0 / 3.04 |

The shares do not move: arcs 90.5-92.8%, ridges 5.9-7.3%, plumes 0.8-3.1% in every bin of both runs. On main's code
819014 (no l6c_p arm) again runs low late (0.68-0.69 over 700-1000, dT -3.9 over 900-1000) against seed 1's 0.83-0.96.
Its lowest bin is its slowest (700-800, 2.75 cm/yr, largest landmass 20.4%); the plate count does not track it. On
both seeds the mean plate speed falls ~35% from the reference years (200-300 Myr, when the source peaks at 1.2-1.3) to
the end, with mantle heat fixed at 1: so the reference is learnt in the start's fast-plate years, and a late slowdown
reads as a cold era. That is cause 3 measured, and the main driver of the tail; cause 5 sets how hard each trench
closure bites on top of it.

Causes 3, 4 and 5 together make the tail; 4 is tectonics (PW-969's welded giant plates make it worse), 5 is the carbon
model's choice of weights (`20.0 x growth` against 1 per new floor cell).

What breaks if never done: ~1 in 5-10 L6 worlds spends its last few hundred Myr deeply cold (frozen-over worlds in lane
67's draws), and every late supercontinent reads as an ice age by construction, a pattern the history and peoples
layers inherit.

The trade-off (why this is a decision, not a slam dunk):
- A (smallest): raise the ridge's yield so ridges are ~40-50% of the source (one constant), re-fit YARDSTICK
  (tools/yardstick.py on the paired judge's draws). Damps trench-closure drops by about half; plate-speed drops stay.
  Moves every run's history, needs the paired judge.
- B: add a continental degassing term (collisional metamorphism at young sutures + rifts), which rises when
  continents collide, a real buffer against assembly cooling; more code, new constants with thin sources.
- C: leave it: the direction is real Earth behaviour (low outgassing with assemblies and ice ages); only the size is
  in question, and the hard bar holds on the current judge.
- D: learn the source's reference later or longer (e.g. over 300-600 Myr instead of 0-300), out of the start's
  fast-plate years; one constant, but it moves YARDSTICK's fit and every run's mid-history.
Lane 271's lean: D addresses the measured driver (the plates' slowdown against a fast-years reference); A only damps
the trench closures. Neither is a clamp; both need the paired judge on the two-tier bar (hard failures 100%, soft
~60-70%).
- [ ] decision taken; if A or B, the share of the source from arcs over 300-1000 Myr on 6+ L6 seeds is <= ~60% and
      the frozen-over count on the paired judge does not rise
