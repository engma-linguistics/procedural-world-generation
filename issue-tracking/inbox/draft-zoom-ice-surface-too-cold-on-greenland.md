---
title: "Time zoom: the ice rule makes Greenland's surface summer ~4 C colder than observed (the local damping and ice_cool on top of the sheet's air)"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: ice-v2-stage1
blocked_by: []
relates: [PW-555, PW-439, PW-336, PW-039, PW-460]
refs: [planet/icemass.py, planet/timezoom/sim.py, docs/review/ice-v2/stage-1.md]
---

## Description
Earth L6 today, the zoom's year with no anchor (`grlprobe.py` in the stage-1 scratch): the climate's own
air over Greenland's ice has a warm month of −3.0 C (observed −4.2), but the ice-surface rule on top
(`ice_cool` 2 C, the local summer damping SUMMER_DAMP × LOCAL, MELT_HOLD) takes it to −8.6 C; margin cells
−7.1 vs −2.1 observed. Stage 1's `surface_air=rest` (the local terms only on the air that isn't the sheet's
carried air) brings margins to −6.1. Without the local terms Greenland matches (−3.2 / −2.0) but Antarctica's
interior goes +6 C too warm (base bias PW-039) and Earth's glacials go too shallow (−47 m). `anchor=obs`
only cools, so it never corrected Greenland. This cold bias is what keeps honest-margin sheets from
retreating (stage 1: the carried air is the measured cause; Earth interglacials keep 12–15% of land iced
against 9–12).
- [ ] Greenland's margins within ~1.5 C of observed in the zoom's year, Antarctica not worse than +2 C
- [ ] Earth zoom interglacial ice 9–12% of land at a cooling ≤ 6 C (tools/tz_earth.py)
