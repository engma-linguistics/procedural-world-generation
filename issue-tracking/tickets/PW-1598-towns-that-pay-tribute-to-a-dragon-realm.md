---
id: PW-1598
title: Towns that pay tribute to a dragon realm are still raided by those dragons in the settlement ledger
type: task
status: todo
parent: PW-856
milestone: later
subsystem: culture
effort: m
impact: low
found_by: lane-253
blocked_by: []
relates: [PW-1108, PW-961, PW-1431]
refs: ["planet/lineages/settlements.py::_War.raid", "planet/lineages/polities.py (dragon realms)", "planet/server.py::polities_doc", "run 0141d1", "run a24559"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** Lane 253 (PW-1108) has dragons and giants, as sapient peoples, raid the towns and cities in their country. The
chance is about 1 in 10 a century at full presence, scaled by their aggression and rivalry. On 0141d1 that gives 3,305 raids in 12.5
kyr, and 1,148 on a24559. The polities read-out separately seats dragon realms that take tribute from the settled land
(polities.py, PW-1431). A town paying tribute is the dragons' own, and dragons should not raid it.

The ledger cannot read the realms: the polities read-out is made from the ledger (polities.derive reads settlements.json), so the
ledger would depend on its own read-out.

**What misleads if never done.** A town under a dragon realm's tribute shows "raided by the red dragons" every few centuries. The
"tribute or raid" hook of PW-961 then reads backwards: a campaign sees the protected towns raided as often as the free ones.

**Options.**
- A: The polities read-out marks which of the ledger's raids fell on its own realm's tributaries. The viewer shows those as "paid
  tribute to" instead.
- B: The ledger computes the realm reach itself: the cells within a dragon's lair reach, with the read-out's rule.

Lean: A.

## Updates
- 2026-11-09: Coordinator 11-09: option A (read-out relabels raids on its own tributaries as tribute).
- 2026-11-09: Created from inbox draft draft-dragon-tribute-not-raids.md (found by lane-253).
