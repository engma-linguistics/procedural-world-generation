---
id: PW-483
title: "The globe view is unusable at phone width: the control panel covers the globe and several panels are hidden"
type: task
status: todo
parent: PW-244
subsystem: viewer
effort: m
impact: low
found_by: agent-make-ui
blocked_by: []
relates: [PW-472, PW-473]
refs: [viewer/index.html]
created: 2026-10-20
updated: 2026-10-20
---

## Description
The new start screen and the New planet form work at 390 px wide (checked in headless Chrome), and the navigator bar moves below the tabs on narrow screens. The existing globe view does not: at 390 px the 220 px controls panel (which cannot be collapsed) covers over half the globe, the legend floats over it, and the info box and summary are hidden by a media query (`@media (max-width: 700px)`). A phone needs a collapsible controls drawer (a "Layers" button), the legend and summary as bottom sheets, and a time slider that fits. Not done here because it is a rewrite of the page's layout, not part of PW-472/473.

## Updates
- 2026-10-20: Created from inbox draft draft-viewer-phone-layout.md (found by agent-make-ui).
