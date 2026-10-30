---
id: PW-1032
title: Neighbouring peoples share a colour on the map (66 lines, 35 colours; kobolds and dragonborn both brown on the same continent)
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: s
impact: high
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-1023]
refs: [planet/lineages/history/params.py, planet/lineages/output.py, "run 3097e3", docs/review/code-audit-2026-10/img/, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-30
---

## Description
In plain words. On the peoples map, different peoples are often painted the same colour, so two neighbours look like one people. In the D&D run, kobolds and dragonborn are the identical brown and live side by side on Hizam; leonin and firbolgs share a navy that also vanishes against the dark ocean; humans and the sky-giants share grey. Dragon colours don't match their names either (green dragons are tan).

Verified on main b36c9581: `history/params.py PALETTE` has 27 colours; `output.py:73` assigns `PALETTE[used % len(PALETTE)]`, so colours repeat after 27 regardless of who lives next to whom. The viewer-ux audit counted 27 shared pairs in run 3097e3.

Fix: assign colours at save time so peoples whose ranges touch or overlap never share one (the run has the overlap data); give each family a hue (dragons reds, chromatic ones named by their own colour; giants blues; fey violets) and tell siblings apart by lightness; drop the near-black colours. Old runs keep old colours until re-run.
- [ ] no two touching peoples share a colour in a re-run of the D&D preset
- [ ] before/after screenshot for the owner

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-30: Status needs-decision -> todo. Owner 10-30 D1: family hues become the default; don't sweat individual dragon colours.
- 2026-10-29: Created from inbox draft draft-peoples-distinct-colours.md (found by code-audit-2026-10).
- 2026-10-30: lane 53: three palettes built behind ?palette=distinct or ?palette=family (viewer/globe/palettes.js, planetViewer.paletteReport()). On 3097e3 current has 4 same-colour neighbour pairs, 37 look-alike under colour-blind sight and 7 colours lost in the ocean or grey; both new options 0. Side-by-sides and colour-blind views in docs/review/viewer-ux-sides/. Lean: family hues + distinct neighbours (black dragons come out dark rose). Needs the owner's pick before it becomes the default.
