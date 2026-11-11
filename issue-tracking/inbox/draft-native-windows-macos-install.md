---
title: "One-command install from GitHub on Windows (native), macOS and Ubuntu, bootstrapping everything (no Python assumed), proven by a 3-OS GitHub Actions smoke test"
type: story
status: todo
parent: PW-1719
milestone: v1.0
subsystem: infra
effort: l
impact: high
found_by: owner
blocked_by: []
relates: [PW-1720, PW-1730, PW-1716]
refs: [install.sh, planet/appconfig.py, planet/__main__.py, planet/api.py, planet/store.py, docs/review/plan/installer.md]
---

## Description
**In plain words.** Daniel (11-11): "easy installation via Github for windows, mac, and ubuntu-at-the-very-least linux ... Assume we have to bootstrap up even 'do you have python' ... Unless this is somehow self-contained". Today install.sh covers Linux, macOS on a best-effort basis, and Windows only through WSL2. It already brings its own Python: the pinned, checksummed uv downloads a managed Python and the wheels, so nothing needs to be preinstalled except curl (Windows has PowerShell built in).

To do:
- `install.ps1` for native Windows, with the same commands as install.sh (`irm <raw url>/install.ps1 | iex`): uv's Windows build, pinned with its sha256; a Start-menu shortcut; the same `planet self` verbs.
- Make the runtime Windows-safe: find every Linux-only spot in planet/ (`/proc` reads in planet/store.py and planet/api.py, process groups and signals, path separators, `xdg-open`, the job runner's process handling) and give each an OS branch.
- The macOS gaps listed in installer.md: numba/TBB on arm64, and a `.command` launcher.
- `.github/workflows/install-smoke.yml`: on ubuntu-latest, macos-latest (arm64) and windows-latest, run the installer from the checkout, then `planet self status`, a tiny L4 make, and the viewer answering 200.
- README: the three one-liners.

**Testing needs Daniel's OK:** only Linux is on hand here, so the Windows and macOS proof is the Actions run, which needs a branch pushed to GitHub (pushes are otherwise only at releases, D83).

**Self-contained option (stretch):** a fully offline single-download bundle per OS (e.g. PyInstaller), which would be large because of numba/llvmlite. The uv route is self-bootstrapping and much smaller, so prefer it unless Daniel wants offline installs.

## Updates
