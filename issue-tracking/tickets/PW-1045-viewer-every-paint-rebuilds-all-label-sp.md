---
id: PW-1045
title: "Viewer: every paint rebuilds all label sprites and re-uploads the cloud texture; the server forbids browser caching of 100 MB runs"
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: s
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-679, PW-687, PW-685]
refs: [viewer/index.html, planet/server.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-30
---

## Description
In plain words. The globe redraws more than it needs to. While a peoples run plays, every frame re-paints every continent name and highlight label from scratch and re-uploads the cloud picture, which is likely part of why the viewer "chugs" on peoples (PW-679). Separately, the server tells the browser never to keep a copy of anything, so every reload, and every embedded globe in the Technology tab, downloads a ~100 MB run again.

From the viewer-code audit (Cache-Control verified): `server.py:314-316 end_headers` sends `Cache-Control: no-store` for every response. `paint()` always ends in `buildOverlays()` (index.html:~1678), which rebuilds axis, landmass names, highlight marks and zoom outlines, each label a new canvas + CanvasTexture; `disposeObj` (~1822) disposes the cached cloud texture (~1919) so it is re-uploaded each rebuild; `cloudCache` is never cleared on world change. Per-cell `new THREE.Color` / `.find` in `pftColor` and `resColor`.

Fix: cache sprites by text|colour and only move them; skip `buildOverlays` when positions and overlay-affecting state are unchanged; mark cached textures shared so `disposeObj` skips them and clear `cloudCache` on world change; hoist per-cell lookups out of `cellColors`. Server: keep no-store for /viewer/ and /api/, send `no-cache` + ETag (size-mtime) for data files and answer 304.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-viewer-redraw-and-reload-waste.md (found by code-audit-2026-10).
- 2026-10-29: Viewer lane 51 split the code into modules. The code paths named here now live in globe/geometry.js (`paint`), globe/overlays.js (`buildOverlays`, `disposeObj`, `cloudTexture` / `cloudCache`) and globe/draw.js. draw.js has `canvasSprite`: one sprite factory instead of four, the natural place for a text|colour cache. The per-cell colour code is now one `color` factory per layer in globe/layers.js (cellColors), which is where the pftColor/resColor lookups should be hoisted out of the loop. Nothing in this ticket is fixed yet.
- 2026-10-30: Viewer lane 53: label sprites are cached (globe/draw.js canvasSprite keeps one SpriteMaterial and canvas texture per text, colour and style, marked shared), so a repaint makes only new Sprite objects, with no canvas drawing or texture upload; disposeObj leaves shared textures and three's sprite geometry alone. The cloud texture is marked shared (no longer disposed and re-uploaded on every overlay rebuild), keyed by the world or run frame and season, emptied when another world or run opens, and capped at 6. Server: data files (anything outside /viewer/, /api/ and /docs/review/) answer Cache-Control: no-cache with an ETag (size-mtime, its own tag for the gzipped body), Last-Modified and Vary: Accept-Encoding, and 304 on If-None-Match or If-Modified-Since. The second check matters: Chrome revalidates an HTTP/1.0 server's answers by date only (checked in headless Chrome, where a run.json and a layer reload now cost a 300-byte 304). The viewer's run, grid and layer fetches use cache: 'no-cache' instead of 'no-store'. The main server on 8765 needs a restart after the merge. Not done: skipping buildOverlays when nothing moved, and hoisting the per-cell pft/resource lookups.
