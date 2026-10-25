---
id: PW-839
title: Highlight number labels over the ocean get a wrong background when 3D Relief is on
type: task
status: done
parent: null
milestone: v2
subsystem: viewer
effort: xs
impact: low
found_by: owner-feedback-2026-10-25
blocked_by: []
relates: []
refs: []
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner feedback 2026-10-25 (feedback doc on world 2a7385): Owner saw it on 2a7385; cause being checked.

## Updates
- 2026-10-25: Status todo -> done. Merged fun lane 24 (de83743).
- 2026-10-25: fun-lane-24: textSprite and wideSprite materials get depthWrite false, alphaTest 0.05 and renderOrder 5 (after the 3D relief's translucent sea at 1). Checked on world 2a7385 in 3D relief with highlights: number labels over the sea are drawn.
- 2026-10-25: Diagnosis (untested): label sprites write depth over their whole quad and draw before the translucent relief sea (relief.js:133-138, renderOrder 1), so the sea fails the depth test there. Fix: depthWrite false or alphaTest, or a higher renderOrder.
- 2026-10-25: Created.
