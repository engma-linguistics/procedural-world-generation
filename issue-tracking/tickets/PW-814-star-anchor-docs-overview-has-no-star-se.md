---
id: PW-814
title: "Star anchor docs: overview has no star section; the params comment, PW-789's help text, make.py UNSUPPORTED and coordination.md describe the old from-start star"
type: task
status: done
parent: PW-244
milestone: v1
subsystem: docs
effort: xs
impact: low
found_by: star-anchor-audit
blocked_by: []
relates: [PW-791, PW-789]
refs: [docs/overview.md, planet/tectonics/params.py, planet/make.py, docs/coordination.md, docs/review/base-climate/star-anchor-audit/]
created: 2026-10-24
updated: 2026-10-31
---

## Description
Audit item 14 (docs/review/base-climate/star-anchor-audit/README.md). Fix these when the anchor lands:
- docs/overview.md's climate section has no star at all. Add a short subsection: the anchor, the rate, and what the
  thermostat passes.
- The planet/tectonics/params.py:81-86 comment says "counted against the run's start" and "a Sun-like 1.0 warms 1 Gyr
  runs ice-free".
- PW-789's proposed form help text says "1.0 ... melts out all ice within ~1 Gyr".
- planet/make.py:88 lists "star brightness" as UNSUPPORTED.
- docs/coordination.md:60 notes the hothouse change "5 before the brightening star".
- [ ] all five updated to the anchored semantics

## Updates
- 2026-10-31: Done (lane 88, docs). Overview §2.6 now has "The star": the Gough curve, the end-of-run anchor (a run spans ages 4570 - T to 4570 Myr; -8% at 1 Gyr, -15% at 2 Gyr), `star_brightening` (default 1) and `star_now_offset_myr`, `check_star`, what the carbon cycle does with the faint start (`start_carbon`, high CO2), and the opt-in star thermostat (off in the presets, PW-865). The params.py comment already described the anchor (already fixed; checked, no change). make.py UNSUPPORTED now says "a different star (always Sun-like, and the run ends at today's Sun)". docs/coordination.md's hothouse row no longer calls the star brightening from the start. PW-789's proposed help text was never built (the ticket is wontdo, so left as written); nothing in code or docs still says "melts out all ice within ~1 Gyr". The form still does not offer the star (CLI `--set star_brightening=`).
- 2026-10-24: Created from inbox draft draft-star-docs-after-anchor.md (found by star-anchor-audit).
