---
title: "Viewer: show a people's other tongues and the era's trade languages (the tongues ledger has no viewer surface)"
type: task
status: todo
parent: null
milestone: v4
subsystem: viewer
effort: s
impact: med
found_by: lane-230
blocked_by: []
relates: [PW-1526, PW-1498]
refs: [planet/lineages/tongues.py, "planet/server.py::tongues", "planet/server.py::tongues_doc", docs/review/peoples/trade-languages.md, viewer/languages.html, tests/test_tongues.py]
---

## Description
In plain words: lane 230 built the ledger of which tongues each people speaks besides its own (a neighbour's, a ruler's, a host town's, a
trade language or pidgin, a faith's liturgy) and the trade languages of each era, served at `GET /api/tongues?run=<id>` (summary),
`&culture=<id>` (one people's rows per era) and `&ago=<kyr>` (one era whole). Nothing in the viewer reads it, and Daniel uses the viewer, not
the CLI, so as it stands the work is invisible to him.

What to add:
- [ ] on a culture's card (where the trade partners and trading towns show), a "Speaks also" list for the era on screen: tongue name (the
  culture's name, plus the language id when the run has languages.json), why (neighbour, ruler, host, trade language, pidgin, liturgy) and
  the share of its people;
- [ ] on the globe's Trade routes overlay, each era's trade languages: colour or label the long-haul network by its trade language, with
  its source (trade, rule, held over, pidgin) and since when;
- [ ] a link from a trade language with a language id to its page in viewer/languages.html.
Columns of a row are in the doc's `columns`; the first call on an L7 run computes the exchange doc (a minute or two) if it is not cached.
