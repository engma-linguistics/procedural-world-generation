---
title: The cached mantle basis can differ from a fresh build (up to 0.063), changing runs
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: med
found_by: pw440
blocked_by: []
relates: []
refs: [planet/tectonics/mantle.py, tests/test_envelopes.py]
---

## Description
In the pw440 worktree, `planet/tectonics/__pycache__/mantle_basis_10242_f95ea8fe34c7f959.npy` (L5),
written during a full `uv run pytest -q` while other numba jobs ran on the machine, differed from a
fresh build of the same key by up to 0.063 (byte 321 on). Runs read it: an L5 seed 1 100 Myr run gave
sea level 184.7 m and 13 plates with it, 159.6 m and 14 plates with a fresh one, and
`test_envelopes.py::test_plates[1]` failed (mean plate speed 1.91 cm/yr < 2). Removing the file (it is
rebuilt) fixed it; the rebuilt file matches a fresh build exactly. Either the build isn't deterministic
(threads, BLAS, degenerate eigenvectors) or a concurrent writer raced (`np.save` isn't atomic and the key
doesn't change). Fix: write atomically (temp + rename) and make the build deterministic (or check it
against a stored digest); the bad file is kept in the pw440 session scratchpad (`pw440/oldbasis/`).
- [ ] two builds of the basis under different thread counts and concurrent load are bit-identical
- [ ] the cache file is written atomically
