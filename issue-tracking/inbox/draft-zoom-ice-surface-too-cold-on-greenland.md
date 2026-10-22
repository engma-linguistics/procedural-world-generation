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
- [x] Greenland's margins within ~1.5 C of observed in the zoom's year, Antarctica not worse than +2 C (stage 1b, fetch)
- [ ] Earth zoom interglacial ice 9–12% of land at a cooling ≤ 6 C (tools/tz_earth.py)

Stage 1b (2026-10-22): `surface_air=fetch` (the local terms on the share of the air that has come over ice within
500 km, icemass.surface_share) takes Greenland's margins to −3.9 C (their ice part observed ~−2.7: the cell's
observed mean −2.1 includes its bare part), inland to −6.2 (obs −4.9), and Antarctica to +3.3 C too warm (from +4.9).
The first check is met. Earth's interglacial ice doesn't move (11.8–15.5%): the cause is the dT-0 floor
(draft-earth-zoom-does-not-hold-todays-ice-at-dt0), so the second check moves there.

Stage 1c (PW-555): against RACMO2.3p3's observed SMB (`tools/tz_earth.py --greenland`) the zoom's Greenland margin
cells are +0.21 m/yr vs -0.02 observed, its inland right (+0.28 vs +0.29), and the margin summers are 2-5 C below
the observed warm month on the north and east margins (81 N -4.6 vs -0.5 C; 77 N -5.2 vs -0.9; 73 N -8.1 vs -4.7),
~0-2.5 C in the southwest. The ramp's geometry matches RACMO's ice surface and its quadrature is exact enough, so
the margin's remaining surplus is its air: this ticket. The start anchor only cools, so it can't take this out on
Earth (and a two-sided anchor would hide a rule every planet has). It is what keeps Greenland's front advancing at dT 0.
