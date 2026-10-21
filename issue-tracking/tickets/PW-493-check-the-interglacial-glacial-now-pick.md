---
id: PW-493
title: Check the interglacial / glacial "now" pick on real L6 time zooms (and offer a kyr in the form)
type: task
status: todo
parent: PW-244
subsystem: timezoom
effort: xs
impact: low
found_by: pw479
blocked_by: []
relates: [PW-479, PW-471]
refs: [planet/finish.py, viewer/start.js]
created: 2026-10-20
updated: 2026-10-20
---

## Description
`finish.now_kyr` (PW-479) is tested on synthetic glacial-index series and on a tiny L4 zoom, not on a real 300 kyr L6 zoom, where one cycle of ~100 kyr means a default `make` often has only 2-3 cycles and sometimes none complete (then `interglacial` falls back to the end and says so).
- [ ] On an Earth L6 600 kyr zoom (showcase 6d0ed0) and two run-moment zooms, run `planet finish <tz> --now interglacial` and `--now glacial`; check the frames picked look right (sea level highest/lowest of their stretch).
- [ ] If the 300 kyr default too often lacks a full cycle, consider a default `kyr` of 400-500 for `make`.
- [ ] The New planet form has no "specific kyr" choice (CLI and API do); add one if wanted.

## Updates
- 2026-10-20: Created from inbox draft draft-now-pick-real-zoom-check.md (found by pw479).
