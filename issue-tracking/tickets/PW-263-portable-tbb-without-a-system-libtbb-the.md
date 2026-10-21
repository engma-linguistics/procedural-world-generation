---
id: PW-263
title: Portable TBB without a system libtbb (the pip "tbb" wheel isn't found by numba as is)
type: task
status: wontdo
parent: PW-247
milestone: v2
subsystem: infra
effort: s
impact: low
found_by: parallel
blocked_by: []
relates: [PW-250, PW-084]
refs: [planet/parallel.py, pyproject.toml]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`parallel.pin_threading_layer` picks numba's `tbb` layer when libtbb loads, else `workqueue` (then `api.COMPUTE` keeps one computation at a time per process). On the Ubuntu box TBB comes from the system (`/usr/lib/x86_64-linux-gnu/libtbb.so.12.17`); a machine without it falls back to workqueue.

Tried 2026-10-15 in a scratch venv (Python 3.14, numba 0.68, `tbb` 2023.1.0 from PyPI): the wheel puts `libtbb.so.12` in `<venv>/lib/`, but numba's `tbbpool` extension has no RPATH and dlopens `libtbb.so.12` by name, so it still loads the system copy, and would find none without one. It only uses the wheel's copy with `LD_LIBRARY_PATH=<venv>/lib`. The PyPI wheels are also x86-64 only (there's none for the arm64 Mac).

Options:
- A. Leave it: system TBB where there is one, workqueue elsewhere. Since the jobs now run in separate processes (planet/parallel.py), workqueue only costs in-process concurrency (server highlights requests), which barely matters.
- B. Add `tbb` as a Linux-only dependency, and have `pin_threading_layer` preload `<sys.prefix>/lib/libtbb.so.12` with `ctypes.CDLL(path, RTLD_GLOBAL)` before importing `tbbpool` when no system copy loads (~10 lines).
- C. Document `LD_LIBRARY_PATH` for the rare machine that needs it.

Lean: A. Outputs are identical under either layer (PW-215), and concurrency now comes from processes.

## Updates
- 2026-10-15: Status needs-decision -> wontdo. Owner (2026-10-15): ignore; system TBB where present, workqueue elsewhere (option A).
- 2026-10-15: Created from inbox draft draft-tbb-portable.md (found by parallel).
