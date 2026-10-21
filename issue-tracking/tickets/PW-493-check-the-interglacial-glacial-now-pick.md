---
id: PW-493
title: Check the interglacial / glacial "now" pick on real L6 time zooms (and offer a kyr in the form)
type: task
status: done
parent: PW-244
milestone: v1
subsystem: timezoom
effort: xs
impact: low
found_by: pw479
blocked_by: []
relates: [PW-479, PW-471]
refs: [planet/finish.py, viewer/start.js]
created: 2026-10-20
updated: 2026-10-21
---

## Description
`finish.now_kyr` (PW-479) is tested on synthetic glacial-index series and on a tiny L4 zoom, not on a real 300 kyr L6 zoom, where one cycle of ~100 kyr means a default `make` often has only 2-3 cycles and sometimes none complete (then `interglacial` falls back to the end and says so).
- [ ] On an Earth L6 600 kyr zoom (showcase 6d0ed0) and two run-moment zooms, run `planet finish <tz> --now interglacial` and `--now glacial`; check the frames picked look right (sea level highest/lowest of their stretch).
- [ ] If the 300 kyr default too often lacks a full cycle, consider a default `kyr` of 400-500 for `make`.
- [ ] The New planet form has no "specific kyr" choice (CLI and API do); add one if wanted.

## Updates
- 2026-10-21: Status todo -> done. 2026-10-21: now-pick checked on the three time zooms in the store (F.now_kyr via F.load_timezoom). e9d59c (600 kyr): interglacial 512 kyr (frame 256, I 0.00, sea -16.5 m); glacial 594 kyr (frame 297, I 0.89, sea -115.4 m, the zoom's sea-level low); end 600 kyr (I 0.91). ae8f75 (300 kyr): interglacial 300 kyr (frame 150, I 0.00, +19.4 m); glacial 266 kyr (frame 133, I 0.76, +19.9 m); end 300 kyr (I 0.00). 7ec3fe is frame-identical to ae8f75 (see draft-duplicate-timezoom-7ec3fe.md). Index check: every pick lands on the matching index (low for interglacial, high for glacial) on all three. Sea-level check: passes on e9d59c. On ae8f75/7ec3fe the sea level does not follow the ice (correlation 0.01, sea 0 to +33 m through 0-0.95 ice index), so the glacial pick is only 0.5 m below the interglacial one: the pick rule is right, the zoom has no sea-level response; filed as draft-timezoom-sealevel-decoupled-300kyr.md. 300 kyr default: both 300 kyr zooms have several full index cycles, so the default stays at 300 kyr. Form: added a kyr number input (#fNowKyr) beside the 'now' choice in viewer/start.js; the three named picks stay as presets; the server checks 0..kyr. Checked with node --check only, not in a browser.
- 2026-10-20: Coordinator checked on Earth zoom 6d0ed0 (600 kyr): interglacial -> 512 kyr (index 0.00, -14 m), glacial -> 594 kyr (index 0.89, -104 m), end -> 600. The pick works on a real zoom; left open only for the form's kyr choice and a 300 kyr check.
- 2026-10-20: Created from inbox draft draft-now-pick-real-zoom-check.md (found by pw479).
