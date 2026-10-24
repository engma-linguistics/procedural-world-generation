---
title: "Salt and sea-food goods: salt sources and distance to salt per cell; fish, shellfish and sea mammals by coast, shelf, upwelling, river runs and lakes"
type: story
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: culinary-intake
blocked_by: []
relates: [PW-188, PW-097, PW-722]
refs: [planet/lineages/land.py, planet/resources.py, planet/coastal.py, docs/proposals/culinary-dnd-intake.md]
---

## Description
The culinary canon leans on salt and the sea, and neither is a food good yet.

**Salt:**
- a disputed salt lake is the oldest human–orc grievance;
- the strait empire's fish sauce comes from coastal salting works;
- herbivore peoples crave salt (proposal §4).

**Sea food:**
- whole steamed fish and paddy carp;
- raw-fish coastal aarakocra;
- pit-oven islanders;
- the goliaths' sea-mammal fat.

**New goods in `land.goods`**, all derived from layers that exist:
- `salt`:
  - from resources' salt (evaporite outcrop, salt pans of closed hot basins);
  - plus sea-salt coasts: arid or seasonally dry coasts with flats between the tides, from coastal life and tides;
  - plus brine springs where evaporite lies under springs (humanuse);
  - and a **distance to salt** per cell (a cost-distance over land).
- `fish`:
  - shelf area and upwelling (coastal.py), reefs, kelp and seagrass as nurseries;
  - **river runs** (cold rivers reaching the sea: salmon-like) and big lakes;
  - deltas and paddies are reached through rice (PW-721).
- `shellfish`: salt marsh, seagrass, flats between the tides, reef.
- `sea_mammals`: seals (exists), plus whales at the ice edge and on upwelling coasts.

Exported in the culinary brief. Optionally read by fisher-forager ways of life (PW-723).
- [ ] Earth plausibility check of the fish good against known rich fisheries (a sanity look, not a fit).
