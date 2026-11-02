---
id: PW-1384
title: "The CO2 references are learnt over 0-300 Myr, a stretch unlike the rest of a run: bare land (sink x0.5), the start's breakup lull (source x0.78), the faint star"
type: task
status: needs-decision
parent: null
milestone: null
subsystem: climate
effort: m
impact: med
found_by: lane135
blocked_by: []
relates: [PW-1316, PW-1163, PW-1158, PW-576, PW-809, PW-798, PW-612, PW-969]
refs: [docs/review/tectonics/co2-refs/round1.md, docs/review/tectonics/co2-refs/spinup.py, docs/review/tectonics/co2-refs/refpredict.py, docs/review/tectonics/co2-refs/envref.py, docs/review/tectonics/co2-refs/envsum.py, "planet/tectonics/earth.py::global_temperature", "planet/tectonics/earth.py::update_vegetation", "planet/tectonics/earth.py::start_carbon", docs/review/base-climate/thermostat.md, docs/review/base-climate/finish-drift-l80/README.md, docs/review/tectonics/margin/pw1295-note.md, docs/scorecard.jsonl]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: the planet's carbon balance is measured against yardsticks learnt in its first 300 Myr. Those 300 Myr
are not like the rest of the run. Before land plants (~506 Myr) the land weathers at half its later rate; the start's
supercontinent breaks up and the volcanic CO2 dips to ~0.8x around 100-200 Myr on nearly every world; the young star
is ~9 C dimmer. The yardsticks are built to look past some of this (the sink's is learnt as if the plants were already
there, at the balance climate), but each correction is a separate patch, and two leftovers are known: the sink's
reference learnt on bare-ground erosion (PW-1163, ~+1.6 C) and the late source decline against the 0-300 Myr source
(PW-1158, ~-1.6 C), which cancel today.

Numbers (lane 135, round1.md section 3; 72 L6 1 Gyr draws): source at 0-100 / 100-200 / 200-300 Myr is 1.08 / 0.78 /
1.09 of its 300-1000 Myr mean; the sink is 0.50 / 0.47 / 0.58 until plants, then x1.7 in one step; ln CO2 sits +1.4
to +0.8 e-folds above its late mean through 0-500 Myr. Of 32 past CO2 / climate-drift episodes surveyed, 10 trace to
the spin-up and 9 partly (round1.md 3b).

Options (diagnosis only; nothing built):
- A. Leave the spin-up as is after PW-1316. Each known bias has its own ticket (PW-1163, PW-1158).
- B. Learn the source's reference over the spin-up but the sink's over a planted window: keep learning the sink until
  plants have arrived and settled (e.g. to ~650 Myr, planet-relative: N Myr after vegetation.land_plants first holds),
  then freeze. Removes the bare-ground step from the sink's reference by construction (PW-1163's cause) instead of
  correcting it. Cost: the planet runs ~350 Myr more on a moving sink yardstick, which PW-576 found weakens the
  thermostat (~30% lost to relearning baselines); the judged window would start later.
- C. A longer spin-up for both (REF_FREEZE ~600 Myr). Simplest, but thermostat.md found judging after 500 Myr changes
  no verdict and halves the sample, and it moves PW-1158's yardstick too.
Lean: A now (see PW-1316's judge first); B is the mechanism-level version if PW-1163's fix by potential-cover learning
proves fiddly. Not C.
- [ ] Daniel picks A, B or C

## Updates
- 2026-11-02: Coordinator: brought to Daniel on the desk with the PW-1316 B result (lean A for now).
- 2026-11-02: Created from inbox draft draft-co2-references-spinup-unlike-the-run.md (found by lane135).
