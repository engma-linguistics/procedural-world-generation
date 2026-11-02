---
id: PW-1311
title: Religion slice 1 judgement calls for Daniel (culture-level beings, faith-tech rates, placeholder purity weight, taboo kinds)
type: task
status: done
parent: PW-1308
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lane117
blocked_by: []
relates: [PW-1304, PW-1305, PW-1306, PW-1307]
refs: [planet/lineages/gods.py, planet/lineages/taboos.py, planet/lineages/taboo_defs.py, planet/lineages/taboos.py::other_taboos, planet/lineages/taboos.py::context, planet/lineages/samples/techtree.toml, tools/religion_stats.py, tests/test_gods.py, docs/review/religion/slice1.md, docs/review/religion/slice2.md, docs/review/religion/stats-round1.md, docs/review/religion/religion_stats_individuation.png, "https://d-place.org/parameters/EA036", "https://d-place.org/parameters/EA015", "https://hraf.yale.edu/documents/106", "run b4d502", "run a24559", "run 3c1caf"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: the first religion slice works, and I made these calls so as not to stall. None is a physics matter, but they shape what the culinary book sees.

1. **Beings live on cultures, not demes.** The ticket says 3-15 beings per deme. A culture (a deme or a run of demes, cultures.py) is the unit with a land and a
   way of life, and a deme split that is not yet a culture would copy gods before a culture exists. Option A (done): per culture. Option B: per deme, copied on every
   deme split, fused on every deme fusion (about 4x more beings, finer cousins). Lean A for v2.
2. **Moralizing high god rate 0.08 per kyr, spread 0.3; divine magic 0.2.** At 0.4 and the default spread, one invention reached every people with kingship in
   under 1 kyr (b4d502). At 0.08/0.3, 21 of 66 peoples get it. The Whitehouse 2019 result behind the idea was retracted (Nature, July 2021), so
   there is no sound Earth anchor; the number is "some peoples, not all". Daniel may want it rarer or commoner.
3. **The purity weight is a seeded placeholder (0.1-0.6 per culture)** until the moral ledger (PW-1307) gives each culture a real one. The number of purity rules
   is 4 x weight.
4. **Taboo kinds** (wild swine, hares, eels, shellfish, whales and seals, waterfowl, bats, carrion birds, snakes, frogs, insects) and what each "straddles" are
   my reading of Douglas 1966, not a sourced table. Replace with a read-and-cited list, or keep as fantasy-neutral categories.
5. **"Practical" taboos** (seasonal poison, parasites) are not emitted: nothing in the sim models them.
6. **Individuation tiers** (spirit ritual 0.1, burial 0.2, temples 0.45, kingship 0.6, high god 0.9; spells above 0.5) are guesses; with them a people with temples
   and kingship but no high god has one spell-granting god, and a people with only temples has none.

Lean: keep all as built and revisit when the ledger and names (PW-986) land.

## Updates
- 2026-11-02: Status todo -> done. Lane 133 (merged a6f3e62a): 13 taboo kinds, 57 non-food rules, each sourced (level stored in SOURCES); stats over 15 runs in docs/review/religion/stats-round1.md. Follow-ups filed.
- 2026-11-02: lane 133: taboo catalogue of 13 kinds and 57 sourced rules beyond food (taboo_defs.py), drawn per culture from its way of life, techs and gods; stats round 1 over 15 runs (docs/review/religion/stats-round1.md): individuation sits in steps under the tier ceilings, pantheons peak at 6, ~16 taboos per culture, spells far commoner than slice 1 said (draft filed).
- 2026-11-02: Status needs-decision -> todo. Owner 2026-11-02: first pass good. Wants many more taboo kinds, both specific taboos to choose from and types (practical/hygienic, ritual purity, totemic, sumptuary, speech/name, kinship, place/time, etc., even ones irrelevant to the sim). Individuation tiers fine; keep stats of the odd cases and the distributions (bell curves) and report them to him over time.
- 2026-11-02: Created from inbox draft draft-religion-slice1-calls.md (found by lane117).
