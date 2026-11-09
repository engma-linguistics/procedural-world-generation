---
id: PW-1575
title: With polities in the history on, the read-out should draw the live map, not a second set of polities
type: task
status: done
parent: PW-661
milestone: v4
subsystem: peoples
effort: l
impact: high
found_by: lane234
blocked_by: []
relates: [PW-1434, PW-1466, PW-1488, PW-1460, PW-1456]
refs: ["planet/lineages/polities.py::derive", "planet/lineages/history/polity_live.py::LivePolities.doc", "planet/lineages/history/polity_live.py::LivePolities._step", "planet/lineages/output.py::save", planet/server.py, "planet/lineages/gods.py::rule_table", docs/review/culture/polities/round7.md, docs/review/culture/polities/round14.md, docs/review/culture/polities/round14/measure.py]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** With the switch on (`params.POLITIES_LIVE`), a run has two sets of polities. The live ones
(`polities_live.json`) are the states that fought inside the history: they pacified land, barred factions and decided which
peoples were kept, thinned or expelled. The read-out (`polities.derive`, run after the history from the settlement ledger) is a
second, separate set: it is what the viewer's Polities layer, the state cards, the religion read-out (gods.py's rulers) and the
nudge checks show. Round 7 (section 3) put off joining them until the gates were the run's own; since PW-1466 (lanes 192-196) they
are. Round 14 measures both sets on the same runs and they differ (see its tables: first states, largest polity, same-ruler share).

**What misleads if never done.** Flip the switch and the viewer shows states that are not the ones that shaped the peoples: a card
can say a state kept its subjects while the history expelled them, and v4's done-when 1 and 2 (states grow, fight and fall; a
state's card says whom it kept, expelled or thinned) would be shown on the wrong map. PW-1488's two attitude walks cannot be made
one until this is done.

**Try.** When `polities_live.json` exists, `derive` builds its doc from it instead of running its own steps: the steps and maps
as they are; each record's capital site from the ledger's town at its cell (or none); its ruling culture per step from cultures.json
at the capital (derive's `_ruler_culture`); its subjects, names, colours and why-fell from derive's own helpers; the invasions'
read-out from the live log. The live step would need to record provinces (`from_rec`) and subject cultures, as derive's maps do.
- [ ] with the switch on, the Polities layer, the cards and gods.py's rulers read the live polities; with it off, nothing changes
- [ ] round 14's measures re-run: the read-out and live columns are one column

## Updates
- 2026-11-09: Status todo -> done. Lane 238 (634864cd) merged: with the switch on, polities.derive builds from polities_live.json (live /2); map, cards, gods' rule_table all name the live polities; switch-off byte-identical. Suite 1934 passed. Switch stays off: live states small (PW-1583, lane 241).
- 2026-11-09: Lane 238: built. With polities_live.json present, polities.derive draws it (polities._from_live): same steps, polities (ids), cells, tiers, falls, conquests; read-out adds ledger capital, ruling culture, subjects, names, colours, fell_why, and the fates of peoples on taken land on the card. Live file now procgen-polities-live/2 (seat people, provinces, record ids; record only). Proof on L6 run f4fb14: 0/83 map steps differ, /api/polities cards and gods rule_table realms all live polities; switch-off read-out hash identical to main. Round 14 measure: readout and live rows one column. Switch stays off: on, states fewer and ~5x smaller at peak (draft live-polities-stay-small). docs/review/culture/polities/round15.md
- 2026-11-09: Created from inbox draft draft-polities-readout-reads-the-live-map.md (found by lane234).
