---
id: PW-156
title: "Weather generator: days-scale animated weather (clouds, storms, hurricanes) consistent with a world's climate"
type: epic
status: todo
parent: null
subsystem: climate
effort: l
impact: med
found_by: daniel
blocked_by: []
relates: [PW-103, PW-143]
refs: []
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner (2026-10-14): watch a year or five of cloud cover move, see where hurricanes form and track. Not a weather-forecast model: a stochastic weather generator whose statistics reproduce the world's stored climate (the approach catastrophe modellers use for synthetic storm tracks). Pieces: (1) daily seasonal cycle interpolated from the July/January fields; (2) extratropical lows and highs spawned in baroclinic zones (strong temperature gradients under the jet) and steered along the storm tracks at jet-derived speeds, carrying cloud and rain; (3) tropical cyclones spawned where SST > ~26.5 C, > ~5 deg from the equator, low wind shear, in the warm season; tracks steered by the trade winds then recurving into the westerlies, decaying over land or cool water, intensity from the SST (potential intensity); (4) cloud and rain fields = climatology + the storms' anomalies, advected by the winds, with noise; (5) a viewer animation (play / scrub days) and track overlays, plus per-world stats (storms per year, hurricane-prone coasts) for highlights and games. Must stay cheap: computed on demand for a chosen world and span (1-5 years), seconds to a minute at L6/L7. Fits PW-103's finest phase (centuries down to days).

## Updates
- 2026-10-14: Created.
