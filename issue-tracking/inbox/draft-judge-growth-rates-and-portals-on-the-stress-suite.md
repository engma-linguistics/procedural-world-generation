---
title: Judge growth rates and portals in force on the peoples stress suite
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: highlights
effort: s
impact: med
found_by: lane78
blocked_by: []
relates: [PW-1147, PW-1150, PW-1148]
refs: [planet/lineages/samples/dnd.toml, tools/peoples_robust.py]
---

## Description
Lane 78 turned on in dnd.toml:
- `growth_rates = true`;
- `portal_mode = "sites"`, `portals = 8`;
- elves `founders = 1e6` in 2 waves; gnomes 4e6.

It measured them only on world 4360a3 at L6, seed 7, 2 tries each (lane 78 report). Lane 77's stress suite (tools/peoples_robust.py) was not yet on main.
- [ ] run the suite with and without the two switches (meta growth_rates; portal_mode sites/off)
- [ ] if anything collapses (a people lost, stranding, a share blow-up), switch that part off in dnd.toml and say which
