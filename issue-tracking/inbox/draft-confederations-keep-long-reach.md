---
title: "Polities: should a confederation keep the long reach? It is now most of the giant polities"
type: task
status: needs-decision
parent: PW-661
milestone: later
subsystem: culture
effort: xs
impact: med
found_by: lane179
blocked_by: []
relates: [PW-1449, PW-1454, PW-785]
refs: ["planet/lineages/polities.py::WIDE_BY", "planet/lineages/polities.py::_confederations", "planet/lineages/polities.py::STATE_MAX_KM", docs/review/culture/polities/round4.md, docs/review/culture/polities/round3.md, "docs/review/cultures-proposal/proposal.md#212-formation-growth-and-reach", "run 3c1caf", "run b4d502"]
---

## Description
**In plain words.** Lane 179 capped an ordinary state's reach at 250 km (Spencer 2010). Two kinds of polity keep the old 900 km
reach: a state that conquered another state, and a confederation (villages of a people with kings but no city, banding together
beside a foreign power; lane 178). On the Seven Meals showcase (3c1caf), 6 of the 8 polities over 1 Mkm² at the present are
confederations: half-orcs, hobgoblins (two), dragonborn, lizardfolk and humans. Some hold 1.0-1.4 Mkm² with ~10,000 villagers
counted in the ledger.

**What misleads if this is never decided:** a default nobody signed off decides both the present-day antelope-kin empire and most
of the map's giants.

Options (numbers on 3c1caf, the present; the baseline is lane 179's default, A):
- **A. Confederations keep the long reach (now).** 8 over 1 Mkm²; median century 3. The antelope-kin empire "North of Razukum" stands
  (0.52 Mkm²). Turchin 2009 puts over 90% of mega-empires in or next to the arid belt, where herder confederations sit
  (`proposal.md` 2.1.2), and steppe riders rule far.
- **B. Confederations get the 250 km cap too.** 1 over 1 Mkm² (largest 1.06). The antelope-kin have 4 states over the whole run,
  none at the present, because 10,000 of their people are not within 250 km of any one place. The PW-785 empire is lost.
- **C. Long reach only for a confederation of a people that rides** (knows `riding`). One more rule; not measured.

Lean: A. It keeps PW-785's empire without forcing it, and it matches Turchin's frontier story. The size of each giant is the
multipliers' problem (the touchy-multipliers draft), not this choice.
