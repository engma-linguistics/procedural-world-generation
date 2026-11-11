---
id: PW-1760
title: One-command install from GitHub on Windows (native), macOS and Ubuntu, bootstrapping everything (no Python assumed), proven by a 3-OS GitHub Actions smoke test
type: story
status: in-progress
parent: null
milestone: v1.0
subsystem: infra
effort: l
impact: high
found_by: owner
blocked_by: []
relates: [PW-1719, PW-1720, PW-1730, PW-1716]
refs: [install.sh, planet/appconfig.py, planet/__main__.py, planet/api.py, planet/store.py, docs/review/plan/installer.md, "planet/store.py::_alive", "planet/store.py::_proc_start", "planet/store.py::lock", "planet/api.py::free_ram_gb", "planet/api.py::cgroup_cap_gb", "planet/api.py::refine_estimate"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** Daniel (11-11): "easy installation via Github for windows, mac, and ubuntu-at-the-very-least linux ... Assume we have to bootstrap up even 'do you have python' ... Unless this is somehow self-contained". Today install.sh covers Linux, macOS on a best-effort basis, and Windows only through WSL2. It already brings its own Python: the pinned, checksummed uv downloads a managed Python and the wheels, so nothing needs to be preinstalled except curl (Windows has PowerShell built in).

To do:
- `install.ps1` for native Windows, with the same commands as install.sh (`irm <raw url>/install.ps1 | iex`): uv's Windows build, pinned with its sha256; a Start-menu shortcut; the same `planet self` verbs.
- Make the runtime Windows-safe: find every Linux-only spot in planet/ (`/proc` reads in planet/store.py and planet/api.py, process groups and signals, path separators, `xdg-open`, the job runner's process handling) and give each an OS branch.
- The macOS gaps listed in installer.md: numba/TBB on arm64, and a `.command` launcher.
- `.github/workflows/install-smoke.yml`: on ubuntu-latest, macos-latest (arm64) and windows-latest, run the installer from the checkout, then `planet self status`, a tiny L4 make, and the viewer answering 200.
- README: the three one-liners.

**Testing (Daniel OK.d the test-branch push 11-11):** only Linux is on hand here, so the Windows and macOS proof is the Actions run, which needs a branch pushed to GitHub (pushes are otherwise only at releases, D83).

**Self-contained option (stretch):** a fully offline single-download bundle per OS (e.g. PyInstaller), which would be large because of numba/llvmlite. The uv route is self-bootstrapping and much smaller, so prefer it unless Daniel wants offline installs.

## Updates
- 2026-11-11: Status todo -> in-progress. lane 315 merged. Actions run 43116330508 on ci/install-smoke: ubuntu passes end to end; macos and windows install and status pass but the tiny make fails at the zoom step. macOS: the zoom RAM guard's fixed 8 GB spare refuses a 2 GB zoom on a 7 GB runner. Windows: Errno 22 writing zooms/<id>/layers/barrier_island.bin (likely rewriting a memory-mapped file, PW-1768). Lane 316 fixes.
- 2026-11-11: Merged inbox draft draft-native-windows-linux-only-spots.md ("Native Windows: Linux-only spots in planet/ (os.kill(pid, 0) ends a live run, no file locks, no free-RAM reading)", found by lane313).
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
- 2026-11-11: Daniel has a Mac to test on: Apple Silicon, 24 GB RAM. The macOS install is proven by hand on it: a checklist step for Daniel, with exact commands; a lane can't reach it. No Windows machine, so Windows is proven by the GitHub Actions run only (Daniel OK.d pushing a test branch for it, 11-11).
- 2026-11-11: Created from inbox draft draft-native-windows-macos-install.md (found by owner).
