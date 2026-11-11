---
id: PW-1767
title: The machine presets' memory cap is applied on Linux only; Windows and macOS run the server uncapped
type: task
status: todo
parent: null
milestone: v1.0
subsystem: infra
effort: m
impact: med
found_by: lane315
blocked_by: []
relates: [PW-1760, PW-1720]
refs: [install.sh, install.ps1, "install.sh::cmd_open", "install.ps1::Cmd-Open", planet/machine.py, planet/api.py, docs/review/plan/machine-presets.md, docs/review/plan/installer.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** The installer's machine probe writes a memory cap (`mem_cap_gb`) for the server and its jobs. On
Linux, `planet self open` enforces it with `systemd-run --scope -p MemoryMax`. On Windows (`install.ps1::Cmd-Open`) and
macOS there is no such wrapper, so the server runs uncapped. The RAM guards (`api.free_ram_gb`, now readable on all three
OSes) and the machine gates still refuse a job that would not fit when it starts, but nothing stops a job that grows
past its measured peak, or two jobs that each fit alone.

If this is never done: on an 8–16 GB Windows laptop or a 24 GB Mac, a heavy job that passes the gate can still push the
machine into swap and make it unresponsive, where the same job on Linux would be stopped cleanly at the cap.

Options: Windows: start the server inside a Job Object with `JOBOBJECT_EXTENDED_LIMIT_INFORMATION.JobMemoryLimit`
(ctypes, in the launcher or in `planet serve` itself; worker processes inherit the job). macOS: no per-process-tree
cap exists without root; a watchdog in `planet serve` that cancels the newest job when the tree's RSS passes the cap is
the portable fallback (and would also cover Windows).

## Updates
- 2026-11-11: Created from inbox draft draft-windows-mac-memory-cap.md (found by lane315).
