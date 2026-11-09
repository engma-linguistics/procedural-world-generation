---
id: PW-1561
title: "Two models of bilingualism: the language pass's l2_share and loans ignore the tongues ledger's trade languages and rulers' tongues"
type: task
status: todo
parent: null
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: lane-230
blocked_by: []
relates: [PW-1526, PW-985]
refs: [planet/lineages/tongues.py, "planet/language/inputs.py::Run.l2_share", "planet/language/inputs.py::Run._trade_triggers", planet/language/history.py, docs/review/peoples/trade-languages.md]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: the language pass (planet/language/) decides how much a people's speech is worn by adult learners and borrows from others
using its own guess at bilingualism (`inputs.Run.l2_share`: other peoples on the deme's cells plus mixed cities) and its own trade-contact
trigger (`_trade_triggers`: shared cells for 3 kyr). Lane 230's tongues ledger (`lineages/tongues.py`) now says, per culture and era, which
other tongues its people speak and roughly how many: borderlands, a ruler's tongue, merchants abroad, the trade language of its trading
towns. The two are not linked, so a people the ledger shows half-bilingual in a ruler's tongue can have an l2_share near zero in the
language pass and borrow nothing from its rulers, and a trade language spoken in every port of a network leaves no loanwords in the
ports' languages. A reader comparing languages.json with /api/tongues will see the contradiction.

What to try: the language pass reads the ledger (it is a read-out of trade_flow and polities, so it would need those docs at language time,
or the ledger's per-era rows written beside languages.json) and takes l2 shares and loan donors from it: the trade language as a loan
source for every culture speaking it, a ruler's tongue as a prestige donor weighted by the ledger's share. Keep the language pass's own
proxy where the run has no trade window (older than 12.5 kyr).
- [ ] languages.json and the tongues ledger agree on who is bilingual in what, era by era, on one L7 dnd run
- [ ] a trade language leaves loans in the languages of its speakers

## Updates
- 2026-11-08: Created from inbox draft draft-language-pass-reads-tongues-ledger.md (found by lane-230).
