---
title: "Native Windows: Linux-only spots in planet/ (os.kill(pid, 0) ends a live run, no file locks, no free-RAM reading)"
type: task
status: todo
parent: null
milestone: v1.0
subsystem: infra
effort: m
impact: high
found_by: lane313
blocked_by: []
relates: [PW-1720, PW-1716]
refs: [planet/store.py::_alive, planet/store.py::_proc_start, planet/store.py::lock, planet/api.py::free_ram_gb, planet/api.py::cgroup_cap_gb, planet/api.py::refine_estimate, install.sh]
---

## Description
In plain words: the installer is to target native Windows (owner, 2026-11-11). A few places in planet/ assume Linux or
macOS, and one of them, on Windows, kills the run it is meant to check on.

If this is never done:
- **`store._alive` calls `os.kill(pid, 0)`** to ask whether a running simulation's process is still there. On Windows,
  Python's `os.kill` with any signal other than CTRL_C/CTRL_BREAK calls TerminateProcess. So listing runs (the viewer, `planet
  list`) would end a simulation that is running. Use a Windows branch: OpenProcess with ctypes, or `psutil.pid_exists` if
  a dependency is acceptable.
- `store._proc_start` reads `/proc/<pid>/stat`. Elsewhere it returns None, so a reused pid passes as the run's own
  process. It is harmless on macOS, but it needs a Windows equivalent (GetProcessTimes) for the check to mean anything.
- `store` imports `fcntl` for its cross-process file lock and has none on Windows (the comment says "the project targets
  Linux and macOS"). Two server jobs then write the same slice or zoom at once. Use `msvcrt.locking`, or a lock file
  taken with `O_CREAT|O_EXCL`.
- `api.free_ram_gb` reads `/proc/meminfo`, or `vm_stat` on macOS, and returns None elsewhere. On Windows every RAM guard
  is off (refine, zoom, tile builds). GlobalMemoryStatusEx's `ullAvailPhys` would do; `planet/machine.py::windows_ram_gb`
  already shows the ctypes call for the total.
- `api.refine_estimate` keeps 40 GB of the temp folder free because `/tmp` is RAM on the Threadripper. On Windows
  `%TEMP%` is disk, so the rule is right but its message ("it is memory on this machine") is wrong.
- The machine presets' memory cap (`mem_cap_gb`) is applied only by `install.sh`'s `planet self open` through
  systemd-run (Linux). Windows would need a Job Object with a memory limit in the launcher, or no cap; the gates still
  apply either way.

Checked by reading the code (`grep` for /proc, /sys, fcntl, os.kill, systemd in planet/); nothing was run on Windows.

- [ ] On a Windows machine, `planet list` while a simulation runs leaves it running, two jobs on one zoom wait for each
  other, and the refine estimate shows the free RAM
