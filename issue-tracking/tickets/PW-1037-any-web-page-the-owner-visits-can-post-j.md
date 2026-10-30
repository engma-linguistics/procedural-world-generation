---
id: PW-1037
title: Any web page the owner visits can POST jobs to the local server (/api/make, /api/lineages ...); add an Origin / Content-Type check
type: task
status: todo
parent: null
milestone: v1
subsystem: infra
effort: xs
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: []
refs: [planet/server.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. The viewer's server accepts "make something" requests from any web page open in your browser, not only from the viewer. A malicious or buggy site could start jobs that write files and burn CPU. It's a one-line guard.

Verified on main b36c9581: `server.py:452 do_POST` reads the body and dispatches `/api/make`, `/api/zoom`, `/api/timezoom`, `/api/finish`, `/api/enrich`, `/api/names`, `/api/favourites` and the lineages API without looking at `Origin` or `Content-Type`. A `text/plain` POST is a "simple" cross-origin request, so the browser sends it without a preflight. (DELETE is safe: its preflight fails.)

Fix: refuse a POST whose `Origin` is present and isn't the server's own host:port, and require `Content-Type: application/json`; make every viewer fetch send that header (lineages.html's run POST currently doesn't).

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Owner 10-29: reliability bugs come into v1.
- 2026-10-29: Created from inbox draft draft-server-rejects-cross-site-posts.md (found by code-audit-2026-10).
