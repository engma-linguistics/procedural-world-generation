---
id: PW-1731
title: free_ram_gb ignores a cgroup memory cap, so jobs pass the RAM guard and get OOM-killed
type: task
status: done
parent: null
milestone: v1.0
subsystem: infra
effort: s
impact: med
found_by: lane304
blocked_by: []
relates: []
refs: [planet/api.py, planet/tiles.py, docs/coordination.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
`api.free_ram_gb` reads the host's MemAvailable (Linux) or vm_stat (macOS). Every agent server and pytest runs under
`systemd-run --scope -p MemoryMax=24G`, and Docker or a desktop session slice may cap memory too. On this machine the
probe says ~130 GB free inside a 24 GB scope, so the refine / zoom / LOD-tile guards let through a job the cap then
kills, and the viewer shows a crashed job instead of the guard's "not enough memory" message.

## Done when
- On Linux the probe takes min(MemAvailable, memory.max − memory.current) of the process's cgroup v2
  (`/proc/self/cgroup` → `/sys/fs/cgroup/<path>/memory.max`, walking up to the root), with "max" meaning no cap.
- A test feeds both files' texts, as `tests/test_install.py` does for meminfo and vm_stat.

## Updates
- 2026-11-11: Status todo -> done. free_ram_gb now takes min(MemAvailable, cap room); tested in an 8G scope: 8.5 GB vs 132 uncapped
- 2026-11-11: Created from inbox draft draft-ram-guard-cgroup.md (found by lane304).
