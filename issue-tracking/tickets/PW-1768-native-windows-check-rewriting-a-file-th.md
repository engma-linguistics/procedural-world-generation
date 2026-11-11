---
id: PW-1768
title: "Native Windows: check rewriting a file the server has open or memory-mapped (layers, tiles, run.json) during a job"
type: task
status: todo
parent: null
milestone: v1.0
subsystem: store
effort: m
impact: med
found_by: lane315
blocked_by: []
relates: [PW-1760]
refs: [planet/osutil.py, "planet/osutil.py::replace", "planet/store.py::write_atomic", "planet/store.py::atomic_path", "planet/store.py::read_layer", planet/tiles.py, planet/server.py, planet/api.py, planet/thumbs.py, .github/workflows/install-smoke.yml]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** On Windows a file that another process (or this one) holds open, or maps with `np.memmap`, cannot
be replaced or deleted. Linux and macOS allow it. The store's atomic writes now retry `os.replace` for about 2 s on
Windows (`osutil.replace`), which covers a short read. But `store.read_layer` maps layer files for as long as the
array lives, and the tile service maps them too. The install smoke test (make, then serve) never rewrites a file
while it is mapped.

If this is never done: on Windows, a refine, a re-made zoom or a tile rebuild while the viewer has that world open can
fail with `PermissionError: [WinError 32] The process cannot access the file because it is being used by another
process`, and a job is lost. Other `os.replace` calls (`server.py` gzip cache, `api.Jobs` state, `thumbs.py`,
`machine.py`) have no retry yet.

To do: a Windows CI test that opens a world through the server, then re-slices or refines it, and deletes it with
`planet delete`. Fix what fails: release the maps first (copy small layers instead of mapping them on Windows), or write
new versions under new names.

## Updates
- 2026-11-11: Created from inbox draft draft-windows-replace-open-files.md (found by lane315).
