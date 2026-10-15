---
id: PW-238
title: "Land is 31-34% of the surface (Earth 29%) and stands high: lower a continental target or accept?"
type: task
status: in-progress
parent: null
subsystem: tectonics
effort: s
impact: med
found_by: tectfound
blocked_by: []
relates: [PW-046, PW-052]
refs: [planet/tectonics/params.py, planet/tectonics/crust.py, tools/scorecard.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
After the foundation round (tectfound: crust area held near its 40% target,
continents back to ~36-38 km median at L6 and L7), continental crust stays at
40-43% of the surface over 1 Gyr (it drifted to 45-49% before), and land is
31-34% (scorecard seeds 1/2 at 1 Gyr: 30.8/31.1%, range 30-36%; L6 seeds 2-4,
mean over 100-1000 Myr: 34.2/34.2/33.9%, 32.5-33.7% before the round, when
the thinned continents stood lower). Mean land elevation is ~1100-1200 m at
L6 and ~1350 m at L7 (Earth ~840 m).
Earth: ~29% land on ~41% continental crust; our continents drown less of
their area (~8 points of the surface vs Earth's ~12).

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

## Updates
- 2026-10-15: Status todo -> in-progress. Worktree tect2.
- 2026-10-15: Status needs-decision -> todo. Coordinator decision (north star: reasonably close to real behaviour, nudge): yes, nudge continental_thickness 37 -> ~35 km (or whatever brings mean land toward ~850-1000 m and land toward ~29-31%); Earth is not a parity target, so stop when it's close-ish.
- 2026-10-15: Created from inbox draft draft-land-share-vs-earth.md (found by tectfound).
