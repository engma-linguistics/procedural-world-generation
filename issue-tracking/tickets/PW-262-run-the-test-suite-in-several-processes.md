---
id: PW-262
title: Run the test suite in several processes (pytest wall time is set by serial work)
type: task
status: wontdo
parent: PW-247
subsystem: infra
effort: s
impact: low
found_by: parallel
blocked_by: []
relates: []
refs: [tests/conftest.py, pyproject.toml]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`uv run pytest` takes ~4.7 min wall on the Threadripper whatever the numba thread count (16 or 4: 284 s against 283 s, 2026-10-15, load ~10). The parallel branch caps tests at 4 numba threads (`tests/conftest.py`), which cuts the CPU from 1406 s to 554 s but not the wall time: the session fixtures (`sim4`, `sim4_60`, the L5 envelope worlds) and the tests run one after the other.

Options:
- A. Add `pytest-xdist` as a dev dependency and run `pytest -n 4 --dist loadfile` (each worker builds the session fixtures it needs: they cost seconds at L4 but ~1 min for the L5 envelope worlds, so group those with `loadgroup`). Probably ~1.5-2 min.
- B. Leave it: ~5 min before a commit is fine.

Lean: A if commits that touch `planet/` become frequent; measure first.

## Updates
- 2026-10-15: Status needs-decision -> wontdo. Owner (2026-10-15): skip; ~4.6 min is fine.
- 2026-10-15: Created from inbox draft draft-pytest-in-processes.md (found by parallel).
