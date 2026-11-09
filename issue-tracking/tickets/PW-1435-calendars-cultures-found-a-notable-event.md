---
id: PW-1435
title: "Calendars cultures found: a notable event can start a count that spreads or fades"
type: task
status: done
parent: null
milestone: v4
subsystem: culture
effort: m
impact: med
found_by: coordinator
blocked_by: []
relates: []
refs: []
created: 2026-11-03
updated: 2026-11-09
---

## Description
In plain words: a culture living through a notable event (a faith or state founded, an invasion, a great flood) may start a count ('year 212 of the Forge'); it spreads with the state or faith and can fade; readouts can show a date in a chosen culture's calendar; 'X years ago' stays the default. Owner 11-03. Plan: docs/review/board/milestones-v2-v5.md.

## Updates
- 2026-11-09: Status todo -> done. Lane 255: planet/lineages/calendars.py (odds and sources in the docstring), GET /api/calendars, the brief's &calendar=, years.in_calendar, and NumFmt.setCalendar plus the workbench's 'dates in' picker. The Cultures tab has a calendars column; click one to use it. Stored L7 runs, current code: a24559 78 calendars (10 in use), 1e97dd 308 (45), 07c755 206 (51). Mostly from states; few faiths are founded after writing. Sources: Wikipedia 'Calendar era', 'Islamic calendar', 'Chinese era name'. The odds are judgement calls. Draft: how many counts a world should have (needs-decision).
- 2026-11-03: Created.
