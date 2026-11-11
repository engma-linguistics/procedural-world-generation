# Machine-aware presets and low-detail mode (lane 313: PW-1720, PW-1721)

## In plain words

The installer now checks what machine it is on: how many cores, how much memory, how much free disk, and which
graphics card. From that, it writes a short list of settings into the install's config file. These say how many jobs run at
once, how big the tile cache may get, the default grid level, and, for each heavy feature (L8 worlds, L8 splits,
2 Myr peoples, L9 refines, zoom tiles), whether it is **allowed**, **warned** or **off**.

Each decision compares the most memory that feature has ever been **measured** using with what the machine can spare.
On a 32 GB desktop, L8 splits are off and zoom tiles build one at a time. On an 8 GB laptop, almost everything heavy is off
and the viewer starts in low detail. On your 180 GB workstation, everything is allowed.

When something is off, the server and `planet make` refuse it at once and say why: "it peaks at about 69 GB … this
machine's budget is 24 GB". The user doesn't wait an hour to run out of memory.

The viewer has a new **Machine** section at the bottom of its left panel. It shows the machine and every gate with the
number that decided it. In an installed copy, each gate can be overridden there, and the choice is saved. It also has a
**Detail** switch (auto / low / full). Low detail keeps fewer zoom tiles loaded and loading, stops at 250 m tiles and draws
at normal pixel density, so laptop graphics stay usable.

A developer checkout (`uv run planet serve`) is never gated. The presets only apply to an install. The panel still shows
what the probe *would* set.

## What a user sees

`planet self first-run` (and the new `planet self probe`, or `planet machine probe --write`) prints, on this workstation:

```
==> Sizing the app to this machine (cores, memory, disk, graphics)
    Machine probe and presets (planet/machine.py; sources in docs/review/plan/machine-presets.md):
      machine   48 cores, 25.8 GB RAM, 728.4 GB free disk, GPU NVIDIA RTX PRO 6000 Blackwell Workstation Edition (102.6 GB)
      budget    18.1 GB for the app (70% of the RAM), 6.5 GB kept spare beside each big job
      defaults  level 7, 1 Myr time zoom, 2 job(s) at once, memory cap 18 GB
      tiles     1 at once, levels [1, 2, 3, 4], cache cap 60 GB
      viewer    low detail auto
      allow     L6 worlds (planet make, 2 Myr time zoom) (~3.9 GB)
      ...
      off       L8 split peoples history, 2 Myr (~69.3 GB)
      (a memory cap of 25.8 GB applies to this process: the presets use it)
    Wrote the presets into …/config.toml (your [overrides] are kept).
```

That run was inside `systemd-run --user --scope -p MemoryMax=24G`. The probe takes a cgroup cap as the machine's RAM, so a
capped cgroup simulates a smaller machine (the ticket's acceptance asks for this). Then:

- `planet serve` prints `2 jobs at once` (the presets' `jobs`, unless `[serve] jobs` or `--jobs` says otherwise).
- `POST /api/make {"level": 8}` answers 409: `not started: L8 worlds (run) is off on this machine: it peaks at about
  30 GB (…); this machine's budget is 18.1 GB of 25.8 GB RAM, with 6.5 GB kept spare. If you know better, allow it in the
  viewer's Machine panel or with planet machine set make_l8 allow`. `planet make --level 8` stops with the same message.
- A warned feature runs: the job's answer carries `"warn": [...]`, and `planet make` prints `warning: …`.
- The refine dialog's estimate (`GET /api/refine/estimate`) lists a gated refine under `refuse` or `warn` like its other
  checks.
- `planet self open` runs the server inside a systemd user scope capped at `mem_cap_gb`, where systemd-run works
  (`PLANET_NO_CAP=1` skips it). `api.free_ram_gb` already honours a cgroup cap, so every RAM guard sees the cap.
- The Machine panel (screenshot checked in headless Chrome with SwiftShader). It chose low detail automatically
  ("software rendering"); 11 gates were shown with chips; an override of `refine_l9` to allow was saved as
  `[overrides] refine_l9 = "allow"` in the config.

## The preset table (tests/test_machine.py; made-up probe inputs)

| | 8 GB / 4-core laptop, Intel iGPU | 32 GB / 8-core desktop, 12 GB GPU | 180 GB / 48-core workstation |
|---|---|---|---|
| budget (share of RAM) / spare | 5.6 GB (70%) / 2 GB | 24 GB (75%) / 8 GB | 144 GB (80%) / 8 GB |
| memory cap (`mem_cap_gb`) | 5 GB | 24 GB | 144 GB |
| jobs at once | 1 | 2 | 4 |
| default level / time zoom | L6 / 1 Myr | L7 / 1 Myr | L7 / 2 Myr |
| LOD tiles | off | levels 1–4, 1 at a time | levels 1–4, 3 at a time |
| tile cache cap | min(60, 20% of free disk) | same | 60 GB |
| L6 worlds (3.9 GB) | warn | allow | allow |
| L7 worlds (6.6 GB) | off | allow | allow |
| L8 worlds (30 GB) | off | off | allow |
| peoples, 1 Myr (14.5 GB) | off | allow | allow |
| peoples, 2 Myr (20.3 GB) | off | warn | allow |
| refine to L8 (11.7 GB) | off | allow | allow |
| refine to L9 (39 GB) | off | off | allow |
| L8 split, 1 Myr (35.5 GB) | off | off | allow |
| L8 split, 2 Myr (69.3 GB) | off | off | allow |
| viewer low detail | on | auto (the viewer checks WebGL) | auto |

### Daniel's Mac (Apple silicon, 24 GB; the hand-test target)

The probe reads `sysctl hw.memsize` = 24 GiB = 25.8 GB. The budget is 70% of that, **18.1 GB**, with **6.5 GB** spare
(a quarter of the RAM). The cores are what `os.cpu_count` counts, performance and efficiency together. The presets are the
same for 8, 10 or 12 of them, because the memory, not the cores, limits the jobs. Test:
`tests/test_machine.py::test_daniels_mac_24gb`.

| feature | on the Mac | why (measured peak + spare against 18.1 GB) |
|---|---|---|
| L6 worlds | allowed | 3.9 GB (L6 starter world, installer.md) + 6.5 ≤ 18.1 |
| L7 worlds, the default level | allowed, default L7 | 6.6 GB (L7 2 Myr time zoom 040d59, two-myr.md §2) + 6.5 ≤ 18.1 |
| L8 worlds | **off** | 30 GB (L8 run, milestones-to-v1.md §4) > 18.1 |
| peoples, 1 Myr (L7) | warned | 14.5 GB (b74691, two-myr.md §2) fits, but not with the spare (21.0) |
| peoples, 2 Myr (L7) | **off**; the default time zoom is 1 Myr | 20.3 GB (580f8c, two-myr.md §2) > 18.1 |
| refine to L8 | warned | 11.7 GB (bcf4ba, two-myr.md §2) + 6.5 = 18.2, just over 18.1 |
| refine to L9 | off | 39 GB (PW-1262) |
| L8 splits, 1 and 2 Myr | off | 35.5 GB (025b98) and 69.3 GB (1f49d0), two-myr.md §2 |
| jobs at once | 2 | min(4, cores ÷ 4, 18.1 ÷ 6.6 GB (a typical heavy job, the L7 time zoom)) = 2 |
| LOD tiles | levels 1–4, **1 at a time** | 8.3 GB (`api.TILE_PEAK_GB[1]`) + 6.5 ≤ 18.1; (18.1 − 6.5) ÷ 8.3 = 1 |
| tile cache cap | 60 GB, or 20% of the free disk if that is less | `tiles.CAP_GB` |
| memory cap | 18 GB, but not applied on macOS (no systemd) | the gates and the RAM guards still apply |
| viewer detail | auto (an Apple GPU is not low by itself) | the viewer checks WebGL |

So on the Mac: L6 and L7 worlds, L7 peoples at 1 Myr with a warning, no L8 (worlds, splits or L9 refines), no 2 Myr
peoples, two jobs, and one detail tile at a time. Two items are close calls: "refine to L8" misses allow by 0.1 GB, and
"peoples at 1 Myr" is warned. Both can be overridden in the Machine panel when hand-testing. The 24 GB cgroup run on the
workstation (above) gave exactly these presets, because a 24 GiB cap reads as 25.8 GB, like the Mac.

## The rule, and where every number comes from

**The budget** is a share of the RAM: the smaller of the physical RAM (`/proc/meminfo` MemTotal, `sysctl hw.memsize` on
macOS) and any cgroup v2 `memory.max` above the process. The share is 70% under 32 GB, 75% under 64 GB and 80% from
64 GB up. These are the per-process caps of milestones-to-v1.md §4's tier table, which marks them as estimates.

**The spare** is 8 GB (`api.REFINE_RAM_SPARE_GB`, the spare the refine and zoom guards already keep), but never more
than a quarter of the RAM. A full 8 GB spare on an 8 GB laptop would forbid everything.

**A gate** is `allow` when peak + spare ≤ budget, `warn` when peak ≤ budget, and `off` otherwise. More RAM never turns a
gate off (tested over 2–258 GB).

| gate | peak | source |
|---|---|---|
| `make_l6` | 3.9 GB | installer.md, end-to-end test: the L6 starter world's peak RSS |
| `make_l7` | 6.6 GB | two-myr.md §2: the L7 2 Myr time zoom 040d59 (the L7 run itself ~0.9 GB) |
| `make_l8` | 30 GB | milestones-to-v1.md §4 (coordination.md): an L8 run's peak at its final write |
| `peoples_1myr` | 14.5 GB | two-myr.md §2: dnd peoples b74691 on a 1 Myr L7 zoom |
| `peoples_2myr` | 20.3 GB | two-myr.md §2: dnd peoples 580f8c on a 2 Myr L7 zoom |
| `refine_l8` | 11.7 GB | two-myr.md §2: refine of 6e2f17 to L8 (bcf4ba) |
| `refine_l9` | 39 GB | milestones-to-v1.md §4 (PW-1262) |
| `split_1myr` | 35.5 GB | two-myr.md §2: split 025b98 |
| `split_2myr` | 69.3 GB | two-myr.md §2: split 1f49d0. Lane 305's fix (two-myr.md §4) *estimates* ~35 GB at L8, but that is not measured, so the measured 69.3 is used. Update it when PW-1752 measures the fixed peak |
| `tiles_l1` | 8.3 GB | `api.TILE_PEAK_GB[1]` (lanes 290, 295) |
| `tiles_l2` | 5.0 GB | `api.TILE_PEAK_GB[2]` (lanes 301, 303) |

**Which gate a request crosses:**
- `make` at level 6/7/8 → `make_l<level>`.
- With peoples, a ≤ 1000 kyr time zoom → `peoples_1myr`; longer → `peoples_2myr`.
- At L8 the peoples gates are the split's (`split_*`).
- L6 peoples have no measurement, so they use the L7 numbers as an upper bound.
- `POST /api/lineages` reads the world's level and its time zoom's length the same way.
- A refine to L8/L9 → `refine_l8`/`refine_l9`.

**The other presets:**
- `jobs` = min(4 (`server.JOBS`), cores ÷ 4, budget ÷ 6.6 GB), at least 1.
- `tile_at_once` = min(3 (`tiles.AT_ONCE`), (budget − spare) ÷ 8.3 GB), at least 1 when tiles are on.
- `tile_levels`: none unless level 1 is allowed (levels 2–4 read level 1).
- `tile_cache_gb` = min(60 (`tiles.CAP_GB`), 20% of free disk). `$PLANET_TILE_CACHE_GB` still wins.
- `default_level` 7 needs L7 allowed and ≥ 8 cores (the plan's minimum machine).
- `default_kyr` 2000 only when 2 Myr peoples are allowed, else 1000.
- `disk` off/warn below 20/50 GB free (install.sh's `check_disk`).
- `low_detail` is "on" for an integrated or software GPU, under 2 GB of VRAM, or under 16 GB RAM (the plan's §4). Otherwise
  "auto", and the viewer decides.

**The viewer's auto detail** (`viewer/machinecore.js`) goes low for:
- no WebGL2;
- a software renderer (SwiftShader, llvmpipe);
- Intel graphics other than Arc;
- a largest texture under 8192 px;
- `navigator.deviceMemory` ≤ 4 GB;
- a probe that said "on".

Low detail sets `LOD.maxTiles` 120 → 40, `maxBytes` 0.4 → 0.12 GB, fetches 4 → 2, `refinePx` 1.5 → 3, `maxLevel` 4 → 3,
and the device pixel ratio cap 2 → 1. URL parameters (`?lodpx`, `?lodmax`, `?dpr`) still win. **These numbers are
judgement, not measured.** The ticket's frame-time check on an integrated GPU is not done (below).

## Per OS (owner scope 2026-11-11: Windows native, macOS, Linux)

The probe has one branch per OS, and each has a safe fallback. Nothing assumes /proc, /sys, systemd or nvidia-smi.

| | Linux (Ubuntu) | macOS | Windows |
|---|---|---|---|
| cores | `sched_getaffinity` (honours taskset) | `os.cpu_count` | `os.cpu_count` |
| RAM | `/proc/meminfo` MemTotal | `sysctl -n hw.memsize` | `GlobalMemoryStatusEx` via ctypes |
| memory cap | cgroup v2 `memory.max` | none | none |
| disk | `shutil.disk_usage` | same | same |
| GPU | nvidia-smi if installed, else `lspci` | `system_profiler SPDisplaysDataType` | nvidia-smi if installed, else left to the viewer's WebGL renderer string |

When the RAM can't be read, the presets plan for 32 GB (the minimum machine) and the probe says so (`ram_known = false`).
An unknown GPU leaves low detail on "auto", and the viewer decides from WebGL.

Tests fake each branch: a fake kernel32, sysctl text, system_profiler text with Apple, AMD and Intel GPUs, and presets for
a Windows laptop, an Apple-silicon MacBook and a Linux box whose RAM can't be read. Only Linux was run.

The memory cap of `planet self open` is Linux only (systemd-run). The Linux-only spots elsewhere in planet/ are in the
inbox draft "Native Windows: Linux-only spots in planet/". One of them, `os.kill(pid, 0)`, would end a running
simulation on Windows.

## The code

- `planet/machine.py`: the probe, `presets_for` (pure), gates and messages, the config writer (replaces `[presets]` and
  `[presets.gates]`; keeps `[overrides]` and everything else; checks the result reads back as TOML), and `report` for
  `GET /api/machine`.
- `planet/__main__.py`: `planet machine probe [--write] [--json] [--config]`, `planet machine show`, and
  `planet machine set GATE allow|warn|off|auto`. `planet make` takes the default level and kyr from the presets and is
  gated. `planet serve` takes `jobs`.
- `planet/server.py`: `GET/POST /api/machine`, gates on `/api/make` and `/api/lineages`, and the tile service built
  with the presets.
- `planet/api.py`: the refine estimate's gate.
- `planet/tiles.py`: `TileService(levels=…)`. A tile of a level that is off is not built (the status note says so).
- `install.sh`: `planet self probe`; `first-run` probes first; `open` runs under the memory cap.
- Viewer: `viewer/machinecore.js` (pure, node-tested) and `viewer/globe/machine.js` (the panel; mounts itself into
  `#controls`). The shared files got one import line in `globe/main.js`, and `globe/lodtiles.js`'s three constants became
  `LOD.maxTiles / maxBytes / fetches`.

## Not done

- No frame-time measurement on an integrated GPU, or with Chrome's GPU throttled (PW-1721's acceptance). The low-detail
  numbers are judgement.
- The "v1.0 walk on a 32 GB machine, nothing OOMs" acceptance was not run. Only the gates were checked under a 24 GB
  cgroup.
- The viewer does not send its WebGL report back to the server. It is shown in the panel only.
- Tile-gate overrides take effect at the next server start (the tile service reads them once).
- macOS: `sysctl hw.memsize` and the systemd-free path are written but not run on a Mac. The memory cap is Linux only.
- The New planet form takes its default level and time zoom length from the presets (through
  `GET /api/make/options`), but it does not grey out a gated choice. Picking L8 or a gated peoples run is refused when
  the form is submitted, with the reason.
