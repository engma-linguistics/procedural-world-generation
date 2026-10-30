---
title: "Viewer: five 'kyr / Myr ago' formatters round differently; pick one and share it"
type: task
status: todo
parent: null
subsystem: viewer
effort: xs
impact: low
found_by: viewer-lane-51
blocked_by: []
relates: [PW-1046]
refs: [viewer/globe/colours.js, viewer/globe/timezoom.js, viewer/globe/panel.js, viewer/techtab.js, viewer/lineages.html]
---

## Description
In plain words. The same kind of date is written in slightly different ways on different parts of the viewer. For example, "1.25 Myr ago" in one place and "1.3 Myr" in another, or "12.5 kyr" next to "13 kyr". Each panel has its own small copy of the formatting code. I didn't merge them during the module split, because merging them changes text you can see.

There are five copies:
- `globe/colours.js` `techAgoText`: 2 decimals, years below 1 kyr.
- The local `fmt` at colours.js ~707: 1 decimal, "yr".
- `globe/timezoom.js` `agoLabel`.
- `techtab.js` `fmt`, which says it copies lineages.html.
- The copy in `lineages.html` itself.

Fix:
- Put one `agoText(kyr, {fine})` in viewer/util.js. `fine` gives the 2-decimal form the technology rows need, for events a few years apart.
- Use it everywhere.
- Accept the small text changes.
- Lean: 1 decimal by default, 2 when fine.

- [ ] one formatter, every copy removed
