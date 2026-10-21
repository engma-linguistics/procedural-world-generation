---
id: PW-489
title: Fine zoom reef area is ~60% of the parent's (patches and bands drawn inside the parent's reef pixels)
type: task
status: needs-decision
parent: null
subsystem: zoom
effort: s
impact: low
found_by: pw392-fine-forms
blocked_by: []
relates: [PW-392]
refs: [planet/zoom_fine_forms.py, "zoom a0097b in 3ac681"]
created: 2026-10-20
updated: 2026-10-20
---

## Description
After PW-392 a0097b has 327 km2 of coral reef against the parent 3ac681's 535 in the same area (485 before, when the parent's blocks were copied), the 50 m zoom 652295 181 vs its parent's 180. The fine zoom places reefs with zoom_coastal.place on its own shelf (fringing and barrier bands, patches, the 6 km noise) and keeps them where the parent's habitat is (bilinear >= 0.25), so the shelf geometry and the `taken` budget at 100 m give fewer reef pixels than 1 km blocks that were drawn whole. Options: (a) leave it (a reef pixel at 1 km is "some reef in this km"; the fine drawing is the better statement of it); (b) scale each parent pixel's fine reef share to the parent's cover, adding patch pixels by the noise order inside parent reef pixels. Lean (a); it is a judgement on whether the parent's cover is a share or presence.
- [ ] decide (a) or (b)

## Updates
- 2026-10-20: Created from inbox draft draft-fine-zoom-reef-share-below-parent.md (found by pw392-fine-forms).
