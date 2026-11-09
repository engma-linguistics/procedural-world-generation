---
id: PW-1599
title: Settlement wars read the live polities' conquests when the history ran them, so a town's 'sacked by' agrees with the state card's 'the conquered'
type: task
status: done
parent: PW-856
milestone: v4
subsystem: culture
effort: m
impact: med
found_by: lane-253
blocked_by: []
relates: [PW-1108, PW-1575, PW-1496, PW-1513]
refs: ["planet/lineages/settlements.py::_War", "planet/lineages/history/polity_live.py::_fates", "planet/lineages/history/polity_live.py (took records, line ~451)", "viewer/globe/polities.js::polityRows", "docs/overview.md 2.25"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** Since lane 253 (PW-1108), the settlement ledger decides which towns were taken by force, sacked or razed. It reads
a stand-in: a town whose cell passed to another people while the old people lost its stake there. When the history runs live polities
(params.POLITIES_LIVE, off by default; lane 248 is changing it), the history itself decides each conquest and how the peoples on the
taken land fared: kept, submitted, thinned, expelled or razed (polity_live._fates). The state card shows that as "the conquered".

**What misleads if never done.** With live polities on, the two read-outs tell different war stories for the same land. The state card
can say "the humans submitted" while the ledger says the town was "razed by the orcs", or the reverse. A campaign writer trusts both.

**What to do.** polities_live.json's `took` rows record the step, the loser, the number of cells, how, and the fates, but not the cells.
- Write the taken cells, or the loser's key, so the ledger can find them.
- When a run has polities_live.json, the ledger reads its conquests for takings by force: razed where the people's fate was 'razed',
  sacked where 'thinned' or 'expelled', occupied where 'kept' or 'submitted'.
- The displacement stand-in stays for runs without live polities.
- [ ] a town on land a live conquest took carries that conquest's fate; tests on a small run with polities_live.json

## Updates
- 2026-11-09: Status todo -> done. Merged lane 254 (f1c313b6).
- 2026-11-09: Created from inbox draft draft-ledger-reads-live-conquests.md (found by lane-253).
