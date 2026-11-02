---
id: PW-1358
title: "Religion views: small god-tree examples, a map of where faiths arose and spread, and a religion timeline apart from the cultures timeline"
type: story
status: done
parent: null
milestone: v2
subsystem: viewer
effort: m
impact: high
found_by: owner
blocked_by: []
relates: [PW-1308, PW-1304]
refs: [planet/lineages/gods.py, planet/lineages/gods.py::Pantheons._conversions, planet/lineages/gods.py::faith_docs, planet/lineages/faithmap.py, planet/lineages/taboos.py, planet/server.py::faithmap, planet/server.py::gods_doc, viewer/religiontab.js, viewer/lineages.html, viewer/techtab.js, tests/test_gods.py, docs/review/religion/slice1.md, docs/review/religion/slice2.md, docs/review/religion/religion-map-follow.png, "run b4d502"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: owner 2026-11-02 wants to see religion: a few small drawn god trees (how a faith's gods split and individuate), a map of where each faith sprang up, moved and changed over time, and a timeline like the cultures one. Faiths must stop being one and the same as cultures: a faith can spread to other cultures or die out while its culture lives.

## Updates
- 2026-11-02: Status todo -> done. Lane 133 (merged a6f3e62a): faiths as own records (FAITH_RULE: found, inherit, schism after 20 kyr drift, conversion by organised neighbours, end); Religion tab: god trees, faith map with slider, timeline, taboos.
- 2026-11-02: lane 133: faiths as records (founded, inherited, schism, conversion, end), the Religion tab (god trees, faith map with time slider via /api/faithmap, faith timeline, taboos); rule filed as a needs-decision draft.
- 2026-11-02: Created.
