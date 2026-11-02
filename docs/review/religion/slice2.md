# Religion, second slice (lane 133): faiths, the taboo catalogue, the Religion tab

Tickets: PW-1311 (more taboo kinds, stats), PW-1358 (religion views), under epic PW-1308. Still readouts: nothing here changes a history.

## In plain words

- **Faiths are now their own records.** A culture that first gets gods founds a faith; its daughter cultures keep it; a culture whose
  leading god turns to another domain for 20 kyr breaks away (a schism); a culture next to a more organised faith (temples, and a leading god
  0.15 more individuated) may convert to it. A faith ends when no culture holds it, which can happen while its cultures live on. In run
  b4d502: 205 faiths ever, about 95 living for 298 living cultures, 104 schisms, 13-20 conversions. The rule is a judgement call
  (draft-faith-spread-rule-call.md).
- **Taboos come in 13 kinds** (was: food only): food, totemic and clan, ritual purity and the dead, speech and names, kinship and marriage,
  the post-partum taboo, women and birth, sacred places, sacred times, hunting and harvest, chiefly and royal, sumptuary, contact and caste.
  57 specific rules beyond food, each from a source that was actually read (listed with how far: D-PLACE pages read, one HRAF summary,
  encyclopedia pages as secondary, one abstract). Each culture draws them from its way of life (farm, herd, forage, hunt, sea), its techs
  (burial, temples, kingship, writing, metal, the high god) and its gods' domains (a forest god makes a sacred grove likely). A culture has
  about 16 taboos.
- **The Religion tab** in the peoples workbench (next to Technology) has four views: small god trees, a map of the faiths with a time
  slider, a faith timeline, and each culture's taboos with the catalogue and its sources.
- **Stats** over 15 runs: docs/review/religion/stats-round1.md.

Viewer links (the owner's server):
- http://localhost:8765/viewer/lineages.html?run=b4d502#religion/trees
- http://localhost:8765/viewer/lineages.html?run=b4d502#religion/map
- http://localhost:8765/viewer/lineages.html?run=b4d502#religion/timeline
- http://localhost:8765/viewer/lineages.html?run=b4d502#religion/taboos

Screenshots: religion-trees.png, religion-map.png, religion-map-follow.png (one faith followed: its cells, its centre's path),
religion-timeline.png, religion-taboos.png, all on run b4d502.

## The taboo catalogue (planet/lineages/taboo_defs.py)

| kind | rules | chance (judgement unless said) | sources |
|---|---|---|---|
| food | (taboos.py: symbolic, identity, divine, purity) | every culture | Wikipedia Food taboo (secondary) |
| totemic and clan | 2 | 0.25, more for foragers and hunters | Wikipedia Totemism (secondary) |
| ritual purity and the dead | 5 | 0.6, more with burial and temples | Wikipedia Taboo on the dead, Tapu (secondary) |
| speech and names | 5 | 0.55, more with burial and kingship | Taboo on the dead, Naming taboo, Avoidance speech (secondary) |
| kinship and marriage | 7 | every culture: the nuclear-family rule always, clan exogamy at EA015's 362/1102 | Incest taboo (secondary), D-PLACE EA015 (read) |
| post-partum | 1, length drawn from EA036 | 364/372 (EA036); long ones x1.5 for farmers without kingship (Saucier 1972 summary) | D-PLACE EA036 (read), HRAF summary of Saucier 1972 |
| women and birth | 6 | 0.8 ("nearly universal" per the page) | Menstrual taboo, Tapu (secondary) |
| sacred places | 6 | 0.6, more with forest, mountain, river gods | Sacred grove, Tapu (secondary) |
| sacred times | 5 | 0.5 | Tapu, Taboo on the dead, Sacred grove, Menstrual taboo (secondary) |
| hunting and harvest | 4 | 0.45, more for foragers, hunters, sea peoples | Tapu (secondary); Idu Mishmi paper and Colding & Folke 2001 (abstract only) |
| chiefly and royal | 4 | only with kingship (0.85) | Tapu, Taboo (secondary) |
| sumptuary | 6 | only with kingship (0.6) | Sumptuary law (secondary) |
| contact and caste | 6 | only with kingship (0.25) | Untouchability, Incest taboo, Blacksmith (secondary) |

Not covered (no source read; draft-taboo-catalogue-gaps.md): gender division of labour, weekly rest days, smith taboos, Colding & Folke's
six resource categories. Rules I wrote and then dropped because the source did not say them: the god's secret name, the shedder of
blood unclean, nobody eats before the ruler, the totem's round-about name, the unclimbed holy peak.

## What was built

- `planet/lineages/gods.py`: `Faith`, `Pantheons` faith bookkeeping (`_join`, `_schisms`, `_conversions`, `faith_track`), `contacts()` (pairs
  of cultures on one cell or neighbouring cells per frame), `faith_docs()`, `FAITH_RULE`; gods.json gains `faiths` and `frames`, each being a
  `faith`, each culture its `faiths` history and `faith_now`.
- `planet/lineages/taboo_defs.py` (the catalogue), `taboos.py` (`context`, `other_taboos`, kind on every taboo; format procgen-taboos/2).
- `planet/lineages/faithmap.py` and `GET /api/faithmap?run=&frame=&w=&only=` (an equirectangular PNG per stored frame); `GET /api/taboos`;
  `/api/gods` recomputes in memory when a stored gods.json predates faiths. `planet/images.png_bytes`.
- `viewer/religiontab.js` and the Religion tab in `viewer/lineages.html`.
- `tools/religion_stats.py` (runs, religion, report). Tests: tests/test_gods.py (faith founding, conversion and end, schism, contacts,
  catalogue sourcing, taboos follow the culture).

## Judgement calls and limits

- The faith rule's three numbers (20 kyr schism, 0.45/0.15 conversion threshold, 30 kyr conversion time) are first guesses.
- A converted culture never breaks away by drift (else its own old gods retake the lead and undo every conversion within 20 kyr).
- Borders between cultures use one culture per cell (the last listed where peoples overlap); shared cells count as contact directly.
- A faith's centre is the mean of its cells' positions, so a faith on two continents has its centre at sea between them.
- Stored runs' gods.json and taboos.json (b4d502, a24559, 3c1caf) are old; the server works the new ones out in memory (about 25 s the
  first time), never writing into the run. `planet religion RUN --rebuild-techtree` would rewrite them (not run here: runs/ is off limits to lanes).
- Faith names wait for PW-986 like the gods': "the sky faith of <founding culture>".

## State (lane 133 hand-off)

Done: PW-1311 catalogue, wiring and stats round 1; PW-1358 views (a), (b), (c) and the faith model. Open follow-ups: the three drafts in
issue-tracking/inbox (faith rule call, catalogue gaps, spells common under kingship).
