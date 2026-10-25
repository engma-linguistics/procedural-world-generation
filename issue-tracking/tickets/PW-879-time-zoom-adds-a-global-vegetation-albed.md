---
id: PW-879
title: Time zoom adds a global vegetation-albedo cooling on top of a glacial cooling sized on Earth's whole LGM cooling
type: task
status: todo
parent: null
milestone: null
subsystem: timezoom
effort: xs
impact: low
found_by: coupling-audit
blocked_by: []
relates: [PW-470, PW-471]
refs: [planet/timezoom/params.py, planet/timezoom/plants.py, docs/review/coupling-audit/]
created: 2026-10-25
updated: 2026-10-25
---

## Description
Coupling audit finding C6 (severity low for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**One side:** planet/timezoom/params.py glacial_cool 6.5 ("Earth's LGM 4.5-6 C"; the LGM total includes vegetation albedo, ~-1 W/m2, Kohler et al. 2010).

**Other side:** planet/timezoom/plants.py measure(): dT_target = veg_lambda x veg_toa x surface albedo change, added to dTg in forcing.py Forcing.update.

**Why they disagree:** The plants' darkening/brightening is in both the scripted cooling and the explicit term.

**Measured:** 8 L7 time zooms: the vegetation term reaches -0.09 to -0.61 C at glacial maxima, 3-7% of the zooms' coldest dTg (-2.3 to -9.6 C).

**What to try:** Either take ~5% off glacial_cool (say so in its comment) or keep the explicit term and note that glacial_cool excludes vegetation. Fold into the ice-age epic.

## Updates
- 2026-10-25: Created from inbox draft draft-timezoom-vegetation-albedo-on-top-of-lgm-cooling.md (found by coupling-audit).
