---
title: "Star anchor docs: overview has no star section; the params comment, PW-789's help text, make.py UNSUPPORTED and coordination.md describe the old from-start star"
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: docs
effort: xs
impact: low
found_by: star-anchor-audit
blocked_by: []
relates: [PW-791, PW-789]
refs: [docs/overview.md, planet/tectonics/params.py, planet/make.py, docs/coordination.md, docs/review/base-climate/star-anchor-audit/]
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
