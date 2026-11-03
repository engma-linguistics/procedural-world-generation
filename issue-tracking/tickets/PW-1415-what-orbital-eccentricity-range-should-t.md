---
id: PW-1415
title: What orbital eccentricity range should the generator draw for v0.2 Earth-likes? (PW-1365 result)
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: lane148
blocked_by: []
relates: [PW-1365, PW-443, PW-481, PW-555, PW-1325]
refs: [docs/review/climate/eccentricity/round1.md, docs/review/climate/eccentricity/runs_results.txt, docs/review/climate/eccentricity/worlds_results.jsonl, "planet/timezoom/params.py::TZParams", "planet/icemass.py::cycle_dq", "planet/finish.py::orbit_dt", "planet/climate.py::_orbit", tools/hard_bar.py, "Spiegel et al. 2010 ApJ 721 1308", "Dressing et al. 2010 ApJ 721 1295", "Way & Georgakarakos 2017 arXiv:1611.06133", "Laskar et al. 2011 A&A 532 A89"]
created: 2026-11-03
updated: 2026-11-03
---

## Description
**In plain words:** an orbit's eccentricity is how stretched it is. Earth's swings between almost 0 and about
0.06 over ~100,000-year cycles. Today every generated planet gets Earth's own cycle (0.002-0.052) in its ice-age
pass, and a fixed 0.03 in its long run. Lane 148 tested worlds from e = 0 to 0.4 (4 seeds of 1 Gyr runs, and
finished worlds on 2 seeds). Earth's range is safe on every measure. Around 0.1 the model itself starts to give
way: the run's ice ages vanish, and the seasons depend on the calendar. The planet only truly boils (hard bar)
at about 0.4. So the limit for now comes from the model, not from physics: real Earth-like planets stay
habitable to about 0.3 in the published climate models.

Measured (round1.md; every comparison against the same seed on today's code / at e = 0.017):
- **Summers.** With perihelion on the northern solstice, the share of ice-free land whose warmest month is
  >= 35 C, at 0.017 / 0.06 / 0.1 / 0.2:
  - a 14 C world: 0.1 / 1.8 / 4.5 / 18%;
  - a warm 19 C world: 2.6 / 7.1 / 12 / 26%. Half of its hot hemisphere is >= 35 C at 0.2.
  - The cold hemisphere's summers stop thawing: up to 3-4% of land at 0.2-0.4.
  - Biomes barely change.
- **Runs.** Today 3/4 soft passes; e = 0.06: 4/4 (with less ice-age time); e = 0.1: 1/4, and land ice is gone on
  every seed. That is the run's ice rule overshooting (0.25 C per W/m2, ~3x the seasonal response).
  - No hard failure up to 0.3 when the carbon cycle answers the extra sunlight.
  - At 0.4: boiled 4/4 and CO2 crash 3/4.
  - Never frozen over, never ocean loss.
- **Model limits above ~0.1.** The climate reads the orbit only in July and January. A perihelion at an equinox
  makes an e = 0.3 world *colder* in its warmest month (22.3 -> 15.9 C), although its yearly sunlight is 4.8%
  higher.
- **Physics.** Spiegel et al. 2010 (Sec. 1): Earth's e runs between almost 0 and ~0.06. Way & Georgakarakos 2017
  (Sec. 3): a coupled-ocean GCM with e up to 0.283 stays temperate (hottest cell 53.9 C). Dressing et al. 2010
  (Sec. 5.1): above ~0.3 habitability depends on the season.

Options:
- **A. Keep today's draw:** every planet gets Earth's cycle (mean 0.027, range 0.002-0.052). The run stays at
  0.03. No work. Every world has the same orbit statistics.
- **B. Per-planet mean within Earth's range:** draw each planet's mean eccentricity (e.g. uniform 0.005-0.04,
  keeping the cycle's swings, so the peak is <= ~0.07). Feed the same draw to the run's ice cycle, so a
  more-eccentric planet has shorter ice-age eras. Some planets get noticeably hotter one-hemisphere summers.
  Small work (the run part is in draft-run-ignores-orbit-eccentricity).
- **C. Allow up to ~0.1-0.15 for v0.2:** more variety (strong-season planets). It needs three fixes first: the run
  takes the draw, the run's ice rule uses the seasons' response (PW-555 stage 3), and the seasons read the
  orbit's own extreme months (draft-eccentric-orbit-two-point-seasons). Without them, those worlds lose their ice
  ages and get calendar-dependent seasons.
- **D. Strong-season worlds (0.1-0.3) as a post-v1 weird-world kind (PW-443)**, built on C's three fixes. Nothing
  above ~0.35 as an Earth-like: the hard bars fail there.

**My lean: B for v0.2, and D for anything above ~0.07.** B adds real variety where the model is sound. It
matches the physics (Earth's own range) and costs little. Going higher is physically fine, but the model would
show artefacts rather than physics. C's fixes are worth doing, but as part of the weird-worlds work. This is a
question about planet variety, so it is your call. The physics does not force either way below ~0.3.

## Updates
- 2026-11-03: Created from inbox draft draft-eccentricity-range-for-earthlikes.md (found by lane148).
