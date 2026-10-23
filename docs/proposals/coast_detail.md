# Coast detail (PW-097): coast form, coast-bound life, game-facing coasts

Status: stage 1 built (world layers, viewer, summary), stage 2 built in part (zoom shore classes, barrier
islands with inlets and lagoons, colonies, hazards; opt-in terrain). Coast-detail lane, 2026-10-23.

## What already existed

- **Coastal life** (PW-188, PW-323, `planet/coastal.py`): coral reef, kelp, seagrass, mangrove and salt marsh
  as % of a cell, plus turbidity (river mud and tidal/wave resuspension) and upwelling. The zoom places them per
  pixel (`zoom_coastal.py`), and since PW-326 non-volcanic reefs are terrain (fringing/barrier/patch reefs,
  reef flats 1-3 m below the sea, lagoons deepened to keep cell means).
- **Volcanic reefs and atolls** (PW-004, `zoom_volcanoes.py`): fringing -> barrier -> atoll on subsiding
  islands, from the run's volcano table (the subsidence history is already the volcano's age and drift).
- **Waves and tides** (`coast.py`): wave power by ray-traced fetch, tidal range with shelf amplification;
  deltas' Galloway weights (river, wave, tide).
- **Harbours** (PW-099, `humanuse.py`).

So reefs, atolls, mangroves, kelp and seagrass were done. The open part of PW-097 after its rescope is
**coast form**: cliffs vs beaches, barrier islands, tidal flats, fjords, deltas as a coast type, plus the
cheap game-facing extras (colonies, hazards).

## Stage 1: world layers (`planet/coastform.py`, built)

All from what a world stores; nothing upstream changes. An add-on like resources: `planet coast <world>`.
Each coastal land cell gets its sea side as the mean of its sea neighbours (as mangroves do in coastal.py).

| Feature | Derived from | Rule (literature) |
|---|---|---|
| ice front | `ice` at the coast | grounded ice meets the sea |
| fjord | glacial scour (`glaciated_myr`, time-zoom `glacial_erosion`, `ice_max`), relief, the deepest sea neighbour, annual temperature | troughs cut below sea level by ice that reached the coast |
| delta | the river mouth's BQART load (coastal.river_loads) and discharge | >= 300 kg/s with >= 1000 m3/s |
| mangrove coast | coastal.py's mangrove % | >= 3% of the cell |
| tidal flats and salt marsh | tidal range >= 4 m on a low or muddy coast (Davies 1964), or salt marsh >= 3% | |
| barrier islands | low relief, shallow sea in front, waves 1-5 kW/m, tides < ~4 m, sand supply (cover, coastal plain, river load), no fresh glacial scour | Hayes 1979; Davis & Fitzgerald 2004 |
| coral coast | reef >= 0.75% on a sea neighbour | |
| cliffs | rocky land x wave power x relief, hard rock counting extra | Sunamura 1992 |
| rocky shore, beach, sheltered low shore | rocky >= 0.5; waves >= 2 kW/m; else | |

Scores stored with the class: `barrier`, `cliff` (0-1, used by the zoom). Coast-bound life and game layers:

- `seabirds`: productive water (upwelling, cool water, tidal mixing; the sea neighbours' best) x a safe nest
  (cliffs, islands of <= 3 cells, rocky shores, ice-free).
- `seals`: the same food x cool water (warmest-month SST ramp 25 -> 18 C) x a haul-out (rocky shore, beach,
  island, sea ice).
- `nav_hazard` (sea cells): reefs, offshore shoals, sea ice much of the year.

Viewer: layers *coasts*, *barrier islands*, *cliffs*, *seabirds*, *seals*, *sea hazards* with legends and a
hover row ("coast: barrier islands and lagoons (barrier 0.62, seabirds 0.41)"). World summary and `.txt` gain a
coast section (km of coast per class, the longest stretches, colony hot spots).

## Stage 2: zooms (`planet/zoom_coast.py`, built in part)

`planet coast zoom:<id> [--terrain]`: new layers `coast_type` (shore band), `barrier_island` (1 island,
2 lagoon, 3 inlet), `nav_hazard`; colonies as point features in `zoom.json` `coast.features`.

- Shore classes per pixel: the world class of the nearest coastal cell for what the zoom cannot see itself
  (fjord, delta), the zoom's own relief within 2 km, wave power, tidal range, rock and coastal life for the rest.
- Barrier islands: off low shores of the world's barrier coasts, a 1-1.5 px strip 1-5 km out over water
  < 15 m, inlets from planet-fixed noise with a spacing set by the tides (microtidal long barriers ~25 km,
  mesotidal short ones ~8 km: Hayes 1979). `--terrain` raises the islands 1.5-3 m and makes them land:
  opt-in, so existing zooms and their goldens never see it.
- Colonies: the best cliff/island shore pixels of the world's colony coasts, >= 25 km apart.

Not done (drafts): islands in `zoom.py` itself (with the satellite colours and the rivers re-routed through
the lagoon), spits and beach ridges oriented by longshore drift, tidal channel networks, cliffs as terrain.

## Later (proposal only)

- **Drowned reefs and reef terraces** from the time zoom's sea-level history (`meta.sea_level_change_m`
  per frame): reefs that grew at a lowstand and drowned (now 60-120 m deep, a shelf-edge hazard and a game
  feature), raised terraces on uplifting arcs (run's uplift rate x the sea-level curve). Needs the time zoom's
  frames: a timezoom/coast draft.
- **Atoll stage from subsidence**: already in PW-004 for volcanic islands; nothing to add at world scale.
- **Harbours**: humanuse already scores shelter; the zoom's barrier inlets and lagoons are natural harbours
  of small craft (and hazards for big ones): feed `nav_hazard` and the inlets into humanuse later.

## Decisions (inbox drafts, needs-decision, built on the lean)

1. Fold `coastform.world_layers` into `world.finish` (every new world gets the coast layers) vs keep it an
   add-on (`planet coast`). Lean: fold in once the owner has seen it (it adds ~1 s per L6 world).
2. `--terrain` barrier islands: opt-in in the add-on (built) vs a step of `planet zoom`. Lean: move into
   `planet zoom` after a golden update the owner agrees to, with the rivers routed through the lagoons.

## Earth anchor (`tools/coast_check.py`, world 577526, L6)

26/32 named places right: Outer Banks, Texas, Florida, Wadden barriers; Norway, Chile, BC, Greenland fjords;
Fundy tidal; Sundarbans, Amazon, Mississippi (salt marsh), Nile, Mekong deltas; Red Sea, Queensland coral;
no coral or mangrove off Peru or Namibia; seabirds on the Peru, Namibia and Orkney coasts; California seals.
Misses: Cornwall (Bristol Channel tides make it tidal), Bunda Cliffs (weak Southern Ocean waves, PW-074),
Korea's west coast (relief), Mississippi as a delta (salt marsh comes first), Belize (0.7% reef: the Earth
rock map's shale shelves, PW-323 note), Namibia seals (0.32: SST at the ramp's edge).
