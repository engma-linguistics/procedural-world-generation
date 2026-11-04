---
title: The culinary brief shows the run's stored gods and taboos, not the faiths Daniel wrote in or his saved gods mode
type: task
status: todo
parent: PW-1308
milestone: later
subsystem: food
effort: s
impact: med
found_by: lane166
blocked_by: []
relates: [PW-1430, PW-1309]
refs: ["planet/lineages/brief.py::_cultures", "planet/server.py::gods_doc", "planet/server.py::taboos", "planet/lineages/gods.py::read_authored", "run b4d502"]
---

## Description
In plain words: after Daniel writes a faith in the Religion tab, the god trees, map, timeline and taboos show it, but the brief panel
does not. Its gods and taboos come from the run's stored gods.json / taboos.json (brief.py, `ctx.religion()`), and those never see
authored.json or the saved gods mode. What goes wrong if this is never done: a culture's brief lists its old gods and taboos, so Daniel
reads a cuisine for a faith he has already replaced. Lane 166 left brief.py alone because lane 164 was working in it.

Fix: have `ctx.religion()` use the server's `gods_doc(d)` / taboos doc (memory and .godscache, keyed by the authored hash) when it runs in the
server, or `gods.derive(d)` (which reads authored.json) otherwise.
- [ ] the brief of the founding culture of an authored faith lists its named gods and their taboos
