---
id: PW-1526
title: "Trade languages and multilingual peoples: who speaks what besides their own tongue; lingua francas along trade routes and in trading towns"
type: task
status: done
parent: null
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: owner
blocked_by: []
relates: [PW-1522, PW-1498]
refs: [planet/lineages/trade_routes.py]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: Daniel 11-08: with trade we need trade languages, and multilingual people. Per culture and era, a ledger of the languages its people speak besides their own: a neighbour's or a ruler's tongue (bilingual borderlands, subjects of an empire), and a trade language where its trading towns meet others (a lingua franca: Aramaic, Greek koine, Swahili, Malay, Sabir; pidgins). A trade language arises from the busiest trading culture on a route network or a ruling state's tongue; it spreads along routes and through merchant quarters. Literature first, sources fetched. The language worktree (another session, merging 11-08) owns the languages themselves; this ticket owns who speaks which, so it names languages by culture ids that the language work can render. Start after the language merge lands, reading its module rather than duplicating it. Religion link: a faith's liturgical language (Latin, Sanskrit, Pali, Arabic) is a second case of the same ledger.

## Updates
- 2026-11-08: Status todo -> done. Lane 230 (d8e513de): planet/lineages/tongues.py ledger per culture and era (neighbour, ruler, host, lingua franca/pidgin, liturgy), GET /api/tongues; 19 tests; design docs/review/peoples/trade-languages.md. Six stored L7 runs: 58-89% of heads speak another tongue; 13-25 trade languages per recent era. Follow-ups taken in from its drafts.
- 2026-11-08: Created.
