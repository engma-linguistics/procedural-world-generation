---
title: "Conquest harshness (PW-1465) should read the winner's tolerance from attitudes, but attitudes are a read-out and the fates are in the history"
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: peoples
effort: s
impact: med
found_by: lane199
blocked_by: []
relates: [PW-1465, PW-904, PW-1434]
refs: ["planet/lineages/history/polity_live.py::FATE_AT", "planet/lineages/history/polity_live.py::FATE_CUT", "planet/lineages/attitudes.py::temperament", "planet/lineages/attitudes.py::Attitudes", docs/review/culture/attitudes/round1.md]
---

## Description
**In plain words.** PW-1465 waits on attitudes so a conqueror's harshness (kept / thinned / expelled) can follow the winner's
tolerance, not only the tree's old enmities. Attitudes v0 now exist (lane 199, `planet/lineages/attitudes.py`), but they are worked
out *after* the run, inside the religion read-out (gods.py), because they read faiths and the polities read-out. The fates are decided
*inside* the history, in `history/polity_live.py` (behind POLITIES_LIVE, off), which cannot read an after-run file. Lane 199 left
polity_live.py alone (lane 196 is editing it), so PW-1465 is not wired.

**What misleads if never done.** With the switch on, every conqueror is equally harsh to a people it dislikes the same amount, so the
v4 card's "which peoples it kept, expelled or thinned" shows placeholder thresholds as if they were the model (PW-1465's own warning).

**The small change.** `attitudes.temperament(line)` is pure (tree traits and demography only) and `Attitudes` has no I/O, so
polity_live can keep its own `Attitudes` and step it per century from its own state (who took what, who rules whom, contacts from the
presence). Then the fate thresholds read hostility x (1 - the winner's tolerance) instead of hostility alone. The after-run read-out
would then become a second copy of the same walk unless one of them reads the other's record.
- [ ] polity_live steps an Attitudes of its own; the fate reads the winner culture's tolerance
- [ ] one source of truth for the walk (the history's record read by gods.py, or the reverse)
