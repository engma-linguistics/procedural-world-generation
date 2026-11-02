---
id: PW-1324
title: The same seed gives a different 1 Gyr world at 6 and at 8 numba threads (check)
type: task
status: done
parent: null
milestone: null
subsystem: infra
effort: s
impact: med
found_by: lane-118 (PW-1297)
blocked_by: []
relates: [PW-1297]
refs: [tools/scorecard.py, docs/review/speed/pw252.md, planet/parallel.py, planet/kernels.py]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: on unchanged main (019339bb), `tools/scorecard.py --myr 1000 --seeds 1 3 --threads 8` gave seed 1 land 33.5%, ice 2.2%,
tree cover 41.5%; a paired screen of the same seed 1 (L6, 1 Gyr, same Simulation setup) at 6 threads gave land 35.6%, ice 2.8% (screen
and scorecard not otherwise identical code paths, so this is a hint, not proof). If a reduction or scatter in a parallel kernel adds in thread-count-
dependent order, runs are not reproducible across machines or thread settings, and any "same seed" comparison between lanes is only
statistical. Found while checking that PW-1297's last-bit changes cause no physical shift (they do not beyond this noise).
Check: run `Simulation(build_grid(5), 1, ...)` for 200 Myr at NUMBA_NUM_THREADS 1, 6, 8, 16 and compare the arrays bit for bit; if they differ,
find the kernel (a prange with an accumulating reduction or atomic-order scatter).
- [ ] bit-compare one small run across thread counts; list the kernels responsible if they differ

## Updates
- 2026-11-02: Status todo -> done. Lane 124: not reproduced at 1/2/6/8/16 threads (L5 to 1 Gyr, L6 100 Myr, whole and chunked); tests/test_thread_independence.py guards it. Lane 118's difference came from its two scripts (PW-1333).
- 2026-11-02: Created from inbox draft draft-run-not-reproducible-across-thread-counts.md (found by lane-118 (PW-1297)).
