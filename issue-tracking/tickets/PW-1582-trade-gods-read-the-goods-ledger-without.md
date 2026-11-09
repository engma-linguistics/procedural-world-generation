---
id: PW-1582
title: "Trade gods: read the goods ledger without pulling the server into the lineages code hash"
type: task
status: todo
parent: null
milestone: v5
subsystem: culture
effort: m
impact: low
found_by: coordinator
blocked_by: []
relates: [PW-1523]
refs: [planet/lineages/gods.py, planet/lineages/brief.py, planet/provenance.py]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: lane 236 let a culture's goods ledger (how much it trades) raise its trade god. But gods.json is written with every run, and reading the ledger goes gods -> trade.derive -> brief.Ctx -> server, so the run's cache hash took in server.py and api.py (tests/test_store.py::test_code_hash_scopes failed) and every run's religion read-out waited ~10 s on the ledger. The coordinator took the read out on 11-09 at merge; trade gods now rise from trade/markets/coinage techs and towns only, and salience's ledger term is always 0. Fix: give trade.derive a context that does not import server (split brief.Ctx's server-reading methods, religion() and trade_flows(), off into the read-out layer), then read the ledger again in gods.inputs.

## Updates
- 2026-11-09: Created.
