---
title: The regional zoom page's layer list is still a flat block with its own names; give it the globe's grouped picker once PW-1026 is decided
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: m
impact: med
found_by: viewer-lane-56
blocked_by: [PW-1026]
relates: [PW-1026]
refs: [viewer/zoom.html, viewer/globe/layerpick.js, viewer/globe/layers.js, docs/review/viewer-ux-sides-2/index.html]
---

## Description
In plain words. The globe now has a grouped "Colour by" picker (a search box, the last few layers used, folding sections) behind `?picker=grouped`, waiting on the owner's choice in PW-1026. The regional zoom page has its own list of 46 layers, in a flat block, with different names for the same things (Height and elevation, Rain and precipitation, Title Case and lower case). If the owner picks the grouped picker, the zoom page should get the same sections and the same names.

Where: `viewer/zoom.html` `#layerSeg` and its own layer list. The globe's picker is `viewer/globe/layerpick.js` (an ES module reading `SECTIONS` and the layer `group` field in `viewer/globe/layers.js`); zoom.html is a classic inline script, so either it loads the module for the picker part or the zoom's layers get a small table of their own sections.
- [ ] the zoom page uses the same sections, search and recent row as the globe
- [ ] a layer shown on both pages has the same name on both
- [ ] `?layer=` links on the zoom page keep working
