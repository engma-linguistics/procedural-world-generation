---
title: "The CO2 source is ~92% arcs, so every late assembly that closes trenches cools the planet hard: give ridges and continental degassing their Earth share?"
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
Causes 4 and 5 together make the tail; 4 is tectonics (PW-969's welded giant plates make it worse), 5 is the carbon
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
Lane 271 recommends A if anything, judged on the two-tier bar (hard failures 100%, soft ~60-70%).
- [ ] decision taken; if A or B, the share of the source from arcs over 300-1000 Myr on 6+ L6 seeds is <= ~60% and
      the frozen-over count on the paired judge does not rise
