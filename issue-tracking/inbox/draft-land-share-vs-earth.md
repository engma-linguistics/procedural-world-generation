---
title: "Land is ~34% of the surface (Earth 29%): lower the continental target or accept?"
type: task
status: needs-decision
parent: null
subsystem: tectonics
effort: s
impact: med
found_by: tectfound
blocked_by: []
relates: [PW-046, PW-052]
refs: [planet/tectonics/params.py, planet/tectonics/crust.py, tools/scorecard.py]
---

## Description
After the foundation round (tectfound: crust area held near its 40% target,
continents back to ~36-38 km median at L6 and L7), continental crust stays at
40-43% of the surface over 1 Gyr (it drifted to 45-47% before), but land is
~34% (L6 seeds 2-4, 1 Gyr, mean after 100 Myr: 34.2/34.2/33.9%; before the
round 32.5-33.7%, because the thinned continents of the old code stood lower).
Earth: ~29% land on ~41% continental crust; our continents drown less of
their area (~8 points of the surface vs Earth's ~12) and mean land stands
~1100-1200 m (Earth ~840 m).

Options:
- (A) Accept: the envelope allows 22-42%, Earth is an analogue, and the
  owner was happy with L6's continents.
- (B) Lower `continental_fraction` 0.40 -> ~0.36: land ~30-31%, fewer and
  smaller continents (largest landmass ~10% smaller).
- (C) Lower `continental_thickness` 37 -> ~35 km: continents ~300 m lower
  (mean land ~900 m, closer to Earth), land ~32%, more low coastal plain and
  shelf; crust a little under Earth's 35-40 km.
Lean: C (it brings both mean land height and land share toward Earth without
shrinking the continents); B if the owner prefers more ocean.
