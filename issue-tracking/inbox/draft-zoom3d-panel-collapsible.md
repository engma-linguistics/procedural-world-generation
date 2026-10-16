---
title: "Zoom 3D panel: collapsible sections so short windows show the falls list without scrolling"
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: low
found_by: worktree-agent-a3947a9de2078ba52
blocked_by: []
relates: [PW-409]
refs: [viewer/zoom.html]
---

## Description
After PW-409 the zoom 3D view's right pane is one flex column: the 3D panel (`#p3d`: render controls, fly along a river, waterfalls list) above the hover card (`#info`), each scrolling inside its share, so nothing overlaps. On short windows (1366x768, especially embedded in the globe's Regional zoom tab, which starts the column 56 px down) the 3D panel's own content is ~500 px, so the Waterfalls list sits below its fold and needs a scroll inside the panel (zoom d7444e: the first fall shows, the rest scroll).

Optional polish: make the render controls (height, detail, sun, river width, the checkboxes) a `<details>` section like index.html's `details.sec` (open state remembered in localStorage), so folding it brings Fly and Waterfalls up. Not needed for correctness.
- [ ] 3D panel's render controls fold; the fold state is remembered
- [ ] at 1366x768 embedded, with the controls folded, the falls list and the hover card are both visible without scrolling
