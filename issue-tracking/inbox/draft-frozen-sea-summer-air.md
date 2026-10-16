---
title: "Climate: summer air over a frozen sea is +4 C (land's carry) or -12 C (the sea's own); melting ice holds it near 0 C"
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: med
found_by: pw313
blocked_by: []
relates: [PW-112, PW-313, PW-013]
refs: [planet/climate.py, planet/ocean.py, docs/review/audit/pw313-polar-summers.md]
---

## Description
In `climate._air_temps` the summer air over a sea has two inconsistent definitions, and neither is right for a
frozen sea. The land's carry uses `sst + sea_half` (sst floored at -1.8), so pack ice gives +4 C summer air at 80
deg. The sea cells' own `t_warm` is `sst + sea_half + 3 x frozen`, which gives -11 to -12 C over 75-90N against
NCEP's +0.8. A melting surface holds the summer air near 0 C.

Fix (measured on main 6392e18, not merged): both become `max(sst + frozen + sea_half, FREEZE)`, with
`frozen = min(t_sea_air - t_sea, 0)`. That is the seasonal sea surface `ocean.open_share` already uses. Earth's
ice-free coastal land then matches NCEP's warmest month within 1 C at every band from 70 to 85N: 75-80N +4.4 ->
+1.9 (obs +1.3), 80-85N +3.4 -> +0.4 (-0.6). The 60-70N coasts are unchanged, and the Arctic Ocean's air comes
to +0.3..-1.3 (obs +0.8). earth_check: land T 80-90N -19.2 -> -20.5 (obs -21.0), 70-80N -17.8 -> -18.3 (-16.4).
Köppen moves ≤ 1 point.

Why not merged alone: it dries the poles. Warmer, right summer air over the polar seas condenses less vapour
onto the coasts: land rain 80-90N 139 -> 108 mm (GPCC 168), Antarctica 70-80S 200 -> 193 (GPCP 412), and at
dT -6 Antarctica 66 -> 55 mm, Greenland 212 -> 192. The PW-313 probe's dT -6 ice falls from -44 to -30 m. The
old -12 C polar sea air was wringing out vapour that the real ~0 C air keeps, so it hid part of the polar dryness.
Land it with the polar snowfall fix (PW-013, draft-antarctic-margin-snowfall), not before.
- [ ] Earth's ice-free 70-85N coasts within ~1 C of NCEP's warmest month; Arctic Ocean summer air ~0 C
- [ ] landed together with the polar snowfall fix, with the PW-313 probe re-run
