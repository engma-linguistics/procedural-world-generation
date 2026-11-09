---
id: PW-1108
title: "Settlements: sacked, razed and walled: war and raids as a cause of a site's fall"
type: task
status: done
parent: PW-856
milestone: v4
subsystem: culture
effort: l
impact: med
found_by: fun-lane-60
blocked_by: []
relates: [PW-1011, PW-661, PW-961]
refs: [planet/lineages/settlements.py, "planet/lineages/settlements.py::_War", planet/lineages/contacts.py, "planet/lineages/attitudes.py::temperament", "planet/lineages/history/polity_live.py::_fates", viewer/globe/settlements.js, planet/lineages/brief.py, tests/test_settlements_war.py, "docs/overview.md 2.25", "run a24559", "run 0141d1", "run 3e0eb4", "Daly 2026 Lieber Institute: The Sack of Cities", "Pausanias 10.3.1-3", "Millek 2023 Destruction and the Fall of the Bronze Age Levant"]
created: 2026-10-30
updated: 2026-11-09
---

## Description
In plain words. Towns and cities in v0 (PW-1011) fall when the sea or the ice takes them, the rain fails, a river moves, or their people leave. When a different people takes over the land, the ledger records a change of hands ("held by the humans since ~2.1 kyr ago"). It calls a site "driven out" only if the newcomers keep no villages. There are no battles: no town is sacked, no city walled, no raids from giants or dragons.

What to try, reading what the runs already store:
- the contact record's incursions (meta.contacts, with direction and dates);
- the 'fortifications' tech;
- the megafauna (PW-961: raids, tribute).

Then:
- a site on a front with an incursion has a chance to be sacked (it shrinks) or razed (it becomes a ruin, "razed by the orcs");
- walls (fortifications) halve that chance;
- dragons and giants raid towns in their country.

Owner (PW-856, 10-25): crowding on a small landmass leads to conflict over resources. This belongs to the civilization epic.
- [ ] a "sacked by" and "razed by" reason in the ledger, from stored contacts; walls matter

## Updates
- 2026-11-09: Merged lane 253 (e1111ef0).
- 2026-11-09: Status todo -> done. Lane 253: built as a read-out in the settlement ledger (settlements._War; no second war model). In plain words: a town whose land passes to another people while its old people loses its stake there (under 25% of the cell's heads, the contact record's own 'holds a cell' share) was taken by force; a change of hands where the old people stays on is peaceful. A taking is sacked (the town loses 30% and regrows), razed (a ruin, 'razed by the orcs', can be resettled on the ruins) or simply occupied, by the winner's aggression (attitudes.temperament, the history's martial mark 0.5) and meta.war; walls (the holder's 'fortifications', towns and cities) halve every chance; dragon and giant kinds, as sapient peoples, raid the towns and cities in their country (presence table) by their aggression and the tree's rivalry (metallic dragons 0.5), never their own kin (kobolds, dragonborn). The run's incursions are too few to be the trigger (3 displacements a run in the ledger's 12.5 kyr on a24559 and 0141d1); they name a taking that lies inside one, with its bearing. Sources (Daly 2026 Lieber Institute: Peninsular War ~30 sieges, 3 towns sacked; Pausanias 10.3.1-3: Phokis razed, then rebuilt; Millek 2023: 52-61% of claimed ca. 1200 BCE destructions false) bound SACK 0.25 and RAZE 0.25 of sacks; both, WALLS 0.5, SACK_LOSS 0.3, RAID 0.1 per century and RAID_LOSS 0.1 are judgements (docs/overview.md 2.25). Three stored L7 dnd runs (baseline: the same runs' ledger before): taken by force 3,903 / 2,444 / 1,875 (a24559 / 0141d1 / 3e0eb4), sacked 577 / 335 / 302, razed 95 / 68 / 50, raided 1,148 / 3,305 / 2,954 (hill giants most); ruins 8,821 -> 8,875, 4,540 -> 4,802, 4,319 -> 4,290. Shows as a 'war' row on the settlement hover card (and 'walled since'), a war line in run.txt, meta.settlements.war, and the brief's ruins ('razed' and each ruin's wars). Stored runs keep their old ledger until 'planet settlements RUN' is redone. Follow-ups as drafts: read live polities' conquests when they run; dragon tribute vs raids.
- 2026-11-03: Milestones 11-03: later -> v4: v4 must-have: war sacks and walls settlements (ruins the campaign can use)
- 2026-11-03: Triage 11-03: v2 -> later: later cultures work (languages, polities, religion, morality); food comes first (fresh-eyes review, D44)
- 2026-10-30: Created from inbox draft draft-settlements-war-and-raids.md (found by fun-lane-60).
