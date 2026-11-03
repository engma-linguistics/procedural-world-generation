---
id: PW-1368
title: "Taboo catalogue: unsourced kinds and thin sources (gender roles, rest days, smiths, Colding & Folke categories)"
type: task
status: todo
parent: PW-1308
milestone: v2
subsystem: culture
effort: s
impact: low
found_by: lane133
blocked_by: []
relates: [PW-1311, PW-1305]
refs: [planet/lineages/taboo_defs.py, "planet/lineages/taboos.py::other_taboos", "planet/lineages/taboos.py::context", docs/review/religion/stats-round1.md, docs/review/religion/slice2.md, "https://d-place.org/parameters/EA036", "https://hraf.yale.edu/documents/106", "https://en.wikipedia.org/wiki/Sumptuary_law"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: the new taboo catalogue (13 kinds, 57 rules) is sourced from pages that were actually read, but most are encyclopedia
summaries and some kinds Daniel named have no source yet, so they were left out rather than made up.

Gaps:
- **Gender roles** beyond menstrual and birth rules (who may hunt, smith, handle weapons, plough): not sourced. D-PLACE has "sex differences
  in activities" variables (EA054 onward) that were not read; they would give real frequencies.
- **Weekly rest days / taboo days**: no source read (the Sabbath and day-of-rest pages were not fetched).
- **Smiths**: the Blacksmith page says only that smiths are endogamous castes in parts of Africa and South Asia; no smith taboos.
- **Colding & Folke 2001** (six kinds of resource taboo): only the abstract was seen; the six categories would structure the "hunting and harvest" kind.
- **Meyer-Rochow 2009** (food taboos) and Fessler & Navarrete 2003 (meat taboos): not reachable; the food kind still rests on lane 117's
  reading of Douglas 1966 (see PW-1311 item 4).
- Only one taboo (post-partum, EA036) has a real frequency; every other kind's chance is a judgement (taboo_defs.KINDS).
- [ ] read the EA sex-difference variables and add a "work by sex" kind with their counts
- [ ] fetch Colding & Folke 2001 in full and regroup the resource rules
- [ ] replace the Wikipedia-only kinds' sources with the works those pages cite, where reachable

## Updates
- 2026-11-02: Created from inbox draft draft-taboo-catalogue-gaps.md (found by lane133).
