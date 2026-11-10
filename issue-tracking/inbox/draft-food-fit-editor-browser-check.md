---
title: "Peoples editor: open the new food-fit field, alcohol flush select and grapes toxin in a browser"
type: task
status: todo
parent: PW-856
milestone: later
subsystem: viewer
effort: xs
impact: low
found_by: lane264
blocked_by: []
relates: [PW-1607]
refs: [viewer/lineages.html, "planet/lineages/spec.py::parse_fit", "planet/lineages/food_fit.py::fit", docs/review/food/lane264.md]
---

## Description
In plain words: lane 264 added a text field ("alcohol=poor, grapes=harmful") for a people's hand-set food fit, a select for the alcohol flush share, and a
"grapes and raisins" check box to the Peoples editor's body section. The lane had no browser, so the page script was only syntax-checked
with node and the server side tested (tests/test_viewer.py, test_food_fit.py). What misleads if never done: a typo in the new handler
would silently drop an owner's edit (a bad level word is ignored by design, a broken handler would lose the whole body edit).
- [ ] open lineages.html on a tree, set a fit, a flush share and the canid toxin on one line, save, reload, and check the child line inherits the fit table and the saved TOML parses
