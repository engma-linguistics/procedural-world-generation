---
id: PW-1001
title: "Present-day dragon density's rationale ('large carnivores at a few percent of their potential, Ripple 2014') is not in Ripple 2014: find a source or restate it"
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: xs
impact: low
found_by: papers-1029
blocked_by: []
relates: [PW-957, PW-963, PW-923, PW-938]
refs: [planet/lineages/history/megafauna.py, docs/proposals/megafauna-scaling.md, docs/references/megafauna/ripple2014_large_carnivores_science.pdf]
created: 2026-10-29
updated: 2026-11-03
---

## Description
The owner accepted the 1 per 5,000 km2 present-day dragon density (PW-923, PW-957), and the proposal explains it as people pressure: "real large carnivores in human-dominated land run at a few percent of their potential (tigers ~3-4% of their historical numbers; Ripple et al. 2014)". `megafauna.PRESS_N0` and the module docstring cited Ripple for that claim too.

Ripple et al. 2014 (Science 343:1241484) is now on file and does not say this. It gives:
- ranges, not numbers: 17 of the 31 largest carnivores hold on average 47% of their historical range, from <1% to 73% (p. 1241484-2);
- per species (Table 1): tiger 18%, lion 17%, gray wolf 67%, brown bear 68%;
- present world populations only (Fig. 1, p. 1241484-3), with no historical counts.

The comments now say what Ripple actually gives. The density-against-potential figure still has no source. The value itself is the owner's pick and is not in question.

Options:
- **A.** Find a source for large-carnivore density or numbers against their potential. Tiger census against historical estimates is the obvious candidate (e.g. the Global Tiger Initiative figures Ripple cites as ref. 87, not on file).
- **B.** Restate the rationale on what Ripple gives: people cut large carnivores to about half their range, and to far less in farmland. Then 1/5,000 stays the owner's choice, motivated but not derived.

Lean: B now. A only if the owner wants the number defended.
- [ ] the proposal's "Natural density, people pressure" bullet and PW-957's Description cite a figure that a paper on file supports, or say it is a judgement

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Dragon-density tail; PW-961 stays.
- 2026-10-29: Created from inbox draft draft-ripple-few-percent-unsourced.md (found by papers-1029).
