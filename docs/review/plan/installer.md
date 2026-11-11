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
`appconfig.presets()` returns the `[presets]` table for the server and `planet make` to read once the probe writes it.

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
