# The installer (lane 304): what a user types and sees

Plan: `milestones-to-v1.md` §4. Built: `install.sh` (repo root), `planet/appconfig.py`, the vendored three.js
(`viewer/vendor/three-r160/`), `api.free_ram_gb` on macOS. Tests: `tests/test_install.py`.
The plan's details are not confirmed yet (desk card D80), so this is the Linux core with macOS best effort; the open
choices are in the inbox draft "Decide where installer releases come from".

## What Daniel types

```sh
curl -LsSf <release>/install.sh | sh                 # once releases are public (see the draft)
sh install.sh                                        # from a checkout or an unpacked tarball
sh install.sh --source ~/repos/procgen --ref v1.0.0  # a tag (or branch) of a local git repo
```

Then:

```sh
planet self open        # start the server and open the viewer (also: "Procgen World" in the app menu)
planet self first-run   # compile numba again, offer the L6 starter world
planet self update      # newest v* tag -> a new app/<version>, warmed up, then switched to
planet self rollback    # back to the previous version (and again to undo)
planet self status
planet self uninstall   # asks; keeps the data folder unless you say yes to deleting it
planet make --seed 7 --level 6   # everything else is the normal CLI, run against the install
```

Options (`sh install.sh --help`): `--root`, `--data`, `--source`, `--ref`, `--bin-dir`, `--port`, `--jobs`,
`--uv PATH`, `--no-desktop`, `--no-first-run`, `--starter/--no-starter`, `--delete-data/--keep-data`, `--yes`,
`--dry-run`. Questions read the terminal even under `curl | sh`; with no terminal (or `--yes`) they take the default.

## What Daniel sees (the test install on this machine)

```
procgen_world installer
    version  v9.0.0   (from /data/personal/scratch/lane304/src)
    install  /data/personal/scratch/lane304/root
    data     /data/personal/scratch/lane304/data
    config   …/home/.config/procgen-world/config.toml
==> uv 0.12.7 (private to this install)
    downloading uv 0.12.7 (x86_64-unknown-linux-gnu)
==> Fetching v9.0.0 from /data/personal/scratch/lane304/src
==> Installing Python 3.14 and the dependencies (uv sync --frozen --no-dev)
    done in 3 s
==> Launcher, config and app-menu entry
    note: …/home/.local/bin is not on your PATH. Add it (e.g. in ~/.profile: export PATH="…/home/.local/bin:$PATH"), or run …/root/bin/planet.
Installed v9.0.0 in 4 s (744M under /data/personal/scratch/lane304/root).
==> First run: compiling the simulation (numba) on a tiny level-4 planet
    this happens once per version; later runs start straight away
    | planet make: seed 7, preset earthlike, level 4, 20 Myr, 10 kyr time zoom, …
    | [  6%] tectonics: 4 of 20 Myr
    | …
    | [100%] done
    compiled in 62 s
Make a starter world now (level 6, seed 7, about 20 min)? [y/N]
    no starter world now; make one any time with: planet make --seed 7 --level 6

Start it with:  planet self open     (or Procgen World in the app menu)
Manage it with: planet self update | rollback | uninstall | status
```

`planet self open` (or `planet serve`) with the server already running just opens the browser:
`A viewer server is already running at http://127.0.0.1:8791/viewer/`. If the config's port is taken by something
else, it says `(port 8765 is taken: using 8766)`.

Update, rollback and uninstall:

```
$ planet self update
Updating procgen_world v9.0.0 -> v9.0.1 (your data in …/data is not touched)
    uv 0.12.7 already in …/root/uv
==> Fetching v9.0.1 from …/src
==> Installing Python 3.14 and the dependencies (uv sync --frozen --no-dev)
    done in 1 s
Now on v9.0.1 (1 s). Back to v9.0.0 with: planet self rollback
==> First run: compiling the simulation (numba) on a tiny level-4 planet      (≈ 65 s, as above)
$ planet self rollback
Rolled back v9.0.1 -> v9.0.0 (planet self rollback again returns to v9.0.1).
$ planet self uninstall
This removes procgen_world from …/root (963M): every version, its private uv
and Python, the launcher (…/home/.local/bin/planet), the app-menu entry and …/config.toml.
Uninstall? [Y/n]
Also delete your data folder …/data (44K of runs and worlds)? [y/N]
Kept your data folder …/data (44K).
procgen_world is uninstalled.
```

## What it does

| piece | where | notes |
|---|---|---|
| uv 0.12.7, pinned | `<root>/uv/uv` | from the GitHub release, sha256 checked (4 targets pinned in the script); `--uv PATH` copies a local one |
| Python 3.14 | `<root>/python` | `UV_PYTHON_INSTALL_DIR`, `UV_PYTHON_PREFERENCE=only-managed`, `UV_NO_CONFIG=1`: never the system's or pyenv's |
| uv cache | `<root>/cache` | the versions' venvs hardlink from it, so a second version costs ~200 MB, not ~600 |
| each version | `<root>/app/<version>/` + `.venv` | `git archive <tag>` (local repo), `git clone --depth 1` (URL) or a copy (plain folder); `uv sync --frozen --no-dev`; smoke check (imports, `planet --help`) before it becomes `current` |
| current / previous | symlinks in `<root>/app` | `rollback` swaps them; `update` prunes anything older than previous |
| launcher | `<root>/bin/planet`, linked from `~/.local/bin/planet` | sets `PLANET_DATA` (from the config unless set), `PLANET_CONFIG`, `PYTHONPATH`; `planet self …` runs `<root>/bin/manage.sh` (the current version's install.sh). An existing `planet` that is not ours is never replaced. Shell profiles are never edited: it prints the PATH line instead |
| app-menu entry | `~/.local/share/applications/procgen-world.desktop` | `Exec=<root>/bin/planet self open`, `Terminal=true` (the server lives in that terminal; Ctrl-C stops it). macOS: `~/Applications/Procgen World.command` |
| config | `~/.config/procgen-world/config.toml` | `data`, `[serve] port, jobs`, and an empty `[presets]` hook. Kept across update and reinstall |
| state | `<root>/install.env` | the source, data folder, links: what update and uninstall need |

Data root: `store.root()` already honoured `$PLANET_DATA`; the launcher sets it from the config. Everything the
server writes (runs, worlds, zooms, grids, `.tiles`, `.thumbs`, `.gzcache`) goes there. Two things stay per
version, in the app folder: numba's cache (`cache=True` writes beside the code) and `.jobs/<port>.json` (queued jobs
of a version are not carried across an update).

**The presets hook (for the machine-aware presets ticket).** `planet/appconfig.py` reads the config only when
`$PLANET_CONFIG` is set (the launcher sets it; a checkout run with `uv run` never does, so a dev checkout ignores an
install). `planet serve` takes `port`, `jobs` and `threads` from `[serve]` when no flag is given;
`appconfig.presets()` returns the `[presets]` table, which the machine probe now writes (`planet/machine.py`; see
`machine-presets.md`).

**Offline viewer.** three.js r160 (`build/three.module.js`, OrbitControls, LineSegments2, LineSegmentsGeometry,
LineMaterial and the MIT LICENSE; 1.4 MB) is vendored under `viewer/vendor/three-r160/`, and the import maps of
`index.html`, `zoom.html` and `ringworld.html` point there. A test fails if a viewer page loads a script from a CDN or
imports an addon that is not vendored.

**`planet serve` port.** With no `--port`, it tries the config's port (else 8765) and the next 19; if the first is
already a planet server (GET `/api/planets` answers JSON) it opens the browser there instead of starting a second
one. An explicit `--port` behaves as before.

## End-to-end test on this machine (2026-11-11)

Scratch root `/data/personal/scratch/lane304/root`, `PLANET_DATA=/data/personal/scratch/lane304/data`,
`HOME=/data/personal/scratch/lane304/home` (so `~/.local/bin`, `~/.config` and the app menu were the scratch ones),
source a scratch clone of `lane304` with test tags `v9.0.0` and `v9.0.1` (`--source <clone>`, no network for the
code; uv and Python came from the network). Install and warm-up ran under
`systemd-run --user --scope -p MemoryMax=16G -p MemorySwapMax=0`, cores 0–7; the server under `MemoryMax=24G`.

| step | result |
|---|---|
| `install.sh --dry-run` | prints every step, changes nothing |
| install (uv download, Python 3.14.7, deps) | **4–5 s** wall (fast link; uv sync 1–3 s) |
| numba warm-up (L4, 20 Myr, 10 kyr, 1 zoom), cold | **62 s, 66 s, 76 s** (three cold versions); peak RSS 3.1 GB |
| the same with the cache warm | **17 s** |
| L6 starter world (`planet make --seed 7 --level 6`, 8 cores) | **1091 s (18.2 min)**, peak RSS 3.9 GB (the plan estimate says ~19.9 min); first-run total 1153 s |
| `planet serve` (config port 8791) | `GET /viewer/` 200 (32.7 KB); `/viewer/vendor/three-r160/build/three.module.js` 200, `text/javascript`, 1.27 MB; OrbitControls and LineSegments2 200; no `jsdelivr` in any page served |
| second `planet serve` | "A viewer server is already running at …:8791" |
| `planet self update` v9.0.0 → v9.0.1 | 1.7 s (+ warm-up); `status` shows current v9.0.1, previous v9.0.0 |
| `planet self rollback` (twice) | instant; symlinks swapped each way; `planet` runs the right version |
| `planet self uninstall --yes` | root, launcher link, menu entry and config removed; the data folder and a marker file in it kept |
| reinstall into the kept data folder | works; the config is written again |

## Disk use

| what | size |
|---|---|
| `<root>/uv` | 48 MB |
| `<root>/python` (CPython 3.14.7) | 111 MB |
| `<root>/cache` (uv) | 405 MB |
| one version (`app/<v>`: code + venv, hardlinked from the cache) | 185 MB, + 11 MB of numba cache after the warm-up |
| **one version installed** | **744 MB** |
| two versions (after an update) | 948 MB |
| data folder after the L6 starter world | 1.3 GB (run 1.2 GB, 4 zooms 128 MB, world 15 MB, grids 5 MB) |

## macOS (PW-1716 and the rest)

- `api.free_ram_gb` now reads `vm_stat` on macOS: free + inactive + speculative pages times the page size (psutil's
  `available`). If `vm_stat` fails it takes a quarter of `sysctl -n hw.memsize` and warns once, so the RAM guards stay
  on. On any other system without `/proc/meminfo` it still returns None (guards off) but now warns once instead of
  staying silent. The parsers are tested on both outputs; **not run on a real Mac**.
- `install.sh` knows the Apple uv targets (arm64 and x86-64, checksums pinned) and writes
  `~/Applications/Procgen World.command` instead of a `.desktop` file. Untested on a Mac: BSD `df`, `du`, `sed`,
  `ln -sfn` and `env -u` are used in their POSIX/BSD-compatible forms, and `shasum -a 256` stands in for `sha256sum`.
- numba and TBB on macOS arm64 are the main unknown (the run-cost table was measured on a Mac, so the code runs).

## Not done / caveats

- `curl | sh` from a release URL is untested: no public release yet (inbox draft). A remote source needs `git`.
- shellcheck was not run (fetching it was refused by the permission system in this lane); `sh -n`, `dash -n` and
  `bash --posix -n` pass, and the script was run end to end under dash.
- The numba cache is per version (its keys include the source path and mtime), so every update compiles again;
  `update` runs the warm-up for the new version before returning.
- The viewer's "update available" notice is not built (inbox draft).
- `planet make` ends with `view: http://127.0.0.1:8765/viewer/?world=…` whatever port the install uses (cosmetic).
- The starter world is only offered (default no, ~18 min on 8 cores); the downloadable sample bundle the plan
  mentions is not built (the L6 family weighs 1.3 GB, mostly the run's layers).
- WSL2: not tested; it is plain Linux to the script, but `xdg-open` from WSL needs `wslu` to reach the Windows browser.

## Windows, macOS and the 3-OS smoke test (lane 315, PW-1760)

### In plain words

There is now a Windows installer, `install.ps1`, which does what `install.sh` does: one line in PowerShell
(`irm …/install.ps1 | iex`) fetches a pinned, checksummed uv, which brings its own Python, so nothing has to be on the
PC first. It puts a "Procgen World" shortcut in the Start menu and a `planet` command on the PATH, and it has the same
`planet self open | update | rollback | uninstall | status` commands.

Before this, a few parts of the program would have gone badly wrong on Windows. The worst: checking whether a running
simulation was still alive would have **killed it**, because that Linux call means "terminate" on Windows. Each of
those spots now has a Windows version. Linux does exactly what it did before.

On a Mac, the installer now refuses Intel Macs and macOS older than 14 with a plain message. The libraries the
simulation needs have no builds for them, so the old behaviour was a confusing failure halfway through. Both
installers also work without git when the source is GitHub: they download the tag's archive instead. A fresh Mac or
Ubuntu has no git.

**What is proven where.** Only Linux was available here. Linux: the full install, make, serve and uninstall run (below),
and the unit tests. **Windows: nothing has run on Windows yet.** `install.ps1` has not even been parsed: there is no
`pwsh` on this machine, so its parse test skips. Windows is proven only when the GitHub Actions run
(`.github/workflows/install-smoke.yml`) passes. **macOS: only by the Actions run and by Daniel's checklist**
(`install-mac-checklist.md`).

### What changed, per OS

| | Linux | macOS | Windows |
|---|---|---|---|
| installer | `install.sh` (unchanged path) | `install.sh`: refuses Intel and macOS < 14 up front; `~/Applications/Procgen World.command` as before | **new** `install.ps1`: uv `x86_64-pc-windows-msvc` 0.12.7, sha256 `bf1518af…5218` (checked against the release's `.sha256` and a download); ARM64 refused (piper-tts has no wheel) |
| source without git | GitHub tarball via the tags API (`PROCGEN_NO_GIT=1` forces it, for tests) | same | GitHub zip, same way |
| install root / config / data | `~/.local/share/procgen-world`, `~/.config/procgen-world/config.toml`, `~/procgen-world-data` | same | `%LOCALAPPDATA%\procgen-world`, `%APPDATA%\procgen-world\config.toml`, `%USERPROFILE%\procgen-world-data` (written with `/` in the TOML) |
| current / previous | symlinks | symlinks | `app\current.txt`, `app\previous.txt` (symlinks need admin or developer mode) |
| launcher | `bin/planet` linked into `~/.local/bin` (PATH never edited) | same | `bin\planet.cmd`; `bin\` is **added to the user PATH** (as uv's own installer does; `-NoModifyPath` skips it; uninstall removes it). Sets `PYTHONUTF8=1`: Python 3.14 on Windows still writes text in the ANSI code page |
| app menu | `.desktop` | `.command` | Start-menu `Procgen World.lnk` → `planet.cmd self open` |
| memory cap (`mem_cap_gb`) | systemd-run scope | none | none (inbox draft) |
| process alive? (`store._alive`) | `os.kill(pid, 0)` | same | OpenProcess + GetExitCodeProcess: **never os.kill** |
| process start (`store._proc_start`) | `/proc/<pid>/stat` | None, as before | GetProcessTimes' creation time |
| cross-process lock (`store.lock`) | `fcntl.flock` | same | `msvcrt.locking` on byte 0, waited for, released before close |
| atomic write (`store.write_atomic`, `atomic_path`, checkpoints) | `os.replace` | same | `os.replace` retried up to ~2 s on PermissionError (a reader has the file open) |
| free RAM (`api.free_ram_gb`) | `/proc/meminfo` + cgroup | `vm_stat` | GlobalMemoryStatusEx `ullAvailPhys` (`machine.windows_free_ram_gb`, the same ctypes reader as the total) |
| refine's temp-folder rule | "/tmp … (it is memory on this machine)" | "the temp folder (…) is nearly full" | same as macOS |
| worker watchdog (`parallel._exit_with_parent`) | getppid changes | same | the parent's pid still running (Windows never reparents) |
| language pass workers | forked | forked | 1 (no fork on Windows; same output, slower) |
| plate arrays (`tectonics/plates._mapped`) | private anonymous mmap | same | plain anonymous mmap (no MAP_* flags on Windows); `release()` already did nothing there |
| opening the browser | `webbrowser` (already portable) | same | same |

The OS branches live in `planet/osutil.py` and are chosen by `sys.platform` when they are called, so tests can fake them.
`grep` over `planet/` (not `planet/language/`, `tools/` or `docs/`) for `os.kill`, `fcntl`, `signal.`, `/proc`, `/sys`,
`xdg-open`, `os.fork`, `preexec_fn`, `start_new_session`, `.sh`, `mmap` and `sched_` found nothing else that runs on an
install: `/proc` and `/sys/fs/cgroup` reads are already wrapped in `try` (cgroup caps are Linux-only by nature), there
are no signals or process groups, the job pool uses `spawn`, and `machine.usable_cores` already falls back off Linux.
`planet/language/history.py` asks for a `fork` pool directly. That folder was out of bounds for this lane, so the
callers (`make.py`, `planet languages`) pass 1 worker where fork is missing.

**Lockfile limits found on the way:** uv.lock has Python 3.14 wheels of numba, llvmlite and onnxruntime for Apple
Silicon only (onnxruntime: macOS 14+), so Intel Macs cannot install. piper-tts has no ARM64 Windows wheel. Both are now
refused up front (inbox draft).

### The smoke workflow

`.github/workflows/install-smoke.yml` runs on push to `ci/*` branches and on `workflow_dispatch`, on ubuntu-latest,
macos-latest (arm64) and windows-latest. Each job has a 30-minute limit. Each installs from the checkout
(`--source $GITHUB_WORKSPACE --ref HEAD`, so a tag in the checkout cannot pick an older version), then runs `planet self
status` and `planet self probe`. It makes the cheapest documented world, the installer's warm-up recipe
(`make --seed 7 --level 4 --myr 20 --kyr 10 --zooms 1`, 62–76 s cold on 8 cores here). It serves on port 8790 and
requires `GET /viewer/` to answer 200, then uninstalls with `--yes --delete-data` and checks that nothing is left.
Windows runs `install.ps1` in Windows PowerShell 5.1, as a script block with options (the one-liner's form). It
uninstalls through `planet.cmd self uninstall`, the way a user would, and checks that the PATH entry and the shortcut
are gone. `PROCGEN_MIN_FREE_GB=5` lowers the 20 GB disk floor for the small runners (both installers read it).

**Run here, on Linux, the same steps as the ubuntu job** (scratch HOME, root and data under
`/data/personal/scratch/lane315/`, `MemoryMax=16G`, cores 0–7, port 8797): install 6 s (770 MB), `self status` and
`self probe` correct, the make **75 s** cold, `GET /viewer/` 200, `/api/planets` lists the world, uninstall removed
root, data, launcher link, menu entry and config; **85 s** in all. First try failed: with no `--ref`, the worktree's
`v0.3.0` tag (older than the installer) was picked, and its tree has no install.sh. Hence `--ref HEAD` in the workflow.

### Tests (`tests/test_install_os.py`, on Linux with faked OS values)

A fake kernel32 (OpenProcess, GetExitCodeProcess, GetProcessTimes) under `sys.platform = "win32"`, with `os.kill` set to
fail the test: liveness, access-denied, exited and reused pids, and `run_status` of a running run. A fake msvcrt: the
lock waits through two busy tries, is re-entrant, and is released before the close. Also: the `os.replace` retry (and no
retry on Linux), one language worker without fork, plates' anonymous map without `MAP_ANONYMOUS`, and Windows free RAM
reaching `api.free_ram_gb`. Linux is checked unchanged: `/proc` start time, `os.kill` liveness. For the installers:
`install.sh` and `install.ps1` pin the same uv; install.ps1 has every verb of install.sh; the launcher's `self` line
exits on the same line (uninstall deletes the .cmd while cmd reads it); it sets `PYTHONUTF8`; there is no bare `exit`,
which would close the window under `iex`; install.ps1 parses (skips: no pwsh here). The no-git tarball dry run, and the
macOS checks with fake `uname`/`sw_vers` (Intel refused, 13 refused, 15 accepted).

### Not done / caveats

- **install.ps1 has never run.** Expect the first Actions run to find PowerShell 5.1 slips. Known risks: argument
  passing of `--yes`-style flags through `powershell -File`, and native stderr under `$ErrorActionPreference = 'Stop'`
  (wrapped, but unproven).
- The one-liners in the README need a public repository or release and a `v*` tag (the release-source draft, D80).
- No memory cap on Windows or macOS; rewriting files the server has mapped is unproven on Windows (inbox drafts).
- `planet make` still prints `view: http://127.0.0.1:8765/…` whatever the port (cosmetic, as before).
- The Mac `.command` is written locally, so it carries no quarantine flag. The checklist asks Daniel to note it if
  Gatekeeper complains.

## The smoke test's zoom step on macOS and Windows (lane 316, PW-1760)

Actions run 43116330508 (`ci/install-smoke`): ubuntu passed; macOS and Windows installed and passed `self status`, then
the tiny make failed at its one zoom.

- **macOS: the zoom RAM guard kept a fixed 8 GB spare.** `api.zoom_estimate` needed peak + `ZOOM_RAM_SPARE_GB` (8), so
  the 2000 km, 4 km/px zoom (about 2 GB) needed 10 GB on a 7 GB runner. Now the zoom, tile and refine guards keep
  `api.ram_spare_gb()`: `machine.spare_gb` of the physical RAM, the presets' own rule (8 GB, at most a quarter of the
  RAM). The 7 GB runner keeps 1.8 GB (the zoom needs 3.8 GB in all); a 32 GB or bigger machine keeps 8 GB as before;
  RAM that can't be read keeps 8. Physical RAM, not a cgroup cap: under `systemd-run MemoryMax` the guard already
  counts the cap's room as the free memory, and the spare stays what the machine is.
- **Windows: `[Errno 22] Invalid argument: ...zooms/<id>/layers/barrier_island.bin`.** `regional.zoom` saves the zoom,
  then `coast.add_to_zoom` loads it with `regional.load`, whose layers are `np.memmap`s (`store.read_layer`), and
  rewrites `barrier_island.bin` with `store.write_layers` while those maps are alive. Windows refuses to open a mapped
  file for writing (ERROR_USER_MAPPED_FILE, which Python reports as errno 22); Linux allows it. `regional.load` has an
  `mmap` option now, and every caller that rewrites layer files of the zoom it loaded uses `mmap=False`:
  `coast.add_to_zoom`, `regional.add_satellite`, `add_game`, `add_humanuse`. `regional.zoom` also frees the built
  arrays before the coast pass, so reading the layers into memory does not raise the peak (at most ~110 bytes a pixel,
  1.8 GB on a 16 Mpx section). Layer bytes are unchanged: the same 70 files, byte for byte, from a zoom with
  add_humanuse and add_game made by the code before and after.
- **`planet make` now logs a failed stage's full traceback** to the run's `run.txt` (named in the error) and, with
  `PLANET_DEBUG=1` (set in the smoke workflow), prints it to stderr.

Tests: `tests/test_windows_mapped_files.py` plays Windows on Linux (a write or `os.replace` onto a layer file with a
live map from `store.read_layer` raises errno 22 / access denied). Without the fix it fails with the CI's message;
with it a zoom build and all four in-place steps pass. `test_zoom_sections.py::test_the_spare_follows_the_machine_presets_rule`
(7 GB: the 2 GB zoom starts, a 10 GB one is refused; 180 GB: unchanged), `test_make.py::test_a_failed_stage_logs_its_traceback`.
