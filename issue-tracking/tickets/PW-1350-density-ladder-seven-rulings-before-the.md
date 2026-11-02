---
id: PW-1350
title: "Density ladder: seven rulings before the build (PW-1275 step 2)"
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: xs
impact: high
found_by: lane130-density-ladder
blocked_by: []
relates: [PW-1275, PW-1203, PW-974, PW-833]
refs: [docs/review/peoples/density-ladder/ladder.md, docs/review/peoples/density-ladder/binford_by_npp.py, "planet/lineages/prey.py::people_fields", "planet/lineages/prey.py::PEOPLE_EXP", "planet/lineages/history/growth.py::ERA_DENSITY", "planet/lineages/history/growth.py::_note_eras", planet/lineages/history/model.py, planet/lineages/samples/dnd.toml, planet/lineages/samples/techtree.toml, "planet/lineages/spec.py::WAYS", tools/peoples_robust.py, "Binford 2001 Table 5.01 via D-PLACE dplace-dataset-binford", "Kelly 2013 Table 7-3", "Butzer 1976 Table 4", "Zimmermann et al. 2009 PPS 75", "Broadberry, Campbell & van Leeuwen 2011", "Bourke & Harwood 2009", "Pingali & Binswanger 1983 Table I", "Wilson 1986 ILCA RR14", "Khazanov 1994 p. 31"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: the sourced density ladder is written up (`docs/review/peoples/density-ladder/ladder.md`); before PW-1275 is built,
Daniel picks seven settings. Each option and lean is laid out in the page's "Questions for Daniel"; in short:

1. What a rung's number means: (A) the people's mean over its land, scaled by land quality; (B) its best-land density. Lean A.
2. Who changes way of life: (A) by land (farmable cells farm once the people knows cultivation); (B) a fixed share per kind; (C) a
   share growing with time since the tech. Lean A.
3. The land-quality power: (A) keep 0.75; (B) 1.0 for all rungs; (C) per rung (foragers ~1.3). Lean B.
4. Den peoples (goblins, kobolds, troglodytes): (A) forager rung with kind factor 1.2; (B) a judged "den" rung ~1-3; (C) give them a
   farming or herding way. Lean A, then C for the part that farms.
5. Irrigation only on cells water reaches (A) or a flat bonus (B). Lean A.
6. The dwarven hold: (A) its valleys' plough or terrace rung plus traded food up to a cap, mushrooms a small bonus; (B) a fixed hold
   rung (~1.5x plough, a judgement). Lean A.
7. Renaissance top: (A) cap the plough rung at the medieval peak (~35 /km²); (B) source an early-modern rung first. Lean A.

## Updates
- 2026-11-02: Status needs-decision -> done. Owner 2026-11-02: Q3 C (power per rung: 1.3 foragers where fitted, 1.0 elsewhere; report with a small write-up/graphs if numbers look odd). Q4 A plus a capped raiding share, sourced first (raiding cultures are real); den-people farming weighted low, rare not forbidden. All seven settled; build on PW-1275.
- 2026-11-02: Owner 2026-11-02: Q1 A (warn if it implements weirdly); Q2 A (confirmed: farming spreads with knowledge and people, outcompeting/assimilating foragers); Q5 A; Q6 A, and trade-fed holds (B) allowed if marked placeholder until trade exists; Q7 A for now plus a literature search for an early-modern rung put on the owner's wishlist. Q3 (land-quality power) and Q4 (den peoples: forager density plus raiding?) under discussion. Also: peoples have no groups for now (groups come from cultures and geography; no subspecies); halflings and gnomes can farm.
- 2026-11-02: Created from inbox draft draft-density-ladder-rulings.md (found by lane130-density-ladder).
