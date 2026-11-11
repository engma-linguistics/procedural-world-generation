---
title: "Flavour and keeping read only the culture's own land: bought-in salt, spice and sugar never reach the profile"
type: task
status: todo
parent: null
milestone: null
subsystem: food
effort: s
impact: med
found_by: lane308
blocked_by: []
relates: []
refs: [planet/lineages/keeping.py::inputs, planet/lineages/keeping.py::flavour, planet/lineages/bought_in.py, planet/lineages/cuisine.py::sheet, planet/lineages/brief.py::_salt, docs/review/food/flavour-preservation.md, "runs a2b637, de1cc6 (copies in a scratch dir, since deleted)"]
---

## Description
In plain words: the salty axis and the salting share come from the culture's own salt reach (brief.salt: share of its land within 100 km
of salt). The hot and sweet axes come from crops grown on its own land. The exchange already knows what a culture buys in (bought_in.py:
the sheet's "Bought in" line, salt and spices among the goods). The flavour profile ignores it. An inland town that buys salt every year
still reads "salty: low, because salt far and dear", and a culture that imports pepper reads "hot: none". The profile then contradicts
the "Bought in" line two rows above it on the same sheet.

Try: in keeping.inputs, raise salt reach by the bought-in salt (with a "bought in from X" reason), and add bought-in spice, sugar and oil to
the hot, sweet and fatty axes at a lower weight than home-grown, inside the exchange's window (the last ~12.5 kyr).
- [ ] a culture whose "Bought in" line lists salt or spice shows it in the flavour reasons
