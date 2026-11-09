---
id: PW-1523
title: Regional pantheons v0 - hubs, matched domain gods, peoples' patrons, a Pantheons subtab
type: story
status: done
parent: PW-1308
milestone: null
subsystem: culture
effort: l
impact: med
found_by: scout220
blocked_by: []
relates: [PW-1308, PW-1489, PW-1477, PW-986]
refs: [docs/review/culture/faiths/pantheon1.md, docs/review/culture/faiths/pantheon1/pantheons.py, "planet/lineages/gods.py::replay", "planet/lineages/gods.py::Pantheons.frame", "planet/lineages/gods.py::rule_table", "planet/lineages/gods.py::inputs", planet/lineages/attitudes.py, planet/lineages/settlements.py, "planet/server.py::gods_doc", "run 0141d1", "run 3e0eb4"]
created: 2026-11-08
updated: 2026-11-09
---

## Description

**In plain words.** This builds what PW-1521 asked for: regional pantheons. In some regions, cultures of different peoples come to
share domain gods (the sea god, the sky god), while each people keeps its own patron god. The pantheon forms around a mixed trade city
or a multi-people state, among tolerant cultures whose faith does not seek converts. Design and sources:
docs/review/culture/faiths/pantheon1.md section 4. **Build only after the needs-decision draft on the five choices is ruled.**

If this is never done, Daniel's request for D&D-style pantheons has no answer in the model. Today each culture's gods are islands,
linked only by descent and conversion.

Scope, read-out only (own random stream; majority faiths and conversions identical to main, checked as the minorities test does):
- [ ] Hubs: a lasting mixed town or city, or the ruler of several peoples (rule_table). Reach by distance (PANTHEON_KM). Openness =
      religious tolerance (lane 219, PW-1520, through one accessor; fallback attitudes tolerance) × not exclusive/missionary.
- [ ] Identification events, which give a seat with member beings (each keeps its id and label). Adoption of a seat by a culture with no
      match (how = "adopted"). Leaving and dissolving.
- [ ] Patrons: per people per pantheon, the leading lineage. It is never identified away.
- [ ] gods.json procgen-gods/3: `pantheons` list, `seat` per being, `patron` per people. Bump the server cache format.
- [ ] Viewer: Religion → Pantheons subtab (a roster table: domain gods × peoples, then a patrons row), the reach outline on the faith map,
      and a line on the being card.
- [ ] Calibration over 3+ runs (0141d1, 3e0eb4, 07c755): a polytheist D&D world gets a few regional pantheons covering under a third of
      the land; a world dominated by a missionary faith gets few or none. A slower hub test may need a `who` series in settlements.json
      (today only "now") or contact edges over time as a stand-in.

## Updates
- 2026-11-09: Status in-progress -> done. Lane 236 (538b2469): planet/lineages/pantheons.py read-out (own stream, faiths identical on/off), Religion -> Pantheons subtab, reach circles; 30 domains in 6 groups (moon, winter, earthquake, feast, healing, craft, kingship, law, wisdom, trade), each from a world or culture driver; gods/5. Living pantheons 0-5 on the D&D runs, 15 on 07c755 (over target, ticket taken in). The new domains change faith history on purpose (0141d1: 80% of cultures keep main's faith).
- 2026-11-08: Status todo -> in-progress. Lane 236 launched 11-08 night on D68 1A+C 2B 3A 4A 5A and Daniel's 'more domains in general' (new domains tied to tectonics, climate, polities, tech tree, trade, crops).
- 2026-11-08: Created from inbox draft draft-regional-pantheons-build-v0.md (found by scout220).
